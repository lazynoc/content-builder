#!/usr/bin/env python3
"""
Test NCERT OCR with Descriptive Filenames
=========================================

This script tests the OCR extractor with NCERT books using descriptive filenames.
"""

import os
import sys
import json
from pathlib import Path

# Add pipeline_components to path
sys.path.append(str(Path(__file__).parent / 'pipeline_components'))

from upsc_book_ocr_extractor import UPSCBookOCRExtractor

def test_ncert_descriptive():
    """Test OCR processing with descriptive NCERT filenames."""
    
    print("🧪 Testing NCERT OCR with Descriptive Filenames")
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
    
    # Test chapters from each subject with descriptive filenames
    test_chapters = [
        {
            "subject": "Geography",
            "path": "Books/NCERT_Books/geography/9/contemporary_India_I/geography_class_9_book_contemporary_India_I_chapter_1.pdf",
            "file_id": "geography_class_9_book_contemporary_India_I_chapter_1"
        },
        {
            "subject": "History", 
            "path": "Books/NCERT_Books/history/9/india_and_contemporary_world_2/history_class_9_book_india_and_contemporary_world_2_chapter_1.pdf",
            "file_id": "history_class_9_book_india_and_contemporary_world_2_chapter_1"
        },
        {
            "subject": "Political Science",
            "path": "Books/NCERT_Books/political/11/indian_constitution_at_work/political_class_11_book_indian_constitution_at_work_chapter_1.pdf", 
            "file_id": "political_class_11_book_indian_constitution_at_work_chapter_1"
        }
    ]
    
    results = {}
    
    for test_case in test_chapters:
        subject = test_case["subject"]
        pdf_path = test_case["path"]
        file_id = test_case["file_id"]
        
        print(f"\n📚 Testing {subject}")
        print(f"📄 File: {pdf_path}")
        print(f"🆔 File ID: {file_id}")
        
        # Check if file exists
        if not Path(pdf_path).exists():
            print(f"❌ File not found: {pdf_path}")
            continue
        
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
                print(f"❌ Failed to process {subject}")
                continue
            
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
            
            results[subject] = {
                "success": True,
                "pages_processed": len(processed_data),
                "summaries_generated": summaries,
                "keywords_generated": keywords,
                "metadata": extracted_metadata
            }
            
            print(f"✅ Successfully processed {len(processed_data)} pages")
            print(f"📝 Generated {summaries} summaries")
            print(f"🏷️ Generated {keywords} keyword sets")
            print(f"📊 Metadata: {extracted_metadata}")
            
            # Save sample result
            output_dir = Path("test_results")
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / f"{subject.lower()}_descriptive_test.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved test result to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error processing {subject}: {e}")
            results[subject] = {
                "success": False,
                "error": str(e)
            }
    
    # Summary
    print(f"\n🎉 Test Summary")
    print("=" * 50)
    
    successful_tests = sum(1 for result in results.values() if result.get("success"))
    total_tests = len(test_chapters)
    
    print(f"📊 Tests completed: {successful_tests}/{total_tests}")
    
    for subject, result in results.items():
        if result.get("success"):
            metadata = result["metadata"]
            print(f"✅ {subject}: {result['pages_processed']} pages, "
                  f"Subject: {metadata['subject']}, "
                  f"Class: {metadata['class']}, "
                  f"Chapter: {metadata['chapter_number']}")
        else:
            print(f"❌ {subject}: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_ncert_descriptive() 