"""Main FastAPI application for OCR Service."""

import os
import sys
import uuid
from contextlib import asynccontextmanager
from typing import List

import structlog
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

try:
    from services.common.logging import setup_logging
except ImportError:
    # Fallback for direct execution
    import structlog
    def setup_logging(level="INFO", service_name="ocr"):
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

from .config import settings
from .engines import ocr_manager
from .image_processor import ImageProcessor
from .models import (
    HealthStatus, OCREngine, OCRRequest, ProcessingStats, ServiceInfo
)
from .text_processor import TextProcessor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging(level=settings.log_level)
    
    logger = structlog.get_logger()
    logger.info(
        "OCR service starting",
        host=settings.host,
        port=settings.port,
        engines=ocr_manager.get_available_engines()
    )
    
    # Create directories
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.temp_dir, exist_ok=True)
    
    # Initialize engines
    try:
        engines_info = ocr_manager.get_engines_info()
        logger.info("OCR engines initialized", engines=engines_info)
    except Exception as e:
        logger.error("Failed to initialize OCR engines", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("OCR service shutting down")


# Create FastAPI app
app = FastAPI(
    title="IELTS OCR Service",
    description="OCR service with PaddleOCR and TrOCR for writing analysis",
    version="0.1.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Add OpenTelemetry instrumentation
if settings.enable_tracing:
    FastAPIInstrumentor.instrument_app(app)

# Statistics tracking
stats = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "processing_times": [],
    "engines_usage": {},
    "languages_processed": {}
}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    available_engines = ocr_manager.get_available_engines()
    engines_info = ocr_manager.get_engines_info()
    
    return HealthStatus(
        status="healthy" if available_engines else "degraded",
        service="ocr",
        version="0.1.0",
        engines_available=available_engines,
        models_loaded={name: info["loaded"] for name, info in engines_info.items()},
        uptime=0.0,  # TODO: Track actual uptime
        total_processed=stats["total_requests"],
        average_processing_time=sum(stats["processing_times"]) / len(stats["processing_times"]) if stats["processing_times"] else 0.0
    )


@app.get("/health/ready")
async def readiness_check():
    """Readiness check endpoint."""
    try:
        available_engines = ocr_manager.get_available_engines()
        if not available_engines:
            return {"status": "not_ready", "reason": "No OCR engines available"}
        
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "reason": str(e)}


@app.get("/health/live")
async def liveness_check():
    """Liveness check endpoint."""
    return {"status": "alive"}


@app.get("/info", response_model=ServiceInfo)
async def service_info():
    """Service information endpoint."""
    return ServiceInfo(
        service="ocr",
        version="0.1.0",
        engines=ocr_manager.get_available_engines(),
        supported_formats=settings.supported_formats,
        max_file_size=settings.max_file_size,
        max_image_size=settings.max_image_size,
        features=[
            "text_extraction",
            "handwritten_text",
            "printed_text",
            "text_cleaning",
            "multiple_engines",
            "batch_processing"
        ]
    )


@app.get("/stats", response_model=ProcessingStats)
async def get_stats():
    """Get processing statistics."""
    return ProcessingStats(
        total_requests=stats["total_requests"],
        successful_requests=stats["successful_requests"],
        failed_requests=stats["failed_requests"],
        average_processing_time=sum(stats["processing_times"]) / len(stats["processing_times"]) if stats["processing_times"] else 0.0,
        average_confidence=0.0,  # TODO: Track confidence
        engines_usage=stats["engines_usage"],
        languages_processed=stats["languages_processed"]
    )


@app.post("/ocr/extract")
async def extract_text(
    file: UploadFile = File(...),
    engine: OCREngine = Form(OCREngine.PADDLEOCR),
    language: str = Form("en"),
    min_confidence: float = Form(0.5),
    enable_cleaning: bool = Form(True),
    enable_spell_check: bool = Form(False)
):
    """Extract text from uploaded image."""
    logger = structlog.get_logger()
    
    # Update stats
    stats["total_requests"] += 1
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Validate image
        is_valid, message = ImageProcessor.validate_image(file_content)
        if not is_valid:
            stats["failed_requests"] += 1
            raise HTTPException(status_code=400, detail=message)
        
        # Load and preprocess image
        image = ImageProcessor.load_image_from_bytes(file_content)
        processed_image = ImageProcessor.preprocess_for_ocr(image, engine.value)
        
        # Create OCR request
        ocr_request = OCRRequest(
            image_data=file_content,
            engine=engine,
            language=language,
            min_confidence=min_confidence,
            enable_cleaning=enable_cleaning,
            enable_spell_check=enable_spell_check
        )
        
        # Process with OCR
        result = ocr_manager.process_image(processed_image, ocr_request)
        
        # Post-process text if requested
        if enable_cleaning and result.text:
            result.cleaned_text = TextProcessor.clean_text(result.text)
        
        # Update stats
        stats["successful_requests"] += 1
        stats["processing_times"].append(result.processing_time)
        stats["engines_usage"][engine.value] = stats["engines_usage"].get(engine.value, 0) + 1
        stats["languages_processed"][language] = stats["languages_processed"].get(language, 0) + 1
        
        logger.info(
            "OCR processing completed",
            filename=file.filename,
            engine=engine.value,
            text_length=len(result.text),
            confidence=result.confidence,
            processing_time=result.processing_time
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        stats["failed_requests"] += 1
        logger.error("OCR processing failed", filename=file.filename, error=str(e))
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@app.post("/ocr/batch")
async def extract_text_batch(files: List[UploadFile] = File(...)):
    """Extract text from multiple images."""
    if len(files) > 10:  # Limit batch size
        raise HTTPException(status_code=400, detail="Maximum 10 files per batch")
    
    results = []
    
    for file in files:
        try:
            # Process each file individually
            file_content = await file.read()
            
            # Validate image
            is_valid, message = ImageProcessor.validate_image(file_content)
            if not is_valid:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": message
                })
                continue
            
            # Load and preprocess image
            image = ImageProcessor.load_image_from_bytes(file_content)
            processed_image = ImageProcessor.preprocess_for_ocr(image, "paddleocr")
            
            # Create OCR request
            ocr_request = OCRRequest(
                image_data=file_content,
                engine=OCREngine.PADDLEOCR,
                language="en",
                min_confidence=0.5,
                enable_cleaning=True
            )
            
            # Process with OCR
            result = ocr_manager.process_image(processed_image, ocr_request)
            
            # Clean text
            if result.text:
                result.cleaned_text = TextProcessor.clean_text(result.text)
            
            results.append({
                "filename": file.filename,
                "success": True,
                "result": result
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    return {"results": results}


@app.get("/engines")
async def get_engines():
    """Get available OCR engines."""
    return {
        "available_engines": ocr_manager.get_available_engines(),
        "engines_info": ocr_manager.get_engines_info()
    }


def main():
    """Main entry point for the OCR service."""
    import uvicorn
    
    uvicorn.run(
        "services.ocr.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()
