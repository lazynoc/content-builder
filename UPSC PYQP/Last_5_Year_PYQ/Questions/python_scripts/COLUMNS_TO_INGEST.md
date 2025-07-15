# Columns to Ingest from Grok-Analyzed JSON

## 📊 **Complete Column Mapping**

### 🔧 **Core Question Fields (from JSON root)**
| JSON Field | Database Column | Type | Description |
|------------|----------------|------|-------------|
| `id` | `id` | UUID | Unique question identifier |
| `question_number` | `question_number` | INTEGER | Question number in exam |
| `type` | `question_type` | VARCHAR(20) | Question type (mcq, etc.) |
| `difficulty` | `difficulty` | VARCHAR(20) | Difficulty level |
| `subject` | `subject` | VARCHAR(100) | Subject area |
| `exam_info` | `exam_info` | VARCHAR(100) | Exam information |
| `question_text` | `question_text` | TEXT | The actual question |
| `options` | `options` | JSONB | Multiple choice options |
| `correct_answer` | `correct_answer` | VARCHAR(10) | Correct answer option |
| `grok_analysis_date` | `grok_analysis_date` | TIMESTAMP | When analysis was performed |

### 🎯 **Student-Facing Analysis (Frontend Display)**
| JSON Field | Database Column | Type | Description |
|------------|----------------|------|-------------|
| `student_facing_analysis.explanation` | `explanation` | TEXT | Clean answer explanation |
| `student_facing_analysis.learning_objectives` | `learning_objectives` | TEXT | What to learn from question |
| `student_facing_analysis.question_strategy` | `question_strategy` | TEXT | How UPSC designs questions |
| `student_facing_analysis.difficulty_level` | `difficulty` | VARCHAR(20) | Easy/Medium/Hard |
| `student_facing_analysis.key_concepts` | `key_concepts` | JSONB | Core concepts tested |
| `student_facing_analysis.time_management` | `time_management` | VARCHAR(100) | Recommended time |

### 🔬 **Detailed Backend Analysis (LLM Feedback)**
| JSON Field | Database Column | Type | Description |
|------------|----------------|------|-------------|
| `detailed_backend_analysis` | `detailed_analysis` | JSONB | Complete 18+ field analysis |

**Detailed Backend Analysis Fields (stored as JSONB):**
- `primary_type` - Main subject area
- `secondary_type` - Specific sub-topic
- `difficulty_reason` - Why this difficulty level
- `options_analysis` - Detailed analysis of each option
- `common_mistakes` - What students typically get wrong
- `elimination_technique` - Step-by-step elimination approach
- `memory_hooks` - Mnemonics and memory techniques
- `related_topics` - Connected subjects/topics
- `exam_strategy` - Time management and confidence assessment
- `source_material` - Recommended study sources
- `motivation` - Why this is important for UPSC
- `examiner_thought_process` - What examiner is testing
- `current_affairs_connection` - Links to current events
- `confidence_calibration` - How to assess confidence level
- `strength_indicators` - What getting it right shows
- `weakness_indicators` - What getting it wrong reveals
- `remediation_topics` - Specific topics to study if wrong
- `advanced_connections` - Links to advanced concepts

### 🏗️ **Database Schema Requirements**

**Required SQL Columns:**
```sql
-- Core fields
id UUID PRIMARY KEY,
question_number INTEGER NOT NULL,
year INTEGER NOT NULL,
exam_type VARCHAR(50) NOT NULL,
exam_stage VARCHAR(50) DEFAULT 'Prelims',
question_text TEXT NOT NULL,
question_type VARCHAR(20) DEFAULT 'mcq',
difficulty VARCHAR(20) DEFAULT 'Medium',
subject VARCHAR(100) DEFAULT 'General Studies',
topic VARCHAR(200),
options JSONB NOT NULL,
correct_answer VARCHAR(10),

-- Student-facing analysis
explanation TEXT,
learning_objectives TEXT,
question_strategy TEXT,
key_concepts JSONB,
time_management VARCHAR(100),

-- Detailed backend analysis
detailed_analysis JSONB,

-- Metadata
grok_analysis_date TIMESTAMP WITH TIME ZONE,
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

### 📈 **Data Volume**
- **2025**: 100 questions with full Grok analysis
- **2024**: 102 questions with full Grok analysis
- **Total**: 202 questions with two-tier analysis structure

### 🎯 **Usage in PAI Mentor Platform**

**Frontend Display:**
- `explanation` - Show after student answers
- `learning_objectives` - Learning section
- `question_strategy` - Strategy insights
- `key_concepts` - Concept tags
- `time_management` - Time recommendations

**Backend LLM Feedback:**
- `detailed_analysis` - Complete data for personalized feedback
- All 18+ fields for strength/weakness analysis
- Study action plans and remediation topics 