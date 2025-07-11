#!/usr/bin/env python3
"""
Manual extraction script for missing questions using exact page numbers provided by user
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
    source_material: str = Field(..., description="Source book or material")
    source_type: str = Field(..., description="Type of source (EM=Essential Material, RM=Reference Material, etc.)")
    test_series_reference: str = Field(..., description="VisionIAS test series reference")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for the question")
    extraction_order: int = Field(default=0, description="Order of extraction")
    chunk_number: int = Field(default=0, description="Chunk number from which this question was extracted")
    page_range: str = Field(default="", description="Page range where this question was found")

def get_manual_page_ranges():
    """Get exact page ranges for missing questions as provided by user"""
    
    # Manual page ranges provided by user
    manual_ranges = {
        5: [7, 8],           # Q5: pages 7-8
        27: [32],            # Q27: page 32
        32: [36, 37, 38, 39, 40, 41],  # Q32-Q36: pages 36-41
        33: [36, 37, 38, 39, 40, 41],  # Q32-Q36: pages 36-41
        34: [36, 37, 38, 39, 40, 41],  # Q32-Q36: pages 36-41
        35: [36, 37, 38, 39, 40, 41],  # Q32-Q36: pages 36-41
        36: [36, 37, 38, 39, 40, 41],  # Q32-Q36: pages 36-41
        66: [75, 76],        # Q66: pages 75-76
        89: [99, 100]        # Q89: pages 99-100
    }
    
    return manual_ranges

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

def main():
    pdf_path = "/Users/shahrukhmalik/Documents/GitHub/UPSC BOOKS/UPSC PYQP/PYQP With Answer/GS/GS Prelims 2023.pdf"
    
    # Get manual page ranges
    manual_ranges = get_manual_page_ranges()
    
    print("🎯 MANUAL MISSING QUESTIONS EXTRACTION")
    print("=" * 60)
    print("Using exact page ranges provided by user:")
    for q_num, pages in manual_ranges.items():
        print(f"   Q{q_num}: pages {min(pages)}-{max(pages)}")
    print()
    
    all_missing_questions = []
    
    # Process each missing question
    for question_num, page_numbers in manual_ranges.items():
        print(f"\n{'='*60}")
        print(f"🎯 PROCESSING: Q{question_num}")
        print(f"{'='*60}")
        
        questions = extract_from_exact_pages(pdf_path, page_numbers, [str(question_num)])
        all_missing_questions.extend(questions)
    
    # Save missing questions
    output_data = {
        "metadata": {
            "extraction_date": datetime.now().isoformat(),
            "total_missing_questions": len(all_missing_questions),
            "extraction_method": "manual_page_extraction",
            "note": "Missing questions extracted using exact page numbers provided by user"
        },
        "questions": []
    }
    
    # Add unique ID to each question
    for i, question in enumerate(all_missing_questions):
        question_dict = question.model_dump()
        question_dict['id'] = str(uuid.uuid4())
        question_dict['extraction_order'] = i + 1
        output_data["questions"].append(question_dict)
    
    # Save to file
    output_path = "GS Prelims 2023_MISSING_questions_MANUAL.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✅ MANUAL EXTRACTION COMPLETE!")
    print(f"   Total missing questions extracted: {len(all_missing_questions)}")
    print(f"   Saved to: {output_path}")
    print(f"{'='*60}")
    
    # Show extracted questions
    if all_missing_questions:
        print(f"\n📝 EXTRACTED MISSING QUESTIONS:")
        for q in all_missing_questions:
            print(f"   Q{q.question_number} (pages {q.page_range}): {q.question_text[:80]}...")
    else:
        print("❌ No missing questions were extracted")

if __name__ == "__main__":
    main() 