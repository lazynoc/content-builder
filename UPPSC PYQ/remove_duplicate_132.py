#!/usr/bin/env python3
"""
Script to remove duplicate Q132 from the enhanced file, keeping only the first occurrence, and update metadata to 150.
"""
import json

with open('uppsc_questions_complete_enhanced.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

seen = set()
unique_questions = []
for q in data['questions']:
    qnum = int(q['question_number'])
    if qnum != 132 or 132 not in seen:
        unique_questions.append(q)
    seen.add(qnum)

# Update metadata
if 'metadata' in data:
    data['metadata']['total_questions'] = 150
    data['metadata']['note'] = data['metadata'].get('note', '') + ' | Removed duplicate Q132.'

data['questions'] = unique_questions

with open('uppsc_questions_complete_enhanced.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Duplicate Q132 removed. File now has 150 unique questions.") 