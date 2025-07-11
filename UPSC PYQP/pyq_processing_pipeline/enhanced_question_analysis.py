import json
import re
import time
from typing import Dict, List, Any, Tuple, Optional
import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv(dotenv_path='../../.env')

# Set up OpenAI client
client = openai.OpenAI()

def extract_options_from_text(question_text: str) -> Tuple[str, Dict[str, str]]:
    """
    Extract options from question text and return clean question + options dict
    """
    # Common patterns for options
    patterns = [
        # Pattern: (a) option (b) option (c) option (d) option
        r'\(([a-d])\)\s*([^(]+?)(?=\s*\([b-d]\)|$)',
        # Pattern: a) option b) option c) option d) option
        r'([a-d])\)\s*([^(]+?)(?=\s*[b-d]\)|$)',
        # Pattern: a. option b. option c. option d. option
        r'([a-d])\.\s*([^(]+?)(?=\s*[b-d]\.|$)',
        # Pattern: (A) option (B) option (C) option (D) option
        r'\(([A-D])\)\s*([^(]+?)(?=\s*\([B-D]\)|$)',
    ]
    
    options = {}
    clean_question = question_text
    
    for pattern in patterns:
        matches = re.findall(pattern, question_text, re.IGNORECASE | re.DOTALL)
        if matches:
            for match in matches:
                option_letter = match[0].upper()
                option_text = match[1].strip()
                options[option_letter] = option_text
            
            # Remove options from question text
            clean_question = re.sub(pattern, '', question_text, flags=re.IGNORECASE | re.DOTALL)
            break
    
    # Clean up the question text
    clean_question = re.sub(r'\s+', ' ', clean_question).strip()
    clean_question = re.sub(r'\s*[\(\)]\s*[a-dA-D]\s*[\)\.]\s*', '', clean_question)
    clean_question = re.sub(r'\s*[a-dA-D]\s*[\)\.]\s*', '', clean_question)
    
    return clean_question, options

def analyze_question_enhanced(question: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced analysis with detailed structured output"""
    
    prompt = f"""
    Analyze this UPSC CSE Prelims question comprehensively and provide detailed analysis in JSON format:

    Question: {question.get('question_text', '')}
    Options: {question.get('options', {})}
    Correct Answer: {question.get('correct_answer', '')}
    Section: {question.get('section', '')}
    Explanation: {question.get('explanation', '')}

    Provide analysis in the following detailed JSON format:

    {{
        "question_nature": {{
            "primary_type": "Factual/Conceptual/Analytical/Current Affairs/Blend",
            "secondary_type": "Memory-based/Application-based/Reasoning-based/Current Affairs-based",
            "difficulty_reason": "Detailed explanation of why this question is easy/medium/hard",
            "knowledge_requirement": "What type of knowledge is needed (static/dynamic/current affairs)"
        }},
        "examiner_thought_process": {{
            "testing_objective": "What the examiner is trying to test",
            "question_design_strategy": "How the question is designed to assess knowledge",
            "trap_setting": "How the examiner has set traps in options",
            "discrimination_potential": "How well this question can differentiate between candidates"
        }},
        "options_analysis": {{
            "A": {{
                "type": "correct_answer/tricky_option/close_call/silly_mistake/plausible_distractor",
                "reason": "Detailed explanation of why this option is correct/incorrect",
                "trap": "How this option can confuse students (leave empty for correct answer)",
                "elimination_strategy": "How to eliminate this option if incorrect"
            }},
            "B": {{
                "type": "correct_answer/tricky_option/close_call/silly_mistake/plausible_distractor",
                "reason": "Detailed explanation of why this option is correct/incorrect",
                "trap": "How this option can confuse students (leave empty for correct answer)",
                "elimination_strategy": "How to eliminate this option if incorrect"
            }},
            "C": {{
                "type": "correct_answer/tricky_option/close_call/silly_mistake/plausible_distractor",
                "reason": "Detailed explanation of why this option is correct/incorrect",
                "trap": "How this option can confuse students (leave empty for correct answer)",
                "elimination_strategy": "How to eliminate this option if incorrect"
            }},
            "D": {{
                "type": "correct_answer/tricky_option/close_call/silly_mistake/plausible_distractor",
                "reason": "Detailed explanation of why this option is correct/incorrect",
                "trap": "How this option can confuse students (leave empty for correct answer)",
                "elimination_strategy": "How to eliminate this option if incorrect"
            }}
        }},
        "learning_insights": {{
            "key_concepts": ["List of key concepts tested in this question"],
            "common_mistakes": ["Common mistakes students make with this type of question"],
            "elimination_technique": "Step-by-step elimination strategy for this question",
            "memory_hooks": ["Mnemonics or memory techniques for this topic"],
            "related_topics": ["Related topics that students should study"],
            "current_affairs_connection": "How this connects to current affairs (if applicable)"
        }},
        "difficulty_level": "Easy/Medium/Hard",
        "time_management": "How much time should be spent on this question",
        "confidence_calibration": "How confident should a well-prepared student be"
    }}

    Be comprehensive and practical. Focus on UPSC CSE Prelims context and provide actionable insights for students.
    """

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert UPSC CSE Prelims analyst with deep knowledge of exam patterns, question design, and student psychology. Provide comprehensive, structured analysis in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        # Extract the response content
        analysis_text = response.choices[0].message.content
        
        # Handle None content
        if analysis_text is None:
            analysis_text = "Analysis failed - no response content"
        
        # Try to parse JSON from response
        try:
            # Clean the response - remove markdown code blocks if present
            cleaned_text = analysis_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]  # Remove ```json
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]  # Remove ```
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]  # Remove trailing ```
            
            analysis = json.loads(cleaned_text.strip())
        except json.JSONDecodeError:
            # If JSON parsing fails, create a structured response
            analysis = {
                "question_nature": {
                    "primary_type": "Factual",
                    "secondary_type": "Memory-based",
                    "difficulty_reason": "Analysis failed",
                    "knowledge_requirement": "Analysis failed"
                },
                "examiner_thought_process": {
                    "testing_objective": "Analysis failed",
                    "question_design_strategy": "Analysis failed",
                    "trap_setting": "Analysis failed",
                    "discrimination_potential": "Analysis failed"
                },
                "options_analysis": {
                    "A": {"type": "silly_mistake", "reason": "Analysis failed", "trap": "Analysis failed", "elimination_strategy": "Analysis failed"},
                    "B": {"type": "silly_mistake", "reason": "Analysis failed", "trap": "Analysis failed", "elimination_strategy": "Analysis failed"},
                    "C": {"type": "silly_mistake", "reason": "Analysis failed", "trap": "Analysis failed", "elimination_strategy": "Analysis failed"},
                    "D": {"type": "silly_mistake", "reason": "Analysis failed", "trap": "Analysis failed", "elimination_strategy": "Analysis failed"}
                },
                "learning_insights": {
                    "key_concepts": ["Analysis failed"],
                    "common_mistakes": ["Analysis failed"],
                    "elimination_technique": "Analysis failed",
                    "memory_hooks": ["Analysis failed"],
                    "related_topics": ["Analysis failed"],
                    "current_affairs_connection": "Analysis failed"
                },
                "difficulty_level": "Medium",
                "time_management": "Analysis failed",
                "confidence_calibration": "Analysis failed",
                "raw_response": analysis_text
            }
        
        return analysis
        
    except Exception as e:
        print(f"Error analyzing question {question.get('question_number', 'unknown')}: {e}")
        return {
            "error": str(e),
            "question_nature": {
                "primary_type": "Factual",
                "secondary_type": "Memory-based",
                "difficulty_reason": "Analysis failed",
                "knowledge_requirement": "Analysis failed"
            },
            "examiner_thought_process": {
                "testing_objective": "Analysis failed",
                "question_design_strategy": "Analysis failed",
                "trap_setting": "Analysis failed",
                "discrimination_potential": "Analysis failed"
            },
            "options_analysis": {
                "A": {"type": "silly_mistake", "reason": "Analysis failed", "trap": "Analysis failed", "elimination_strategy": "Analysis failed"},
                "B": {"type": "silly_mistake", "reason": "Analysis failed", "trap": "Analysis failed", "elimination_strategy": "Analysis failed"},
                "C": {"type": "silly_mistake", "reason": "Analysis failed", "trap": "Analysis failed", "elimination_strategy": "Analysis failed"},
                "D": {"type": "silly_mistake", "reason": "Analysis failed", "trap": "Analysis failed", "elimination_strategy": "Analysis failed"}
            },
            "learning_insights": {
                "key_concepts": ["Analysis failed"],
                "common_mistakes": ["Analysis failed"],
                "elimination_technique": "Analysis failed",
                "memory_hooks": ["Analysis failed"],
                "related_topics": ["Analysis failed"],
                "current_affairs_connection": "Analysis failed"
            },
            "difficulty_level": "Medium",
            "time_management": "Analysis failed",
            "confidence_calibration": "Analysis failed"
        }

def restructure_question_data(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Restructure question data to separate options from question text
    """
    question_text = question.get('question_text', '')
    clean_question, options = extract_options_from_text(question_text)
    
    # Create restructured question
    restructured = {
        'question_number': question.get('question_number', ''),
        'section': question.get('section', ''),
        'question_text': clean_question,
        'options': options,
        'correct_answer': question.get('correct_answer', ''),
        'explanation': question.get('explanation', ''),
        'motivation': question.get('motivation', ''),
        'source_material': question.get('source_material', ''),
        'source_type': question.get('source_type', ''),
        'test_series_reference': question.get('test_series_reference', ''),
        'id': question.get('id', ''),
        'extraction_order': question.get('extraction_order', ''),
        'chunk_number': question.get('chunk_number', ''),
        # Enhanced analysis fields
        'question_nature': {},
        'examiner_thought_process': {},
        'options_analysis': {},
        'learning_insights': {},
        'difficulty_level': '',
        'time_management': '',
        'confidence_calibration': ''
    }
    
    return restructured

def process_questions_enhanced(input_file: str, output_file: str, start_index: int = 0, end_index: Optional[int] = None):
    """
    Process questions with enhanced analysis
    """
    print(f"Processing {input_file} with enhanced analysis...")
    
    # Load questions
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    print(f"Found {len(questions)} questions")
    
    # Limit range if specified
    if end_index is None:
        end_index = len(questions)
    questions_to_process = questions[start_index:end_index]
    
    print(f"Processing {len(questions_to_process)} questions from {start_index} to {end_index-1}")
    
    # Process each question
    processed_questions = []
    
    for i, question in enumerate(questions_to_process):
        print(f"Processing question {i+1}/{len(questions_to_process)}: {question.get('question_number', 'unknown')}")
        
        # Step 1: Separate options from question text
        question_text = question.get('question_text', '')
        clean_question, options = extract_options_from_text(question_text)
        
        # Step 2: Create base restructured question
        restructured_question = restructure_question_data(question)
        restructured_question['question_text'] = clean_question
        restructured_question['options'] = options
        
        # Step 3: Add enhanced OpenAI analysis
        if options:  # Only analyze if we have options
            print(f"  🔍 Analyzing with enhanced OpenAI...")
            analysis = analyze_question_enhanced(restructured_question)
            
            # Update question with enhanced analysis
            restructured_question['question_nature'] = analysis.get('question_nature', {})
            restructured_question['examiner_thought_process'] = analysis.get('examiner_thought_process', {})
            restructured_question['options_analysis'] = analysis.get('options_analysis', {})
            restructured_question['learning_insights'] = analysis.get('learning_insights', {})
            restructured_question['difficulty_level'] = analysis.get('difficulty_level', 'Medium')
            restructured_question['time_management'] = analysis.get('time_management', '')
            restructured_question['confidence_calibration'] = analysis.get('confidence_calibration', '')
            
            print(f"  ✅ Enhanced analysis complete: {restructured_question['question_nature'].get('primary_type', 'Unknown')}, {restructured_question['difficulty_level']}")
            
            # Add delay to avoid rate limiting
            time.sleep(2)
        
        processed_questions.append(restructured_question)
    
    # Create output data
    output_data = {
        'metadata': {
            'original_file': input_file,
            'processing_date': time.strftime("%Y-%m-%d %H:%M:%S"),
            'total_questions': len(processed_questions),
            'processing_note': 'Enhanced processing: options separated + comprehensive OpenAI analysis',
            'analysis_method': 'OpenAI GPT-4o-mini (Enhanced)'
        },
        'questions': processed_questions
    }
    
    # Save processed data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Enhanced processing finished! Saved to {output_file}")
    print(f"📊 Processed {len(processed_questions)} questions")
    
    # Show sample of first question
    if processed_questions:
        sample = processed_questions[0]
        print(f"\n📝 Sample enhanced question:")
        print(f"   Question: {sample['question_text'][:80]}...")
        print(f"   Options: {sample['options']}")
        print(f"   Correct Answer: {sample['correct_answer']}")
        print(f"   Primary Type: {sample['question_nature'].get('primary_type', 'Unknown')}")
        print(f"   Difficulty: {sample['difficulty_level']}")

def test_enhanced_analysis():
    """Test enhanced analysis with a few questions"""
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    # Test with 2 questions from 2024
    try:
        process_questions_enhanced(
            input_file="GS Prelims 2024 _complete_questions.json",
            output_file="GS Prelims 2024_enhanced_analysis.json",
            start_index=0,
            end_index=2
        )
    except FileNotFoundError:
        print("❌ File 'GS Prelims 2024 _complete_questions.json' not found!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Question Analysis...")
    test_enhanced_analysis()