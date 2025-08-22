"""Common logging configuration for all services."""

import sys
from typing import Any, Dict
import structlog
from structlog.types import Processor


def setup_logging(level: str = "INFO") -> None:
    """Setup structured logging with JSON output."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    import logging
    
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def add_request_context(logger: structlog.BoundLogger, request_id: str, user_id: str = None) -> structlog.BoundLogger:
    """Add request context to logger."""
    context: Dict[str, Any] = {"request_id": request_id}
    if user_id:
        context["user_id"] = user_id
    return logger.bind(**context)


def log_request(logger: structlog.BoundLogger, method: str, path: str, status_code: int, duration: float, **kwargs) -> None:
    """Log HTTP request details."""
    logger.info(
        "HTTP request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=round(duration * 1000, 2),
        **kwargs
    )


def log_error(logger: structlog.BoundLogger, error: Exception, context: Dict[str, Any] = None) -> None:
    """Log error with context."""
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    
    if context:
        error_data.update(context)
    
    logger.error("Error occurred", **error_data, exc_info=True)


def log_performance(logger: structlog.BoundLogger, operation: str, duration: float, **kwargs) -> None:
    """Log performance metrics."""
    logger.info(
        "Performance metric",
        operation=operation,
        duration_ms=round(duration * 1000, 2),
        **kwargs
    )


def log_business_event(logger: structlog.BoundLogger, event: str, **kwargs) -> None:
    """Log business events."""
    logger.info("Business event", event=event, **kwargs)


# Convenience functions for common logging patterns
def log_user_action(logger: structlog.BoundLogger, user_id: str, action: str, **kwargs) -> None:
    """Log user actions."""
    log_business_event(logger, f"user.{action}", user_id=user_id, **kwargs)


def log_api_call(logger: structlog.BoundLogger, service: str, endpoint: str, **kwargs) -> None:
    """Log API calls to external services."""
    log_business_event(logger, f"api.{service}.{endpoint}", **kwargs)


def log_ai_operation(logger: structlog.BoundLogger, operation: str, model: str, **kwargs) -> None:
    """Log AI/ML operations."""
    log_business_event(logger, f"ai.{operation}", model=model, **kwargs)
