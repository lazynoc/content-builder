#!/usr/bin/env python3
"""
Script to separate options from question_text and create structured option fields
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

def extract_options_from_text(question_text: str) -> Tuple[str, Dict[str, str]]:
    """
    Extract options from question text and return clean question + options dict
    """
    # Pattern to match options at the end of question
    option_pattern = r'\(a\)\s*([^)]+)\s*\(b\)\s*([^)]+)\s*\(c\)\s*([^)]+)\s*\(d\)\s*([^)]+)'
    
    # Try to find options at the end
    match = re.search(option_pattern, question_text, re.IGNORECASE | re.DOTALL)
    
    if match:
        # Extract options
        option_a = match.group(1).strip()
        option_b = match.group(2).strip()
        option_c = match.group(3).strip()
        option_d = match.group(4).strip()
        
        # Remove options from question text
        clean_question = question_text[:match.start()].strip()
        
        options = {
            "A": option_a,
            "B": option_b,
            "C": option_c,
            "D": option_d
        }
        
        return clean_question, options
    
    # If no match found, try alternative patterns
    # Pattern for questions with "How many of the above" or similar
    alt_pattern = r'\(a\)\s*([^)]+)\s*\(b\)\s*([^)]+)\s*\(c\)\s*([^)]+)\s*\(d\)\s*([^)]+)'
    alt_match = re.search(alt_pattern, question_text, re.IGNORECASE | re.DOTALL)
    
    if alt_match:
        option_a = alt_match.group(1).strip()
        option_b = alt_match.group(2).strip()
        option_c = alt_match.group(3).strip()
        option_d = alt_match.group(4).strip()
        
        clean_question = question_text[:alt_match.start()].strip()
        
        options = {
            "A": option_a,
            "B": option_b,
            "C": option_c,
            "D": option_d
        }
        
        return clean_question, options
    
    # If still no match, return original text and empty options
    print(f"⚠️  Could not extract options from: {question_text[:100]}...")
    return question_text, {}

def process_questions_with_separated_options(input_file: str, output_file: str):
    """Process questions and separate options"""
    
    print(f"🔍 PROCESSING: {input_file}")
    print("=" * 60)
    
    # Load input file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    processed_questions = []
    
    print(f"📝 Processing {len(questions)} questions...")
    
    for i, question in enumerate(questions):
        question_text = question.get('question_text', '')
        
        # Extract options
        clean_question, options = extract_options_from_text(question_text)
        
        # Create new question structure
        new_question = question.copy()
        new_question['question_text'] = clean_question
        new_question['options'] = options
        
        # Add processing metadata
        new_question['options_extracted'] = len(options) > 0
        new_question['processing_date'] = datetime.now().isoformat()
        
        processed_questions.append(new_question)
        
        if (i + 1) % 10 == 0:
            print(f"   Processed {i + 1}/{len(questions)} questions")
    
    # Create output data
    output_data = {
        "metadata": {
            "original_file": input_file,
            "processing_date": datetime.now().isoformat(),
            "total_questions": len(processed_questions),
            "questions_with_options": len([q for q in processed_questions if q['options_extracted']]),
            "processing_method": "options_separation",
            "note": "Options separated from question_text for better quiz functionality"
        },
        "questions": processed_questions
    }
    
    # Save output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ PROCESSING COMPLETE!")
    print(f"   Input: {input_file}")
    print(f"   Output: {output_file}")
    print(f"   Total questions: {len(processed_questions)}")
    print(f"   Questions with extracted options: {len([q for q in processed_questions if q['options_extracted']])}")
    
    # Show sample
    if processed_questions:
        print(f"\n📝 SAMPLE PROCESSED QUESTION:")
        sample = processed_questions[0]
        print(f"   Q{sample['question_number']}: {sample['question_text'][:100]}...")
        print(f"   Options: {sample['options']}")
        print(f"   Correct Answer: {sample['correct_answer']}")

def main():
    # Process 2022 dataset
    if Path("GS Prelims 2022_COMPLETE_100_QUESTIONS.json").exists():
        process_questions_with_separated_options(
            "GS Prelims 2022_COMPLETE_100_QUESTIONS.json",
            "GS Prelims 2022_WITH_SEPARATED_OPTIONS.json"
        )
    
    # Process 2023 dataset
    if Path("GS Prelims 2023_COMPLETE_ALL_QUESTIONS.json").exists():
        process_questions_with_separated_options(
            "GS Prelims 2023_COMPLETE_ALL_QUESTIONS.json",
            "GS Prelims 2023_WITH_SEPARATED_OPTIONS.json"
        )
    
    # Process 2024 dataset
    if Path("GS Prelims 2024_COMPLETE_100_QUESTIONS.json").exists():
        process_questions_with_separated_options(
            "GS Prelims 2024_COMPLETE_100_QUESTIONS.json",
            "GS Prelims 2024_WITH_SEPARATED_OPTIONS.json"
        )
    
    print(f"\n{'='*60}")
    print(f"🎉 ALL PROCESSING COMPLETE!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 