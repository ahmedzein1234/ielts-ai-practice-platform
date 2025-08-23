"""Main scoring service that orchestrates LLM scoring and feature extraction."""

import time
from typing import Dict, List, Optional

import structlog
import redis.asyncio as redis

from config import settings
from models import (
    ScoringRequest, ScoringResponse, CriterionScore, FeatureAnalysis,
    TaskType, CriterionType, BatchScoringRequest, BatchScoringResponse
)
from llm_client import llm_manager
from feature_extractor import feature_extractor

logger = structlog.get_logger()


class ScoringService:
    """Main scoring service for IELTS submissions."""
    
    def __init__(self):
        """Initialize scoring service."""
        self.redis_client: Optional[redis.Redis] = None
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_processing_time": 0.0,
            "total_processing_time": 0.0
        }
        self._init_redis()
    
    def _init_redis(self) -> None:
        """Initialize Redis connection for caching."""
        if settings.enable_caching and settings.redis_url:
            try:
                self.redis_client = redis.from_url(settings.redis_url)
                logger.info("Redis client initialized for caching")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis: {e}")
                self.redis_client = None
    
    async def score_submission(self, request: ScoringRequest) -> ScoringResponse:
        """Score a single submission."""
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                logger.info("Returning cached scoring result", cache_key=cache_key)
                return cached_result
            
            # Extract features
            features = None
            if request.enable_feature_analysis:
                features = feature_extractor.extract_features(request.text, request.task_type)
                logger.info("Features extracted", word_count=features.word_count)
            
            # Get LLM client
            llm_client = llm_manager.get_client()
            
            # Score with LLM
            scoring_result = await llm_client.score_submission(request)
            
            # Add feature analysis if enabled
            if features:
                scoring_result.feature_analysis = features
            
            # Cache result
            await self._cache_result(cache_key, scoring_result)
            
            # Update stats
            processing_time = time.time() - start_time
            self.stats["successful_requests"] += 1
            self.stats["total_processing_time"] += processing_time
            self.stats["average_processing_time"] = (
                self.stats["total_processing_time"] / self.stats["successful_requests"]
            )
            
            logger.info(
                "Scoring completed",
                task_type=request.task_type.value,
                band_score=scoring_result.overall_band_score,
                processing_time=processing_time,
                model_used=scoring_result.model_used
            )
            
            return scoring_result
            
        except Exception as e:
            self.stats["failed_requests"] += 1
            logger.error("Scoring failed", error=str(e), task_type=request.task_type.value)
            raise
    
    async def score_batch(self, request: BatchScoringRequest) -> BatchScoringResponse:
        """Score multiple submissions in batch."""
        start_time = time.time()
        
        results = []
        successful = 0
        failed = 0
        
        for submission in request.submissions:
            try:
                result = await self.score_submission(submission)
                results.append(result)
                successful += 1
            except Exception as e:
                logger.error("Batch scoring failed for submission", error=str(e))
                failed += 1
                # Add error result
                error_result = ScoringResponse(
                    overall_band_score=0.0,
                    confidence=0.0,
                    criteria_scores=[],
                    detailed_feedback=f"Scoring failed: {str(e)}",
                    processing_time=0.0,
                    model_used="error",
                    task_type=submission.task_type,
                    language=submission.language
                )
                results.append(error_result)
        
        processing_time = time.time() - start_time
        
        logger.info(
            "Batch scoring completed",
            total=len(request.submissions),
            successful=successful,
            failed=failed,
            processing_time=processing_time
        )
        
        return BatchScoringResponse(
            results=results,
            total_submissions=len(request.submissions),
            successful=successful,
            failed=failed,
            processing_time=processing_time
        )
    
    def _generate_cache_key(self, request: ScoringRequest) -> str:
        """Generate cache key for request."""
        import hashlib
        
        # Create a hash of the request content
        content = f"{request.text}:{request.task_type.value}:{request.language}"
        if request.prompt:
            content += f":{request.prompt}"
        
        return f"scoring:{hashlib.md5(content.encode()).hexdigest()}"
    
    async def _get_cached_result(self, cache_key: str) -> Optional[ScoringResponse]:
        """Get cached scoring result."""
        if not self.redis_client or not settings.enable_caching:
            return None
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                import json
                data = json.loads(cached_data)
                
                # Reconstruct ScoringResponse
                criteria_scores = []
                for criterion_data in data.get("criteria_scores", []):
                    criteria_scores.append(CriterionScore(**criterion_data))
                
                feature_analysis = None
                if "feature_analysis" in data:
                    feature_analysis = FeatureAnalysis(**data["feature_analysis"])
                
                return ScoringResponse(
                    overall_band_score=data["overall_band_score"],
                    confidence=data["confidence"],
                    criteria_scores=criteria_scores,
                    detailed_feedback=data["detailed_feedback"],
                    processing_time=data["processing_time"],
                    model_used=data["model_used"],
                    task_type=TaskType(data["task_type"]),
                    language=data["language"],
                    feature_analysis=feature_analysis
                )
        except Exception as e:
            logger.warning(f"Failed to get cached result: {e}")
        
        return None
    
    async def _cache_result(self, cache_key: str, result: ScoringResponse) -> None:
        """Cache scoring result."""
        if not self.redis_client or not settings.enable_caching:
            return
        
        try:
            import json
            
            # Convert to dict for caching
            data = {
                "overall_band_score": result.overall_band_score,
                "confidence": result.confidence,
                "criteria_scores": [score.dict() for score in result.criteria_scores],
                "detailed_feedback": result.detailed_feedback,
                "processing_time": result.processing_time,
                "model_used": result.model_used,
                "task_type": result.task_type.value,
                "language": result.language,
                "timestamp": result.timestamp.isoformat()
            }
            
            if result.feature_analysis:
                data["feature_analysis"] = result.feature_analysis.dict()
            
            await self.redis_client.setex(
                cache_key,
                settings.cache_ttl,
                json.dumps(data)
            )
            
            logger.debug("Result cached", cache_key=cache_key)
            
        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")
    
    def get_stats(self) -> Dict:
        """Get service statistics."""
        return {
            "total_requests": self.stats["total_requests"],
            "successful_requests": self.stats["successful_requests"],
            "failed_requests": self.stats["failed_requests"],
            "average_processing_time": round(self.stats["average_processing_time"], 3),
            "available_llm_providers": llm_manager.get_available_providers(),
            "llm_clients_info": llm_manager.get_clients_info()
        }
    
    async def health_check(self) -> Dict:
        """Perform health check."""
        health_status = {
            "status": "healthy",
            "service": "scoring-service",
            "version": "0.1.0",
            "llm_providers_available": llm_manager.get_available_providers(),
            "models_loaded": {},
            "uptime": time.time() - getattr(self, '_start_time', time.time()),
            "total_scored": self.stats["successful_requests"],
            "average_processing_time": round(self.stats["average_processing_time"], 3)
        }
        
        # Check LLM clients
        for name, client in llm_manager.clients.items():
            health_status["models_loaded"][name] = client.is_available
        
        # Check Redis
        if self.redis_client:
            try:
                await self.redis_client.ping()
                health_status["redis_status"] = "connected"
            except Exception as e:
                health_status["redis_status"] = f"error: {e}"
                health_status["status"] = "degraded"
        else:
            health_status["redis_status"] = "disabled"
        
        return health_status
    
    def get_service_info(self) -> Dict:
        """Get service information."""
        return {
            "service": "scoring-service",
            "version": "0.1.0",
            "supported_tasks": [task.value for task in TaskType],
            "supported_criteria": [criterion.value for criterion in CriterionType],
            "llm_providers": llm_manager.get_available_providers(),
            "features": [
                "AI-powered scoring",
                "Feature extraction",
                "Caching support",
                "Batch processing",
                "Multiple LLM providers"
            ]
        }


# Global scoring service instance
scoring_service = ScoringService()
