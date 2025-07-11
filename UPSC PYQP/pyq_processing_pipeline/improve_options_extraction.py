#!/usr/bin/env python3
"""
Improved script to handle remaining questions with better regex patterns
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

def extract_options_improved(question_text: str) -> Tuple[str, Dict[str, str]]:
    """
    Improved extraction with multiple patterns
    """
    
    # Pattern 1: Standard (a) option (b) option (c) option (d) option
    pattern1 = r'\(a\)\s*([^)]+)\s*\(b\)\s*([^)]+)\s*\(c\)\s*([^)]+)\s*\(d\)\s*([^)]+)'
    
    # Pattern 2: Handle questions with line breaks and special characters
    pattern2 = r'\(a\)\s*([^)]+?)\s*\(b\)\s*([^)]+?)\s*\(c\)\s*([^)]+?)\s*\(d\)\s*([^)]+?)'
    
    # Pattern 3: Handle questions with "How many of the above" format
    pattern3 = r'\(a\)\s*([^)]+?)\s*\(b\)\s*([^)]+?)\s*\(c\)\s*([^)]+?)\s*\(d\)\s*([^)]+?)(?:\s*$|\s*\n)'
    
    # Pattern 4: Handle questions with multiple statements
    pattern4 = r'\(a\)\s*([^)]+?)\s*\(b\)\s*([^)]+?)\s*\(c\)\s*([^)]+?)\s*\(d\)\s*([^)]+?)(?:\s*$|\s*\n|\s*\.)'
    
    patterns = [pattern1, pattern2, pattern3, pattern4]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, question_text, re.IGNORECASE | re.DOTALL)
        if match:
            try:
                option_a = match.group(1).strip()
                option_b = match.group(2).strip()
                option_c = match.group(3).strip()
                option_d = match.group(4).strip()
                
                # Clean up options (remove extra whitespace, newlines)
                option_a = re.sub(r'\s+', ' ', option_a).strip()
                option_b = re.sub(r'\s+', ' ', option_b).strip()
                option_c = re.sub(r'\s+', ' ', option_c).strip()
                option_d = re.sub(r'\s+', ' ', option_d).strip()
                
                # Remove options from question text
                clean_question = question_text[:match.start()].strip()
                
                options = {
                    "A": option_a,
                    "B": option_b,
                    "C": option_c,
                    "D": option_d
                }
                
                print(f"✅ Pattern {i+1} matched for: {question_text[:50]}...")
                return clean_question, options
                
            except Exception as e:
                print(f"❌ Error with pattern {i+1}: {e}")
                continue
    
    # If no pattern matches, try manual extraction for specific cases
    if "Statement-I:" in question_text and "Statement-II:" in question_text:
        # Handle statement-based questions
        return extract_statement_options(question_text)
    
    print(f"⚠️  Could not extract options from: {question_text[:100]}...")
    return question_text, {}

def extract_statement_options(question_text: str) -> Tuple[str, Dict[str, str]]:
    """Handle statement-based questions"""
    
    # Pattern for statement questions
    statement_pattern = r'\(a\)\s*([^)]+?)\s*\(b\)\s*([^)]+?)\s*\(c\)\s*([^)]+?)\s*\(d\)\s*([^)]+?)(?:\s*$|\s*\n)'
    
    match = re.search(statement_pattern, question_text, re.IGNORECASE | re.DOTALL)
    if match:
        option_a = match.group(1).strip()
        option_b = match.group(2).strip()
        option_c = match.group(3).strip()
        option_d = match.group(4).strip()
        
        clean_question = question_text[:match.start()].strip()
        
        options = {
            "A": option_a,
            "B": option_b,
            "C": option_c,
            "D": option_d
        }
        
        return clean_question, options
    
    return question_text, {}

def process_remaining_questions(input_file: str, output_file: str):
    """Process questions that couldn't be extracted with improved patterns"""
    
    print(f"🔍 IMPROVED PROCESSING: {input_file}")
    print("=" * 60)
    
    # Load input file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    processed_questions = []
    
    print(f"📝 Processing {len(questions)} questions with improved patterns...")
    
    for i, question in enumerate(questions):
        question_text = question.get('question_text', '')
        
        # Check if options were already extracted
        if question.get('options_extracted', False):
            processed_questions.append(question)
            continue
        
        # Try improved extraction
        clean_question, options = extract_options_improved(question_text)
        
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
            "processing_method": "improved_options_separation",
            "note": "Options separated with improved regex patterns"
        },
        "questions": processed_questions
    }
    
    # Save output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ IMPROVED PROCESSING COMPLETE!")
    print(f"   Input: {input_file}")
    print(f"   Output: {output_file}")
    print(f"   Total questions: {len(processed_questions)}")
    print(f"   Questions with extracted options: {len([q for q in processed_questions if q['options_extracted']])}")
    
    # Show questions without options
    questions_without_options = [q for q in processed_questions if not q['options_extracted']]
    if questions_without_options:
        print(f"\n❌ QUESTIONS WITHOUT OPTIONS ({len(questions_without_options)}):")
        for q in questions_without_options:
            print(f"   Q{q['question_number']}: {q['question_text'][:100]}...")

def main():
    # Process 2023 dataset with improved patterns
    if Path("GS Prelims 2023_WITH_SEPARATED_OPTIONS.json").exists():
        process_remaining_questions(
            "GS Prelims 2023_WITH_SEPARATED_OPTIONS.json",
            "GS Prelims 2023_IMPROVED_OPTIONS.json"
        )
    
    # Process 2024 dataset with improved patterns
    if Path("GS Prelims 2024_WITH_SEPARATED_OPTIONS.json").exists():
        process_remaining_questions(
            "GS Prelims 2024_WITH_SEPARATED_OPTIONS.json",
            "GS Prelims 2024_IMPROVED_OPTIONS.json"
        )
    
    print(f"\n{'='*60}")
    print(f"🎉 IMPROVED PROCESSING COMPLETE!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 