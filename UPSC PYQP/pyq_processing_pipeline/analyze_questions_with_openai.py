#!/usr/bin/env python3
"""
Script to analyze questions with OpenAI and add comprehensive analysis
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()

import openai

# --- CONFIG ---
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def analyze_single_question(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a single question to OpenAI for comprehensive analysis
    """
    
    question_text = question.get('question_text', '')
    options = question.get('options', {})
    correct_answer = question.get('correct_answer', '')
    explanation = question.get('explanation', '')
    section = question.get('section', '')
    
    # Prepare the prompt for OpenAI
    prompt = f"""
    Analyze this UPSC Prelims question comprehensively and provide detailed insights in JSON format.

    QUESTION DETAILS:
    Section: {section}
    Question: {question_text}
    Options: {options}
    Correct Answer: {correct_answer}
    Explanation: {explanation}

    Please provide analysis in the following JSON structure:

    {{
        "question_nature": {{
            "primary_type": "Factual/Conceptual/Analytical/Application",
            "secondary_type": "Memory-based/Understanding-based/Application-based",
            "difficulty_reason": "Explanation of why this question is easy/medium/difficult",
            "knowledge_requirement": "Type of knowledge required (static/current affairs/mixed)"
        }},
        "examiner_thought_process": {{
            "testing_objective": "What the examiner is trying to test",
            "question_design_strategy": "How the question is designed to evaluate candidates",
            "trap_setting": "Any traps or misleading elements in the question",
            "discrimination_potential": "How well this question can differentiate between candidates"
        }},
        "options_analysis": {{
            "A": {{
                "type": "correct_answer/plausible_distractor/obvious_wrong",
                "reason": "Why this option is correct/incorrect",
                "trap": "If it's a distractor, what trap does it set",
                "elimination_strategy": "How to eliminate this option"
            }},
            "B": {{
                "type": "correct_answer/plausible_distractor/obvious_wrong",
                "reason": "Why this option is correct/incorrect",
                "trap": "If it's a distractor, what trap does it set",
                "elimination_strategy": "How to eliminate this option"
            }},
            "C": {{
                "type": "correct_answer/plausible_distractor/obvious_wrong",
                "reason": "Why this option is correct/incorrect",
                "trap": "If it's a distractor, what trap does it set",
                "elimination_strategy": "How to eliminate this option"
            }},
            "D": {{
                "type": "correct_answer/plausible_distractor/obvious_wrong",
                "reason": "Why this option is correct/incorrect",
                "trap": "If it's a distractor, what trap does it set",
                "elimination_strategy": "How to eliminate this option"
            }}
        }},
        "learning_insights": {{
            "key_concepts": ["List of key concepts tested"],
            "common_mistakes": ["Common mistakes students make"],
            "elimination_technique_semi_knowledge": "If a student knows only part of the topic, what is the best way to maximize their chances?",
            "elimination_technique_safe_guess": "If a student has little or no knowledge, what is the safest approach or examiner-mindset trick to attempt this question?",
            "memory_hooks": ["Mnemonics or memory aids"],
            "related_topics": ["Related topics for further study"],
            "current_affairs_connection": "Connection to current events if any"
        }},
        "difficulty_level": "Easy/Medium/Difficult",
        "time_management": "How much time should be spent on this question",
        "confidence_calibration": "How confident should a well-prepared student be"
    }}

    Focus on providing actionable insights that would help UPSC aspirants understand the question better and improve their preparation strategy. For the two elimination techniques, be specific and practical.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert UPSC mentor with deep knowledge of the exam pattern, question design, and preparation strategies. Provide comprehensive analysis of UPSC questions."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        if content:
            analysis = json.loads(content)
        else:
            analysis = {}
        return analysis
        
    except Exception as e:
        print(f"❌ Error analyzing question {question.get('question_number', 'N/A')}: {e}")
        return {}

def process_questions_with_analysis(input_file: str, output_file: str, max_questions: Optional[int] = None):
    """
    Process questions and add OpenAI analysis
    """
    
    print(f"🔍 ANALYZING QUESTIONS WITH OPENAI: {input_file}")
    print("=" * 60)
    
    # Load input file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    
    # Remove question limit if max_questions is None
    questions_to_process = questions if max_questions is None else questions[:max_questions]
    
    print(f"📝 Processing {len(questions_to_process)} questions...")
    
    processed_questions = []
    
    for i, question in enumerate(questions_to_process):
        print(f"\n🔍 Analyzing Q{question.get('question_number', 'N/A')} ({i+1}/{len(questions_to_process)})")
        
        # Add OpenAI analysis
        analysis = analyze_single_question(question)
        
        if analysis:
            # Merge analysis with question
            enhanced_question = question.copy()
            enhanced_question.update(analysis)
            enhanced_question['openai_analysis_date'] = datetime.now().isoformat()
            
            processed_questions.append(enhanced_question)
            print(f"✅ Analysis completed for Q{question.get('question_number', 'N/A')}")
        else:
            # Keep original question if analysis failed
            processed_questions.append(question)
            print(f"❌ Analysis failed for Q{question.get('question_number', 'N/A')}")
        
        # Add delay to avoid rate limiting
        time.sleep(2)
    
    # Create output data
    output_data = {
        "metadata": {
            "original_file": input_file,
            "processing_date": datetime.now().isoformat(),
            "total_questions": len(processed_questions),
            "questions_with_analysis": len([q for q in processed_questions if 'openai_analysis_date' in q]),
            "processing_method": "openai_comprehensive_analysis",
            "note": f"Enhanced with OpenAI analysis (all questions)"
        },
        "questions": processed_questions
    }
    
    # Save output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ ANALYSIS COMPLETE!")
    print(f"   Input: {input_file}")
    print(f"   Output: {output_file}")
    print(f"   Total questions: {len(processed_questions)}")
    print(f"   Questions with analysis: {len([q for q in processed_questions if 'openai_analysis_date' in q])}")
    
    # Show sample analysis
    if processed_questions:
        sample = processed_questions[0]
        print(f"\n📝 SAMPLE ENHANCED QUESTION:")
        print(f"   Q{sample['question_number']}: {sample['question_text'][:100]}...")
        if 'question_nature' in sample:
            print(f"   Nature: {sample['question_nature']['primary_type']}")
            print(f"   Difficulty: {sample.get('difficulty_level', 'N/A')}")

def main():
    # Accept input and output file paths as command-line arguments
    if len(sys.argv) >= 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        print("Usage: python3 analyze_questions_with_openai.py <input_file> <output_file>")
        print("Example: python3 analyze_questions_with_openai.py GS_Prelims_2022_WITH_SEPARATED_OPTIONS.json GS_Prelims_2022_WITH_OPENAI_ANALYSIS.json")
        # Default to 2023 files for backward compatibility
        input_file = "GS Prelims 2023_WITH_SEPARATED_OPTIONS.json"
        output_file = "GS Prelims 2023_WITH_OPENAI_ANALYSIS.json"
        print(f"[INFO] Defaulting to: {input_file} -> {output_file}")

    process_questions_with_analysis(input_file, output_file)

if __name__ == "__main__":
    main() 