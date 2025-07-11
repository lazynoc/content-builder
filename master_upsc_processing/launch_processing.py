#!/usr/bin/env python3
"""
Universal UPSC Book Processing Launcher
=======================================

This script launches the OCR processing for any book type (Environment, NCERT, etc.)
by detecting the book type from the folder structure.
"""

import os
import sys
import argparse
from pathlib import Path

# Add pipeline_components to path
sys.path.append(str(Path(__file__).parent / 'pipeline_components'))

from upsc_book_ocr_extractor import UPSCBookOCRExtractor

def detect_book_type(books_dir):
    """Detect book type from available folders."""
    available_books = []
    
    for item in books_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            available_books.append(item.name)
    
    return available_books

def get_book_config(book_type):
    """Get configuration for different book types."""
    configs = {
        "Environment_Book": {
            "input_pattern": "Chapter_*.pdf",
            "output_suffix": "_with_summaries.json",
            "folder_structure": "proper_chapters"
        },
        "NCERT_Books": {
            "input_pattern": "*.pdf",  # Will be updated based on NCERT structure
            "output_suffix": "_with_summaries.json",
            "folder_structure": "chapters"  # Will be created
        }
    }
    
    return configs.get(book_type, configs["Environment_Book"])

def main():
    parser = argparse.ArgumentParser(description="Universal UPSC Book Processing Launcher")
    parser.add_argument("--book-type", choices=["Environment_Book", "NCERT_Books"], 
                       help="Type of book to process")
    parser.add_argument("--list-books", action="store_true", 
                       help="List available books and exit")
    
    args = parser.parse_args()
    
    print("🚀 Universal UPSC Book Processing Launcher")
    print("=" * 50)
    
    # Check environment variables
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not mistral_api_key:
        print("❌ MISTRAL_API_KEY not found in environment variables")
        return
    
    if not openai_api_key:
        print("⚠️ OPENAI_API_KEY not found. Summaries will not be generated.")
    
    # Get base directory and books directory
    base_dir = Path(__file__).parent.resolve()
    books_dir = base_dir / "Books"
    
    # List available books if requested
    if args.list_books:
        available_books = detect_book_type(books_dir)
        print("📚 Available Books:")
        for i, book in enumerate(available_books, 1):
            print(f"   {i}. {book}")
        return
    
    # Detect book type if not specified
    if not args.book_type:
        available_books = detect_book_type(books_dir)
        if len(available_books) == 1:
            args.book_type = available_books[0]
            print(f"📚 Auto-detected book type: {args.book_type}")
        elif len(available_books) > 1:
            print("📚 Multiple books found. Please specify --book-type:")
            for book in available_books:
                print(f"   - {book}")
            print("\nUsage: python launch_processing.py --book-type <book_name>")
            return
        else:
            print("❌ No books found in Books directory")
            return
    
    # Validate book type exists
    book_dir = books_dir / args.book_type
    if not book_dir.exists():
        print(f"❌ Book directory not found: {book_dir}")
        return
    
    print(f"📚 Processing book: {args.book_type}")
    
    # Get book configuration
    config = get_book_config(args.book_type)
    
    # Initialize extractor
    extractor = UPSCBookOCRExtractor(
        api_key=mistral_api_key,
        openai_api_key=openai_api_key
    )
    
    # Set up paths based on book type
    if args.book_type == "Environment_Book":
        input_dir = book_dir / "Environment_Book_Chapters/proper_chapters"
        output_dir = book_dir / "Environment_Book_Chapters/proper_chapters/complete_processed_with_summaries"
    elif args.book_type == "NCERT_Books":
        # For NCERT books, we'll create a chapters folder
        input_dir = book_dir / "chapters"
        output_dir = book_dir / "chapters/complete_processed_with_summaries"
    else:
        input_dir = book_dir / config["folder_structure"]
        output_dir = book_dir / config["folder_structure"] / "complete_processed_with_summaries"
    
    # Check if input directory exists
    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        print(f"💡 Please ensure your book chapters are in: {input_dir}")
        return
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all PDF files
    pdf_pattern = config["input_pattern"]
    pdf_files = sorted(input_dir.glob(pdf_pattern))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {input_dir}")
        print(f"💡 Expected pattern: {pdf_pattern}")
        return
    
    print(f"📁 Found {len(pdf_files)} chapter PDFs")
    print(f"📁 Input directory: {input_dir}")
    print(f"📁 Output directory: {output_dir}")
    print("-" * 50)
    
    total_processed = 0
    total_pages = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        try:
            filename = pdf_file.name
            file_id = str(pdf_file)  # Full path for better book detection
            
            print(f"\n📄 Processing {i}/{len(pdf_files)}: {filename}")
            
            # Process the chapter
            processed_data = extractor.extract_upsc_book_data(
                pdf_path=str(pdf_file),
                file_id=file_id,
                source_url=None,
                pages=None,
                include_images=False
            )
            
            if not processed_data:
                print(f"❌ Failed to process {filename}")
                continue
            
            # Count summaries and keywords
            summaries = sum(1 for page in processed_data if page.get('metadata', {}).get('summary'))
            keywords = sum(1 for page in processed_data if page.get('metadata', {}).get('keywords'))
            
            total_pages += len(processed_data)
            
            # Save results
            output_filename = filename.replace('.pdf', config["output_suffix"])
            output_file = Path(output_dir) / output_filename
            
            with open(output_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(processed_data, f, indent=2, ensure_ascii=False)
            
            total_processed += 1
            
            print(f"✅ Processed {len(processed_data)} pages")
            print(f"📝 Generated {summaries} summaries")
            print(f"🏷️ Generated {keywords} keyword sets")
            print(f"💾 Saved to: {output_filename}")
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            continue
    
    print(f"\n🎉 Processing Complete!")
    print(f"📊 Summary:")
    print(f"   Book type: {args.book_type}")
    print(f"   Total chapters processed: {total_processed}")
    print(f"   Total pages: {total_pages}")
    print(f"   Output directory: {output_dir}")

if __name__ == "__main__":
    main() 