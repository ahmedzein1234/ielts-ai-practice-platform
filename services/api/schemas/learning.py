"""
Pydantic schemas for Advanced Learning Features (Phase 3).
Includes request/response models for learning paths, progress tracking, recommendations, and skill mastery.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class LearningPathStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ARCHIVED = "archived"

class LearningObjectiveType(str, Enum):
    SKILL_IMPROVEMENT = "skill_improvement"
    CONTENT_MASTERY = "content_mastery"
    ASSESSMENT_TARGET = "assessment_target"
    TIME_BASED = "time_based"

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    UPPER_INTERMEDIATE = "upper_intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class RecommendationType(str, Enum):
    CONTENT_BASED = "content_based"
    COLLABORATIVE = "collaborative"
    PERFORMANCE_BASED = "performance_based"
    CONTEXT_AWARE = "context_aware"
    SPACED_REPETITION = "spaced_repetition"

# Base Models
class LearningPathBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    target_band_score: Optional[float] = Field(None, ge=0.0, le=9.0)
    estimated_duration_days: Optional[int] = Field(None, ge=1, le=365)
    learning_style: Optional[str] = Field(None, max_length=50)

class LearningObjectiveBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    objective_type: LearningObjectiveType
    target_skill: Optional[str] = Field(None, max_length=100)
    target_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    estimated_time_minutes: Optional[int] = Field(None, ge=1, le=480)
    difficulty_level: Optional[SkillLevel] = None
    sort_order: int = Field(0, ge=0)

class UserProgressBase(BaseModel):
    time_spent_minutes: int = Field(0, ge=0)
    completion_rate: float = Field(0.0, ge=0.0, le=100.0)
    score: Optional[float] = Field(None, ge=0.0, le=100.0)
    accuracy: Optional[float] = Field(None, ge=0.0, le=100.0)
    engagement_level: Optional[int] = Field(None, ge=1, le=10)
    difficulty_rating: Optional[int] = Field(None, ge=1, le=10)
    confidence_level: Optional[int] = Field(None, ge=1, le=10)
    device_type: Optional[str] = Field(None, max_length=50)
    study_environment: Optional[str] = Field(None, max_length=50)
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    focus_level: Optional[int] = Field(None, ge=1, le=10)

class RecommendationBase(BaseModel):
    recommendation_type: RecommendationType
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    reasoning: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    priority_score: float = Field(..., ge=0.0, le=1.0)
    estimated_impact: Optional[float] = Field(None, ge=0.0, le=1.0)
    time_to_complete: Optional[int] = Field(None, ge=1, le=1440)  # minutes

class SkillMasteryBase(BaseModel):
    skill_name: str = Field(..., min_length=1, max_length=100)
    module_type: str = Field(..., min_length=1, max_length=50)
    current_level: SkillLevel
    mastery_score: float = Field(..., ge=0.0, le=1.0)
    total_attempts: int = Field(0, ge=0)
    successful_attempts: int = Field(0, ge=0)
    average_score: float = Field(0.0, ge=0.0, le=100.0)
    best_score: float = Field(0.0, ge=0.0, le=100.0)
    total_time_spent: int = Field(0, ge=0)  # minutes

# Create Models
class LearningPathCreate(LearningPathBase):
    pass

class LearningObjectiveCreate(LearningObjectiveBase):
    content_items: Optional[List[str]] = None
    required_activities: Optional[List[str]] = None
    optional_activities: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    unlocks: Optional[List[str]] = None

class UserProgressCreate(UserProgressBase):
    learning_path_id: Optional[str] = None
    content_item_id: Optional[str] = None
    test_session_id: Optional[str] = None

class RecommendationCreate(RecommendationBase):
    content_item_id: Optional[str] = None
    learning_path_id: Optional[str] = None
    action_type: Optional[str] = Field(None, max_length=100)
    action_data: Optional[Dict[str, Any]] = None
    context_data: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None

class SkillMasteryCreate(SkillMasteryBase):
    pass

# Update Models
class LearningPathUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[LearningPathStatus] = None
    target_band_score: Optional[float] = Field(None, ge=0.0, le=9.0)
    estimated_duration_days: Optional[int] = Field(None, ge=1, le=365)
    difficulty_progression: Optional[Dict[str, Any]] = None
    learning_style: Optional[str] = Field(None, max_length=50)
    path_structure: Optional[Dict[str, Any]] = None
    skill_gaps: Optional[List[str]] = None
    priority_areas: Optional[List[str]] = None
    current_position: Optional[int] = Field(None, ge=0)
    completion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)

class LearningObjectiveUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    target_skill: Optional[str] = Field(None, max_length=100)
    target_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    estimated_time_minutes: Optional[int] = Field(None, ge=1, le=480)
    difficulty_level: Optional[SkillLevel] = None
    content_items: Optional[List[str]] = None
    required_activities: Optional[List[str]] = None
    optional_activities: Optional[List[str]] = None
    sort_order: Optional[int] = Field(None, ge=0)
    is_completed: Optional[bool] = None
    actual_time_spent: Optional[int] = Field(None, ge=0)
    prerequisites: Optional[List[str]] = None
    unlocks: Optional[List[str]] = None

class UserProgressUpdate(BaseModel):
    time_spent_minutes: Optional[int] = Field(None, ge=0)
    completion_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    score: Optional[float] = Field(None, ge=0.0, le=100.0)
    accuracy: Optional[float] = Field(None, ge=0.0, le=100.0)
    engagement_level: Optional[int] = Field(None, ge=1, le=10)
    difficulty_rating: Optional[int] = Field(None, ge=1, le=10)
    confidence_level: Optional[int] = Field(None, ge=1, le=10)
    learning_velocity: Optional[float] = None
    session_end: Optional[datetime] = None
    session_duration: Optional[int] = Field(None, ge=0)
    device_type: Optional[str] = Field(None, max_length=50)
    study_environment: Optional[str] = Field(None, max_length=50)
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    focus_level: Optional[int] = Field(None, ge=1, le=10)

class RecommendationUpdate(BaseModel):
    is_viewed: Optional[bool] = None
    is_accepted: Optional[bool] = None
    viewed_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None

class SkillMasteryUpdate(BaseModel):
    current_level: Optional[SkillLevel] = None
    mastery_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    total_attempts: Optional[int] = Field(None, ge=0)
    successful_attempts: Optional[int] = Field(None, ge=0)
    average_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    best_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    total_time_spent: Optional[int] = Field(None, ge=0)
    last_practiced: Optional[datetime] = None
    days_since_last_practice: Optional[int] = Field(None, ge=0)
    improvement_rate: Optional[float] = None
    learning_curve: Optional[Dict[str, Any]] = None
    identified_weaknesses: Optional[List[str]] = None
    identified_strengths: Optional[List[str]] = None

# Response Models
class LearningPathResponse(LearningPathBase):
    id: str
    user_id: str
    status: LearningPathStatus
    difficulty_progression: Optional[Dict[str, Any]] = None
    path_structure: Optional[Dict[str, Any]] = None
    skill_gaps: Optional[List[str]] = None
    priority_areas: Optional[List[str]] = None
    current_position: int
    completion_percentage: float
    total_objectives: int
    completed_objectives: int
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LearningObjectiveResponse(LearningObjectiveBase):
    id: str
    learning_path_id: str
    content_items: Optional[List[str]] = None
    required_activities: Optional[List[str]] = None
    optional_activities: Optional[List[str]] = None
    is_completed: bool
    completion_date: Optional[datetime] = None
    actual_time_spent: Optional[int] = None
    prerequisites: Optional[List[str]] = None
    unlocks: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserProgressResponse(UserProgressBase):
    id: str
    user_id: str
    learning_path_id: Optional[str] = None
    content_item_id: Optional[str] = None
    test_session_id: Optional[str] = None
    learning_velocity: Optional[float] = None
    session_start: datetime
    session_end: Optional[datetime] = None
    session_duration: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RecommendationResponse(RecommendationBase):
    id: str
    user_id: str
    content_item_id: Optional[str] = None
    learning_path_id: Optional[str] = None
    action_type: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    is_viewed: bool
    is_accepted: Optional[bool] = None
    viewed_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    context_data: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SkillMasteryResponse(SkillMasteryBase):
    id: str
    user_id: str
    previous_level: Optional[SkillLevel] = None
    last_practiced: Optional[datetime] = None
    days_since_last_practice: Optional[int] = None
    improvement_rate: Optional[float] = None
    learning_curve: Optional[Dict[str, Any]] = None
    identified_weaknesses: Optional[List[str]] = None
    identified_strengths: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    level_upgraded_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Analytics Models
class LearningAnalyticsResponse(BaseModel):
    id: str
    user_id: str
    date: datetime
    total_study_time: int
    sessions_count: int
    content_items_completed: int
    objectives_completed: int
    average_score: float
    average_accuracy: float
    improvement_rate: Optional[float] = None
    engagement_score: float
    focus_score: float
    consistency_score: float
    preferred_study_times: Optional[List[str]] = None
    preferred_content_types: Optional[List[str]] = None
    learning_velocity: Optional[float] = None
    skills_improved: Optional[List[str]] = None
    skills_struggling: Optional[List[str]] = None
    recommendations_generated: int
    recommendations_accepted: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Search and Filter Models
class LearningPathSearchParams(BaseModel):
    status: Optional[LearningPathStatus] = None
    target_band_score_min: Optional[float] = Field(None, ge=0.0, le=9.0)
    target_band_score_max: Optional[float] = Field(None, ge=0.0, le=9.0)
    completion_percentage_min: Optional[float] = Field(None, ge=0.0, le=100.0)
    completion_percentage_max: Optional[float] = Field(None, ge=0.0, le=100.0)
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class RecommendationSearchParams(BaseModel):
    recommendation_type: Optional[RecommendationType] = None
    is_viewed: Optional[bool] = None
    is_accepted: Optional[bool] = None
    confidence_score_min: Optional[float] = Field(None, ge=0.0, le=1.0)
    priority_score_min: Optional[float] = Field(None, ge=0.0, le=1.0)
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class SkillMasterySearchParams(BaseModel):
    skill_name: Optional[str] = None
    module_type: Optional[str] = None
    current_level: Optional[SkillLevel] = None
    mastery_score_min: Optional[float] = Field(None, ge=0.0, le=1.0)
    mastery_score_max: Optional[float] = Field(None, ge=0.0, le=1.0)
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

# Dashboard Models
class LearningDashboardStats(BaseModel):
    total_learning_paths: int
    active_learning_paths: int
    completed_learning_paths: int
    total_study_time_hours: float
    average_daily_study_time: float
    total_objectives_completed: int
    current_streak_days: int
    longest_streak_days: int
    average_score: float
    improvement_rate: float
    skills_mastered: int
    skills_in_progress: int
    recommendations_accepted: int
    recommendations_pending: int

class SkillGapAnalysis(BaseModel):
    skill_name: str
    module_type: str
    current_level: SkillLevel
    target_level: SkillLevel
    mastery_score: float
    gap_size: float
    recommended_actions: List[str]
    estimated_time_to_target: int  # minutes

class PersonalizedInsights(BaseModel):
    learning_velocity: float
    preferred_study_times: List[str]
    preferred_content_types: List[str]
    strengths: List[str]
    weaknesses: List[str]
    improvement_opportunities: List[str]
    next_best_actions: List[str]
    predicted_band_score: float
    time_to_target: int  # days

# Validation
@validator('target_band_score')
def validate_band_score(cls, v):
    if v is not None and (v < 0.0 or v > 9.0):
        raise ValueError('Band score must be between 0.0 and 9.0')
    return v

@validator('completion_rate', 'accuracy')
def validate_percentage(cls, v):
    if v is not None and (v < 0.0 or v > 100.0):
        raise ValueError('Percentage must be between 0.0 and 100.0')
    return v

@validator('confidence_score', 'priority_score', 'mastery_score')
def validate_score(cls, v):
    if v is not None and (v < 0.0 or v > 1.0):
        raise ValueError('Score must be between 0.0 and 1.0')
    return v
