-- =====================================================
-- MINIMAL UPSC PYQ Questions Table Setup for Supabase
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the main questions table (basic structure)
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
    
    -- Options (stored as JSONB for flexibility)
    options JSONB NOT NULL,
    
    -- Exam-specific metadata
    exam_info VARCHAR(100),
    paper VARCHAR(50),
    section VARCHAR(50),
    
    -- Processing metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version VARCHAR(10) DEFAULT '1.0',
    source VARCHAR(100) DEFAULT 'Official',
    
    -- Basic constraints
    CONSTRAINT unique_question_per_exam UNIQUE (question_number, year, exam_type, exam_stage),
    CONSTRAINT valid_year CHECK (year >= 2000 AND year <= 2030),
    CONSTRAINT valid_question_number CHECK (question_number > 0)
);

-- Basic indexes for performance
CREATE INDEX IF NOT EXISTS idx_question_bank_year ON question_bank(year);
CREATE INDEX IF NOT EXISTS idx_question_bank_exam_type ON question_bank(exam_type);
CREATE INDEX IF NOT EXISTS idx_question_bank_year_exam_type ON question_bank(year, exam_type);

-- =====================================================
-- BASIC PERMISSIONS FOR DATA INGESTION
-- =====================================================

-- Grant permissions to the database user (for ingestion script)
GRANT ALL ON question_bank TO postgres;
GRANT USAGE ON SCHEMA public TO postgres;

-- =====================================================
-- VERIFICATION QUERY
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