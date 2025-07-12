import json

# Load the JSON file
with open('uppsc_questions_complete_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get all question numbers
question_numbers = []
for question in data['questions']:
    question_numbers.append(int(question['question_number']))

# Sort the question numbers
question_numbers.sort()

print(f"Total questions found: {len(question_numbers)}")
print(f"Expected total: 150")
print(f"Questions with answers: {len([q for q in data['questions'] if 'correct_answer' in q])}")
print(f"Questions without answers: {len([q for q in data['questions'] if 'correct_answer' not in q])}")

# Check for missing question numbers
missing_numbers = []
for i in range(1, 151):
    if i not in question_numbers:
        missing_numbers.append(i)

if missing_numbers:
    print(f"\nMissing question numbers: {missing_numbers}")
else:
    print(f"\n✅ All 150 questions are present!")

# Check for duplicates
duplicates = []
seen = set()
for num in question_numbers:
    if num in seen:
        duplicates.append(num)
    seen.add(num)

if duplicates:
    print(f"Duplicate question numbers: {duplicates}")
else:
    print("✅ No duplicate question numbers found")

# Show first and last question numbers
print(f"\nFirst question number: {min(question_numbers)}")
print(f"Last question number: {max(question_numbers)}")

# Show metadata
print(f"\nMetadata from file:")
print(f"- Total questions: {data['metadata']['total_questions']}")
print(f"- Questions with answers: {data['metadata']['questions_with_answers']}")
print(f"- Questions without answers: {data['metadata']['questions_without_answers']}") 