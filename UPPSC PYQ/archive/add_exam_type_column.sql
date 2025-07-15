-- Add exam_type column to pyq_question_table
ALTER TABLE public.pyq_question_table 
ADD COLUMN exam_type character varying(50) NOT NULL DEFAULT 'UPSC';

-- Create index for exam_type
CREATE INDEX IF NOT EXISTS idx_pyq_questions_exam_type 
ON public.pyq_question_table USING btree (exam_type) TABLESPACE pg_default;

-- Update existing records to have exam_type = 'UPSC' (if any exist)
UPDATE public.pyq_question_table 
SET exam_type = 'UPSC' 
WHERE exam_type IS NULL; 