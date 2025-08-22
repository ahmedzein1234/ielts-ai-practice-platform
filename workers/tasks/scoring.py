"""Background scoring tasks for IELTS submissions."""

import time
from typing import Dict, Any, Optional

from celery import current_task
from celery.signals import task_prerun, task_postrun, task_failure
import structlog
import httpx

from workers.celery_app import celery_app
from workers.config import settings

logger = structlog.get_logger()


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extras):
    """Log task start."""
    logger.info(
        "Task starting",
        task_name=task.name,
        task_id=task_id,
        args=args,
        kwargs=kwargs
    )


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **extras):
    """Log task completion."""
    logger.info(
        "Task completed",
        task_name=task.name,
        task_id=task_id,
        state=state,
        retval=retval
    )


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **extras):
    """Log task failure."""
    logger.error(
        "Task failed",
        task_name=sender.name,
        task_id=task_id,
        exception=str(exception),
        traceback=traceback
    )


@celery_app.task(bind=True, name="workers.tasks.scoring.score_submission")
def score_submission_task(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
    """Score an IELTS submission in the background."""
    start_time = time.time()
    
    try:
        logger.info(
            "Starting background scoring task",
            task_id=self.request.id,
            submission_id=submission_data.get("submission_id"),
            task_type=submission_data.get("task_type")
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Processing submission", "progress": 10}
        )
        
        # Call scoring service
        scoring_url = f"{settings.scoring_service_url}/score"
        
        async def score_submission():
            async with httpx.AsyncClient(timeout=settings.api_gateway_timeout) as client:
                response = await client.post(scoring_url, json=submission_data)
                return response.json()
        
        # For now, we'll use a synchronous approach
        # In a real implementation, you'd use asyncio.run() or similar
        import asyncio
        try:
            scoring_result = asyncio.run(score_submission())
        except Exception as e:
            logger.error("Failed to call scoring service", error=str(e))
            raise
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Scoring completed", "progress": 90}
        )
        
        # Process result
        processing_time = time.time() - start_time
        
        result = {
            "submission_id": submission_data.get("submission_id"),
            "task_id": self.request.id,
            "band_score": scoring_result.get("overall_band_score"),
            "confidence": scoring_result.get("confidence"),
            "model_used": scoring_result.get("model_used"),
            "processing_time": processing_time,
            "status": "completed",
            "timestamp": time.time()
        }
        
        logger.info(
            "Background scoring completed",
            task_id=self.request.id,
            band_score=result["band_score"],
            processing_time=processing_time
        )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Background scoring failed",
            task_id=self.request.id,
            error=str(e),
            processing_time=processing_time
        )
        
        # Update task state
        self.update_state(
            state="FAILURE",
            meta={
                "status": "Failed",
                "error": str(e),
                "processing_time": processing_time
            }
        )
        
        raise


@celery_app.task(bind=True, name="workers.tasks.scoring.score_batch")
def score_batch_task(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
    """Score multiple submissions in batch."""
    start_time = time.time()
    
    try:
        submissions = batch_data.get("submissions", [])
        total_submissions = len(submissions)
        
        logger.info(
            "Starting batch scoring task",
            task_id=self.request.id,
            total_submissions=total_submissions
        )
        
        results = []
        successful = 0
        failed = 0
        
        for i, submission in enumerate(submissions):
            try:
                # Update progress
                progress = int((i / total_submissions) * 100)
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "status": f"Processing submission {i+1}/{total_submissions}",
                        "progress": progress,
                        "completed": i,
                        "total": total_submissions
                    }
                )
                
                # Score individual submission
                result = score_submission_task.apply_async(
                    args=[submission],
                    queue=settings.scoring_queue
                )
                
                # Wait for result (in production, you might want to handle this differently)
                submission_result = result.get(timeout=300)  # 5 minute timeout
                results.append(submission_result)
                successful += 1
                
            except Exception as e:
                logger.error(
                    "Failed to score submission in batch",
                    submission_id=submission.get("submission_id"),
                    error=str(e)
                )
                failed += 1
                results.append({
                    "submission_id": submission.get("submission_id"),
                    "status": "failed",
                    "error": str(e)
                })
        
        processing_time = time.time() - start_time
        
        batch_result = {
            "batch_id": batch_data.get("batch_id"),
            "task_id": self.request.id,
            "total_submissions": total_submissions,
            "successful": successful,
            "failed": failed,
            "results": results,
            "processing_time": processing_time,
            "status": "completed",
            "timestamp": time.time()
        }
        
        logger.info(
            "Batch scoring completed",
            task_id=self.request.id,
            successful=successful,
            failed=failed,
            processing_time=processing_time
        )
        
        return batch_result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Batch scoring failed",
            task_id=self.request.id,
            error=str(e),
            processing_time=processing_time
        )
        raise


@celery_app.task(bind=True, name="workers.tasks.scoring.generate_feedback")
def generate_feedback_task(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate detailed feedback for a scored submission."""
    start_time = time.time()
    
    try:
        logger.info(
            "Starting feedback generation task",
            task_id=self.request.id,
            submission_id=feedback_data.get("submission_id")
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Generating feedback", "progress": 10}
        )
        
        # Call scoring service for feedback
        feedback_url = f"{settings.scoring_service_url}/score"
        
        # Prepare request with feedback generation flag
        request_data = {
            **feedback_data,
            "enable_detailed_feedback": True,
            "enable_feature_analysis": True
        }
        
        async def generate_feedback():
            async with httpx.AsyncClient(timeout=settings.api_gateway_timeout) as client:
                response = await client.post(feedback_url, json=request_data)
                return response.json()
        
        import asyncio
        try:
            feedback_result = asyncio.run(generate_feedback())
        except Exception as e:
            logger.error("Failed to generate feedback", error=str(e))
            raise
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Feedback generated", "progress": 90}
        )
        
        processing_time = time.time() - start_time
        
        result = {
            "submission_id": feedback_data.get("submission_id"),
            "task_id": self.request.id,
            "detailed_feedback": feedback_result.get("detailed_feedback"),
            "criteria_scores": feedback_result.get("criteria_scores"),
            "feature_analysis": feedback_result.get("feature_analysis"),
            "processing_time": processing_time,
            "status": "completed",
            "timestamp": time.time()
        }
        
        logger.info(
            "Feedback generation completed",
            task_id=self.request.id,
            processing_time=processing_time
        )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Feedback generation failed",
            task_id=self.request.id,
            error=str(e),
            processing_time=processing_time
        )
        raise


@celery_app.task(bind=True, name="workers.tasks.scoring.cleanup_old_results")
def cleanup_old_results_task(self, days_old: int = 30) -> Dict[str, Any]:
    """Clean up old scoring results from the database."""
    start_time = time.time()
    
    try:
        logger.info(
            "Starting cleanup task",
            task_id=self.request.id,
            days_old=days_old
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Cleaning up old results", "progress": 10}
        )
        
        # In a real implementation, you would:
        # 1. Query the database for old results
        # 2. Delete them in batches
        # 3. Update related records
        
        # For now, we'll simulate the cleanup
        import time
        time.sleep(2)  # Simulate work
        
        processing_time = time.time() - start_time
        
        result = {
            "task_id": self.request.id,
            "days_old": days_old,
            "records_cleaned": 0,  # Would be actual count
            "processing_time": processing_time,
            "status": "completed",
            "timestamp": time.time()
        }
        
        logger.info(
            "Cleanup completed",
            task_id=self.request.id,
            processing_time=processing_time
        )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Cleanup failed",
            task_id=self.request.id,
            error=str(e),
            processing_time=processing_time
        )
        raise
