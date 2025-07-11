#!/usr/bin/env python3
"""
Simple Pipeline Runner
=====================

A simple script to run the UPSC book processing pipeline.

Usage:
    python run_pipeline.py

This script will prompt you for the required inputs and run the complete pipeline.
"""

import os
import sys
from pathlib import Path

def get_user_input():
    """Get input files and book details from user."""
    print("🚀 UPSC Book Processing Pipeline")
    print("=" * 50)
    
    # Get index PDF
    while True:
        index_pdf = input("📄 Enter path to INDEX PDF: ").strip()
        if os.path.exists(index_pdf):
            break
        print("❌ File not found. Please enter a valid path.")
    
    # Get full book PDF
    while True:
        full_pdf = input("📚 Enter path to FULL BOOK PDF: ").strip()
        if os.path.exists(full_pdf):
            break
        print("❌ File not found. Please enter a valid path.")
    
    # Get book name
    book_name = input("📖 Enter book name: ").strip()
    if not book_name:
        book_name = "UPSC_Book"
    
    # Get output directory (optional)
    output_dir = input("📁 Enter output directory (press Enter for default 'processed_books'): ").strip()
    if not output_dir:
        output_dir = "processed_books"
    
    return {
        'index_pdf': index_pdf,
        'full_pdf': full_pdf,
        'book_name': book_name,
        'output_dir': output_dir
    }

def main():
    """Main function."""
    try:
        # Get user input
        inputs = get_user_input()
        
        print("\n" + "=" * 50)
        print("📋 Pipeline Configuration:")
        print(f"   Index PDF: {inputs['index_pdf']}")
        print(f"   Full Book PDF: {inputs['full_pdf']}")
        print(f"   Book Name: {inputs['book_name']}")
        print(f"   Output Directory: {inputs['output_dir']}")
        print("=" * 50)
        
        # Confirm
        confirm = input("\nProceed with pipeline? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Pipeline cancelled.")
            return
        
        # Import and run pipeline
        from upsc_book_pipeline import UPSCBookPipeline
        
        pipeline = UPSCBookPipeline(inputs['book_name'], inputs['output_dir'])
        summary = pipeline.run_pipeline(inputs['index_pdf'], inputs['full_pdf'])
        
        print("\n" + "=" * 50)
        print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"📚 Book: {summary['book_name']}")
        print(f"📊 Chapters processed: {summary['statistics']['total_chapters']}")
        print(f"📁 Output directory: {pipeline.book_dir}")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n❌ Pipeline interrupted by user.")
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 