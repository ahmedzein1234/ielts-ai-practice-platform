"""Main FastAPI application for Speech Service."""

import os
import sys
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

try:
    from services.common.logging import setup_logging
except ImportError:
    # Fallback for direct execution
    import structlog
    def setup_logging(level="INFO", format="json", service_name="speech"):
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer() if format == "json" else structlog.dev.ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
from .config import settings
from .stt import stt_service
from .websocket_manager import websocket_handler, connection_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging(level=settings.log_level)
    
    logger = structlog.get_logger()
    logger.info(
        "Speech service starting",
        host=settings.host,
        port=settings.port,
        whisper_model=settings.whisper_model,
        whisper_device=settings.whisper_device
    )
    
    # Initialize STT service
    try:
        model_info = stt_service.get_model_info()
        logger.info("STT service initialized", model_info=model_info)
    except Exception as e:
        logger.error("Failed to initialize STT service", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Speech service shutting down")


# Create FastAPI app
app = FastAPI(
    title="IELTS Speech Service",
    description="WebSocket STT service using faster-whisper",
    version="0.1.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Add OpenTelemetry instrumentation
if settings.enable_tracing:
    FastAPIInstrumentor.instrument_app(app)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "speech",
        "model_info": stt_service.get_model_info(),
        "connections": connection_manager.get_connection_stats()
    }


@app.get("/health/ready")
async def readiness_check():
    """Readiness check endpoint."""
    try:
        model_info = stt_service.get_model_info()
        if model_info.get("status") != "loaded":
            return {"status": "not_ready", "reason": "STT model not loaded"}
        
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "reason": str(e)}


@app.get("/health/live")
async def liveness_check():
    """Liveness check endpoint."""
    return {"status": "alive"}


@app.get("/info")
async def service_info():
    """Service information endpoint."""
    return {
        "service": "speech",
        "version": "0.1.0",
        "config": {
            "whisper_model": settings.whisper_model,
            "whisper_device": settings.whisper_device,
            "whisper_compute_type": settings.whisper_compute_type,
            "sample_rate": settings.sample_rate,
            "chunk_duration": settings.chunk_duration,
            "max_audio_duration": settings.max_audio_duration
        },
        "model_info": stt_service.get_model_info()
    }


@app.websocket("/ws/speech")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time speech recognition."""
    await websocket_handler.handle_websocket(websocket)


@app.get("/stats")
async def get_stats():
    """Get service statistics."""
    return {
        "connections": connection_manager.get_connection_stats(),
        "model_info": stt_service.get_model_info()
    }


@app.get("/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """Get all sessions for a user."""
    sessions = connection_manager.get_user_sessions(user_id)
    session_infos = []
    
    for session_id in sessions:
        session_info = connection_manager.get_session_info(session_id)
        if session_info:
            session_infos.append(session_info.model_dump())
    
    return {
        "user_id": user_id,
        "sessions": session_infos,
        "count": len(session_infos)
    }


def main():
    """Main entry point for the speech service."""
    import uvicorn
    
    uvicorn.run(
        "services.speech.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()
