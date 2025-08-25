"""Enhanced debugging middleware for FastAPI services."""

import time
import json
import logging
from typing import Callable, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger()

class DebugMiddleware:
    """Enhanced debugging middleware for development."""
    
    def __init__(self, app):
        self.app = app
        self.request_count = 0
        self.error_count = 0
        self.slow_requests = []
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        self.request_count += 1
        
        # Create custom send wrapper to capture response
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Log request details
                path = scope.get("path", "")
                method = scope.get("method", "")
                client = scope.get("client", ("unknown", 0))
                
                logger.debug(
                    "HTTP Request",
                    method=method,
                    path=path,
                    client_ip=client[0],
                    request_id=self.request_count
                )
            
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
            
            # Log response details
            processing_time = time.time() - start_time
            
            if processing_time > 1.0:  # Log slow requests
                self.slow_requests.append({
                    "path": scope.get("path", ""),
                    "method": scope.get("method", ""),
                    "processing_time": processing_time
                })
                logger.warning(
                    "Slow request detected",
                    path=scope.get("path", ""),
                    method=scope.get("method", ""),
                    processing_time=f"{processing_time:.3f}s"
                )
            
            logger.debug(
                "HTTP Response",
                path=scope.get("path", ""),
                method=scope.get("method", ""),
                processing_time=f"{processing_time:.3f}s"
            )
            
        except Exception as e:
            self.error_count += 1
            processing_time = time.time() - start_time
            
            logger.error(
                "Request failed",
                path=scope.get("path", ""),
                method=scope.get("method", ""),
                error=str(e),
                processing_time=f"{processing_time:.3f}s"
            )
            raise


class RequestLoggingMiddleware:
    """Middleware for detailed request/response logging."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Log request headers and body
        headers = dict(scope.get("headers", []))
        
        logger.debug(
            "Request details",
            method=scope.get("method", ""),
            path=scope.get("path", ""),
            headers=headers,
            query_string=scope.get("query_string", b"").decode()
        )
        
        await self.app(scope, receive, send)


def setup_debug_logging():
    """Setup enhanced debug logging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('debug.log')
        ]
    )
    
    # Configure structlog for structured logging
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
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def debug_endpoint_stats():
    """Get debugging statistics."""
    return {
        "total_requests": getattr(DebugMiddleware, 'request_count', 0),
        "error_count": getattr(DebugMiddleware, 'error_count', 0),
        "slow_requests": getattr(DebugMiddleware, 'slow_requests', [])
    }
