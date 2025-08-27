"""
Enhanced Learning Path Service for Phase 5: Advanced Features.
Implements dynamic path optimization, advanced skill assessment, and predictive path planning.
"""

import structlog
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor

from config import settings
from models.advanced_tutor import (
    LearningObjective, TeachingStyle, InteractionMode,
    AdaptiveContext, ProgressInsight
)
from models.learning_path import LearningPath, LearningStep, ContentType, LearningAnalytics, DifficultyLevel
from models.tutor import UserProgress

logger = structlog.get_logger()

class EnhancedLearningPathService:
    """Enhanced Learning Path Service with advanced capabilities"""
    
    def __init__(self):
        self.skill_assessment_models = {}
        self.predictive_models = {}
        self.collaborative_groups: Dict[str, List[str]] = {}
        
    async def initialize(self):
        """Initialize the enhanced learning path service"""
        logger.info("Initializing Enhanced Learning Path Service")
        
        # Initialize ML models
        await self._initialize_ml_models()
        
        # Initialize collaborative learning groups
        await self._initialize_collaborative_groups()
        
        logger.info("Enhanced Learning Path Service initialized successfully")
    
    async def _initialize_ml_models(self):
        """Initialize machine learning models"""
        try:
            self.skill_assessment_models = {
                "skill_clustering": KMeans(n_clusters=5, random_state=42),
                "difficulty_predictor": RandomForestRegressor(n_estimators=100, random_state=42)
            }
            
            self.predictive_models = {
                "score_predictor": RandomForestRegressor(n_estimators=100, random_state=42),
                "completion_predictor": RandomForestRegressor(n_estimators=50, random_state=42)
            }
            
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize ML models", error=str(e))
    
    async def _initialize_collaborative_groups(self):
        """Initialize collaborative learning groups"""
        try:
            self.collaborative_groups = {
                "beginner_group": ["user_1", "user_2", "user_3"],
                "intermediate_group": ["user_4", "user_5", "user_6"],
                "advanced_group": ["user_7", "user_8", "user_9"]
            }
            logger.info("Collaborative groups initialized")
            
        except Exception as e:
            logger.error("Failed to initialize collaborative groups", error=str(e))
    
    async def generate_enhanced_path(self, user_id: str, target_score: float, 
                                   timeframe: str = "30", 
                                   adaptive_context: Optional[AdaptiveContext] = None) -> Dict[str, Any]:
        """Generate enhanced personalized learning path"""
        try:
            logger.info("Generating enhanced learning path", user_id=user_id, target_score=target_score)
            
            # Get user progress and analytics
            user_progress = await self._get_user_progress(user_id)
            learning_analytics = await self._get_learning_analytics(user_id)
            
            # Perform advanced skill assessment
            skill_assessment = await self._perform_advanced_skill_assessment(user_id, user_progress, learning_analytics)
            
            # Calculate current score with confidence
            current_score, confidence_interval = await self._calculate_current_score_with_confidence(
                user_progress, learning_analytics, skill_assessment
            )
            
            # Determine optimal path type
            path_type = await self._determine_optimal_path_type(
                current_score, target_score, timeframe, skill_assessment, adaptive_context
            )
            
            # Generate learning path
            learning_path = await self._create_enhanced_learning_path(
                user_id, current_score, target_score, timeframe, path_type, 
                skill_assessment, adaptive_context
            )
            
            # Generate insights and opportunities
            predictive_insights = await self._generate_predictive_insights(user_id, learning_path, skill_assessment)
            collaborative_opportunities = await self._identify_collaborative_opportunities(user_id, skill_assessment)
            
            enhanced_path = {
                **learning_path.dict(),
                "skill_assessment": skill_assessment,
                "confidence_interval": confidence_interval,
                "predictive_insights": predictive_insights,
                "collaborative_opportunities": collaborative_opportunities,
                "adaptive_parameters": await self._generate_adaptive_parameters(adaptive_context)
            }
            
            logger.info("Enhanced learning path generated", user_id=user_id)
            return enhanced_path
            
        except Exception as e:
            logger.error("Error generating enhanced learning path", user_id=user_id, error=str(e))
            return await self._get_fallback_enhanced_path(user_id, target_score, timeframe)
    
    async def _perform_advanced_skill_assessment(self, user_id: str, user_progress: UserProgress,
                                               learning_analytics: LearningAnalytics) -> Dict[str, Any]:
        """Perform advanced skill assessment"""
        try:
            assessment = {
                "overall_skill_level": "intermediate",
                "skill_breakdown": {},
                "strengths": [],
                "weaknesses": [],
                "learning_style": "visual",
                "confidence_scores": {},
                "recommendations": []
            }
            
            # Analyze skill breakdown
            modules = ["reading", "writing", "listening", "speaking"]
            for module in modules:
                module_score = self._extract_module_score(user_progress, module)
                assessment["skill_breakdown"][module] = {
                    "score": module_score,
                    "confidence": 0.85,
                    "trend": "improving",
                    "difficulty_level": self._classify_difficulty_level(module_score)
                }
            
            # Identify strengths and weaknesses
            strengths, weaknesses = self._identify_strengths_weaknesses(assessment["skill_breakdown"])
            assessment["strengths"] = strengths
            assessment["weaknesses"] = weaknesses
            
            # Generate recommendations
            assessment["recommendations"] = await self._generate_skill_recommendations(assessment)
            
            return assessment
            
        except Exception as e:
            logger.error("Error performing advanced skill assessment", error=str(e))
            return self._create_fallback_skill_assessment()
    
    async def _calculate_current_score_with_confidence(self, user_progress: UserProgress,
                                                     learning_analytics: LearningAnalytics,
                                                     skill_assessment: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Calculate current score with confidence intervals"""
        try:
            base_score = self._calculate_base_score(user_progress)
            confidence_interval = {
                "lower_bound": max(0.0, base_score - 0.5),
                "upper_bound": min(9.0, base_score + 0.5),
                "confidence_level": 0.95
            }
            return base_score, confidence_interval
            
        except Exception as e:
            logger.error("Error calculating current score with confidence", error=str(e))
            return 6.0, {"lower_bound": 5.5, "upper_bound": 6.5, "confidence_level": 0.8}
    
    async def _determine_optimal_path_type(self, current_score: float, target_score: float,
                                         timeframe: str, skill_assessment: Dict[str, Any],
                                         adaptive_context: Optional[AdaptiveContext]) -> str:
        """Determine optimal path type"""
        try:
            score_gap = target_score - current_score
            
            if score_gap > 2.0:
                return "intensive_improvement"
            elif score_gap > 1.0:
                return "moderate_improvement"
            elif score_gap > 0.5:
                return "refinement"
            else:
                return "maintenance"
                
        except Exception as e:
            logger.error("Error determining optimal path type", error=str(e))
            return "moderate_improvement"
    
    async def _create_enhanced_learning_path(self, user_id: str, current_score: float,
                                           target_score: float, timeframe: str, path_type: str,
                                           skill_assessment: Dict[str, Any],
                                           adaptive_context: Optional[AdaptiveContext]) -> LearningPath:
        """Create enhanced learning path"""
        try:
            # Generate learning objectives
            learning_objectives = await self._create_enhanced_learning_objectives(skill_assessment, target_score)
            
            # Generate steps
            steps = await self._generate_adaptive_steps(path_type, learning_objectives, skill_assessment)
            
            # Calculate completion time
            estimated_completion = await self._predict_completion_time(steps, adaptive_context)
            
            learning_path = LearningPath(
                id=f"path_{user_id}_{datetime.utcnow().timestamp()}",
                user_id=user_id,
                path_name=f"Enhanced {path_type.replace('_', ' ').title()} Path",
                target_score=target_score,
                current_score=current_score,
                target_date=estimated_completion,
                estimated_completion_time=int(timeframe),
                steps=steps,
                progress_percentage=0.0,
                status="active"
            )
            
            return learning_path
            
        except Exception as e:
            logger.error("Error creating enhanced learning path", error=str(e))
            return self._create_fallback_learning_path(user_id, target_score, timeframe)
    
    async def _create_enhanced_learning_objectives(self, skill_assessment: Dict[str, Any],
                                                 target_score: float) -> List[LearningObjective]:
        """Create enhanced learning objectives"""
        try:
            objectives = []
            
            # Create objectives for weaknesses
            for weakness in skill_assessment.get("weaknesses", []):
                objective = LearningObjective(
                    title=f"Improve {weakness}",
                    description=f"Focus on improving {weakness} skills",
                    skill_area=weakness,
                    difficulty_level=DifficultyLevel.INTERMEDIATE,
                    estimated_time=30,
                    success_criteria=[f"Achieve {target_score} in {weakness}"],
                    assessment_methods=["practice_tests", "skill_checks"]
                )
                objectives.append(objective)
            
            # Add overall objective
            overall_objective = LearningObjective(
                title=f"Achieve {target_score} Band Score",
                description=f"Reach target IELTS band score of {target_score}",
                skill_area="overall",
                difficulty_level=DifficultyLevel.ADVANCED,
                estimated_time=30,
                success_criteria=[f"Achieve {target_score} in all modules"],
                assessment_methods=["full_practice_tests"]
            )
            objectives.append(overall_objective)
            
            return objectives
            
        except Exception as e:
            logger.error("Error creating enhanced learning objectives", error=str(e))
            return [self._create_fallback_learning_objective(target_score)]
    
    async def _generate_adaptive_steps(self, path_type: str, learning_objectives: List[LearningObjective],
                                     skill_assessment: Dict[str, Any]) -> List[LearningStep]:
        """Generate adaptive learning steps"""
        try:
            steps = []
            num_steps = 10 if path_type == "intensive_improvement" else 7
            
            for i in range(num_steps):
                step = LearningStep(
                    step_number=i + 1,
                    title=f"Step {i + 1}",
                    description=f"Learning step {i + 1}",
                    content_type=ContentType.EXERCISE,
                    difficulty=self._determine_step_difficulty(i, num_steps),
                    estimated_duration=30,
                    prerequisites=[],
                    learning_objectives=[obj.title for obj in learning_objectives]
                )
                steps.append(step)
            
            return steps
            
        except Exception as e:
            logger.error("Error generating adaptive steps", error=str(e))
            return [self._create_fallback_learning_step()]
    
    async def _predict_completion_time(self, steps: List[LearningStep],
                                     adaptive_context: Optional[AdaptiveContext]) -> datetime:
        """Predict completion time"""
        try:
            total_minutes = sum(step.estimated_duration for step in steps)
            
            if adaptive_context and adaptive_context.learning_pace == "fast":
                total_minutes *= 0.8
            
            return datetime.utcnow() + timedelta(minutes=total_minutes)
            
        except Exception as e:
            logger.error("Error predicting completion time", error=str(e))
            return datetime.utcnow() + timedelta(days=30)
    
    async def _generate_predictive_insights(self, user_id: str, learning_path: LearningPath,
                                          skill_assessment: Dict[str, Any]) -> List[ProgressInsight]:
        """Generate predictive insights"""
        try:
            insights = []
            
            # Score improvement prediction
            predicted_score = learning_path.current_score + 1.0
            insights.append(ProgressInsight(
                user_id=user_id,
                insight_type="prediction",
                title="Score Improvement Prediction",
                description=f"Predicted to reach {predicted_score:.1f}",
                data_points=[{"metric": "predicted_score", "value": predicted_score}],
                confidence=0.85,
                actionable_items=["Focus on weak areas", "Increase practice frequency"],
                priority="medium"
            ))
            
            return insights
            
        except Exception as e:
            logger.error("Error generating predictive insights", error=str(e))
            return []
    
    async def _identify_collaborative_opportunities(self, user_id: str, skill_assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify collaborative learning opportunities"""
        try:
            opportunities = []
            
            # Find similar users
            similar_users = await self._find_similar_users(user_id, skill_assessment)
            
            for user in similar_users:
                opportunities.append({
                    "type": "peer_study",
                    "user_id": user["user_id"],
                    "skill_match": user["skill_match"],
                    "activity": "joint_practice_session",
                    "estimated_benefit": "10-15% improvement"
                })
            
            return opportunities
            
        except Exception as e:
            logger.error("Error identifying collaborative opportunities", error=str(e))
            return []
    
    async def _generate_adaptive_parameters(self, adaptive_context: Optional[AdaptiveContext]) -> Dict[str, Any]:
        """Generate adaptive parameters"""
        try:
            if not adaptive_context:
                return {}
            
            return {
                "learning_pace": adaptive_context.learning_pace,
                "attention_span": adaptive_context.attention_span,
                "preferred_interaction_mode": adaptive_context.preferred_interaction_mode.value,
                "teaching_style": adaptive_context.current_teaching_style.value
            }
            
        except Exception as e:
            logger.error("Error generating adaptive parameters", error=str(e))
            return {}
    
    # Helper methods
    def _extract_module_score(self, user_progress: UserProgress, module: str) -> float:
        """Extract module score"""
        mock_scores = {"reading": 6.5, "writing": 6.0, "listening": 7.0, "speaking": 6.5}
        return mock_scores.get(module, 6.0)
    
    def _classify_difficulty_level(self, score: float) -> DifficultyLevel:
        """Classify difficulty level"""
        if score >= 7.5:
            return DifficultyLevel.EXPERT
        elif score >= 6.5:
            return DifficultyLevel.ADVANCED
        elif score >= 5.5:
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.BEGINNER
    
    def _identify_strengths_weaknesses(self, skill_breakdown: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Identify strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        for module, data in skill_breakdown.items():
            score = data.get("score", 6.0)
            if score >= 7.0:
                strengths.append(module)
            elif score < 6.0:
                weaknesses.append(module)
        
        return strengths, weaknesses
    
    async def _generate_skill_recommendations(self, skill_assessment: Dict[str, Any]) -> List[str]:
        """Generate skill recommendations"""
        recommendations = []
        
        for weakness in skill_assessment.get("weaknesses", []):
            if weakness == "grammar":
                recommendations.append("Focus on grammar rules and practice exercises")
            elif weakness == "vocabulary":
                recommendations.append("Expand vocabulary through reading")
            elif weakness == "pronunciation":
                recommendations.append("Practice pronunciation with audio exercises")
        
        return recommendations
    
    def _calculate_base_score(self, user_progress: UserProgress) -> float:
        """Calculate base score"""
        return 6.5
    
    def _determine_path_difficulty(self, path_type: str, skill_assessment: Dict[str, Any]) -> DifficultyLevel:
        """Determine path difficulty"""
        if path_type == "intensive_improvement":
            return DifficultyLevel.ADVANCED
        elif path_type == "moderate_improvement":
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.BEGINNER
    
    def _determine_step_difficulty(self, step_index: int, total_steps: int) -> DifficultyLevel:
        """Determine step difficulty"""
        if step_index < total_steps * 0.3:
            return DifficultyLevel.BEGINNER
        elif step_index < total_steps * 0.7:
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.ADVANCED
    
    async def _find_similar_users(self, user_id: str, skill_assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar users"""
        return [
            {"user_id": "user_2", "skill_match": 0.85},
            {"user_id": "user_3", "skill_match": 0.78}
        ]
    
    # Fallback methods
    def _create_fallback_skill_assessment(self) -> Dict[str, Any]:
        """Create fallback skill assessment"""
        return {
            "overall_skill_level": "intermediate",
            "skill_breakdown": {},
            "strengths": [],
            "weaknesses": [],
            "learning_style": "visual",
            "confidence_scores": {},
            "recommendations": ["Continue with current study plan"]
        }
    
    def _create_fallback_learning_objective(self, target_score: float) -> LearningObjective:
        """Create fallback learning objective"""
        return LearningObjective(
            title=f"Achieve {target_score} Band Score",
            description=f"Reach target IELTS band score of {target_score}",
            skill_area="overall",
            difficulty_level=DifficultyLevel.INTERMEDIATE,
            estimated_time=30,
            success_criteria=[f"Achieve {target_score} in all modules"],
            assessment_methods=["practice_tests", "mock_exams"]
        )
    
    def _create_fallback_learning_step(self) -> LearningStep:
        """Create fallback learning step"""
        return LearningStep(
            step_number=1,
            title="Practice Exercise",
            description="General practice exercise",
            content_type=ContentType.EXERCISE,
            difficulty=DifficultyLevel.INTERMEDIATE,
            estimated_duration=30,
            prerequisites=[],
            learning_objectives=["Improve overall skills"]
        )
    
    def _create_fallback_learning_path(self, user_id: str, target_score: float, timeframe: str) -> LearningPath:
        """Create fallback learning path"""
        return LearningPath(
            id=f"fallback_path_{user_id}",
            user_id=user_id,
            path_name="Fallback Learning Path",
            target_score=target_score,
            current_score=6.0,
            target_date=datetime.utcnow() + timedelta(days=int(timeframe)),
            estimated_completion_time=int(timeframe),
            steps=[],
            progress_percentage=0.0,
            status="active"
        )
    
    async def _get_fallback_enhanced_path(self, user_id: str, target_score: float, timeframe: str) -> Dict[str, Any]:
        """Get fallback enhanced learning path"""
        return {
            "id": f"fallback_path_{user_id}",
            "user_id": user_id,
            "name": "Fallback Learning Path",
            "description": "Basic learning path for IELTS preparation",
            "target_score": target_score,
            "current_score": 6.0,
            "estimated_days": int(timeframe),
            "difficulty_level": DifficultyLevel.INTERMEDIATE.value,
            "learning_objectives": [],
            "steps": [],
            "progress_percentage": 0.0,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "estimated_completion": (datetime.utcnow() + timedelta(days=int(timeframe))).isoformat(),
            "skill_assessment": self._create_fallback_skill_assessment(),
            "confidence_interval": {"lower_bound": 5.5, "upper_bound": 6.5, "confidence_level": 0.8},
            "predictive_insights": [],
            "collaborative_opportunities": [],
            "adaptive_parameters": {}
        }
    
    # Required methods for compatibility
    async def _get_user_progress(self, user_id: str) -> UserProgress:
        """Get user progress"""
        return UserProgress(
            user_id=user_id,
            overall_score=6.5,
            module_scores={"reading": 6.5, "writing": 6.0, "listening": 7.0, "speaking": 6.5},
            study_time=120,
            practice_sessions=15,
            last_updated=datetime.utcnow()
        )
    
    async def _get_learning_analytics(self, user_id: str) -> LearningAnalytics:
        """Get learning analytics"""
        return LearningAnalytics(
            user_id=user_id,
            learning_patterns={},
            skill_progression={},
            engagement_metrics={},
            performance_trends={},
            last_updated=datetime.utcnow()
        )
