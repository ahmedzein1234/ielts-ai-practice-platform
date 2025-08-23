import structlog
import httpx
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random

from config import settings
from models.learning_path import Recommendation, AdaptiveContent, LearningAnalytics, ContentType, DifficultyLevel
from models.tutor import UserProgress

logger = structlog.get_logger()

class RecommendationService:
    """Service for generating personalized learning recommendations"""
    
    def __init__(self):
        self.recommendation_cache: Dict[str, List[Recommendation]] = {}
        self.content_database: Dict[str, List[Dict[str, Any]]] = {}
        
    async def initialize(self):
        """Initialize the recommendation service"""
        logger.info("Initializing Recommendation Service")
        
        # Load content database
        await self._load_content_database()
        
        # Initialize cache
        self.recommendation_cache = {}
        
        logger.info("Recommendation Service initialized successfully")
    
    async def get_recommendations(self, user_id: str, module: Optional[str] = None, 
                                limit: int = 5) -> List[Dict[str, Any]]:
        """Get personalized recommendations for user"""
        try:
            logger.info("Generating recommendations", user_id=user_id, module=module, limit=limit)
            
            # Check cache first
            cache_key = f"{user_id}_{module}_{limit}"
            if cache_key in self.recommendation_cache:
                cached_recommendations = self.recommendation_cache[cache_key]
                if self._is_cache_valid(cached_recommendations):
                    logger.info("Returning cached recommendations", user_id=user_id)
                    return [rec.dict() for rec in cached_recommendations]
            
            # Get user progress and analytics
            user_progress = await self._get_user_progress(user_id)
            learning_analytics = await self._get_learning_analytics(user_id)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                user_id, user_progress, learning_analytics, module, limit
            )
            
            # Cache recommendations
            self.recommendation_cache[cache_key] = recommendations
            
            logger.info("Generated recommendations", user_id=user_id, count=len(recommendations))
            
            return [rec.dict() for rec in recommendations]
            
        except Exception as e:
            logger.error("Error generating recommendations", user_id=user_id, error=str(e))
            return self._get_fallback_recommendations(module, limit)
    
    async def get_adaptive_content(self, user_id: str, module: str, 
                                 current_difficulty: str) -> List[AdaptiveContent]:
        """Get adaptive content based on user performance"""
        try:
            logger.info("Getting adaptive content", user_id=user_id, module=module, difficulty=current_difficulty)
            
            # Get user performance data
            performance_data = await self._get_user_performance(user_id, module)
            
            # Determine optimal difficulty
            optimal_difficulty = self._calculate_optimal_difficulty(
                current_difficulty, performance_data
            )
            
            # Get content at optimal difficulty
            content_list = self.content_database.get(module, [])
            adaptive_content = []
            
            for content in content_list:
                if content.get("difficulty") == optimal_difficulty:
                    adaptive_content.append(AdaptiveContent(
                        content_id=content["id"],
                        content_type=ContentType(content["type"]),
                        difficulty=DifficultyLevel(content["difficulty"]),
                        user_performance_prediction=self._predict_performance(content, performance_data),
                        confidence_score=self._calculate_confidence(content, performance_data),
                        recommended_duration=content.get("duration", 30),
                        learning_objectives=content.get("learning_objectives", []),
                        prerequisites_met=self._check_prerequisites(content, user_id),
                        adaptive_factors={
                            "performance_trend": performance_data.get("trend", "stable"),
                            "weak_areas": performance_data.get("weak_areas", []),
                            "learning_style": performance_data.get("learning_style", "balanced")
                        }
                    ))
            
            # Sort by predicted performance and confidence
            adaptive_content.sort(key=lambda x: (x.user_performance_prediction, x.confidence_score), reverse=True)
            
            logger.info("Generated adaptive content", user_id=user_id, count=len(adaptive_content))
            
            return adaptive_content[:5]  # Return top 5
            
        except Exception as e:
            logger.error("Error getting adaptive content", user_id=user_id, error=str(e))
            return []
    
    async def get_daily_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get daily personalized recommendations"""
        try:
            logger.info("Generating daily recommendations", user_id=user_id)
            
            # Get user progress
            user_progress = await self._get_user_progress(user_id)
            learning_analytics = await self._get_learning_analytics(user_id)
            
            daily_recommendations = {
                "date": datetime.utcnow().date().isoformat(),
                "user_id": user_id,
                "recommendations": [],
                "study_plan": {},
                "motivational_message": "",
                "progress_summary": {}
            }
            
            # Generate recommendations for each module
            modules = ["speaking", "writing", "reading", "listening"]
            for module in modules:
                module_recs = await self.get_recommendations(user_id, module, limit=2)
                daily_recommendations["recommendations"].extend(module_recs)
            
            # Generate study plan
            daily_recommendations["study_plan"] = await self._generate_study_plan(
                user_id, user_progress, learning_analytics
            )
            
            # Generate motivational message
            daily_recommendations["motivational_message"] = self._generate_motivational_message(
                user_progress, learning_analytics
            )
            
            # Generate progress summary
            daily_recommendations["progress_summary"] = self._generate_progress_summary(
                user_progress, learning_analytics
            )
            
            logger.info("Generated daily recommendations", user_id=user_id)
            
            return daily_recommendations
            
        except Exception as e:
            logger.error("Error generating daily recommendations", user_id=user_id, error=str(e))
            return self._get_fallback_daily_recommendations(user_id)
    
    async def _generate_recommendations(self, user_id: str, user_progress: Optional[UserProgress],
                                      learning_analytics: Optional[LearningAnalytics], 
                                      module: Optional[str], limit: int) -> List[Recommendation]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Determine user's weak areas
        weak_areas = []
        if user_progress:
            weak_areas = user_progress.weak_areas
        elif learning_analytics:
            weak_areas = learning_analytics.weak_areas
        
        # If no specific module requested, focus on weak areas
        if not module and weak_areas:
            module = weak_areas[0]
        
        # Get content for the module
        content_list = self.content_database.get(module or "general", [])
        
        # Filter and rank content
        for content in content_list:
            if len(recommendations) >= limit:
                break
                
            # Calculate recommendation score
            score = self._calculate_recommendation_score(
                content, user_progress, learning_analytics, weak_areas
            )
            
            if score > 0.5:  # Only recommend if score is above threshold
                recommendation = Recommendation(
                    user_id=user_id,
                    recommendation_type=self._determine_recommendation_type(content, user_progress),
                    title=content["title"],
                    description=content["description"],
                    content_type=ContentType(content["type"]),
                    difficulty=DifficultyLevel(content["difficulty"]),
                    priority=self._calculate_priority(content, weak_areas),
                    reasoning=self._generate_reasoning(content, weak_areas, user_progress),
                    expected_benefit=content.get("expected_benefit", "Improve overall skills"),
                    estimated_time=content.get("duration", 30),
                    tags=content.get("tags", [])
                )
                recommendations.append(recommendation)
        
        # Sort by priority and score
        recommendations.sort(key=lambda x: (x.priority, self._calculate_recommendation_score(
            {"title": x.title, "difficulty": x.difficulty.value}, user_progress, learning_analytics, weak_areas
        )), reverse=True)
        
        return recommendations[:limit]
    
    def _calculate_recommendation_score(self, content: Dict[str, Any], 
                                      user_progress: Optional[UserProgress],
                                      learning_analytics: Optional[LearningAnalytics],
                                      weak_areas: List[str]) -> float:
        """Calculate recommendation score based on user needs"""
        score = 0.5  # Base score
        
        # Boost score if content addresses weak areas
        if content.get("module") in weak_areas:
            score += 0.3
        
        # Boost score based on user progress
        if user_progress:
            if content.get("difficulty") == user_progress.current_level:
                score += 0.2
            elif content.get("difficulty") == user_progress.target_level:
                score += 0.1
        
        # Boost score based on learning analytics
        if learning_analytics:
            if learning_analytics.accuracy_rate < 70 and content.get("type") == "practice":
                score += 0.2
            if learning_analytics.study_time < 60 and content.get("duration", 0) < 30:
                score += 0.1
        
        return min(score, 1.0)
    
    def _determine_recommendation_type(self, content: Dict[str, Any], 
                                     user_progress: Optional[UserProgress]) -> str:
        """Determine the type of recommendation"""
        content_type = content.get("type", "")
        
        if content_type in ["quiz", "practice_test"]:
            return "practice"
        elif content_type in ["lesson", "video"]:
            return "content"
        elif content_type in ["review", "summary"]:
            return "review"
        else:
            return "challenge"
    
    def _calculate_priority(self, content: Dict[str, Any], weak_areas: List[str]) -> int:
        """Calculate recommendation priority (1 = highest)"""
        if content.get("module") in weak_areas:
            return 1
        elif content.get("type") in ["practice", "quiz"]:
            return 2
        elif content.get("type") in ["lesson", "video"]:
            return 3
        else:
            return 4
    
    def _generate_reasoning(self, content: Dict[str, Any], weak_areas: List[str],
                          user_progress: Optional[UserProgress]) -> str:
        """Generate reasoning for recommendation"""
        reasoning = f"This {content.get('type', 'content')} will help you "
        
        if content.get("module") in weak_areas:
            reasoning += f"improve your {content.get('module')} skills, which is currently your weakest area."
        elif content.get("type") in ["practice", "quiz"]:
            reasoning += "reinforce what you've learned through active practice."
        elif content.get("type") in ["lesson", "video"]:
            reasoning += "learn new concepts and strategies."
        else:
            reasoning += "challenge yourself and test your current abilities."
        
        return reasoning
    
    def _calculate_optimal_difficulty(self, current_difficulty: str, 
                                    performance_data: Dict[str, Any]) -> str:
        """Calculate optimal difficulty based on performance"""
        accuracy = performance_data.get("accuracy", 0.7)
        
        if accuracy > 0.85:
            # User is doing well, increase difficulty
            difficulty_levels = ["beginner", "elementary", "intermediate", "upper_intermediate", "advanced", "expert"]
            current_index = difficulty_levels.index(current_difficulty)
            if current_index < len(difficulty_levels) - 1:
                return difficulty_levels[current_index + 1]
        elif accuracy < 0.6:
            # User is struggling, decrease difficulty
            difficulty_levels = ["beginner", "elementary", "intermediate", "upper_intermediate", "advanced", "expert"]
            current_index = difficulty_levels.index(current_difficulty)
            if current_index > 0:
                return difficulty_levels[current_index - 1]
        
        return current_difficulty
    
    def _predict_performance(self, content: Dict[str, Any], 
                           performance_data: Dict[str, Any]) -> float:
        """Predict user performance on content"""
        base_performance = performance_data.get("accuracy", 0.7)
        
        # Adjust based on content difficulty
        difficulty_boost = {
            "beginner": 0.1,
            "elementary": 0.05,
            "intermediate": 0.0,
            "upper_intermediate": -0.05,
            "advanced": -0.1,
            "expert": -0.15
        }
        
        difficulty = content.get("difficulty", "intermediate")
        boost = difficulty_boost.get(difficulty, 0.0)
        
        return min(max(base_performance + boost, 0.0), 1.0)
    
    def _calculate_confidence(self, content: Dict[str, Any], 
                            performance_data: Dict[str, Any]) -> float:
        """Calculate confidence in recommendation"""
        # Base confidence on performance consistency
        consistency = performance_data.get("consistency", 0.7)
        
        # Adjust based on content type
        type_confidence = {
            "lesson": 0.9,
            "practice": 0.8,
            "quiz": 0.7,
            "video": 0.85
        }
        
        content_type = content.get("type", "practice")
        type_conf = type_confidence.get(content_type, 0.7)
        
        return (consistency + type_conf) / 2
    
    def _check_prerequisites(self, content: Dict[str, Any], user_id: str) -> bool:
        """Check if user meets content prerequisites"""
        # For now, assume prerequisites are met
        # In production, this would check user's completed content
        return True
    
    async def _generate_study_plan(self, user_id: str, user_progress: Optional[UserProgress],
                                 learning_analytics: Optional[LearningAnalytics]) -> Dict[str, Any]:
        """Generate daily study plan"""
        study_plan = {
            "total_time": 60,  # minutes
            "sessions": []
        }
        
        # Determine study time based on analytics
        if learning_analytics:
            if learning_analytics.study_time < 30:
                study_plan["total_time"] = 45
            elif learning_analytics.study_time > 120:
                study_plan["total_time"] = 90
        
        # Create study sessions
        modules = ["speaking", "writing", "reading", "listening"]
        time_per_module = study_plan["total_time"] // len(modules)
        
        for module in modules:
            study_plan["sessions"].append({
                "module": module,
                "duration": time_per_module,
                "activities": ["practice", "review"],
                "focus_areas": user_progress.weak_areas if user_progress else []
            })
        
        return study_plan
    
    def _generate_motivational_message(self, user_progress: Optional[UserProgress],
                                     learning_analytics: Optional[LearningAnalytics]) -> str:
        """Generate motivational message"""
        messages = [
            "Great job staying consistent with your studies! Keep up the excellent work.",
            "Every practice session brings you closer to your target score. You're doing amazing!",
            "Your dedication to learning is inspiring. Remember, progress takes time and patience.",
            "You're making steady progress toward your IELTS goals. Stay focused and keep practicing!",
            "Every challenge you overcome makes you stronger. Keep pushing forward!"
        ]
        
        return random.choice(messages)
    
    def _generate_progress_summary(self, user_progress: Optional[UserProgress],
                                 learning_analytics: Optional[LearningAnalytics]) -> Dict[str, Any]:
        """Generate progress summary"""
        summary = {
            "current_level": "intermediate",
            "target_level": "advanced",
            "progress_percentage": 65.0,
            "streak_days": 0,
            "total_study_time": 0,
            "accuracy_rate": 0.0
        }
        
        if user_progress:
            summary.update({
                "current_level": user_progress.current_level,
                "target_level": user_progress.target_level,
                "progress_percentage": user_progress.progress_percentage
            })
        
        if learning_analytics:
            summary.update({
                "streak_days": learning_analytics.streak_days,
                "total_study_time": learning_analytics.study_time,
                "accuracy_rate": learning_analytics.accuracy_rate
            })
        
        return summary
    
    async def _get_user_progress(self, user_id: str) -> Optional[UserProgress]:
        """Get user progress from external service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.api_service_url}/api/v1/users/{user_id}/progress",
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return UserProgress(**data)
        except Exception as e:
            logger.warning("Could not fetch user progress", user_id=user_id, error=str(e))
        
        return None
    
    async def _get_learning_analytics(self, user_id: str) -> Optional[LearningAnalytics]:
        """Get learning analytics from external service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.analytics_service_url}/api/v1/analytics/{user_id}",
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return LearningAnalytics(**data)
        except Exception as e:
            logger.warning("Could not fetch learning analytics", user_id=user_id, error=str(e))
        
        return None
    
    async def _get_user_performance(self, user_id: str, module: str) -> Dict[str, Any]:
        """Get user performance data for module"""
        # Mock performance data for development
        return {
            "accuracy": 0.75,
            "consistency": 0.8,
            "trend": "improving",
            "weak_areas": ["vocabulary", "grammar"],
            "learning_style": "visual"
        }
    
    async def _load_content_database(self):
        """Load content database"""
        logger.info("Loading content database")
        
        # Mock content database for development
        self.content_database = {
            "speaking": [
                {
                    "id": "speak_001",
                    "title": "Part 1 Speaking Practice",
                    "description": "Practice common Part 1 questions with AI feedback",
                    "type": "practice",
                    "difficulty": "intermediate",
                    "duration": 20,
                    "module": "speaking",
                    "learning_objectives": ["Improve fluency", "Practice common topics"],
                    "expected_benefit": "Build confidence in Part 1 responses",
                    "tags": ["part1", "fluency", "common_topics"]
                },
                {
                    "id": "speak_002",
                    "title": "Pronunciation Masterclass",
                    "description": "Learn advanced pronunciation techniques",
                    "type": "lesson",
                    "difficulty": "advanced",
                    "duration": 45,
                    "module": "speaking",
                    "learning_objectives": ["Master pronunciation", "Improve clarity"],
                    "expected_benefit": "Enhance speaking clarity and confidence",
                    "tags": ["pronunciation", "advanced", "clarity"]
                }
            ],
            "writing": [
                {
                    "id": "write_001",
                    "title": "Task 2 Essay Structure",
                    "description": "Learn the perfect essay structure for Task 2",
                    "type": "lesson",
                    "difficulty": "intermediate",
                    "duration": 30,
                    "module": "writing",
                    "learning_objectives": ["Master essay structure", "Learn paragraph organization"],
                    "expected_benefit": "Write well-structured essays",
                    "tags": ["task2", "structure", "essay"]
                },
                {
                    "id": "write_002",
                    "title": "Academic Vocabulary Builder",
                    "description": "Expand your academic vocabulary for writing",
                    "type": "lesson",
                    "difficulty": "upper_intermediate",
                    "duration": 40,
                    "module": "writing",
                    "learning_objectives": ["Learn academic vocabulary", "Improve lexical resource"],
                    "expected_benefit": "Use sophisticated vocabulary in essays",
                    "tags": ["vocabulary", "academic", "lexical_resource"]
                }
            ],
            "reading": [
                {
                    "id": "read_001",
                    "title": "Skimming and Scanning Techniques",
                    "description": "Master reading strategies for IELTS",
                    "type": "lesson",
                    "difficulty": "intermediate",
                    "duration": 25,
                    "module": "reading",
                    "learning_objectives": ["Learn skimming", "Master scanning", "Improve speed"],
                    "expected_benefit": "Read faster and more efficiently",
                    "tags": ["skimming", "scanning", "speed"]
                }
            ],
            "listening": [
                {
                    "id": "listen_001",
                    "title": "Note-taking Strategies",
                    "description": "Learn effective note-taking for listening tests",
                    "type": "lesson",
                    "difficulty": "intermediate",
                    "duration": 35,
                    "module": "listening",
                    "learning_objectives": ["Improve note-taking", "Enhance listening skills"],
                    "expected_benefit": "Take better notes during listening tests",
                    "tags": ["note-taking", "listening", "strategies"]
                }
            ]
        }
    
    def _is_cache_valid(self, recommendations: List[Recommendation]) -> bool:
        """Check if cached recommendations are still valid"""
        if not recommendations:
            return False
        
        # Check if recommendations are less than 1 hour old
        oldest_rec = min(recommendations, key=lambda x: x.created_date)
        age = datetime.utcnow() - oldest_rec.created_date
        
        return age.total_seconds() < settings.recommendation_cache_ttl
    
    def _get_fallback_recommendations(self, module: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Get fallback recommendations when service is unavailable"""
        fallback_recs = []
        
        for i in range(limit):
            fallback_recs.append({
                "id": f"fallback_{i}",
                "user_id": "unknown",
                "recommendation_type": "practice",
                "title": f"Practice {module or 'IELTS'} Skills",
                "description": "Continue practicing to improve your skills",
                "content_type": "practice",
                "difficulty": "intermediate",
                "priority": 3,
                "reasoning": "Regular practice is essential for improvement",
                "expected_benefit": "Maintain and improve skills",
                "estimated_time": 30,
                "tags": ["practice", "general"],
                "created_date": datetime.utcnow().isoformat(),
                "is_completed": False
            })
        
        return fallback_recs
    
    def _get_fallback_daily_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get fallback daily recommendations"""
        return {
            "date": datetime.utcnow().date().isoformat(),
            "user_id": user_id,
            "recommendations": self._get_fallback_recommendations(None, 4),
            "study_plan": {
                "total_time": 60,
                "sessions": [
                    {"module": "speaking", "duration": 15, "activities": ["practice"]},
                    {"module": "writing", "duration": 15, "activities": ["practice"]},
                    {"module": "reading", "duration": 15, "activities": ["practice"]},
                    {"module": "listening", "duration": 15, "activities": ["practice"]}
                ]
            },
            "motivational_message": "Keep up the great work! Every practice session counts.",
            "progress_summary": {
                "current_level": "intermediate",
                "target_level": "advanced",
                "progress_percentage": 65.0,
                "streak_days": 0,
                "total_study_time": 0,
                "accuracy_rate": 0.0
            }
        }
