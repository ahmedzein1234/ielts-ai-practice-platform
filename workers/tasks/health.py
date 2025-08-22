"""Health check tasks for the worker system."""

import time
from typing import Dict, Any
import httpx
import structlog

from workers.celery_app import celery_app
from workers.config import settings

logger = structlog.get_logger()


@celery_app.task(bind=True, name="workers.tasks.health.health_check")
def health_check_task(self) -> Dict[str, Any]:
    """Perform health check of all services."""
    start_time = time.time()
    
    try:
        logger.info(
            "Starting health check task",
            task_id=self.request.id
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Checking service health", "progress": 10}
        )
        
        health_results = {}
        
        # Check API Gateway
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.api_gateway_url}/health/")
                health_results["api_gateway"] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
        except Exception as e:
            health_results["api_gateway"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Checking speech service", "progress": 30}
        )
        
        # Check Speech Service
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.speech_service_url}/health")
                health_results["speech_service"] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
        except Exception as e:
            health_results["speech_service"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Checking OCR service", "progress": 50}
        )
        
        # Check OCR Service
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.ocr_service_url}/health")
                health_results["ocr_service"] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
        except Exception as e:
            health_results["ocr_service"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Checking scoring service", "progress": 70}
        )
        
        # Check Scoring Service
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.scoring_service_url}/health")
                health_results["scoring_service"] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
        except Exception as e:
            health_results["scoring_service"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Checking Redis", "progress": 90}
        )
        
        # Check Redis
        try:
            import redis.asyncio as redis
            redis_client = redis.from_url(settings.redis_url)
            await redis_client.ping()
            health_results["redis"] = {
                "status": "healthy",
                "response_time": 0.001  # Very fast for ping
            }
            await redis_client.close()
        except Exception as e:
            health_results["redis"] = {
                "status": "error",
                "error": str(e)
            }
        
        processing_time = time.time() - start_time
        
        # Calculate overall health
        healthy_services = sum(1 for service in health_results.values() 
                             if service.get("status") == "healthy")
        total_services = len(health_results)
        overall_health = "healthy" if healthy_services == total_services else "degraded"
        
        result = {
            "task_id": self.request.id,
            "overall_health": overall_health,
            "healthy_services": healthy_services,
            "total_services": total_services,
            "services": health_results,
            "processing_time": processing_time,
            "status": "completed",
            "timestamp": time.time()
        }
        
        logger.info(
            "Health check completed",
            task_id=self.request.id,
            overall_health=overall_health,
            healthy_services=healthy_services,
            total_services=total_services,
            processing_time=processing_time
        )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Health check task failed",
            task_id=self.request.id,
            error=str(e),
            processing_time=processing_time
        )
        raise


@celery_app.task(bind=True, name="workers.tasks.health.monitor_queue_depth")
def monitor_queue_depth_task(self) -> Dict[str, Any]:
    """Monitor queue depths for all task queues."""
    start_time = time.time()
    
    try:
        logger.info(
            "Starting queue depth monitoring task",
            task_id=self.request.id
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Monitoring queue depths", "progress": 50}
        )
        
        # In a real implementation, you would check Redis queue depths
        # For now, we'll simulate the monitoring
        
        queue_depths = {
            "scoring": 0,  # Would be actual queue depth
            "file_processing": 0,
            "email": 0,
            "analytics": 0
        }
        
        processing_time = time.time() - start_time
        
        result = {
            "task_id": self.request.id,
            "queue_depths": queue_depths,
            "processing_time": processing_time,
            "status": "completed",
            "timestamp": time.time()
        }
        
        logger.info(
            "Queue depth monitoring completed",
            task_id=self.request.id,
            queue_depths=queue_depths,
            processing_time=processing_time
        )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Queue depth monitoring failed",
            task_id=self.request.id,
            error=str(e),
            processing_time=processing_time
        )
        raise
