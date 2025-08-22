"""File processing tasks for OCR and audio processing."""

import os
import time
import shutil
from typing import Dict, Any, Optional, List
from pathlib import Path

from celery import current_task
import structlog
import httpx
import aiofiles

from workers.celery_app import celery_app
from workers.config import settings

logger = structlog.get_logger()


@celery_app.task(bind=True, name="workers.tasks.file_processing.process_image")
def process_image_task(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process an uploaded image for OCR analysis."""
    start_time = time.time()
    
    try:
        file_path = file_data.get("file_path")
        file_id = file_data.get("file_id")
        user_id = file_data.get("user_id")
        
        logger.info(
            "Starting image processing task",
            task_id=self.request.id,
            file_id=file_id,
            file_path=file_path
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Processing image", "progress": 10}
        )
        
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Validate file type
        file_extension = Path(file_path).suffix.lower().lstrip('.')
        if file_extension not in settings.allowed_file_types:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Validating file", "progress": 20}
        )
        
        # Call OCR service
        ocr_url = f"{settings.ocr_service_url}/ocr"
        
        async def process_with_ocr():
            async with httpx.AsyncClient(timeout=settings.api_gateway_timeout) as client:
                # Read file as bytes
                async with aiofiles.open(file_path, 'rb') as f:
                    file_content = await f.read()
                
                # Prepare multipart form data
                files = {"file": (os.path.basename(file_path), file_content, "image/jpeg")}
                data = {
                    "language": file_data.get("language", "en"),
                    "engine": file_data.get("engine", "paddleocr")
                }
                
                response = await client.post(ocr_url, files=files, data=data)
                return response.json()
        
        import asyncio
        try:
            ocr_result = asyncio.run(process_with_ocr())
        except Exception as e:
            logger.error("Failed to process image with OCR", error=str(e))
            raise
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "OCR completed", "progress": 80}
        )
        
        # Process OCR result
        extracted_text = ocr_result.get("text", "")
        confidence = ocr_result.get("confidence", 0.0)
        word_count = ocr_result.get("word_count", 0)
        
        # Store result (in a real implementation, you'd save to database)
        result = {
            "file_id": file_id,
            "task_id": self.request.id,
            "user_id": user_id,
            "extracted_text": extracted_text,
            "confidence": confidence,
            "word_count": word_count,
            "processing_time": time.time() - start_time,
            "status": "completed",
            "timestamp": time.time(),
            "ocr_result": ocr_result
        }
        
        # Clean up temporary file
        try:
            os.remove(file_path)
            logger.info("Temporary file cleaned up", file_path=file_path)
        except Exception as e:
            logger.warning("Failed to clean up temporary file", file_path=file_path, error=str(e))
        
        logger.info(
            "Image processing completed",
            task_id=self.request.id,
            file_id=file_id,
            word_count=word_count,
            confidence=confidence
        )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Image processing failed",
            task_id=self.request.id,
            file_id=file_data.get("file_id"),
            error=str(e),
            processing_time=processing_time
        )
        
        # Clean up on failure
        file_path = file_data.get("file_path")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        
        raise


@celery_app.task(bind=True, name="workers.tasks.file_processing.process_audio")
def process_audio_task(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process an uploaded audio file for transcription."""
    start_time = time.time()
    
    try:
        file_path = file_data.get("file_path")
        file_id = file_data.get("file_id")
        user_id = file_data.get("user_id")
        
        logger.info(
            "Starting audio processing task",
            task_id=self.request.id,
            file_id=file_id,
            file_path=file_path
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Processing audio", "progress": 10}
        )
        
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Validate file type
        file_extension = Path(file_path).suffix.lower().lstrip('.')
        if file_extension not in ["mp3", "wav", "m4a", "ogg"]:
            raise ValueError(f"Unsupported audio format: {file_extension}")
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Validating audio file", "progress": 20}
        )
        
        # Call speech service for transcription
        # Note: This would typically use the WebSocket service, but for file processing
        # we might want a REST endpoint for file uploads
        
        # For now, we'll simulate the transcription
        import time
        time.sleep(2)  # Simulate processing time
        
        # Simulate transcription result
        transcription_result = {
            "text": "This is a simulated transcription of the uploaded audio file.",
            "confidence": 0.85,
            "duration": 120.5,
            "word_count": 12,
            "language": file_data.get("language", "en")
        }
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Transcription completed", "progress": 80}
        )
        
        # Process result
        result = {
            "file_id": file_id,
            "task_id": self.request.id,
            "user_id": user_id,
            "transcription": transcription_result.get("text"),
            "confidence": transcription_result.get("confidence"),
            "duration": transcription_result.get("duration"),
            "word_count": transcription_result.get("word_count"),
            "processing_time": time.time() - start_time,
            "status": "completed",
            "timestamp": time.time(),
            "transcription_result": transcription_result
        }
        
        # Clean up temporary file
        try:
            os.remove(file_path)
            logger.info("Temporary audio file cleaned up", file_path=file_path)
        except Exception as e:
            logger.warning("Failed to clean up temporary audio file", file_path=file_path, error=str(e))
        
        logger.info(
            "Audio processing completed",
            task_id=self.request.id,
            file_id=file_id,
            word_count=transcription_result.get("word_count"),
            confidence=transcription_result.get("confidence")
        )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Audio processing failed",
            task_id=self.request.id,
            file_id=file_data.get("file_id"),
            error=str(e),
            processing_time=processing_time
        )
        
        # Clean up on failure
        file_path = file_data.get("file_path")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        
        raise


@celery_app.task(bind=True, name="workers.tasks.file_processing.upload_to_s3")
def upload_to_s3_task(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
    """Upload a processed file to S3 for permanent storage."""
    start_time = time.time()
    
    try:
        file_path = file_data.get("file_path")
        file_id = file_data.get("file_id")
        s3_key = file_data.get("s3_key")
        
        logger.info(
            "Starting S3 upload task",
            task_id=self.request.id,
            file_id=file_id,
            s3_key=s3_key
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Uploading to S3", "progress": 10}
        )
        
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Upload to S3 (in a real implementation)
        # import boto3
        # s3_client = boto3.client('s3')
        # s3_client.upload_file(file_path, settings.s3_bucket, s3_key)
        
        # For now, we'll simulate the upload
        import time
        time.sleep(1)  # Simulate upload time
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Upload completed", "progress": 90}
        )
        
        # Generate presigned URL for access
        s3_url = f"https://{settings.s3_bucket}.s3.amazonaws.com/{s3_key}"
        
        result = {
            "file_id": file_id,
            "task_id": self.request.id,
            "s3_key": s3_key,
            "s3_url": s3_url,
            "bucket": settings.s3_bucket,
            "processing_time": time.time() - start_time,
            "status": "completed",
            "timestamp": time.time()
        }
        
        logger.info(
            "S3 upload completed",
            task_id=self.request.id,
            file_id=file_id,
            s3_key=s3_key
        )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "S3 upload failed",
            task_id=self.request.id,
            file_id=file_data.get("file_id"),
            error=str(e),
            processing_time=processing_time
        )
        raise


@celery_app.task(bind=True, name="workers.tasks.file_processing.cleanup_temp_files")
def cleanup_temp_files_task(self, days_old: int = 1) -> Dict[str, Any]:
    """Clean up temporary files older than specified days."""
    start_time = time.time()
    
    try:
        logger.info(
            "Starting temp files cleanup task",
            task_id=self.request.id,
            days_old=days_old
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Cleaning up temp files", "progress": 10}
        )
        
        # Clean up temp directory
        temp_dir = Path(settings.temp_dir)
        if not temp_dir.exists():
            return {
                "task_id": self.request.id,
                "files_cleaned": 0,
                "processing_time": time.time() - start_time,
                "status": "completed"
            }
        
        # Calculate cutoff time
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        
        files_cleaned = 0
        for file_path in temp_dir.rglob("*"):
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        files_cleaned += 1
                    except Exception as e:
                        logger.warning("Failed to delete temp file", file_path=str(file_path), error=str(e))
        
        processing_time = time.time() - start_time
        
        result = {
            "task_id": self.request.id,
            "days_old": days_old,
            "files_cleaned": files_cleaned,
            "processing_time": processing_time,
            "status": "completed",
            "timestamp": time.time()
        }
        
        logger.info(
            "Temp files cleanup completed",
            task_id=self.request.id,
            files_cleaned=files_cleaned,
            processing_time=processing_time
        )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Temp files cleanup failed",
            task_id=self.request.id,
            error=str(e),
            processing_time=processing_time
        )
        raise


@celery_app.task(bind=True, name="workers.tasks.file_processing.process_batch")
def process_batch_task(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process multiple files in batch."""
    start_time = time.time()
    
    try:
        files = batch_data.get("files", [])
        total_files = len(files)
        
        logger.info(
            "Starting batch file processing task",
            task_id=self.request.id,
            total_files=total_files
        )
        
        results = []
        successful = 0
        failed = 0
        
        for i, file_data in enumerate(files):
            try:
                # Update progress
                progress = int((i / total_files) * 100)
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "status": f"Processing file {i+1}/{total_files}",
                        "progress": progress,
                        "completed": i,
                        "total": total_files
                    }
                )
                
                # Process file based on type
                file_type = file_data.get("file_type", "image")
                if file_type == "image":
                    result = process_image_task.apply_async(
                        args=[file_data],
                        queue=settings.file_processing_queue
                    )
                elif file_type == "audio":
                    result = process_audio_task.apply_async(
                        args=[file_data],
                        queue=settings.file_processing_queue
                    )
                else:
                    raise ValueError(f"Unsupported file type: {file_type}")
                
                # Wait for result
                file_result = result.get(timeout=300)  # 5 minute timeout
                results.append(file_result)
                successful += 1
                
            except Exception as e:
                logger.error(
                    "Failed to process file in batch",
                    file_id=file_data.get("file_id"),
                    error=str(e)
                )
                failed += 1
                results.append({
                    "file_id": file_data.get("file_id"),
                    "status": "failed",
                    "error": str(e)
                })
        
        processing_time = time.time() - start_time
        
        batch_result = {
            "batch_id": batch_data.get("batch_id"),
            "task_id": self.request.id,
            "total_files": total_files,
            "successful": successful,
            "failed": failed,
            "results": results,
            "processing_time": processing_time,
            "status": "completed",
            "timestamp": time.time()
        }
        
        logger.info(
            "Batch file processing completed",
            task_id=self.request.id,
            successful=successful,
            failed=failed,
            processing_time=processing_time
        )
        
        return batch_result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Batch file processing failed",
            task_id=self.request.id,
            error=str(e),
            processing_time=processing_time
        )
        raise
