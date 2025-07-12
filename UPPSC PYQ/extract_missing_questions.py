#!/usr/bin/env python3
"""
Extract Missing UPPSC Questions from Specific Pages
This script extracts the missing questions from specific pages and adds them to the existing JSON.
"""

import os
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

# --- UPPSC QUESTION SCHEMA ---
class UPPSCQuestion(BaseModel):
    question_number: str = Field(..., description="Question number (e.g., 1, 2, 3)")
    question_text: str = Field(..., description="The complete question text")
    options: Dict[str, str] = Field(..., description="Options as dict with keys 'a', 'b', 'c', 'd'")
    correct_answer: str = Field(..., description="Correct answer (A, B, C, or D)")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for the question")
    extraction_order: int = Field(default=0, description="Order of extraction")
    chunk_number: int = Field(default=0, description="Chunk number from which this question was extracted")

# --- ANSWER KEY FOR MISSING QUESTIONS ---
MISSING_ANSWERS = {
    "18": "A", "21": "C", "22": "A", "85": "A", "86": "D", "88": "C", "132": "C"
}

# --- MISSING QUESTIONS PAGES ---
MISSING_QUESTIONS_PAGES = {
    "18": [5],  # Page 6 (0-indexed = 5)
    "21": [6],  # Page 7 (0-indexed = 6)
    "22": [6],  # Page 7 (0-indexed = 6)
    "85": [20], # Page 21 (0-indexed = 20)
    "86": [20], # Page 21 (0-indexed = 20)
    "88": [21], # Page 22 (0-indexed = 21)
    "132": [32, 33]  # Pages 33-34 (0-indexed = 32, 33)
}

def process_specific_pages(client: Mistral, pdf_path: str, target_questions: List[str]) -> List[UPPSCQuestion]:
    """Process specific pages to extract missing questions."""
    print(f"🔍 Extracting missing questions: {target_questions}")
    
    with open(pdf_path, "rb") as pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    
    # 1. OCR the PDF
    print("📖 Running OCR...")
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_pdf}"
        },
        include_image_base64=False
    )
    
    # 2. Get all unique pages we need to process
    all_pages_needed = set()
    for question_num in target_questions:
        if question_num in MISSING_QUESTIONS_PAGES:
            all_pages_needed.update(MISSING_QUESTIONS_PAGES[question_num])
    
    print(f"📄 Processing pages: {sorted(all_pages_needed)}")
    
    # 3. Extract content from specific pages
    extracted_questions = []
    
    for page_idx in sorted(all_pages_needed):
        if page_idx < len(ocr_response.pages):
            page_content = ocr_response.pages[page_idx].markdown
            print(f"📄 Processing page {page_idx + 1} (index {page_idx})...")
            
            # Extract questions from this page
            page_questions = extract_questions_from_page_content(client, page_content, page_idx, target_questions)
            extracted_questions.extend(page_questions)
    
    return extracted_questions

def extract_questions_from_page_content(client: Mistral, content: str, page_idx: int, target_questions: List[str]) -> List[UPPSCQuestion]:
    """Extract specific questions from page content."""
    
    prompt = f"""
    Extract ONLY the following specific questions from this UPPSC question paper content:
    {target_questions}
    
    IMPORTANT RULES:
    1. Only extract the questions with numbers: {target_questions}
    2. Each question should have 4 options labeled (a), (b), (c), (d) or A), B), C), D)
    3. Extract the complete question text and all options
    4. Skip any other questions not in the target list
    
    Extract as a JSON array with these fields:
    - question_number: The question number
    - question_text: Complete question text (without options)
    - options: Object with keys "a", "b", "c", "d" containing the option text
    
    Content to process:
    {content}
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
        
        # Parse JSON
        try:
            parsed_data = json.loads(response_content)
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            return []
        
        # Handle different response formats
        if isinstance(parsed_data, dict):
            if 'questions' in parsed_data:
                questions_data = parsed_data['questions']
            else:
                questions_data = [parsed_data]
        elif isinstance(parsed_data, list):
            questions_data = parsed_data
        else:
            questions_data = [parsed_data]
        
        # Process questions
        valid_questions = []
        for i, item in enumerate(questions_data):
            try:
                question_num = str(item.get('question_number', ''))
                
                # Only process target questions
                if question_num not in target_questions:
                    continue
                
                # Add correct answer
                if question_num in MISSING_ANSWERS:
                    item['correct_answer'] = MISSING_ANSWERS[question_num]
                else:
                    item['correct_answer'] = "Unknown"
                
                # Add metadata
                item['chunk_number'] = page_idx
                
                question = UPPSCQuestion(**item, extraction_order=i+1)
                
                if is_valid_uppsc_question(question):
                    valid_questions.append(question)
                    print(f"✅ Extracted Q{question.question_number} from page {page_idx + 1} (Answer: {question.correct_answer})")
                
            except Exception as e:
                print(f"Error processing question: {e}")
                continue
        
        return valid_questions
        
    except Exception as e:
        print(f"Failed to process page {page_idx + 1}: {e}")
        return []

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

def add_missing_questions_to_json(missing_questions: List[UPPSCQuestion]):
    """Add missing questions to the existing JSON file."""
    
    input_file = "uppsc_questions_with_answers.json"
    output_file = "uppsc_questions_complete_final.json"
    
    try:
        # Load existing JSON
        print(f"📖 Loading existing JSON from {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        existing_questions = data.get('questions', [])
        existing_numbers = set(q.get('question_number') for q in existing_questions)
        
        print(f"📊 Existing questions: {len(existing_questions)}")
        print(f"📊 Missing questions found: {len(missing_questions)}")
        
        # Add missing questions
        added_count = 0
        for question in missing_questions:
            if question.question_number not in existing_numbers:
                question_dict = question.model_dump()
                question_dict['id'] = str(uuid.uuid4())
                question_dict['extraction_order'] = len(existing_questions) + added_count + 1
                existing_questions.append(question_dict)
                added_count += 1
                print(f"✅ Added Q{question.question_number}")
            else:
                print(f"⚠️ Q{question.question_number} already exists, skipping")
        
        # Sort by question number
        existing_questions.sort(key=lambda x: int(x['question_number']) if x['question_number'].isdigit() else float('inf'))
        
        # Update metadata
        data['metadata']['missing_questions_added'] = True
        data['metadata']['total_questions'] = len(existing_questions)
        data['metadata']['questions_added'] = added_count
        data['metadata']['final_extraction_date'] = datetime.now().isoformat()
        
        # Save updated JSON
        print(f"\n💾 Saving complete JSON to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 COMPLETE!")
        print(f"📊 Total questions now: {len(existing_questions)}")
        print(f"✅ Questions added: {added_count}")
        print(f"💾 Complete JSON saved to: {output_file}")
        
        # Show final status
        all_numbers = set(int(q['question_number']) for q in existing_questions)
        missing_final = set(range(1, 151)) - all_numbers
        extra_final = all_numbers - set(range(1, 151))
        
        print(f"\n📋 FINAL STATUS:")
        print(f"✅ Success rate: {len(existing_questions)}/150 = {(len(existing_questions)/150)*100:.1f}%")
        if missing_final:
            print(f"❌ Still missing: {sorted(missing_final)}")
        if extra_final:
            print(f"➕ Extra questions: {sorted(extra_final)}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to extract missing questions."""
    
    # Check if Mistral API key is available
    if not MISTRAL_API_KEY:
        print("Error: MISTRAL_API_KEY not found in environment variables")
        return
    
    # Input file
    pdf_path = "split_versions/UPPCS_2024_Prelims_GS1_Question_Paper_English.pdf"
    
    # Check if input file exists
    if not os.path.exists(pdf_path):
        print(f"Error: Input file '{pdf_path}' not found!")
        return
    
    try:
        print("🚀 Starting extraction of missing questions...")
        
        # Initialize Mistral client
        client = Mistral(api_key=MISTRAL_API_KEY)
        
        # Target questions to extract
        target_questions = ["18", "21", "22", "85", "86", "88", "132"]
        
        # Extract missing questions
        missing_questions = process_specific_pages(client, pdf_path, target_questions)
        
        if missing_questions:
            print(f"\n✅ Successfully extracted {len(missing_questions)} missing questions")
            
            # Add to existing JSON
            add_missing_questions_to_json(missing_questions)
            
        else:
            print("❌ No missing questions extracted")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 