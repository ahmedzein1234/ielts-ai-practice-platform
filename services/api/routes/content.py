from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User, UserRole
from ..services.content_service import ContentService
from ..schemas.content import (
    ContentItemCreate, ContentItemUpdate, ContentItemResponse,
    ContentCategoryCreate, ContentCategoryUpdate, ContentCategoryResponse,
    ContentQuestionCreate, ContentQuestionUpdate, ContentQuestionResponse,
    ContentUsageCreate, ContentUsageUpdate, ContentUsageResponse,
    ContentAnalyticsResponse, ContentSearchParams, ContentFilterParams,
    ContentStatisticsResponse
)
from ..auth import get_current_user
from ..models.user import UserRole
from ..models.content import ContentType, DifficultyLevel, ContentStatus

router = APIRouter(prefix="/content", tags=["content"])


def require_role(allowed_roles: list[UserRole]):
    """Dependency to require specific user roles."""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


# Content Categories
@router.post("/categories", response_model=ContentCategoryResponse)
async def create_category(
    category_data: ContentCategoryCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TUTOR])),
    db: Session = Depends(get_db)
):
    """Create a new content category."""
    content_service = ContentService(db)
    return content_service.create_category(category_data, current_user)


@router.get("/categories", response_model=List[ContentCategoryResponse])
async def get_categories(
    include_inactive: bool = Query(False, description="Include inactive categories"),
    db: Session = Depends(get_db)
):
    """Get all content categories."""
    content_service = ContentService(db)
    return content_service.get_categories(include_inactive=include_inactive)


@router.get("/categories/{category_id}", response_model=ContentCategoryResponse)
async def get_category(
    category_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific content category."""
    content_service = ContentService(db)
    category = content_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/categories/{category_id}", response_model=ContentCategoryResponse)
async def update_category(
    category_id: str,
    category_data: ContentCategoryUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TUTOR])),
    db: Session = Depends(get_db)
):
    """Update a content category."""
    content_service = ContentService(db)
    category = content_service.update_category(category_id, category_data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Delete a content category."""
    content_service = ContentService(db)
    success = content_service.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}


# Content Items
@router.post("/items", response_model=ContentItemResponse)
async def create_content_item(
    content_data: ContentItemCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TUTOR])),
    db: Session = Depends(get_db)
):
    """Create a new content item."""
    content_service = ContentService(db)
    return content_service.create_content_item(content_data, current_user)


@router.get("/items", response_model=List[ContentItemResponse])
async def get_content_items(
    search: Optional[str] = Query(None, description="Search term"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_desc: Optional[bool] = Query(True, description="Sort descending"),
    limit: int = Query(50, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: Session = Depends(get_db)
):
    """Get content items with search and filtering."""
    content_service = ContentService(db)
    
    # Build search and filter parameters
    search_params = ContentSearchParams(
        search=search,
        sort_by=sort_by,
        sort_desc=sort_desc
    ) if search or sort_by else None
    
    filter_params = None
    if any([content_type, difficulty_level, status, category_id, tags]):
        filter_params = ContentFilterParams(
            content_type=ContentType(content_type) if content_type else None,
            difficulty_level=DifficultyLevel(difficulty_level) if difficulty_level else None,
            status=ContentStatus(status) if status else None,
            category_id=category_id,
            tags=tags.split(",") if tags else None
        )
    
    return content_service.get_content_items(
        search_params=search_params,
        filter_params=filter_params,
        limit=limit,
        offset=offset
    )


@router.get("/items/{content_id}", response_model=ContentItemResponse)
async def get_content_item(
    content_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific content item."""
    content_service = ContentService(db)
    content_item = content_service.get_content_item(content_id)
    if not content_item:
        raise HTTPException(status_code=404, detail="Content item not found")
    return content_item


@router.put("/items/{content_id}", response_model=ContentItemResponse)
async def update_content_item(
    content_id: str,
    content_data: ContentItemUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TUTOR])),
    db: Session = Depends(get_db)
):
    """Update a content item."""
    content_service = ContentService(db)
    content_item = content_service.update_content_item(content_id, content_data)
    if not content_item:
        raise HTTPException(status_code=404, detail="Content item not found")
    return content_item


@router.delete("/items/{content_id}")
async def delete_content_item(
    content_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TUTOR])),
    db: Session = Depends(get_db)
):
    """Delete a content item."""
    content_service = ContentService(db)
    success = content_service.delete_content_item(content_id)
    if not success:
        raise HTTPException(status_code=404, detail="Content item not found")
    return {"message": "Content item deleted successfully"}


@router.post("/items/{content_id}/publish", response_model=ContentItemResponse)
async def publish_content_item(
    content_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TUTOR])),
    db: Session = Depends(get_db)
):
    """Publish a content item."""
    content_service = ContentService(db)
    content_item = content_service.publish_content_item(content_id)
    if not content_item:
        raise HTTPException(status_code=404, detail="Content item not found")
    return content_item


# Content Questions
@router.post("/questions", response_model=ContentQuestionResponse)
async def create_question(
    question_data: ContentQuestionCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TUTOR])),
    db: Session = Depends(get_db)
):
    """Create a new content question."""
    content_service = ContentService(db)
    return content_service.create_question(question_data)


@router.get("/items/{content_id}/questions", response_model=List[ContentQuestionResponse])
async def get_questions_for_content(
    content_id: str,
    db: Session = Depends(get_db)
):
    """Get all questions for a content item."""
    content_service = ContentService(db)
    return content_service.get_questions_for_content(content_id)


@router.put("/questions/{question_id}", response_model=ContentQuestionResponse)
async def update_question(
    question_id: str,
    question_data: ContentQuestionUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TUTOR])),
    db: Session = Depends(get_db)
):
    """Update a content question."""
    content_service = ContentService(db)
    question = content_service.update_question(question_id, question_data)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TUTOR])),
    db: Session = Depends(get_db)
):
    """Delete a content question."""
    content_service = ContentService(db)
    success = content_service.delete_question(question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}


# Content Usage Tracking
@router.post("/usage", response_model=ContentUsageResponse)
async def track_content_usage(
    usage_data: ContentUsageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track content usage by a user."""
    content_service = ContentService(db)
    # Ensure the user_id matches the current user
    usage_data.user_id = current_user.id
    return content_service.track_content_usage(usage_data)


@router.get("/usage", response_model=List[ContentUsageResponse])
async def get_user_content_usage(
    content_id: Optional[str] = Query(None, description="Filter by content ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get content usage for the current user."""
    content_service = ContentService(db)
    return content_service.get_user_content_usage(current_user.id, content_id)


@router.get("/items/{content_id}/analytics", response_model=ContentAnalyticsResponse)
async def get_content_analytics(
    content_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TUTOR])),
    db: Session = Depends(get_db)
):
    """Get analytics for a content item."""
    content_service = ContentService(db)
    return content_service.get_content_analytics(content_id, days)


# Content Statistics
@router.get("/statistics", response_model=ContentStatisticsResponse)
async def get_content_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get content statistics for dashboard."""
    content_service = ContentService(db)
    return content_service.get_content_statistics(current_user)


# User-specific content endpoints
@router.get("/my-content", response_model=List[ContentItemResponse])
async def get_my_content(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TUTOR])),
    db: Session = Depends(get_db)
):
    """Get content items created by the current user."""
    content_service = ContentService(db)
    filter_params = ContentFilterParams(created_by_id=current_user.id)
    return content_service.get_content_items(filter_params=filter_params)


@router.get("/my-usage", response_model=List[ContentUsageResponse])
async def get_my_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get content usage for the current user."""
    content_service = ContentService(db)
    return content_service.get_user_content_usage(current_user.id)
