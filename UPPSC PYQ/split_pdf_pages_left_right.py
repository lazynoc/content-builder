#!/usr/bin/env python3
"""
Split PDF Pages into Combined Hindi and English PDFs
==================================================

This script extracts ALL pages of the UPPSC 2024 Prelims GS1 PDF,
splits each page into left and right halves (Hindi/English), and saves them as two combined PDFs.
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
    hindi_images.append(left_img)
    
    # Right half (English)
    right_img = page_img.crop((mid, 0, w, h))
    english_images.append(right_img)
    
    print(f"Processed page {page_number}/{len(pages)}")

# Create combined PDFs only
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

print(f"\n🎉 SUCCESS! Split complete:")
print(f"📄 Pages processed: {len(pages)}")
print(f"� Hindi PDF: {combined_hindi_path.name} ({combined_hindi_path.stat().st_size / 1024 / 1024:.1f} MB)")
print(f"📚 English PDF: {combined_english_path.name} ({combined_english_path.stat().st_size / 1024 / 1024:.1f} MB)")
print(f"📁 Files saved in: {OUTPUT_DIR}") 