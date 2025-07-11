#!/usr/bin/env python3
"""
Simple NCERT OCR Test
=====================

A simple test to verify NCERT OCR processing works with descriptive filenames.
"""

import os
import sys
import json
from pathlib import Path

# Add pipeline_components to path
sys.path.append(str(Path(__file__).parent / 'pipeline_components'))

from upsc_book_ocr_extractor import UPSCBookOCRExtractor

def simple_ncert_test():
    """Simple test of NCERT OCR processing."""
    
    print("🧪 Simple NCERT OCR Test")
    print("=" * 50)
    
    # Check environment variables
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not mistral_api_key:
        print("❌ MISTRAL_API_KEY not found in environment variables")
        return
    
    if not openai_api_key:
        print("⚠️ OPENAI_API_KEY not found. Summaries will not be generated.")
    
    # Initialize extractor
    extractor = UPSCBookOCRExtractor(
        api_key=mistral_api_key,
        openai_api_key=openai_api_key
    )
    
    # Test with one Geography chapter
    pdf_path = "Books/NCERT_Books/geography/9/contemporary_India_I/geography_class_9_book_contemporary_India_I_chapter_1.pdf"
    file_id = "geography_class_9_book_contemporary_India_I_chapter_1"
    
    print(f"📚 Testing Geography Chapter 1")
    print(f"📄 File: {pdf_path}")
    print(f"🆔 File ID: {file_id}")
    
    # Check if file exists
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        return
    
    try:
        # Process the chapter
        processed_data = extractor.extract_upsc_book_data(
            pdf_path=pdf_path,
            file_id=file_id,
            source_url=None,
            pages=None,
            include_images=False
        )
        
        if not processed_data:
            print(f"❌ Failed to process Geography chapter")
            return
        
        # Count summaries and keywords
        summaries = sum(1 for page in processed_data if page.get('metadata', {}).get('summary'))
        keywords = sum(1 for page in processed_data if page.get('metadata', {}).get('keywords'))
        
        # Extract metadata for verification
        first_page = processed_data[0]
        extracted_metadata = {
            "subject": first_page.get("subject"),
            "book_name": first_page.get("book_name"),
            "chapter_name": first_page.get("chapter_name"),
            "chapter_number": first_page.get("chapter_number"),
            "class": first_page.get("metadata", {}).get("class"),
            "part": first_page.get("metadata", {}).get("part")
        }
        
        print(f"✅ Successfully processed {len(processed_data)} pages")
        print(f"📝 Generated {summaries} summaries")
        print(f"🏷️ Generated {keywords} keyword sets")
        print(f"📊 Metadata: {extracted_metadata}")
        
        # Save sample result
        output_dir = Path("test_results")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "geography_simple_test.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved test result to: {output_file}")
        
        # Show a sample of the extracted content
        if processed_data:
            sample_page = processed_data[0]
            print(f"\n📄 Sample Page Content:")
            print(f"   Subject: {sample_page.get('subject')}")
            print(f"   Book Name: {sample_page.get('book_name')}")
            print(f"   Chapter: {sample_page.get('chapter_name')} ({sample_page.get('chapter_number')})")
            print(f"   Class: {sample_page.get('metadata', {}).get('class')}")
            print(f"   Part: {sample_page.get('metadata', {}).get('part')}")
            print(f"   Summary: {sample_page.get('metadata', {}).get('summary', 'No summary')[:100]}...")
        
    except Exception as e:
        print(f"❌ Error processing Geography chapter: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_ncert_test() 