#!/usr/bin/env python3
"""
Test UPPSC OCR Processing (English Only)
=======================================

This script extracts only the English questions from the first 5 pages
of the 2024 UPPSC Prelims GS1 paper using the Mistral-based OCR pipeline.
"""

import os
import sys
import json
from pathlib import Path
import re

# Add pipeline_components to path
sys.path.append(str(Path(__file__).parent.parent / 'master_upsc_processing' / 'pipeline_components'))

from upsc_book_ocr_extractor import UPSCBookOCRExtractor

PDF_PATH = str(Path(__file__).parent / 'UPPCS_2024_Prelims_GS1_Question_Paper.pdf')
FILE_ID = 'uppsc_2024_prelims_gs1'

# Number of pages to process
PAGES_TO_PROCESS = 5

# Helper: Detect if a line is mostly English (not Hindi)
def is_english(text):
    # Heuristic: If >60% of chars are ASCII, treat as English
    if not text.strip():
        return False
    ascii_count = sum(1 for c in text if ord(c) < 128)
    return ascii_count / max(1, len(text)) > 0.6

def extract_english_questions_from_ocr(ocr_data):
    english_questions = []
    for page in ocr_data:
        page_text = page.get('content', '')
        # Split by lines, keep only English lines
        english_lines = [line for line in page_text.split('\n') if is_english(line)]
        # Optionally, join lines back to paragraphs
        english_page = '\n'.join(english_lines).strip()
        if english_page:
            english_questions.append({
                'page_number': page.get('page_number'),
                'english_text': english_page
            })
    return english_questions

def main():
    print("\n🧪 Extracting English questions from UPPSC 2024 Prelims GS1 (first 5 pages)...")
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    if not mistral_api_key:
        print("❌ MISTRAL_API_KEY not found in environment variables")
        return
    extractor = UPSCBookOCRExtractor(api_key=mistral_api_key)
    # Process only the first 5 pages
    ocr_data = extractor.extract_upsc_book_data(
        pdf_path=PDF_PATH,
        file_id=FILE_ID,
        source_url=None,
        pages=list(range(1, PAGES_TO_PROCESS + 1)),
        include_images=False
    )
    if not ocr_data:
        print("❌ OCR extraction failed.")
        return
    english_questions = extract_english_questions_from_ocr(ocr_data)
    # Output results
    output_file = Path(__file__).parent / 'uppsc_2024_english_questions_first5.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(english_questions, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Extracted English questions saved to: {output_file}")
    print("\nSample output (first page):\n")
    if english_questions:
        print(english_questions[0]['english_text'][:1000])
    else:
        print("No English text found.")

if __name__ == "__main__":
    main() 