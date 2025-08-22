"""Pydantic models for OCR Service."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field


class OCREngine(str, Enum):
    """Supported OCR engines."""
    
    PADDLEOCR = "paddleocr"
    TROCR = "trocr"


class ImageFormat(str, Enum):
    """Supported image formats."""
    
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    BMP = "bmp"
    TIFF = "tiff"
    WEBP = "webp"


class TextRegion(BaseModel):
    """Detected text region with bounding box and confidence."""
    
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: List[List[float]]  # [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    line_number: Optional[int] = None
    word_count: int = 0


class OCRRequest(BaseModel):
    """OCR processing request."""
    
    image_data: bytes
    engine: OCREngine = OCREngine.PADDLEOCR
    language: str = "en"
    enable_cleaning: bool = True
    enable_spell_check: bool = True
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class OCRResponse(BaseModel):
    """OCR processing response."""
    
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    regions: List[TextRegion]
    word_count: int
    line_count: int
    processing_time: float
    engine_used: OCREngine
    language: str
    image_dimensions: Tuple[int, int]  # (width, height)
    cleaned_text: Optional[str] = None
    spell_checked_text: Optional[str] = None


class ImageUpload(BaseModel):
    """Image upload metadata."""
    
    filename: str
    content_type: str
    size: int
    format: ImageFormat
    dimensions: Tuple[int, int]
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class OCRJob(BaseModel):
    """OCR processing job."""
    
    job_id: str
    user_id: Optional[str] = None
    question_id: Optional[str] = None
    image_upload: ImageUpload
    request_params: OCRRequest
    status: str = "pending"  # pending, processing, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[OCRResponse] = None
    error: Optional[str] = None


class TextCleaningOptions(BaseModel):
    """Text cleaning configuration."""
    
    remove_extra_whitespace: bool = True
    fix_line_breaks: bool = True
    remove_special_chars: bool = False
    normalize_unicode: bool = True
    fix_encoding: bool = True


class SpellCheckOptions(BaseModel):
    """Spell checking configuration."""
    
    language: str = "en"
    max_suggestions: int = 3
    confidence_threshold: float = 0.8
    ignore_proper_nouns: bool = True
    ignore_numbers: bool = True


class HealthStatus(BaseModel):
    """Service health status."""
    
    status: str
    service: str
    version: str
    engines_available: List[str]
    models_loaded: Dict[str, bool]
    uptime: float
    total_processed: int
    average_processing_time: float


class ServiceInfo(BaseModel):
    """Service information."""
    
    service: str
    version: str
    engines: List[str]
    supported_formats: List[str]
    max_file_size: int
    max_image_size: int
    features: List[str]


class ProcessingStats(BaseModel):
    """Processing statistics."""
    
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_processing_time: float
    average_confidence: float
    engines_usage: Dict[str, int]
    languages_processed: Dict[str, int]
