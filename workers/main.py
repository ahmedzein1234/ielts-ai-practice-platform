"""Main worker application entry point."""

import sys
import os
from contextlib import asynccontextmanager

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from services.common.logging import setup_logging
from workers.config import settings
from workers.celery_app import celery_app

# Import all task modules to register them
from workers.tasks import scoring, file_processing, email, analytics

logger = None


def main():
    """Main entry point for the worker application."""
    global logger
    
    # Setup logging
    setup_logging(level=settings.log_level)
    logger = structlog.get_logger()
    
    logger.info(
        "Starting IELTS Worker System",
        version="0.1.0",
        broker_url=settings.celery_broker_url,
        result_backend=settings.celery_result_backend
    )
    
    # Start Celery worker
    argv = [
        'worker',
        '--loglevel=info',
        '--concurrency=4',
        '--queues=scoring,file_processing,email,analytics',
        '--hostname=ielts-worker@%h'
    ]
    
    celery_app.worker_main(argv)


if __name__ == "__main__":
    main()
