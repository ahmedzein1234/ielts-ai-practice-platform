"""Main FastAPI application for the Scoring service."""

import sys
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from services.common.logging import setup_logging
from .config import settings
from .models import (
    ScoringRequest, ScoringResponse, BatchScoringRequest, BatchScoringResponse,
    HealthStatus, ServiceInfo, ScoringStats
)
from .scoring_service import scoring_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging(level=settings.log_level)
    logger = structlog.get_logger()
    logger.info("Starting Scoring Service", version="0.1.0")
    
    # Set start time for uptime calculation
    import time
    scoring_service._start_time = time.time()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Scoring Service")


# Create FastAPI app
app = FastAPI(
    title="IELTS Scoring Service",
    description="AI-powered IELTS scoring service with multiple LLM providers",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = structlog.get_logger()


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint."""
    try:
        health_data = await scoring_service.health_check()
        return HealthStatus(**health_data)
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@app.get("/info", response_model=ServiceInfo)
async def get_service_info():
    """Get service information."""
    try:
        info_data = scoring_service.get_service_info()
        return ServiceInfo(**info_data)
    except Exception as e:
        logger.error("Failed to get service info", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get service info: {e}")


@app.get("/stats", response_model=ScoringStats)
async def get_stats():
    """Get service statistics."""
    try:
        stats_data = scoring_service.get_stats()
        return ScoringStats(**stats_data)
    except Exception as e:
        logger.error("Failed to get stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {e}")


@app.post("/score", response_model=ScoringResponse)
async def score_submission(request: ScoringRequest):
    """Score a single submission."""
    try:
        logger.info(
            "Scoring request received",
            task_type=request.task_type.value,
            language=request.language,
            user_id=request.user_id
        )
        
        result = await scoring_service.score_submission(request)
        
        logger.info(
            "Scoring completed",
            task_type=request.task_type.value,
            band_score=result.overall_band_score,
            confidence=result.confidence
        )
        
        return result
        
    except Exception as e:
        logger.error("Scoring failed", error=str(e), task_type=request.task_type.value)
        raise HTTPException(status_code=500, detail=f"Scoring failed: {e}")


@app.post("/score/batch", response_model=BatchScoringResponse)
async def score_batch(request: BatchScoringRequest):
    """Score multiple submissions in batch."""
    try:
        logger.info(
            "Batch scoring request received",
            total_submissions=len(request.submissions)
        )
        
        result = await scoring_service.score_batch(request)
        
        logger.info(
            "Batch scoring completed",
            total=result.total_submissions,
            successful=result.successful,
            failed=result.failed
        )
        
        return result
        
    except Exception as e:
        logger.error("Batch scoring failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Batch scoring failed: {e}")


@app.post("/score/async")
async def score_submission_async(request: ScoringRequest, background_tasks: BackgroundTasks):
    """Score a submission asynchronously (for long-running tasks)."""
    try:
        logger.info(
            "Async scoring request received",
            task_type=request.task_type.value,
            language=request.language
        )
        
        # For now, just return a job ID (in a real implementation, this would queue the task)
        import time
        job_id = f"scoring_{int(time.time())}"
        
        # Add to background tasks (simplified)
        background_tasks.add_task(scoring_service.score_submission, request)
        
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Scoring job queued successfully"
        }
        
    except Exception as e:
        logger.error("Async scoring failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Async scoring failed: {e}")


@app.get("/providers")
async def get_available_providers():
    """Get available LLM providers."""
    try:
        from .llm_client import llm_manager
        
        providers = llm_manager.get_available_providers()
        clients_info = llm_manager.get_clients_info()
        
        return {
            "available_providers": providers,
            "clients_info": clients_info
        }
        
    except Exception as e:
        logger.error("Failed to get providers", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get providers: {e}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
