import json

# Load the complete questions file
with open('GS Prelims 2024 _complete_questions.json', 'r') as f:
    data = json.load(f)

questions = data['questions']

print("Question numbers in order:")
for i, q in enumerate(questions):
    chunk_info = q.get('chunk_number', 'original')
    print(f"{i+1:3d}. Question {q['question_number']} (chunk: {chunk_info})")

print("\nNew questions (chunk 999) at positions:")
new_positions = []
for i, q in enumerate(questions):
    if q.get('chunk_number') == 999:
        new_positions.append(i+1)
        print(f"Position {i+1}: Question {q['question_number']}")

print(f"\nNew questions inserted at positions: {new_positions}")

# Check if they're in the right order
question_numbers = [int(q['question_number']) for q in questions if q['question_number'].isdigit()]
print(f"\nAll question numbers: {question_numbers[:20]}...{question_numbers[-20:]}")
print(f"Questions 18-21 present: {all(i in question_numbers for i in [18,19,20,21])}")
print(f"Question 44 present: {44 in question_numbers}") 