-- =====================================================
-- ADD GROK ANALYSIS COLUMNS TO EXISTING TABLE
-- Based on current schema analysis
-- =====================================================

-- Add missing columns for Grok analysis
ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS correct_answer VARCHAR(10);
ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS explanation TEXT;
ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS learning_objectives TEXT;
ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS question_strategy TEXT;
ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS key_concepts JSONB;
ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS time_management VARCHAR(100);
ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS detailed_analysis JSONB;
ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS grok_analysis_date TIMESTAMP WITH TIME ZONE;

-- Add indexes for new columns
CREATE INDEX IF NOT EXISTS idx_question_bank_grok_analysis_date ON question_bank(grok_analysis_date);
CREATE INDEX IF NOT EXISTS idx_question_bank_key_concepts_gin ON question_bank USING GIN (key_concepts);
CREATE INDEX IF NOT EXISTS idx_question_bank_detailed_analysis_gin ON question_bank USING GIN (detailed_analysis);

-- Verify the new columns were added
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'question_bank' 
AND column_name IN ('correct_answer', 'explanation', 'learning_objectives', 'question_strategy', 'key_concepts', 'time_management', 'detailed_analysis', 'grok_analysis_date')
ORDER BY column_name; 