# UPSC 2025 Grok Analysis

This directory contains scripts to analyze UPSC 2025 Prelims questions using Grok AI for comprehensive insights.

## Files

- `grok_analysis_upsc_2025.py` - Main analysis script
- `test_grok_setup.py` - Test script to verify setup
- `requirements_grok.txt` - Python dependencies
- `README_GROK_ANALYSIS.md` - This file

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements_grok.txt
```

### 2. Environment Variables

Create or update your `.env` file in the project root with:

```
GROK_API_KEY=your_grok_api_key_here
```

### 3. Test Setup

Run the test script to verify everything is working:

```bash
python test_grok_setup.py
```

This will test:
- API key availability
- Input file accessibility
- Single question analysis

### 4. Run Full Analysis

Once tests pass, run the full analysis:

```bash
python grok_analysis_upsc_2025.py
```

## Input/Output

- **Input**: `../json_files/upsc_prelims_2025_with_answers.json`
- **Output**: `../json_files/upsc_prelims_2025_grok_analyzed.json`

## Analysis Fields

The script adds 18 comprehensive analysis fields to each question:

1. `explanation` - Detailed explanation of correct answer
2. `primary_type` - Main subject area
3. `secondary_type` - Specific sub-topic
4. `difficulty_level` - Easy/Medium/Hard
5. `difficulty_reason` - Why this difficulty level
6. `learning_objectives` - What knowledge is needed
7. `question_strategy` - How question is designed
8. `options_analysis` - Detailed analysis of each option
9. `key_concepts` - Key concepts tested
10. `common_mistakes` - Common mistakes aspirants make
11. `elimination_technique` - How to eliminate wrong options
12. `memory_hooks` - Memory techniques
13. `related_topics` - Related topics for preparation
14. `exam_strategy` - Time management and confidence
15. `source_material` - Recommended sources
16. `motivation` - Why this is important
17. `examiner_thought_process` - What examiner is thinking
18. `current_affairs_connection` - Current events connection
19. `time_management` - Recommended time allocation
20. `confidence_calibration` - How to assess confidence

## Configuration

- **Model**: grok-4-0709
- **Timeout**: 120 seconds
- **Max Retries**: 3
- **Batch Size**: 5 questions
- **Rate Limiting**: 3 seconds between questions, 15 seconds between batches

## Troubleshooting

### API Key Issues
- Ensure `GROK_API_KEY` is set in `.env` file
- Verify the key is valid and has sufficient credits

### File Path Issues
- Ensure you're running from the `python_scripts` directory
- Check that input file exists at `../json_files/upsc_prelims_2025_structured_for_frontend.json`

### Analysis Failures
- Check internet connection
- Verify Grok API service status
- Review error messages in console output

## Expected Output

The script will create a JSON file with:
- Original question data
- 18 additional analysis fields per question
- Metadata about the analysis process
- Timestamps for each analysis

## Usage Notes

- The script processes all 100 questions by default
- For testing, uncomment the line `questions = questions[:5]` in the main function
- Analysis takes approximately 30-45 minutes for all questions
- Progress is displayed in real-time with batch information 