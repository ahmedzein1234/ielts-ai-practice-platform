import structlog
import httpx
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import openai
import anthropic
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from config import settings
from models.tutor import TutorMessage, TutorResponse, TutorSession, MessageType, TutorPersonality
from models.tutor import UserProgress
from models.learning_path import LearningAnalytics

logger = structlog.get_logger()

class TutorService:
    """AI Tutor Service for personalized IELTS tutoring"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.active_sessions: Dict[str, TutorSession] = {}
        self.user_contexts: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self):
        """Initialize the tutor service"""
        logger.info("Initializing AI Tutor Service")
        
        # Initialize OpenAI client
        if settings.openai_api_key and settings.openai_api_key != "your-openai-api-key":
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
            logger.info("OpenAI client initialized")
        
        # Initialize Anthropic client
        if settings.anthropic_api_key and settings.anthropic_api_key != "your-anthropic-api-key":
            self.anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
            logger.info("Anthropic client initialized")
        
        # Initialize user contexts
        await self._load_user_contexts()
        
        logger.info("AI Tutor Service initialized successfully")
    
    async def chat(self, user_id: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle chat interaction with AI tutor"""
        try:
            logger.info("Processing chat message", user_id=user_id, message_length=len(message))
            
            # Get or create user context
            user_context = self.user_contexts.get(user_id, {})
            if context:
                user_context.update(context)
            
            # Get user progress and analytics
            user_progress = await self._get_user_progress(user_id)
            learning_analytics = await self._get_learning_analytics(user_id)
            
            # Build conversation context
            conversation_context = self._build_conversation_context(
                user_id, message, user_context, user_progress, learning_analytics
            )
            
            # Generate AI response
            ai_response = await self._generate_ai_response(conversation_context)
            
            # Create tutor response
            tutor_response = TutorResponse(
                message_id=f"msg_{datetime.utcnow().timestamp()}",
                response=ai_response["response"],
                response_type=ai_response.get("type", MessageType.CHAT),
                confidence=ai_response.get("confidence", 0.8),
                suggestions=ai_response.get("suggestions", []),
                follow_up_questions=ai_response.get("follow_up_questions", []),
                learning_objectives=ai_response.get("learning_objectives", [])
            )
            
            # Update user context
            self._update_user_context(user_id, message, tutor_response)
            
            # Update session
            await self._update_session(user_id, message, tutor_response)
            
            logger.info("Chat response generated", user_id=user_id, response_length=len(tutor_response.response))
            
            return {
                "response": tutor_response.response,
                "type": tutor_response.response_type,
                "confidence": tutor_response.confidence,
                "suggestions": tutor_response.suggestions,
                "follow_up_questions": tutor_response.follow_up_questions,
                "learning_objectives": tutor_response.learning_objectives,
                "session_id": self._get_session_id(user_id)
            }
            
        except Exception as e:
            logger.error("Error in chat", user_id=user_id, error=str(e))
            return {
                "response": "I apologize, but I'm having trouble processing your request right now. Please try again in a moment.",
                "type": MessageType.CHAT,
                "confidence": 0.5,
                "suggestions": [],
                "follow_up_questions": [],
                "learning_objectives": []
            }
    
    async def get_personalized_feedback(self, user_id: str, module: str, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized feedback based on user performance"""
        try:
            logger.info("Generating personalized feedback", user_id=user_id, module=module)
            
            # Get user progress
            user_progress = await self._get_user_progress(user_id)
            
            # Build feedback context
            feedback_context = {
                "user_id": user_id,
                "module": module,
                "performance_data": performance_data,
                "user_progress": user_progress,
                "feedback_type": "performance_analysis"
            }
            
            # Generate AI feedback
            ai_feedback = await self._generate_ai_response(feedback_context)
            
            return {
                "feedback": ai_feedback["response"],
                "strengths": ai_feedback.get("strengths", []),
                "weaknesses": ai_feedback.get("weaknesses", []),
                "recommendations": ai_feedback.get("recommendations", []),
                "next_steps": ai_feedback.get("next_steps", [])
            }
            
        except Exception as e:
            logger.error("Error generating feedback", user_id=user_id, error=str(e))
            return {
                "feedback": "I'm unable to generate personalized feedback at the moment. Please try again later.",
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
                "next_steps": []
            }
    
    async def start_session(self, user_id: str) -> str:
        """Start a new tutoring session"""
        session_id = f"session_{user_id}_{datetime.utcnow().timestamp()}"
        
        session = TutorSession(
            user_id=user_id,
            session_id=session_id,
            start_time=datetime.utcnow()
        )
        
        self.active_sessions[session_id] = session
        logger.info("Started new tutoring session", user_id=user_id, session_id=session_id)
        
        return session_id
    
    async def end_session(self, session_id: str, user_satisfaction: Optional[int] = None) -> Dict[str, Any]:
        """End a tutoring session and generate summary"""
        if session_id not in self.active_sessions:
            raise ValueError("Session not found")
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.utcnow()
        session.duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
        session.user_satisfaction = user_satisfaction
        
        # Generate session summary
        session_summary = await self._generate_session_summary(session)
        session.session_summary = session_summary
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        logger.info("Ended tutoring session", session_id=session_id, duration=session.duration_minutes)
        
        return {
            "session_id": session_id,
            "duration_minutes": session.duration_minutes,
            "messages_count": session.messages_count,
            "topics_covered": session.topics_covered,
            "learning_objectives": session.learning_objectives,
            "session_summary": session_summary,
            "user_satisfaction": user_satisfaction
        }
    
    def _build_conversation_context(self, user_id: str, message: str, user_context: Dict[str, Any], 
                                  user_progress: Optional[UserProgress], 
                                  learning_analytics: Optional[LearningAnalytics]) -> Dict[str, Any]:
        """Build context for AI conversation"""
        context = {
            "user_id": user_id,
            "message": message,
            "user_context": user_context,
            "tutor_personality": settings.tutor_personality,
            "current_time": datetime.utcnow().isoformat(),
            "ielts_focus": True
        }
        
        if user_progress:
            context["user_progress"] = {
                "current_level": user_progress.current_level,
                "target_level": user_progress.target_level,
                "progress_percentage": user_progress.progress_percentage,
                "weak_areas": user_progress.weak_areas,
                "strong_areas": user_progress.strong_areas
            }
        
        if learning_analytics:
            context["learning_analytics"] = {
                "accuracy_rate": learning_analytics.accuracy_rate,
                "study_time": learning_analytics.study_time,
                "streak_days": learning_analytics.streak_days,
                "learning_velocity": learning_analytics.learning_velocity
            }
        
        return context
    
    async def _generate_ai_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI response using available LLMs"""
        try:
            # Try OpenAI first
            if self.openai_client:
                return await self._generate_openai_response(context)
            
            # Fallback to Anthropic
            elif self.anthropic_client:
                return await self._generate_anthropic_response(context)
            
            # Mock response for development
            else:
                return self._generate_mock_response(context)
                
        except Exception as e:
            logger.error("Error generating AI response", error=str(e))
            return self._generate_mock_response(context)
    
    async def _generate_openai_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        system_prompt = self._build_system_prompt(context)
        
        response = await self.openai_client.chat.completions.create(
            model=settings.default_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context["message"]}
            ],
            max_tokens=settings.max_tokens,
            temperature=settings.temperature
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse structured response
        return self._parse_ai_response(ai_response, context)
    
    async def _generate_anthropic_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response using Anthropic"""
        system_prompt = self._build_system_prompt(context)
        
        response = await self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": context["message"]}
            ]
        )
        
        ai_response = response.content[0].text
        
        # Parse structured response
        return self._parse_ai_response(ai_response, context)
    
    def _generate_mock_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock response for development"""
        message = context["message"].lower()
        
        if "hello" in message or "hi" in message:
            return {
                "response": "Hello! I'm your IELTS AI tutor. I'm here to help you improve your English skills and achieve your target score. How can I assist you today?",
                "type": MessageType.CHAT,
                "confidence": 0.9,
                "suggestions": ["Start a practice test", "Review weak areas", "Set learning goals"],
                "follow_up_questions": ["What's your current IELTS score?", "Which module do you find most challenging?"],
                "learning_objectives": ["Establish learning baseline", "Identify focus areas"]
            }
        elif "speaking" in message:
            return {
                "response": "Great! Speaking is often the most challenging module. Let me help you improve your speaking skills. I can provide practice questions, pronunciation tips, and fluency exercises.",
                "type": MessageType.CHAT,
                "confidence": 0.85,
                "suggestions": ["Practice Part 1 questions", "Work on pronunciation", "Record yourself speaking"],
                "follow_up_questions": ["What's your current speaking score?", "Do you struggle with fluency or accuracy?"],
                "learning_objectives": ["Improve speaking fluency", "Enhance pronunciation"]
            }
        elif "writing" in message:
            return {
                "response": "Writing requires practice and understanding of the assessment criteria. I can help you with Task 1 (Academic/General) and Task 2 essay writing, including structure, vocabulary, and grammar.",
                "type": MessageType.CHAT,
                "confidence": 0.85,
                "suggestions": ["Practice Task 2 essays", "Learn academic vocabulary", "Review grammar rules"],
                "follow_up_questions": ["What's your target writing score?", "Do you prefer Academic or General IELTS?"],
                "learning_objectives": ["Master essay structure", "Expand vocabulary"]
            }
        else:
            return {
                "response": "I understand you're working on your IELTS preparation. I'm here to provide personalized guidance, practice materials, and feedback to help you achieve your target score. What specific area would you like to focus on today?",
                "type": MessageType.CHAT,
                "confidence": 0.8,
                "suggestions": ["Take a diagnostic test", "Review your progress", "Set daily goals"],
                "follow_up_questions": ["What's your target IELTS score?", "When is your test date?"],
                "learning_objectives": ["Assess current level", "Create study plan"]
            }
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt for AI tutor"""
        personality = context.get("tutor_personality", "friendly_expert")
        
        base_prompt = f"""You are an expert IELTS tutor with a {personality} personality. Your role is to help students improve their English skills and achieve their target IELTS scores.

Key responsibilities:
1. Provide personalized feedback and guidance
2. Answer questions about IELTS format and strategies
3. Suggest practice activities and resources
4. Motivate and encourage students
5. Adapt your teaching style to the student's level and needs

IELTS Modules:
- Speaking: Fluency, pronunciation, vocabulary, grammar
- Writing: Task 1 (Academic/General) and Task 2 essays
- Reading: Comprehension, skimming, scanning, vocabulary
- Listening: Understanding accents, note-taking, detail recognition

Current student context:
- User ID: {context.get('user_id', 'Unknown')}
- Progress: {context.get('user_progress', {})}
- Learning analytics: {context.get('learning_analytics', {})}

Respond in a helpful, encouraging manner. Provide specific, actionable advice. Ask follow-up questions to better understand the student's needs."""
        
        return base_prompt
    
    def _parse_ai_response(self, ai_response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response and extract structured information"""
        # For now, return a simple parsed response
        # In production, this would use more sophisticated parsing
        return {
            "response": ai_response,
            "type": MessageType.CHAT,
            "confidence": 0.8,
            "suggestions": [],
            "follow_up_questions": [],
            "learning_objectives": []
        }
    
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
    
    def _update_user_context(self, user_id: str, message: str, response: TutorResponse):
        """Update user context with conversation history"""
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {}
        
        context = self.user_contexts[user_id]
        
        # Add conversation to context
        if "conversation_history" not in context:
            context["conversation_history"] = []
        
        context["conversation_history"].append({
            "message": message,
            "response": response.response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last 10 messages
        if len(context["conversation_history"]) > 10:
            context["conversation_history"] = context["conversation_history"][-10:]
    
    async def _update_session(self, user_id: str, message: str, response: TutorResponse):
        """Update active session with new message"""
        session_id = self._get_session_id(user_id)
        
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.messages_count += 1
            
            # Extract topics from message and response
            topics = self._extract_topics(message + " " + response.response)
            session.topics_covered.extend(topics)
            session.topics_covered = list(set(session.topics_covered))  # Remove duplicates
    
    def _get_session_id(self, user_id: str) -> str:
        """Get or create session ID for user"""
        for session_id, session in self.active_sessions.items():
            if session.user_id == user_id:
                return session_id
        
        # Create new session if none exists
        return asyncio.create_task(self.start_session(user_id))
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract IELTS-related topics from text"""
        topics = []
        text_lower = text.lower()
        
        ielts_topics = [
            "speaking", "writing", "reading", "listening",
            "grammar", "vocabulary", "pronunciation", "fluency",
            "essay", "task 1", "task 2", "academic", "general",
            "band score", "ielts", "english", "practice"
        ]
        
        for topic in ielts_topics:
            if topic in text_lower:
                topics.append(topic)
        
        return topics
    
    async def _generate_session_summary(self, session: TutorSession) -> str:
        """Generate summary of tutoring session"""
        summary = f"Tutoring session completed with {session.messages_count} messages exchanged. "
        summary += f"Duration: {session.duration_minutes} minutes. "
        
        if session.topics_covered:
            summary += f"Topics covered: {', '.join(set(session.topics_covered))}. "
        
        if session.learning_objectives:
            summary += f"Learning objectives: {', '.join(session.learning_objectives)}."
        
        return summary
    
    async def _load_user_contexts(self):
        """Load user contexts from storage"""
        # In production, this would load from database
        logger.info("Loading user contexts")
        self.user_contexts = {}
