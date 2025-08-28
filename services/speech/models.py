"""Speech service models."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class STTRequest(BaseModel):
    """Speech-to-Text request model."""
    audio_data: bytes
    sample_rate: int = Field(default=16000, ge=8000, le=48000)
    language: Optional[str] = Field(default="en", max_length=10)
    task: str = Field(default="transcribe", pattern="^(transcribe|translate)$")


class STTResponse(BaseModel):
    """Speech-to-Text response model."""
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    language: str
    processing_time: float
    segments: List[Dict[str, Any]] = Field(default_factory=list)


class PronunciationScore(BaseModel):
    """Pronunciation scoring model."""
    overall_score: float = Field(
        ge=0.0, le=9.0, 
        description="Overall pronunciation score (IELTS band)"
    )
    phoneme_accuracy: float = Field(
        ge=0.0, le=1.0, 
        description="Phoneme recognition accuracy"
    )
    word_stress: float = Field(
        ge=0.0, le=1.0, 
        description="Word stress accuracy"
    )
    sentence_stress: float = Field(
        ge=0.0, le=1.0, 
        description="Sentence stress accuracy"
    )
    intonation: float = Field(
        ge=0.0, le=1.0, 
        description="Intonation pattern accuracy"
    )
    clarity: float = Field(
        ge=0.0, le=1.0, 
        description="Speech clarity score"
    )
    feedback: List[str] = Field(
        default_factory=list, 
        description="Specific pronunciation feedback"
    )


class FluencyMetrics(BaseModel):
    """Fluency analysis metrics."""
    words_per_minute: float = Field(
        ge=0.0, description="Speaking rate in words per minute"
    )
    pause_frequency: float = Field(
        ge=0.0, description="Number of pauses per minute"
    )
    pause_duration: float = Field(
        ge=0.0, description="Average pause duration in seconds"
    )
    filler_words: int = Field(
        ge=0, description="Number of filler words used"
    )
    filler_frequency: float = Field(
        ge=0.0, description="Filler words per minute"
    )
    speech_continuity: float = Field(
        ge=0.0, le=1.0, description="Speech continuity score"
    )
    hesitation_ratio: float = Field(
        ge=0.0, le=1.0, description="Ratio of hesitant speech"
    )
    feedback: List[str] = Field(
        default_factory=list, 
        description="Fluency improvement suggestions"
    )


class AccentAnalysis(BaseModel):
    """Accent detection and analysis."""
    detected_accent: str = Field(description="Detected accent/language variety")
    accent_confidence: float = Field(ge=0.0, le=1.0, description="Confidence in accent detection")
    accent_features: List[str] = Field(default_factory=list, description="Key accent features")
    comprehensibility: float = Field(ge=0.0, le=1.0, description="Accent comprehensibility score")
    feedback: List[str] = Field(default_factory=list, description="Accent-specific feedback")


class EnhancedSTTResponse(BaseModel):
    """Enhanced Speech-to-Text response with analysis."""
    # Basic transcription
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    language: str
    processing_time: float
    segments: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Enhanced analysis
    pronunciation: Optional[PronunciationScore] = None
    fluency: Optional[FluencyMetrics] = None
    accent: Optional[AccentAnalysis] = None
    
    # Overall assessment
    overall_score: float = Field(ge=0.0, le=9.0, description="Overall IELTS speaking score")
    band_level: str = Field(description="IELTS band level (e.g., 'Band 7')")
    detailed_feedback: List[str] = Field(default_factory=list, description="Comprehensive feedback")


class SpeechAnalysisRequest(BaseModel):
    """Request for comprehensive speech analysis."""
    audio_data: bytes
    sample_rate: int = Field(default=16000, ge=8000, le=48000)
    language: Optional[str] = Field(default="en", max_length=10)
    include_pronunciation: bool = Field(default=True, description="Include pronunciation analysis")
    include_fluency: bool = Field(default=True, description="Include fluency analysis")
    include_accent: bool = Field(default=True, description="Include accent analysis")
    target_band: Optional[float] = Field(default=None, ge=0.0, le=9.0, description="Target IELTS band score")


class SpeechAnalysisResponse(BaseModel):
    """Comprehensive speech analysis response."""
    transcription: STTResponse
    analysis: EnhancedSTTResponse
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")
    practice_suggestions: List[str] = Field(default_factory=list, description="Practice exercise suggestions")
