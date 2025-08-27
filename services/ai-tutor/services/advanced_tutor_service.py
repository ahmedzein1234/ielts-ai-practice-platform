"""
Enhanced AI Tutor Service for Phase 5: Advanced Features.
Implements multi-modal responses, adaptive teaching styles, real-time speech processing,
and intelligent feedback generation.
"""

import structlog
import httpx
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import openai
import anthropic
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from config import settings
from models.advanced_tutor import (
    MultiModalResponse, InteractiveExercise, SpeechAnalysis, ProgressInsight,
    AdaptiveContext, ErrorPattern, AdaptiveFeedback, LearningObjective,
    ResponseType, TeachingStyle, InteractionMode, ExerciseType, DifficultyLevel
)
from models.tutor import TutorMessage, TutorResponse, TutorSession, MessageType
from models.learning_path import LearningAnalytics
from models.tutor import UserProgress

logger = structlog.get_logger()

class AdvancedTutorService:
    """Enhanced AI Tutor Service with advanced capabilities"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.active_sessions: Dict[str, TutorSession] = {}
        self.adaptive_contexts: Dict[str, AdaptiveContext] = {}
        self.error_patterns: Dict[str, List[ErrorPattern]] = {}
        self.teaching_style_models = {}
        
    async def initialize(self):
        """Initialize the advanced tutor service"""
        logger.info("Initializing Advanced AI Tutor Service")
        
        # Initialize AI clients
        if settings.openai_api_key and settings.openai_api_key != "your-openai-api-key":
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
            logger.info("OpenAI client initialized")
        
        if settings.anthropic_api_key and settings.anthropic_api_key != "your-anthropic-api-key":
            self.anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
            logger.info("Anthropic client initialized")
        
        # Initialize teaching style models
        await self._initialize_teaching_models()
        
        # Load adaptive contexts
        await self._load_adaptive_contexts()
        
        logger.info("Advanced AI Tutor Service initialized successfully")
    
    async def _initialize_teaching_models(self):
        """Initialize teaching style models"""
        try:
            # Initialize K-means clustering for teaching style adaptation
            self.teaching_style_models = {
                "engagement_clustering": KMeans(n_clusters=3, random_state=42),
                "learning_pace_clustering": KMeans(n_clusters=3, random_state=42),
                "error_pattern_clustering": KMeans(n_clusters=4, random_state=42)
            }
            logger.info("Teaching style models initialized")
        except Exception as e:
            logger.error("Failed to initialize teaching models", error=str(e))
    
    async def _load_adaptive_contexts(self):
        """Load adaptive contexts for users"""
        try:
            # In production, this would load from database
            # For now, initialize with default contexts
            logger.info("Adaptive contexts loaded")
        except Exception as e:
            logger.error("Failed to load adaptive contexts", error=str(e))
    
    async def advanced_chat(self, user_id: str, message: str, 
                          interaction_mode: InteractionMode = InteractionMode.TEXT,
                          context: Dict[str, Any] = None) -> MultiModalResponse:
        """Enhanced chat with multi-modal responses and adaptive teaching"""
        try:
            logger.info("Processing advanced chat", user_id=user_id, mode=interaction_mode.value)
            
            # Get or create adaptive context
            adaptive_context = await self._get_adaptive_context(user_id)
            
            # Analyze user input and context
            analysis_result = await self._analyze_user_input(message, adaptive_context, interaction_mode)
            
            # Determine optimal teaching style
            teaching_style = await self._determine_teaching_style(adaptive_context, analysis_result)
            
            # Generate multi-modal response
            response = await self._generate_multi_modal_response(
                user_id, message, teaching_style, adaptive_context, analysis_result
            )
            
            # Update adaptive context
            await self._update_adaptive_context(user_id, adaptive_context, analysis_result, response)
            
            # Generate progress insights
            insights = await self._generate_progress_insights(user_id, adaptive_context)
            
            logger.info("Advanced chat response generated", user_id=user_id, 
                       response_type=response.response_type.value)
            
            return response
            
        except Exception as e:
            logger.error("Error in advanced chat", user_id=user_id, error=str(e))
            return self._create_fallback_response(user_id, message)
    
    async def _analyze_user_input(self, message: str, adaptive_context: AdaptiveContext, 
                                interaction_mode: InteractionMode) -> Dict[str, Any]:
        """Analyze user input for patterns and context"""
        try:
            analysis = {
                "sentiment": "neutral",
                "complexity": "medium",
                "engagement_level": 0.7,
                "error_patterns": [],
                "learning_indicators": [],
                "attention_signals": []
            }
            
            # Analyze sentiment and complexity
            if self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Analyze the user's message for sentiment, complexity, and learning indicators."},
                        {"role": "user", "content": f"Analyze: {message}"}
                    ],
                    max_tokens=100
                )
                
                # Parse analysis (simplified for demo)
                analysis["sentiment"] = "positive" if any(word in message.lower() for word in ["good", "great", "excellent"]) else "neutral"
                analysis["complexity"] = "high" if len(message.split()) > 20 else "medium"
            
            # Detect error patterns
            error_patterns = await self._detect_error_patterns(message, adaptive_context)
            analysis["error_patterns"] = error_patterns
            
            # Analyze learning indicators
            learning_indicators = await self._analyze_learning_indicators(message, adaptive_context)
            analysis["learning_indicators"] = learning_indicators
            
            return analysis
            
        except Exception as e:
            logger.error("Error analyzing user input", error=str(e))
            return {"sentiment": "neutral", "complexity": "medium", "engagement_level": 0.5}
    
    async def _determine_teaching_style(self, adaptive_context: AdaptiveContext, 
                                      analysis_result: Dict[str, Any]) -> TeachingStyle:
        """Determine optimal teaching style based on user context and analysis"""
        try:
            # Get current engagement level
            engagement = analysis_result.get("engagement_level", 0.5)
            
            # Get error patterns
            error_count = len(analysis_result.get("error_patterns", []))
            
            # Determine teaching style based on engagement and errors
            if engagement < 0.3:
                return TeachingStyle.SUPPORTIVE
            elif error_count > 3:
                return TeachingStyle.STRUCTURED
            elif engagement > 0.8:
                return TeachingStyle.CHALLENGING
            elif adaptive_context.learning_pace == "fast":
                return TeachingStyle.EXPLORATORY
            else:
                return TeachingStyle.CONVERSATIONAL
                
        except Exception as e:
            logger.error("Error determining teaching style", error=str(e))
            return TeachingStyle.CONVERSATIONAL
    
    async def _generate_multi_modal_response(self, user_id: str, message: str, 
                                           teaching_style: TeachingStyle,
                                           adaptive_context: AdaptiveContext,
                                           analysis_result: Dict[str, Any]) -> MultiModalResponse:
        """Generate multi-modal response based on teaching style and context"""
        try:
            # Generate base text response
            text_response = await self._generate_text_response(message, teaching_style, adaptive_context)
            
            # Determine response type based on context
            response_type = await self._determine_response_type(adaptive_context, analysis_result)
            
            # Generate content based on response type
            content = await self._generate_response_content(
                response_type, text_response, teaching_style, adaptive_context
            )
            
            # Create multi-modal response
            response = MultiModalResponse(
                response_type=response_type,
                content=content,
                confidence=0.85,
                teaching_style=teaching_style,
                adaptive_context=adaptive_context,
                follow_up_actions=await self._generate_follow_up_actions(adaptive_context, analysis_result)
            )
            
            return response
            
        except Exception as e:
            logger.error("Error generating multi-modal response", error=str(e))
            return self._create_fallback_response(user_id, message)
    
    async def _generate_text_response(self, message: str, teaching_style: TeachingStyle,
                                    adaptive_context: AdaptiveContext) -> str:
        """Generate text response using AI models"""
        try:
            if self.openai_client:
                # Create context-aware prompt
                prompt = self._create_teaching_prompt(message, teaching_style, adaptive_context)
                
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=300
                )
                
                return response.choices[0].message.content
            else:
                # Fallback response
                return f"I understand you said: '{message}'. Let me help you with that."
                
        except Exception as e:
            logger.error("Error generating text response", error=str(e))
            return "I'm here to help you with your IELTS preparation. Could you please rephrase your question?"
    
    def _create_teaching_prompt(self, message: str, teaching_style: TeachingStyle,
                               adaptive_context: AdaptiveContext) -> str:
        """Create context-aware teaching prompt"""
        base_prompt = "You are an expert IELTS tutor. "
        
        if teaching_style == TeachingStyle.SUPPORTIVE:
            base_prompt += "Be encouraging and supportive. Focus on building confidence."
        elif teaching_style == TeachingStyle.STRUCTURED:
            base_prompt += "Provide clear, structured explanations with step-by-step guidance."
        elif teaching_style == TeachingStyle.CHALLENGING:
            base_prompt += "Challenge the student with advanced concepts and encourage critical thinking."
        elif teaching_style == TeachingStyle.EXPLORATORY:
            base_prompt += "Encourage exploration and discovery. Ask probing questions."
        elif teaching_style == TeachingStyle.CONVERSATIONAL:
            base_prompt += "Maintain a natural conversation flow while providing educational value."
        elif teaching_style == TeachingStyle.GAMIFIED:
            base_prompt += "Make learning fun and engaging with gamified elements."
        
        base_prompt += f" Current focus area: {adaptive_context.current_focus_area}. "
        base_prompt += "Keep responses concise and actionable."
        
        return base_prompt
    
    async def _determine_response_type(self, adaptive_context: AdaptiveContext,
                                     analysis_result: Dict[str, Any]) -> ResponseType:
        """Determine the type of response to generate"""
        try:
            # Check if user prefers voice interaction
            if adaptive_context.preferred_interaction_mode == InteractionMode.VOICE:
                return ResponseType.AUDIO
            
            # Check if we should provide an interactive exercise
            if len(analysis_result.get("error_patterns", [])) > 2:
                return ResponseType.EXERCISE
            
            # Check if we should provide visual content
            if adaptive_context.attention_span < 5:  # Short attention span
                return ResponseType.VISUAL
            
            # Default to text with potential for interactive elements
            return ResponseType.INTERACTIVE
            
        except Exception as e:
            logger.error("Error determining response type", error=str(e))
            return ResponseType.TEXT
    
    async def _generate_response_content(self, response_type: ResponseType, 
                                       text_response: str, teaching_style: TeachingStyle,
                                       adaptive_context: AdaptiveContext) -> Dict[str, Any]:
        """Generate content based on response type"""
        try:
            content = {
                "text": text_response,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if response_type == ResponseType.AUDIO:
                content["audio"] = {
                    "url": f"/api/audio/generate/{adaptive_context.user_id}",
                    "duration": len(text_response.split()) * 0.5,  # Rough estimate
                    "voice_style": "friendly" if teaching_style == TeachingStyle.SUPPORTIVE else "professional"
                }
            
            elif response_type == ResponseType.VISUAL:
                content["visual"] = {
                    "type": "infographic",
                    "elements": [
                        {"type": "text", "content": text_response[:100] + "..."},
                        {"type": "icon", "name": "lightbulb"},
                        {"type": "progress_bar", "value": adaptive_context.engagement_level}
                    ]
                }
            
            elif response_type == ResponseType.EXERCISE:
                exercise = await self._generate_interactive_exercise(adaptive_context)
                content["exercise"] = exercise.dict()
            
            elif response_type == ResponseType.INTERACTIVE:
                content["interactive"] = {
                    "type": "chat_with_options",
                    "options": await self._generate_response_options(adaptive_context),
                    "quick_actions": ["Practice", "Review", "Ask Question"]
                }
            
            return content
            
        except Exception as e:
            logger.error("Error generating response content", error=str(e))
            return {"text": text_response, "timestamp": datetime.utcnow().isoformat()}
    
    async def _generate_interactive_exercise(self, adaptive_context: AdaptiveContext) -> InteractiveExercise:
        """Generate interactive exercise based on user context"""
        try:
            # Determine exercise type based on focus area
            exercise_type = ExerciseType.MULTIPLE_CHOICE
            if adaptive_context.current_focus_area == "speaking":
                exercise_type = ExerciseType.SPEAKING
            elif adaptive_context.current_focus_area == "writing":
                exercise_type = ExerciseType.WRITING
            elif adaptive_context.current_focus_area == "listening":
                exercise_type = ExerciseType.LISTENING
            elif adaptive_context.current_focus_area == "reading":
                exercise_type = ExerciseType.READING
            
            # Generate exercise content
            exercise_content = await self._generate_exercise_content(exercise_type, adaptive_context)
            
            exercise = InteractiveExercise(
                exercise_type=exercise_type,
                title=f"{adaptive_context.current_focus_area.title()} Practice",
                description=f"Practice your {adaptive_context.current_focus_area} skills",
                content=exercise_content,
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                estimated_duration=5,
                learning_objectives=[f"Improve {adaptive_context.current_focus_area} skills"],
                hints=["Take your time", "Focus on accuracy"],
                solutions=[{"answer": "correct_answer", "explanation": "Detailed explanation"}]
            )
            
            return exercise
            
        except Exception as e:
            logger.error("Error generating interactive exercise", error=str(e))
            return self._create_fallback_exercise()
    
    async def _generate_exercise_content(self, exercise_type: ExerciseType,
                                       adaptive_context: AdaptiveContext) -> Dict[str, Any]:
        """Generate exercise content based on type"""
        try:
            if exercise_type == ExerciseType.MULTIPLE_CHOICE:
                return {
                    "question": "What is the correct form of the verb in this sentence?",
                    "options": ["A) is", "B) are", "C) was", "D) were"],
                    "correct_answer": "A",
                    "explanation": "The subject is singular, so we use 'is'."
                }
            elif exercise_type == ExerciseType.SPEAKING:
                return {
                    "prompt": "Describe your hometown in 2 minutes.",
                    "recording_duration": 120,
                    "evaluation_criteria": ["fluency", "pronunciation", "grammar", "vocabulary"]
                }
            elif exercise_type == ExerciseType.WRITING:
                return {
                    "task": "Write a 150-word essay on the benefits of learning English.",
                    "time_limit": 20,
                    "word_count_target": 150
                }
            else:
                return {
                    "question": "Practice question for your current focus area.",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "A"
                }
                
        except Exception as e:
            logger.error("Error generating exercise content", error=str(e))
            return {"question": "Default practice question", "options": ["A", "B", "C", "D"]}
    
    async def _generate_response_options(self, adaptive_context: AdaptiveContext) -> List[str]:
        """Generate response options for interactive chat"""
        try:
            options = [
                "I need more practice",
                "Can you explain this further?",
                "Show me an example",
                "I'm ready for the next topic"
            ]
            
            # Customize based on user's current focus area
            if adaptive_context.current_focus_area == "speaking":
                options.append("Practice pronunciation")
            elif adaptive_context.current_focus_area == "writing":
                options.append("Review my writing")
            
            return options
            
        except Exception as e:
            logger.error("Error generating response options", error=str(e))
            return ["Continue", "Ask question", "Practice more"]
    
    async def _generate_follow_up_actions(self, adaptive_context: AdaptiveContext,
                                        analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate follow-up actions based on context and analysis"""
        try:
            actions = []
            
            # Add practice action if errors detected
            if len(analysis_result.get("error_patterns", [])) > 0:
                actions.append({
                    "type": "practice",
                    "title": "Practice this concept",
                    "description": "Let's practice to improve your understanding",
                    "priority": "high"
                })
            
            # Add review action if engagement is low
            if analysis_result.get("engagement_level", 0.5) < 0.4:
                actions.append({
                    "type": "review",
                    "title": "Review previous material",
                    "description": "Let's review what we covered earlier",
                    "priority": "medium"
                })
            
            # Add challenge action if user is doing well
            if analysis_result.get("engagement_level", 0.5) > 0.8:
                actions.append({
                    "type": "challenge",
                    "title": "Try a more challenging exercise",
                    "description": "You're doing great! Let's try something harder",
                    "priority": "medium"
                })
            
            return actions
            
        except Exception as e:
            logger.error("Error generating follow-up actions", error=str(e))
            return []
    
    async def _detect_error_patterns(self, message: str, adaptive_context: AdaptiveContext) -> List[ErrorPattern]:
        """Detect error patterns in user input"""
        try:
            patterns = []
            
            # Simple error detection (in production, use more sophisticated NLP)
            common_errors = {
                "grammar": ["I is", "you was", "they has"],
                "vocabulary": ["very good", "very bad", "very nice"],
                "pronunciation": ["tink", "dat", "wut"]
            }
            
            message_lower = message.lower()
            
            for error_type, error_phrases in common_errors.items():
                for phrase in error_phrases:
                    if phrase in message_lower:
                        patterns.append(ErrorPattern(
                            error_type=error_type,
                            frequency=1,
                            context={"phrase": phrase, "message": message},
                            severity="medium",
                            suggested_interventions=[f"Practice {error_type} rules"]
                        ))
            
            return patterns
            
        except Exception as e:
            logger.error("Error detecting error patterns", error=str(e))
            return []
    
    async def _analyze_learning_indicators(self, message: str, adaptive_context: AdaptiveContext) -> List[Dict[str, Any]]:
        """Analyze learning indicators in user input"""
        try:
            indicators = []
            
            # Check for learning-related keywords
            learning_keywords = ["learn", "practice", "understand", "improve", "help"]
            message_lower = message.lower()
            
            for keyword in learning_keywords:
                if keyword in message_lower:
                    indicators.append({
                        "type": "learning_intent",
                        "keyword": keyword,
                        "confidence": 0.8
                    })
            
            # Check for question patterns
            if "?" in message:
                indicators.append({
                    "type": "question",
                    "confidence": 0.9
                })
            
            return indicators
            
        except Exception as e:
            logger.error("Error analyzing learning indicators", error=str(e))
            return []
    
    async def _get_adaptive_context(self, user_id: str) -> AdaptiveContext:
        """Get or create adaptive context for user"""
        try:
            if user_id in self.adaptive_contexts:
                return self.adaptive_contexts[user_id]
            
            # Create new adaptive context
            context = AdaptiveContext(
                user_id=user_id,
                current_teaching_style=TeachingStyle.CONVERSATIONAL,
                preferred_interaction_mode=InteractionMode.TEXT,
                learning_pace="normal",
                attention_span=15,
                current_focus_area="general",
                session_duration=0,
                engagement_level=0.5
            )
            
            self.adaptive_contexts[user_id] = context
            return context
            
        except Exception as e:
            logger.error("Error getting adaptive context", error=str(e))
            return AdaptiveContext(
                user_id=user_id,
                current_teaching_style=TeachingStyle.CONVERSATIONAL,
                preferred_interaction_mode=InteractionMode.TEXT,
                learning_pace="normal",
                attention_span=15,
                current_focus_area="general",
                session_duration=0,
                engagement_level=0.5
            )
    
    async def _update_adaptive_context(self, user_id: str, adaptive_context: AdaptiveContext,
                                     analysis_result: Dict[str, Any], response: MultiModalResponse):
        """Update adaptive context based on interaction"""
        try:
            # Update engagement level
            adaptive_context.engagement_level = analysis_result.get("engagement_level", 0.5)
            
            # Update error patterns
            new_errors = analysis_result.get("error_patterns", [])
            adaptive_context.error_patterns.extend(new_errors)
            
            # Update session duration
            adaptive_context.session_duration += 1
            
            # Update last activity
            adaptive_context.last_updated = datetime.utcnow()
            
            # Update teaching style if needed
            if response.teaching_style != adaptive_context.current_teaching_style:
                adaptive_context.current_teaching_style = response.teaching_style
            
            self.adaptive_contexts[user_id] = adaptive_context
            
        except Exception as e:
            logger.error("Error updating adaptive context", error=str(e))
    
    async def _generate_progress_insights(self, user_id: str, adaptive_context: AdaptiveContext) -> List[ProgressInsight]:
        """Generate progress insights for user"""
        try:
            insights = []
            
            # Generate engagement insight
            if adaptive_context.engagement_level > 0.8:
                insights.append(ProgressInsight(
                    user_id=user_id,
                    insight_type="achievement",
                    title="High Engagement Detected",
                    description="You're showing excellent engagement with the learning material!",
                    data_points=[{"metric": "engagement", "value": adaptive_context.engagement_level}],
                    confidence=0.9,
                    actionable_items=["Continue with current pace", "Try more challenging exercises"],
                    priority="low"
                ))
            
            # Generate improvement insight
            if len(adaptive_context.error_patterns) > 5:
                insights.append(ProgressInsight(
                    user_id=user_id,
                    insight_type="improvement",
                    title="Error Pattern Identified",
                    description="We've noticed some recurring patterns in your responses.",
                    data_points=[{"metric": "error_count", "value": len(adaptive_context.error_patterns)}],
                    confidence=0.8,
                    actionable_items=["Focus on grammar rules", "Practice specific areas"],
                    priority="high"
                ))
            
            return insights
            
        except Exception as e:
            logger.error("Error generating progress insights", error=str(e))
            return []
    
    def _create_fallback_response(self, user_id: str, message: str) -> MultiModalResponse:
        """Create fallback response when errors occur"""
        return MultiModalResponse(
            response_type=ResponseType.TEXT,
            content={
                "text": "I'm here to help you with your IELTS preparation. Could you please rephrase your question?",
                "timestamp": datetime.utcnow().isoformat()
            },
            confidence=0.5,
            teaching_style=TeachingStyle.SUPPORTIVE
        )
    
    def _create_fallback_exercise(self) -> InteractiveExercise:
        """Create fallback exercise when generation fails"""
        return InteractiveExercise(
            exercise_type=ExerciseType.MULTIPLE_CHOICE,
            title="Practice Exercise",
            description="General practice question",
            content={
                "question": "What is the correct form of the verb?",
                "options": ["A) is", "B) are", "C) was", "D) were"],
                "correct_answer": "A"
            },
            difficulty_level=DifficultyLevel.BEGINNER,
            estimated_duration=3,
            learning_objectives=["Practice basic grammar"]
        )
