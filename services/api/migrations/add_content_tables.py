"""Add content management tables to the database."""

from sqlalchemy import text
from sqlalchemy.orm import Session
import structlog

logger = structlog.get_logger(__name__)


def create_content_tables(db: Session):
    """Create all content management tables."""
    
    # Create content_categories table
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS content_categories (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            parent_category_id UUID REFERENCES content_categories(id),
            color VARCHAR(7),
            icon VARCHAR(50),
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """))
    
    # Create content_items table
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS content_items (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(255) NOT NULL,
            content_type VARCHAR(50) NOT NULL,
            difficulty_level VARCHAR(50) NOT NULL,
            status VARCHAR(50) DEFAULT 'draft',
            content_text TEXT,
            audio_url VARCHAR(500),
            audio_duration INTEGER,
            transcript TEXT,
            prompt TEXT,
            sample_answer TEXT,
            vocabulary_list JSONB,
            grammar_points JSONB,
            tags JSONB,
            estimated_time INTEGER,
            word_count INTEGER,
            target_band_score NUMERIC(3,1),
            category_id UUID REFERENCES content_categories(id),
            created_by_id UUID NOT NULL REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            published_at TIMESTAMP WITH TIME ZONE
        )
    """))
    
    # Create content_questions table
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS content_questions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            content_item_id UUID NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
            question_text TEXT NOT NULL,
            question_type VARCHAR(50) NOT NULL,
            correct_answer TEXT NOT NULL,
            options JSONB,
            explanation TEXT,
            difficulty_level VARCHAR(50) NOT NULL,
            points INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """))
    
    # Create content_usage table
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS content_usage (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            content_item_id UUID NOT NULL REFERENCES content_items(id),
            user_id UUID NOT NULL REFERENCES users(id),
            session_id VARCHAR(100),
            time_spent INTEGER,
            completion_rate NUMERIC(5,2),
            score NUMERIC(5,2),
            questions_attempted INTEGER,
            questions_correct INTEGER,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            feedback TEXT,
            difficulty_rating INTEGER CHECK (difficulty_rating >= 1 AND difficulty_rating <= 5),
            accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE
        )
    """))
    
    # Create content_analytics table
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS content_analytics (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            content_item_id UUID NOT NULL REFERENCES content_items(id),
            date DATE NOT NULL,
            total_views INTEGER DEFAULT 0,
            total_completions INTEGER DEFAULT 0,
            average_time_spent NUMERIC(10,2),
            average_score NUMERIC(5,2),
            average_rating NUMERIC(3,2),
            completion_rate NUMERIC(5,2),
            difficulty_rating_avg NUMERIC(3,2),
            difficulty_rating_count INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(content_item_id, date)
        )
    """))
    
    # Create indexes for better performance
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_content_items_category ON content_items(category_id)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_content_items_created_by ON content_items(created_by_id)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_content_items_status ON content_items(status)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_content_items_type ON content_items(content_type)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_content_items_difficulty ON content_items(difficulty_level)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_content_questions_content ON content_questions(content_item_id)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_content_usage_content ON content_usage(content_item_id)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_content_usage_user ON content_usage(user_id)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_content_usage_accessed ON content_usage(accessed_at)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_content_analytics_content ON content_analytics(content_item_id)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_content_analytics_date ON content_analytics(date)"))
    
    db.commit()
    logger.info("Content management tables created successfully")


def insert_sample_content_data(db: Session):
    """Insert sample content data for testing."""
    
    # Insert sample categories
    db.execute(text("""
        INSERT INTO content_categories (name, description, color, icon, sort_order)
        VALUES 
            ('Academic Reading', 'Academic reading passages and questions', '#3B82F6', 'book-open', 1),
            ('General Reading', 'General reading passages and questions', '#10B981', 'newspaper', 2),
            ('Listening', 'Audio content and listening exercises', '#F59E0B', 'headphones', 3),
            ('Writing', 'Writing prompts and sample answers', '#8B5CF6', 'pen-tool', 4),
            ('Speaking', 'Speaking topics and sample responses', '#EF4444', 'mic', 5),
            ('Grammar', 'Grammar lessons and exercises', '#06B6D4', 'code', 6),
            ('Vocabulary', 'Vocabulary lessons and word lists', '#84CC16', 'bookmark', 7)
        ON CONFLICT (name) DO NOTHING
    """))
    
    # Get category IDs
    result = db.execute(text("SELECT id, name FROM content_categories LIMIT 7"))
    categories = {row[1]: row[0] for row in result.fetchall()}
    
    # Insert sample content items
    db.execute(text("""
        INSERT INTO content_items (title, content_type, difficulty_level, content_text, category_id, created_by_id, status)
        VALUES 
            ('Academic Reading: Climate Change', 'reading_passage', 'intermediate', 
             'Climate change is one of the most pressing issues facing humanity today...', 
             :academic_id, :user_id, 'published'),
            ('Listening: University Lecture', 'listening_audio', 'intermediate', 
             'In today''s lecture, we will discuss the impact of technology on modern society...', 
             :listening_id, :user_id, 'published'),
            ('Writing Task 2: Technology', 'writing_prompt', 'intermediate', 
             'Some people believe that technology has made life more complex, while others argue that it has simplified our lives. Discuss both views and give your opinion.', 
             :writing_id, :user_id, 'published'),
            ('Speaking: Hometown', 'speaking_topic', 'beginner', 
             'Describe your hometown. What is it like? What are the main attractions?', 
             :speaking_id, :user_id, 'published'),
            ('Grammar: Present Perfect', 'grammar_lesson', 'elementary', 
             'The present perfect tense is used to describe actions that started in the past and continue to the present...', 
             :grammar_id, :user_id, 'published'),
            ('Vocabulary: Academic Words', 'vocabulary_lesson', 'intermediate', 
             'This lesson covers essential academic vocabulary for IELTS...', 
             :vocab_id, :user_id, 'published')
        ON CONFLICT DO NOTHING
    """), {
        'academic_id': categories.get('Academic Reading'),
        'listening_id': categories.get('Listening'),
        'writing_id': categories.get('Writing'),
        'speaking_id': categories.get('Speaking'),
        'grammar_id': categories.get('Grammar'),
        'vocab_id': categories.get('Vocabulary'),
        'user_id': None  # Will be set to actual user ID
    })
    
    # Get a user ID for the content
    result = db.execute(text("SELECT id FROM users LIMIT 1"))
    user_row = result.fetchone()
    user_id = user_row[0] if user_row else None
    
    if user_id:
        # Update content items with user ID
        db.execute(text("""
            UPDATE content_items 
            SET created_by_id = :user_id 
            WHERE created_by_id IS NULL
        """), {'user_id': user_id})
        
        # Get content item IDs
        result = db.execute(text("SELECT id FROM content_items LIMIT 6"))
        content_ids = [row[0] for row in result.fetchall()]
        
        # Insert sample questions for reading content
        if content_ids:
            db.execute(text("""
                INSERT INTO content_questions (content_item_id, question_text, question_type, correct_answer, options, difficulty_level)
                VALUES 
                    (:content_id, 'What is the main topic of this passage?', 'multiple_choice', 'Climate change', 
                     '["Climate change", "Technology", "Education", "Health"]', 'intermediate'),
                    (:content_id, 'According to the passage, climate change is...', 'multiple_choice', 'a pressing issue', 
                     '["a minor concern", "a pressing issue", "not important", "solved"]', 'intermediate'),
                    (:content_id, 'The author suggests that climate change affects...', 'multiple_choice', 'humanity', 
                     '["only animals", "only plants", "humanity", "only oceans"]', 'intermediate')
                ON CONFLICT DO NOTHING
            """), {'content_id': content_ids[0] if content_ids else None})
    
    db.commit()
    logger.info("Sample content data inserted successfully")


def run_migration(db: Session):
    """Run the complete content management migration."""
    try:
        logger.info("Starting content management migration...")
        create_content_tables(db)
        insert_sample_content_data(db)
        logger.info("Content management migration completed successfully")
    except Exception as e:
        logger.error("Content management migration failed", error=str(e))
        db.rollback()
        raise
