"""
FastAPI routes for Advanced Learning Features (Phase 3).
Includes endpoints for learning paths, progress tracking, recommendations, and skill mastery.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
import structlog

from ..models.learning import LearningPath, SkillMastery, LearningPathStatus, RecommendationType, SkillLevel

from ..database import get_db
from ..auth import get_current_user
from ..models.user import User
from ..services.learning_service import LearningService
from ..schemas.learning import (
    LearningPathCreate, LearningPathResponse, LearningPathUpdate, LearningPathSearchParams,
    LearningObjectiveCreate, LearningObjectiveResponse, LearningObjectiveUpdate,
    UserProgressCreate, UserProgressResponse, UserProgressUpdate,
    RecommendationCreate, RecommendationResponse, RecommendationUpdate, RecommendationSearchParams,
    SkillMasteryCreate, SkillMasteryResponse, SkillMasteryUpdate, SkillMasterySearchParams,
    LearningDashboardStats, SkillGapAnalysis, PersonalizedInsights
)

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/learning", tags=["learning"])

# Helper function for role-based access
def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.value != required_role and current_user.role.value != "admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# Learning Path Management
@router.post("/paths", response_model=LearningPathResponse)
async def create_learning_path(
    path_data: LearningPathCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new personalized learning path for the current user."""
    try:
        learning_service = LearningService(db)
        learning_path = learning_service.create_learning_path(current_user.id, path_data)
        return learning_path
    except Exception as e:
        logger.error("Failed to create learning path", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create learning path")

@router.get("/paths", response_model=List[LearningPathResponse])
async def get_learning_paths(
    status: Optional[str] = Query(None, description="Filter by path status"),
    target_band_score_min: Optional[float] = Query(None, ge=0.0, le=9.0),
    target_band_score_max: Optional[float] = Query(None, ge=0.0, le=9.0),
    completion_percentage_min: Optional[float] = Query(None, ge=0.0, le=100.0),
    completion_percentage_max: Optional[float] = Query(None, ge=0.0, le=100.0),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get learning paths for the current user with filtering."""
    try:
        params = LearningPathSearchParams(
            status=LearningPathStatus(status) if status else None,
            target_band_score_min=target_band_score_min,
            target_band_score_max=target_band_score_max,
            completion_percentage_min=completion_percentage_min,
            completion_percentage_max=completion_percentage_max,
            limit=limit,
            offset=offset
        )
        
        learning_service = LearningService(db)
        learning_paths = learning_service.get_user_learning_paths(current_user.id, params)
        return learning_paths
    except Exception as e:
        logger.error("Failed to get learning paths", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get learning paths")

@router.get("/paths/{path_id}", response_model=LearningPathResponse)
async def get_learning_path(
    path_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific learning path by ID."""
    try:
        learning_service = LearningService(db)
        learning_path = learning_service.db.query(LearningPath).filter(
            and_(
                LearningPath.id == path_id,
                LearningPath.user_id == current_user.id
            )
        ).first()
        
        if not learning_path:
            raise HTTPException(status_code=404, detail="Learning path not found")
        
        return learning_path
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get learning path", path_id=path_id, user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get learning path")

@router.put("/paths/{path_id}", response_model=LearningPathResponse)
async def update_learning_path(
    path_id: str,
    update_data: LearningPathUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a learning path."""
    try:
        learning_service = LearningService(db)
        learning_path = learning_service.update_learning_path(path_id, update_data)
        return learning_path
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to update learning path", path_id=path_id, user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update learning path")

@router.post("/objectives/{objective_id}/complete", response_model=LearningObjectiveResponse)
async def complete_learning_objective(
    objective_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a learning objective as completed."""
    try:
        learning_service = LearningService(db)
        objective = learning_service.complete_learning_objective(objective_id, current_user.id)
        return objective
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to complete learning objective", objective_id=objective_id, user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to complete learning objective")

# Progress Tracking
@router.post("/progress", response_model=UserProgressResponse)
async def record_progress(
    progress_data: UserProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record user progress for learning activities."""
    try:
        learning_service = LearningService(db)
        progress = learning_service.record_user_progress(current_user.id, progress_data)
        return progress
    except Exception as e:
        logger.error("Failed to record progress", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to record progress")

@router.get("/progress/summary")
async def get_progress_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a summary of user progress over a period."""
    try:
        learning_service = LearningService(db)
        summary = learning_service.get_user_progress_summary(current_user.id, days)
        return summary
    except Exception as e:
        logger.error("Failed to get progress summary", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get progress summary")

# AI Recommendations
@router.post("/recommendations/generate")
async def generate_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations to generate"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered recommendations for the current user."""
    try:
        learning_service = LearningService(db)
        recommendations = learning_service.generate_recommendations(current_user.id, limit)
        return {"message": f"Generated {len(recommendations)} recommendations", "count": len(recommendations)}
    except Exception as e:
        logger.error("Failed to generate recommendations", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")

@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    recommendation_type: Optional[str] = Query(None, description="Filter by recommendation type"),
    is_viewed: Optional[bool] = Query(None, description="Filter by viewed status"),
    is_accepted: Optional[bool] = Query(None, description="Filter by accepted status"),
    confidence_score_min: Optional[float] = Query(None, ge=0.0, le=1.0),
    priority_score_min: Optional[float] = Query(None, ge=0.0, le=1.0),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recommendations for the current user with filtering."""
    try:
        params = RecommendationSearchParams(
            recommendation_type=RecommendationType(recommendation_type) if recommendation_type else None,
            is_viewed=is_viewed,
            is_accepted=is_accepted,
            confidence_score_min=confidence_score_min,
            priority_score_min=priority_score_min,
            limit=limit,
            offset=offset
        )
        
        learning_service = LearningService(db)
        recommendations = learning_service.get_user_recommendations(current_user.id, params)
        return recommendations
    except Exception as e:
        logger.error("Failed to get recommendations", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

@router.put("/recommendations/{recommendation_id}/view", response_model=RecommendationResponse)
async def mark_recommendation_viewed(
    recommendation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a recommendation as viewed."""
    try:
        learning_service = LearningService(db)
        recommendation = learning_service.mark_recommendation_viewed(recommendation_id, current_user.id)
        return recommendation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to mark recommendation as viewed", recommendation_id=recommendation_id, user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to mark recommendation as viewed")

@router.put("/recommendations/{recommendation_id}/accept", response_model=RecommendationResponse)
async def accept_recommendation(
    recommendation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a recommendation as accepted."""
    try:
        learning_service = LearningService(db)
        recommendation = learning_service.accept_recommendation(recommendation_id, current_user.id)
        return recommendation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to accept recommendation", recommendation_id=recommendation_id, user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to accept recommendation")

# Skill Mastery
@router.post("/skills/mastery", response_model=SkillMasteryResponse)
async def update_skill_mastery(
    skill_data: SkillMasteryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update or create skill mastery record."""
    try:
        learning_service = LearningService(db)
        mastery = learning_service.update_skill_mastery(current_user.id, skill_data)
        return mastery
    except Exception as e:
        logger.error("Failed to update skill mastery", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update skill mastery")

@router.get("/skills/mastery", response_model=List[SkillMasteryResponse])
async def get_skill_mastery(
    skill_name: Optional[str] = Query(None, description="Filter by skill name"),
    module_type: Optional[str] = Query(None, description="Filter by module type"),
    current_level: Optional[str] = Query(None, description="Filter by current level"),
    mastery_score_min: Optional[float] = Query(None, ge=0.0, le=1.0),
    mastery_score_max: Optional[float] = Query(None, ge=0.0, le=1.0),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get skill mastery records for the current user with filtering."""
    try:
        params = SkillMasterySearchParams(
            skill_name=skill_name,
            module_type=module_type,
            current_level=SkillLevel(current_level) if current_level else None,
            mastery_score_min=mastery_score_min,
            mastery_score_max=mastery_score_max,
            limit=limit,
            offset=offset
        )
        
        learning_service = LearningService(db)
        skill_mastery = learning_service.db.query(SkillMastery).filter(SkillMastery.user_id == current_user.id)
        
        # Apply filters
        if params.skill_name:
            skill_mastery = skill_mastery.filter(SkillMastery.skill_name == params.skill_name)
        if params.module_type:
            skill_mastery = skill_mastery.filter(SkillMastery.module_type == params.module_type)
        if params.current_level:
            skill_mastery = skill_mastery.filter(SkillMastery.current_level == params.current_level)
        if params.mastery_score_min is not None:
            skill_mastery = skill_mastery.filter(SkillMastery.mastery_score >= params.mastery_score_min)
        if params.mastery_score_max is not None:
            skill_mastery = skill_mastery.filter(SkillMastery.mastery_score <= params.mastery_score_max)
        
        skill_mastery = skill_mastery.offset(params.offset).limit(params.limit).all()
        return skill_mastery
    except Exception as e:
        logger.error("Failed to get skill mastery", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get skill mastery")

@router.get("/skills/gap-analysis", response_model=List[SkillGapAnalysis])
async def get_skill_gap_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get skill gap analysis for the current user."""
    try:
        learning_service = LearningService(db)
        gap_analysis = learning_service.get_skill_gap_analysis(current_user.id)
        return gap_analysis
    except Exception as e:
        logger.error("Failed to get skill gap analysis", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get skill gap analysis")

# Analytics and Insights
@router.get("/dashboard/stats", response_model=LearningDashboardStats)
async def get_learning_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive learning dashboard statistics."""
    try:
        learning_service = LearningService(db)
        stats = learning_service.get_learning_dashboard_stats(current_user.id)
        return stats
    except Exception as e:
        logger.error("Failed to get dashboard stats", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get dashboard stats")

@router.get("/insights/personalized", response_model=PersonalizedInsights)
async def get_personalized_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized learning insights for the current user."""
    try:
        learning_service = LearningService(db)
        insights = learning_service.get_personalized_insights(current_user.id)
        return insights
    except Exception as e:
        logger.error("Failed to get personalized insights", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get personalized insights")

# Admin endpoints (for tutors and administrators)
@router.get("/admin/user/{user_id}/paths", response_model=List[LearningPathResponse])
async def get_user_learning_paths_admin(
    user_id: str,
    current_user: User = Depends(require_role("tutor")),
    db: Session = Depends(get_db)
):
    """Get learning paths for a specific user (admin/tutor only)."""
    try:
        learning_service = LearningService(db)
        params = LearningPathSearchParams(limit=100, offset=0)
        learning_paths = learning_service.get_user_learning_paths(user_id, params)
        return learning_paths
    except Exception as e:
        logger.error("Failed to get user learning paths (admin)", user_id=user_id, admin_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get user learning paths")

@router.get("/admin/user/{user_id}/progress")
async def get_user_progress_admin(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_role("tutor")),
    db: Session = Depends(get_db)
):
    """Get progress summary for a specific user (admin/tutor only)."""
    try:
        learning_service = LearningService(db)
        summary = learning_service.get_user_progress_summary(user_id, days)
        return summary
    except Exception as e:
        logger.error("Failed to get user progress (admin)", user_id=user_id, admin_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get user progress")

@router.get("/admin/user/{user_id}/insights", response_model=PersonalizedInsights)
async def get_user_insights_admin(
    user_id: str,
    current_user: User = Depends(require_role("tutor")),
    db: Session = Depends(get_db)
):
    """Get personalized insights for a specific user (admin/tutor only)."""
    try:
        learning_service = LearningService(db)
        insights = learning_service.get_personalized_insights(user_id)
        return insights
    except Exception as e:
        logger.error("Failed to get user insights (admin)", user_id=user_id, admin_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get user insights")
