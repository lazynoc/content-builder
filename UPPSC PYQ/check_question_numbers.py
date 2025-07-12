#!/usr/bin/env python3
"""
Script to count, list, and check for duplicate/missing question numbers in the enhanced file
"""
import json
from collections import Counter

with open('uppsc_questions_complete_enhanced.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

question_numbers = [int(q['question_number']) for q in data['questions']]

print(f"Total questions: {len(question_numbers)}")
print(f"Min question number: {min(question_numbers)}")
print(f"Max question number: {max(question_numbers)}")
print(f"Unique question numbers: {len(set(question_numbers))}")

# Check for duplicates
counter = Counter(question_numbers)
duplicates = [num for num, count in counter.items() if count > 1]
if duplicates:
    print(f"Duplicate question numbers: {duplicates}")
else:
    print("No duplicate question numbers.")

# Check for missing
missing = [n for n in range(1, max(question_numbers)+1) if n not in question_numbers]
if missing:
    print(f"Missing question numbers: {missing}")
else:
    print("No missing question numbers.") 