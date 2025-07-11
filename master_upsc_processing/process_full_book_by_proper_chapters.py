#!/usr/bin/env python3
"""
Process Full Book by Proper Chapters
====================================

This script:
1. Uses OCR to extract text from the indexed PDF to get chapter information
2. Splits the full book into individual chapter PDFs (using existing tools)
3. Processes each chapter with correct metadata
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from datetime import datetime

# Import our existing components
from pipeline_components.index_parser import parse_index_json, ChapterInfo, print_chapter_summary, save_chapter_list
from pipeline_components.upsc_book_ocr_extractor import UPSCBookOCRExtractor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FullBookProcessor:
    def __init__(self):
        self.api_key = os.getenv('MISTRAL_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY environment variable is required")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.extractor = UPSCBookOCRExtractor(self.api_key, openai_api_key=self.openai_api_key)
        
        # Directory paths
        self.base_dir = Path(__file__).parent
        self.books_dir = self.base_dir / "Books" / "Environment_Book"
        self.output_dir = self.base_dir / "Books" / "Environment_Book_Chapters" / "proper_chapters"
        self.processed_dir = self.output_dir / "complete_processed_with_summaries"
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_index_using_ocr(self, indexed_pdf_path: str) -> str:
        """
        Extract text from the indexed PDF using our OCR extractor
        """
        logger.info(f"Extracting index using OCR from: {indexed_pdf_path}")
        
        try:
            # Use our OCR extractor to get the content
            file_id = "Environment_Book_Index"
            results = self.extractor.extract_upsc_book_data(
                indexed_pdf_path, 
                file_id, 
                include_images=False  # No need for images in index
            )
            
            if not results:
                raise ValueError("No results from OCR extraction")
            
            # Combine all page content
            index_text = ""
            for page_data in results:
                index_text += page_data.get("content", "") + "\n"
            
            logger.info(f"Successfully extracted {len(index_text)} characters from index PDF using OCR")
            return index_text
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF using OCR: {e}")
            raise
    
    def parse_chapters_from_index(self, index_text: str) -> List[ChapterInfo]:
        """
        Parse chapter information from the index text
        """
        logger.info("Parsing chapter information from index text")
        
        # Create a mock JSON structure for the index parser
        mock_json_data = {
            "pages": [
                {"content": line} for line in index_text.split('\n')
            ]
        }
        
        temp_json_file = self.output_dir / "temp_index.json"
        with open(temp_json_file, 'w', encoding='utf-8') as f:
            json.dump(mock_json_data, f, indent=2)
        
        # Parse chapters using our existing index parser
        chapters = parse_index_json(str(temp_json_file))
        
        # Clean up temporary files
        temp_json_file.unlink(missing_ok=True)
        
        logger.info(f"Extracted {len(chapters)} chapters from index")
        return chapters
    
    def create_chapter_pdfs_manually(self, full_book_path: str, chapters: List[ChapterInfo]) -> List[str]:
        """
        Create chapter PDFs by copying the full book and noting the page ranges
        For now, we'll just create a mapping file since we can't split PDFs without external tools
        """
        logger.info(f"Creating chapter mapping for {len(chapters)} chapters")
        
        # Create a chapter mapping file
        chapter_mapping = []
        
        for chapter in chapters:
            chapter_info = {
                "chapter_number": chapter.chapter_number,
                "chapter_name": chapter.chapter_name,
                "part": chapter.part,
                "start_page": chapter.start_page,
                "end_page": chapter.end_page,
                "page_count": chapter.end_page - chapter.start_page + 1,
                "full_book_path": str(full_book_path)
            }
            chapter_mapping.append(chapter_info)
        
        # Save chapter mapping
        mapping_file = self.output_dir / "chapter_mapping.json"
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump({
                "book_name": "Environment by Shankar IAS Academy",
                "total_chapters": len(chapters),
                "full_book_path": str(full_book_path),
                "chapters": chapter_mapping
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Chapter mapping saved to: {mapping_file}")
        return [str(full_book_path)] * len(chapters)  # Return full book path for each chapter
    
    def process_chapter_from_full_book(self, full_book_path: str, chapter_info: ChapterInfo) -> bool:
        """
        Process a single chapter by extracting pages from the full book using our OCR extractor
        """
        logger.info(f"Processing chapter {chapter_info.chapter_number}: {chapter_info.chapter_name}")
        
        # Create file ID with proper chapter information
        file_id = f"Chapter_{chapter_info.chapter_number:02d}_{chapter_info.chapter_name.replace(' ', '_')}_pages_{chapter_info.start_page}-{chapter_info.end_page}"
        
        try:
            # Calculate page indices (0-based for OCR extractor)
            start_page_index = chapter_info.start_page - 1
            end_page_index = chapter_info.end_page - 1
            page_indices = list(range(start_page_index, end_page_index + 1))
            
            # Extract data using our OCR extractor with specific pages
            results = self.extractor.extract_upsc_book_data(
                full_book_path, 
                file_id, 
                pages=page_indices,
                include_images=True
            )
            
            if not results:
                logger.error(f"No results from OCR extraction for chapter {chapter_info.chapter_number}")
                return False
            
            # Override metadata with correct chapter information from index
            for page_data in results:
                page_data["chapter_name"] = chapter_info.chapter_name
                page_data["chapter_number"] = chapter_info.chapter_number
                page_data["metadata"]["chapter_name"] = chapter_info.chapter_name
                page_data["metadata"]["chapter_number"] = chapter_info.chapter_number
                page_data["metadata"]["part"] = chapter_info.part
            
            # Save to file
            output_filename = f"{file_id}_with_summaries.json"
            output_path = self.processed_dir / output_filename
            
            # Create consolidated data structure
            consolidated_data = {
                "file_info": {
                    "file_id": file_id,
                    "book_name": "Environment by Shankar IAS Academy",
                    "subject": "Environment",
                    "chapter_number": chapter_info.chapter_number,
                    "chapter_name": chapter_info.chapter_name,
                    "part": chapter_info.part,
                    "start_page": chapter_info.start_page,
                    "end_page": chapter_info.end_page,
                    "total_pages": len(results),
                    "extraction_date": datetime.now().isoformat()
                },
                "pages": results
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Processed chapter {chapter_info.chapter_number}: {len(results)} pages")
            return True
            
        except Exception as e:
            logger.error(f"Error processing chapter {chapter_info.chapter_number}: {e}")
            return False
    
    def process_full_book(self):
        """
        Main method to process the full book
        """
        logger.info("🚀 Starting Full Book Processing")
        logger.info("=" * 60)
        
        # File paths
        indexed_pdf_path = self.books_dir / "Environment by Shankar IAS Academy (UpscStdEbooks) Indexed.pdf"
        full_book_path = self.books_dir / "Environment by Shankar IAS Academy (UpscStdEbooks)(page 1-346).pdf"
        
        if not indexed_pdf_path.exists():
            raise FileNotFoundError(f"Indexed PDF not found: {indexed_pdf_path}")
        if not full_book_path.exists():
            raise FileNotFoundError(f"Full book PDF not found: {full_book_path}")
        
        # Step 1: Extract index using OCR
        logger.info("📖 Step 1: Extracting index using OCR")
        index_text = self.extract_index_using_ocr(str(indexed_pdf_path))
        
        # Step 2: Parse chapters from index
        logger.info("📋 Step 2: Parsing chapter information")
        chapters = self.parse_chapters_from_index(index_text)
        
        # Print chapter summary
        print_chapter_summary(chapters)
        
        # Save chapter list
        chapter_list_path = self.output_dir / "chapter_index.json"
        save_chapter_list(chapters, str(chapter_list_path))
        
        # Step 3: Create chapter mapping
        logger.info("📋 Step 3: Creating chapter mapping")
        self.create_chapter_pdfs_manually(str(full_book_path), chapters)
        
        # Step 4: Process each chapter from full book
        logger.info("🔄 Step 4: Processing individual chapters from full book")
        successful_chapters = 0
        
        for chapter_info in chapters:
            if self.process_chapter_from_full_book(str(full_book_path), chapter_info):
                successful_chapters += 1
        
        # Summary
        logger.info("=" * 60)
        logger.info("🎉 Processing Complete!")
        logger.info(f"📊 Summary:")
        logger.info(f"   Total chapters: {len(chapters)}")
        logger.info(f"   Successful: {successful_chapters}")
        logger.info(f"   Failed: {len(chapters) - successful_chapters}")
        logger.info(f"   Output directory: {self.processed_dir}")
        
        return successful_chapters == len(chapters)

def main():
    """Main function"""
    try:
        processor = FullBookProcessor()
        success = processor.process_full_book()
        
        if success:
            print("\n🎉 All chapters processed successfully!")
        else:
            print("\n⚠️ Some chapters failed to process. Check logs for details.")
            
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise

if __name__ == "__main__":
    main() 