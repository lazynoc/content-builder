#!/usr/bin/env python3
"""
Split PDF Pages into Left (Hindi) and Right (English) PDFs
=========================================================

This script extracts ALL pages of the UPPSC 2024 Prelims GS1 PDF,
splits each page into left and right halves (Hindi/English), and saves them as PDFs.
"""

import os
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image

PDF_PATH = Path(__file__).parent / 'UPPCS_2024_Prelims_GS1_Question_Paper.pdf'
OUTPUT_DIR = Path(__file__).parent / 'split_pages'

OUTPUT_DIR.mkdir(exist_ok=True)

# Convert ALL pages to images
print("Converting ALL pages to images...")
pages = convert_from_path(str(PDF_PATH))

print(f"Found {len(pages)} pages to process...")

hindi_images = []
english_images = []

for idx, page_img in enumerate(pages):
    page_number = idx + 1
    w, h = page_img.size
    mid = w // 2
    
    # Left half (Hindi)
    left_img = page_img.crop((0, 0, mid, h))
    left_path = OUTPUT_DIR / f"page_{page_number:02d}_left_hindi.pdf"
    left_img.save(left_path, "PDF")
    hindi_images.append(left_img)
    
    # Right half (English)
    right_img = page_img.crop((mid, 0, w, h))
    right_path = OUTPUT_DIR / f"page_{page_number:02d}_right_english.pdf"
    right_img.save(right_path, "PDF")
    english_images.append(right_img)
    
    print(f"Saved: {left_path} and {right_path}")

# Create combined PDFs
print("\nCreating combined PDFs...")

# Combined Hindi PDF
combined_hindi_path = OUTPUT_DIR / "UPPSC_2024_Complete_Hindi_Questions.pdf"
if hindi_images:
    hindi_images[0].save(combined_hindi_path, "PDF", save_all=True, append_images=hindi_images[1:])
    print(f"✅ Combined Hindi PDF saved: {combined_hindi_path}")

# Combined English PDF
combined_english_path = OUTPUT_DIR / "UPPSC_2024_Complete_English_Questions.pdf"
if english_images:
    english_images[0].save(combined_english_path, "PDF", save_all=True, append_images=english_images[1:])
    print(f"✅ Combined English PDF saved: {combined_english_path}")

print(f"\n✅ Page splitting complete. Files saved in: {OUTPUT_DIR}")
print(f"📄 Individual PDFs: {len(pages) * 2} files")
print(f"📚 Combined PDFs: 2 files (Hindi + English)") 