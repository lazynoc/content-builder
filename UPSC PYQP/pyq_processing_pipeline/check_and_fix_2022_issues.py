#!/usr/bin/env python3
"""
Script to check and fix 2022 UPSC questions before OpenAI analysis
Extracts options from question_text and adds missing fields
"""

import json
import re
import os
from typing import Dict, Any, List

def extract_options_from_text(question_text: str) -> Dict[str, str]:
    """Extract options from question text that contains embedded options"""
    options = {}
    
    # Pattern to match options like (a) text, (b) text, etc.
    pattern = r'\(([a-d])\)\s*([^\(]+?)(?=\([a-d]\)|$)'
    matches = re.findall(pattern, question_text, re.IGNORECASE | re.DOTALL)
    
    for match in matches:
        option_letter = match[0].upper()
        option_text = match[1].strip()
        # Clean up option text
        option_text = re.sub(r'\n+', ' ', option_text).strip()
        options[option_letter] = option_text
    
    return options

def clean_question_text(question_text: str) -> str:
    """Remove options from question text to get clean question"""
    # Remove options from the end of question text
    # Pattern to match options at the end
    pattern = r'\([a-d]\)\s*[^\(]+(?:\s*\([a-d]\)\s*[^\(]+)*$'
    cleaned_text = re.sub(pattern, '', question_text, flags=re.IGNORECASE | re.DOTALL)
    return cleaned_text.strip()

def check_2022_questions():
    """Check 2022 questions for issues and fix them"""
    
    input_file = "GS Prelims 2022_COMPLETE_100_QUESTIONS.json"
    output_file = "GS Prelims 2022_FIXED_FOR_ANALYSIS.json"
    
    print(f"📖 Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    print(f"📊 Found {len(questions)} questions to check")
    
    issues_found = []
    fixed_questions = []
    
    for i, question in enumerate(questions):
        question_num = question.get('question_number', str(i+1))
        print(f"\n🔍 Checking Question {question_num}...")
        
        # Check for missing options field
        if 'options' not in question:
            print(f"  ⚠️  Missing 'options' field")
            question_text = question.get('question_text', '')
            
            # Extract options from question text
            options = extract_options_from_text(question_text)
            if options:
                print(f"  ✅ Extracted {len(options)} options: {list(options.keys())}")
                question['options'] = options
                question['options_extracted'] = True
                
                # Clean question text
                cleaned_text = clean_question_text(question_text)
                question['question_text'] = cleaned_text
                print(f"  ✅ Cleaned question text")
            else:
                print(f"  ❌ Could not extract options from question text")
                issues_found.append(f"Q{question_num}: Could not extract options")
                question['options'] = {}
                question['options_extracted'] = False
        else:
            print(f"  ✅ Options field exists")
            question['options_extracted'] = True
        
        # Check for missing required fields
        required_fields = ['question_number', 'question_text', 'correct_answer']
        missing_fields = []
        for field in required_fields:
            if not question.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"  ❌ Missing required fields: {missing_fields}")
            issues_found.append(f"Q{question_num}: Missing {missing_fields}")
        else:
            print(f"  ✅ All required fields present")
        
        # Add missing fields that 2023/2024 have
        if 'examiner_thought_process' not in question:
            question['examiner_thought_process'] = {}
        if 'learning_insights' not in question:
            question['learning_insights'] = {}
        if 'options_analysis' not in question:
            question['options_analysis'] = {}
        if 'question_nature' not in question:
            question['question_nature'] = {}
        
        # Add processing metadata
        question['processing_date'] = "2025-07-06T22:50:00.000000"
        question['openai_analysis_date'] = None  # Will be set after OpenAI analysis
        
        fixed_questions.append(question)
    
    # Create output data structure
    output_data = {
        "metadata": {
            "original_file": input_file,
            "processing_date": "2025-07-06T22:50:00.000000",
            "total_questions": len(fixed_questions),
            "issues_found": len(issues_found),
            "processing_method": "pre_openai_fix",
            "note": "Fixed 2022 questions for OpenAI analysis compatibility"
        },
        "questions": fixed_questions
    }
    
    # Save fixed file
    print(f"\n💾 Saving fixed file: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📈 Summary:")
    print(f"   ✅ Questions processed: {len(fixed_questions)}")
    print(f"   ⚠️  Issues found: {len(issues_found)}")
    
    if issues_found:
        print(f"\n📝 Issues found:")
        for issue in issues_found[:10]:  # Show first 10 issues
            print(f"   - {issue}")
        if len(issues_found) > 10:
            print(f"   ... and {len(issues_found) - 10} more")
    
    print(f"\n✅ Fixed file ready for OpenAI analysis: {output_file}")
    return output_file

if __name__ == "__main__":
    check_2022_questions() 