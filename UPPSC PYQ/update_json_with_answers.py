#!/usr/bin/env python3
"""
Update existing UPPSC questions JSON with correct answers
This script adds the correct_answer field to each question in the existing JSON file.
"""

import json
from pathlib import Path

# --- ANSWER KEY ---
ANSWER_KEY = {
    "1": "A", "2": "B", "3": "D", "4": "C", "5": "D", "6": "A", "7": "D", "8": "A", "9": "C", "10": "D",
    "11": "A", "12": "D", "13": "A", "14": "D", "15": "D", "16": "A", "17": "C", "18": "A", "19": "B", "20": "A",
    "21": "C", "22": "A", "23": "B", "24": "D", "25": "C", "26": "D", "27": "A", "28": "B", "29": "B", "30": "C",
    "31": "B", "32": "C", "33": "C", "34": "C", "35": "B", "36": "A", "37": "C", "38": "B", "39": "C", "40": "B",
    "41": "A", "42": "A", "43": "C", "44": "D", "45": "A", "46": "C", "47": "D", "48": "C", "49": "A", "50": "D",
    "51": "B", "52": "B", "53": "B", "54": "C", "55": "A", "56": "B", "57": "B", "58": "C", "59": "B", "60": "B",
    "61": "B", "62": "C", "63": "A", "64": "B", "65": "D", "66": "D", "67": "C", "68": "A", "69": "D", "70": "C",
    "71": "B", "72": "A", "73": "A", "74": "D", "75": "A", "76": "A", "77": "D", "78": "B", "79": "D", "80": "A",
    "81": "D", "82": "D", "83": "C", "84": "D", "85": "A", "86": "D", "87": "A", "88": "C", "89": "D", "90": "D",
    "91": "B", "92": "C", "93": "C", "94": "D", "95": "A", "96": "A", "97": "A", "98": "A", "99": "B", "100": "B",
    "101": "D", "102": "C", "103": "A", "104": "D", "105": "C", "106": "C", "107": "B", "108": "A", "109": "C", "110": "D",
    "111": "D", "112": "B", "113": "D", "114": "A", "115": "A", "116": "D", "117": "B", "118": "D", "119": "C", "120": "B",
    "121": "B", "122": "A", "123": "B", "124": "D", "125": "D", "126": "C", "127": "D", "128": "C", "129": "D", "130": "D",
    "131": "B", "132": "C", "133": "B", "134": "C", "135": "C", "136": "B", "137": "A", "138": "A", "139": "B", "140": "A",
    "141": "B", "142": "B", "143": "D", "144": "B", "145": "D", "146": "D", "147": "A", "148": "C", "149": "B", "150": "C"
}

def update_json_with_answers():
    """Update the existing JSON file with correct answers."""
    
    input_file = "uppsc_questions_chat_complete.json"
    output_file = "uppsc_questions_with_answers.json"
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found!")
        return
    
    try:
        # Load existing JSON
        print(f"📖 Loading existing JSON from {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        questions = data.get('questions', [])
        print(f"📊 Found {len(questions)} questions to update")
        
        # Update each question with correct answer
        updated_count = 0
        missing_answers = []
        
        for question in questions:
            question_num = question.get('question_number', '')
            
            if question_num in ANSWER_KEY:
                question['correct_answer'] = ANSWER_KEY[question_num]
                updated_count += 1
                print(f"✅ Q{question_num}: Added answer {ANSWER_KEY[question_num]}")
            else:
                question['correct_answer'] = "Unknown"
                missing_answers.append(question_num)
                print(f"❓ Q{question_num}: No answer found in key")
        
        # Update metadata
        data['metadata']['answer_key_added'] = True
        data['metadata']['questions_with_answers'] = updated_count
        data['metadata']['questions_without_answers'] = len(missing_answers)
        data['metadata']['missing_question_numbers'] = missing_answers
        
        # Save updated JSON
        print(f"\n💾 Saving updated JSON to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Summary
        print(f"\n🎉 UPDATE COMPLETE!")
        print(f"📊 Total questions: {len(questions)}")
        print(f"✅ Questions with answers: {updated_count}")
        print(f"❓ Questions without answers: {len(missing_answers)}")
        
        if missing_answers:
            print(f"📋 Missing answers for questions: {missing_answers}")
        
        # Show sample questions with answers
        print(f"\n📝 SAMPLE QUESTIONS WITH ANSWERS:")
        for i, q in enumerate(questions[:5]):
            print(f"   Q{q['question_number']}: {q['question_text'][:60]}...")
            print(f"   Answer: {q['correct_answer']}")
            print()
        
        print(f"💾 Updated JSON saved to: {output_file}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_json_with_answers() 