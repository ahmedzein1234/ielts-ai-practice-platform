"""Configuration settings for the Scoring Service."""

import os
import sys
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Service configuration
    service_name: str = "scoring-service"
    host: str = Field(default="0.0.0.0", env="SCORING_HOST")
    port: int = Field(default=8004, env="SCORING_PORT")
    debug: bool = Field(default=False, env="SCORING_DEBUG")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # AI/LLM configuration
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")  # openai, anthropic, openrouter
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="anthropic/claude-3-sonnet", env="OPENROUTER_MODEL")
    
    # Scoring configuration
    default_language: str = Field(default="en", env="DEFAULT_LANGUAGE")
    min_confidence: float = Field(default=0.7, env="MIN_CONFIDENCE")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    timeout: int = Field(default=60, env="TIMEOUT")
    
    # IELTS band descriptors
    band_descriptors_path: str = Field(default="./data/band_descriptors", env="BAND_DESCRIPTORS_PATH")
    
    # Feature extraction
    enable_grammar_check: bool = Field(default=True, env="ENABLE_GRAMMAR_CHECK")
    enable_readability_analysis: bool = Field(default=True, env="ENABLE_READABILITY_ANALYSIS")
    enable_vocabulary_analysis: bool = Field(default=True, env="ENABLE_VOCABULARY_ANALYSIS")
    enable_coherence_analysis: bool = Field(default=True, env="ENABLE_COHERENCE_ANALYSIS")
    
    # Caching
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    
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
