#!/usr/bin/env python3
"""
Extract remaining missing questions from 2022 that weren't found in the first extraction
"""

import json
import os
import sys
import uuid
import base64
import re
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

# --- PYQ QUESTION SCHEMA ---
class PYQQuestion(BaseModel):
    question_number: str = Field(..., description="Question number (e.g., 1, 2, 3)")
    section: str = Field(..., description="Subject section (e.g., Polity & Governance, Geography)")
    question_text: str = Field(..., description="The actual question text with options (a), (b), (c), (d)")
    correct_answer: str = Field(..., description="Correct answer option (A, B, C, or D)")
    explanation: str = Field(..., description="Detailed explanation of the answer")
    motivation: str = Field(..., description="Current affairs context or motivation")
    difficulty_level: str = Field(..., description="Difficulty level (E=Easy, M=Medium, D=Difficult)")
    question_nature: str = Field(..., description="Nature of question (F=Fundamental, FA=Fundamental Applied, CA=Current Affairs, etc.)")
    source_material: str = Field(default="", description="Source book or material")
    source_type: str = Field(default="", description="Type of source (EM=Essential Material, RM=Reference Material, etc.)")
    test_series_reference: str = Field(default="", description="VisionIAS test series reference")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for the question")
    extraction_order: int = Field(default=0, description="Order of extraction")
    chunk_number: int = Field(default=0, description="Chunk number from which this question was extracted")
    page_range: str = Field(default="", description="Page range where this question was found")

def extract_from_exact_pages(pdf_path: str, page_numbers: List[int], target_questions: List[str]) -> List[PYQQuestion]:
    """Extract questions from exact page numbers"""
    print(f"🎯 EXACT EXTRACTION: Looking for questions {target_questions} from pages {min(page_numbers)}-{max(page_numbers)}")
    
    with open(pdf_path, "rb") as pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    
    client = Mistral(api_key=MISTRAL_API_KEY)
    
    # OCR the PDF
    print("📖 Running OCR...")
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_pdf}"
        },
        include_image_base64=False
    )
    
    # Extract content from specific pages
    content = ""
    for page_num in page_numbers:
        if page_num <= len(ocr_response.pages):
            content += ocr_response.pages[page_num - 1].markdown + "\n"
            print(f"📄 Added page {page_num}")
        else:
            print(f"⚠️  Page {page_num} not found in PDF")
    
    print(f"📝 Total content length: {len(content)} characters")
    
    # Extract questions from this page range
    prompt = f"""
    CRITICAL: Extract the specific UPSC PYQ questions from pages {min(page_numbers)}-{max(page_numbers)}.
    
    IGNORE completely the test series reference column (VisionIAS/Sandhan/PT 365/Open Test/Abhyaas).
    
    IMPORTANT RULES:
    1. Only extract questions from the "Original PYQ" column (first column)
    2. Skip any questions from the "Test Series Reference" column
    3. Extract ALL questions you find in this page range
    4. Questions should have complete text with options (a), (b), (c), (d)
    
    Extract as a JSON array with these fields:
    - question_number: The question number
    - section: Subject section (Polity & Governance, Geography, History, etc.)
    - question_text: Complete question with options (a), (b), (c), (d)
    - correct_answer: A, B, C, or D
    - explanation: Detailed explanation
    - motivation: Current affairs context
    - difficulty_level: E, M, or D
    - question_nature: F, FA, CA, etc.
    - source_material: Source book
    - source_type: EM, RM, etc.
    - test_series_reference: Leave empty for original PYQs
    - page_range: "{min(page_numbers)}-{max(page_numbers)}"
    
    Skip separator lines (all "---"). Only extract actual questions from the first column.
    
    Content to process:
    {content[:8000]}
    """
    
    try:
        chat_response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            safe_prompt=True,
            max_tokens=4000
        )
        
        response_content = chat_response.choices[0].message.content
        if not isinstance(response_content, str):
            response_content = str(response_content)
        
        # Parse JSON with error handling
        try:
            parsed_data = json.loads(response_content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            return []
        
        # Handle different response formats
        if isinstance(parsed_data, dict):
            if 'questions' in parsed_data:
                questions_data = parsed_data['questions']
            elif 'data' in parsed_data:
                questions_data = parsed_data['data']
            else:
                questions_data = [parsed_data]
        elif isinstance(parsed_data, list):
            questions_data = parsed_data
        else:
            questions_data = [parsed_data]
        
        # Process and filter for target questions
        valid_questions = []
        all_found_questions = []
        
        for i, item in enumerate(questions_data):
            try:
                if 'question_number' in item:
                    item['question_number'] = str(item['question_number'])
                
                question = PYQQuestion(**item, extraction_order=i+1, chunk_number=1)
                all_found_questions.append(question)
                
                # Check if this is one of our target questions
                if question.question_number in target_questions:
                    valid_questions.append(question)
                    print(f"✅ TARGET FOUND: Q{question.question_number} (pages {min(page_numbers)}-{max(page_numbers)}): {question.question_text[:50]}...")
                else:
                    print(f"📝 OTHER FOUND: Q{question.question_number} (not in target list)")
                    
            except Exception as e:
                print(f"❌ Error processing question: {e}")
                continue
        
        print(f"🎯 Found {len(valid_questions)} target questions out of {len(all_found_questions)} total questions")
        return valid_questions
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return []

def save_results(questions, output_file):
    """Save extracted questions to JSON file"""
    result = {
        "metadata": {
            "pdf_name": "GS Prelims 2022.pdf",
            "extraction_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "total_questions": len(questions),
            "extraction_method": "remaining_missing_questions_2022",
            "note": "Extracted remaining missing questions that weren't found in first extraction"
        },
        "questions": [q.dict() for q in questions]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(questions)} questions to {output_file}")

def main():
    pdf_path = "../PYQP With Answer/GS/GS Prelims 2022.pdf"
    
    # Remaining missing questions from 2022
    remaining_missing = [26, 27, 28, 53, 60, 61, 62, 63, 64, 72]
    
    print(f"Remaining missing questions to extract: {remaining_missing}")
    print(f"Total remaining missing: {len(remaining_missing)}")
    
    # Page ranges for remaining questions (corrected page numbers provided by user)
    page_ranges = {
        "50": [53],             # Question 53 on page 50
        "59-60": [63, 64],      # Questions 63, 64 on pages 59-60
        "66-67": [72]           # Question 72 on pages 66-67
    }
    
    print("Page ranges configured:")
    for page_range, questions in page_ranges.items():
        print(f"  Pages {page_range}: Questions {questions}")
    
    print(f"\nPage ranges to process: {page_ranges}")
    
    # Extract questions from each page range
    all_extracted_questions = []
    
    for page_range, question_numbers in page_ranges.items():
        # Convert page range string to list of page numbers
        if '-' in page_range:
            start_page, end_page = map(int, page_range.split('-'))
            page_numbers = list(range(start_page, end_page + 1))
        else:
            # Single page
            page_numbers = [int(page_range)]
        
        # Convert question numbers to strings for comparison
        target_questions = [str(q) for q in question_numbers]
        
        print(f"\n{'='*60}")
        print(f"Processing pages {page_range} for questions {question_numbers}")
        print(f"{'='*60}")
        
        # Extract questions from this page range
        questions = extract_from_exact_pages(pdf_path, page_numbers, target_questions)
        all_extracted_questions.extend(questions)
    
    # Save results
    output_file = "GS Prelims 2022_REMAINING_MISSING.json"
    save_results(all_extracted_questions, output_file)
    
    # Summary
    extracted_numbers = [q.question_number for q in all_extracted_questions]
    print(f"\nExtracted question numbers: {extracted_numbers}")
    print(f"Successfully extracted {len(all_extracted_questions)} out of {len(remaining_missing)} remaining missing questions")

if __name__ == "__main__":
    main() 