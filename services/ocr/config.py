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
    
    # Database (for compatibility with shared env)
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # JWT (for compatibility with shared env)
    jwt_secret_key: Optional[str] = Field(default=None, env="JWT_SECRET_KEY")
    jwt_algorithm: Optional[str] = Field(default=None, env="JWT_ALGORITHM")
    access_token_expire_minutes: Optional[int] = Field(default=None, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: Optional[int] = Field(default=None, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # AI/LLM (for compatibility with shared env)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    
    # AWS (for compatibility with shared env)
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: Optional[str] = Field(default=None, env="AWS_REGION")
    s3_bucket: Optional[str] = Field(default=None, env="S3_BUCKET")
    
    # Stripe (for compatibility with shared env)
    stripe_secret_key: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    stripe_webhook_secret: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    stripe_price_id: Optional[str] = Field(default=None, env="STRIPE_PRICE_ID")
    
    # Email (for compatibility with shared env)
    sendgrid_api_key: Optional[str] = Field(default=None, env="SENDGRID_API_KEY")
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: Optional[int] = Field(default=None, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # GitHub (for compatibility with shared env)
    github_personal_access_token: Optional[str] = Field(default=None, env="GITHUB_PERSONAL_ACCESS_TOKEN")
    github_username: Optional[str] = Field(default=None, env="GITHUB_USERNAME")
    github_repo_name: Optional[str] = Field(default=None, env="GITHUB_REPO_NAME")
    
    # Upstash Context7 (for compatibility with shared env)
    upstash_context7_api_key: Optional[str] = Field(default=None, env="UPSTASH_CONTEXT7_API_KEY")
    
    # Deepgram (for compatibility with shared env)
    deepgram_api_key: Optional[str] = Field(default=None, env="DEEPGRAM_API_KEY")
    
    # Deployment (for compatibility with shared env)
    railway_token: Optional[str] = Field(default=None, env="RAILWAY_TOKEN")
    cloudflare_api_token: Optional[str] = Field(default=None, env="CLOUDFLARE_API_TOKEN")
    
    # Service ports (for compatibility with shared env)
    api_port: Optional[int] = Field(default=None, env="API_PORT")
    speech_port: Optional[int] = Field(default=None, env="SPEECH_PORT")
    ocr_port: Optional[int] = Field(default=None, env="OCR_PORT")
    scoring_port: Optional[int] = Field(default=None, env="SCORING_PORT")
    
    # Environment (for compatibility with shared env)
    environment: Optional[str] = Field(default=None, env="ENVIRONMENT")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Allow extra fields to be ignored
    }


# Global settings instance
settings = Settings()
