"""Add learning feature tables to the database."""

from sqlalchemy import text
from sqlalchemy.orm import Session
import structlog

logger = structlog.get_logger(__name__)


def create_learning_tables(db: Session):
    """Create all learning feature tables."""

    # Create learning_paths table
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS learning_paths (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id),
            title VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(50) DEFAULT 'active',
            target_band_score NUMERIC(3,1),
            estimated_duration_days INTEGER,
            difficulty_progression JSONB,
            learning_style VARCHAR(50),
            path_structure JSONB,
            skill_gaps JSONB,
            priority_areas JSONB,
            current_position INTEGER DEFAULT 0,
            completion_percentage FLOAT DEFAULT 0.0,
            total_objectives INTEGER DEFAULT 0,
            completed_objectives INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            started_at TIMESTAMP WITH TIME ZONE,
            completed_at TIMESTAMP WITH TIME ZONE
        )
    """))

    # Create learning_objectives table
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS learning_objectives (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            learning_path_id UUID NOT NULL REFERENCES learning_paths(id),
            title VARCHAR(255) NOT NULL,
            description TEXT,
            objective_type VARCHAR(50) NOT NULL,
            target_skill VARCHAR(100),
            target_score NUMERIC(5,2),
            estimated_time_minutes INTEGER,
            difficulty_level VARCHAR(50),
            content_items JSONB,
            required_activities JSONB,
            optional_activities JSONB,
            sort_order INTEGER DEFAULT 0,
            is_completed BOOLEAN DEFAULT FALSE,
            completion_date TIMESTAMP WITH TIME ZONE,
            actual_time_spent INTEGER,
            prerequisites JSONB,
            unlocks JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """))

    # Create user_progress table
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS user_progress (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id),
            learning_path_id UUID REFERENCES learning_paths(id),
            content_item_id UUID REFERENCES content_items(id),
            test_session_id UUID REFERENCES test_sessions(id),
            time_spent_minutes INTEGER DEFAULT 0,
            completion_rate FLOAT DEFAULT 0.0,
            score NUMERIC(5,2),
            accuracy NUMERIC(5,2),
            engagement_level INTEGER,
            difficulty_rating INTEGER,
            confidence_level INTEGER,
            learning_velocity FLOAT,
            session_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            session_end TIMESTAMP WITH TIME ZONE,
            session_duration INTEGER,
            device_type VARCHAR(50),
            study_environment VARCHAR(50),
            energy_level INTEGER,
            focus_level INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """))

    # Create recommendations table
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id),
            recommendation_type VARCHAR(50) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            reasoning TEXT,
            content_item_id UUID REFERENCES content_items(id),
            learning_path_id UUID REFERENCES learning_paths(id),
            action_type VARCHAR(100),
            action_data JSONB,
            confidence_score FLOAT NOT NULL,
            priority_score FLOAT NOT NULL,
            estimated_impact FLOAT,
            time_to_complete INTEGER,
            is_viewed BOOLEAN DEFAULT FALSE,
            is_accepted BOOLEAN,
            viewed_at TIMESTAMP WITH TIME ZONE,
            accepted_at TIMESTAMP WITH TIME ZONE,
            context_data JSONB,
            expires_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """))

    # Create skill_mastery table
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS skill_mastery (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id),
            skill_name VARCHAR(100) NOT NULL,
            module_type VARCHAR(50) NOT NULL,
            current_level VARCHAR(50) NOT NULL,
            previous_level VARCHAR(50),
            mastery_score FLOAT NOT NULL,
            total_attempts INTEGER DEFAULT 0,
            successful_attempts INTEGER DEFAULT 0,
            average_score FLOAT DEFAULT 0.0,
            best_score FLOAT DEFAULT 0.0,
            total_time_spent INTEGER DEFAULT 0,
            last_practiced TIMESTAMP WITH TIME ZONE,
            days_since_last_practice INTEGER,
            improvement_rate FLOAT,
            learning_curve JSONB,
            identified_weaknesses JSONB,
            identified_strengths JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            level_upgraded_at TIMESTAMP WITH TIME ZONE
        )
    """))

    # Create learning_analytics table
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS learning_analytics (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id),
            date TIMESTAMP WITH TIME ZONE NOT NULL,
            total_study_time INTEGER DEFAULT 0,
            sessions_count INTEGER DEFAULT 0,
            content_items_completed INTEGER DEFAULT 0,
            objectives_completed INTEGER DEFAULT 0,
            average_score FLOAT DEFAULT 0.0,
            average_accuracy FLOAT DEFAULT 0.0,
            improvement_rate FLOAT,
            engagement_score FLOAT DEFAULT 0.0,
            focus_score FLOAT DEFAULT 0.0,
            consistency_score FLOAT DEFAULT 0.0,
            preferred_study_times JSONB,
            preferred_content_types JSONB,
            learning_velocity FLOAT,
            skills_improved JSONB,
            skills_struggling JSONB,
            recommendations_generated INTEGER DEFAULT 0,
            recommendations_accepted INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """))

    # Create indexes for performance
    db.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_learning_paths_user_id ON learning_paths(user_id);
        CREATE INDEX IF NOT EXISTS idx_learning_paths_status ON learning_paths(status);
        CREATE INDEX IF NOT EXISTS idx_learning_objectives_path_id ON learning_objectives(learning_path_id);
        CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_progress_session_start ON user_progress(session_start);
        CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON recommendations(user_id);
        CREATE INDEX IF NOT EXISTS idx_recommendations_type ON recommendations(recommendation_type);
        CREATE INDEX IF NOT EXISTS idx_recommendations_priority ON recommendations(priority_score DESC);
        CREATE INDEX IF NOT EXISTS idx_skill_mastery_user_id ON skill_mastery(user_id);
        CREATE INDEX IF NOT EXISTS idx_skill_mastery_skill ON skill_mastery(skill_name, module_type);
        CREATE INDEX IF NOT EXISTS idx_learning_analytics_user_date ON learning_analytics(user_id, date);
    """))

    db.commit()
    logger.info("Learning feature tables created successfully")


def insert_sample_learning_data(db: Session):
    """Insert sample learning data for testing."""
    
    # Get a sample user ID (assuming there's at least one user)
    result = db.execute(text("SELECT id FROM users LIMIT 1"))
    row = result.fetchone()
    if not row:
        logger.warning("No users found, skipping sample learning data insertion")
        return
    
    user_id = row[0]
    
    # Insert sample learning path
    db.execute(text("""
        INSERT INTO learning_paths (
            user_id, title, description, status, target_band_score, 
            estimated_duration_days, skill_gaps, priority_areas, total_objectives
        ) VALUES (
            :user_id, 'IELTS Band 7 Preparation', 
            'Comprehensive path to achieve IELTS Band 7', 'active', 7.0, 90,
            '["Speaking Fluency", "Grammar Accuracy", "Academic Vocabulary"]',
            '["Reading Speed", "Listening Comprehension", "Writing Coherence"]', 3
        )
    """), {"user_id": user_id})
    
    # Get the learning path ID
    result = db.execute(text("SELECT id FROM learning_paths WHERE user_id = :user_id LIMIT 1"))
    row = result.fetchone()
    if row:
        learning_path_id = row[0]
        
        # Insert sample learning objectives
        objectives = [
            {
                "title": "Improve Speaking Fluency",
                "description": "Focus on developing speaking fluency skills",
                "objective_type": "skill_improvement",
                "target_skill": "Speaking Fluency",
                "target_score": 80.0,
                "estimated_time_minutes": 45,
                "difficulty_level": "intermediate",
                "sort_order": 0
            },
            {
                "title": "Enhance Grammar Accuracy",
                "description": "Work on grammar rules and accuracy",
                "objective_type": "skill_improvement",
                "target_skill": "Grammar Accuracy",
                "target_score": 85.0,
                "estimated_time_minutes": 60,
                "difficulty_level": "intermediate",
                "sort_order": 1
            },
            {
                "title": "Expand Academic Vocabulary",
                "description": "Build academic vocabulary for better performance",
                "objective_type": "skill_improvement",
                "target_skill": "Academic Vocabulary",
                "target_score": 75.0,
                "estimated_time_minutes": 30,
                "difficulty_level": "intermediate",
                "sort_order": 2
            }
        ]
        
        for obj in objectives:
            db.execute(text("""
                INSERT INTO learning_objectives (
                    learning_path_id, title, description, objective_type,
                    target_skill, target_score, estimated_time_minutes,
                    difficulty_level, sort_order
                ) VALUES (
                    :learning_path_id, :title, :description, :objective_type,
                    :target_skill, :target_score, :estimated_time_minutes,
                    :difficulty_level, :sort_order
                )
            """), {
                "learning_path_id": learning_path_id,
                "title": obj["title"],
                "description": obj["description"],
                "objective_type": obj["objective_type"],
                "target_skill": obj["target_skill"],
                "target_score": obj["target_score"],
                "estimated_time_minutes": obj["estimated_time_minutes"],
                "difficulty_level": obj["difficulty_level"],
                "sort_order": obj["sort_order"]
            })
    
    # Insert sample skill mastery records
    skills = [
        ("Reading Comprehension", "reading_passage", "intermediate", 0.65),
        ("Listening Comprehension", "listening_audio", "intermediate", 0.58),
        ("Writing Skills", "writing_prompt", "elementary", 0.45),
        ("Speaking Skills", "speaking_topic", "elementary", 0.42),
        ("Grammar", "grammar_lesson", "intermediate", 0.62),
        ("Vocabulary", "vocabulary_lesson", "intermediate", 0.68)
    ]
    
    for skill_name, module_type, current_level, mastery_score in skills:
        db.execute(text("""
            INSERT INTO skill_mastery (
                user_id, skill_name, module_type, current_level, mastery_score,
                total_attempts, successful_attempts, average_score, best_score,
                total_time_spent
            ) VALUES (
                :user_id, :skill_name, :module_type, :current_level, :mastery_score,
                10, 7, 75.0, 85.0, 120
            )
        """), {
            "user_id": user_id,
            "skill_name": skill_name,
            "module_type": module_type,
            "current_level": current_level,
            "mastery_score": mastery_score
        })
    
    # Insert sample recommendations
    recommendations = [
        {
            "recommendation_type": "performance_based",
            "title": "Improve Speaking Fluency",
            "description": "Focus on speaking practice to improve your fluency score",
            "reasoning": "Your speaking score is below target",
            "confidence_score": 0.9,
            "priority_score": 0.8,
            "estimated_impact": 0.8,
            "time_to_complete": 45
        },
        {
            "recommendation_type": "content_based",
            "title": "Practice Reading Comprehension",
            "description": "Try this reading passage to improve your comprehension skills",
            "reasoning": "Similar to content you've engaged with",
            "confidence_score": 0.8,
            "priority_score": 0.7,
            "estimated_impact": 0.6,
            "time_to_complete": 30
        },
        {
            "recommendation_type": "context_aware",
            "title": "Optimal Study Time",
            "description": "This is your peak study time. Take advantage of it!",
            "reasoning": "You perform best during this time of day",
            "confidence_score": 0.7,
            "priority_score": 0.6,
            "estimated_impact": 0.7,
            "time_to_complete": 60
        }
    ]
    
    for rec in recommendations:
        db.execute(text("""
            INSERT INTO recommendations (
                user_id, recommendation_type, title, description, reasoning,
                confidence_score, priority_score, estimated_impact, time_to_complete
            ) VALUES (
                :user_id, :recommendation_type, :title, :description, :reasoning,
                :confidence_score, :priority_score, :estimated_impact, :time_to_complete
            )
        """), {
            "user_id": user_id,
            "recommendation_type": rec["recommendation_type"],
            "title": rec["title"],
            "description": rec["description"],
            "reasoning": rec["reasoning"],
            "confidence_score": rec["confidence_score"],
            "priority_score": rec["priority_score"],
            "estimated_impact": rec["estimated_impact"],
            "time_to_complete": rec["time_to_complete"]
        })
    
    # Insert sample learning analytics
    db.execute(text("""
        INSERT INTO learning_analytics (
            user_id, date, total_study_time, sessions_count, content_items_completed,
            objectives_completed, average_score, average_accuracy, engagement_score,
            focus_score, consistency_score, recommendations_generated, recommendations_accepted
        ) VALUES (
            :user_id, CURRENT_DATE, 120, 3, 5, 1, 75.5, 78.2, 0.8, 0.7, 0.6, 3, 1
        )
    """), {"user_id": user_id})
    
    db.commit()
    logger.info("Sample learning data inserted successfully")


def run_migration(db: Session):
    """Run the complete learning features migration."""
    try:
        logger.info("Starting learning features migration...")
        create_learning_tables(db)
        insert_sample_learning_data(db)
        logger.info("Learning features migration completed successfully")
    except Exception as e:
        logger.error("Learning features migration failed", error=str(e))
        db.rollback()
        raise
