"""Configuration settings for the Speech Service."""

import os
import sys
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Service configuration
    service_name: str = "speech-service"
    host: str = Field(default="0.0.0.0", env="SPEECH_HOST")
    port: int = Field(default=8001, env="SPEECH_PORT")
    debug: bool = Field(default=False, env="SPEECH_DEBUG")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Whisper configuration
    whisper_model: str = Field(default="base", env="WHISPER_MODEL")
    whisper_device: str = Field(default="cpu", env="WHISPER_DEVICE")
    whisper_compute_type: str = Field(default="int8", env="WHISPER_COMPUTE_TYPE")
    whisper_language: Optional[str] = Field(default=None, env="WHISPER_LANGUAGE")
    
    # WebSocket configuration
    max_connections: int = Field(default=100, env="MAX_WEBSOCKET_CONNECTIONS")
    max_message_size: int = Field(default=1024 * 1024, env="MAX_MESSAGE_SIZE")  # 1MB
    ping_interval: int = Field(default=20, env="PING_INTERVAL")
    ping_timeout: int = Field(default=20, env="PING_TIMEOUT")
    
    # Audio processing
    sample_rate: int = Field(default=16000, env="SAMPLE_RATE")
    chunk_duration: float = Field(default=0.5, env="CHUNK_DURATION")  # seconds
    max_audio_duration: float = Field(default=300.0, env="MAX_AUDIO_DURATION")  # 5 minutes
    
    # Redis configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # API Gateway
    api_gateway_url: str = Field(default="http://localhost:8000", env="API_GATEWAY_URL")
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    allowed_origins: list[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    enable_tracing: bool = Field(default=True, env="ENABLE_TRACING")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
