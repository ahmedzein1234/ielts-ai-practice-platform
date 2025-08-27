"""
Learning Service for Advanced Learning Features (Phase 3).
Implements AI-powered learning path generation, recommendation engine, and progress tracking.
"""

import structlog
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import json
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

from ..models.learning import (
    LearningPath, LearningObjective, UserProgress, Recommendation, 
    SkillMastery, LearningAnalytics, LearningPathStatus, LearningObjectiveType,
    SkillLevel, RecommendationType
)
from ..models.assessment import TestSession, TestStatus
from ..models.content import ContentItem, ContentType, DifficultyLevel
from ..models.user import User
from ..schemas.learning import (
    LearningPathCreate, LearningObjectiveCreate, UserProgressCreate,
    RecommendationCreate, SkillMasteryCreate, LearningPathUpdate,
    LearningObjectiveUpdate, UserProgressUpdate, RecommendationUpdate,
    SkillMasteryUpdate, LearningPathSearchParams, RecommendationSearchParams,
    SkillMasterySearchParams, LearningDashboardStats, SkillGapAnalysis,
    PersonalizedInsights
)

logger = structlog.get_logger(__name__)

class LearningService:
    """Service for managing advanced learning features."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Learning Path Management
    def create_learning_path(self, user_id: str, path_data: LearningPathCreate) -> LearningPath:
        """Create a new learning path for a user."""
        try:
            # Generate AI-powered path structure
            path_structure = self._generate_path_structure(user_id, path_data)
            
            # Create learning path
            learning_path = LearningPath(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title=path_data.title,
                description=path_data.description,
                target_band_score=path_data.target_band_score,
                estimated_duration_days=path_data.estimated_duration_days,
                learning_style=path_data.learning_style,
                path_structure=path_structure,
                skill_gaps=path_structure.get("skill_gaps", []),
                priority_areas=path_structure.get("priority_areas", []),
                difficulty_progression=path_structure.get("difficulty_progression", {}),
                total_objectives=len(path_structure.get("objectives", []))
            )
            
            self.db.add(learning_path)
            self.db.commit()
            self.db.refresh(learning_path)
            
            # Create learning objectives
            self._create_learning_objectives(learning_path.id, path_structure.get("objectives", []))
            
            logger.info("Learning path created successfully", 
                       user_id=user_id, path_id=learning_path.id)
            return learning_path
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create learning path", 
                        user_id=user_id, error=str(e))
            raise
    
    def get_user_learning_paths(self, user_id: str, params: LearningPathSearchParams) -> List[LearningPath]:
        """Get learning paths for a user with filtering."""
        query = self.db.query(LearningPath).filter(LearningPath.user_id == user_id)
        
        if params.status:
            query = query.filter(LearningPath.status == params.status)
        
        if params.target_band_score_min is not None:
            query = query.filter(LearningPath.target_band_score >= params.target_band_score_min)
        
        if params.target_band_score_max is not None:
            query = query.filter(LearningPath.target_band_score <= params.target_band_score_max)
        
        if params.completion_percentage_min is not None:
            query = query.filter(LearningPath.completion_percentage >= params.completion_percentage_min)
        
        if params.completion_percentage_max is not None:
            query = query.filter(LearningPath.completion_percentage <= params.completion_percentage_max)
        
        if params.created_after:
            query = query.filter(LearningPath.created_at >= params.created_after)
        
        if params.created_before:
            query = query.filter(LearningPath.created_at <= params.created_before)
        
        return query.offset(params.offset).limit(params.limit).all()
    
    def update_learning_path(self, path_id: str, update_data: LearningPathUpdate) -> LearningPath:
        """Update a learning path."""
        learning_path = self.db.query(LearningPath).filter(LearningPath.id == path_id).first()
        if not learning_path:
            raise ValueError("Learning path not found")
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(learning_path, field, value)
        
        self.db.commit()
        self.db.refresh(learning_path)
        return learning_path
    
    def complete_learning_objective(self, objective_id: str, user_id: str) -> LearningObjective:
        """Mark a learning objective as completed."""
        objective = self.db.query(LearningObjective).join(LearningPath).filter(
            and_(
                LearningObjective.id == objective_id,
                LearningPath.user_id == user_id
            )
        ).first()
        
        if not objective:
            raise ValueError("Learning objective not found")
        
        objective.is_completed = True
        objective.completion_date = datetime.utcnow()
        
        # Update learning path progress
        learning_path = objective.learning_path
        learning_path.completed_objectives += 1
        learning_path.completion_percentage = (
            learning_path.completed_objectives / learning_path.total_objectives * 100
        )
        
        # Check if path is completed
        if learning_path.completion_percentage >= 100:
            learning_path.status = LearningPathStatus.COMPLETED
            learning_path.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(objective)
        return objective
    
    # Progress Tracking
    def record_user_progress(self, user_id: str, progress_data: UserProgressCreate) -> UserProgress:
        """Record user progress for learning activities."""
        progress = UserProgress(
            id=str(uuid.uuid4()),
            user_id=user_id,
            learning_path_id=progress_data.learning_path_id,
            content_item_id=progress_data.content_item_id,
            test_session_id=progress_data.test_session_id,
            time_spent_minutes=progress_data.time_spent_minutes,
            completion_rate=progress_data.completion_rate,
            score=progress_data.score,
            accuracy=progress_data.accuracy,
            engagement_level=progress_data.engagement_level,
            difficulty_rating=progress_data.difficulty_rating,
            confidence_level=progress_data.confidence_level,
            device_type=progress_data.device_type,
            study_environment=progress_data.study_environment,
            energy_level=progress_data.energy_level,
            focus_level=progress_data.focus_level
        )
        
        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        
        # Update skill mastery
        self._update_skill_mastery(user_id, progress_data)
        
        return progress
    
    def get_user_progress_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get a summary of user progress over a period."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        progress_records = self.db.query(UserProgress).filter(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.session_start >= start_date
            )
        ).all()
        
        if not progress_records:
            return {
                "total_study_time": 0,
                "average_score": 0.0,
                "completion_rate": 0.0,
                "sessions_count": 0
            }
        
        total_time = sum(p.time_spent_minutes for p in progress_records)
        scores = [p.score for p in progress_records if p.score is not None]
        completion_rates = [p.completion_rate for p in progress_records]
        
        return {
            "total_study_time": total_time,
            "average_score": np.mean(scores) if scores else 0.0,
            "completion_rate": np.mean(completion_rates),
            "sessions_count": len(progress_records)
        }
    
    # AI Recommendation Engine
    def generate_recommendations(self, user_id: str, limit: int = 10) -> List[Recommendation]:
        """Generate AI-powered recommendations for a user."""
        try:
            recommendations = []
            
            # Get user's learning history and preferences
            user_profile = self._analyze_user_profile(user_id)
            
            # Content-based recommendations
            content_recs = self._generate_content_based_recommendations(user_id, user_profile, limit // 3)
            recommendations.extend(content_recs)
            
            # Performance-based recommendations
            performance_recs = self._generate_performance_based_recommendations(user_id, user_profile, limit // 3)
            recommendations.extend(performance_recs)
            
            # Context-aware recommendations
            context_recs = self._generate_context_aware_recommendations(user_id, user_profile, limit // 3)
            recommendations.extend(context_recs)
            
            # Add recommendations to database
            for rec in recommendations:
                self.db.add(rec)
            
            self.db.commit()
            
            logger.info("Generated recommendations successfully", 
                       user_id=user_id, count=len(recommendations))
            return recommendations
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to generate recommendations", 
                        user_id=user_id, error=str(e))
            raise
    
    def get_user_recommendations(self, user_id: str, params: RecommendationSearchParams) -> List[Recommendation]:
        """Get recommendations for a user with filtering."""
        query = self.db.query(Recommendation).filter(Recommendation.user_id == user_id)
        
        if params.recommendation_type:
            query = query.filter(Recommendation.recommendation_type == params.recommendation_type)
        
        if params.is_viewed is not None:
            query = query.filter(Recommendation.is_viewed == params.is_viewed)
        
        if params.is_accepted is not None:
            query = query.filter(Recommendation.is_accepted == params.is_accepted)
        
        if params.confidence_score_min is not None:
            query = query.filter(Recommendation.confidence_score >= params.confidence_score_min)
        
        if params.priority_score_min is not None:
            query = query.filter(Recommendation.priority_score >= params.priority_score_min)
        
        if params.created_after:
            query = query.filter(Recommendation.created_at >= params.created_after)
        
        if params.created_before:
            query = query.filter(Recommendation.created_at <= params.created_before)
        
        return query.order_by(desc(Recommendation.priority_score)).offset(params.offset).limit(params.limit).all()
    
    def mark_recommendation_viewed(self, recommendation_id: str, user_id: str) -> Recommendation:
        """Mark a recommendation as viewed."""
        recommendation = self.db.query(Recommendation).filter(
            and_(
                Recommendation.id == recommendation_id,
                Recommendation.user_id == user_id
            )
        ).first()
        
        if not recommendation:
            raise ValueError("Recommendation not found")
        
        recommendation.is_viewed = True
        recommendation.viewed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(recommendation)
        return recommendation
    
    def accept_recommendation(self, recommendation_id: str, user_id: str) -> Recommendation:
        """Mark a recommendation as accepted."""
        recommendation = self.db.query(Recommendation).filter(
            and_(
                Recommendation.id == recommendation_id,
                Recommendation.user_id == user_id
            )
        ).first()
        
        if not recommendation:
            raise ValueError("Recommendation not found")
        
        recommendation.is_accepted = True
        recommendation.accepted_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(recommendation)
        return recommendation
    
    # Skill Mastery Tracking
    def update_skill_mastery(self, user_id: str, skill_data: SkillMasteryCreate) -> SkillMastery:
        """Update or create skill mastery record."""
        existing_mastery = self.db.query(SkillMastery).filter(
            and_(
                SkillMastery.user_id == user_id,
                SkillMastery.skill_name == skill_data.skill_name,
                SkillMastery.module_type == skill_data.module_type
            )
        ).first()
        
        if existing_mastery:
            # Update existing mastery
            for field, value in skill_data.dict(exclude_unset=True).items():
                if field == "current_level" and value != existing_mastery.current_level:
                    existing_mastery.previous_level = existing_mastery.current_level
                    existing_mastery.level_upgraded_at = datetime.utcnow()
                setattr(existing_mastery, field, value)
            
            # Calculate improvement rate
            existing_mastery.improvement_rate = self._calculate_improvement_rate(existing_mastery)
            
            self.db.commit()
            self.db.refresh(existing_mastery)
            return existing_mastery
        else:
            # Create new mastery record
            mastery = SkillMastery(
                id=str(uuid.uuid4()),
                user_id=user_id,
                skill_name=skill_data.skill_name,
                module_type=skill_data.module_type,
                current_level=skill_data.current_level,
                mastery_score=skill_data.mastery_score,
                total_attempts=skill_data.total_attempts,
                successful_attempts=skill_data.successful_attempts,
                average_score=skill_data.average_score,
                best_score=skill_data.best_score,
                total_time_spent=skill_data.total_time_spent,
                last_practiced=datetime.utcnow()
            )
            
            self.db.add(mastery)
            self.db.commit()
            self.db.refresh(mastery)
            return mastery
    
    def get_skill_gap_analysis(self, user_id: str) -> List[SkillGapAnalysis]:
        """Analyze skill gaps for a user."""
        skill_mastery = self.db.query(SkillMastery).filter(
            SkillMastery.user_id == user_id
        ).all()
        
        gap_analysis = []
        for mastery in skill_mastery:
            # Determine target level based on user's goals
            target_level = self._determine_target_level(mastery.current_level)
            
            # Calculate gap size
            gap_size = self._calculate_skill_gap(mastery.mastery_score, target_level)
            
            # Generate recommended actions
            recommended_actions = self._generate_skill_improvement_actions(
                mastery.skill_name, mastery.module_type, mastery.current_level, target_level
            )
            
            gap_analysis.append(SkillGapAnalysis(
                skill_name=mastery.skill_name,
                module_type=mastery.module_type,
                current_level=mastery.current_level,
                target_level=target_level,
                mastery_score=mastery.mastery_score,
                gap_size=gap_size,
                recommended_actions=recommended_actions,
                estimated_time_to_target=self._estimate_time_to_target(gap_size)
            ))
        
        return gap_analysis
    
    # Analytics and Insights
    def get_learning_dashboard_stats(self, user_id: str) -> LearningDashboardStats:
        """Get comprehensive learning dashboard statistics."""
        # Learning paths stats
        learning_paths = self.db.query(LearningPath).filter(LearningPath.user_id == user_id).all()
        total_paths = len(learning_paths)
        active_paths = len([p for p in learning_paths if p.status == LearningPathStatus.ACTIVE])
        completed_paths = len([p for p in learning_paths if p.status == LearningPathStatus.COMPLETED])
        
        # Study time stats
        progress_summary = self.get_user_progress_summary(user_id, days=30)
        total_study_time_hours = progress_summary["total_study_time"] / 60
        average_daily_study_time = total_study_time_hours / 30
        
        # Objectives completed
        total_objectives = sum(p.total_objectives for p in learning_paths)
        completed_objectives = sum(p.completed_objectives for p in learning_paths)
        
        # Streak calculation
        current_streak, longest_streak = self._calculate_study_streaks(user_id)
        
        # Skill mastery stats
        skill_mastery = self.db.query(SkillMastery).filter(SkillMastery.user_id == user_id).all()
        skills_mastered = len([s for s in skill_mastery if s.current_level in [SkillLevel.ADVANCED, SkillLevel.EXPERT]])
        skills_in_progress = len([s for s in skill_mastery if s.current_level in [SkillLevel.INTERMEDIATE, SkillLevel.UPPER_INTERMEDIATE]])
        
        # Recommendations stats
        recommendations = self.db.query(Recommendation).filter(Recommendation.user_id == user_id).all()
        recommendations_accepted = len([r for r in recommendations if r.is_accepted])
        recommendations_pending = len([r for r in recommendations if not r.is_viewed])
        
        return LearningDashboardStats(
            total_learning_paths=total_paths,
            active_learning_paths=active_paths,
            completed_learning_paths=completed_paths,
            total_study_time_hours=total_study_time_hours,
            average_daily_study_time=average_daily_study_time,
            total_objectives_completed=completed_objectives,
            current_streak_days=current_streak,
            longest_streak_days=longest_streak,
            average_score=progress_summary["average_score"],
            improvement_rate=self._calculate_overall_improvement_rate(user_id),
            skills_mastered=skills_mastered,
            skills_in_progress=skills_in_progress,
            recommendations_accepted=recommendations_accepted,
            recommendations_pending=recommendations_pending
        )
    
    def get_personalized_insights(self, user_id: str) -> PersonalizedInsights:
        """Generate personalized learning insights for a user."""
        # Analyze learning patterns
        learning_velocity = self._calculate_learning_velocity(user_id)
        preferred_times = self._analyze_preferred_study_times(user_id)
        preferred_content = self._analyze_preferred_content_types(user_id)
        
        # Analyze strengths and weaknesses
        strengths, weaknesses = self._analyze_strengths_weaknesses(user_id)
        
        # Generate improvement opportunities
        improvement_opportunities = self._generate_improvement_opportunities(user_id)
        
        # Generate next best actions
        next_best_actions = self._generate_next_best_actions(user_id)
        
        # Predict band score
        predicted_band_score = self._predict_band_score(user_id)
        
        # Estimate time to target
        time_to_target = self._estimate_time_to_target_score(user_id, predicted_band_score)
        
        return PersonalizedInsights(
            learning_velocity=learning_velocity,
            preferred_study_times=preferred_times,
            preferred_content_types=preferred_content,
            strengths=strengths,
            weaknesses=weaknesses,
            improvement_opportunities=improvement_opportunities,
            next_best_actions=next_best_actions,
            predicted_band_score=predicted_band_score,
            time_to_target=time_to_target
        )
    
    # Private helper methods
    def _generate_path_structure(self, user_id: str, path_data: LearningPathCreate) -> Dict[str, Any]:
        """Generate AI-powered learning path structure."""
        # Analyze user's current skills and gaps
        skill_gaps = self._identify_skill_gaps(user_id)
        priority_areas = self._identify_priority_areas(user_id, path_data.target_band_score)
        
        # Generate difficulty progression
        difficulty_progression = self._generate_difficulty_progression(
            user_id, path_data.target_band_score
        )
        
        # Generate learning objectives
        objectives = self._generate_learning_objectives(
            user_id, skill_gaps, priority_areas, path_data.target_band_score
        )
        
        return {
            "skill_gaps": skill_gaps,
            "priority_areas": priority_areas,
            "difficulty_progression": difficulty_progression,
            "objectives": objectives
        }
    
    def _create_learning_objectives(self, path_id: str, objectives_data: List[Dict[str, Any]]) -> None:
        """Create learning objectives for a path."""
        for i, obj_data in enumerate(objectives_data):
            objective = LearningObjective(
                id=str(uuid.uuid4()),
                learning_path_id=path_id,
                title=obj_data["title"],
                description=obj_data.get("description"),
                objective_type=LearningObjectiveType(obj_data["type"]),
                target_skill=obj_data.get("target_skill"),
                target_score=obj_data.get("target_score"),
                estimated_time_minutes=obj_data.get("estimated_time", 30),
                difficulty_level=SkillLevel(obj_data.get("difficulty", "intermediate")),
                content_items=obj_data.get("content_items", []),
                required_activities=obj_data.get("required_activities", []),
                optional_activities=obj_data.get("optional_activities", []),
                sort_order=i,
                prerequisites=obj_data.get("prerequisites", []),
                unlocks=obj_data.get("unlocks", [])
            )
            self.db.add(objective)
        
        self.db.commit()
    
    def _analyze_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's learning profile and preferences."""
        # Get user's progress history
        progress_records = self.db.query(UserProgress).filter(
            UserProgress.user_id == user_id
        ).all()
        
        # Get user's test results
        test_sessions = self.db.query(TestSession).filter(
            and_(
                TestSession.user_id == user_id,
                TestSession.status == TestStatus.COMPLETED
            )
        ).all()
        
        # Get user's content preferences
        content_usage = self.db.query(ContentItem).join(UserProgress).filter(
            UserProgress.user_id == user_id
        ).all()
        
        return {
            "progress_records": progress_records,
            "test_sessions": test_sessions,
            "content_usage": content_usage,
            "average_score": np.mean([t.score_data.get("overall_score", 0.0) for t in test_sessions if t.score_data]) if test_sessions else 0.0,
            "preferred_content_types": self._get_preferred_content_types(content_usage),
            "study_patterns": self._analyze_study_patterns(progress_records)
        }
    
    def _generate_content_based_recommendations(self, user_id: str, user_profile: Dict[str, Any], limit: int) -> List[Recommendation]:
        """Generate content-based recommendations."""
        recommendations = []
        
        # Get content items similar to what user has engaged with
        preferred_types = user_profile.get("preferred_content_types", [])
        
        similar_content = self.db.query(ContentItem).filter(
            and_(
                ContentItem.status == "published",
                ContentItem.content_type.in_(preferred_types)
            )
        ).limit(limit).all()
        
        for content in similar_content:
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                user_id=user_id,
                recommendation_type=RecommendationType.CONTENT_BASED,
                title=f"Practice {content.content_type.value.replace('_', ' ').title()}",
                description=f"Based on your preferences, try this {content.difficulty_level} level content",
                reasoning="Similar to content you've enjoyed in the past",
                confidence_score=0.8,
                priority_score=0.7,
                content_item_id=content.id,
                estimated_impact=0.6,
                time_to_complete=content.estimated_time or 30
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_performance_based_recommendations(self, user_id: str, user_profile: Dict[str, Any], limit: int) -> List[Recommendation]:
        """Generate performance-based recommendations."""
        recommendations = []
        
        # Identify weak areas based on test results
        weak_areas = self._identify_weak_areas(user_profile.get("test_sessions", []))
        
        for area in weak_areas[:limit]:
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                user_id=user_id,
                recommendation_type=RecommendationType.PERFORMANCE_BASED,
                title=f"Improve {area['skill']} Skills",
                description=f"Focus on {area['skill']} to improve your overall performance",
                reasoning=f"Your {area['skill']} score is {area['score']:.1f}, below target",
                confidence_score=0.9,
                priority_score=0.8,
                action_type="skill_improvement",
                action_data={"skill": area["skill"], "target_score": area["target_score"]},
                estimated_impact=0.8,
                time_to_complete=45
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_context_aware_recommendations(self, user_id: str, user_profile: Dict[str, Any], limit: int) -> List[Recommendation]:
        """Generate context-aware recommendations."""
        recommendations = []
        
        # Analyze current time and user's study patterns
        current_hour = datetime.utcnow().hour
        study_patterns = user_profile.get("study_patterns", {})
        
        # Recommend based on optimal study times
        if current_hour in study_patterns.get("peak_hours", []):
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                user_id=user_id,
                recommendation_type=RecommendationType.CONTEXT_AWARE,
                title="Optimal Study Time",
                description="This is your peak study time. Take advantage of it!",
                reasoning="You perform best during this time of day",
                confidence_score=0.7,
                priority_score=0.6,
                action_type="study_session",
                action_data={"duration": 60, "focus": "intensive"},
                estimated_impact=0.7,
                time_to_complete=60
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _update_skill_mastery(self, user_id: str, progress_data: UserProgressCreate) -> None:
        """Update skill mastery based on progress data."""
        if not progress_data.content_item_id:
            return
        
        # Get content item to determine skill area
        content_item = self.db.query(ContentItem).filter(
            ContentItem.id == progress_data.content_item_id
        ).first()
        
        if not content_item:
            return
        
        # Determine skill name based on content type
        skill_name = self._map_content_type_to_skill(content_item.content_type)
        
        # Calculate mastery score
        mastery_score = self._calculate_mastery_score(progress_data)
        
        # Update or create skill mastery
        skill_data = SkillMasteryCreate(
            skill_name=skill_name,
            module_type=content_item.content_type.value,
            current_level=self._determine_skill_level(mastery_score),
            mastery_score=mastery_score,
            total_attempts=1,
            successful_attempts=1 if progress_data.score and progress_data.score >= 70 else 0,
            average_score=progress_data.score or 0.0,
            best_score=progress_data.score or 0.0,
            total_time_spent=progress_data.time_spent_minutes
        )
        
        self.update_skill_mastery(user_id, skill_data)
    
    def _calculate_mastery_score(self, progress_data: UserProgressCreate) -> float:
        """Calculate mastery score from progress data."""
        score = progress_data.score or 0.0
        accuracy = progress_data.accuracy or 0.0
        completion_rate = progress_data.completion_rate or 0.0
        
        # Weighted average
        mastery_score = (score * 0.4 + accuracy * 0.4 + completion_rate * 0.2) / 100
        return min(max(mastery_score, 0.0), 1.0)
    
    def _determine_skill_level(self, mastery_score: float) -> SkillLevel:
        """Determine skill level based on mastery score."""
        if mastery_score >= 0.9:
            return SkillLevel.EXPERT
        elif mastery_score >= 0.8:
            return SkillLevel.ADVANCED
        elif mastery_score >= 0.6:
            return SkillLevel.UPPER_INTERMEDIATE
        elif mastery_score >= 0.4:
            return SkillLevel.INTERMEDIATE
        elif mastery_score >= 0.2:
            return SkillLevel.ELEMENTARY
        else:
            return SkillLevel.BEGINNER
    
    def _map_content_type_to_skill(self, content_type: ContentType) -> str:
        """Map content type to skill name."""
        mapping = {
            ContentType.READING_PASSAGE: "Reading Comprehension",
            ContentType.LISTENING_AUDIO: "Listening Comprehension",
            ContentType.WRITING_PROMPT: "Writing Skills",
            ContentType.SPEAKING_TOPIC: "Speaking Skills",
            ContentType.GRAMMAR_LESSON: "Grammar",
            ContentType.VOCABULARY_LESSON: "Vocabulary"
        }
        return mapping.get(content_type, "General Skills")
    
    def _calculate_study_streaks(self, user_id: str) -> Tuple[int, int]:
        """Calculate current and longest study streaks."""
        # Implementation would analyze daily study patterns
        # For now, return placeholder values
        return 5, 12
    
    def _calculate_overall_improvement_rate(self, user_id: str) -> float:
        """Calculate overall improvement rate."""
        # Implementation would analyze score trends over time
        # For now, return placeholder value
        return 0.15
    
    def _calculate_learning_velocity(self, user_id: str) -> float:
        """Calculate learning velocity (progress per unit time)."""
        # Implementation would analyze progress over time
        # For now, return placeholder value
        return 0.25
    
    def _analyze_preferred_study_times(self, user_id: str) -> List[str]:
        """Analyze user's preferred study times."""
        # Implementation would analyze study session timing
        # For now, return placeholder values
        return ["09:00", "14:00", "20:00"]
    
    def _analyze_preferred_content_types(self, user_id: str) -> List[str]:
        """Analyze user's preferred content types."""
        # Implementation would analyze content engagement
        # For now, return placeholder values
        return ["reading_passage", "listening_audio"]
    
    def _analyze_strengths_weaknesses(self, user_id: str) -> Tuple[List[str], List[str]]:
        """Analyze user's strengths and weaknesses."""
        # Implementation would analyze performance patterns
        # For now, return placeholder values
        strengths = ["Reading Comprehension", "Vocabulary"]
        weaknesses = ["Speaking Fluency", "Grammar Accuracy"]
        return strengths, weaknesses
    
    def _generate_improvement_opportunities(self, user_id: str) -> List[str]:
        """Generate improvement opportunities."""
        # Implementation would identify specific areas for improvement
        # For now, return placeholder values
        return [
            "Practice speaking with native speakers",
            "Focus on grammar rules",
            "Expand vocabulary in academic contexts"
        ]
    
    def _generate_next_best_actions(self, user_id: str) -> List[str]:
        """Generate next best actions for the user."""
        # Implementation would prioritize actions based on impact
        # For now, return placeholder values
        return [
            "Complete today's recommended practice",
            "Review yesterday's mistakes",
            "Take a mock test to assess progress"
        ]
    
    def _predict_band_score(self, user_id: str) -> float:
        """Predict user's current band score."""
        # Implementation would use ML model to predict score
        # For now, return placeholder value
        return 6.5
    
    def _estimate_time_to_target_score(self, user_id: str, current_score: float) -> int:
        """Estimate time to reach target score."""
        # Implementation would calculate based on learning velocity
        # For now, return placeholder value
        return 30
    
    # Additional helper methods
    def _identify_skill_gaps(self, user_id: str) -> List[str]:
        """Identify skill gaps for a user."""
        # Implementation would analyze test results and performance
        # For now, return placeholder values
        return ["Speaking Fluency", "Grammar Accuracy", "Academic Vocabulary"]
    
    def _identify_priority_areas(self, user_id: str, target_band_score: Optional[float]) -> List[str]:
        """Identify priority areas for improvement."""
        # Implementation would prioritize based on target score and current performance
        # For now, return placeholder values
        return ["Reading Speed", "Listening Comprehension", "Writing Coherence"]
    
    def _generate_difficulty_progression(self, user_id: str, target_band_score: Optional[float]) -> Dict[str, Any]:
        """Generate difficulty progression for learning path."""
        # Implementation would create adaptive difficulty curve
        # For now, return placeholder structure
        return {
            "initial_level": "intermediate",
            "progression_rate": 0.1,
            "milestones": [0.25, 0.5, 0.75, 1.0]
        }
    
    def _generate_learning_objectives(self, user_id: str, skill_gaps: List[str], priority_areas: List[str], target_band_score: Optional[float]) -> List[Dict[str, Any]]:
        """Generate learning objectives for a path."""
        objectives = []
        
        # Create objectives for skill gaps
        for i, skill in enumerate(skill_gaps[:3]):  # Limit to 3 objectives
            objectives.append({
                "title": f"Improve {skill}",
                "description": f"Focus on developing {skill.lower()} skills",
                "type": "skill_improvement",
                "target_skill": skill,
                "target_score": 80.0,
                "estimated_time": 45,
                "difficulty": "intermediate",
                "content_items": [],
                "required_activities": [f"practice_{skill.lower().replace(' ', '_')}"],
                "optional_activities": [],
                "prerequisites": [],
                "unlocks": []
            })
        
        return objectives
    
    def _get_preferred_content_types(self, content_usage: List[ContentItem]) -> List[str]:
        """Get user's preferred content types."""
        if not content_usage:
            return ["reading_passage", "listening_audio"]
        
        # Count content type usage
        type_counts = {}
        for content in content_usage:
            content_type = content.content_type.value
            type_counts[content_type] = type_counts.get(content_type, 0) + 1
        
        # Return top 3 preferred types
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        return [content_type for content_type, _ in sorted_types[:3]]
    
    def _analyze_study_patterns(self, progress_records: List[UserProgress]) -> Dict[str, Any]:
        """Analyze user's study patterns."""
        if not progress_records:
            return {"peak_hours": [9, 14, 20], "average_session_length": 30}
        
        # Analyze session timing and duration
        session_hours = [p.session_start.hour for p in progress_records]
        session_lengths = [p.time_spent_minutes for p in progress_records if p.time_spent_minutes]
        
        # Find peak study hours (most common hours)
        hour_counts = {}
        for hour in session_hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_hours = [hour for hour, _ in peak_hours]
        
        average_session_length = np.mean(session_lengths) if session_lengths else 30
        
        return {
            "peak_hours": peak_hours,
            "average_session_length": average_session_length
        }
    
    def _identify_weak_areas(self, test_sessions: List[TestSession]) -> List[Dict[str, Any]]:
        """Identify weak areas based on test results."""
        if not test_sessions:
            return []
        
        # Analyze module scores from score_data
        module_scores = {}
        for session in test_sessions:
            if session.score_data:
                scores = session.score_data.get("module_scores", {})
                for module, score in scores.items():
                    if module not in module_scores:
                        module_scores[module] = []
                    module_scores[module].append(score)
        
        weak_areas = []
        for module, scores in module_scores.items():
            avg_score = np.mean(scores)
            if avg_score < 6.0:  # Below band 6
                weak_areas.append({
                    "skill": module,
                    "score": avg_score,
                    "target_score": 6.5
                })
        
        return weak_areas
    
    def _determine_target_level(self, current_level: SkillLevel) -> SkillLevel:
        """Determine target level for skill improvement."""
        level_progression = {
            SkillLevel.BEGINNER: SkillLevel.ELEMENTARY,
            SkillLevel.ELEMENTARY: SkillLevel.INTERMEDIATE,
            SkillLevel.INTERMEDIATE: SkillLevel.UPPER_INTERMEDIATE,
            SkillLevel.UPPER_INTERMEDIATE: SkillLevel.ADVANCED,
            SkillLevel.ADVANCED: SkillLevel.EXPERT,
            SkillLevel.EXPERT: SkillLevel.EXPERT
        }
        return level_progression.get(current_level, SkillLevel.INTERMEDIATE)
    
    def _calculate_skill_gap(self, mastery_score: float, target_level: SkillLevel) -> float:
        """Calculate gap between current mastery and target level."""
        level_scores = {
            SkillLevel.BEGINNER: 0.0,
            SkillLevel.ELEMENTARY: 0.2,
            SkillLevel.INTERMEDIATE: 0.4,
            SkillLevel.UPPER_INTERMEDIATE: 0.6,
            SkillLevel.ADVANCED: 0.8,
            SkillLevel.EXPERT: 0.9
        }
        target_score = level_scores.get(target_level, 0.6)
        return max(0.0, target_score - mastery_score)
    
    def _generate_skill_improvement_actions(self, skill_name: str, module_type: str, current_level: SkillLevel, target_level: SkillLevel) -> List[str]:
        """Generate recommended actions for skill improvement."""
        actions = []
        
        if skill_name == "Reading Comprehension":
            actions.extend([
                "Practice skimming and scanning techniques",
                "Read academic articles regularly",
                "Work on vocabulary building"
            ])
        elif skill_name == "Listening Comprehension":
            actions.extend([
                "Listen to podcasts and lectures",
                "Practice note-taking during listening",
                "Work on accent recognition"
            ])
        elif skill_name == "Writing Skills":
            actions.extend([
                "Practice essay structure and organization",
                "Work on grammar and punctuation",
                "Expand academic vocabulary"
            ])
        elif skill_name == "Speaking Skills":
            actions.extend([
                "Practice with speaking partners",
                "Record and analyze your speech",
                "Work on pronunciation and fluency"
            ])
        
        return actions
    
    def _estimate_time_to_target(self, gap_size: float) -> int:
        """Estimate time to reach target (in minutes)."""
        # Rough estimation: 1 hour per 0.1 gap size
        return int(gap_size * 600)  # Convert to minutes
    
    def _calculate_improvement_rate(self, mastery: SkillMastery) -> float:
        """Calculate improvement rate for skill mastery."""
        # Implementation would analyze historical data
        # For now, return placeholder value
        return 0.1
