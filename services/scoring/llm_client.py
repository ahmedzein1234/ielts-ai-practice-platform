"""LLM client for AI scoring with multiple provider support."""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional

import httpx
import structlog
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from config import settings
from models import ScoringRequest, ScoringResponse, CriterionScore, CriterionType

logger = structlog.get_logger()


class BaseLLMClient:
    """Base LLM client interface."""
    
    def __init__(self):
        """Initialize the LLM client."""
        self.provider_name = "base"
        self.is_available = False
    
    async def score_submission(self, request: ScoringRequest) -> ScoringResponse:
        """Score a submission using the LLM."""
        raise NotImplementedError
    
    async def generate_feedback(self, text: str, task_type: str, band_score: float) -> str:
        """Generate detailed feedback for a submission."""
        raise NotImplementedError
    
    def get_info(self) -> Dict[str, Any]:
        """Get client information."""
        return {
            "provider": self.provider_name,
            "available": self.is_available
        }


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for development and testing."""
    
    def __init__(self):
        """Initialize mock LLM client."""
        super().__init__()
        self.provider_name = "mock"
        self.is_available = True
    
    async def score_submission(self, request: ScoringRequest) -> ScoringResponse:
        """Mock scoring implementation."""
        import time
        
        start_time = time.time()
        
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Mock band score (6.5 for demonstration)
        overall_band_score = 6.5
        confidence = 0.85
        
        # Mock criterion scores
        criteria_scores = [
            CriterionScore(
                criterion=CriterionType.TASK_ACHIEVEMENT,
                band_score=6.5,
                confidence=0.8,
                feedback="Good task achievement with clear response to the prompt.",
                strengths=["Addresses the task requirements", "Clear main ideas"],
                weaknesses=["Could develop ideas further", "Some points lack detail"],
                suggestions=["Expand on key points", "Add more specific examples"]
            ),
            CriterionScore(
                criterion=CriterionType.COHERENCE_COHESION,
                band_score=6.0,
                confidence=0.75,
                feedback="Generally coherent with some logical progression.",
                strengths=["Clear paragraph structure", "Good use of linking words"],
                weaknesses=["Some ideas could be better connected", "Occasional repetition"],
                suggestions=["Improve transitions between paragraphs", "Vary linking expressions"]
            ),
            CriterionScore(
                criterion=CriterionType.LEXICAL_RESOURCE,
                band_score=6.5,
                confidence=0.8,
                feedback="Good range of vocabulary with some sophisticated items.",
                strengths=["Adequate vocabulary range", "Some less common words used"],
                weaknesses=["Some word choice could be more precise", "Occasional collocation errors"],
                suggestions=["Use more precise vocabulary", "Improve collocations"]
            ),
            CriterionScore(
                criterion=CriterionType.GRAMMATICAL_RANGE_ACCURACY,
                band_score=6.0,
                confidence=0.7,
                feedback="Good range of structures with some errors.",
                strengths=["Variety of sentence structures", "Mostly accurate grammar"],
                weaknesses=["Some grammatical errors", "Could use more complex structures"],
                suggestions=["Review verb tenses", "Practice complex sentence structures"]
            )
        ]
        
        detailed_feedback = """
        Overall Assessment: Band 6.5
        
        This is a good response that demonstrates competent English language skills. 
        The candidate addresses the task requirements and presents ideas clearly. 
        There is good use of vocabulary and grammar, though there are areas for improvement.
        
        Key Strengths:
        - Clear response to the task
        - Good paragraph organization
        - Adequate vocabulary range
        
        Areas for Improvement:
        - Develop ideas more fully
        - Improve grammatical accuracy
        - Use more sophisticated vocabulary
        
        Recommendations:
        - Practice writing longer, more detailed responses
        - Review common grammatical patterns
        - Expand vocabulary through reading and practice
        """
        
        processing_time = time.time() - start_time
        
        return ScoringResponse(
            overall_band_score=overall_band_score,
            confidence=confidence,
            criteria_scores=criteria_scores,
            detailed_feedback=detailed_feedback.strip(),
            processing_time=processing_time,
            model_used="mock-llm",
            task_type=request.task_type,
            language=request.language
        )
    
    async def generate_feedback(self, text: str, task_type: str, band_score: float) -> str:
        """Generate mock feedback."""
        return f"Mock feedback for {task_type} submission (Band {band_score}): {text[:100]}..."


class OpenAIClient(BaseLLMClient):
    """OpenAI client for scoring."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        super().__init__()
        self.provider_name = "openai"
        
        if settings.openai_api_key:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
            self.is_available = True
        else:
            logger.warning("OpenAI API key not provided")
            self.is_available = False
    
    async def score_submission(self, request: ScoringRequest) -> ScoringResponse:
        """Score submission using OpenAI."""
        if not self.is_available:
            raise RuntimeError("OpenAI client not available")
        
        start_time = time.time()
        
        try:
            # Create scoring prompt
            prompt = self._create_scoring_prompt(request)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert IELTS examiner with deep knowledge of the band descriptors and assessment criteria."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse response
            result = self._parse_scoring_response(response.choices[0].message.content, request)
            
            processing_time = time.time() - start_time
            
            return ScoringResponse(
                overall_band_score=result["overall_band_score"],
                confidence=result["confidence"],
                criteria_scores=result["criteria_scores"],
                detailed_feedback=result["detailed_feedback"],
                processing_time=processing_time,
                model_used=settings.openai_model,
                task_type=request.task_type,
                language=request.language
            )
            
        except Exception as e:
            logger.error("OpenAI scoring failed", error=str(e))
            raise RuntimeError(f"OpenAI scoring failed: {e}")
    
    def _create_scoring_prompt(self, request: ScoringRequest) -> str:
        """Create scoring prompt for OpenAI."""
        task_info = {
            "writing_task_1": "Academic Writing Task 1 (describe a chart/graph/process)",
            "writing_task_2": "Academic Writing Task 2 (essay)",
            "speaking_part_1": "Speaking Part 1 (personal questions)",
            "speaking_part_2": "Speaking Part 2 (individual long turn)",
            "speaking_part_3": "Speaking Part 3 (discussion)"
        }
        
        prompt = f"""
        Please assess this IELTS {task_info.get(request.task_type.value, request.task_type.value)} submission.
        
        Task Type: {request.task_type.value}
        Language: {request.language}
        
        Submission Text:
        {request.text}
        
        {f'Task Prompt: {request.prompt}' if request.prompt else ''}
        
        Please provide a detailed assessment following the IELTS band descriptors:
        
        1. Overall Band Score (1.0-9.0)
        2. Individual criterion scores:
           - Task Achievement (Writing) / Fluency (Speaking)
           - Coherence and Cohesion
           - Lexical Resource
           - Grammatical Range and Accuracy
           - Pronunciation (Speaking only)
        
        3. Detailed feedback with strengths, weaknesses, and suggestions
        
        Respond in JSON format:
        {{
            "overall_band_score": 6.5,
            "confidence": 0.85,
            "criteria_scores": [
                {{
                    "criterion": "task_achievement",
                    "band_score": 6.5,
                    "confidence": 0.8,
                    "feedback": "...",
                    "strengths": ["..."],
                    "weaknesses": ["..."],
                    "suggestions": ["..."]
                }}
            ],
            "detailed_feedback": "..."
        }}
        """
        
        return prompt
    
    def _parse_scoring_response(self, response: str, request: ScoringRequest) -> Dict[str, Any]:
        """Parse OpenAI response."""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            
            data = json.loads(json_str)
            
            # Convert criteria scores
            criteria_scores = []
            for criterion_data in data.get("criteria_scores", []):
                criteria_scores.append(CriterionScore(**criterion_data))
            
            return {
                "overall_band_score": data.get("overall_band_score", 6.0),
                "confidence": data.get("confidence", 0.8),
                "criteria_scores": criteria_scores,
                "detailed_feedback": data.get("detailed_feedback", "")
            }
            
        except Exception as e:
            logger.error("Failed to parse OpenAI response", error=str(e))
            # Return fallback response
            return {
                "overall_band_score": 6.0,
                "confidence": 0.5,
                "criteria_scores": [],
                "detailed_feedback": "Error parsing AI response"
            }
    
    async def generate_feedback(self, text: str, task_type: str, band_score: float) -> str:
        """Generate feedback using OpenAI."""
        if not self.is_available:
            return "OpenAI client not available"
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an IELTS examiner providing detailed feedback."},
                    {"role": "user", "content": f"Provide detailed feedback for this {task_type} submission (Band {band_score}): {text}"}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error("OpenAI feedback generation failed", error=str(e))
            return f"Error generating feedback: {e}"


class AnthropicClient(BaseLLMClient):
    """Anthropic client for scoring."""
    
    def __init__(self):
        """Initialize Anthropic client."""
        super().__init__()
        self.provider_name = "anthropic"
        
        if settings.anthropic_api_key:
            self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
            self.is_available = True
        else:
            logger.warning("Anthropic API key not provided")
            self.is_available = False
    
    async def score_submission(self, request: ScoringRequest) -> ScoringResponse:
        """Score submission using Anthropic."""
        if not self.is_available:
            raise RuntimeError("Anthropic client not available")
        
        start_time = time.time()
        
        try:
            # Create scoring prompt
            prompt = self._create_scoring_prompt(request)
            
            # Call Anthropic API
            response = await self.client.messages.create(
                model=settings.anthropic_model,
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse response
            result = self._parse_scoring_response(response.content[0].text, request)
            
            processing_time = time.time() - start_time
            
            return ScoringResponse(
                overall_band_score=result["overall_band_score"],
                confidence=result["confidence"],
                criteria_scores=result["criteria_scores"],
                detailed_feedback=result["detailed_feedback"],
                processing_time=processing_time,
                model_used=settings.anthropic_model,
                task_type=request.task_type,
                language=request.language
            )
            
        except Exception as e:
            logger.error("Anthropic scoring failed", error=str(e))
            raise RuntimeError(f"Anthropic scoring failed: {e}")
    
    def _create_scoring_prompt(self, request: ScoringRequest) -> str:
        """Create scoring prompt for Anthropic."""
        # Similar to OpenAI prompt but adapted for Claude
        return f"""
        You are an expert IELTS examiner. Please assess this {request.task_type.value} submission:
        
        Text: {request.text}
        
        Provide assessment in JSON format with overall band score, individual criteria scores, and detailed feedback.
        """
    
    def _parse_scoring_response(self, response: str, request: ScoringRequest) -> Dict[str, Any]:
        """Parse Anthropic response."""
        # Similar to OpenAI parsing
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            
            data = json.loads(json_str)
            
            criteria_scores = []
            for criterion_data in data.get("criteria_scores", []):
                criteria_scores.append(CriterionScore(**criterion_data))
            
            return {
                "overall_band_score": data.get("overall_band_score", 6.0),
                "confidence": data.get("confidence", 0.8),
                "criteria_scores": criteria_scores,
                "detailed_feedback": data.get("detailed_feedback", "")
            }
            
        except Exception as e:
            logger.error("Failed to parse Anthropic response", error=str(e))
            return {
                "overall_band_score": 6.0,
                "confidence": 0.5,
                "criteria_scores": [],
                "detailed_feedback": "Error parsing AI response"
            }
    
    async def generate_feedback(self, text: str, task_type: str, band_score: float) -> str:
        """Generate feedback using Anthropic."""
        if not self.is_available:
            return "Anthropic client not available"
        
        try:
            response = await self.client.messages.create(
                model=settings.anthropic_model,
                max_tokens=500,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": f"Provide detailed feedback for this {task_type} submission (Band {band_score}): {text}"}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error("Anthropic feedback generation failed", error=str(e))
            return f"Error generating feedback: {e}"


class LLMClientManager:
    """Manages multiple LLM clients."""
    
    def __init__(self):
        """Initialize LLM client manager."""
        self.clients: Dict[str, BaseLLMClient] = {}
        self._load_clients()
    
    def _load_clients(self) -> None:
        """Load available LLM clients."""
        # Load OpenAI client
        try:
            openai_client = OpenAIClient()
            if openai_client.is_available:
                self.clients["openai"] = openai_client
        except Exception as e:
            logger.warning(f"Failed to load OpenAI client: {e}")
        
        # Load Anthropic client
        try:
            anthropic_client = AnthropicClient()
            if anthropic_client.is_available:
                self.clients["anthropic"] = anthropic_client
        except Exception as e:
            logger.warning(f"Failed to load Anthropic client: {e}")
        
        # Always load mock client as fallback
        mock_client = MockLLMClient()
        self.clients["mock"] = mock_client
        
        logger.info(f"Loaded LLM clients: {list(self.clients.keys())}")
    
    def get_client(self, provider: str = None) -> BaseLLMClient:
        """Get LLM client by provider."""
        if provider and provider in self.clients:
            return self.clients[provider]
        
        # Return first available client (prefer real over mock)
        for name, client in self.clients.items():
            if name != "mock" and client.is_available:
                return client
        
        # Fallback to mock
        return self.clients["mock"]
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return [name for name, client in self.clients.items() if client.is_available]
    
    def get_clients_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all clients."""
        return {name: client.get_info() for name, client in self.clients.items()}


# Global LLM client manager
llm_manager = LLMClientManager()
