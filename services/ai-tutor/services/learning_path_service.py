import structlog
import httpx
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random

from config import settings
from models.learning_path import LearningPath, LearningStep, ContentType, DifficultyLevel, LearningAnalytics
from models.tutor import UserProgress

logger = structlog.get_logger()

class LearningPathService:
    """Service for generating personalized learning paths"""
    
    def __init__(self):
        self.path_templates: Dict[str, List[Dict[str, Any]]] = {}
        self.content_database: Dict[str, List[Dict[str, Any]]] = {}
        
    async def initialize(self):
        """Initialize the learning path service"""
        logger.info("Initializing Learning Path Service")
        
        # Load path templates and content database
        await self._load_path_templates()
        await self._load_content_database()
        
        logger.info("Learning Path Service initialized successfully")
    
    async def generate_path(self, user_id: str, target_score: float, 
                          timeframe: str = "30") -> Dict[str, Any]:
        """Generate personalized learning path for user"""
        try:
            logger.info("Generating learning path", user_id=user_id, target_score=target_score, timeframe=timeframe)
            
            # Get user progress and analytics
            user_progress = await self._get_user_progress(user_id)
            learning_analytics = await self._get_learning_analytics(user_id)
            
            # Calculate current score
            current_score = self._calculate_current_score(user_progress, learning_analytics)
            
            # Determine path type based on score gap
            score_gap = target_score - current_score
            path_type = self._determine_path_type(score_gap, timeframe)
            
            # Generate learning path
            learning_path = await self._create_learning_path(
                user_id, current_score, target_score, timeframe, path_type, user_progress, learning_analytics
            )
            
            logger.info("Generated learning path", user_id=user_id, path_id=learning_path.id)
            
            return learning_path.dict()
            
        except Exception as e:
            logger.error("Error generating learning path", user_id=user_id, error=str(e))
            return self._get_fallback_learning_path(user_id, target_score, timeframe)
    
    async def update_path_progress(self, user_id: str, path_id: str, 
                                 completed_step_id: str) -> Dict[str, Any]:
        """Update learning path progress when user completes a step"""
        try:
            logger.info("Updating path progress", user_id=user_id, path_id=path_id, step_id=completed_step_id)
            
            # In production, this would update the database
            # For now, return mock updated path
            updated_path = {
                "id": path_id,
                "user_id": user_id,
                "progress_percentage": 75.0,  # Mock progress
                "completed_steps": [completed_step_id],
                "next_steps": ["step_2", "step_3"],
                "estimated_completion": "2024-02-15"
            }
            
            return updated_path
            
        except Exception as e:
            logger.error("Error updating path progress", user_id=user_id, error=str(e))
            return {"error": "Failed to update progress"}
    
    async def get_path_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recommended learning paths for user"""
        try:
            logger.info("Getting path recommendations", user_id=user_id)
            
            # Get user progress
            user_progress = await self._get_user_progress(user_id)
            learning_analytics = await self._get_learning_analytics(user_id)
            
            # Generate different path options
            recommendations = []
            
            # Quick improvement path (2 weeks)
            quick_path = await self.generate_path(user_id, 7.0, "14")
            quick_path["name"] = "Quick Improvement Path"
            quick_path["description"] = "Intensive 2-week program to boost your score"
            recommendations.append(quick_path)
            
            # Steady progress path (1 month)
            steady_path = await self.generate_path(user_id, 7.5, "30")
            steady_path["name"] = "Steady Progress Path"
            steady_path["description"] = "Balanced 1-month program for consistent improvement"
            recommendations.append(steady_path)
            
            # Comprehensive path (3 months)
            comprehensive_path = await self.generate_path(user_id, 8.0, "90")
            comprehensive_path["name"] = "Comprehensive Mastery Path"
            comprehensive_path["description"] = "Thorough 3-month program for significant improvement"
            recommendations.append(comprehensive_path)
            
            logger.info("Generated path recommendations", user_id=user_id, count=len(recommendations))
            
            return recommendations
            
        except Exception as e:
            logger.error("Error getting path recommendations", user_id=user_id, error=str(e))
            return []
    
    async def _create_learning_path(self, user_id: str, current_score: float, 
                                  target_score: float, timeframe: str, path_type: str,
                                  user_progress: Optional[UserProgress],
                                  learning_analytics: Optional[LearningAnalytics]) -> LearningPath:
        """Create personalized learning path"""
        
        # Calculate estimated completion time
        days = int(timeframe)
        target_date = datetime.utcnow() + timedelta(days=days)
        
        # Generate path name
        path_name = f"{path_type.title()} Path to {target_score}"
        
        # Create learning steps
        steps = await self._generate_learning_steps(
            current_score, target_score, days, path_type, user_progress, learning_analytics
        )
        
        # Calculate progress percentage
        progress_percentage = self._calculate_initial_progress(user_progress, learning_analytics)
        
        # Create learning path
        learning_path = LearningPath(
            user_id=user_id,
            path_name=path_name,
            target_score=target_score,
            current_score=current_score,
            target_date=target_date,
            estimated_completion_time=days,
            steps=steps,
            progress_percentage=progress_percentage,
            status="active"
        )
        
        return learning_path
    
    async def _generate_learning_steps(self, current_score: float, target_score: float,
                                     days: int, path_type: str, user_progress: Optional[UserProgress],
                                     learning_analytics: Optional[LearningAnalytics]) -> List[LearningStep]:
        """Generate learning steps for the path"""
        steps = []
        step_number = 1
        
        # Determine weak areas to focus on
        weak_areas = self._identify_weak_areas(user_progress, learning_analytics)
        
        # Calculate steps per day based on path type
        if path_type == "intensive":
            steps_per_day = 3
        elif path_type == "balanced":
            steps_per_day = 2
        else:  # gradual
            steps_per_day = 1
        
        total_steps = days * steps_per_day
        
        # Generate foundation steps (first 30% of path)
        foundation_steps = int(total_steps * 0.3)
        for i in range(foundation_steps):
            step = self._create_foundation_step(step_number, weak_areas)
            steps.append(step)
            step_number += 1
        
        # Generate skill-building steps (next 40% of path)
        skill_steps = int(total_steps * 0.4)
        for i in range(skill_steps):
            step = self._create_skill_step(step_number, weak_areas, current_score)
            steps.append(step)
            step_number += 1
        
        # Generate advanced steps (final 30% of path)
        advanced_steps = total_steps - len(steps)
        for i in range(advanced_steps):
            step = self._create_advanced_step(step_number, weak_areas, target_score)
            steps.append(step)
            step_number += 1
        
        return steps
    
    def _create_foundation_step(self, step_number: int, weak_areas: List[str]) -> LearningStep:
        """Create a foundation learning step"""
        module = weak_areas[0] if weak_areas else "general"
        
        foundation_content = {
            "speaking": {
                "title": "Basic Speaking Fundamentals",
                "description": "Learn essential speaking techniques and build confidence",
                "content_type": ContentType.LESSON,
                "difficulty": DifficultyLevel.ELEMENTARY,
                "duration": 30,
                "learning_objectives": ["Build speaking confidence", "Learn basic techniques"],
                "resources": ["Video lessons", "Practice exercises"]
            },
            "writing": {
                "title": "Writing Foundation Skills",
                "description": "Master basic writing structure and grammar",
                "content_type": ContentType.LESSON,
                "difficulty": DifficultyLevel.ELEMENTARY,
                "duration": 45,
                "learning_objectives": ["Learn essay structure", "Improve grammar"],
                "resources": ["Writing templates", "Grammar exercises"]
            },
            "reading": {
                "title": "Reading Comprehension Basics",
                "description": "Develop fundamental reading skills and strategies",
                "content_type": ContentType.LESSON,
                "difficulty": DifficultyLevel.ELEMENTARY,
                "duration": 40,
                "learning_objectives": ["Improve comprehension", "Learn reading strategies"],
                "resources": ["Reading passages", "Comprehension exercises"]
            },
            "listening": {
                "title": "Listening Fundamentals",
                "description": "Build essential listening skills and note-taking",
                "content_type": ContentType.LESSON,
                "difficulty": DifficultyLevel.ELEMENTARY,
                "duration": 35,
                "learning_objectives": ["Improve listening skills", "Learn note-taking"],
                "resources": ["Audio materials", "Note-taking exercises"]
            }
        }
        
        content = foundation_content.get(module, foundation_content["general"])
        
        return LearningStep(
            step_number=step_number,
            title=content["title"],
            description=content["description"],
            content_type=content["content_type"],
            difficulty=content["difficulty"],
            estimated_duration=content["duration"],
            learning_objectives=content["learning_objectives"],
            resources=content["resources"]
        )
    
    def _create_skill_step(self, step_number: int, weak_areas: List[str], current_score: float) -> LearningStep:
        """Create a skill-building learning step"""
        module = weak_areas[0] if weak_areas else "general"
        
        skill_content = {
            "speaking": {
                "title": "Advanced Speaking Practice",
                "description": "Practice complex speaking tasks with detailed feedback",
                "content_type": ContentType.PRACTICE_TEST,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "duration": 60,
                "learning_objectives": ["Practice complex topics", "Improve fluency"],
                "resources": ["Speaking prompts", "AI feedback"]
            },
            "writing": {
                "title": "Essay Writing Practice",
                "description": "Write and receive feedback on Task 2 essays",
                "content_type": ContentType.PRACTICE_TEST,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "duration": 90,
                "learning_objectives": ["Write complete essays", "Receive detailed feedback"],
                "resources": ["Essay prompts", "Writing assessment"]
            },
            "reading": {
                "title": "Reading Speed and Accuracy",
                "description": "Practice reading with time constraints and accuracy focus",
                "content_type": ContentType.PRACTICE_TEST,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "duration": 60,
                "learning_objectives": ["Improve reading speed", "Enhance accuracy"],
                "resources": ["Timed passages", "Comprehension questions"]
            },
            "listening": {
                "title": "Complex Listening Tasks",
                "description": "Practice listening to complex audio with detailed questions",
                "content_type": ContentType.PRACTICE_TEST,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "duration": 45,
                "learning_objectives": ["Handle complex audio", "Improve note-taking"],
                "resources": ["Complex audio", "Detailed questions"]
            }
        }
        
        content = skill_content.get(module, skill_content["general"])
        
        return LearningStep(
            step_number=step_number,
            title=content["title"],
            description=content["description"],
            content_type=content["content_type"],
            difficulty=content["difficulty"],
            estimated_duration=content["duration"],
            learning_objectives=content["learning_objectives"],
            resources=content["resources"]
        )
    
    def _create_advanced_step(self, step_number: int, weak_areas: List[str], target_score: float) -> LearningStep:
        """Create an advanced learning step"""
        module = weak_areas[0] if weak_areas else "general"
        
        advanced_content = {
            "speaking": {
                "title": "Expert Speaking Mastery",
                "description": "Master advanced speaking techniques for high scores",
                "content_type": ContentType.PRACTICE_TEST,
                "difficulty": DifficultyLevel.ADVANCED,
                "duration": 75,
                "learning_objectives": ["Achieve speaking mastery", "Score 7.5+"],
                "resources": ["Expert feedback", "Advanced techniques"]
            },
            "writing": {
                "title": "Writing Excellence",
                "description": "Perfect your writing skills for top scores",
                "content_type": ContentType.PRACTICE_TEST,
                "difficulty": DifficultyLevel.ADVANCED,
                "duration": 120,
                "learning_objectives": ["Achieve writing excellence", "Score 7.5+"],
                "resources": ["Expert assessment", "Advanced strategies"]
            },
            "reading": {
                "title": "Reading Mastery",
                "description": "Master advanced reading techniques for high scores",
                "content_type": ContentType.PRACTICE_TEST,
                "difficulty": DifficultyLevel.ADVANCED,
                "duration": 60,
                "learning_objectives": ["Achieve reading mastery", "Score 7.5+"],
                "resources": ["Complex passages", "Advanced strategies"]
            },
            "listening": {
                "title": "Listening Excellence",
                "description": "Perfect your listening skills for top scores",
                "content_type": ContentType.PRACTICE_TEST,
                "difficulty": DifficultyLevel.ADVANCED,
                "duration": 60,
                "learning_objectives": ["Achieve listening excellence", "Score 7.5+"],
                "resources": ["Complex audio", "Advanced techniques"]
            }
        }
        
        content = advanced_content.get(module, advanced_content["general"])
        
        return LearningStep(
            step_number=step_number,
            title=content["title"],
            description=content["description"],
            content_type=content["content_type"],
            difficulty=content["difficulty"],
            estimated_duration=content["duration"],
            learning_objectives=content["learning_objectives"],
            resources=content["resources"]
        )
    
    def _identify_weak_areas(self, user_progress: Optional[UserProgress],
                           learning_analytics: Optional[LearningAnalytics]) -> List[str]:
        """Identify user's weak areas"""
        weak_areas = []
        
        if user_progress:
            weak_areas.extend(user_progress.weak_areas)
        
        if learning_analytics:
            weak_areas.extend(learning_analytics.weak_areas)
        
        # Remove duplicates and ensure we have areas to work on
        weak_areas = list(set(weak_areas))
        
        if not weak_areas:
            # Default weak areas if none identified
            weak_areas = ["speaking", "writing"]
        
        return weak_areas
    
    def _calculate_current_score(self, user_progress: Optional[UserProgress],
                               learning_analytics: Optional[LearningAnalytics]) -> float:
        """Calculate current IELTS score"""
        if user_progress and hasattr(user_progress, 'current_score'):
            return user_progress.current_score
        
        # Mock calculation based on analytics
        if learning_analytics:
            # Simple scoring based on accuracy rate
            accuracy = learning_analytics.accuracy_rate / 100
            base_score = 5.0 + (accuracy * 3.0)  # 5.0 to 8.0 range
            return round(base_score, 1)
        
        # Default score
        return 6.0
    
    def _determine_path_type(self, score_gap: float, timeframe: str) -> str:
        """Determine the type of learning path based on score gap and timeframe"""
        days = int(timeframe)
        
        if score_gap > 1.5:
            if days <= 14:
                return "intensive"
            elif days <= 30:
                return "balanced"
            else:
                return "gradual"
        elif score_gap > 0.5:
            if days <= 30:
                return "balanced"
            else:
                return "gradual"
        else:
            return "gradual"
    
    def _calculate_initial_progress(self, user_progress: Optional[UserProgress],
                                  learning_analytics: Optional[LearningAnalytics]) -> float:
        """Calculate initial progress percentage"""
        if user_progress:
            return user_progress.progress_percentage
        
        # Mock progress based on analytics
        if learning_analytics:
            # Progress based on study time and accuracy
            study_progress = min(learning_analytics.study_time / 100, 1.0)  # Normalize to 100 hours
            accuracy_progress = learning_analytics.accuracy_rate / 100
            return (study_progress + accuracy_progress) / 2 * 100
        
        return 0.0
    
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
    
    async def _load_path_templates(self):
        """Load learning path templates"""
        logger.info("Loading path templates")
        
        # Mock path templates for development
        self.path_templates = {
            "intensive": [
                {"type": "foundation", "duration": 7, "steps_per_day": 3},
                {"type": "skill_building", "duration": 5, "steps_per_day": 3},
                {"type": "advanced", "duration": 2, "steps_per_day": 3}
            ],
            "balanced": [
                {"type": "foundation", "duration": 10, "steps_per_day": 2},
                {"type": "skill_building", "duration": 15, "steps_per_day": 2},
                {"type": "advanced", "duration": 5, "steps_per_day": 2}
            ],
            "gradual": [
                {"type": "foundation", "duration": 15, "steps_per_day": 1},
                {"type": "skill_building", "duration": 30, "steps_per_day": 1},
                {"type": "advanced", "duration": 15, "steps_per_day": 1}
            ]
        }
    
    async def _load_content_database(self):
        """Load content database"""
        logger.info("Loading content database")
        
        # Mock content database for development
        self.content_database = {
            "speaking": [
                {"id": "speak_001", "title": "Speaking Fundamentals", "type": "lesson", "difficulty": "elementary"},
                {"id": "speak_002", "title": "Advanced Speaking", "type": "practice", "difficulty": "advanced"}
            ],
            "writing": [
                {"id": "write_001", "title": "Essay Writing", "type": "lesson", "difficulty": "intermediate"},
                {"id": "write_002", "title": "Writing Practice", "type": "practice", "difficulty": "advanced"}
            ],
            "reading": [
                {"id": "read_001", "title": "Reading Strategies", "type": "lesson", "difficulty": "intermediate"},
                {"id": "read_002", "title": "Reading Practice", "type": "practice", "difficulty": "advanced"}
            ],
            "listening": [
                {"id": "listen_001", "title": "Listening Skills", "type": "lesson", "difficulty": "intermediate"},
                {"id": "listen_002", "title": "Listening Practice", "type": "practice", "difficulty": "advanced"}
            ]
        }
    
    def _get_fallback_learning_path(self, user_id: str, target_score: float, timeframe: str) -> Dict[str, Any]:
        """Get fallback learning path when service is unavailable"""
        days = int(timeframe)
        target_date = datetime.utcnow() + timedelta(days=days)
        
        return {
            "id": f"fallback_path_{user_id}",
            "user_id": user_id,
            "path_name": f"Standard Path to {target_score}",
            "target_score": target_score,
            "current_score": 6.0,
            "target_date": target_date.isoformat(),
            "created_date": datetime.utcnow().isoformat(),
            "estimated_completion_time": days,
            "steps": [
                {
                    "step_number": 1,
                    "title": "Foundation Review",
                    "description": "Review basic IELTS concepts and strategies",
                    "content_type": "lesson",
                    "difficulty": "intermediate",
                    "estimated_duration": 45,
                    "learning_objectives": ["Review fundamentals", "Build confidence"],
                    "resources": ["Video lessons", "Practice exercises"],
                    "completion_status": "pending"
                },
                {
                    "step_number": 2,
                    "title": "Practice Test",
                    "description": "Take a full practice test to assess current level",
                    "content_type": "practice_test",
                    "difficulty": "intermediate",
                    "estimated_duration": 180,
                    "learning_objectives": ["Assess current level", "Identify weak areas"],
                    "resources": ["Full practice test", "Detailed feedback"],
                    "completion_status": "pending"
                }
            ],
            "progress_percentage": 0.0,
            "status": "active",
            "adaptive_adjustments": []
        }
