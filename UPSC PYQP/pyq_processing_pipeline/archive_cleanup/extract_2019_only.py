import os
import json
import base64
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from mistralai import Mistral
from pydantic import BaseModel, Field

# --- CONFIG ---
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
OUTPUT_DIR = Path(__file__).parent

# --- QUESTION SCHEMA ---
class PYQQuestionHybrid(BaseModel):
    question_number: str = Field(..., description="Question number (e.g., 1, 2, 3)")
    section: str = Field(..., description="Subject section (e.g., Polity & Governance, Geography)")
    question_text: str = Field(..., description="The actual question text with options (a), (b), (c), (d)")
    correct_answer: str = Field(..., description="Correct answer option (A, B, C, or D)")
    explanation: str = Field(..., description="Detailed explanation of the answer")
    motivation: str = Field(..., description="Current affairs context or motivation")
    difficulty_level: str = Field(..., description="Difficulty level (E=Easy, M=Medium, D=Difficult)")
    question_nature: str = Field(..., description="Nature of question (F=Fundamental, FA=Fundamental Applied, CA=Current Affairs, etc.)")
    source_material: str = Field(..., description="Source book or material")
    source_type: str = Field(..., description="Type of source (EM=Essential Material, RM=Reference Material, etc.)")
    test_series_reference: str = Field(..., description="VisionIAS test series reference")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for the question")
    extraction_order: int = Field(default=0, description="Order of extraction")
    chunk_number: int = Field(default=0, description="Chunk number from which this question was extracted")

def extract_2019_missing_questions():
    """Extract missing questions for 2019."""
    
    year = 2019
    print(f"[{year}] Starting targeted extraction...")
    
    pdf_path = f"../PYQP With Answer/GS/GS Prelims {year}.pdf"
    if not os.path.exists(pdf_path):
        print(f"[{year}] PDF not found: {pdf_path}")
        return []
    
    with open(pdf_path, "rb") as pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    
    client = Mistral(api_key=MISTRAL_API_KEY)
    
    # 1. OCR the PDF
    print(f"[{year}] Running OCR...")
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_pdf}"
        },
        include_image_base64=False
    )
    
    # 2. Collect content from specific pages
    page_content_map = {}
    for i, page in enumerate(ocr_response.pages, 1):
        page_num = i
        content = page.markdown
        page_content_map[page_num] = content
    
    # 3. Define missing questions with page ranges
    missing_questions = [
        {'questions': [24], 'pages': [27, 28]},
        {'questions': [54, 55, 56, 57], 'pages': [56, 57, 58, 59, 60]}
    ]
    
    extracted_questions = []
    
    for q_group in missing_questions:
        question_numbers = q_group['questions']
        page_numbers = q_group['pages']
        
        print(f"[{year}] Processing questions {question_numbers} from pages {page_numbers}")
        
        # Get content from specific pages
        target_content = ""
        for page_num in page_numbers:
            if page_num in page_content_map:
                target_content += f"\n--- PAGE {page_num} ---\n{page_content_map[page_num]}\n"
        
        if not target_content:
            print(f"[{year}] No content found for pages {page_numbers}")
            continue
        
        # Extract each question number
        for q_num in question_numbers:
            print(f"[{year}] Looking for question {q_num}...")
            
            prompt = f"""
            Find and extract question number {q_num} from the following UPSC Prelims {year} content.
            
            Look for patterns like:
            - "{q_num}."
            - "{q_num})"
            - "Question {q_num}"
            
            Extract the complete question with all options and return as JSON:
            {{
                "question_number": "{q_num}",
                "section": "General Studies",
                "question_text": "complete question with options",
                "correct_answer": "A/B/C/D",
                "explanation": "detailed explanation",
                "motivation": "current affairs context",
                "difficulty_level": "Medium",
                "question_nature": "F",
                "source_material": "NCERT",
                "source_type": "EM",
                "test_series_reference": "VisionIAS Prelims Test Series {year}"
            }}
            
            Content to search:
            {target_content[:12000]}
            """
            
            try:
                import time
                start_time = time.time()
                
                chat_response = client.chat.complete(
                    model="mistral-large-latest",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    safe_prompt=True,
                    max_tokens=2000
                )
                
                elapsed_time = time.time() - start_time
                print(f"[{year}] Question {q_num} extracted in {elapsed_time:.2f}s")
                
                response_content = chat_response.choices[0].message.content
                if not isinstance(response_content, str):
                    response_content = str(response_content)
                
                parsed_data = json.loads(response_content)
                
                if 'question_number' in parsed_data:
                    parsed_data['question_number'] = str(parsed_data['question_number'])
                    
                    # Ensure all required fields are present
                    if 'test_series_reference' not in parsed_data or parsed_data['test_series_reference'] is None:
                        parsed_data['test_series_reference'] = f"VisionIAS Prelims Test Series {year}"
                    if 'motivation' not in parsed_data or parsed_data['motivation'] is None:
                        parsed_data['motivation'] = "Current affairs context"
                    if 'difficulty_level' not in parsed_data or parsed_data['difficulty_level'] is None:
                        parsed_data['difficulty_level'] = "Medium"
                    if 'question_nature' not in parsed_data or parsed_data['question_nature'] is None:
                        parsed_data['question_nature'] = "F"
                    if 'source_material' not in parsed_data or parsed_data['source_material'] is None:
                        parsed_data['source_material'] = "NCERT"
                    if 'source_type' not in parsed_data or parsed_data['source_type'] is None:
                        parsed_data['source_type'] = "EM"
                    
                    question = PYQQuestionHybrid(**parsed_data, extraction_order=q_num, chunk_number=999)
                    extracted_questions.append(question)
                    print(f"[{year}] Successfully extracted question {q_num}")
                        
            except Exception as e:
                print(f"[{year}] Error extracting question {q_num}: {e}")
                continue
    
    print(f"[{year}] Extracted {len(extracted_questions)} questions")
    return extracted_questions

def update_2019_json(new_questions: List[PYQQuestionHybrid]):
    """Update 2019 JSON file with new questions."""
    
    year = 2019
    existing_file = f"GS Prelims {year}_chunked_hybrid_questions.json"
    
    if not os.path.exists(existing_file):
        print(f"[{year}] No existing file found")
        return
    
    print(f"[{year}] Loading existing questions from {existing_file}...")
    with open(existing_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    existing_questions = data['questions']
    
    # Convert new questions to dict format
    new_dicts = [q.model_dump() for q in new_questions]
    
    # Merge and sort by question number
    all_questions = existing_questions + new_dicts
    
    # Sort by question number
    def sort_key(q):
        try:
            return int(q['question_number'])
        except (ValueError, KeyError):
            return float('inf')
    
    all_questions.sort(key=sort_key)
    
    # Update metadata
    data['questions'] = all_questions
    data['metadata']['total_questions'] = len(all_questions)
    data['metadata']['missing_questions_added'] = len(new_questions)
    data['metadata']['completion_date'] = datetime.now().isoformat()
    
    # Save as complete file
    output_file = f"GS Prelims {year}_complete_questions.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[{year}] Saved {len(all_questions)} questions to {output_file}")
    
    # Verify we have all questions 1-100
    question_numbers = [int(q['question_number']) for q in all_questions if q['question_number'].isdigit()]
    question_numbers.sort()
    missing = [i for i in range(1, 101) if i not in question_numbers]
    
    if missing:
        print(f"[{year}] Still missing questions: {missing}")
    else:
        print(f"[{year}] Success! All questions 1-100 are now present!")

def main():
    """Extract missing questions for 2019 only."""
    
    print("Starting targeted extraction for 2019...")
    
    # Extract missing questions
    missing_questions = extract_2019_missing_questions()
    
    if missing_questions:
        # Update existing JSON file
        update_2019_json(missing_questions)
    else:
        print("[2019] No missing questions were extracted")
    
    print("2019 extraction process finished!")

if __name__ == "__main__":
    main() 