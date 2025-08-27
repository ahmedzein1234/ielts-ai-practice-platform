"""Assessment API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.assessment import (
    MockTestCreate, MockTestResponse, TestSessionCreate, TestSessionResponse,
    TestQuestionResponse, SessionAnswerCreate, SessionAnswerResponse, TestResult,
    TestType, DifficultyLevel, TestStatus
)
from ..services.assessment_service import AssessmentService
from ..auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("/tests", response_model=MockTestResponse, status_code=status.HTTP_201_CREATED)
async def create_mock_test(
    test_data: MockTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new mock test (admin only)."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create mock tests"
        )
    
    assessment_service = AssessmentService(db)
    mock_test = assessment_service.create_mock_test(test_data)
    
    return MockTestResponse.from_orm(mock_test)


@router.get("/tests", response_model=List[MockTestResponse])
async def get_mock_tests(
    test_type: Optional[TestType] = None,
    difficulty_level: Optional[DifficultyLevel] = None,
    is_active: bool = True,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available mock tests with optional filtering."""
    assessment_service = AssessmentService(db)
    mock_tests = assessment_service.get_mock_tests(
        test_type=test_type,
        difficulty_level=difficulty_level,
        is_active=is_active,
        limit=limit,
        offset=offset
    )
    
    return [MockTestResponse.from_orm(test) for test in mock_tests]


@router.get("/tests/{test_id}", response_model=MockTestResponse)
async def get_mock_test(
    test_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific mock test by ID."""
    assessment_service = AssessmentService(db)
    mock_test = assessment_service.get_mock_test_by_id(test_id)
    
    if not mock_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mock test not found"
        )
    
    return MockTestResponse.from_orm(mock_test)


@router.post("/sessions", response_model=TestSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_test_session(
    session_data: TestSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new test session."""
    assessment_service = AssessmentService(db)
    
    # Verify the test exists
    mock_test = assessment_service.get_mock_test_by_id(session_data.test_id)
    if not mock_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mock test not found"
        )
    
    if not mock_test.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This test is not currently available"
        )
    
    session = assessment_service.start_test_session(
        user_id=current_user.id,
        test_id=session_data.test_id
    )
    
    return TestSessionResponse.from_orm(session)


@router.get("/sessions/{session_id}", response_model=TestSessionResponse)
async def get_test_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific test session."""
    assessment_service = AssessmentService(db)
    session = assessment_service.get_test_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found"
        )
    
    # Ensure user can only access their own sessions
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return TestSessionResponse.from_orm(session)


@router.get("/sessions/{session_id}/questions", response_model=List[TestQuestionResponse])
async def get_session_questions(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get questions for a test session."""
    assessment_service = AssessmentService(db)
    session = assessment_service.get_test_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found"
        )
    
    # Ensure user can only access their own sessions
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    questions = assessment_service.get_test_questions(session.test_id)
    
    return [TestQuestionResponse.from_orm(q) for q in questions]


@router.post("/sessions/{session_id}/answers", response_model=SessionAnswerResponse)
async def submit_answer(
    session_id: str,
    answer_data: SessionAnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit an answer for a test question."""
    assessment_service = AssessmentService(db)
    session = assessment_service.get_test_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found"
        )
    
    # Ensure user can only access their own sessions
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Ensure session is active
    if session.status not in [TestStatus.STARTED, TestStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot submit answers to a completed session"
        )
    
    try:
        answer = assessment_service.submit_answer(
            session_id=session_id,
            question_id=answer_data.question_id,
            user_answer=answer_data.user_answer,
            time_spent=answer_data.time_spent
        )
        
        # Update session status to in progress if it was just started
        if session.status == TestStatus.STARTED:
            assessment_service.update_session_status(session_id, TestStatus.IN_PROGRESS)
        
        return SessionAnswerResponse.from_orm(answer)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/sessions/{session_id}/complete", response_model=TestResult)
async def complete_test_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete a test session and get results."""
    assessment_service = AssessmentService(db)
    session = assessment_service.get_test_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found"
        )
    
    # Ensure user can only access their own sessions
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Ensure session is active
    if session.status == TestStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is already completed"
        )
    
    try:
        result = assessment_service.complete_test_session(session_id)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/sessions/active", response_model=List[TestSessionResponse])
async def get_active_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active test sessions for the current user."""
    assessment_service = AssessmentService(db)
    sessions = assessment_service.get_user_active_sessions(current_user.id)
    
    return [TestSessionResponse.from_orm(session) for session in sessions]


@router.get("/history", response_model=List[TestSessionResponse])
async def get_test_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get test history for the current user."""
    assessment_service = AssessmentService(db)
    sessions = assessment_service.get_user_test_history(current_user.id, limit=limit)
    
    return [TestSessionResponse.from_orm(session) for session in sessions]
