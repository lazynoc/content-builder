#!/usr/bin/env python3
"""
Fix UPSC 2025 Correct Answers
Update the correct_answer field for each question using the provided answer key
"""

import json

# UPSC 2025 Correct Answer Key
correct_answers_2025 = {
    1: "A", 2: "D", 3: "D", 4: "C", 5: "C", 6: "A", 7: "C", 8: "B", 9: "B", 10: "C",
    11: "A", 12: "A", 13: "A", 14: "D", 15: "D", 16: "B", 17: "B", 18: "A", 19: "C", 20: "A",
    21: "D", 22: "A", 23: "D", 24: "B", 25: "D", 26: "B", 27: "D", 28: "A", 29: "C", 30: "A",
    31: "A", 32: "B", 33: "C", 34: "A", 35: "B", 36: "B", 37: "A", 38: "B", 39: "D", 40: "C",
    41: "A", 42: "A", 43: "B", 44: "A", 45: "A", 46: "C", 47: "B", 48: "D", 49: "D", 50: "A",
    51: "B", 52: "D", 53: "A", 54: "C", 55: "C", 56: "C", 57: "C", 58: "D", 59: "D", 60: "B",
    61: "D", 62: "B", 63: "A", 64: "C", 65: "C", 66: "C", 67: "A", 68: "D", 69: "B", 70: "C",
    71: "B", 72: "A", 73: "C", 74: "C", 75: "D", 76: "A", 77: "B", 78: "A", 79: "C", 80: "A",
    81: "C", 82: "C", 83: "A", 84: "D", 85: "C", 86: "B", 87: "C", 88: "C", 89: "C", 90: "D",
    91: "C", 92: "C", 93: "D", 94: "C", 95: "B", 96: "A", 97: "D", 98: "D", 99: "A", 100: "D"
}

def fix_2025_answers():
    """Update correct answers for UPSC 2025"""
    
    # Load the 2025 file
    input_file = '../json_files/upsc_prelims_2025_structured_for_frontend.json'
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded {len(data['questions'])} questions from UPSC 2025")
        
        # Update correct answers
        updated_count = 0
        for question in data['questions']:
            question_num = question['question_number']
            if question_num in correct_answers_2025:
                old_answer = question.get('correct_answer', 'Not set')
                new_answer = correct_answers_2025[question_num]
                question['correct_answer'] = new_answer
                
                if old_answer != new_answer:
                    print(f"Q{question_num}: {old_answer} → {new_answer}")
                    updated_count += 1
            else:
                print(f"Warning: No answer found for Q{question_num}")
        
        # Update metadata
        data['exam_info']['answer_key_added'] = True
        data['exam_info']['answer_key_date'] = "2025-07-14"
        data['exam_info']['total_questions_with_answers'] = len(data['questions'])
        
        # Save updated file
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Updated {updated_count} questions")
        print(f"📁 File saved: {input_file}")
        
        # Verify a few answers
        print("\n📋 Sample verification:")
        for i in [1, 25, 50, 75, 100]:
            question = next((q for q in data['questions'] if q['question_number'] == i), None)
            if question:
                print(f"Q{i}: {question['correct_answer']}")
        
    except FileNotFoundError:
        print(f"❌ File not found: {input_file}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_2025_answers() 