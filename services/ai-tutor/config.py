from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from typing import List, Optional
import os

class Settings(BaseSettings):
    """AI Tutor Service Configuration"""
    
    # Service Configuration
    service_name: str = "ai-tutor"
    version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8001, env="PORT")
    
    # CORS and Security
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./ai_tutor.db",
        env="DATABASE_URL"
    )
    
    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # AI Model Configuration
    openai_api_key: str = Field(
        default="your-openai-api-key",
        env="OPENAI_API_KEY"
    )
    anthropic_api_key: str = Field(
        default="your-anthropic-api-key",
        env="ANTHROPIC_API_KEY"
    )
    openrouter_api_key: str = Field(
        default="your-openrouter-api-key",
        env="OPENROUTER_API_KEY"
    )
    
    # Model Settings
    default_model: str = Field(
        default="gpt-4",
        env="DEFAULT_MODEL"
    )
    max_tokens: int = Field(
        default=1000,
        env="MAX_TOKENS"
    )
    temperature: float = Field(
        default=0.7,
        env="TEMPERATURE"
    )
    
    # External Services
    api_service_url: str = Field(
        default="http://localhost:8000",
        env="API_SERVICE_URL"
    )
    scoring_service_url: str = Field(
        default="http://localhost:8001",
        env="SCORING_SERVICE_URL"
    )
    analytics_service_url: str = Field(
        default="http://localhost:8002",
        env="ANALYTICS_SERVICE_URL"
    )
    
    # Learning Path Configuration
    max_path_length: int = Field(
        default=30,
        env="MAX_PATH_LENGTH"
    )
    min_study_time: int = Field(
        default=30,
        env="MIN_STUDY_TIME"
    )
    max_study_time: int = Field(
        default=120,
        env="MAX_STUDY_TIME"
    )
    
    # Recommendation Settings
    recommendation_cache_ttl: int = Field(
        default=3600,
        env="RECOMMENDATION_CACHE_TTL"
    )
    max_recommendations: int = Field(
        default=10,
        env="MAX_RECOMMENDATIONS"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60,
        env="RATE_LIMIT_PER_MINUTE"
    )
    
    # WebSocket Configuration
    websocket_ping_interval: int = Field(
        default=20,
        env="WEBSOCKET_PING_INTERVAL"
    )
    websocket_ping_timeout: int = Field(
        default=20,
        env="WEBSOCKET_PING_TIMEOUT"
    )
    
    # Tutor Personality
    tutor_personality: str = Field(
        default="friendly_expert",
        env="TUTOR_PERSONALITY"
    )
    
    # Learning Analytics
    analytics_enabled: bool = Field(
        default=True,
        env="ANALYTICS_ENABLED"
    )
    
    # Feature Flags
    enable_adaptive_difficulty: bool = Field(
        default=True,
        env="ENABLE_ADAPTIVE_DIFFICULTY"
    )
    enable_personalized_feedback: bool = Field(
        default=True,
        env="ENABLE_PERSONALIZED_FEEDBACK"
    )
    enable_learning_paths: bool = Field(
        default=True,
        env="ENABLE_LEARNING_PATHS"
    )
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

# Create settings instance
settings = Settings()
