"""Configuration settings for the OCR Service."""

import os
import sys
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Service configuration
    service_name: str = "ocr-service"
    host: str = Field(default="0.0.0.0", env="OCR_HOST")
    port: int = Field(default=8003, env="OCR_PORT")
    debug: bool = Field(default=False, env="OCR_DEBUG")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # OCR configuration
    ocr_engine: str = Field(default="paddleocr", env="OCR_ENGINE")  # paddleocr, trocr
    paddle_lang: str = Field(default="en", env="PADDLE_LANG")
    paddle_use_gpu: bool = Field(default=False, env="PADDLE_USE_GPU")
    paddle_use_angle_cls: bool = Field(default=True, env="PADDLE_USE_ANGLE_CLS")
    paddle_use_space_char: bool = Field(default=True, env="PADDLE_USE_SPACE_CHAR")
    
    # TrOCR configuration
    trocr_model: str = Field(default="microsoft/trocr-base-handwritten", env="TROCR_MODEL")
    trocr_device: str = Field(default="cpu", env="TROCR_DEVICE")
    
    # Image processing
    max_image_size: int = Field(default=4096, env="MAX_IMAGE_SIZE")  # pixels
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    supported_formats: List[str] = Field(
        default=["jpg", "jpeg", "png", "bmp", "tiff", "webp"], 
        env="SUPPORTED_FORMATS"
    )
    
    # Text processing
    min_confidence: float = Field(default=0.5, env="MIN_CONFIDENCE")
    enable_text_cleaning: bool = Field(default=True, env="ENABLE_TEXT_CLEANING")
    enable_spell_check: bool = Field(default=True, env="ENABLE_SPELL_CHECK")
    
    # Storage
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    temp_dir: str = Field(default="./temp", env="TEMP_DIR")
    
    # Redis configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # API Gateway
    api_gateway_url: str = Field(default="http://localhost:8000", env="API_GATEWAY_URL")
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    allowed_origins: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    enable_tracing: bool = Field(default=True, env="ENABLE_TRACING")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
