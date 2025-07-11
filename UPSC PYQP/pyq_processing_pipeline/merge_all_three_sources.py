#!/usr/bin/env python3
"""
Comprehensive merge script to combine all three question sources:
1. Original complete file (GS Prelims 2024_COMPLETE_questions.json) - 81 questions
2. First missing batch (GS Prelims 2024_MISSING_questions.json) - original missing questions
3. Second missing batch (GS Prelims 2024_MISSING_questions_TRY_2.json) - latest missing questions

This will create a truly complete dataset with all questions from all sources.
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
    
    print("🔄 Starting comprehensive merge of all sources...")
    
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
        "extraction_method": "comprehensive_merge_all_sources",
        "source_files": source_files,
        "source_statistics": source_stats,
        "note": "Complete 2024 GS Prelims questions - all sources merged with deduplication"
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
        "GS Prelims 2024_COMPLETE_questions.json",
        "GS Prelims 2024_MISSING_questions.json", 
        "GS Prelims 2024_MISSING_questions_TRY_2.json"
    ]
    
    print("🚀 Starting comprehensive merge of all question sources...")
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
    print("📊 MERGE RESULTS:")
    print(f"✅ Total questions after merge: {total_questions}")
    print(f"❌ Missing questions: {len(missing_questions)}")
    
    if missing_questions:
        print(f"📋 Missing question numbers: {missing_questions}")
    else:
        print("🎉 All 100 questions are present!")
    
    # Save merged data
    output_file = "GS Prelims 2024_FINAL_COMPLETE_ALL_SOURCES.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Merged data saved to: {output_file}")
    
    # Save missing questions analysis
    if missing_questions:
        missing_data = {
            "metadata": {
                "analysis_date": datetime.now().isoformat(),
                "total_questions_found": total_questions,
                "missing_count": len(missing_questions),
                "note": "Questions still missing after comprehensive merge"
            },
            "missing_questions": missing_questions
        }
        
        missing_file = "FINAL_MISSING_questions.json"
        with open(missing_file, 'w', encoding='utf-8') as f:
            json.dump(missing_data, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Missing questions analysis saved to: {missing_file}")
    
    print("\n✅ Merge completed successfully!")

if __name__ == "__main__":
    main()