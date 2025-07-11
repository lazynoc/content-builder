#!/usr/bin/env python3
"""
Split Hindi and English Questions from Raw OCR Output
====================================================

This script reads the raw OCR output from the first 5 pages of the UPPSC 2024 Prelims GS1 paper,
and splits the content into separate Hindi and English JSON files per page.
"""

import json
import re
from pathlib import Path

RAW_OCR_PATH = Path(__file__).parent / 'uppsc_2024_raw_ocr_first5.json'
ENGLISH_OUT_PATH = Path(__file__).parent / 'uppsc_2024_english_questions_first5.json'
HINDI_OUT_PATH = Path(__file__).parent / 'uppsc_2024_hindi_questions_first5.json'

# Helper: Detect if a line is mostly Hindi (Devanagari)
def is_hindi(text):
    # If more than 30% of chars are Devanagari, treat as Hindi
    dev_count = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    return dev_count / max(1, len(text)) > 0.3

# Helper: Detect if a line is mostly English/Latin
def is_english(text):
    ascii_count = sum(1 for c in text if ord(c) < 128)
    return ascii_count / max(1, len(text)) > 0.6

def split_questions(raw_text):
    # Split by question number pattern (handles both Hindi and English)
    blocks = re.split(r'(?m)^\s*\d+\.', raw_text)
    # The first block may be header/empty, skip if so
    if blocks and not blocks[0].strip():
        blocks = blocks[1:]
    hindi_blocks = []
    english_blocks = []
    for block in blocks:
        lines = block.strip().split('\n')
        hindi_lines = [line for line in lines if is_hindi(line)]
        english_lines = [line for line in lines if is_english(line)]
        # If most lines are Hindi, treat as Hindi block
        if len(hindi_lines) > len(english_lines):
            hindi_blocks.append(block.strip())
        elif len(english_lines) > 0:
            english_blocks.append(block.strip())
    return hindi_blocks, english_blocks

def main():
    with open(RAW_OCR_PATH, 'r', encoding='utf-8') as f:
        raw_pages = json.load(f)
    all_hindi = []
    all_english = []
    for page in raw_pages:
        page_number = page['page_number']
        raw_text = page['raw_text']
        hindi_blocks, english_blocks = split_questions(raw_text)
        for idx, block in enumerate(hindi_blocks):
            all_hindi.append({'page_number': page_number, 'block_index': idx+1, 'text': block})
        for idx, block in enumerate(english_blocks):
            all_english.append({'page_number': page_number, 'block_index': idx+1, 'text': block})
    with open(HINDI_OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_hindi, f, indent=2, ensure_ascii=False)
    with open(ENGLISH_OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_english, f, indent=2, ensure_ascii=False)
    print(f"✅ Split complete.\nEnglish: {ENGLISH_OUT_PATH}\nHindi: {HINDI_OUT_PATH}")
    if all_english:
        print("\nSample English block:\n", all_english[0]['text'][:500])
    if all_hindi:
        print("\nSample Hindi block:\n", all_hindi[0]['text'][:500])

if __name__ == "__main__":
    main() 