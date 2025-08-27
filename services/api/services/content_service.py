from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta
import uuid

from ..models.content import (
    ContentItem, ContentCategory, ContentQuestion, ContentUsage, ContentAnalytics,
    ContentType, DifficultyLevel, ContentStatus
)
from ..models.user import User, UserRole
from ..schemas.content import (
    ContentItemCreate, ContentItemUpdate, ContentItemResponse,
    ContentCategoryCreate, ContentCategoryUpdate, ContentCategoryResponse,
    ContentQuestionCreate, ContentQuestionUpdate, ContentQuestionResponse,
    ContentUsageCreate, ContentUsageUpdate, ContentUsageResponse,
    ContentAnalyticsResponse, ContentSearchParams, ContentFilterParams
)


class ContentService:
    """Service for managing content items, categories, and analytics."""

    def __init__(self, db: Session):
        self.db = db

    # Content Categories
    def create_category(self, category_data: ContentCategoryCreate, created_by: User) -> ContentCategory:
        """Create a new content category."""
        category = ContentCategory(
            id=str(uuid.uuid4()),
            name=category_data.name,
            description=category_data.description,
            parent_category_id=category_data.parent_category_id,
            color=category_data.color,
            icon=category_data.icon,
            sort_order=category_data.sort_order or 0
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_categories(self, include_inactive: bool = False) -> List[ContentCategory]:
        """Get all content categories."""
        query = self.db.query(ContentCategory)
        if not include_inactive:
            query = query.filter(ContentCategory.is_active == True)
        return query.order_by(ContentCategory.sort_order, ContentCategory.name).all()

    def get_category(self, category_id: str) -> Optional[ContentCategory]:
        """Get a specific content category."""
        return self.db.query(ContentCategory).filter(ContentCategory.id == category_id).first()

    def update_category(self, category_id: str, category_data: ContentCategoryUpdate) -> Optional[ContentCategory]:
        """Update a content category."""
        category = self.get_category(category_id)
        if not category:
            return None
        
        for field, value in category_data.dict(exclude_unset=True).items():
            setattr(category, field, value)
        
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category_id: str) -> bool:
        """Delete a content category."""
        category = self.get_category(category_id)
        if not category:
            return False
        
        # Check if category has content items
        if category.content_items:
            # Soft delete by setting is_active to False
            category.is_active = False
            self.db.commit()
        else:
            # Hard delete if no content items
            self.db.delete(category)
            self.db.commit()
        
        return True

    # Content Items
    def create_content_item(self, content_data: ContentItemCreate, created_by: User) -> ContentItem:
        """Create a new content item."""
        content_item = ContentItem(
            id=str(uuid.uuid4()),
            title=content_data.title,
            content_type=content_data.content_type,
            difficulty_level=content_data.difficulty_level,
            content_text=content_data.content_text,
            audio_url=content_data.audio_url,
            audio_duration=content_data.audio_duration,
            transcript=content_data.transcript,
            prompt=content_data.prompt,
            sample_answer=content_data.sample_answer,
            vocabulary_list=content_data.vocabulary_list,
            grammar_points=content_data.grammar_points,
            tags=content_data.tags,
            estimated_time=content_data.estimated_time,
            word_count=content_data.word_count,
            target_band_score=content_data.target_band_score,
            category_id=content_data.category_id,
            created_by_id=created_by.id
        )
        self.db.add(content_item)
        self.db.commit()
        self.db.refresh(content_item)
        return content_item

    def get_content_items(
        self,
        search_params: Optional[ContentSearchParams] = None,
        filter_params: Optional[ContentFilterParams] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ContentItem]:
        """Get content items with search and filtering."""
        query = self.db.query(ContentItem).options(
            joinedload(ContentItem.category),
            joinedload(ContentItem.created_by),
            joinedload(ContentItem.questions)
        )

        # Apply search filters
        if search_params:
            if search_params.search:
                search_term = f"%{search_params.search}%"
                query = query.filter(
                    or_(
                        ContentItem.title.ilike(search_term),
                        ContentItem.content_text.ilike(search_term),
                        ContentItem.tags.contains([search_params.search])
                    )
                )

        # Apply filter parameters
        if filter_params:
            if filter_params.content_type:
                query = query.filter(ContentItem.content_type == filter_params.content_type)
            if filter_params.difficulty_level:
                query = query.filter(ContentItem.difficulty_level == filter_params.difficulty_level)
            if filter_params.status:
                query = query.filter(ContentItem.status == filter_params.status)
            if filter_params.category_id:
                query = query.filter(ContentItem.category_id == filter_params.category_id)
            if filter_params.created_by_id:
                query = query.filter(ContentItem.created_by_id == filter_params.created_by_id)
            if filter_params.tags:
                query = query.filter(ContentItem.tags.contains(filter_params.tags))

        # Apply sorting
        sort_field = getattr(ContentItem, search_params.sort_by if search_params and search_params.sort_by else "created_at")
        if search_params and search_params.sort_desc:
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))

        return query.offset(offset).limit(limit).all()

    def get_content_item(self, content_id: str) -> Optional[ContentItem]:
        """Get a specific content item."""
        return self.db.query(ContentItem).options(
            joinedload(ContentItem.category),
            joinedload(ContentItem.created_by),
            joinedload(ContentItem.questions)
        ).filter(ContentItem.id == content_id).first()

    def update_content_item(self, content_id: str, content_data: ContentItemUpdate) -> Optional[ContentItem]:
        """Update a content item."""
        content_item = self.get_content_item(content_id)
        if not content_item:
            return None
        
        for field, value in content_data.dict(exclude_unset=True).items():
            setattr(content_item, field, value)
        
        # Update published_at if status is being set to published
        if content_data.status == ContentStatus.PUBLISHED and content_item.status != ContentStatus.PUBLISHED:
            content_item.published_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(content_item)
        return content_item

    def delete_content_item(self, content_id: str) -> bool:
        """Delete a content item."""
        content_item = self.get_content_item(content_id)
        if not content_item:
            return False
        
        self.db.delete(content_item)
        self.db.commit()
        return True

    def publish_content_item(self, content_id: str) -> Optional[ContentItem]:
        """Publish a content item."""
        content_item = self.get_content_item(content_id)
        if not content_item:
            return None
        
        content_item.status = ContentStatus.PUBLISHED
        content_item.published_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(content_item)
        return content_item

    # Content Questions
    def create_question(self, question_data: ContentQuestionCreate) -> ContentQuestion:
        """Create a new content question."""
        question = ContentQuestion(
            id=str(uuid.uuid4()),
            content_item_id=question_data.content_item_id,
            question_text=question_data.question_text,
            question_type=question_data.question_type,
            correct_answer=question_data.correct_answer,
            options=question_data.options,
            explanation=question_data.explanation,
            difficulty_level=question_data.difficulty_level,
            points=question_data.points or 1,
            sort_order=question_data.sort_order or 0
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def get_questions_for_content(self, content_id: str) -> List[ContentQuestion]:
        """Get all questions for a content item."""
        return self.db.query(ContentQuestion).filter(
            ContentQuestion.content_item_id == content_id
        ).order_by(ContentQuestion.sort_order).all()

    def update_question(self, question_id: str, question_data: ContentQuestionUpdate) -> Optional[ContentQuestion]:
        """Update a content question."""
        question = self.db.query(ContentQuestion).filter(ContentQuestion.id == question_id).first()
        if not question:
            return None
        
        for field, value in question_data.dict(exclude_unset=True).items():
            setattr(question, field, value)
        
        self.db.commit()
        self.db.refresh(question)
        return question

    def delete_question(self, question_id: str) -> bool:
        """Delete a content question."""
        question = self.db.query(ContentQuestion).filter(ContentQuestion.id == question_id).first()
        if not question:
            return False
        
        self.db.delete(question)
        self.db.commit()
        return True

    # Content Usage Tracking
    def track_content_usage(self, usage_data: ContentUsageCreate) -> ContentUsage:
        """Track content usage by a user."""
        usage = ContentUsage(
            id=str(uuid.uuid4()),
            content_item_id=usage_data.content_item_id,
            user_id=usage_data.user_id,
            session_id=usage_data.session_id,
            time_spent=usage_data.time_spent,
            completion_rate=usage_data.completion_rate,
            score=usage_data.score,
            questions_attempted=usage_data.questions_attempted,
            questions_correct=usage_data.questions_correct,
            rating=usage_data.rating,
            feedback=usage_data.feedback,
            difficulty_rating=usage_data.difficulty_rating
        )
        
        if usage_data.completion_rate == 100.0:
            usage.completed_at = datetime.utcnow()
        
        self.db.add(usage)
        self.db.commit()
        self.db.refresh(usage)
        
        # Update analytics
        self._update_content_analytics(usage_data.content_item_id)
        
        return usage

    def get_user_content_usage(self, user_id: str, content_id: Optional[str] = None) -> List[ContentUsage]:
        """Get content usage for a user."""
        query = self.db.query(ContentUsage).filter(ContentUsage.user_id == user_id)
        if content_id:
            query = query.filter(ContentUsage.content_item_id == content_id)
        return query.order_by(desc(ContentUsage.accessed_at)).all()

    def get_content_analytics(self, content_id: str, days: int = 30) -> ContentAnalyticsResponse:
        """Get analytics for a content item."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get aggregated analytics
        analytics = self.db.query(ContentAnalytics).filter(
            and_(
                ContentAnalytics.content_item_id == content_id,
                ContentAnalytics.date >= start_date
            )
        ).order_by(desc(ContentAnalytics.date)).all()
        
        # Get recent usage data
        recent_usage = self.db.query(ContentUsage).filter(
            and_(
                ContentUsage.content_item_id == content_id,
                ContentUsage.accessed_at >= start_date
            )
        ).all()
        
        # Calculate summary statistics
        total_views = sum(a.total_views for a in analytics)
        total_completions = sum(a.total_completions for a in analytics)
        avg_time_spent = sum(a.average_time_spent or 0 for a in analytics) / len(analytics) if analytics else 0
        avg_score = sum(a.average_score or 0 for a in analytics) / len(analytics) if analytics else 0
        avg_rating = sum(a.average_rating or 0 for a in analytics) / len(analytics) if analytics else 0
        
        return ContentAnalyticsResponse(
            content_id=content_id,
            period_days=days,
            total_views=total_views,
            total_completions=total_completions,
            average_time_spent=avg_time_spent,
            average_score=avg_score,
            average_rating=avg_rating,
            completion_rate=(total_completions / total_views * 100) if total_views > 0 else 0,
            daily_analytics=analytics,
            recent_usage=recent_usage
        )

    def _update_content_analytics(self, content_id: str):
        """Update aggregated analytics for a content item."""
        today = datetime.utcnow().date()
        
        # Get today's usage data
        today_usage = self.db.query(ContentUsage).filter(
            and_(
                ContentUsage.content_item_id == content_id,
                func.date(ContentUsage.accessed_at) == today
            )
        ).all()
        
        if not today_usage:
            return
        
        # Calculate aggregated metrics
        total_views = len(today_usage)
        total_completions = len([u for u in today_usage if u.completion_rate == 100.0])
        avg_time_spent = sum(u.time_spent or 0 for u in today_usage) / total_views if total_views > 0 else 0
        avg_score = sum(u.score or 0 for u in today_usage) / total_views if total_views > 0 else 0
        avg_rating = sum(u.rating or 0 for u in today_usage) / total_views if total_views > 0 else 0
        completion_rate = (total_completions / total_views * 100) if total_views > 0 else 0
        
        # Get difficulty ratings
        difficulty_ratings = [u.difficulty_rating for u in today_usage if u.difficulty_rating]
        avg_difficulty_rating = sum(difficulty_ratings) / len(difficulty_ratings) if difficulty_ratings else None
        
        # Update or create analytics record
        analytics = self.db.query(ContentAnalytics).filter(
            and_(
                ContentAnalytics.content_item_id == content_id,
                func.date(ContentAnalytics.date) == today
            )
        ).first()
        
        if analytics:
            # Update existing record
            analytics.total_views = total_views
            analytics.total_completions = total_completions
            analytics.average_time_spent = avg_time_spent
            analytics.average_score = avg_score
            analytics.average_rating = avg_rating
            analytics.completion_rate = completion_rate
            analytics.difficulty_rating_avg = avg_difficulty_rating
            analytics.difficulty_rating_count = len(difficulty_ratings)
        else:
            # Create new record
            analytics = ContentAnalytics(
                id=str(uuid.uuid4()),
                content_item_id=content_id,
                date=datetime.combine(today, datetime.min.time()),
                total_views=total_views,
                total_completions=total_completions,
                average_time_spent=avg_time_spent,
                average_score=avg_score,
                average_rating=avg_rating,
                completion_rate=completion_rate,
                difficulty_rating_avg=avg_difficulty_rating,
                difficulty_rating_count=len(difficulty_ratings)
            )
            self.db.add(analytics)
        
        self.db.commit()

    # Content Statistics
    def get_content_statistics(self, user: User) -> Dict[str, Any]:
        """Get content statistics for dashboard."""
        if user.role == UserRole.ADMIN:
            # Admin statistics
            total_content = self.db.query(ContentItem).count()
            published_content = self.db.query(ContentItem).filter(
                ContentItem.status == ContentStatus.PUBLISHED
            ).count()
            total_categories = self.db.query(ContentCategory).filter(
                ContentCategory.is_active == True
            ).count()
            
            # Recent activity
            recent_content = self.db.query(ContentItem).order_by(
                desc(ContentItem.created_at)
            ).limit(5).all()
            
            return {
                "total_content": total_content,
                "published_content": published_content,
                "draft_content": total_content - published_content,
                "total_categories": total_categories,
                "recent_content": recent_content
            }
        else:
            # User statistics
            user_content = self.db.query(ContentItem).filter(
                ContentItem.created_by_id == user.id
            ).count()
            
            user_usage = self.db.query(ContentUsage).filter(
                ContentUsage.user_id == user.id
            ).count()
            
            recent_usage = self.db.query(ContentUsage).filter(
                ContentUsage.user_id == user.id
            ).order_by(desc(ContentUsage.accessed_at)).limit(5).all()
            
            return {
                "user_content": user_content,
                "content_used": user_usage,
                "recent_usage": recent_usage
            }
