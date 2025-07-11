#!/usr/bin/env python3
"""
Full OCR extraction for GS Prelims 2022
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

def extract_questions_from_chunk(pdf_path: str, chunk_pages: List[int], chunk_number: int) -> List[PYQQuestion]:
    """Extract questions from a specific chunk of pages"""
    print(f"📖 Processing chunk {chunk_number}: pages {min(chunk_pages)}-{max(chunk_pages)}")
    
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
    for page_num in chunk_pages:
        if page_num <= len(ocr_response.pages):
            content += ocr_response.pages[page_num - 1].markdown + "\n"
            print(f"📄 Added page {page_num}")
        else:
            print(f"⚠️  Page {page_num} not found in PDF")
    
    print(f"📝 Total content length: {len(content)} characters")
    
    # Extract questions from this chunk
    prompt = f"""
    CRITICAL: Extract ALL ORIGINAL UPSC PYQ questions from pages {min(chunk_pages)}-{max(chunk_pages)}.
    
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
    - page_range: "{min(chunk_pages)}-{max(chunk_pages)}"
    
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
        
        # Process questions
        questions = []
        for i, item in enumerate(questions_data):
            try:
                if 'question_number' in item:
                    item['question_number'] = str(item['question_number'])
                
                question = PYQQuestion(**item, extraction_order=i+1, chunk_number=chunk_number)
                questions.append(question)
                print(f"✅ Extracted Q{question.question_number} (pages {min(chunk_pages)}-{max(chunk_pages)}): {question.question_text[:50]}...")
                    
            except Exception as e:
                print(f"❌ Error processing question: {e}")
                continue
        
        print(f"🎯 Extracted {len(questions)} questions from chunk {chunk_number}")
        return questions
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return []

def main():
    pdf_path = "/Users/shahrukhmalik/Documents/GitHub/UPSC BOOKS/UPSC PYQP/PYQP With Answer/GS/GS Prelims 2022.pdf"
    
    print("🔍 FULL OCR EXTRACTION FOR GS PRELIMS 2022")
    print("=" * 60)
    
    # Define chunks (5 pages each)
    chunks = [
        list(range(1, 6)),    # pages 1-5
        list(range(6, 11)),   # pages 6-10
        list(range(11, 16)),  # pages 11-15
        list(range(16, 21)),  # pages 16-20
        list(range(21, 26)),  # pages 21-25
        list(range(26, 31)),  # pages 26-30
        list(range(31, 36)),  # pages 31-35
        list(range(36, 41)),  # pages 36-40
        list(range(41, 46)),  # pages 41-45
        list(range(46, 51)),  # pages 46-50
        list(range(51, 56)),  # pages 51-55
        list(range(56, 61)),  # pages 56-60
        list(range(61, 66)),  # pages 61-65
        list(range(66, 71)),  # pages 66-70
        list(range(71, 76)),  # pages 71-75
        list(range(76, 81)),  # pages 76-80
        list(range(81, 86)),  # pages 81-85
        list(range(86, 91)),  # pages 86-90
        list(range(91, 96)),  # pages 91-95
        list(range(96, 101)), # pages 96-100
        list(range(101, 106)), # pages 101-105
        list(range(106, 111)), # pages 106-110
        list(range(111, 116)), # pages 111-115
        list(range(116, 121)), # pages 116-120
        list(range(121, 126)), # pages 121-125
        list(range(126, 131)), # pages 126-130
        list(range(131, 136)), # pages 131-135
        list(range(136, 141)), # pages 136-140
        list(range(141, 146)), # pages 141-145
        list(range(146, 151)), # pages 146-150
        list(range(151, 156)), # pages 151-155
        list(range(156, 161)), # pages 156-160
        list(range(161, 166)), # pages 161-165
        list(range(166, 171)), # pages 166-170
        list(range(171, 176)), # pages 171-175
        list(range(176, 181)), # pages 176-180
        list(range(181, 186)), # pages 181-185
        list(range(186, 191)), # pages 186-190
        list(range(191, 196)), # pages 191-195
        list(range(196, 201)), # pages 196-200
    ]
    
    all_questions = []
    
    # Process each chunk
    for i, chunk_pages in enumerate(chunks, 1):
        print(f"\n{'='*60}")
        print(f"🔍 PROCESSING CHUNK {i}/{len(chunks)}")
        print(f"{'='*60}")
        
        questions = extract_questions_from_chunk(pdf_path, chunk_pages, i)
        all_questions.extend(questions)
        
        print(f"📊 Running total: {len(all_questions)} questions")
    
    # Save all questions
    output_data = {
        "metadata": {
            "extraction_date": datetime.now().isoformat(),
            "total_questions": len(all_questions),
            "extraction_method": "full_ocr_chunked",
            "note": "GS Prelims 2022 full extraction using chunked OCR"
        },
        "questions": []
    }
    
    # Add unique ID to each question
    for i, question in enumerate(all_questions):
        question_dict = question.model_dump()
        question_dict['id'] = str(uuid.uuid4())
        question_dict['final_extraction_order'] = i + 1
        output_data["questions"].append(question_dict)
    
    # Save to file
    output_path = "GS Prelims 2022_PYQ_ONLY_chunked.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✅ FULL EXTRACTION COMPLETE!")
    print(f"   Total questions extracted: {len(all_questions)}")
    print(f"   Saved to: {output_path}")
    print(f"{'='*60}")
    
    # Show question numbers
    question_nums = sorted([int(q.get('question_number', 0)) for q in all_questions])
    print(f"\n📝 QUESTION NUMBERS FOUND ({len(question_nums)}):")
    print(f"   {question_nums}")
    
    # Check for gaps
    if question_nums:
        expected_range = set(range(1, max(question_nums) + 1))
        actual_range = set(question_nums)
        missing = expected_range - actual_range
        
        if missing:
            print(f"\n❌ MISSING QUESTIONS: {sorted(missing)}")
        else:
            print(f"\n✅ NO MISSING QUESTIONS - Complete dataset!")

if __name__ == "__main__":
    main() 