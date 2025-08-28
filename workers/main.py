"""Main FastAPI application for the Worker service."""

import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="IELTS Worker Service",
    description="Background task processing service",
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


class TaskRequest(BaseModel):
    task_type: str
    data: dict


class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: dict = None


# Service state
_start_time = time.time()


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint."""
    uptime = time.time() - _start_time
    return HealthStatus(
        status="healthy",
        service="worker",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        uptime=uptime,
    )


@app.post("/task", response_model=TaskResponse)
async def process_task(request: TaskRequest):
    """Process a background task."""
    # Simplified task processing logic
    task_id = f"task_{int(time.time())}"

    # Simulate processing
    result = {"processed": True, "task_type": request.task_type, "data": request.data}

    return TaskResponse(task_id=task_id, status="completed", result=result)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "IELTS Worker Service",
        "version": "0.1.0",
        "endpoints": ["/health", "/task"],
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8004))
    uvicorn.run(app, host="0.0.0.0", port=port)
