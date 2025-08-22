"""Writing module endpoints."""

from typing import Dict, Any, List
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
import structlog

from services.common.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class WritingPrompt(BaseModel):
    """Writing prompt model."""
    id: str
    task: str
    title: str
    description: str
    word_limit: int
    time_limit: int


class WritingSubmission(BaseModel):
    """Writing submission model."""
    id: str
    user_id: str
    task: str
    text: str
    image_url: str = None
    score: Dict[str, float]
    feedback: List[str]


@router.get("/prompts")
async def get_writing_prompts(task: str = None) -> List[WritingPrompt]:
    """Get writing prompts."""
    # TODO: Implement actual prompt retrieval
    logger.info("Fetching writing prompts", task=task)
    
    # Placeholder prompts
    prompts = [
        WritingPrompt(
            id="1",
            task="task_1",
            title="Bar Chart: Global Coffee Production",
            description="The chart below shows global coffee production from 2010 to 2020. Summarise the information by selecting and reporting the main features.",
            word_limit=150,
            time_limit=20
        ),
        WritingPrompt(
            id="2",
            task="task_2",
            title="Essay: Technology in Education",
            description="Some people believe that technology has made education more accessible, while others think it has created more problems. Discuss both views and give your opinion.",
            word_limit=250,
            time_limit=40
        )
    ]
    
    if task:
        prompts = [p for p in prompts if p.task == task]
    
    return prompts


@router.post("/submissions")
async def create_writing_submission(
    prompt_id: str,
    text: str,
    image: UploadFile = File(None)
) -> WritingSubmission:
    """Create a new writing submission."""
    # TODO: Implement actual submission creation and OCR processing
    logger.info("Creating writing submission", prompt_id=prompt_id)
    
    return WritingSubmission(
        id="submission_1",
        user_id="user_1",
        task="task_2",
        text=text,
        image_url=image.filename if image else None,
        score={
            "task_achievement": 7.0,
            "coherence": 6.5,
            "lexical_resource": 7.0,
            "grammatical_range": 6.0,
            "overall": 6.6
        },
        feedback=[
            "Good task response and clear structure",
            "Work on grammatical accuracy",
            "Expand vocabulary range"
        ]
    )


@router.get("/submissions/{submission_id}")
async def get_writing_submission(submission_id: str) -> WritingSubmission:
    """Get writing submission details."""
    # TODO: Implement actual submission retrieval
    logger.info("Fetching writing submission", submission_id=submission_id)
    
    return WritingSubmission(
        id=submission_id,
        user_id="user_1",
        task="task_2",
        text="Technology has undoubtedly transformed education in recent years...",
        image_url="https://example.com/essay.jpg",
        score={
            "task_achievement": 7.0,
            "coherence": 6.5,
            "lexical_resource": 7.0,
            "grammatical_range": 6.0,
            "overall": 6.6
        },
        feedback=[
            "Good task response and clear structure",
            "Work on grammatical accuracy",
            "Expand vocabulary range"
        ]
    )


@router.post("/ocr")
async def process_ocr(image: UploadFile = File(...)) -> Dict[str, Any]:
    """Process OCR for handwritten text."""
    # TODO: Implement actual OCR processing
    logger.info("Processing OCR", filename=image.filename)
    
    return {
        "text": "This is a sample OCR result from the uploaded image.",
        "confidence": 0.95,
        "word_count": 15
    }


@router.get("/history")
async def get_writing_history() -> List[WritingSubmission]:
    """Get user's writing history."""
    # TODO: Implement actual history retrieval
    logger.info("Fetching writing history")
    
    return [
        WritingSubmission(
            id="submission_1",
            user_id="user_1",
            task="task_2",
            text="Technology has undoubtedly transformed education...",
            image_url="https://example.com/essay1.jpg",
            score={"overall": 6.6},
            feedback=["Good task response"]
        )
    ]
