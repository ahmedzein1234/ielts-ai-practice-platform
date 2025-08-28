"""Main FastAPI application for the OCR service."""

import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="IELTS OCR Service",
    description="OCR service for processing images and documents",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class HealthStatus(BaseModel):
    status: str
    service: str
    timestamp: str
    uptime: float


class OCRRequest(BaseModel):
    image_url: str = None
    text: str = None


class OCRResponse(BaseModel):
    extracted_text: str
    confidence: float
    language: str
    processing_time: float


# Service state
_start_time = time.time()


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint."""
    uptime = time.time() - _start_time
    return HealthStatus(
        status="healthy",
        service="ocr",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        uptime=uptime,
    )


@app.post("/extract", response_model=OCRResponse)
async def extract_text(request: OCRRequest):
    """Extract text from image or process existing text."""
    # Simplified OCR logic
    if request.text:
        extracted_text = request.text
    else:
        extracted_text = "Sample extracted text from image"

    return OCRResponse(
        extracted_text=extracted_text,
        confidence=0.95,
        language="en",
        processing_time=0.5,
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "IELTS OCR Service",
        "version": "0.1.0",
        "endpoints": ["/health", "/extract"],
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
