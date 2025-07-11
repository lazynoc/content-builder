#!/usr/bin/env python3
"""
Script to fix question 93 by extracting options from question text
"""

import json

def fix_q93_options():
    """Fix question 93 by extracting options from question text"""
    
    input_file = "GS Prelims 2022_WITH_OPENAI_ANALYSIS.json"
    output_file = "GS Prelims 2022_WITH_OPENAI_ANALYSIS.json"
    
    print(f"📖 Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    
    # Find and fix question 93
    for question in questions:
        if question.get('question_number') == '93':
            print("🔧 Fixing question 93...")
            
            # Extract options from question text
            question_text = question.get('question_text', '')
            
            # The options are in the format: (a) text, (b) text, (c) text, (d) text
            options = {}
            
            # Extract option A
            if '(a)' in question_text:
                start = question_text.find('(a)') + 3
                end = question_text.find('(b)') if '(b)' in question_text else len(question_text)
                options['A'] = question_text[start:end].strip()
            
            # Extract option B
            if '(b)' in question_text:
                start = question_text.find('(b)') + 3
                end = question_text.find('(c)') if '(c)' in question_text else len(question_text)
                options['B'] = question_text[start:end].strip()
            
            # Extract option C
            if '(c)' in question_text:
                start = question_text.find('(c)') + 3
                end = question_text.find('(d)') if '(d)' in question_text else len(question_text)
                options['C'] = question_text[start:end].strip()
            
            # Extract option D
            if '(d)' in question_text:
                start = question_text.find('(d)') + 3
                end = len(question_text)
                options['D'] = question_text[start:end].strip()
            
            # Update the question
            question['options'] = options
            question['options_extracted'] = True
            
            print(f"✅ Fixed question 93 options: {options}")
            break
    
    # Save the updated file
    print(f"💾 Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("✅ Question 93 fixed successfully!")

if __name__ == "__main__":
    fix_q93_options() 