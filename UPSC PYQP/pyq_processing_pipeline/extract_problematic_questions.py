#!/usr/bin/env python3
"""
Extract the 3 problematic questions (13, 16, 20) to show their current state
"""

import json

def extract_problematic_questions():
    """Extract the 3 problematic questions"""
    
    input_file = "GS Prelims 2022_FIXED_FOR_ANALYSIS.json"
    
    print(f"📖 Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    problematic_questions = []
    
    for question in questions:
        question_num = question.get('question_number')
        if question_num in ["13", "16", "20"]:
            problematic_questions.append(question)
    
    print(f"\n🔍 Found {len(problematic_questions)} problematic questions:")
    
    for question in problematic_questions:
        print(f"\n{'='*60}")
        print(f"Question {question['question_number']}:")
        print(f"Section: {question['section']}")
        print(f"Question Text: {question['question_text']}")
        print(f"Correct Answer: {question['correct_answer']}")
        print(f"Options: {question['options']}")
        print(f"Options Extracted: {question['options_extracted']}")
        print(f"{'='*60}")
    
    # Save to a separate file for easy reference
    output_data = {
        "metadata": {
            "note": "Extracted problematic questions from 2022 for manual fixing",
            "total_questions": len(problematic_questions)
        },
        "questions": problematic_questions
    }
    
    output_file = "2022_problematic_questions.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved problematic questions to: {output_file}")
    print(f"\n📝 Please provide the missing parts for these questions!")

if __name__ == "__main__":
    extract_problematic_questions() 