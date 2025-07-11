#!/usr/bin/env python3
"""
Verification script to check completeness of GS Prelims 2023 dataset
"""

import json
from typing import List, Set

def verify_complete_dataset():
    """Verify if the final dataset has all 100 questions"""
    
    print("🔍 VERIFYING COMPLETE DATASET")
    print("=" * 60)
    
    # Load the final dataset
    try:
        with open('GS Prelims 2023_COMPLETE_ALL_QUESTIONS.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Final dataset file not found!")
        return
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return
    
    questions = data.get('questions', [])
    total_questions = len(questions)
    
    print(f"📊 DATASET ANALYSIS:")
    print(f"   Total questions found: {total_questions}")
    print(f"   Expected questions: 100")
    
    if total_questions != 100:
        print(f"   ❌ MISMATCH: Expected 100, found {total_questions}")
    else:
        print(f"   ✅ MATCH: Found exactly 100 questions")
    
    # Extract all question numbers
    question_numbers = []
    for q in questions:
        try:
            q_num = int(q.get('question_number', 0))
            question_numbers.append(q_num)
        except (ValueError, TypeError):
            print(f"   ⚠️  Invalid question number: {q.get('question_number', 'N/A')}")
    
    # Sort question numbers
    question_numbers.sort()
    
    print(f"\n📝 QUESTION NUMBERS FOUND ({len(question_numbers)}):")
    print(f"   {question_numbers}")
    
    # Check for missing questions
    expected_range = set(range(1, 101))  # 1 to 100
    actual_range = set(question_numbers)
    missing = expected_range - actual_range
    extra = actual_range - expected_range
    
    print(f"\n🔍 COMPLETENESS CHECK:")
    
    if missing:
        print(f"   ❌ MISSING QUESTIONS ({len(missing)}): {sorted(missing)}")
    else:
        print(f"   ✅ NO MISSING QUESTIONS")
    
    if extra:
        print(f"   ⚠️  EXTRA QUESTIONS ({len(extra)}): {sorted(extra)}")
    else:
        print(f"   ✅ NO EXTRA QUESTIONS")
    
    # Check for duplicates
    duplicates = []
    seen = set()
    for q_num in question_numbers:
        if q_num in seen:
            duplicates.append(q_num)
        else:
            seen.add(q_num)
    
    if duplicates:
        print(f"   ❌ DUPLICATE QUESTIONS: {sorted(duplicates)}")
    else:
        print(f"   ✅ NO DUPLICATE QUESTIONS")
    
    # Check question quality
    print(f"\n📋 QUALITY CHECK:")
    
    missing_fields = []
    for i, q in enumerate(questions):
        required_fields = ['question_number', 'section', 'question_text', 'correct_answer', 'explanation']
        for field in required_fields:
            if not q.get(field):
                missing_fields.append(f"Q{q.get('question_number', 'N/A')} missing {field}")
    
    if missing_fields:
        print(f"   ⚠️  QUESTIONS WITH MISSING FIELDS:")
        for field in missing_fields[:10]:  # Show first 10
            print(f"      {field}")
        if len(missing_fields) > 10:
            print(f"      ... and {len(missing_fields) - 10} more")
    else:
        print(f"   ✅ ALL QUESTIONS HAVE REQUIRED FIELDS")
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"📊 FINAL VERIFICATION SUMMARY:")
    print(f"   Total questions: {total_questions}/100")
    print(f"   Missing questions: {len(missing)}")
    print(f"   Extra questions: {len(extra)}")
    print(f"   Duplicate questions: {len(duplicates)}")
    print(f"   Questions with missing fields: {len(missing_fields)}")
    
    if total_questions == 100 and not missing and not extra and not duplicates and not missing_fields:
        print(f"\n🎉 PERFECT DATASET! All 100 questions present and complete!")
    else:
        print(f"\n⚠️  DATASET NEEDS ATTENTION - Issues found above")
    
    print(f"{'='*60}")
    
    return {
        'total': total_questions,
        'missing': sorted(missing),
        'extra': sorted(extra),
        'duplicates': sorted(duplicates),
        'missing_fields': missing_fields
    }

def main():
    result = verify_complete_dataset()
    
    # Show detailed missing questions if any
    if result['missing']:
        print(f"\n🔍 DETAILED MISSING QUESTIONS:")
        for q_num in result['missing']:
            print(f"   Q{q_num}")

if __name__ == "__main__":
    main() 