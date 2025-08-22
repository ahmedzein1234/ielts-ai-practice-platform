"""FastAPI gateway for IELTS AI platform."""

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from services.common.logging import setup_logging
from services.api.config import settings
from services.api.database import init_db, close_db
from services.api.routers import auth, health, speaking, writing, listening, reading

# Setup logging
setup_logging()
logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="IELTS AI Platform API",
    description="AI-powered IELTS preparation platform API",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts,
)

# Setup OpenTelemetry
if settings.telemetry_enabled:
    FastAPIInstrumentor.instrument_app(app)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(speaking.router, prefix="/api/v1/speaking", tags=["speaking"])
app.include_router(writing.router, prefix="/api/v1/writing", tags=["writing"])
app.include_router(listening.router, prefix="/api/v1/listening", tags=["listening"])
app.include_router(reading.router, prefix="/api/v1/reading", tags=["reading"])

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests for tracing."""
    request_id = request.headers.get("X-Request-ID", str(trace.get_current_span().get_span_context().span_id))
    request.state.request_id = request_id
    
    # Add request ID to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        "Unhandled exception",
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id,
            "message": "An unexpected error occurred" if not settings.debug else str(exc),
        },
    )

@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Starting IELTS AI Platform API", version="1.0.0")
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down IELTS AI Platform API")
    await close_db()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
