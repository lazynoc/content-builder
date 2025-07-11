#!/usr/bin/env python3
"""
Extract Raw OCR Text from UPPSC 2024 Prelims GS1 (First 5 Pages)
==============================================================

This script extracts the full, unfiltered OCR text from the first 5 pages of the UPPSC 2024 Prelims GS1 PDF.
No language filtering, no structuring, no chat completion—just pure OCR output per page.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
import sys

# Add pipeline_components to path
sys.path.append(str(Path(__file__).parent.parent / 'master_upsc_processing' / 'pipeline_components'))
from upsc_book_ocr_extractor import UPSCBookOCRExtractor

# Load environment variables from .env in project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

PDF_PATH = str(Path(__file__).parent / 'UPPCS_2024_Prelims_GS1_Question_Paper.pdf')
FILE_ID = 'uppsc_2024_prelims_gs1_raw'
PAGES_TO_PROCESS = 5
OUTPUT_PATH = Path(__file__).parent / 'uppsc_2024_raw_ocr_first5.json'

MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
if not MISTRAL_API_KEY:
    raise RuntimeError('MISTRAL_API_KEY not found in environment variables')

extractor = UPSCBookOCRExtractor(api_key=MISTRAL_API_KEY)

def main():
    print(f"\n🧪 Extracting raw OCR text from first {PAGES_TO_PROCESS} pages of UPPSC 2024 Prelims GS1...")
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
    raw_pages = []
    for page in ocr_data:
        raw_pages.append({
            'page_number': page.get('page_number'),
            'raw_text': page.get('content', '')
        })
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(raw_pages, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Raw OCR text saved to: {OUTPUT_PATH}")
    print("\nSample output (first page):\n")
    if raw_pages:
        print(raw_pages[0]['raw_text'][:1000])
    else:
        print("No OCR text found.")

if __name__ == "__main__":
    main() 