"""Celery application configuration for the worker system."""

import os
import sys
from typing import Any, Dict

from celery import Celery
from celery.signals import setup_logging, worker_init, worker_process_init
import structlog

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from workers.config import settings, get_celery_config
from services.common.logging import setup_logging as setup_structured_logging


def create_celery_app() -> Celery:
    """Create and configure Celery application."""
    
    # Create Celery app
    app = Celery(
        "ielts-workers",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=[
            "workers.tasks.scoring",
            "workers.tasks.file_processing", 
            "workers.tasks.email",
            "workers.tasks.analytics",
            "workers.tasks.health",
        ]
    )
    
    # Configure Celery
    app.conf.update(get_celery_config())
    
    # Set task routing
    app.conf.task_routes = settings.task_routes
    
    # Configure task serialization
    app.conf.task_serializer = settings.celery_task_serializer
    app.conf.result_serializer = settings.celery_result_serializer
    app.conf.accept_content = settings.celery_accept_content
    
    # Configure timezone
    app.conf.timezone = settings.celery_timezone
    app.conf.enable_utc = settings.celery_enable_utc
    
    # Configure task limits
    app.conf.task_time_limit = settings.celery_task_time_limit
    app.conf.task_soft_time_limit = settings.celery_task_soft_time_limit
    
    # Configure worker settings
    app.conf.worker_prefetch_multiplier = settings.worker_prefetch_multiplier
    app.conf.worker_max_tasks_per_child = settings.worker_max_tasks_per_child
    
    # Configure result backend
    app.conf.result_expires = 3600  # 1 hour
    app.conf.task_ignore_result = False
    
    # Configure broker connection
    app.conf.broker_connection_retry_on_startup = True
    app.conf.broker_connection_max_retries = 10
    
    # Configure task tracking
    app.conf.task_track_started = settings.celery_task_track_started
    app.conf.worker_send_task_events = True
    app.conf.task_send_sent_event = True
    
    # Configure event queue
    app.conf.event_queue_expires = 60
    
    # Configure worker state
    app.conf.worker_state_db = None
    
    # Configure logging
    app.conf.worker_log_format = settings.celery_worker_log_format
    app.conf.worker_task_log_format = settings.celery_worker_task_log_format
    
    return app


# Create global Celery app instance
celery_app = create_celery_app()


@setup_logging.connect
def setup_celery_logging(loglevel: str = None, **kwargs: Any) -> None:
    """Setup structured logging for Celery."""
    setup_structured_logging(level=settings.log_level)


@worker_init.connect
def worker_init_handler(**kwargs: Any) -> None:
    """Initialize worker process."""
    logger = structlog.get_logger()
    logger.info(
        "Worker initializing",
        worker_name=settings.worker_name,
        concurrency=settings.worker_concurrency,
        broker_url=settings.celery_broker_url
    )


@worker_process_init.connect
def worker_process_init_handler(**kwargs: Any) -> None:
    """Initialize worker process."""
    logger = structlog.get_logger()
    logger.info(
        "Worker process initialized",
        process_id=os.getpid(),
        worker_name=settings.worker_name
    )


# Task routing configuration
celery_app.conf.task_routes = {
    "workers.tasks.scoring.*": {"queue": settings.scoring_queue},
    "workers.tasks.file_processing.*": {"queue": settings.file_processing_queue},
    "workers.tasks.email.*": {"queue": settings.email_queue},
    "workers.tasks.analytics.*": {"queue": settings.analytics_queue},
    "workers.tasks.health.*": {"queue": settings.health_queue},
}


# Rate limiting configuration
celery_app.conf.task_annotations = {
    "workers.tasks.scoring.*": {
        "rate_limit": f"{settings.max_scoring_tasks_per_minute}/m"
    },
    "workers.tasks.file_processing.*": {
        "rate_limit": f"{settings.max_file_processing_tasks_per_minute}/m"
    },
    "workers.tasks.email.*": {
        "rate_limit": f"{settings.max_email_tasks_per_minute}/m"
    },
}


if __name__ == "__main__":
    celery_app.start()
