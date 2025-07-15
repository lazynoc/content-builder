import json
import re

def parse_raw_questions(raw_file):
    """Parse questions from raw markdown file"""
    with open(raw_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by QUESTION blocks
    question_blocks = re.split(r'QUESTION (\d+)', content)[1:]  # Skip first empty part
    
    questions = []
    for i in range(0, len(question_blocks), 2):
        if i + 1 < len(question_blocks):
            question_num = int(question_blocks[i])
            question_content = question_blocks[i + 1].strip()
            
            # Extract metadata and question text
            lines = question_content.split('\n')
            
            # Find difficulty, subject, exam_info
            difficulty = "Medium"  # default
            subject = "General Studies"  # default
            exam_info = "Prelims 2024"
            
            question_text = ""
            options = []
            current_section = "metadata"
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line in ["Easy", "Medium", "Hard"]:
                    difficulty = line
                elif line in ["Physical Geography", "Ancient History", "Indian Polity", "World Geography", 
                            "Science & Technology", "Economy", "International Relations", "Modern History",
                            "Environment", "Current Affairs", "Indian Economy", "Geography", "History"]:
                    subject = line
                elif line == "Prelims 2024":
                    exam_info = line
                elif line in ["A", "B", "C", "D"]:
                    current_section = "options"
                    options.append({"letter": line, "text": ""})
                elif current_section == "options" and options:
                    # Handle multi-line option text
                    if options[-1]["text"]:
                        options[-1]["text"] += " " + line
                    else:
                        options[-1]["text"] = line
                else:
                    # This is question text - preserve all content
                    if question_text:
                        question_text += "\n" + line
                    else:
                        question_text = line
            
            # Clean up question text and options
            question_text = question_text.strip()
            for option in options:
                option["text"] = option["text"].strip()
            
            questions.append({
                "question_number": question_num,
                "question_text": question_text,
                "difficulty": difficulty,
                "subject": subject,
                "exam_info": exam_info,
                "options": options
            })
    
    return questions

# Test the parsing
questions = parse_raw_questions('raw_questions_dump_pyq_2023.md')
print(f"Found {len(questions)} questions")

# Show first 3 questions to verify parsing
for i, q in enumerate(questions[:3]):
    print(f"\n=== Question {q['question_number']} ===")
    print(f"Difficulty: {q['difficulty']}")
    print(f"Subject: {q['subject']}")
    print(f"Question text: {q['question_text'][:100]}...")
    print(f"Options: {len(q['options'])} options")
    for opt in q['options']:
        print(f"  {opt['letter']}: {opt['text'][:50]}...") 