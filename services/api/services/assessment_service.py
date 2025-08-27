"""Assessment service for managing mock tests and sessions."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import uuid

from ..models.assessment import (
    MockTest, TestSession, TestQuestion, SessionAnswer,
    TestType, DifficultyLevel, ModuleType, TestStatus,
    MockTestCreate, TestSessionCreate, SessionAnswerCreate,
    TestResult
)
from ..models.user import User


class AssessmentService:
    """Service for managing assessment-related operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_mock_test(self, test_data: MockTestCreate) -> MockTest:
        """Create a new mock test."""
        mock_test = MockTest(
            title=test_data.title,
            test_type=test_data.test_type,
            difficulty_level=test_data.difficulty_level,
            duration_minutes=test_data.duration_minutes,
            total_questions=test_data.total_questions
        )
        
        self.db.add(mock_test)
        self.db.commit()
        self.db.refresh(mock_test)
        
        return mock_test
    
    def get_mock_tests(
        self,
        test_type: Optional[TestType] = None,
        difficulty_level: Optional[DifficultyLevel] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> List[MockTest]:
        """Get mock tests with optional filtering."""
        query = self.db.query(MockTest)
        
        if test_type:
            query = query.filter(MockTest.test_type == test_type)
        
        if difficulty_level:
            query = query.filter(MockTest.difficulty_level == difficulty_level)
        
        if is_active is not None:
            query = query.filter(MockTest.is_active == is_active)
        
        return query.order_by(desc(MockTest.created_at)).offset(offset).limit(limit).all()
    
    def get_mock_test_by_id(self, test_id: str) -> Optional[MockTest]:
        """Get a mock test by ID."""
        return self.db.query(MockTest).filter(MockTest.id == test_id).first()
    
    def start_test_session(self, user_id: str, test_id: str) -> TestSession:
        """Start a new test session for a user."""
        # Check if user already has an active session for this test
        existing_session = self.db.query(TestSession).filter(
            and_(
                TestSession.user_id == user_id,
                TestSession.test_id == test_id,
                TestSession.status.in_([TestStatus.STARTED, TestStatus.IN_PROGRESS])
            )
        ).first()
        
        if existing_session:
            return existing_session
        
        # Create new session
        session = TestSession(
            user_id=user_id,
            test_id=test_id,
            status=TestStatus.STARTED,
            start_time=datetime.utcnow()
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def get_test_session(self, session_id: str) -> Optional[TestSession]:
        """Get a test session by ID."""
        return self.db.query(TestSession).filter(TestSession.id == session_id).first()
    
    def get_user_active_sessions(self, user_id: str) -> List[TestSession]:
        """Get all active test sessions for a user."""
        return self.db.query(TestSession).filter(
            and_(
                TestSession.user_id == user_id,
                TestSession.status.in_([TestStatus.STARTED, TestStatus.IN_PROGRESS])
            )
        ).all()
    
    def update_session_status(self, session_id: str, status: TestStatus) -> Optional[TestSession]:
        """Update the status of a test session."""
        session = self.get_test_session(session_id)
        if not session:
            return None
        
        session.status = status
        
        if status == TestStatus.COMPLETED:
            session.end_time = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def get_test_questions(self, test_id: str) -> List[TestQuestion]:
        """Get all questions for a mock test."""
        return self.db.query(TestQuestion).filter(
            TestQuestion.test_id == test_id
        ).order_by(TestQuestion.question_number).all()
    
    def submit_answer(
        self,
        session_id: str,
        question_id: str,
        user_answer: Dict[str, Any],
        time_spent: Optional[int] = None
    ) -> SessionAnswer:
        """Submit an answer for a test question."""
        # Get the question to validate the answer
        question = self.db.query(TestQuestion).filter(TestQuestion.id == question_id).first()
        if not question:
            raise ValueError("Question not found")
        
        # Check if answer already exists
        existing_answer = self.db.query(SessionAnswer).filter(
            and_(
                SessionAnswer.session_id == session_id,
                SessionAnswer.question_id == question_id
            )
        ).first()
        
        if existing_answer:
            # Update existing answer
            existing_answer.user_answer = user_answer
            existing_answer.time_spent = time_spent
            existing_answer.is_correct = self._validate_answer(user_answer, question.correct_answer)
            self.db.commit()
            self.db.refresh(existing_answer)
            return existing_answer
        
        # Create new answer
        answer = SessionAnswer(
            session_id=session_id,
            question_id=question_id,
            user_answer=user_answer,
            time_spent=time_spent,
            is_correct=self._validate_answer(user_answer, question.correct_answer)
        )
        
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        
        return answer
    
    def complete_test_session(self, session_id: str) -> TestResult:
        """Complete a test session and calculate results."""
        session = self.get_test_session(session_id)
        if not session:
            raise ValueError("Session not found")
        
        # Get all answers for this session
        answers = self.db.query(SessionAnswer).filter(
            SessionAnswer.session_id == session_id
        ).all()
        
        # Calculate results
        total_questions = len(answers)
        correct_answers = sum(1 for answer in answers if answer.is_correct)
        overall_score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Calculate module scores
        module_scores = self._calculate_module_scores(answers)
        
        # Calculate band score (simplified IELTS band calculation)
        band_score = self._calculate_band_score(overall_score)
        
        # Calculate time taken
        time_taken = 0
        if session.end_time and session.start_time:
            time_taken = int((session.end_time - session.start_time).total_seconds() / 60)
        
        # Create detailed feedback
        detailed_feedback = self._generate_detailed_feedback(answers, module_scores)
        
        # Update session with results
        session.status = TestStatus.COMPLETED
        session.end_time = datetime.utcnow()
        session.score_data = {
            "overall_score": overall_score,
            "module_scores": module_scores,
            "band_score": band_score,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "time_taken": time_taken
        }
        
        self.db.commit()
        
        return TestResult(
            session_id=session_id,
            overall_score=overall_score,
            module_scores=module_scores,
            total_questions=total_questions,
            correct_answers=correct_answers,
            time_taken=time_taken,
            band_score=band_score,
            detailed_feedback=detailed_feedback
        )
    
    def _validate_answer(self, user_answer: Dict[str, Any], correct_answer: Dict[str, Any]) -> bool:
        """Validate if a user answer is correct."""
        # This is a simplified validation - in a real implementation,
        # you would have more sophisticated logic for different question types
        return user_answer == correct_answer
    
    def _calculate_module_scores(self, answers: List[SessionAnswer]) -> Dict[str, float]:
        """Calculate scores for each module."""
        module_scores = {}
        
        for module in ModuleType:
            module_answers = [a for a in answers if a.test_question.module_type == module]
            if module_answers:
                correct_count = sum(1 for a in module_answers if a.is_correct)
                module_scores[module.value] = (correct_count / len(module_answers)) * 100
            else:
                module_scores[module.value] = 0.0
        
        return module_scores
    
    def _calculate_band_score(self, overall_score: float) -> float:
        """Calculate IELTS band score from percentage."""
        # Simplified band score calculation
        # In reality, IELTS uses a complex scoring system
        if overall_score >= 90:
            return 9.0
        elif overall_score >= 80:
            return 8.0
        elif overall_score >= 70:
            return 7.0
        elif overall_score >= 60:
            return 6.0
        elif overall_score >= 50:
            return 5.0
        elif overall_score >= 40:
            return 4.0
        elif overall_score >= 30:
            return 3.0
        elif overall_score >= 20:
            return 2.0
        else:
            return 1.0
    
    def _generate_detailed_feedback(self, answers: List[SessionAnswer], module_scores: Dict[str, float]) -> Dict[str, Any]:
        """Generate detailed feedback for the test results."""
        feedback = {
            "overall_performance": "Good" if module_scores.get("overall", 0) >= 70 else "Needs Improvement",
            "module_analysis": {},
            "recommendations": []
        }
        
        # Analyze each module
        for module, score in module_scores.items():
            if score >= 80:
                feedback["module_analysis"][module] = "Excellent"
            elif score >= 70:
                feedback["module_analysis"][module] = "Good"
            elif score >= 60:
                feedback["module_analysis"][module] = "Satisfactory"
            else:
                feedback["module_analysis"][module] = "Needs Improvement"
                feedback["recommendations"].append(f"Focus on improving your {module} skills")
        
        return feedback
    
    def get_user_test_history(self, user_id: str, limit: int = 20) -> List[TestSession]:
        """Get test history for a user."""
        return self.db.query(TestSession).filter(
            and_(
                TestSession.user_id == user_id,
                TestSession.status == TestStatus.COMPLETED
            )
        ).order_by(desc(TestSession.end_time)).limit(limit).all()
