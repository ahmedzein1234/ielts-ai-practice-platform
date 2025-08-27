from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import structlog
import uvicorn
from contextlib import asynccontextmanager
import asyncio
from typing import Dict, List
import json
import base64

from config import settings
from api.routes import router
from api.websocket import EnhancedWebSocketManager
from services.tutor_service import TutorService
from services.recommendation_service import RecommendationService
from services.learning_path_service import LearningPathService
from services.advanced_tutor_service import AdvancedTutorService
from services.enhanced_learning_path_service import EnhancedLearningPathService
from services.speech_processor import SpeechProcessor
from models.advanced_tutor import InteractionMode

# Configure structured logging
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
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# WebSocket connection manager
websocket_manager = EnhancedWebSocketManager()

# Service instances
tutor_service = TutorService()
recommendation_service = RecommendationService()
learning_path_service = LearningPathService()
advanced_tutor_service = AdvancedTutorService()
enhanced_learning_path_service = EnhancedLearningPathService()
speech_processor = SpeechProcessor()

# Inject service instances into API routes
import api.routes
api.routes.tutor_service = tutor_service
api.routes.recommendation_service = recommendation_service
api.routes.learning_path_service = learning_path_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting AI Tutor Service", version=settings.version)
    
    # Initialize services
    await tutor_service.initialize()
    await recommendation_service.initialize()
    await learning_path_service.initialize()
    await advanced_tutor_service.initialize()
    await enhanced_learning_path_service.initialize()
    
    logger.info("AI Tutor Service started successfully")
    yield
    
    # Cleanup
    logger.info("Shutting down AI Tutor Service")
    await websocket_manager.disconnect_all()

# Create FastAPI app
app = FastAPI(
    title="IELTS AI Tutor Service",
    description="AI-powered tutoring and personalized learning for IELTS preparation",
    version=settings.version,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts
)

# Include routers
app.include_router(router, prefix="/api/v1")

# WebSocket endpoint for real-time tutoring
@app.websocket("/ws/tutor/{user_id}")
async def websocket_tutor_endpoint(websocket: WebSocket, user_id: str):
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle message using enhanced WebSocket manager
            await websocket_manager.handle_message(user_id, message)
            
            # Process message based on type
            if message.get("type") == "user_message":
                # Use advanced tutor service for enhanced responses
                response = await advanced_tutor_service.advanced_chat(
                    user_id=user_id,
                    message=message.get("message", ""),
                    interaction_mode=InteractionMode(message.get("interaction_mode", "text")),
                    context=message.get("context", {})
                )
                
                await websocket_manager.send_multi_modal_response(user_id, response.dict())
                
            elif message.get("type") == "audio_message":
                # Process audio message
                audio_data = base64.b64decode(message.get("audio_data", ""))
                speech_result = await speech_processor.process_audio(
                    audio_data=audio_data,
                    user_id=user_id,
                    format_type=message.get("format", "wav")
                )
                
                # Send speech analysis
                await websocket_manager.send_speech_analysis(user_id, speech_result)
                
                # Generate tutor response based on speech analysis
                if speech_result.get("analysis"):
                    response = await advanced_tutor_service.advanced_chat(
                        user_id=user_id,
                        message="[Voice input processed]",
                        interaction_mode=InteractionMode.VOICE,
                        context={"speech_analysis": speech_result}
                    )
                    await websocket_manager.send_multi_modal_response(user_id, response.dict())
                
            elif message.get("type") == "get_recommendations":
                recommendations = await recommendation_service.get_recommendations(
                    user_id=user_id,
                    module=message.get("module"),
                    limit=message.get("limit", 5)
                )
                
                await websocket_manager.send_message(user_id, {
                    "type": "recommendations",
                    "data": recommendations
                })
                
            elif message.get("type") == "get_learning_path":
                # Use enhanced learning path service
                learning_path = await enhanced_learning_path_service.generate_enhanced_path(
                    user_id=user_id,
                    target_score=message.get("target_score"),
                    timeframe=message.get("timeframe", "30")
                )
                
                await websocket_manager.send_message(user_id, {
                    "type": "learning_path",
                    "data": learning_path
                })
                
            elif message.get("type") == "voice_start":
                # Handle voice recording start
                await websocket_manager.send_message(user_id, {
                    "type": "voice_started",
                    "data": {"message": "Voice recording started"}
                })
                
            elif message.get("type") == "voice_stop":
                # Handle voice recording stop
                await websocket_manager.send_message(user_id, {
                    "type": "voice_processing",
                    "data": {"message": "Processing voice input..."}
                })
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id)
        logger.info("WebSocket disconnected", user_id=user_id)
    except Exception as e:
        logger.error("WebSocket error", user_id=user_id, error=str(e))
        websocket_manager.disconnect(user_id)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-tutor",
        "version": settings.version
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "IELTS AI Tutor Service",
        "version": settings.version,
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
