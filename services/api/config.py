"""Configuration settings for the API Gateway."""

import os
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    debug: bool = Field(default=False, env="DEBUG")
    app_name: str = Field(default="IELTS AI Platform API", env="APP_NAME")
    version: str = Field(default="1.0.0", env="VERSION")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=30, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # JWT Settings
    jwt_secret_key: str = Field(default="your-super-secret-jwt-key-change-this-in-production", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="ALLOWED_ORIGINS"
    )
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    
    # Database
    database_url: str = Field(default="sqlite:///./ielts_dev.db", env="DATABASE_URL")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # AWS
    aws_access_key_id: str = Field(default="dev-access-key", env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="dev-secret-key", env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="eu-west-2", env="AWS_REGION")
    s3_bucket: str = Field(default="ielts-uploads-dev", env="S3_BUCKET")
    
    # AI Services
    openrouter_api_key: str = Field(default="dev-api-key", env="OPENROUTER_API_KEY")
    openai_api_key: str = Field(default="your-openai-api-key", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="your-anthropic-api-key", env="ANTHROPIC_API_KEY")
    deepgram_api_key: str = Field(default="dev-api-key", env="DEEPGRAM_API_KEY")
    
    # Stripe
    stripe_secret_key: str = Field(default="sk_test_dev", env="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str = Field(default="whsec_dev", env="STRIPE_WEBHOOK_SECRET")
    stripe_publishable_key: str = Field(default="pk_test_dev", env="STRIPE_PUBLISHABLE_KEY")
    stripe_price_id: str = Field(default="your-stripe-price-id", env="STRIPE_PRICE_ID")
    
    # Monitoring
    telemetry_enabled: bool = Field(default=True, env="TELEMETRY_ENABLED")
    sentry_dsn: str = Field(default="", env="SENTRY_DSN")
    
    # Email
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: str = Field(default="dev@example.com", env="SMTP_USER")
    smtp_pass: str = Field(default="dev-password", env="SMTP_PASS")
    smtp_password: str = Field(default="your-app-password", env="SMTP_PASSWORD")
    sendgrid_api_key: str = Field(default="your-sendgrid-api-key", env="SENDGRID_API_KEY")
    
    # Analytics
    posthog_api_key: str = Field(default="", env="POSTHOG_API_KEY")
    posthog_host: str = Field(default="https://app.posthog.com", env="POSTHOG_HOST")
    
    # GitHub
    github_personal_access_token: str = Field(default="your-github-personal-access-token", env="GITHUB_PERSONAL_ACCESS_TOKEN")
    github_username: str = Field(default="ahmedzein1234", env="GITHUB_USERNAME")
    github_repo_name: str = Field(default="ielts-ai-platform", env="GITHUB_REPO_NAME")
    
    # Upstash Context7
    upstash_context7_api_key: str = Field(default="your-upstash-context7-api-key", env="UPSTASH_CONTEXT7_API_KEY")
    
    # Vercel
    vercel_token: str = Field(default="your-vercel-token", env="VERCEL_TOKEN")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Service Ports
    api_port: str = Field(default="8000", env="API_PORT")
    speech_port: str = Field(default="8002", env="SPEECH_PORT")
    ocr_port: str = Field(default="8003", env="OCR_PORT")
    scoring_port: str = Field(default="8005", env="SCORING_PORT")
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields to be ignored


# Create settings instance
settings = Settings()
