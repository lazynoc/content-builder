# Supabase Setup Guide for UPSC PYQ Questions

## Overview
This guide covers setting up the Supabase database to store and serve UPSC PYQ questions for the frontend practice test environment.

## 🗄️ Database Schema

### Table: `question_bank`
Comprehensive question bank that stores questions for multiple exam types (UPSC, SSC, Banking, etc.) with proper indexing and constraints.

#### Key Features:
- **Primary Key**: `id` (UUID) - Unique identifier for each question
- **Unique Constraint**: `(question_number, year, exam_type)` - Prevents duplicate questions
- **JSONB Options**: Flexible storage for answer options
- **Future-Ready**: Reserved columns for Grok analysis results

#### Core Columns:
```sql
id UUID PRIMARY KEY                    -- Unique question identifier
question_number INTEGER NOT NULL       -- Sequential number within year
year INTEGER NOT NULL                  -- Exam year (2021-2025)
exam_type VARCHAR(50) NOT NULL         -- Exam type (UPSC, SSC, BANKING, etc.)
exam_stage VARCHAR(50) DEFAULT 'Prelims' -- Stage (Prelims, Mains, Interview)
question_text TEXT NOT NULL            -- Question content
question_type VARCHAR(20) DEFAULT 'mcq' -- Question format
difficulty VARCHAR(20) DEFAULT 'Medium' -- Easy/Medium/Hard
subject VARCHAR(100)                   -- Subject category
topic VARCHAR(200)                     -- Specific topic within subject
options JSONB NOT NULL                 -- Answer options
exam_info VARCHAR(100)                 -- Exam details
paper VARCHAR(50)                      -- Paper type
section VARCHAR(50)                    -- Section within paper
source VARCHAR(100) DEFAULT 'Official' -- Source (Official, Practice, Mock)
```

#### Future Columns (for Grok Analysis):
```sql
grok_analysis JSONB                    -- Grok analysis results
complexity_score DECIMAL(3,2)          -- Question complexity
topic_tags TEXT[]                      -- Related topics
learning_objectives TEXT[]             -- Learning goals
common_mistakes TEXT[]                 -- Typical errors
explanation TEXT                       -- Detailed explanation
related_concepts TEXT[]                -- Related concepts
```

## 🔧 Setup Instructions

### 1. Environment Variables
Add these to your `.env` file:
```bash
# Supabase Database Configuration
SUPABASE_HOST=your-project.supabase.co
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-db-password
SUPABASE_DB_PORT=5432
```

### 2. Install Dependencies
```bash
cd python_scripts
pip install -r requirements_supabase.txt
```

### 3. Create Database Schema
Run the SQL script in your Supabase SQL editor:
```bash
# Copy and paste the contents of supabase_setup.sql
# This creates the table, indexes, policies, and functions
```

### 4. Ingest Data
```bash
# Ingest all years (2021-2025)
python3 supabase_ingest.py

# Or ingest specific year
python3 supabase_ingest.py 2025
```

## 🔐 Security & Permissions

### Row Level Security (RLS)
- **Public Read**: Anyone can read questions
- **Authenticated Read**: Logged-in users can read
- **Service Role**: Full access for admin operations
- **Admin Role**: Can modify data

### Policies:
```sql
-- Public read access
CREATE POLICY "Public read access" ON upsc_pyq_questions
    FOR SELECT USING (true);

-- Authenticated users can read
CREATE POLICY "Authenticated users can read" ON upsc_pyq_questions
    FOR SELECT USING (auth.role() = 'authenticated');

-- Service role full access
CREATE POLICY "Service role full access" ON upsc_pyq_questions
    FOR ALL USING (auth.role() = 'service_role');
```

## 📊 Helper Functions

### 1. Get Questions by Year and Exam Type
```sql
SELECT * FROM get_questions_by_year_exam(2025, 'UPSC');
```

### 2. Get Questions by Subject, Year and Exam Type
```sql
SELECT * FROM get_questions_by_subject_year_exam('Economy', 2025, 'UPSC');
```

### 3. Get Random Questions for Practice
```sql
-- 10 random UPSC questions from 2025
SELECT * FROM get_random_questions(10, 'UPSC', 2025);

-- 5 random Economy questions from any year (UPSC)
SELECT * FROM get_random_questions(5, 'UPSC', NULL, 'Economy');

-- 15 random Medium difficulty questions (UPSC)
SELECT * FROM get_random_questions(15, 'UPSC', NULL, NULL, 'Medium');

-- 10 random SSC questions
SELECT * FROM get_random_questions(10, 'SSC');
```

## 🎯 Frontend Integration Examples

### 1. Fetch Questions for Practice Test
```javascript
// Get 10 random UPSC questions from 2025
const { data, error } = await supabase
  .rpc('get_random_questions', {
    num_questions: 10,
    target_exam_type: 'UPSC',
    target_year: 2025
  });
```

### 2. Get Questions by Subject
```javascript
// Get all Economy questions from 2024 (UPSC)
const { data, error } = await supabase
  .rpc('get_questions_by_subject_year_exam', {
    target_subject: 'Economy',
    target_year: 2024,
    target_exam_type: 'UPSC'
  });
```

### 3. Get Question Statistics
```javascript
// Get year-wise summary for UPSC
const { data, error } = await supabase
  .from('year_summary')
  .select('*')
  .eq('exam_type', 'UPSC');

// Get exam type summary
const { data, error } = await supabase
  .from('exam_type_summary')
  .select('*');
```

## 📈 Performance Optimizations

### Indexes Created:
- `idx_question_bank_year` - Year-based queries
- `idx_question_bank_exam_type` - Exam type-based queries
- `idx_question_bank_subject` - Subject-based queries
- `idx_question_bank_difficulty` - Difficulty-based queries
- `idx_question_bank_year_exam_type` - Combined year+exam_type queries
- `idx_question_bank_exam_type_subject` - Combined exam_type+subject queries
- `idx_question_bank_created_at` - Time-based queries

### Query Optimization Tips:
1. Use specific years when possible
2. Leverage the helper functions for common queries
3. Use JSONB operators for options filtering
4. Consider pagination for large result sets

## 🔄 Data Management

### Adding New Years:
1. Process new year JSON: `python3 process_new_year.py 2026`
2. Ingest to database: `python3 supabase_ingest.py 2026`

### Updating Existing Data:
```sql
-- Update question content
UPDATE question_bank 
SET question_text = 'Updated text'
WHERE id = 'question-uuid';

-- Update Grok analysis (future)
UPDATE question_bank 
SET grok_analysis = '{"analysis": "data"}'
WHERE id = 'question-uuid';

-- Update topic and section (after Grok analysis)
UPDATE question_bank 
SET topic = 'Specific Topic', section = 'Current Affairs'
WHERE id = 'question-uuid';
```

### Backup and Restore:
```sql
-- Export questions
COPY question_bank TO '/tmp/question_bank_backup.csv' CSV HEADER;

-- Import questions
COPY question_bank FROM '/tmp/question_bank_backup.csv' CSV HEADER;

-- Export specific exam type
COPY (SELECT * FROM question_bank WHERE exam_type = 'UPSC') 
TO '/tmp/upsc_questions_backup.csv' CSV HEADER;
```

## 🚨 Troubleshooting

### Common Issues:

1. **Connection Failed**
   - Check environment variables
   - Verify Supabase credentials
   - Ensure network connectivity

2. **Permission Denied**
   - Check RLS policies
   - Verify user role
   - Check table permissions

3. **Duplicate Key Error**
   - Question already exists
   - Check unique constraint
   - Use ON CONFLICT handling

4. **JSONB Parsing Error**
   - Validate JSON structure
   - Check options format
   - Ensure proper escaping

### Verification Queries:
```sql
-- Check table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'question_bank';

-- Check question count by exam type and year
SELECT exam_type, year, COUNT(*) as count 
FROM question_bank 
GROUP BY exam_type, year 
ORDER BY exam_type, year;

-- Check for duplicates
SELECT question_number, year, exam_type, COUNT(*) 
FROM question_bank 
GROUP BY question_number, year, exam_type 
HAVING COUNT(*) > 1;

-- Check exam type summary
SELECT * FROM exam_type_summary;
```

## 📋 Next Steps

### Phase 1: Basic Setup ✅
- [x] Create database schema
- [x] Set up security policies
- [x] Ingest existing data (2021-2025)
- [x] Create helper functions

### Phase 2: Frontend Integration
- [ ] Test API endpoints
- [ ] Implement question fetching
- [ ] Add pagination
- [ ] Create practice test interface

### Phase 3: Grok Analysis Integration
- [ ] Add Grok analysis columns
- [ ] Process questions with Grok
- [ ] Store analysis results
- [ ] Implement micro-analysis features

### Phase 4: Advanced Features
- [ ] Question difficulty calibration
- [ ] User performance tracking
- [ ] Adaptive testing
- [ ] Analytics dashboard

---
*Last Updated: July 13, 2025*
*Total Questions Ready: 522*
*Database: Supabase PostgreSQL* 