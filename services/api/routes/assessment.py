"""Assessment API routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class MockTestResponse(BaseModel):
    id: str
    title: str
    test_type: str
    difficulty_level: str
    duration_minutes: int
    is_active: bool


class TestSessionResponse(BaseModel):
    id: str
    test_id: str
    user_id: int
    status: str
    start_time: str
    end_time: Optional[str] = None


@router.get("/", response_model=List[MockTestResponse])
async def get_mock_tests():
    """Get available mock tests."""
    return [
        MockTestResponse(
            id="test-1",
            title="IELTS Academic Reading Test 1",
            test_type="academic",
            difficulty_level="intermediate",
            duration_minutes=60,
            is_active=True,
        ),
        MockTestResponse(
            id="test-2",
            title="IELTS General Writing Test 1",
            test_type="general",
            difficulty_level="advanced",
            duration_minutes=60,
            is_active=True,
        ),
    ]


@router.get("/{test_id}", response_model=MockTestResponse)
async def get_mock_test(test_id: str):
    """Get a specific mock test by ID."""
    return MockTestResponse(
        id=test_id,
        title=f"IELTS Test {test_id}",
        test_type="academic",
        difficulty_level="intermediate",
        duration_minutes=60,
        is_active=True,
    )


@router.post("/sessions", response_model=TestSessionResponse)
async def start_test_session():
    """Start a new test session."""
    return TestSessionResponse(
        id="session-1",
        test_id="test-1",
        user_id=1,
        status="in_progress",
        start_time="2024-01-01T10:00:00Z",
    )


@router.get("/sessions/{session_id}", response_model=TestSessionResponse)
async def get_test_session(session_id: str):
    """Get a specific test session."""
    return TestSessionResponse(
        id=session_id,
        test_id="test-1",
        user_id=1,
        status="completed",
        start_time="2024-01-01T10:00:00Z",
        end_time="2024-01-01T11:00:00Z",
    )
