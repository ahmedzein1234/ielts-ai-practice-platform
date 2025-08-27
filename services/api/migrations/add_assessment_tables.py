"""Migration script to add assessment tables."""

import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Database URL - adjust as needed
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ielts_ai")

def create_assessment_tables():
    """Create assessment-related tables."""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Create mock_tests table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS mock_tests (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title VARCHAR(255) NOT NULL,
                test_type VARCHAR(20) NOT NULL CHECK (test_type IN ('academic', 'general')),
                difficulty_level VARCHAR(20) NOT NULL CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
                duration_minutes INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create test_sessions table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS test_sessions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                test_id UUID NOT NULL REFERENCES mock_tests(id) ON DELETE CASCADE,
                status VARCHAR(20) NOT NULL CHECK (status IN ('started', 'in_progress', 'completed', 'abandoned')),
                start_time TIMESTAMP WITH TIME ZONE NOT NULL,
                end_time TIMESTAMP WITH TIME ZONE,
                score_data JSONB,
                proctoring_data JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create test_questions table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS test_questions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                test_id UUID NOT NULL REFERENCES mock_tests(id) ON DELETE CASCADE,
                module_type VARCHAR(20) NOT NULL CHECK (module_type IN ('listening', 'reading', 'writing', 'speaking')),
                question_number INTEGER NOT NULL,
                question_data JSONB NOT NULL,
                correct_answer JSONB NOT NULL,
                points INTEGER DEFAULT 1,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create session_answers table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS session_answers (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                session_id UUID NOT NULL REFERENCES test_sessions(id) ON DELETE CASCADE,
                question_id UUID NOT NULL REFERENCES test_questions(id) ON DELETE CASCADE,
                user_answer JSONB,
                is_correct BOOLEAN,
                time_spent INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Add indexes for better performance
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_test_sessions_user_id ON test_sessions(user_id);
            CREATE INDEX IF NOT EXISTS idx_test_sessions_test_id ON test_sessions(test_id);
            CREATE INDEX IF NOT EXISTS idx_test_questions_test_id ON test_questions(test_id);
            CREATE INDEX IF NOT EXISTS idx_session_answers_session_id ON session_answers(session_id);
            CREATE INDEX IF NOT EXISTS idx_session_answers_question_id ON session_answers(question_id);
        """))
        
        conn.commit()
        print("✅ Assessment tables created successfully!")

def insert_sample_data():
    """Insert sample mock test data."""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Insert sample mock tests
        conn.execute(text("""
            INSERT INTO mock_tests (title, test_type, difficulty_level, duration_minutes, total_questions)
            VALUES 
                ('IELTS Academic Practice Test 1', 'academic', 'intermediate', 165, 40),
                ('IELTS General Training Practice Test 1', 'general', 'intermediate', 165, 40),
                ('IELTS Academic Practice Test 2', 'academic', 'advanced', 165, 40),
                ('IELTS General Training Practice Test 2', 'general', 'beginner', 165, 40)
            ON CONFLICT DO NOTHING;
        """))
        
        # Get the test IDs to insert sample questions
        result = conn.execute(text("SELECT id FROM mock_tests LIMIT 1"))
        row = result.fetchone()
        test_id = row[0] if row else None
        
        if test_id:
            # Insert sample questions for the first test
            sample_questions = [
                {
                    "test_id": test_id,
                    "module_type": "listening",
                    "question_number": 1,
                    "question_data": {
                        "question_text": "What is the main topic of the conversation?",
                        "options": ["Weather", "Travel", "Food", "Sports"],
                        "question_type": "multiple_choice",
                        "module_specific_data": {"audio_url": "sample_audio_1.mp3"}
                    },
                    "correct_answer": {"answer": "Travel"},
                    "points": 1
                },
                {
                    "test_id": test_id,
                    "module_type": "reading",
                    "question_number": 2,
                    "question_data": {
                        "question_text": "According to the passage, what is the primary cause of climate change?",
                        "options": ["Natural cycles", "Human activities", "Solar radiation", "Volcanic eruptions"],
                        "question_type": "multiple_choice",
                        "module_specific_data": {"passage_text": "Sample passage about climate change..."}
                    },
                    "correct_answer": {"answer": "Human activities"},
                    "points": 1
                },
                {
                    "test_id": test_id,
                    "module_type": "writing",
                    "question_number": 3,
                    "question_data": {
                        "question_text": "Write an essay on the following topic: The impact of technology on modern education.",
                        "question_type": "essay",
                        "module_specific_data": {"word_limit": 250, "time_limit": 40}
                    },
                    "correct_answer": {"criteria": ["coherence", "grammar", "vocabulary", "task_achievement"]},
                    "points": 1
                },
                {
                    "test_id": test_id,
                    "module_type": "speaking",
                    "question_number": 4,
                    "question_data": {
                        "question_text": "Describe your hometown. What do you like most about it?",
                        "question_type": "speaking_prompt",
                        "module_specific_data": {"time_limit": 2, "preparation_time": 1}
                    },
                    "correct_answer": {"criteria": ["fluency", "pronunciation", "grammar", "vocabulary"]},
                    "points": 1
                }
            ]
            
            for question in sample_questions:
                conn.execute(text("""
                    INSERT INTO test_questions (test_id, module_type, question_number, question_data, correct_answer, points)
                    VALUES (:test_id, :module_type, :question_number, :question_data, :correct_answer, :points)
                    ON CONFLICT DO NOTHING;
                """), question)
        
        conn.commit()
        print("✅ Sample data inserted successfully!")

if __name__ == "__main__":
    print("🚀 Starting assessment tables migration...")
    create_assessment_tables()
    insert_sample_data()
    print("✅ Migration completed successfully!")
