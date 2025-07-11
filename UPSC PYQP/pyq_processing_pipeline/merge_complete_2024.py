import json
from pathlib import Path
from datetime import datetime

def merge_questions():
    """Merge original questions with missing questions to create complete dataset."""
    
    # Load original questions
    with open("GS Prelims 2024 _PYQ_ONLY_chunked.json", 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    # Load missing questions
    with open("GS Prelims 2024_MISSING_questions.json", 'r', encoding='utf-8') as f:
        missing_data = json.load(f)
    
    original_questions = original_data.get('questions', [])
    missing_questions = missing_data.get('questions', [])
    
    print(f"📊 MERGING QUESTIONS:")
    print(f"   Original questions: {len(original_questions)}")
    print(f"   Missing questions: {len(missing_questions)}")
    print(f"   Total after merge: {len(original_questions) + len(missing_questions)}")
    
    # Combine all questions
    all_questions = original_questions + missing_questions
    
    # Sort by question number
    all_questions.sort(key=lambda x: int(x.get('question_number', 0)) if x.get('question_number', '0').isdigit() else float('inf'))
    
    # Update extraction order
    for i, question in enumerate(all_questions):
        question['extraction_order'] = i + 1
    
    # Create complete dataset
    complete_data = {
        "metadata": {
            "pdf_name": "GS Prelims 2024 .pdf",
            "extraction_date": datetime.now().isoformat(),
            "total_questions": len(all_questions),
            "extraction_method": "chunked_ocr_chat + targeted_page_extraction",
            "original_extracted": len(original_questions),
            "missing_extracted": len(missing_questions),
            "note": "Complete 2024 GS Prelims questions - original + missing questions merged"
        },
        "questions": all_questions
    }
    
    # Save complete dataset
    output_path = "GS Prelims 2024_COMPLETE_questions.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(complete_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ MERGE COMPLETE!")
    print(f"   Complete dataset saved to: {output_path}")
    
    # Show question numbers
    question_numbers = [int(q.get('question_number', 0)) for q in all_questions if q.get('question_number', '0').isdigit()]
    question_numbers.sort()
    
    print(f"\n📝 QUESTION NUMBERS IN COMPLETE DATASET:")
    print(f"   Total: {len(question_numbers)} questions")
    print(f"   Range: Q{min(question_numbers)} to Q{max(question_numbers)}")
    
    # Check for gaps
    expected_numbers = set(range(1, 101))
    actual_numbers = set(question_numbers)
    missing_numbers = sorted(expected_numbers - actual_numbers)
    
    if missing_numbers:
        print(f"\n❌ STILL MISSING QUESTIONS:")
        print(f"   Numbers: {missing_numbers}")
        print(f"   Count: {len(missing_numbers)}")
    else:
        print(f"\n🎉 PERFECT! All 100 questions extracted!")
    
    return complete_data

def main():
    merge_questions()

if __name__ == "__main__":
    main()