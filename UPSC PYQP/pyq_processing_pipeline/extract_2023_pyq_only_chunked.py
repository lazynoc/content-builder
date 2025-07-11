import os
import sys
import json
import uuid
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

from mistralai import Mistral
from pydantic import BaseModel, Field

# --- CONFIG ---
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
OUTPUT_DIR = Path(__file__).parent
CHUNK_SIZE = 5  # Process 5 pages at a time
MAX_TOKENS_PER_CHUNK = 4000

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

def process_chunk_pyq_only(client: Mistral, chunk_content: str, chunk_number: int, start_page: int, end_page: int) -> List[PYQQuestion]:
    """Process a single chunk of content and extract ONLY original PYQ questions."""
    print(f"[Chunk {chunk_number}] Processing pages {start_page}-{end_page} with {len(chunk_content)} characters...")
    
    # Truncate content if too long
    if len(chunk_content) > MAX_TOKENS_PER_CHUNK * 4:
        chunk_content = chunk_content[:MAX_TOKENS_PER_CHUNK * 4]
        print(f"[Chunk {chunk_number}] Content truncated to {len(chunk_content)} characters")
    
    prompt = f"""
    CRITICAL: Extract ONLY the ORIGINAL UPSC PYQ questions from the FIRST COLUMN of this table.
    
    IGNORE completely the test series reference column (VisionIAS/Sandhan/PT 365/Open Test/Abhyaas).
    
    IMPORTANT RULES:
    1. Only extract questions from the "Original PYQ" column (first column)
    2. Skip any questions from the "Test Series Reference" column
    3. Each question should have a proper question number (1, 2, 3, etc.)
    4. Questions should have complete text with options (a), (b), (c), (d)
    5. Look for questions that start with numbers and have proper question format
    
    Extract as a JSON array with these fields:
    - question_number: The question number (1, 2, 3, etc.)
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
    
    Skip separator lines (all "---"). Only extract actual questions from the first column.
    
    Content to process (pages {start_page}-{end_page}):
    {chunk_content}
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
        
        # Try to parse JSON with better error handling
        parsed_data = None
        try:
            parsed_data = json.loads(response_content)
        except json.JSONDecodeError as e:
            print(f"[Chunk {chunk_number}] JSON parsing failed: {e}")
            print(f"[Chunk {chunk_number}] Attempting to fix malformed JSON...")
            
            try:
                fixed_content = re.sub(r',(\s*[}\]])', r'\1', response_content)
                fixed_content = re.sub(r'([^"])"([^"]*)$', r'\1"\2"', fixed_content)
                parsed_data = json.loads(fixed_content)
                print(f"[Chunk {chunk_number}] JSON fixed and parsed successfully")
            except:
                print(f"[Chunk {chunk_number}] Could not fix JSON, trying alternative approach...")
                return extract_questions_with_regex(chunk_content, chunk_number, start_page, end_page)
        
        if parsed_data is None:
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
        
        # Process and validate questions
        valid_questions = []
        for i, item in enumerate(questions_data):
            try:
                if 'question_number' in item:
                    item['question_number'] = str(item['question_number'])
                
                item['chunk_number'] = chunk_number
                item['page_range'] = f"{start_page}-{end_page}"
                
                question = PYQQuestion(**item, extraction_order=i+1)
                
                if is_original_pyq(question):
                    valid_questions.append(question)
                    print(f"[Chunk {chunk_number}] ✅ Valid PYQ {question.question_number} (pages {start_page}-{end_page}): {question.question_text[:50]}...")
                else:
                    print(f"[Chunk {chunk_number}] ❌ Skipped test series question {question.question_number}")
                    
            except Exception as e:
                print(f"[Chunk {chunk_number}] Error processing question: {e}")
                continue
        
        print(f"[Chunk {chunk_number}] Extracted {len(valid_questions)} valid original PYQ questions")
        return valid_questions
        
    except Exception as e:
        print(f"[Chunk {chunk_number}] Failed to process chunk: {e}")
        return extract_questions_with_regex(chunk_content, chunk_number, start_page, end_page)

def extract_questions_with_regex(content: str, chunk_number: int, start_page: int, end_page: int) -> List[PYQQuestion]:
    """Fallback method to extract questions using regex patterns."""
    print(f"[Chunk {chunk_number}] Using regex fallback extraction...")
    
    questions = []
    seen_question_numbers = set()
    
    question_patterns = [
        r'(\d+)\.\s*([^?]+\?[^|]*?\(a\)[^|]*?\(b\)[^|]*?\(c\)[^|]*?\(d\)[^|]*)',
        r'(\d+)\.\s*([^?]+\?[^|]*)',
    ]
    
    for pattern in question_patterns:
        matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            try:
                question_num = match.group(1)
                question_text = match.group(2).strip()
                
                if question_num in seen_question_numbers:
                    continue
                
                if any(pattern in question_text.lower() for pattern in ['visionias', 'sandhan', 'pt 365', 'test series']):
                    continue
                
                if len(question_text) < 20:
                    continue
                
                question = PYQQuestion(
                    question_number=question_num,
                    section="Unknown",
                    question_text=question_text,
                    correct_answer="",
                    explanation="",
                    motivation="",
                    difficulty_level="",
                    question_nature="",
                    source_material="",
                    source_type="",
                    test_series_reference="",
                    chunk_number=chunk_number,
                    page_range=f"{start_page}-{end_page}",
                    extraction_order=len(questions) + 1
                )
                
                questions.append(question)
                seen_question_numbers.add(question_num)
                print(f"[Chunk {chunk_number}] ✅ Regex extracted Q{question_num} (pages {start_page}-{end_page})")
                
            except Exception as e:
                print(f"[Chunk {chunk_number}] Error in regex extraction: {e}")
                continue
    
    print(f"[Chunk {chunk_number}] Regex fallback extracted {len(questions)} unique questions")
    return questions

def is_original_pyq(question: PYQQuestion) -> bool:
    """Check if this looks like an original PYQ question (not test series)."""
    
    if not question.question_number.isdigit():
        return False
    
    if not question.question_text or len(question.question_text) < 20:
        return False
    
    test_series_patterns = [
        'visionias', 'sandhan', 'pt 365', 'open test', 'abhyaas',
        'test series', 'mock test', 'practice test',
        'consider the following statements regarding',
        'which of the following statements are correct about',
        'select the correct answer using the code given below'
    ]
    
    question_text_lower = question.question_text.lower()
    if any(pattern in question_text_lower for pattern in test_series_patterns):
        return False
    
    if question.correct_answer not in ['A', 'B', 'C', 'D']:
        return False
    
    return True

def extract_pyq_only_chunked(pdf_path: str, max_pages: Optional[int] = None) -> List[PYQQuestion]:
    """Extract ONLY original PYQ questions from PDF using chunked processing."""
    print(f"🔍 [PYQ Only Chunked] Extracting ORIGINAL PYQ questions only from {pdf_path}")
    
    with open(pdf_path, "rb") as pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    
    client = Mistral(api_key=MISTRAL_API_KEY)
    
    # 1. OCR the PDF
    print("📖 [PYQ Only Chunked] Running OCR...")
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_pdf}"
        },
        include_image_base64=False
    )
    
    # 2. Determine pages to process
    total_pages = len(ocr_response.pages)
    pages_to_process = ocr_response.pages[:max_pages] if max_pages else ocr_response.pages
    print(f"📄 [PYQ Only Chunked] Processing {len(pages_to_process)} pages out of {total_pages} total pages")
    
    # 3. Process in chunks
    all_questions = []
    chunk_number = 1
    
    for i in range(0, len(pages_to_process), CHUNK_SIZE):
        chunk_pages = pages_to_process[i:i + CHUNK_SIZE]
        chunk_content = ""
        
        for page in chunk_pages:
            chunk_content += page.markdown + "\n"
        
        if chunk_content.strip():
            start_page = i + 1
            end_page = min(i + CHUNK_SIZE, len(pages_to_process))
            chunk_questions = process_chunk_pyq_only(client, chunk_content, chunk_number, start_page, end_page)
            all_questions.extend(chunk_questions)
            chunk_number += 1
    
    # 4. Remove duplicates and reorder
    unique_questions = []
    seen_numbers = set()
    
    for question in all_questions:
        if question.question_number not in seen_numbers:
            unique_questions.append(question)
            seen_numbers.add(question.question_number)
    
    # Reorder by question number
    unique_questions.sort(key=lambda x: int(x.question_number) if x.question_number.isdigit() else float('inf'))
    
    print(f"📊 [PYQ Only Chunked] Total extracted: {len(all_questions)}, Unique original PYQs: {len(unique_questions)}")
    return unique_questions

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract ONLY original PYQ questions using chunked processing")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--max-pages", type=int, help="Maximum number of pages to process")
    
    args = parser.parse_args()
    
    # Extract questions
    questions = extract_pyq_only_chunked(args.pdf_path, args.max_pages)
    
    # Prepare output
    output_data = {
        "metadata": {
            "pdf_name": Path(args.pdf_path).name,
            "extraction_date": datetime.now().isoformat(),
            "total_questions": len(questions),
            "extraction_method": "pyq_only_chunked_ocr_chat",
            "max_pages_processed": args.max_pages or "full_pdf",
            "chunk_size": CHUNK_SIZE,
            "note": "Only original PYQ questions extracted, test series questions filtered out"
        },
        "questions": []
    }
    
    # Add unique ID to each question
    for i, question in enumerate(questions):
        question_dict = question.model_dump()
        question_dict['id'] = str(uuid.uuid4())
        question_dict['extraction_order'] = i + 1
        output_data["questions"].append(question_dict)
    
    # Save to file
    output_path = args.output or OUTPUT_DIR / f"{Path(args.pdf_path).stem}_PYQ_ONLY_chunked.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved {len(questions)} original PYQ questions to {output_path}")
    
    # Show sample questions with page ranges
    if questions:
        print(f"\n📝 SAMPLE QUESTIONS:")
        for i, q in enumerate(questions[:3]):
            print(f"   Q{q.question_number} (pages {q.page_range}): {q.question_text[:100]}...")
            print(f"   Answer: {q.correct_answer}")
            print()

if __name__ == "__main__":
    main() 