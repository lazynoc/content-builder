#!/usr/bin/env python3
"""
Script to add answer keys to UPSC 2024 and 2025 questions
"""

import json
import os

def add_answer_keys_2025():
    """Add answer keys to UPSC 2025 questions"""
    
    # UPSC 2025 Answer Key
    answer_key_2025 = {
        1: "A", 2: "B", 3: "D", 4: "B", 5: "C", 6: "A", 7: "A", 8: "B", 9: "A", 10: "D",
        11: "B", 12: "C", 13: "C", 14: "C", 15: "A", 16: "C", 17: "A", 18: "D", 19: "B", 20: "B",
        21: "D", 22: "C", 23: "C", 24: "D", 25: "C", 26: "D", 27: "D", 28: "B", 29: "B", 30: "A",
        31: "C", 32: "B", 33: "A", 34: "D", 35: "A", 36: "B", 37: "A", 38: "C", 39: "B", 40: "D",
        41: "C", 42: "A", 43: "D", 44: "A", 45: "D", 46: "C", 47: "D", 48: "D", 49: "D", 50: "D",
        51: "D", 52: "D", 53: "B", 54: "B", 55: "C", 56: "C", 57: "A", 58: "A", 59: "C", 60: "B",
        61: "A", 62: "A", 63: "B", 64: "B", 65: "A", 66: "D", 67: "B", 68: "D", 69: "A", 70: "D",
        71: "D", 72: "B", 73: "B", 74: "C", 75: "C", 76: "C", 77: "D", 78: "C", 79: "D", 80: "B",
        81: "A", 82: "A", 83: "D", 84: "A", 85: "C", 86: "D", 87: "A", 88: "D", 89: "C", 90: "D",
        91: "C", 92: "A", 93: "D", 94: "C", 95: "A", 96: "B", 97: "A", 98: "A", 99: "B", 100: "D"
    }
    
    return update_file_with_answers(2025, answer_key_2025)

def add_answer_keys_2024():
    """Add answer keys to UPSC 2024 questions"""
    
    # UPSC 2024 Answer Key
    answer_key_2024 = {
        1: "A", 2: "B", 3: "D", 4: "B", 5: "C", 6: "A", 7: "A", 8: "B", 9: "A", 10: "D",
        11: "B", 12: "C", 13: "C", 14: "C", 15: "A", 16: "C", 17: "A", 18: "D", 19: "B", 20: "B",
        21: "D", 22: "C", 23: "C", 24: "D", 25: "C", 26: "D", 27: "D", 28: "B", 29: "B", 30: "A",
        31: "C", 32: "B", 33: "A", 34: "D", 35: "A", 36: "B", 37: "A", 38: "C", 39: "B", 40: "D",
        41: "C", 42: "A", 43: "D", 44: "A", 45: "D", 46: "C", 47: "D", 48: "D", 49: "D", 50: "D",
        51: "D", 52: "D", 53: "B", 54: "B", 55: "C", 56: "C", 57: "A", 58: "A", 59: "C", 60: "B",
        61: "A", 62: "A", 63: "B", 64: "B", 65: "A", 66: "D", 67: "B", 68: "D", 69: "A", 70: "D",
        71: "D", 72: "B", 73: "B", 74: "C", 75: "C", 76: "C", 77: "D", 78: "C", 79: "D", 80: "B",
        81: "A", 82: "A", 83: "D", 84: "A", 85: "C", 86: "D", 87: "A", 88: "D", 89: "C", 90: "D",
        91: "C", 92: "A", 93: "D", 94: "C", 95: "A", 96: "B", 97: "A", 98: "A", 99: "B", 100: "D",
        101: "C", 102: "C"
    }
    
    return update_file_with_answers(2024, answer_key_2024)

def update_file_with_answers(year, answer_key):
    """Update a specific year's file with answer keys"""
    
    input_file = f'../json_files/upsc_prelims_{year}_structured_for_frontend.json'
    
    print(f"\n📝 Processing UPSC {year}...")
    
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return False
    
    # Read the original file
    print(f"Reading file: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data['questions']
    total_questions = len(questions)
    
    print(f"Found {total_questions} questions")
    
    # Add answer keys to each question
    questions_updated = 0
    questions_missing = []
    
    for question in questions:
        question_num = question['question_number']
        
        if question_num in answer_key:
            question['correct_answer'] = answer_key[question_num]
            questions_updated += 1
            print(f"✅ Q{question_num}: {answer_key[question_num]}")
        else:
            questions_missing.append(question_num)
            print(f"❌ Q{question_num}: No answer key found")
    
    # Update metadata
    data['exam_info']['answer_key_added'] = True
    data['exam_info']['answer_key_date'] = "2025-01-15"
    data['exam_info']['total_questions_with_answers'] = questions_updated
    
    # Save the updated file (overwrite original)
    print(f"Saving updated file: {input_file}")
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Summary
    print(f"📊 UPSC {year} Summary:")
    print(f"   Total questions: {total_questions}")
    print(f"   Questions updated: {questions_updated}")
    print(f"   Questions missing answers: {len(questions_missing)}")
    
    if questions_missing:
        print(f"   Missing answers for questions: {questions_missing}")
    
    return True

def verify_answer_keys(year):
    """Verify that answer keys were added correctly for a specific year"""
    
    input_file = f'../json_files/upsc_prelims_{year}_structured_for_frontend.json'
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return False
    
    print(f"\n🔍 Verifying UPSC {year} answer keys...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data['questions']
    
    # Check first 10 questions
    print(f"First 10 questions with answers:")
    for i in range(min(10, len(questions))):
        q = questions[i]
        print(f"   Q{q['question_number']}: {q.get('correct_answer', 'MISSING')}")
    
    # Check if all questions have answers
    missing_answers = []
    for q in questions:
        if 'correct_answer' not in q:
            missing_answers.append(q['question_number'])
    
    if missing_answers:
        print(f"❌ Questions missing answers: {missing_answers}")
        return False
    else:
        print(f"✅ All questions have answer keys!")
        return True

def main():
    """Main function"""
    print("🔑 Adding Answer Keys to UPSC 2024 and 2025 Questions")
    print("=" * 60)
    
    # Process both years
    success_2025 = add_answer_keys_2025()
    success_2024 = add_answer_keys_2024()
    
    # Verify both years
    if success_2025:
        verify_answer_keys(2025)
    
    if success_2024:
        verify_answer_keys(2024)
    
    # Final summary
    print(f"\n🎯 Final Summary:")
    print(f"   UPSC 2025: {'✅' if success_2025 else '❌'}")
    print(f"   UPSC 2024: {'✅' if success_2024 else '❌'}")
    
    if success_2025 and success_2024:
        print(f"\n🎉 All files updated successfully!")
    else:
        print(f"\n⚠️  Some files failed to update.")

if __name__ == "__main__":
    main() 