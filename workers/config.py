"""Configuration settings for the worker system."""

import os
from typing import List, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Worker system settings."""
    
    # Worker configuration
    worker_name: str = Field(default="ielts-worker", env="WORKER_NAME")
    worker_concurrency: int = Field(default=4, env="WORKER_CONCURRENCY")
    worker_prefetch_multiplier: int = Field(default=1, env="WORKER_PREFETCH_MULTIPLIER")
    worker_max_tasks_per_child: int = Field(default=1000, env="WORKER_MAX_TASKS_PER_CHILD")
    
    # Celery configuration
    celery_broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    celery_task_serializer: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    celery_result_serializer: str = Field(default="json", env="CELERY_RESULT_SERIALIZER")
    celery_accept_content: List[str] = Field(default=["json"], env="CELERY_ACCEPT_CONTENT")
    celery_timezone: str = Field(default="UTC", env="CELERY_TIMEZONE")
    celery_enable_utc: bool = Field(default=True, env="CELERY_ENABLE_UTC")
    celery_task_track_started: bool = Field(default=True, env="CELERY_TASK_TRACK_STARTED")
    celery_task_time_limit: int = Field(default=30 * 60, env="CELERY_TASK_TIME_LIMIT")  # 30 minutes
    celery_task_soft_time_limit: int = Field(default=25 * 60, env="CELERY_TASK_SOFT_TIME_LIMIT")  # 25 minutes
    
    # Redis configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    
    # Database configuration
    database_url: str = Field(default="sqlite:///./ielts_dev.db", env="DATABASE_URL")
    
    # API Gateway configuration
    api_gateway_url: str = Field(default="http://localhost:8000", env="API_GATEWAY_URL")
    api_gateway_timeout: int = Field(default=30, env="API_GATEWAY_TIMEOUT")
    
    # Service URLs
    speech_service_url: str = Field(default="http://localhost:8002", env="SPEECH_SERVICE_URL")
    ocr_service_url: str = Field(default="http://localhost:8003", env="OCR_SERVICE_URL")
    scoring_service_url: str = Field(default="http://localhost:8004", env="SCORING_SERVICE_URL")
    
    # Email configuration
    email_provider: str = Field(default="sendgrid", env="EMAIL_PROVIDER")
    sendgrid_api_key: Optional[str] = Field(default=None, env="SENDGRID_API_KEY")
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    from_email: str = Field(default="noreply@ielts-ai.com", env="FROM_EMAIL")
    from_name: str = Field(default="IELTS AI Platform", env="FROM_NAME")
    
    # AWS configuration
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    s3_bucket: str = Field(default="ielts-ai-platform", env="S3_BUCKET")
    
    # File processing
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    temp_dir: str = Field(default="./temp", env="TEMP_DIR")
    max_file_size: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    allowed_file_types: List[str] = Field(
        default=["jpg", "jpeg", "png", "pdf", "doc", "docx", "mp3", "wav", "m4a"],
        env="ALLOWED_FILE_TYPES"
    )
    
    # Analytics configuration
    analytics_enabled: bool = Field(default=True, env="ANALYTICS_ENABLED")
    analytics_batch_size: int = Field(default=100, env="ANALYTICS_BATCH_SIZE")
    analytics_retention_days: int = Field(default=90, env="ANALYTICS_RETENTION_DAYS")
    
    # Logging configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Monitoring configuration
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    enable_tracing: bool = Field(default=True, env="ENABLE_TRACING")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # Security configuration
    secret_key: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    jwt_secret_key: str = Field(default="dev-jwt-secret-change-in-production", env="JWT_SECRET_KEY")
    
    # Task queues
    scoring_queue: str = Field(default="scoring", env="SCORING_QUEUE")
    file_processing_queue: str = Field(default="file_processing", env="FILE_PROCESSING_QUEUE")
    email_queue: str = Field(default="email", env="EMAIL_QUEUE")
    analytics_queue: str = Field(default="analytics", env="ANALYTICS_QUEUE")
    health_queue: str = Field(default="health", env="HEALTH_QUEUE")
    default_queue: str = Field(default="default", env="DEFAULT_QUEUE")
    
    # Task routing
    task_routes: dict = Field(
        default={
            "workers.tasks.scoring.*": {"queue": "scoring"},
            "workers.tasks.file_processing.*": {"queue": "file_processing"},
            "workers.tasks.email.*": {"queue": "email"},
            "workers.tasks.analytics.*": {"queue": "analytics"},
        },
        env="TASK_ROUTES"
    )
    
    # Rate limiting
    max_scoring_tasks_per_minute: int = Field(default=60, env="MAX_SCORING_TASKS_PER_MINUTE")
    max_file_processing_tasks_per_minute: int = Field(default=30, env="MAX_FILE_PROCESSING_TASKS_PER_MINUTE")
    max_email_tasks_per_minute: int = Field(default=100, env="MAX_EMAIL_TASKS_PER_MINUTE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_celery_config() -> dict:
    """Get Celery configuration dictionary."""
    return {
        "broker_url": settings.celery_broker_url,
        "result_backend": settings.celery_result_backend,
        "task_serializer": settings.celery_task_serializer,
        "result_serializer": settings.celery_result_serializer,
        "accept_content": settings.celery_accept_content,
        "timezone": settings.celery_timezone,
        "enable_utc": settings.celery_enable_utc,
        "task_track_started": settings.celery_task_track_started,
        "task_time_limit": settings.celery_task_time_limit,
        "task_soft_time_limit": settings.celery_task_soft_time_limit,
        "task_routes": settings.task_routes,
        "worker_prefetch_multiplier": settings.worker_prefetch_multiplier,
        "worker_max_tasks_per_child": settings.worker_max_tasks_per_child,
        "broker_connection_retry_on_startup": True,
        "broker_connection_max_retries": 10,
        "result_expires": 3600,  # 1 hour
        "task_ignore_result": False,
        "task_always_eager": False,  # Set to True for testing
        "task_eager_propagates": True,
        "worker_disable_rate_limits": False,
        "worker_send_task_events": True,
        "task_send_sent_event": True,
        "event_queue_expires": 60,
        "worker_state_db": None,
        "worker_log_format": "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
        "worker_task_log_format": "[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
    }
