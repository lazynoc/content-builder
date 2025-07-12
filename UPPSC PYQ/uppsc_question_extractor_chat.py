#!/usr/bin/env python3
"""
UPPSC Question Extractor using Chat Completions (Based on successful UPSC PYQP approach)
This script uses Mistral's chat completion API with chunked processing to extract questions and options.
"""

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

# Load environment variables from parent directory
load_dotenv('../.env')

from mistralai import Mistral
from pydantic import BaseModel, Field

# --- CONFIG ---
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
OUTPUT_DIR = Path(__file__).parent
CHUNK_SIZE = 5  # Process 5 pages at a time
MAX_TOKENS_PER_CHUNK = 4000

# --- UPPSC QUESTION SCHEMA ---
class UPPSCQuestion(BaseModel):
    question_number: str = Field(..., description="Question number (e.g., 1, 2, 3)")
    question_text: str = Field(..., description="The complete question text")
    options: Dict[str, str] = Field(..., description="Options as dict with keys 'a', 'b', 'c', 'd'")
    correct_answer: str = Field(..., description="Correct answer (A, B, C, or D)")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for the question")
    extraction_order: int = Field(default=0, description="Order of extraction")
    chunk_number: int = Field(default=0, description="Chunk number from which this question was extracted")

# --- ANSWER KEY ---
ANSWER_KEY = {
    "1": "A", "2": "B", "3": "D", "4": "C", "5": "D", "6": "A", "7": "D", "8": "A", "9": "C", "10": "D",
    "11": "A", "12": "D", "13": "A", "14": "D", "15": "D", "16": "A", "17": "C", "18": "A", "19": "B", "20": "A",
    "21": "C", "22": "A", "23": "B", "24": "D", "25": "C", "26": "D", "27": "A", "28": "B", "29": "B", "30": "C",
    "31": "B", "32": "C", "33": "C", "34": "C", "35": "B", "36": "A", "37": "C", "38": "B", "39": "C", "40": "B",
    "41": "A", "42": "A", "43": "C", "44": "D", "45": "A", "46": "C", "47": "D", "48": "C", "49": "A", "50": "D",
    "51": "B", "52": "B", "53": "B", "54": "C", "55": "A", "56": "B", "57": "B", "58": "C", "59": "B", "60": "B",
    "61": "B", "62": "C", "63": "A", "64": "B", "65": "D", "66": "D", "67": "C", "68": "A", "69": "D", "70": "C",
    "71": "B", "72": "A", "73": "A", "74": "D", "75": "A", "76": "A", "77": "D", "78": "B", "79": "D", "80": "A",
    "81": "D", "82": "D", "83": "C", "84": "D", "85": "A", "86": "D", "87": "A", "88": "C", "89": "D", "90": "D",
    "91": "B", "92": "C", "93": "C", "94": "D", "95": "A", "96": "A", "97": "A", "98": "A", "99": "B", "100": "B",
    "101": "D", "102": "C", "103": "A", "104": "D", "105": "C", "106": "C", "107": "B", "108": "A", "109": "C", "110": "D",
    "111": "D", "112": "B", "113": "D", "114": "A", "115": "A", "116": "D", "117": "B", "118": "D", "119": "C", "120": "B",
    "121": "B", "122": "A", "123": "B", "124": "D", "125": "D", "126": "C", "127": "D", "128": "C", "129": "D", "130": "D",
    "131": "B", "132": "C", "133": "B", "134": "C", "135": "C", "136": "B", "137": "A", "138": "A", "139": "B", "140": "A",
    "141": "B", "142": "B", "143": "D", "144": "B", "145": "D", "146": "D", "147": "A", "148": "C", "149": "B", "150": "C"
}

def process_chunk_uppsc(client: Mistral, chunk_content: str, chunk_number: int) -> List[UPPSCQuestion]:
    """Process a single chunk of content and extract UPPSC questions with options."""
    print(f"[Chunk {chunk_number}] Processing chunk with {len(chunk_content)} characters...")
    
    # Truncate content if too long
    if len(chunk_content) > MAX_TOKENS_PER_CHUNK * 4:  # Rough estimate: 4 chars per token
        chunk_content = chunk_content[:MAX_TOKENS_PER_CHUNK * 4]
        print(f"[Chunk {chunk_number}] Content truncated to {len(chunk_content)} characters")
    
    prompt = f"""
    Extract all multiple-choice questions from this UPPSC question paper content.
    
    IMPORTANT RULES:
    1. Look for questions that start with numbers (1, 2, 3, etc.)
    2. Each question should have 4 options labeled (a), (b), (c), (d) or A), B), C), D)
    3. Extract the complete question text and all options
    4. If a question is incomplete or split across pages, include as much as is visible
    5. Skip any non-question content (headers, instructions, etc.)
    
    Extract as a JSON array with these fields:
    - question_number: The question number (1, 2, 3, etc.)
    - question_text: Complete question text (without options)
    - options: Object with keys "a", "b", "c", "d" containing the option text
    
    Example format:
    [
      {{
        "question_number": "1",
        "question_text": "What is the capital of India?",
        "options": {{
          "a": "Mumbai",
          "b": "Delhi", 
          "c": "Kolkata",
          "d": "Chennai"
        }}
      }}
    ]
    
    Content to process:
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
            
            # Try to fix common JSON issues
            try:
                # Remove any trailing commas
                fixed_content = re.sub(r',(\s*[}\]])', r'\1', response_content)
                # Try to close any unclosed quotes
                fixed_content = re.sub(r'([^"])"([^"]*)$', r'\1"\2"', fixed_content)
                parsed_data = json.loads(fixed_content)
                print(f"[Chunk {chunk_number}] JSON fixed and parsed successfully")
            except:
                print(f"[Chunk {chunk_number}] Could not fix JSON, trying regex fallback...")
                return extract_questions_with_regex(chunk_content, chunk_number)
        
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
                # Ensure question_number is string
                if 'question_number' in item:
                    item['question_number'] = str(item['question_number'])
                
                # Add correct answer from answer key
                question_num = item['question_number']
                if question_num in ANSWER_KEY:
                    item['correct_answer'] = ANSWER_KEY[question_num]
                else:
                    item['correct_answer'] = "Unknown"
                
                # Add chunk number
                item['chunk_number'] = chunk_number
                
                question = UPPSCQuestion(**item, extraction_order=i+1)
                
                # Validate question format
                if is_valid_uppsc_question(question):
                    valid_questions.append(question)
                    print(f"[Chunk {chunk_number}] ✅ Valid Q{question.question_number}: {question.question_text[:50]}... (Answer: {question.correct_answer})")
                else:
                    print(f"[Chunk {chunk_number}] ❌ Invalid question format for Q{question.question_number}")
                    
            except Exception as e:
                print(f"[Chunk {chunk_number}] Error processing question: {e}")
                continue
        
        print(f"[Chunk {chunk_number}] Extracted {len(valid_questions)} valid questions")
        return valid_questions
        
    except Exception as e:
        print(f"[Chunk {chunk_number}] Failed to process chunk: {e}")
        # Try regex fallback
        return extract_questions_with_regex(chunk_content, chunk_number)

def extract_questions_with_regex(content: str, chunk_number: int) -> List[UPPSCQuestion]:
    """Fallback method to extract questions using regex patterns."""
    print(f"[Chunk {chunk_number}] Using regex fallback extraction...")
    
    questions = []
    seen_question_numbers = set()
    
    # Look for question patterns with options
    question_patterns = [
        # Pattern for questions with (a), (b), (c), (d) options
        r'(\d+)\.\s*([^?]+\?[^|]*?\(a\)[^|]*?\(b\)[^|]*?\(c\)[^|]*?\(d\)[^|]*)',
        # Pattern for questions with A), B), C), D) options
        r'(\d+)\.\s*([^?]+\?[^|]*?A\)[^|]*?B\)[^|]*?C\)[^|]*?D\)[^|]*)',
        # Pattern for questions without options (fallback)
        r'(\d+)\.\s*([^?]+\?[^|]*)',
    ]
    
    for pattern in question_patterns:
        matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            try:
                question_num = match.group(1)
                question_text = match.group(2).strip()
                
                # Skip if we've already seen this question number
                if question_num in seen_question_numbers:
                    continue
                
                # Skip if question text is too short
                if len(question_text) < 20:
                    continue
                
                # Extract options if present
                options = extract_options_from_text(question_text)
                
                # Remove options from question text
                clean_question_text = remove_options_from_text(question_text)
                
                # Get correct answer from answer key
                correct_answer = ANSWER_KEY.get(question_num, "Unknown")
                
                # Create question object
                question = UPPSCQuestion(
                    question_number=question_num,
                    question_text=clean_question_text,
                    options=options,
                    correct_answer=correct_answer,
                    chunk_number=chunk_number,
                    extraction_order=len(questions) + 1
                )
                
                questions.append(question)
                seen_question_numbers.add(question_num)
                print(f"[Chunk {chunk_number}] ✅ Regex extracted Q{question_num}")
                
            except Exception as e:
                print(f"[Chunk {chunk_number}] Error in regex extraction: {e}")
                continue
    
    print(f"[Chunk {chunk_number}] Regex fallback extracted {len(questions)} unique questions")
    return questions

def extract_options_from_text(text: str) -> Dict[str, str]:
    """Extract options (a, b, c, d) from question text."""
    options = {"a": "", "b": "", "c": "", "d": ""}
    
    # Try to find options with different patterns
    option_patterns = [
        r'\(a\)\s*([^\(\)]+?)(?=\(b\)|$)',
        r'A\)\s*([^A-D]+?)(?=B\)|$)',
        r'\(a\)\s*([^\(\)]+?)(?=\(b\)|$)',
        r'a\)\s*([^a-d]+?)(?=b\)|$)',
    ]
    
    for pattern in option_patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        if len(matches) >= 4:
            options["a"] = matches[0].strip()
            options["b"] = matches[1].strip()
            options["c"] = matches[2].strip()
            options["d"] = matches[3].strip()
            break
    
    return options

def remove_options_from_text(text: str) -> str:
    """Remove options from question text to get clean question."""
    # Remove options patterns
    text = re.sub(r'\(a\)[^\(\)]*\(b\)[^\(\)]*\(c\)[^\(\)]*\(d\)[^\(\)]*', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'A\)[^A-D]*B\)[^A-D]*C\)[^A-D]*D\)[^A-D]*', '', text, flags=re.DOTALL | re.IGNORECASE)
    return text.strip()

def is_valid_uppsc_question(question: UPPSCQuestion) -> bool:
    """Check if this looks like a valid UPPSC question."""
    
    # Check question number
    if not question.question_number.isdigit():
        return False
    
    # Check question text
    if not question.question_text or len(question.question_text) < 10:
        return False
    
    # Check options
    if not question.options or len(question.options) < 4:
        return False
    
    # Check if options have content
    for key in ['a', 'b', 'c', 'd']:
        if not question.options.get(key, '').strip():
            return False
    
    # Check correct answer
    if not question.correct_answer or question.correct_answer not in ['A', 'B', 'C', 'D', 'Unknown']:
        return False
    
    return True

def extract_uppsc_questions_chunked(pdf_path: str, max_pages: Optional[int] = None) -> List[UPPSCQuestion]:
    """Extract UPPSC questions from PDF using chunked processing with chat completions."""
    print(f"🔍 [UPPSC Chat] Extracting questions from {pdf_path}")
    
    with open(pdf_path, "rb") as pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    
    client = Mistral(api_key=MISTRAL_API_KEY)
    
    # 1. OCR the PDF
    print("📖 [UPPSC Chat] Running OCR...")
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
    print(f"📄 [UPPSC Chat] Processing {len(pages_to_process)} pages out of {total_pages} total pages")
    
    # 3. Process in chunks
    all_questions = []
    chunk_number = 1
    
    for i in range(0, len(pages_to_process), CHUNK_SIZE):
        chunk_pages = pages_to_process[i:i + CHUNK_SIZE]
        chunk_content = ""
        
        for page in chunk_pages:
            chunk_content += page.markdown + "\n"
        
        if chunk_content.strip():
            chunk_questions = process_chunk_uppsc(client, chunk_content, chunk_number)
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
    
    print(f"📊 [UPPSC Chat] Total extracted: {len(all_questions)}, Unique questions: {len(unique_questions)}")
    return unique_questions

def main():
    """Main function to execute the question extraction."""
    
    # Check if Mistral API key is available
    if not MISTRAL_API_KEY:
        print("Error: MISTRAL_API_KEY not found in environment variables")
        print("Please set your Mistral API key in the .env file")
        return
    
    # Input and output paths
    pdf_path = "split_versions/UPPCS_2024_Prelims_GS1_Question_Paper_English.pdf"
    output_path = "uppsc_questions_chat_complete.json"
    
    # Check if input file exists
    if not os.path.exists(pdf_path):
        print(f"Error: Input file '{pdf_path}' not found!")
        print("Please run the PDF splitting script first.")
        return
    
    try:
        print("🚀 Starting UPPSC question extraction for ENTIRE PDF using chat completions...")
        print("📚 Target: Extract all ~150 questions from 39 pages")
        
        # Extract questions using chat completions - process entire PDF
        questions = extract_uppsc_questions_chunked(pdf_path)  # No max_pages limit
        
        if questions:
            # Prepare output
            output_data = {
                "metadata": {
                    "pdf_name": Path(pdf_path).name,
                    "extraction_date": datetime.now().isoformat(),
                    "total_questions": len(questions),
                    "extraction_method": "chat_completions_chunked",
                    "pages_processed": "all_39_pages",
                    "chunk_size": CHUNK_SIZE,
                    "note": "Complete UPPSC 2024 Prelims GS1 question paper extracted using Mistral chat completions"
                },
                "questions": []
            }
            
            # Add questions to output
            for i, question in enumerate(questions):
                question_dict = question.model_dump()
                question_dict['id'] = str(uuid.uuid4())
                question_dict['extraction_order'] = i + 1
                output_data["questions"].append(question_dict)
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ SUCCESS! Saved {len(questions)} questions to {output_path}")
            print(f"📊 Expected: ~150 questions, Actual: {len(questions)} questions")
            
            # Show sample questions from different parts
            print(f"\n📝 SAMPLE QUESTIONS (showing first 3, middle 3, and last 3):")
            
            # First 3
            print("🔸 FIRST 3 QUESTIONS:")
            for i, q in enumerate(questions[:3]):
                print(f"   Q{q.question_number}: {q.question_text[:80]}...")
                print(f"   Options: a) {q.options.get('a', 'N/A')[:40]}...")
                print()
            
            # Middle 3
            if len(questions) > 6:
                middle_start = len(questions) // 2 - 1
                print("🔸 MIDDLE 3 QUESTIONS:")
                for i, q in enumerate(questions[middle_start:middle_start+3]):
                    print(f"   Q{q.question_number}: {q.question_text[:80]}...")
                    print(f"   Options: a) {q.options.get('a', 'N/A')[:40]}...")
                    print()
            
            # Last 3
            if len(questions) > 3:
                print("🔸 LAST 3 QUESTIONS:")
                for i, q in enumerate(questions[-3:]):
                    print(f"   Q{q.question_number}: {q.question_text[:80]}...")
                    print(f"   Options: a) {q.options.get('a', 'N/A')[:40]}...")
                    print()
            
            # Question number range
            if questions:
                first_q = questions[0].question_number
                last_q = questions[-1].question_number
                print(f"📋 Question range: Q{first_q} to Q{last_q}")
            
        else:
            print("❌ No questions extracted from PDF")
        
    except ImportError as e:
        print(f"Error: Missing required package - {e}")
        print("Please install the Mistral AI client: pip install mistralai")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 