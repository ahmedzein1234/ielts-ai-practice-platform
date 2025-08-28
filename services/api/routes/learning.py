"""Learning paths API routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class LearningPathResponse(BaseModel):
    id: str
    title: str
    description: str
    difficulty_level: str
    estimated_duration: int
    is_active: bool


class RecommendationResponse(BaseModel):
    id: str
    type: str
    title: str
    description: str
    priority: str
    created_at: str


@router.get("/", response_model=List[LearningPathResponse])
async def get_learning_paths():
    """Get learning paths."""
    return [
        LearningPathResponse(
            id="path-1",
            title="IELTS Academic Preparation",
            description="Complete preparation for IELTS Academic",
            difficulty_level="intermediate",
            estimated_duration=30,
            is_active=True,
        ),
        LearningPathResponse(
            id="path-2",
            title="IELTS General Training",
            description="Complete preparation for IELTS General",
            difficulty_level="beginner",
            estimated_duration=25,
            is_active=True,
        ),
    ]


@router.get("/{path_id}", response_model=LearningPathResponse)
async def get_learning_path(path_id: str):
    """Get a specific learning path."""
    return LearningPathResponse(
        id=path_id,
        title=f"Learning Path {path_id}",
        description="A comprehensive learning path",
        difficulty_level="intermediate",
        estimated_duration=30,
        is_active=True,
    )


@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations():
    """Get learning recommendations."""
    return [
        RecommendationResponse(
            id="rec-1",
            type="content",
            title="Practice Reading Comprehension",
            description="Focus on reading skills",
            priority="high",
            created_at="2024-01-01T00:00:00Z",
        ),
        RecommendationResponse(
            id="rec-2",
            type="assessment",
            title="Take a Mock Test",
            description="Test your current level",
            priority="medium",
            created_at="2024-01-01T00:00:00Z",
        ),
    ]
