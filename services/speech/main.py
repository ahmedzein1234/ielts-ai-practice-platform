"""Main FastAPI application for Speech Service."""

import os
import sys
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from pydantic import BaseModel
import time

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
    description="Speech processing service for audio analysis", 
    version="0.1.0"
)

# Add middleware
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Add OpenTelemetry instrumentation
if settings.enable_tracing:
    FastAPIInstrumentor.instrument_app(app)


class HealthStatus(BaseModel): 
    status: str
    service: str
    timestamp: str
    uptime: float

class SpeechRequest(BaseModel): 
    audio_url: str = None
    text: str = None

class SpeechResponse(BaseModel): 
    transcribed_text: str
    confidence: float
    language: str
    processing_time: float
    pronunciation_score: float = None

class EnhancedAnalysisRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    sample_rate: int = 16000
    language: str = "en"
    include_pronunciation: bool = True
    include_fluency: bool = True
    include_accent: bool = True
    target_band: float = None

class EnhancedAnalysisResponse(BaseModel):
    transcription: dict
    pronunciation: dict = None
    fluency: dict = None
    accent: dict = None
    overall_score: float
    band_level: str
    recommendations: list
    practice_suggestions: list

_start_time = time.time()

@app.get("/health", response_model=HealthStatus)
async def health_check():
    uptime = time.time() - _start_time
    return HealthStatus(
        status="healthy",
        service="speech",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        uptime=uptime,
    )

@app.post("/transcribe", response_model=SpeechResponse)
async def transcribe_audio(request: SpeechRequest):
    start_time = time.time()
    
    if request.audio_url:
        transcribed_text = "Sample transcribed text from audio URL"
    elif request.text:
        transcribed_text = request.text
    else:
        transcribed_text = "Sample transcribed text from audio"
    
    return SpeechResponse(
        transcribed_text=transcribed_text,
        confidence=0.92,
        language="en",
        processing_time=1.2,
        pronunciation_score=7.5,
    )

@app.post("/analyze", response_model=EnhancedAnalysisResponse)
async def analyze_speech(request: EnhancedAnalysisRequest):
    """Enhanced speech analysis with pronunciation, fluency, and accent detection."""
    start_time = time.time()
    
    # Simulate enhanced analysis (in production, this would use the actual models)
    processing_time = time.time() - start_time
    
    # Mock transcription
    transcription = {
        "text": "This is a sample transcription for enhanced analysis",
        "confidence": 0.92,
        "language": "en",
        "processing_time": processing_time,
        "segments": []
    }
    
    # Mock pronunciation analysis
    pronunciation = {
        "overall_score": 7.2,
        "phoneme_accuracy": 0.85,
        "word_stress": 0.80,
        "sentence_stress": 0.75,
        "intonation": 0.82,
        "clarity": 0.88,
        "feedback": [
            "Good overall pronunciation",
            "Work on word stress patterns",
            "Practice sentence intonation"
        ]
    }
    
    # Mock fluency analysis
    fluency = {
        "words_per_minute": 135.0,
        "pause_frequency": 4.2,
        "pause_duration": 0.6,
        "filler_words": 2,
        "filler_frequency": 1.5,
        "speech_continuity": 0.85,
        "hesitation_ratio": 0.15,
        "feedback": [
            "Good speaking pace",
            "Reduce pauses slightly",
            "Minimal filler word usage"
        ]
    }
    
    # Mock accent analysis
    accent = {
        "detected_accent": "British English",
        "accent_confidence": 0.78,
        "accent_features": [
            "Clear vowel pronunciation",
            "Standard British intonation"
        ],
        "comprehensibility": 0.87,
        "feedback": [
            "Good accent comprehensibility",
            "Maintain consistent pronunciation"
        ]
    }
    
    # Calculate overall score
    overall_score = 7.1
    band_level = "Band 7"
    
    recommendations = [
        "Focus on pronunciation improvement",
        "Practice speaking at natural pace",
        "Work on reducing filler words"
    ]
    
    practice_suggestions = [
        "Practice minimal pairs for better pronunciation",
        "Use tongue twisters to improve fluency",
        "Listen to native speakers and mimic patterns",
        "Join conversation groups for regular practice"
    ]
    
    return EnhancedAnalysisResponse(
        transcription=transcription,
        pronunciation=pronunciation,
        fluency=fluency,
        accent=accent,
        overall_score=overall_score,
        band_level=band_level,
        recommendations=recommendations,
        practice_suggestions=practice_suggestions
    )

@app.get("/")
async def root():
    return {
        "message": "IELTS Speech Service",
        "version": "0.1.0",
        "endpoints": ["/health", "/transcribe", "/analyze"],
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
