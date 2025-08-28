"""Main FastAPI application for the Scoring service."""

import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="IELTS Scoring Service",
    description="AI-powered IELTS scoring service",
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


class ScoringRequest(BaseModel):
    text: str
    task_type: str
    band_score: float = None


class ScoringResponse(BaseModel):
    score: float
    feedback: str
    confidence: float
    breakdown: dict


# Service state
_start_time = time.time()


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint."""
    uptime = time.time() - _start_time
    return HealthStatus(
        status="healthy",
        service="scoring",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        uptime=uptime,
    )


@app.post("/score", response_model=ScoringResponse)
async def score_submission(request: ScoringRequest):
    """Score a submission."""
    # Simplified scoring logic
    score = 7.0  # Default score
    feedback = "Good work! Continue practicing."
    confidence = 0.85

    breakdown = {
        "grammar": 7.0,
        "vocabulary": 7.0,
        "coherence": 7.0,
        "task_achievement": 7.0,
    }

    return ScoringResponse(
        score=score, feedback=feedback, confidence=confidence, breakdown=breakdown
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "IELTS Scoring Service",
        "version": "0.1.0",
        "endpoints": ["/health", "/score"],
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
