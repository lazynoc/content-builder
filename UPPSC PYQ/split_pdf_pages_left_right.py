#!/usr/bin/env python3
"""
Split PDF Pages into Left (Hindi) and Right (English) Images
===========================================================

This script extracts the first 5 pages of the UPPSC 2024 Prelims GS1 PDF,
splits each page into left and right halves (Hindi/English), and saves the images for OCR.
"""

import os
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image

PDF_PATH = Path(__file__).parent / 'UPPCS_2024_Prelims_GS1_Question_Paper.pdf'
OUTPUT_DIR = Path(__file__).parent / 'split_pages'
PAGES_TO_PROCESS = 5

OUTPUT_DIR.mkdir(exist_ok=True)

# Convert first 5 pages to images
print(f"Converting first {PAGES_TO_PROCESS} pages to images...")
pages = convert_from_path(str(PDF_PATH), first_page=1, last_page=PAGES_TO_PROCESS)

for idx, page_img in enumerate(pages):
    page_number = idx + 1
    w, h = page_img.size
    mid = w // 2
    # Left half (Hindi)
    left_img = page_img.crop((0, 0, mid, h))
    left_path = OUTPUT_DIR / f"page_{page_number:02d}_left_hindi.png"
    left_img.save(left_path)
    # Right half (English)
    right_img = page_img.crop((mid, 0, w, h))
    right_path = OUTPUT_DIR / f"page_{page_number:02d}_right_english.png"
    right_img.save(right_path)
    print(f"Saved: {left_path} and {right_path}")

print("\n✅ Page splitting complete. Images saved in:", OUTPUT_DIR) 