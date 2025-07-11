#!/usr/bin/env python3
"""
Extract Structured UPPSC 2024 Questions (English Only)
=====================================================

This script takes the English OCR output from the first 5 pages of the UPPSC 2024 Prelims GS1 paper,
sends each page's text to Mistral chat completion, and extracts structured question objects.
"""

import os
import json
from pathlib import Path
from mistralai import Mistral
from dotenv import load_dotenv

# Load environment variables from .env in project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

# Input: English OCR output from previous step
OCR_JSON_PATH = Path(__file__).parent / 'uppsc_2024_english_questions_first5.json'
OUTPUT_PATH = Path(__file__).parent / 'uppsc_2024_structured_questions_first5.json'

MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
if not MISTRAL_API_KEY:
    raise RuntimeError('MISTRAL_API_KEY not found in environment variables')

client = Mistral(api_key=MISTRAL_API_KEY)

# Prompt template for Mistral chat completion
PROMPT_TEMPLATE = '''
You are an expert at extracting structured data from exam papers.

Extract all multiple-choice questions from the following text. For each question, return a JSON object with these fields:
- question_number: (e.g., 1, 2, 3)
- question_text: (full question, in English only)
- options: (dictionary with keys A, B, C, D and their text)
- correct_answer: (A, B, C, or D, if present; otherwise null)
- explanation: (if present; otherwise null)

Ignore any Hindi or non-English content. Only extract English questions and options.

Text to process:
"""
{page_text}
"""
Return a JSON array of question objects as described above. Do not include any extra commentary.
'''

def extract_structured_questions(page_text, page_number):
    prompt = PROMPT_TEMPLATE.format(page_text=page_text)
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        safe_prompt=True,
        max_tokens=4000
    )
    content = response.choices[0].message.content
    try:
        data = json.loads(content)
        if isinstance(data, dict) and 'questions' in data:
            return data['questions']
        elif isinstance(data, list):
            return data
        else:
            return []
    except Exception as e:
        print(f"[Page {page_number}] Error parsing Mistral output: {e}")
        return []

def main():
    if not OCR_JSON_PATH.exists():
        print(f"❌ OCR JSON file not found: {OCR_JSON_PATH}\nPlease run the OCR extraction step first.")
        return
    with open(OCR_JSON_PATH, 'r', encoding='utf-8') as f:
        ocr_pages = json.load(f)
    all_questions = []
    for page in ocr_pages:
        page_number = page.get('page_number')
        page_text = page.get('english_text', '').strip()
        if not page_text:
            continue
        print(f"\n[Page {page_number}] Extracting structured questions...")
        questions = extract_structured_questions(page_text, page_number)
        for q in questions:
            q['page_number'] = page_number
        all_questions.extend(questions)
        print(f"[Page {page_number}] Extracted {len(questions)} questions.")
    # Save output
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Structured questions saved to: {OUTPUT_PATH}")
    if all_questions:
        print("\nSample output:\n")
        print(json.dumps(all_questions[0], indent=2, ensure_ascii=False))
    else:
        print("No questions extracted.")

if __name__ == "__main__":
    main() 