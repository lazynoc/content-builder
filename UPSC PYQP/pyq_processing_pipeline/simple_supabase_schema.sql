-- UPSC Questions Database Schema
-- This schema supports comprehensive question analysis with OpenAI insights

-- Drop table if exists (for clean setup)
DROP TABLE IF EXISTS questions CASCADE;

-- Create the main questions table
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    question_number VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    section VARCHAR(100),
    question_text TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    explanation TEXT,
    
    -- Options stored as JSON
    options JSONB,
    
    -- Question nature and analysis
    primary_type VARCHAR(50),
    secondary_type VARCHAR(50),
    difficulty_level VARCHAR(20),
    difficulty_reason TEXT,
    knowledge_requirement VARCHAR(100),
    
    -- Examiner thought process
    testing_objective TEXT,
    question_design_strategy TEXT,
    trap_setting TEXT,
    discrimination_potential TEXT,
    
    -- Options analysis (stored as JSON)
    options_analysis JSONB,
    
    -- Learning insights
    key_concepts JSONB, -- Array of concepts
    common_mistakes JSONB, -- Array of mistakes
    elimination_technique JSONB, -- Object with techniques
    memory_hooks JSONB, -- Array of memory hooks
    related_topics JSONB, -- Array of topics
    current_affairs_connection TEXT,
    
    -- Time and confidence
    time_management TEXT,
    confidence_calibration TEXT,
    
    -- Source information
    source_material TEXT,
    source_type VARCHAR(100),
    test_series_reference TEXT,
    
    -- Processing metadata
    extraction_order INTEGER,
    chunk_number INTEGER,
    tags TEXT[], -- Array of tags
    
    -- Additional fields from your data
    motivation TEXT,
    examiner_thought_process JSONB,
    learning_insights JSONB,
    openai_analysis_date TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_questions_year ON questions(year);
CREATE INDEX idx_questions_section ON questions(section);
CREATE INDEX idx_questions_difficulty ON questions(difficulty_level);
CREATE INDEX idx_questions_primary_type ON questions(primary_type);
CREATE INDEX idx_questions_number_year ON questions(question_number, year);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_questions_updated_at 
    BEFORE UPDATE ON questions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE questions IS 'UPSC Prelims questions with comprehensive analysis and insights';
COMMENT ON COLUMN questions.question_number IS 'Question number as it appears in the exam';
COMMENT ON COLUMN questions.year IS 'Year of the UPSC exam';
COMMENT ON COLUMN questions.section IS 'Subject section (e.g., Polity, Geography, etc.)';
COMMENT ON COLUMN questions.options IS 'JSON object containing options A, B, C, D';
COMMENT ON COLUMN questions.options_analysis IS 'Detailed analysis of each option with reasoning';
COMMENT ON COLUMN questions.learning_insights IS 'Comprehensive learning insights and strategies';
COMMENT ON COLUMN questions.tags IS 'Array of tags for categorization and search'; 