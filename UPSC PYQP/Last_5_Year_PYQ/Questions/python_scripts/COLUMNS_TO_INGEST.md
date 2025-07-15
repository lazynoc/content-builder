# Columns to Ingest from Enhanced OpenAI Analysis

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
| `openai_analysis_date` | `openai_analysis_date` | TIMESTAMP | When analysis was performed |

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
| `detailed_backend_analysis` | `detailed_analysis` | JSONB | Complete micro-level analysis |

**Detailed Backend Analysis Fields (stored as JSONB):**

#### 📋 **Question Nature**
- `question_nature.primary_type` - Factual/Conceptual/Analytical/Application
- `question_nature.secondary_type` - Memory-based/Understanding-based/Application-based
- `question_nature.difficulty_reason` - Why this difficulty level
- `question_nature.knowledge_requirement` - Static/current affairs/mixed

#### 🧠 **Examiner Thought Process**
- `examiner_thought_process.testing_objective` - What examiner is testing
- `examiner_thought_process.question_design_strategy` - How question is designed
- `examiner_thought_process.trap_setting` - Traps or misleading elements
- `examiner_thought_process.discrimination_potential` - How well it differentiates candidates

#### 🎯 **Micro-Level Options Analysis**
- `options_analysis.A.type` - correct_answer/plausible_distractor/obvious_wrong
- `options_analysis.A.reason` - Why this option is correct/incorrect
- `options_analysis.A.trap` - What trap it sets (if distractor)
- `options_analysis.A.elimination_strategy` - How to eliminate this option
- `options_analysis.A.student_reasoning_pattern` - What choosing A reveals about thinking
- `options_analysis.A.common_misconception` - Misconception leading to this choice
- *(Same structure for B, C, D)*

#### 📚 **Learning Insights**
- `learning_insights.key_concepts` - Key concepts tested
- `learning_insights.common_mistakes` - Common student mistakes
- `learning_insights.elimination_technique_semi_knowledge` - Strategy with partial knowledge
- `learning_insights.elimination_technique_safe_guess` - Strategy with no knowledge
- `learning_insights.memory_hooks` - Mnemonics and memory aids
- `learning_insights.related_topics` - Related topics for study
- `learning_insights.current_affairs_connection` - Links to current events

#### 📊 **Assessment & Strategy**
- `difficulty_level` - Easy/Medium/Difficult
- `time_management` - Recommended time allocation
- `confidence_calibration` - How confident should student be
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

-- Detailed backend analysis (enhanced)
detailed_analysis JSONB,

-- Metadata
openai_analysis_date TIMESTAMP WITH TIME ZONE,
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

### 📈 **Data Volume**
- **2025**: 100 questions with micro-level analysis
- **Total**: 100 questions with enhanced two-tier analysis structure

### 🎯 **Usage in PAI Mentor Platform**

**Frontend Display:**
- `explanation` - Show after student answers
- `learning_objectives` - Learning section
- `question_strategy` - Strategy insights
- `key_concepts` - Concept tags
- `time_management` - Time recommendations

**Backend LLM Feedback (Enhanced):**
- `detailed_analysis.options_analysis` - Micro-level option analysis
- `detailed_analysis.student_reasoning_pattern` - Personalized feedback based on choice
- `detailed_analysis.elimination_technique_semi_knowledge` - Strategy for partial knowledge
- `detailed_analysis.elimination_technique_safe_guess` - Strategy for no knowledge
- All detailed fields for comprehensive personalized feedback

### 🚀 **Key Advantages of This Structure**

1. **Micro-Level Option Analysis**: Each option choice reveals specific reasoning patterns
2. **Personalized Feedback**: Different feedback for A vs B vs C vs D choices
3. **Strategy-Based Learning**: Specific elimination techniques for different knowledge levels
4. **Examiner Mindset**: Understanding what UPSC is testing
5. **Comprehensive Remediation**: Targeted study suggestions based on specific mistakes 