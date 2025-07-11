#!/usr/bin/env python3
"""
PDF Chapter Splitter for UPSC Books
Splits the main PDF into individual chapter files based on the index
"""

import json
import os
import subprocess
from pathlib import Path
from typing import List, Dict
import argparse
import PyPDF2

def load_chapter_index(index_file: str) -> Dict:
    """
    Load the chapter index from JSON file
    """
    with open(index_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def split_pdf_by_chapters(pdf_path: str, chapter_index: Dict, output_dir: str = "chapters"):
    """
    Split the PDF into individual chapter files
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    chapters = chapter_index['chapters']
    book_name = chapter_index['book_name']
    
    print(f"📚 Splitting '{book_name}' into {len(chapters)} chapters...")
    print("=" * 80)
    
    chapter_files = []
    
    for chapter in chapters:
        chapter_num = chapter['chapter_number']
        chapter_name = chapter['chapter_name']
        start_page = chapter['start_page']
        end_page = chapter['end_page']
        part = chapter['part']
        
        # Create safe filename with page range
        safe_name = chapter_name.replace(' ', '_').replace('/', '_').replace('&', 'and')
        output_filename = f"Chapter_{chapter_num:02d}_{safe_name}_pages_{start_page}-{end_page}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"📖 Chapter {chapter_num:2d}: {chapter_name}")
        print(f"    Part: {part}")
        print(f"    Pages: {start_page}-{end_page}")
        print(f"    Output: {output_filename}")
        
        # Use PyPDF2 to extract pages
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Create a PDF writer for the chapter
                pdf_writer = PyPDF2.PdfWriter()
                
                # Extract pages (adjust for 0-based indexing)
                # PDF page numbers in index are 1-based, but PyPDF2 uses 0-based
                for page_num in range(start_page - 1, end_page):
                    if page_num < len(pdf_reader.pages):
                        pdf_writer.add_page(pdf_reader.pages[page_num])
                
                # Write the chapter PDF
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                
                print(f"    ✅ Successfully created: {output_filename}")
                chapter_files.append({
                    'chapter_number': chapter_num,
                    'chapter_name': chapter_name,
                    'part': part,
                    'start_page': start_page,
                    'end_page': end_page,
                    'file_path': output_path,
                    'filename': output_filename
                })
                
        except Exception as e:
            print(f"    ❌ Error creating {output_filename}: {str(e)}")
        
        print()
    
    # Save chapter file list
    chapter_list_file = os.path.join(output_dir, "chapter_files.json")
    with open(chapter_list_file, 'w', encoding='utf-8') as f:
        json.dump({
            'book_name': book_name,
            'total_chapters': len(chapter_files),
            'chapters': chapter_files
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Chapter file list saved to: {chapter_list_file}")
    print(f"📊 Successfully created {len(chapter_files)} chapter files")
    
    return chapter_files

def process_chapters_with_ocr(chapter_files: List[Dict], base_file_id: str = "shankar_env"):
    """
    Process each chapter file with OCR
    """
    if not chapter_files:
        print("❌ No chapter files to process")
        return
    
    print(f"\n🔍 Processing {len(chapter_files)} chapters with OCR...")
    print("=" * 80)
    
    for chapter_info in chapter_files:
        chapter_num = chapter_info['chapter_number']
        chapter_name = chapter_info['chapter_name']
        file_path = chapter_info['file_path']
        
        print(f"\n📖 Processing Chapter {chapter_num}: {chapter_name}")
        print(f"    File: {chapter_info['filename']}")
        
        # Create file ID for this chapter
        file_id = f"{base_file_id}_ch{chapter_num:02d}"
        
        # Run OCR extraction
        try:
            cmd = [
                'python3', 'upsc_book_ocr_extractor.py',
                file_path,
                '--file-id', file_id,
                '--no-db'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"    ✅ OCR completed successfully")
                print(f"    📄 Output: upsc_output/{os.path.basename(file_path).replace('.pdf', '_consolidated.json')}")
            else:
                print(f"    ❌ OCR failed: {result.stderr}")
                
        except Exception as e:
            print(f"    ❌ Error running OCR: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Split PDF into chapters and process with OCR')
    parser.add_argument('pdf_path', help='Path to the main PDF file')
    parser.add_argument('--index-file', default='upsc_output/chapter_index.json', 
                       help='Path to chapter index JSON file')
    parser.add_argument('--output-dir', default='Books/Environment_Book_Chapters', 
                       help='Output directory for chapter files')
    parser.add_argument('--file-id', default='shankar_env', 
                       help='Base file ID for chapter files')
    parser.add_argument('--no-ocr', action='store_true', 
                       help='Skip OCR processing')
    
    args = parser.parse_args()
    
    # Check if files exist
    if not os.path.exists(args.pdf_path):
        print(f"❌ PDF file not found: {args.pdf_path}")
        return
    
    if not os.path.exists(args.index_file):
        print(f"❌ Index file not found: {args.index_file}")
        return
    
    # Load chapter index
    print(f"📖 Loading chapter index from: {args.index_file}")
    chapter_index = load_chapter_index(args.index_file)
    
    # Split PDF into chapters
    chapter_files = split_pdf_by_chapters(args.pdf_path, chapter_index, args.output_dir)
    
    if chapter_files and not args.no_ocr:
        # Process chapters with OCR
        process_chapters_with_ocr(chapter_files, args.file_id)
    
    print(f"\n🎉 Chapter splitting and processing completed!")

if __name__ == "__main__":
    main() 