-- =====================================================
-- UPDATED UPSC PYQ Questions Table Setup for Supabase
-- Includes Grok Analysis Columns
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the main questions table (updated structure with Grok analysis)
CREATE TABLE IF NOT EXISTS question_bank (
    -- Primary identifier (UUID from our JSON)
    id UUID PRIMARY KEY,
    
    -- Core identification fields
    question_number INTEGER NOT NULL,
    year INTEGER NOT NULL,
    exam_type VARCHAR(50) NOT NULL,
    exam_stage VARCHAR(50) DEFAULT 'Prelims',
    
    -- Question content
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) DEFAULT 'mcq',
    difficulty VARCHAR(20) DEFAULT 'Medium',
    subject VARCHAR(100) DEFAULT 'General Studies',
    topic VARCHAR(200),
    
    -- Options and correct answer
    options JSONB NOT NULL,
    correct_answer VARCHAR(10),
    
    -- Exam-specific metadata
    exam_info VARCHAR(100),
    paper VARCHAR(50),
    section VARCHAR(50),
    
    -- Student-facing analysis (for frontend display)
    explanation TEXT,
    learning_objectives TEXT,
    question_strategy TEXT,
    key_concepts JSONB,
    time_management VARCHAR(100),
    
    -- Detailed backend analysis (for LLM feedback)
    detailed_analysis JSONB,
    
    -- Processing metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    grok_analysis_date TIMESTAMP WITH TIME ZONE,
    version VARCHAR(10) DEFAULT '1.0',
    source VARCHAR(100) DEFAULT 'Official',
    
    -- Basic constraints
    CONSTRAINT unique_question_per_exam UNIQUE (question_number, year, exam_type, exam_stage),
    CONSTRAINT valid_year CHECK (year >= 2000 AND year <= 2030),
    CONSTRAINT valid_question_number CHECK (question_number > 0)
);

-- Add columns if they don't exist (for existing tables)
DO $$ 
BEGIN
    -- Add correct_answer column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'question_bank' AND column_name = 'correct_answer') THEN
        ALTER TABLE question_bank ADD COLUMN correct_answer VARCHAR(10);
    END IF;
    
    -- Add explanation column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'question_bank' AND column_name = 'explanation') THEN
        ALTER TABLE question_bank ADD COLUMN explanation TEXT;
    END IF;
    
    -- Add learning_objectives column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'question_bank' AND column_name = 'learning_objectives') THEN
        ALTER TABLE question_bank ADD COLUMN learning_objectives TEXT;
    END IF;
    
    -- Add question_strategy column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'question_bank' AND column_name = 'question_strategy') THEN
        ALTER TABLE question_bank ADD COLUMN question_strategy TEXT;
    END IF;
    
    -- Add key_concepts column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'question_bank' AND column_name = 'key_concepts') THEN
        ALTER TABLE question_bank ADD COLUMN key_concepts JSONB;
    END IF;
    
    -- Add time_management column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'question_bank' AND column_name = 'time_management') THEN
        ALTER TABLE question_bank ADD COLUMN time_management VARCHAR(100);
    END IF;
    
    -- Add detailed_analysis column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'question_bank' AND column_name = 'detailed_analysis') THEN
        ALTER TABLE question_bank ADD COLUMN detailed_analysis JSONB;
    END IF;
    
    -- Add grok_analysis_date column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'question_bank' AND column_name = 'grok_analysis_date') THEN
        ALTER TABLE question_bank ADD COLUMN grok_analysis_date TIMESTAMP WITH TIME ZONE;
    END IF;
    
END $$;

-- Enhanced indexes for performance (including new columns)
CREATE INDEX IF NOT EXISTS idx_question_bank_year ON question_bank(year);
CREATE INDEX IF NOT EXISTS idx_question_bank_exam_type ON question_bank(exam_type);
CREATE INDEX IF NOT EXISTS idx_question_bank_year_exam_type ON question_bank(year, exam_type);
CREATE INDEX IF NOT EXISTS idx_question_bank_subject ON question_bank(subject);
CREATE INDEX IF NOT EXISTS idx_question_bank_difficulty ON question_bank(difficulty);
CREATE INDEX IF NOT EXISTS idx_question_bank_grok_analysis_date ON question_bank(grok_analysis_date);

-- Index for JSONB columns
CREATE INDEX IF NOT EXISTS idx_question_bank_options_gin ON question_bank USING GIN (options);
CREATE INDEX IF NOT EXISTS idx_question_bank_key_concepts_gin ON question_bank USING GIN (key_concepts);
CREATE INDEX IF NOT EXISTS idx_question_bank_detailed_analysis_gin ON question_bank USING GIN (detailed_analysis);

-- =====================================================
-- PERMISSIONS FOR DATA INGESTION
-- =====================================================

-- Grant permissions to the database user (for ingestion script)
GRANT ALL ON question_bank TO postgres;
GRANT USAGE ON SCHEMA public TO postgres;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check if table was created successfully with all columns
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'question_bank'
ORDER BY ordinal_position;

-- Check if Grok analysis columns exist
SELECT 
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_name = 'question_bank' 
AND column_name IN ('explanation', 'learning_objectives', 'question_strategy', 'key_concepts', 'time_management', 'detailed_analysis', 'grok_analysis_date')
ORDER BY column_name;

-- =====================================================
-- SAMPLE QUERIES FOR TESTING
-- =====================================================

-- Count questions with Grok analysis
-- SELECT COUNT(*) as total_questions,
--        COUNT(CASE WHEN explanation IS NOT NULL AND explanation != '' THEN 1 END) as with_explanation,
--        COUNT(CASE WHEN detailed_analysis IS NOT NULL THEN 1 END) as with_detailed_analysis
-- FROM question_bank 
-- WHERE exam_type = 'UPSC';

-- Get sample question with analysis
-- SELECT question_number, year, question_text, explanation, learning_objectives
-- FROM question_bank 
-- WHERE exam_type = 'UPSC' AND explanation IS NOT NULL
-- LIMIT 5; 