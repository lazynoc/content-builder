#!/usr/bin/env python3
"""
Organize NCERT Files Structure
==============================

This script organizes NCERT files into a hierarchical folder structure:
subject/class/book/chapters
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def parse_ncert_filename(filename):
    """Parse NCERT filename to extract metadata."""
    # Remove .pdf extension
    name = filename.replace('.pdf', '')
    
    # Parse the components
    parts = name.split('_')
    
    # Extract subject (first part)
    subject = parts[0]
    
    # Find class (after 'class')
    class_index = parts.index('class')
    class_num = parts[class_index + 1]
    
    # Find book name (between 'book' and 'chapter')
    book_index = parts.index('book')
    chapter_index = parts.index('chapter')
    book_name_parts = parts[book_index + 1:chapter_index]
    book_name = '_'.join(book_name_parts)
    
    # Extract chapter number
    chapter_num = parts[chapter_index + 1]
    
    return {
        'subject': subject,
        'class': class_num,
        'book_name': book_name,
        'chapter_number': int(chapter_num),
        'original_filename': filename
    }

def organize_ncert_files():
    """Organize NCERT files into hierarchical structure."""
    ncert_dir = Path("Books/NCERT_Books")
    
    if not ncert_dir.exists():
        print("❌ NCERT_Books directory not found")
        return
    
    print("📁 Organizing NCERT Files Structure")
    print("=" * 50)
    
    # Get all PDF files
    pdf_files = list(ncert_dir.glob("*.pdf"))
    print(f"📚 Found {len(pdf_files)} PDF files")
    
    # Group files by subject, class, and book
    file_groups = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for pdf_file in pdf_files:
        try:
            metadata = parse_ncert_filename(pdf_file.name)
            subject = metadata['subject']
            class_num = metadata['class']
            book_name = metadata['book_name']
            
            file_groups[subject][class_num][book_name].append({
                'file': pdf_file,
                'metadata': metadata
            })
        except Exception as e:
            print(f"⚠️  Error parsing {pdf_file.name}: {e}")
            continue
    
    # Create folder structure and move files
    moved_count = 0
    
    for subject, classes in file_groups.items():
        print(f"\n📖 Subject: {subject}")
        
        for class_num, books in classes.items():
            print(f"  📚 Class: {class_num}")
            
            for book_name, chapters in books.items():
                print(f"    📗 Book: {book_name} ({len(chapters)} chapters)")
                
                # Create folder structure
                book_folder = ncert_dir / subject / class_num / book_name
                book_folder.mkdir(parents=True, exist_ok=True)
                
                # Sort chapters by chapter number
                chapters.sort(key=lambda x: x['metadata']['chapter_number'])
                
                # Move files and rename for consistency
                for i, chapter_data in enumerate(chapters):
                    original_file = chapter_data['file']
                    chapter_num = chapter_data['metadata']['chapter_number']
                    
                    # Create new filename with page numbers (assuming sequential)
                    new_filename = f"chapter_{chapter_num:02d}.pdf"
                    new_path = book_folder / new_filename
                    
                    try:
                        # Move file to new location
                        original_file.rename(new_path)
                        print(f"      ✅ {original_file.name} → {new_filename}")
                        moved_count += 1
                    except Exception as e:
                        print(f"      ❌ Error moving {original_file.name}: {e}")
    
    print(f"\n🎉 Organization Complete!")
    print(f"📊 Files moved: {moved_count}")
    print(f"📁 New structure created in: {ncert_dir}")
    
    # Show the new structure
    print(f"\n📂 New Folder Structure:")
    for subject in sorted(file_groups.keys()):
        print(f"  📖 {subject}/")
        for class_num in sorted(file_groups[subject].keys()):
            print(f"    📚 {class_num}/")
            for book_name in sorted(file_groups[subject][class_num].keys()):
                chapter_count = len(file_groups[subject][class_num][book_name])
                print(f"      📗 {book_name}/ ({chapter_count} chapters)")

if __name__ == "__main__":
    organize_ncert_files() 