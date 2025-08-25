-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    target_score DECIMAL(3,1),
    current_level VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create speaking_sessions table
CREATE TABLE IF NOT EXISTS speaking_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    question_id VARCHAR(255) NOT NULL,
    transcript TEXT NOT NULL,
    audio_url TEXT,
    score DECIMAL(3,1),
    feedback JSONB,
    duration INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create writing_submissions table
CREATE TABLE IF NOT EXISTS writing_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    prompt_id VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    score DECIMAL(3,1),
    feedback JSONB,
    suggestions TEXT[],
    image_url TEXT,
    duration INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create reading_tests table
CREATE TABLE IF NOT EXISTS reading_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    test_id VARCHAR(255) NOT NULL,
    score DECIMAL(3,1) NOT NULL,
    correct_answers INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    duration INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create listening_tests table
CREATE TABLE IF NOT EXISTS listening_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    test_id VARCHAR(255) NOT NULL,
    score DECIMAL(3,1) NOT NULL,
    correct_answers INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    duration INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_progress table
CREATE TABLE IF NOT EXISTS user_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    skill VARCHAR(50) NOT NULL,
    current_score DECIMAL(3,1) NOT NULL,
    target_score DECIMAL(3,1) NOT NULL,
    improvement DECIMAL(3,1) DEFAULT 0,
    last_practice TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, skill)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_speaking_sessions_user_id ON speaking_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_speaking_sessions_created_at ON speaking_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_writing_submissions_user_id ON writing_submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_writing_submissions_created_at ON writing_submissions(created_at);
CREATE INDEX IF NOT EXISTS idx_reading_tests_user_id ON reading_tests(user_id);
CREATE INDEX IF NOT EXISTS idx_reading_tests_created_at ON reading_tests(created_at);
CREATE INDEX IF NOT EXISTS idx_listening_tests_user_id ON listening_tests(user_id);
CREATE INDEX IF NOT EXISTS idx_listening_tests_created_at ON listening_tests(created_at);
CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_progress_updated_at BEFORE UPDATE ON user_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE speaking_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE writing_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE reading_tests ENABLE ROW LEVEL SECURITY;
ALTER TABLE listening_tests ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_progress ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only access their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Speaking sessions policies
CREATE POLICY "Users can view own speaking sessions" ON speaking_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own speaking sessions" ON speaking_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own speaking sessions" ON speaking_sessions
    FOR UPDATE USING (auth.uid() = user_id);

-- Writing submissions policies
CREATE POLICY "Users can view own writing submissions" ON writing_submissions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own writing submissions" ON writing_submissions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own writing submissions" ON writing_submissions
    FOR UPDATE USING (auth.uid() = user_id);

-- Reading tests policies
CREATE POLICY "Users can view own reading tests" ON reading_tests
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own reading tests" ON reading_tests
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Listening tests policies
CREATE POLICY "Users can view own listening tests" ON listening_tests
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own listening tests" ON listening_tests
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- User progress policies
CREATE POLICY "Users can view own progress" ON user_progress
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own progress" ON user_progress
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own progress" ON user_progress
    FOR UPDATE USING (auth.uid() = user_id);

-- Create storage bucket for audio files
INSERT INTO storage.buckets (id, name, public) 
VALUES ('audio-recordings', 'audio-recordings', true)
ON CONFLICT (id) DO NOTHING;

-- Create storage bucket for writing images
INSERT INTO storage.buckets (id, name, public) 
VALUES ('writing-images', 'writing-images', true)
ON CONFLICT (id) DO NOTHING;

-- Storage policies for audio recordings
CREATE POLICY "Users can upload own audio recordings" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'audio-recordings' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can view own audio recordings" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'audio-recordings' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Storage policies for writing images
CREATE POLICY "Users can upload own writing images" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'writing-images' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can view own writing images" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'writing-images' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );
