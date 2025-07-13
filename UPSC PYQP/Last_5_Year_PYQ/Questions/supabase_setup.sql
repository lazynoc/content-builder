-- =====================================================
-- UPSC PYQ Questions Table Setup for Supabase
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create the main questions table (generic for all exam types)
CREATE TABLE IF NOT EXISTS question_bank (
    -- Primary identifier (UUID from our JSON)
    id UUID PRIMARY KEY,
    
    -- Core identification fields (unique constraint combination)
    question_number INTEGER NOT NULL,
    year INTEGER NOT NULL,
    exam_type VARCHAR(50) NOT NULL,
    exam_stage VARCHAR(50) DEFAULT 'Prelims', -- Prelims, Mains, Interview, etc.
    
    -- Question content
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) DEFAULT 'mcq',
    difficulty VARCHAR(20) DEFAULT 'Medium',
    subject VARCHAR(100) DEFAULT 'General Studies',
    topic VARCHAR(200), -- More specific topic within subject
    
    -- Options (stored as JSONB for flexibility)
    options JSONB NOT NULL,
    
    -- Exam-specific metadata
    exam_info VARCHAR(100), -- e.g., "Prelims 2025", "Mains GS1 2024"
    paper VARCHAR(50), -- e.g., "General Studies Paper I", "Quantitative Aptitude"
    section VARCHAR(50), -- e.g., "Current Affairs", "Reasoning"
    
    -- Processing metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version VARCHAR(10) DEFAULT '1.0',
    source VARCHAR(100) DEFAULT 'Official', -- Official, Practice, Mock, etc.
    
    -- Future columns for Grok analysis (commented for now)
    -- grok_analysis JSONB,
    -- complexity_score DECIMAL(3,2),
    -- topic_tags TEXT[],
    -- learning_objectives TEXT[],
    -- common_mistakes TEXT[],
    -- explanation TEXT,
    -- related_concepts TEXT[],
    -- correct_answer VARCHAR(10), -- A, B, C, D
    -- answer_explanation TEXT,
    
    -- Constraints
    CONSTRAINT unique_question_per_exam UNIQUE (question_number, year, exam_type, exam_stage),
    CONSTRAINT valid_year CHECK (year >= 2000 AND year <= 2030),
    CONSTRAINT valid_question_number CHECK (question_number > 0),
    CONSTRAINT valid_difficulty CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    CONSTRAINT valid_question_type CHECK (question_type IN ('mcq', 'table_mcq', 'list_mcq', 'match_mcq', 'fill_blank', 'true_false')),
    CONSTRAINT valid_exam_type CHECK (exam_type IN ('UPSC', 'SSC', 'BANKING', 'CAT', 'GATE', 'NEET', 'JEE', 'CUSTOM'))
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_question_bank_year ON question_bank(year);
CREATE INDEX IF NOT EXISTS idx_question_bank_exam_type ON question_bank(exam_type);
CREATE INDEX IF NOT EXISTS idx_question_bank_subject ON question_bank(subject);
CREATE INDEX IF NOT EXISTS idx_question_bank_difficulty ON question_bank(difficulty);
CREATE INDEX IF NOT EXISTS idx_question_bank_year_exam_type ON question_bank(year, exam_type);
CREATE INDEX IF NOT EXISTS idx_question_bank_exam_type_subject ON question_bank(exam_type, subject);
CREATE INDEX IF NOT EXISTS idx_question_bank_created_at ON question_bank(created_at);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_question_bank_updated_at 
    BEFORE UPDATE ON question_bank 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- ROW LEVEL SECURITY (RLS) SETUP
-- =====================================================

-- Enable RLS on the table
ALTER TABLE question_bank ENABLE ROW LEVEL SECURITY;

-- Create policies for different access levels

-- 1. Public read access (anyone can read questions)
CREATE POLICY "Public read access" ON question_bank
    FOR SELECT USING (true);

-- 2. Authenticated users can read questions
CREATE POLICY "Authenticated users can read" ON question_bank
    FOR SELECT USING (auth.role() = 'authenticated');

-- 3. Service role can do everything (for admin operations)
CREATE POLICY "Service role full access" ON question_bank
    FOR ALL USING (auth.role() = 'service_role');

-- 4. Admin users can insert/update/delete
CREATE POLICY "Admin users can modify" ON question_bank
    FOR ALL USING (auth.role() = 'authenticated' AND auth.jwt() ->> 'role' = 'admin');

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to get questions by year and exam type
CREATE OR REPLACE FUNCTION get_questions_by_year_exam(target_year INTEGER, target_exam_type VARCHAR(50))
RETURNS TABLE (
    id UUID,
    question_number INTEGER,
    question_text TEXT,
    question_type VARCHAR(20),
    difficulty VARCHAR(20),
    subject VARCHAR(100),
    options JSONB,
    exam_info VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        q.id,
        q.question_number,
        q.question_text,
        q.question_type,
        q.difficulty,
        q.subject,
        q.options,
        q.exam_info
    FROM question_bank q
    WHERE q.year = target_year AND q.exam_type = target_exam_type
    ORDER BY q.question_number;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get questions by subject, year and exam type
CREATE OR REPLACE FUNCTION get_questions_by_subject_year_exam(target_subject VARCHAR(100), target_year INTEGER, target_exam_type VARCHAR(50))
RETURNS TABLE (
    id UUID,
    question_number INTEGER,
    question_text TEXT,
    question_type VARCHAR(20),
    difficulty VARCHAR(20),
    options JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        q.id,
        q.question_number,
        q.question_text,
        q.question_type,
        q.difficulty,
        q.options
    FROM question_bank q
    WHERE q.subject ILIKE '%' || target_subject || '%' 
      AND q.year = target_year
      AND q.exam_type = target_exam_type
    ORDER BY q.question_number;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get random questions for practice
CREATE OR REPLACE FUNCTION get_random_questions(
    num_questions INTEGER DEFAULT 10,
    target_exam_type VARCHAR(50) DEFAULT 'UPSC',
    target_year INTEGER DEFAULT NULL,
    target_subject VARCHAR(100) DEFAULT NULL,
    target_difficulty VARCHAR(20) DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    question_number INTEGER,
    year INTEGER,
    exam_type VARCHAR(50),
    question_text TEXT,
    question_type VARCHAR(20),
    difficulty VARCHAR(20),
    subject VARCHAR(100),
    options JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        q.id,
        q.question_number,
        q.year,
        q.exam_type,
        q.question_text,
        q.question_type,
        q.difficulty,
        q.subject,
        q.options
    FROM question_bank q
    WHERE q.exam_type = target_exam_type
      AND (target_year IS NULL OR q.year = target_year)
      AND (target_subject IS NULL OR q.subject ILIKE '%' || target_subject || '%')
      AND (target_difficulty IS NULL OR q.difficulty = target_difficulty)
    ORDER BY RANDOM()
    LIMIT num_questions;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- View for question statistics
CREATE OR REPLACE VIEW question_statistics AS
SELECT 
    exam_type,
    year,
    subject,
    difficulty,
    question_type,
    COUNT(*) as question_count
FROM question_bank
GROUP BY exam_type, year, subject, difficulty, question_type
ORDER BY exam_type, year DESC, subject, difficulty;

-- View for year-wise summary
CREATE OR REPLACE VIEW year_summary AS
SELECT 
    exam_type,
    year,
    COUNT(*) as total_questions,
    COUNT(DISTINCT subject) as subjects_covered,
    COUNT(CASE WHEN difficulty = 'Easy' THEN 1 END) as easy_questions,
    COUNT(CASE WHEN difficulty = 'Medium' THEN 1 END) as medium_questions,
    COUNT(CASE WHEN difficulty = 'Hard' THEN 1 END) as hard_questions
FROM question_bank
GROUP BY exam_type, year
ORDER BY exam_type, year DESC;

-- View for exam type summary
CREATE OR REPLACE VIEW exam_type_summary AS
SELECT 
    exam_type,
    COUNT(*) as total_questions,
    COUNT(DISTINCT year) as years_covered,
    COUNT(DISTINCT subject) as subjects_covered,
    MIN(year) as earliest_year,
    MAX(year) as latest_year
FROM question_bank
GROUP BY exam_type
ORDER BY total_questions DESC;

-- =====================================================
-- SAMPLE DATA INSERTION (for testing)
-- =====================================================

-- Insert a sample question for testing
INSERT INTO question_bank (
    id,
    question_number,
    year,
    exam_type,
    exam_stage,
    question_text,
    question_type,
    difficulty,
    subject,
    topic,
    options,
    exam_info,
    paper,
    section,
    source
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    1,
    2025,
    'UPSC',
    'Prelims',
    'Sample question for testing database setup',
    'mcq',
    'Medium',
    'General Studies',
    'Current Affairs',
    '[
        {"letter": "A", "text": "Option A"},
        {"letter": "B", "text": "Option B"},
        {"letter": "C", "text": "Option C"},
        {"letter": "D", "text": "Option D"}
    ]'::jsonb,
    'Prelims 2025',
    'General Studies Paper I',
    'Current Affairs',
    'Official'
) ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- COMMENTS AND DOCUMENTATION
-- =====================================================

COMMENT ON TABLE question_bank IS 'Comprehensive question bank supporting multiple exam types (UPSC, SSC, Banking, etc.)';
COMMENT ON COLUMN question_bank.id IS 'Unique UUID identifier for each question';
COMMENT ON COLUMN question_bank.question_number IS 'Sequential question number within the year and exam type';
COMMENT ON COLUMN question_bank.year IS 'Year of the exam';
COMMENT ON COLUMN question_bank.exam_type IS 'Type of exam (UPSC, SSC, BANKING, CAT, etc.)';
COMMENT ON COLUMN question_bank.exam_stage IS 'Stage of exam (Prelims, Mains, Interview, etc.)';
COMMENT ON COLUMN question_bank.topic IS 'Specific topic within the subject';
COMMENT ON COLUMN question_bank.options IS 'JSONB array of answer options with letter and text';
COMMENT ON COLUMN question_bank.section IS 'Section within the paper (Current Affairs, Reasoning, etc.)';
COMMENT ON COLUMN question_bank.source IS 'Source of question (Official, Practice, Mock, etc.)';
COMMENT ON COLUMN question_bank.grok_analysis IS 'Future: Grok analysis results for micro-analysis';

-- =====================================================
-- GRANTS AND PERMISSIONS
-- =====================================================

-- Grant necessary permissions to authenticated users
GRANT SELECT ON question_bank TO authenticated;
GRANT SELECT ON question_statistics TO authenticated;
GRANT SELECT ON year_summary TO authenticated;
GRANT SELECT ON exam_type_summary TO authenticated;
GRANT EXECUTE ON FUNCTION get_questions_by_year_exam(INTEGER, VARCHAR(50)) TO authenticated;
GRANT EXECUTE ON FUNCTION get_questions_by_subject_year_exam(VARCHAR(100), INTEGER, VARCHAR(50)) TO authenticated;
GRANT EXECUTE ON FUNCTION get_random_questions(INTEGER, VARCHAR(50), INTEGER, VARCHAR(100), VARCHAR(20)) TO authenticated;

-- Grant full access to service role
GRANT ALL ON question_bank TO service_role;
GRANT ALL ON question_statistics TO service_role;
GRANT ALL ON year_summary TO service_role;
GRANT ALL ON exam_type_summary TO service_role;

-- Grant usage on sequences if any
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check if table was created successfully
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'question_bank'
ORDER BY ordinal_position;

-- Check if policies are in place
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies 
WHERE tablename = 'question_bank';

-- Check if indexes are created
SELECT 
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename = 'question_bank'; 