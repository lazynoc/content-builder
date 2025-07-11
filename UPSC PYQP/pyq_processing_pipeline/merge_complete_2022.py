#!/usr/bin/env python3
"""
Merge all 2022 questions into a complete dataset
Combines original extraction + first missing questions + remaining missing questions
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

def load_json_file(file_path):
    """Load and return JSON data from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in {file_path}: {e}")
        return None

def merge_2022_questions():
    """Merge all 2022 question sources into one complete dataset"""
    
    print("🔄 MERGING COMPLETE 2022 DATASET")
    print("=" * 60)
    
    # Load all question sources
    sources = {
        "original": "GS Prelims 2022_PYQ_ONLY_chunked.json",
        "missing_1": "GS Prelims 2022_MISSING_QUESTIONS.json", 
        "missing_2": "GS Prelims 2022_REMAINING_MISSING.json"
    }
    
    all_questions = []
    source_stats = {}
    
    for source_name, file_path in sources.items():
        print(f"\n📖 Loading {source_name}: {file_path}")
        data = load_json_file(file_path)
        
        if data and 'questions' in data:
            questions = data['questions']
            source_stats[source_name] = len(questions)
            print(f"   ✅ Loaded {len(questions)} questions")
            
            # Add source tracking
            for q in questions:
                q['source_file'] = source_name
                q['merge_date'] = datetime.now().isoformat()
            
            all_questions.extend(questions)
        else:
            source_stats[source_name] = 0
            print(f"   ❌ No questions loaded")
    
    # Sort questions by question number
    all_questions.sort(key=lambda x: int(x['question_number']))
    
    # Check for duplicates
    question_numbers = [q['question_number'] for q in all_questions]
    duplicates = [num for num in set(question_numbers) if question_numbers.count(num) > 1]
    
    if duplicates:
        print(f"\n⚠️  WARNING: Found duplicate question numbers: {duplicates}")
        # Remove duplicates (keep first occurrence)
        seen = set()
        unique_questions = []
        for q in all_questions:
            if q['question_number'] not in seen:
                seen.add(q['question_number'])
                unique_questions.append(q)
        all_questions = unique_questions
        print(f"   Removed duplicates, kept {len(all_questions)} unique questions")
    
    # Create final merged dataset
    merged_data = {
        "metadata": {
            "pdf_name": "GS Prelims 2022.pdf",
            "merge_date": datetime.now().isoformat(),
            "total_questions": len(all_questions),
            "merge_method": "complete_2022_merge",
            "source_files": sources,
            "source_stats": source_stats,
            "note": "Complete 2022 dataset merged from original extraction + missing questions"
        },
        "questions": all_questions
    }
    
    # Save merged dataset
    output_file = "GS Prelims 2022_COMPLETE_ALL_QUESTIONS.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✅ MERGE COMPLETE!")
    print(f"   Total questions: {len(all_questions)}")
    print(f"   Saved to: {output_file}")
    print(f"{'='*60}")
    
    # Show question number range
    if all_questions:
        min_q = min(all_questions, key=lambda x: int(x['question_number']))
        max_q = max(all_questions, key=lambda x: int(x['question_number']))
        print(f"   Question range: {min_q['question_number']} to {max_q['question_number']}")
    
    # Show source breakdown
    print(f"\n📊 SOURCE BREAKDOWN:")
    for source, count in source_stats.items():
        print(f"   {source}: {count} questions")
    
    # Check for missing questions (1-100)
    expected_range = set(range(1, 101))
    actual_numbers = set(int(q['question_number']) for q in all_questions)
    missing = expected_range - actual_numbers
    
    if missing:
        print(f"\n❌ MISSING QUESTIONS (1-100): {sorted(missing)}")
        print(f"   Missing count: {len(missing)}")
    else:
        print(f"\n✅ ALL QUESTIONS (1-100) PRESENT!")
    
    return merged_data

if __name__ == "__main__":
    merge_2022_questions() 