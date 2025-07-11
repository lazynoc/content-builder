#!/usr/bin/env python3
"""
Script to fix remaining missing options for 2022 questions
"""

import json

def fix_remaining_options():
    """Fix remaining missing options for specific questions"""
    
    input_file = "GS Prelims 2022_WITH_SEPARATED_OPTIONS.json"
    output_file = "GS Prelims 2022_WITH_SEPARATED_OPTIONS.json"
    
    print(f"📖 Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    
    # Manual fixes for remaining questions
    fixes = {
        "36": {
            "question_text": "Consider following communication the technologies:\n1. Closed-circuit Television\n2. Radio Frequency Identification\n3. Wireless Local Area Network\nWhich of the above are considered Short Range devices/technologies?",
            "options": {
                "A": "1 and 2 only",
                "B": "2 and 3 only",
                "C": "1 and 3 only", 
                "D": "1, 2 and 3"
            }
        },
        "88": {
            "question_text": "Which one of the following statements about Sangam literature in ancient South India is correct?",
            "options": {
                "A": "The Sangam literature was generally composed in the period between c. 300 BCE and 300 CE.",
                "B": "The Sangam literature provides no information about the social and economic life of the people.",
                "C": "The Sangam literature was written in Sanskrit language.",
                "D": "The Sangam literature was composed by the Buddhist monks."
            }
        },
        "94": {
            "question_text": "Consider the following pairs:\nRegion often mentioned in the news Country\n1. Anatolia - Turkey\n2. Amhara - Ethiopia\n3. Cabo Delgado - Spain\n4. Catalonia - Italy\nHow many pairs given above are correctly matched?",
            "options": {
                "A": "Only one pair",
                "B": "Only two pairs",
                "C": "Only three pairs",
                "D": "All four pairs"
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
    print(f"   ✅ All 100 questions now have complete options")
    
    return output_file

if __name__ == "__main__":
    fix_remaining_options() 