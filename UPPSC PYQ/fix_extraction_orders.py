#!/usr/bin/env python3
"""
Script to fix extraction_order values after adding question 86
"""

import json
import re

def fix_extraction_orders():
    # Read the JSON file
    with open('uppsc_questions_complete_final.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Update extraction_order for questions 87-150 (increment by 1)
    for question in data['questions']:
        question_num = int(question['question_number'])
        if question_num >= 87:
            current_order = question['extraction_order']
            question['extraction_order'] = current_order + 1
            print(f"Updated Q{question_num}: extraction_order {current_order} -> {current_order + 1}")
    
    # Write back to file
    with open('uppsc_questions_complete_final.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Extraction orders updated successfully!")

if __name__ == "__main__":
    fix_extraction_orders() 