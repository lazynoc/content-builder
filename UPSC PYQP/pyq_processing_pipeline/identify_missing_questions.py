#!/usr/bin/env python3
"""
Identify missing questions from the complete merged dataset
"""

import json
from typing import List, Dict, Any

def load_questions(file_path: str) -> List[Dict[str, Any]]:
    """Load questions from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('questions', [])
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return []

def analyze_questions(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze questions and identify missing ones"""
    if not questions:
        return {
            'total': 0,
            'valid_numbers': [],
            'missing_numbers': list(range(1, 101)),
            'success_rate': 0.0
        }
    
    # Extract question numbers
    question_numbers = []
    for q in questions:
        try:
            num = int(q.get('question_number', 0))
            if num > 0:
                question_numbers.append(num)
        except (ValueError, TypeError):
            continue
    
    question_numbers.sort()
    
    # Find missing numbers (1-100)
    all_numbers = set(range(1, 101))
    valid_numbers = set(question_numbers)
    missing_numbers = sorted(list(all_numbers - valid_numbers))
    
    return {
        'total': len(questions),
        'valid_numbers': question_numbers,
        'missing_numbers': missing_numbers,
        'success_rate': (len(questions) / 100) * 100
    }

def group_missing_questions(missing_numbers: List[int]) -> List[str]:
    """Group consecutive missing questions for easier reading"""
    if not missing_numbers:
        return []
    
    groups = []
    start = missing_numbers[0]
    end = start
    
    for i in range(1, len(missing_numbers)):
        if missing_numbers[i] == end + 1:
            end = missing_numbers[i]
        else:
            if start == end:
                groups.append(f"Q{start}")
            else:
                groups.append(f"Q{start}-Q{end}")
            start = end = missing_numbers[i]
    
    # Add the last group
    if start == end:
        groups.append(f"Q{start}")
    else:
        groups.append(f"Q{start}-Q{end}")
    
    return groups

def main():
    print("🔍 IDENTIFYING MISSING QUESTIONS FROM COMPLETE DATASET")
    print("=" * 60)
    
    # Load from the complete merged file
    file_path = "GS Prelims 2024_COMPLETE_questions.json"
    questions = load_questions(file_path)
    
    if not questions:
        print("❌ No questions found!")
        return
    
    # Analyze questions
    analysis = analyze_questions(questions)
    
    print(f"📊 EXTRACTION ANALYSIS:")
    print(f"   Total questions extracted: {analysis['total']}")
    print(f"   Valid question numbers: {len(analysis['valid_numbers'])}")
    print(f"   Missing questions: {len(analysis['missing_numbers'])}")
    print(f"   Success rate: {analysis['success_rate']:.1f}%")
    print()
    
    print(f"✅ EXTRACTED QUESTIONS:")
    print(f"   Numbers: {analysis['valid_numbers']}")
    print()
    
    if analysis['missing_numbers']:
        print(f"❌ MISSING QUESTIONS:")
        print(f"   Numbers: {analysis['missing_numbers']}")
        print()
        
        grouped_missing = group_missing_questions(analysis['missing_numbers'])
        print(f"📄 MISSING QUESTIONS BY RANGES:")
        for group in grouped_missing:
            print(f"   {group}")
        print()
        
        # Save missing questions for reference
        missing_data = {
            'total_missing': len(analysis['missing_numbers']),
            'missing_numbers': analysis['missing_numbers'],
            'grouped_missing': grouped_missing,
            'extracted_count': analysis['total']
        }
        
        with open('missing_questions_2024.json', 'w', encoding='utf-8') as f:
            json.dump(missing_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Missing questions saved to: missing_questions_2024.json")
    else:
        print("🎉 ALL QUESTIONS EXTRACTED SUCCESSFULLY!")

if __name__ == "__main__":
    main() 