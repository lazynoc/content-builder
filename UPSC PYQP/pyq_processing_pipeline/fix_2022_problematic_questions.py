#!/usr/bin/env python3
"""
Script to manually fix the 3 problematic 2022 questions (13, 16, 20)
that have truncated question text and missing options
"""

import json
import os

def fix_problematic_questions():
    """Fix the 3 problematic questions manually"""
    
    input_file = "GS Prelims 2022_FIXED_FOR_ANALYSIS.json"
    output_file = "GS Prelims 2022_FIXED_FOR_ANALYSIS.json"
    
    print(f"📖 Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    
    # Manual fixes for the problematic questions
    fixes = {
        "13": {
            "question_text": "Consider the following statements:\n1. A bill amending the Constitution requires a prior recommendation of the President of India.\n2. A Constitution Amendment Bill must be passed by both Lok Sabha and Rajya Sabha by a special majority and there is no provision for joint sitting.\nWhich of the statements given above is/are correct?\n(a) 1 only\n(b) 2 only\n(c) Both 1 and 2\n(d) Neither 1 nor 2",
            "options": {
                "A": "1 only",
                "B": "2 only", 
                "C": "Both 1 and 2",
                "D": "Neither 1 nor 2"
            }
        },
        "16": {
            "question_text": "With reference to anti-defection law in India, consider the following statements:\n1. The law specifies that a nominated legislator cannot join any political party within six months of being appointed to the House.\n2. The law does not provide any time-frame within which the presiding officer has to decide a disqualification case.\nWhich of the statements given above is/are correct?\n(a) 1 only\n(b) 2 only\n(c) Both 1 and 2\n(d) Neither 1 nor 2",
            "options": {
                "A": "1 only",
                "B": "2 only",
                "C": "Both 1 and 2", 
                "D": "Neither 1 nor 2"
            }
        },
        "20": {
            "question_text": "With reference to Deputy Speaker of Lok Sabha, consider the following statements:\n1. As per the Rules of Procedure and Conduct of Business in Lok Sabha, the election of Deputy Speaker shall be held on such date as the Speaker may fix.\n2. There is a mandatory provision that the election of Deputy Speaker of Lok Sabha must be held within six months from the date of election of the Speaker.\n3. The Deputy Speaker has the same power as of the Speaker when presiding over a sitting of the House and no appeal lies against his rulings.\n4. The well established parliamentary practice regarding the appointment of Deputy Speaker is that the motion is moved by the Speaker and duly seconded by the Prime Minister.\nWhich of the statements given above are correct?\n(a) 1 and 3 only\n(b) 1, 2 and 4 only\n(c) 3 and 4 only\n(d) 2 and 3 only",
            "options": {
                "A": "1 and 3 only",
                "B": "1, 2 and 4 only",
                "C": "3 and 4 only",
                "D": "2 and 3 only"
            }
        }
    }
    
    fixed_count = 0
    for question in questions:
        question_num = question.get('question_number')
        if question_num in fixes:
            print(f"🔧 Fixing Question {question_num}...")
            
            # Apply the fix
            fix_data = fixes[question_num]
            question['question_text'] = fix_data['question_text']
            question['options'] = fix_data['options']
            question['options_extracted'] = True
            
            print(f"  ✅ Fixed question text and options")
            fixed_count += 1
    
    # Save the fixed file
    print(f"\n💾 Saving fixed file: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📈 Summary:")
    print(f"   ✅ Questions fixed: {fixed_count}")
    print(f"   ✅ All 100 questions now ready for OpenAI analysis")
    
    return output_file

if __name__ == "__main__":
    fix_problematic_questions() 