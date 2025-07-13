import json
import os
import openai
from tqdm import tqdm
import time
import uuid
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../../.env')
openai.api_key = os.getenv('OPENAI_API_KEY')
MODEL = 'gpt-4.1-mini'
RAW_FILE = 'markdown_files/raw_questions_dump_pyq_2021.md'
OUTPUT_FILE = 'json_files/upsc_prelims_2021_structured_for_frontend.json'
YEAR = 2021

PROMPT = (
    "You are an expert at structuring UPSC exam questions for frontend display. "
    "Analyze the given question and return a JSON object with the best structure.\n"
    "- Order the fields as: id, question_number, type, difficulty, subject, exam_info, question_text, options.\n"
    "- If the question contains a table, list, or special formatting, structure it accordingly.\n"
    "- Always include 'question_text', 'options', 'difficulty', 'subject', and 'exam_info'.\n"
    "- Use 'type' to indicate the question type (e.g., 'mcq', 'table_mcq', 'list_mcq').\n"
    "- Include 'question_number' (the sequential number) and 'id' (unique UUID identifier).\n"
    "- Output ONLY the JSON object, no additional text."
)

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
            exam_info = f"Prelims {YEAR}"
            
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

def call_openai_single_question(question, question_number):
    """Process a single question with OpenAI"""
    # Add UUID ID
    question_data = question.copy()
    question_data['id'] = str(uuid.uuid4())
    question_data['question_number'] = question_number
    
    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": json.dumps(question_data, ensure_ascii=False)}
    ]
    
    for attempt in range(3):
        try:
            response = openai.chat.completions.create(
                model=MODEL,
                messages=messages,  # type: ignore
                temperature=0.0,
                max_tokens=800
            )
            content = response.choices[0].message.content
            if content is not None:
                try:
                    improved = json.loads(content)
                    if isinstance(improved, dict):
                        return improved
                except Exception:
                    start = content.find('{')
                    end = content.rfind('}')
                    if start != -1 and end != -1:
                        try:
                            improved = json.loads(content[start:end+1])
                            if isinstance(improved, dict):
                                return improved
                        except Exception:
                            pass
            return None
        except Exception as e:
            print(f"OpenAI API error: {e}. Retrying...")
            time.sleep(5)
    print(f"Failed to get response from OpenAI after 3 attempts for question {question_number}")
    return None

def save_results(results):
    """Save results to file with metadata header"""
    metadata = {
        "exam_info": {
            "exam_name": "UPSC Civil Services Preliminary Examination",
            "year": YEAR,
            "paper": "General Studies Paper I",
            "total_questions": len(results),
            "processing_date": datetime.now().isoformat(),
            "version": "1.0"
        },
        "questions": results
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

def main():
    print("Parsing raw questions from markdown file...")
    questions = parse_raw_questions(RAW_FILE)
    print(f"Found {len(questions)} questions in raw file")
    
    processed_questions = []
    
    # Process questions one by one
    for i, question in enumerate(tqdm(questions, desc="Processing questions")):
        print(f"\nProcessing question {question['question_number']} ({i+1}/{len(questions)})")
        
        # Process with OpenAI
        improved_question = call_openai_single_question(question, question['question_number'])
        
        if improved_question:
            processed_questions.append(improved_question)
            # Save after each successful processing
            save_results(processed_questions)
            print(f"✓ Question {question['question_number']} processed and saved")
        else:
            print(f"✗ Failed to process question {question['question_number']}")
        
        time.sleep(1)
    
    print(f"\nProcessing complete!")
    print(f"Total questions processed: {len(processed_questions)}")
    print(f"Results saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main() 