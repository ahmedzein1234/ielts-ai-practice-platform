from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

from ..models.content import ContentType, DifficultyLevel, ContentStatus


# Base schemas
class ContentCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_category_id: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = Field(0, ge=0)


class ContentItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content_type: ContentType
    difficulty_level: DifficultyLevel
    content_text: Optional[str] = None
    audio_url: Optional[str] = Field(None, max_length=500)
    audio_duration: Optional[int] = Field(None, ge=0)
    transcript: Optional[str] = None
    prompt: Optional[str] = None
    sample_answer: Optional[str] = None
    vocabulary_list: Optional[Dict[str, Any]] = None
    grammar_points: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    estimated_time: Optional[int] = Field(None, ge=0)
    word_count: Optional[int] = Field(None, ge=0)
    target_band_score: Optional[float] = Field(None, ge=0.0, le=9.0)
    category_id: Optional[str] = None


class ContentQuestionBase(BaseModel):
    question_text: str = Field(..., min_length=1)
    question_type: str = Field(..., max_length=50)
    correct_answer: str = Field(..., min_length=1)
    options: Optional[List[str]] = None
    explanation: Optional[str] = None
    difficulty_level: DifficultyLevel
    points: Optional[int] = Field(1, ge=1)
    sort_order: Optional[int] = Field(0, ge=0)


class ContentUsageBase(BaseModel):
    content_item_id: str
    session_id: Optional[str] = Field(None, max_length=100)
    time_spent: Optional[int] = Field(None, ge=0)
    completion_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    score: Optional[float] = Field(None, ge=0.0, le=100.0)
    questions_attempted: Optional[int] = Field(None, ge=0)
    questions_correct: Optional[int] = Field(None, ge=0)
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback: Optional[str] = None
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5)


# Create schemas
class ContentCategoryCreate(ContentCategoryBase):
    pass


class ContentItemCreate(ContentItemBase):
    pass


class ContentQuestionCreate(ContentQuestionBase):
    content_item_id: str


class ContentUsageCreate(ContentUsageBase):
    user_id: str


# Update schemas
class ContentCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_category_id: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ContentItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content_type: Optional[ContentType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    status: Optional[ContentStatus] = None
    content_text: Optional[str] = None
    audio_url: Optional[str] = Field(None, max_length=500)
    audio_duration: Optional[int] = Field(None, ge=0)
    transcript: Optional[str] = None
    prompt: Optional[str] = None
    sample_answer: Optional[str] = None
    vocabulary_list: Optional[Dict[str, Any]] = None
    grammar_points: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    estimated_time: Optional[int] = Field(None, ge=0)
    word_count: Optional[int] = Field(None, ge=0)
    target_band_score: Optional[float] = Field(None, ge=0.0, le=9.0)
    category_id: Optional[str] = None


class ContentQuestionUpdate(BaseModel):
    question_text: Optional[str] = Field(None, min_length=1)
    question_type: Optional[str] = Field(None, max_length=50)
    correct_answer: Optional[str] = Field(None, min_length=1)
    options: Optional[List[str]] = None
    explanation: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    points: Optional[int] = Field(None, ge=1)
    sort_order: Optional[int] = Field(None, ge=0)


class ContentUsageUpdate(BaseModel):
    session_id: Optional[str] = Field(None, max_length=100)
    time_spent: Optional[int] = Field(None, ge=0)
    completion_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    score: Optional[float] = Field(None, ge=0.0, le=100.0)
    questions_attempted: Optional[int] = Field(None, ge=0)
    questions_correct: Optional[int] = Field(None, ge=0)
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback: Optional[str] = None
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5)


# Response schemas
class ContentCategoryResponse(ContentCategoryBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    sub_categories: List["ContentCategoryResponse"] = []
    content_count: Optional[int] = None

    class Config:
        from_attributes = True


class ContentQuestionResponse(ContentQuestionBase):
    id: str
    content_item_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContentItemResponse(ContentItemBase):
    id: str
    status: ContentStatus
    created_by_id: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    category: Optional[ContentCategoryResponse] = None
    created_by: Optional[Dict[str, Any]] = None
    questions: List[ContentQuestionResponse] = []
    usage_count: Optional[int] = None
    average_rating: Optional[float] = None

    class Config:
        from_attributes = True


class ContentUsageResponse(ContentUsageBase):
    id: str
    user_id: str
    accessed_at: datetime
    completed_at: Optional[datetime] = None
    content_item: Optional[Dict[str, Any]] = None
    user: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ContentAnalyticsResponse(BaseModel):
    content_id: str
    period_days: int
    total_views: int
    total_completions: int
    average_time_spent: float
    average_score: float
    average_rating: float
    completion_rate: float
    daily_analytics: List[Dict[str, Any]] = []
    recent_usage: List[ContentUsageResponse] = []

    class Config:
        from_attributes = True


# Search and filter schemas
class ContentSearchParams(BaseModel):
    search: Optional[str] = None
    sort_by: Optional[str] = Field("created_at", pattern=r'^(title|created_at|updated_at|difficulty_level|content_type)$')
    sort_desc: Optional[bool] = True


class ContentFilterParams(BaseModel):
    content_type: Optional[ContentType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    status: Optional[ContentStatus] = None
    category_id: Optional[str] = None
    created_by_id: Optional[str] = None
    tags: Optional[List[str]] = None


# Statistics schemas
class ContentStatisticsResponse(BaseModel):
    total_content: Optional[int] = None
    published_content: Optional[int] = None
    draft_content: Optional[int] = None
    total_categories: Optional[int] = None
    user_content: Optional[int] = None
    content_used: Optional[int] = None
    recent_content: List[ContentItemResponse] = []
    recent_usage: List[ContentUsageResponse] = []

    class Config:
        from_attributes = True


# Update forward references
ContentCategoryResponse.model_rebuild()
