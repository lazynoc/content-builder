#!/usr/bin/env python3
"""
Final complete merge script to combine all question sources including question 48:
1. Final complete file (GS Prelims 2024_FINAL_COMPLETE_ALL_SOURCES.json) - 99 questions
2. Question 48 (Question_48_final.json) - 1 question

This will create a truly complete dataset with all 100 questions.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Set

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file and return data"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return {"questions": []}
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in {file_path}: {e}")
        return {"questions": []}

def get_question_key(question: Dict[str, Any]) -> str:
    """Create a unique key for a question based on question number"""
    return f"Q{question.get('question_number', 'unknown')}"

def merge_questions(source_files: List[str]) -> Dict[str, Any]:
    """Merge questions from multiple source files with deduplication"""
    
    all_questions = []
    seen_questions = set()
    source_stats = {}
    
    print("🔄 Starting final complete merge...")
    
    for file_path in source_files:
        print(f"\n📁 Processing: {file_path}")
        data = load_json_file(file_path)
        questions = data.get('questions', [])
        
        source_stats[file_path] = {
            'total': len(questions),
            'added': 0,
            'duplicates': 0
        }
        
        for question in questions:
            question_key = get_question_key(question)
            
            if question_key not in seen_questions:
                # Add source tracking
                question['source_file'] = file_path
                question['merge_timestamp'] = datetime.now().isoformat()
                
                all_questions.append(question)
                seen_questions.add(question_key)
                source_stats[file_path]['added'] += 1
            else:
                source_stats[file_path]['duplicates'] += 1
                print(f"   ⚠️  Duplicate found: {question_key}")
    
    # Sort by question number
    all_questions.sort(key=lambda x: int(x.get('question_number', 0)))
    
    # Create comprehensive metadata
    metadata = {
        "pdf_name": "GS Prelims 2024 .pdf",
        "extraction_date": datetime.now().isoformat(),
        "total_questions": len(all_questions),
        "extraction_method": "final_complete_merge_all_sources",
        "source_files": source_files,
        "source_statistics": source_stats,
        "note": "COMPLETE 2024 GS Prelims questions - ALL 100 QUESTIONS INCLUDING QUESTION 48"
    }
    
    return {
        "metadata": metadata,
        "questions": all_questions
    }

def analyze_missing_questions(merged_data: Dict[str, Any]) -> List[int]:
    """Analyze and identify any still missing questions"""
    questions = merged_data.get('questions', [])
    question_numbers = set()
    
    for question in questions:
        try:
            question_numbers.add(int(question.get('question_number', 0)))
        except (ValueError, TypeError):
            continue
    
    # Check for missing questions (1-100)
    missing = []
    for i in range(1, 101):
        if i not in question_numbers:
            missing.append(i)
    
    return missing

def main():
    """Main merge function"""
    
    # Define source files
    source_files = [
        "GS Prelims 2024_FINAL_COMPLETE_ALL_SOURCES.json",
        "Question_48_complete.json"
    ]
    
    print("🚀 Starting FINAL COMPLETE merge to achieve 100 questions...")
    print("=" * 60)
    
    # Check if all files exist
    for file_path in source_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                questions = data.get('questions', [])
                print(f"✅ {file_path}: {len(questions)} questions")
        except FileNotFoundError:
            print(f"❌ {file_path}: File not found")
            return
        except json.JSONDecodeError as e:
            print(f"❌ {file_path}: JSON error - {e}")
            return
    
    # Perform merge
    merged_data = merge_questions(source_files)
    
    # Analyze results
    total_questions = len(merged_data['questions'])
    missing_questions = analyze_missing_questions(merged_data)
    
    print("\n" + "=" * 60)
    print("🎉 FINAL MERGE RESULTS:")
    print(f"✅ Total questions after merge: {total_questions}")
    print(f"❌ Missing questions: {len(missing_questions)}")
    
    if missing_questions:
        print(f"📋 Missing question numbers: {missing_questions}")
    else:
        print("🎉 ALL 100 QUESTIONS ARE PRESENT! COMPLETE DATASET ACHIEVED!")
    
    # Save merged data
    output_file = "GS Prelims 2024_COMPLETE_100_QUESTIONS.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Complete dataset saved to: {output_file}")
    
    # Save missing questions analysis
    if missing_questions:
        missing_data = {
            "metadata": {
                "analysis_date": datetime.now().isoformat(),
                "total_questions_found": total_questions,
                "missing_count": len(missing_questions),
                "note": "Questions still missing after final merge"
            },
            "missing_questions": missing_questions
        }
        
        missing_file = "FINAL_MISSING_questions.json"
        with open(missing_file, 'w', encoding='utf-8') as f:
            json.dump(missing_data, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Missing questions analysis saved to: {missing_file}")
    else:
        print("🎯 No missing questions analysis needed - dataset is complete!")
    
    print("\n✅ Final merge completed successfully!")

if __name__ == "__main__":
    main() 