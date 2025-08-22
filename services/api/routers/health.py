"""Health check endpoints."""

import time
from typing import Dict, Any
from fastapi import APIRouter, Depends
import structlog

from services.common.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "ielts-api",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check for Kubernetes."""
    # TODO: Add database and Redis connectivity checks
    return {
        "status": "ready",
        "timestamp": time.time(),
        "checks": {
            "database": "healthy",  # TODO: Implement actual check
            "redis": "healthy",     # TODO: Implement actual check
            "external_apis": "healthy"  # TODO: Implement actual check
        }
    }


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """Liveness check for Kubernetes."""
    return {
        "status": "alive",
        "timestamp": time.time()
    }


@router.get("/info")
async def service_info() -> Dict[str, Any]:
    """Service information endpoint."""
    return {
        "name": "IELTS AI Platform API",
        "version": "1.0.0",
        "description": "AI-powered IELTS preparation platform API",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth": "/api/v1/auth",
            "speaking": "/api/v1/speaking",
            "writing": "/api/v1/writing",
            "listening": "/api/v1/listening",
            "reading": "/api/v1/reading"
        }
    }
