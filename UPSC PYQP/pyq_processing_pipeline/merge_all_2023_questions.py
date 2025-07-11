#!/usr/bin/env python3
"""
Final merge script to combine all 2023 GS Prelims questions
"""

import json
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file with error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return {"questions": []}
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in {file_path}: {e}")
        return {"questions": []}

def merge_all_2023_questions():
    """Merge all 2023 GS Prelims questions into a complete dataset"""
    
    print("🔄 MERGING ALL 2023 GS PRELIMS QUESTIONS")
    print("=" * 60)
    
    # Load all question files
    files_to_merge = [
        "GS Prelims 2023_PYQ_ONLY_chunked.json",  # Original 91 questions
        "GS Prelims 2023_MISSING_questions_MANUAL.json",  # Q5, Q27, Q32, Q33, Q66, Q89
        "GS Prelims 2023_REMAINING_34_35_36.json",  # Q34, Q35
        "GS Prelims 2023_Q36_FINAL.json"  # Q36
    ]
    
    all_questions = []
    question_numbers = set()
    
    # Load and process each file
    for file_path in files_to_merge:
        print(f"📂 Loading: {file_path}")
        data = load_json_file(file_path)
        
        if "questions" in data and data["questions"]:
            file_questions = data["questions"]
            print(f"   Found {len(file_questions)} questions")
            
            for q in file_questions:
                q_num = str(q.get('question_number', ''))
                if q_num and q_num not in question_numbers:
                    question_numbers.add(q_num)
                    all_questions.append(q)
                    print(f"   ✅ Added Q{q_num}")
                else:
                    print(f"   ⚠️  Skipped duplicate Q{q_num}")
        else:
            print(f"   ❌ No questions found in {file_path}")
    
    # Sort questions by question number
    all_questions.sort(key=lambda x: int(x.get('question_number', 0)))
    
    # Create final merged dataset
    merged_data = {
        "metadata": {
            "extraction_date": datetime.now().isoformat(),
            "total_questions": len(all_questions),
            "merge_method": "complete_2023_merge",
            "source_files": files_to_merge,
            "note": "Complete GS Prelims 2023 dataset with all questions from multiple extraction methods"
        },
        "questions": []
    }
    
    # Add unique IDs and finalize questions
    for i, question in enumerate(all_questions):
        question_dict = question.copy()
        question_dict['id'] = str(uuid.uuid4())
        question_dict['final_extraction_order'] = i + 1
        merged_data["questions"].append(question_dict)
    
    # Save merged dataset
    output_path = "GS Prelims 2023_COMPLETE_ALL_QUESTIONS.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✅ MERGE COMPLETE!")
    print(f"   Total questions: {len(all_questions)}")
    print(f"   Saved to: {output_path}")
    print(f"{'='*60}")
    
    # Show question numbers
    question_nums = sorted([int(q.get('question_number', 0)) for q in all_questions])
    print(f"\n📝 QUESTION NUMBERS ({len(question_nums)} total):")
    print(f"   {question_nums}")
    
    # Check for any gaps
    expected_range = set(range(1, len(question_nums) + 1))
    actual_range = set(question_nums)
    missing = expected_range - actual_range
    
    if missing:
        print(f"\n❌ MISSING QUESTIONS: {sorted(missing)}")
    else:
        print(f"\n✅ NO MISSING QUESTIONS - Complete dataset!")
    
    return merged_data

def main():
    merged_data = merge_all_2023_questions()
    
    # Show summary of extracted questions
    print(f"\n📊 EXTRACTION SUMMARY:")
    print(f"   Original extraction: 91 questions")
    print(f"   Manual extraction: 6 questions (Q5, Q27, Q32, Q33, Q66, Q89)")
    print(f"   Remaining extraction: 2 questions (Q34, Q35)")
    print(f"   Final extraction: 1 question (Q36)")
    print(f"   Total merged: {len(merged_data['questions'])} questions")

if __name__ == "__main__":
    main() 