"""Pydantic models for Scoring Service."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """IELTS task types."""
    
    WRITING_TASK_1 = "writing_task_1"
    WRITING_TASK_2 = "writing_task_2"
    SPEAKING_PART_1 = "speaking_part_1"
    SPEAKING_PART_2 = "speaking_part_2"
    SPEAKING_PART_3 = "speaking_part_3"


class BandScore(float, Enum):
    """IELTS band scores."""
    
    BAND_1_0 = 1.0
    BAND_1_5 = 1.5
    BAND_2_0 = 2.0
    BAND_2_5 = 2.5
    BAND_3_0 = 3.0
    BAND_3_5 = 3.5
    BAND_4_0 = 4.0
    BAND_4_5 = 4.5
    BAND_5_0 = 5.0
    BAND_5_5 = 5.5
    BAND_6_0 = 6.0
    BAND_6_5 = 6.5
    BAND_7_0 = 7.0
    BAND_7_5 = 7.5
    BAND_8_0 = 8.0
    BAND_8_5 = 8.5
    BAND_9_0 = 9.0


class CriterionType(str, Enum):
    """IELTS assessment criteria."""
    
    TASK_ACHIEVEMENT = "task_achievement"
    COHERENCE_COHESION = "coherence_cohesion"
    LEXICAL_RESOURCE = "lexical_resource"
    GRAMMATICAL_RANGE_ACCURACY = "grammatical_range_accuracy"
    FLUENCY = "fluency"
    PRONUNCIATION = "pronunciation"


class ScoringRequest(BaseModel):
    """Scoring request model."""
    
    task_type: TaskType
    text: str
    prompt: Optional[str] = None
    audio_transcript: Optional[str] = None
    language: str = "en"
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    enable_detailed_feedback: bool = True
    enable_feature_analysis: bool = True


class CriterionScore(BaseModel):
    """Individual criterion score."""
    
    criterion: CriterionType
    band_score: float = Field(ge=1.0, le=9.0)
    confidence: float = Field(ge=0.0, le=1.0)
    feedback: str
    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[str] = []


class FeatureAnalysis(BaseModel):
    """Text feature analysis."""
    
    word_count: int
    sentence_count: int
    avg_sentence_length: float
    readability_score: float
    vocabulary_diversity: float
    grammar_errors: List[Dict[str, Any]]
    coherence_score: float
    task_relevance: float
    complexity_metrics: Dict[str, float]


class ScoringResponse(BaseModel):
    """Scoring response model."""
    
    overall_band_score: float = Field(ge=1.0, le=9.0)
    confidence: float = Field(ge=0.0, le=1.0)
    criteria_scores: List[CriterionScore]
    detailed_feedback: str
    feature_analysis: Optional[FeatureAnalysis] = None
    processing_time: float
    model_used: str
    task_type: TaskType
    language: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BatchScoringRequest(BaseModel):
    """Batch scoring request."""
    
    submissions: List[ScoringRequest]
    enable_parallel: bool = True
    max_concurrent: int = Field(default=5, ge=1, le=10)


class BatchScoringResponse(BaseModel):
    """Batch scoring response."""
    
    results: List[ScoringResponse]
    total_processing_time: float
    successful_count: int
    failed_count: int
    errors: List[Dict[str, Any]]


class HealthStatus(BaseModel):
    """Service health status."""
    
    status: str
    service: str
    version: str
    llm_providers_available: List[str]
    models_loaded: Dict[str, bool]
    uptime: float
    total_scored: int
    average_processing_time: float


class ServiceInfo(BaseModel):
    """Service information."""
    
    service: str
    version: str
    supported_tasks: List[str]
    supported_criteria: List[str]
    llm_providers: List[str]
    features: List[str]


class ScoringStats(BaseModel):
    """Scoring statistics."""
    
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_processing_time: float
    average_band_score: float
    task_type_distribution: Dict[str, int]
    band_score_distribution: Dict[str, int]
    llm_usage: Dict[str, int]


class BandDescriptor(BaseModel):
    """IELTS band descriptor."""
    
    band_score: float
    criterion: CriterionType
    task_type: TaskType
    descriptor: str
    examples: List[str] = []
    keywords: List[str] = []


class PromptTemplate(BaseModel):
    """Prompt template for scoring."""
    
    name: str
    task_type: TaskType
    template: str
    variables: List[str]
    version: str = "1.0"
