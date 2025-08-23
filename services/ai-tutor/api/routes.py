from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional, Any
import structlog
from datetime import datetime

from services.tutor_service import TutorService
from services.recommendation_service import RecommendationService
from services.learning_path_service import LearningPathService

logger = structlog.get_logger()

router = APIRouter()

# Service instances (will be injected)
tutor_service: Optional[TutorService] = None
recommendation_service: Optional[RecommendationService] = None
learning_path_service: Optional[LearningPathService] = None

def get_tutor_service() -> TutorService:
    if tutor_service is None:
        raise HTTPException(status_code=503, detail="Tutor service not available")
    return tutor_service

def get_recommendation_service() -> RecommendationService:
    if recommendation_service is None:
        raise HTTPException(status_code=503, detail="Recommendation service not available")
    return recommendation_service

def get_learning_path_service() -> LearningPathService:
    if learning_path_service is None:
        raise HTTPException(status_code=503, detail="Learning path service not available")
    return learning_path_service

@router.post("/chat")
async def chat_with_tutor(
    user_id: str,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    tutor_service: TutorService = Depends(get_tutor_service)
) -> Dict[str, Any]:
    """Chat with AI tutor"""
    try:
        logger.info("Chat request received", user_id=user_id, message_length=len(message))
        
        response = await tutor_service.chat(user_id, message, context)
        
        return {
            "success": True,
            "data": response
        }
        
    except Exception as e:
        logger.error("Error in chat endpoint", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process chat request")

@router.post("/feedback")
async def get_personalized_feedback(
    user_id: str,
    module: str,
    performance_data: Dict[str, Any],
    tutor_service: TutorService = Depends(get_tutor_service)
) -> Dict[str, Any]:
    """Get personalized feedback based on performance"""
    try:
        logger.info("Feedback request received", user_id=user_id, module=module)
        
        feedback = await tutor_service.get_personalized_feedback(user_id, module, performance_data)
        
        return {
            "success": True,
            "data": feedback
        }
        
    except Exception as e:
        logger.error("Error in feedback endpoint", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate feedback")

@router.get("/recommendations")
async def get_recommendations(
    user_id: str,
    module: Optional[str] = Query(None, description="Specific module to get recommendations for"),
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations to return"),
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
) -> Dict[str, Any]:
    """Get personalized recommendations"""
    try:
        logger.info("Recommendations request received", user_id=user_id, module=module, limit=limit)
        
        recommendations = await recommendation_service.get_recommendations(user_id, module, limit)
        
        return {
            "success": True,
            "data": recommendations
        }
        
    except Exception as e:
        logger.error("Error in recommendations endpoint", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

@router.get("/recommendations/daily")
async def get_daily_recommendations(
    user_id: str,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
) -> Dict[str, Any]:
    """Get daily personalized recommendations"""
    try:
        logger.info("Daily recommendations request received", user_id=user_id)
        
        daily_recommendations = await recommendation_service.get_daily_recommendations(user_id)
        
        return {
            "success": True,
            "data": daily_recommendations
        }
        
    except Exception as e:
        logger.error("Error in daily recommendations endpoint", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get daily recommendations")

@router.get("/adaptive-content")
async def get_adaptive_content(
    user_id: str,
    module: str,
    current_difficulty: str,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
) -> Dict[str, Any]:
    """Get adaptive content based on user performance"""
    try:
        logger.info("Adaptive content request received", user_id=user_id, module=module, difficulty=current_difficulty)
        
        adaptive_content = await recommendation_service.get_adaptive_content(user_id, module, current_difficulty)
        
        return {
            "success": True,
            "data": [content.dict() for content in adaptive_content]
        }
        
    except Exception as e:
        logger.error("Error in adaptive content endpoint", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get adaptive content")

@router.post("/learning-paths/generate")
async def generate_learning_path(
    user_id: str,
    target_score: float,
    timeframe: str = "30",
    learning_path_service: LearningPathService = Depends(get_learning_path_service)
) -> Dict[str, Any]:
    """Generate personalized learning path"""
    try:
        logger.info("Learning path generation request received", user_id=user_id, target_score=target_score, timeframe=timeframe)
        
        learning_path = await learning_path_service.generate_path(user_id, target_score, timeframe)
        
        return {
            "success": True,
            "data": learning_path
        }
        
    except Exception as e:
        logger.error("Error in learning path generation endpoint", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate learning path")

@router.put("/learning-paths/{path_id}/progress")
async def update_path_progress(
    path_id: str,
    user_id: str,
    completed_step_id: str,
    learning_path_service: LearningPathService = Depends(get_learning_path_service)
) -> Dict[str, Any]:
    """Update learning path progress"""
    try:
        logger.info("Path progress update request received", user_id=user_id, path_id=path_id, step_id=completed_step_id)
        
        updated_path = await learning_path_service.update_path_progress(user_id, path_id, completed_step_id)
        
        return {
            "success": True,
            "data": updated_path
        }
        
    except Exception as e:
        logger.error("Error in path progress update endpoint", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update path progress")

@router.get("/learning-paths/recommendations")
async def get_path_recommendations(
    user_id: str,
    learning_path_service: LearningPathService = Depends(get_learning_path_service)
) -> Dict[str, Any]:
    """Get recommended learning paths"""
    try:
        logger.info("Path recommendations request received", user_id=user_id)
        
        path_recommendations = await learning_path_service.get_path_recommendations(user_id)
        
        return {
            "success": True,
            "data": path_recommendations
        }
        
    except Exception as e:
        logger.error("Error in path recommendations endpoint", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get path recommendations")

@router.post("/sessions/start")
async def start_tutoring_session(
    user_id: str,
    tutor_service: TutorService = Depends(get_tutor_service)
) -> Dict[str, Any]:
    """Start a new tutoring session"""
    try:
        logger.info("Session start request received", user_id=user_id)
        
        session_id = await tutor_service.start_session(user_id)
        
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "user_id": user_id,
                "start_time": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error("Error in session start endpoint", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to start session")

@router.post("/sessions/{session_id}/end")
async def end_tutoring_session(
    session_id: str,
    user_satisfaction: Optional[int] = None,
    tutor_service: TutorService = Depends(get_tutor_service)
) -> Dict[str, Any]:
    """End a tutoring session"""
    try:
        logger.info("Session end request received", session_id=session_id)
        
        session_summary = await tutor_service.end_session(session_id, user_satisfaction)
        
        return {
            "success": True,
            "data": session_summary
        }
        
    except Exception as e:
        logger.error("Error in session end endpoint", session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to end session")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-tutor",
        "timestamp": datetime.utcnow().isoformat()
    }
