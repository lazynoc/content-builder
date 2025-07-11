-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Drop the old table if it exists
DROP TABLE IF EXISTS pyq_question_table CASCADE;

-- Create the new, best-of-both questions table with JSONB for list fields
CREATE TABLE pyq_question_table (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Core info
    question_number VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    section VARCHAR(100) NOT NULL,
    question_text TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    explanation TEXT,

    -- Options and analysis
    options JSONB NOT NULL, -- {"A": "...", "B": "...", ...}
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

    -- Options analysis (JSONB)
    options_analysis JSONB,

    -- Learning insights (all as JSONB for flexibility)
    key_concepts JSONB, -- ["concept1", "concept2", ...]
    common_mistakes JSONB, -- ["mistake1", "mistake2", ...]
    elimination_technique TEXT,
    memory_hooks JSONB, -- ["hook1", "hook2", ...]
    related_topics JSONB, -- ["topic1", "topic2", ...]
    current_affairs_connection TEXT,

    -- Time and confidence
    time_management TEXT,
    confidence_calibration TEXT,

    -- Metadata
    source_material TEXT,
    source_type VARCHAR(100),
    test_series_reference TEXT,
    extraction_order INTEGER,
    chunk_number INTEGER,

    -- Tags for filtering (JSONB)
    tags JSONB, -- ["tag1", "tag2", ...]

    -- Enhanced/AI fields (optional, for future-proofing)
    motivation TEXT,
    examiner_thought_process JSONB,
    learning_insights JSONB,
    openai_analysis_date TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    UNIQUE(year, question_number)
);

-- Indexes for performance
CREATE INDEX idx_pyq_questions_year ON pyq_question_table(year);
CREATE INDEX idx_pyq_questions_section ON pyq_question_table(section);
CREATE INDEX idx_pyq_questions_difficulty ON pyq_question_table(difficulty_level);
CREATE INDEX idx_pyq_questions_primary_type ON pyq_question_table(primary_type);
CREATE INDEX idx_pyq_questions_tags ON pyq_question_table USING GIN(tags);
CREATE INDEX idx_pyq_questions_options ON pyq_question_table USING GIN(options);
CREATE INDEX idx_pyq_questions_options_analysis ON pyq_question_table USING GIN(options_analysis);
CREATE INDEX idx_pyq_questions_key_concepts ON pyq_question_table USING GIN(key_concepts);
CREATE INDEX idx_pyq_questions_common_mistakes ON pyq_question_table USING GIN(common_mistakes);
CREATE INDEX idx_pyq_questions_memory_hooks ON pyq_question_table USING GIN(memory_hooks);
CREATE INDEX idx_pyq_questions_related_topics ON pyq_question_table USING GIN(related_topics);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_pyq_questions_updated_at
    BEFORE UPDATE ON pyq_question_table
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 