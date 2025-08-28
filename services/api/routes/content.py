"""Content management API routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ContentItemResponse(BaseModel):
    id: str
    title: str
    content_type: str
    difficulty_level: str
    is_active: bool
    created_at: str


class ContentCategoryResponse(BaseModel):
    id: str
    name: str
    description: str
    content_count: int


@router.get("/", response_model=List[ContentItemResponse])
async def get_content_items():
    """Get content items."""
    return [
        ContentItemResponse(
            id="content-1",
            title="IELTS Reading Practice",
            content_type="reading",
            difficulty_level="intermediate",
            is_active=True,
            created_at="2024-01-01T00:00:00Z",
        ),
        ContentItemResponse(
            id="content-2",
            title="IELTS Writing Task 2",
            content_type="writing",
            difficulty_level="advanced",
            is_active=True,
            created_at="2024-01-01T00:00:00Z",
        ),
    ]


@router.get("/categories", response_model=List[ContentCategoryResponse])
async def get_content_categories():
    """Get content categories."""
    return [
        ContentCategoryResponse(
            id="cat-1",
            name="Reading",
            description="Reading comprehension materials",
            content_count=10,
        ),
        ContentCategoryResponse(
            id="cat-2",
            name="Writing",
            description="Writing practice materials",
            content_count=15,
        ),
    ]


@router.get("/{item_id}", response_model=ContentItemResponse)
async def get_content_item(item_id: str):
    """Get a specific content item."""
    return ContentItemResponse(
        id=item_id,
        title=f"Content {item_id}",
        content_type="reading",
        difficulty_level="intermediate",
        is_active=True,
        created_at="2024-01-01T00:00:00Z",
    )
