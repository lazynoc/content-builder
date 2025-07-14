#!/usr/bin/env python3
"""
Script to add correct answer keys to UPSC questions
"""

import json

# Answer keys
answer_key_2025 = {
    1: 'A', 2: 'B', 3: 'D', 4: 'B', 5: 'C', 6: 'A', 7: 'A', 8: 'B', 9: 'A', 10: 'D',
    11: 'B', 12: 'C', 13: 'C', 14: 'C', 15: 'A', 16: 'C', 17: 'A', 18: 'D', 19: 'B', 20: 'B',
    21: 'D', 22: 'C', 23: 'C', 24: 'D', 25: 'C', 26: 'D', 27: 'D', 28: 'B', 29: 'B', 30: 'A',
    31: 'C', 32: 'B', 33: 'A', 34: 'D', 35: 'A', 36: 'B', 37: 'A', 38: 'C', 39: 'B', 40: 'D',
    41: 'C', 42: 'A', 43: 'D', 44: 'A', 45: 'D', 46: 'C', 47: 'D', 48: 'D', 49: 'D', 50: 'D',
    51: 'D', 52: 'D', 53: 'B', 54: 'B', 55: 'C', 56: 'C', 57: 'A', 58: 'A', 59: 'C', 60: 'B',
    61: 'A', 62: 'A', 63: 'B', 64: 'B', 65: 'A', 66: 'D', 67: 'B', 68: 'D', 69: 'A', 70: 'D',
    71: 'D', 72: 'B', 73: 'B', 74: 'C', 75: 'C', 76: 'C', 77: 'D', 78: 'C', 79: 'D', 80: 'B',
    81: 'A', 82: 'A', 83: 'D', 84: 'A', 85: 'C', 86: 'D', 87: 'A', 88: 'D', 89: 'C', 90: 'D',
    91: 'C', 92: 'A', 93: 'D', 94: 'C', 95: 'A', 96: 'B', 97: 'A', 98: 'A', 99: 'B', 100: 'D'
}

answer_key_2024 = {
    1: 'A', 2: 'B', 3: 'D', 4: 'B', 5: 'C', 6: 'A', 7: 'A', 8: 'B', 9: 'A', 10: 'D',
    11: 'B', 12: 'C', 13: 'C', 14: 'C', 15: 'A', 16: 'C', 17: 'A', 18: 'D', 19: 'B', 20: 'B',
    21: 'D', 22: 'C', 23: 'C', 24: 'D', 25: 'C', 26: 'D', 27: 'D', 28: 'B', 29: 'B', 30: 'A',
    31: 'C', 32: 'B', 33: 'A', 34: 'D', 35: 'A', 36: 'B', 37: 'A', 38: 'C', 39: 'B', 40: 'D',
    41: 'C', 42: 'A', 43: 'D', 44: 'A', 45: 'D', 46: 'C', 47: 'D', 48: 'D', 49: 'D', 50: 'D',
    51: 'D', 52: 'D', 53: 'B', 54: 'B', 55: 'C', 56: 'C', 57: 'A', 58: 'A', 59: 'C', 60: 'B',
    61: 'A', 62: 'A', 63: 'B', 64: 'B', 65: 'A', 66: 'D', 67: 'B', 68: 'D', 69: 'A', 70: 'D',
    71: 'D', 72: 'B', 73: 'B', 74: 'C', 75: 'C', 76: 'C', 77: 'D', 78: 'C', 79: 'D', 80: 'B',
    81: 'A', 82: 'A', 83: 'D', 84: 'A', 85: 'C', 86: 'D', 87: 'A', 88: 'D', 89: 'C', 90: 'D',
    91: 'C', 92: 'A', 93: 'D', 94: 'C', 95: 'A', 96: 'B', 97: 'A', 98: 'A', 99: 'B', 100: 'D',
    101: 'C', 102: 'C'
}

def add_correct_answers(input_file, output_file, year):
    """Add correct answers to questions based on year"""
    
    # Select answer key based on year
    if year == 2025:
        answer_key = answer_key_2025
    elif year == 2024:
        answer_key = answer_key_2024
    else:
        print(f"No answer key available for year {year}")
        return
    
    # Load the JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Add correct answers to each question
    questions_updated = 0
    for question in data['questions']:
        q_num = question['question_number']
        
        if q_num in answer_key:
            correct_answer = answer_key[q_num]
            question['correct_answer'] = correct_answer
            questions_updated += 1
            
            # Also mark the correct option
            for option in question['options']:
                if option['letter'].upper() == correct_answer:
                    option['is_correct'] = True
                else:
                    option['is_correct'] = False
        else:
            print(f"Warning: No answer found for question {q_num}")
    
    # Save the updated JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Updated {questions_updated} questions with correct answers")
    print(f"📁 Saved to: {output_file}")

def main():
    """Main function"""
    
    # Process 2025 questions
    print("Processing UPSC 2025 questions...")
    add_correct_answers(
        input_file='../json_files/upsc_prelims_2025_structured_for_frontend.json',
        output_file='../json_files/upsc_prelims_2025_with_answers.json',
        year=2025
    )
    
    # Check if 2024 file exists and process it
    import os
    if os.path.exists('../json_files/upsc_prelims_2024_structured_for_frontend.json'):
        print("\nProcessing UPSC 2024 questions...")
        add_correct_answers(
            input_file='../json_files/upsc_prelims_2024_structured_for_frontend.json',
            output_file='../json_files/upsc_prelims_2024_with_answers.json',
            year=2024
        )

if __name__ == "__main__":
    main()