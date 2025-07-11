#!/usr/bin/env python3
"""
UPSC Book Processing Pipeline
============================

A comprehensive pipeline that automates the entire process from PDF input to Supabase ingestion.

Workflow:
1. Process indexed PDF to extract chapter information
2. Split full book PDF into chapters based on index
3. Perform OCR with image annotation and table extraction
4. Create structured JSON files chapter-wise
5. Generate embeddings and ingest into Supabase
6. Organize files into appropriate folders

Usage:
    python upsc_book_pipeline.py --index-pdf "path/to/index.pdf" --full-pdf "path/to/full_book.pdf" --book-name "Book Name"

Author: UPSC Books OCR Pipeline
"""

import os
import sys
import json
import argparse
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Import our custom modules
from index_parser import IndexParser
from pdf_chapter_splitter import PDFChapterSplitter
from upsc_book_ocr_extractor import UPSCBookOCRExtractor
from batch_supabase_ingest import main as batch_ingest

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class UPSCBookPipeline:
    """Main pipeline class for processing UPSC books."""
    
    def __init__(self, book_name: str, output_dir: str = "processed_books"):
        self.book_name = book_name
        self.output_dir = output_dir
        self.book_dir = os.path.join(output_dir, book_name.replace(" ", "_"))
        
        # Create directory structure
        self.create_directory_structure()
        
        # Get API keys
        mistral_api_key = os.getenv("MISTRAL_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not mistral_api_key:
            raise ValueError("MISTRAL_API_KEY environment variable is required")
        
        # Initialize components
        self.index_parser = IndexParser()
        self.chapter_splitter = PDFChapterSplitter()
        self.ocr_extractor = UPSCBookOCRExtractor(
            api_key=mistral_api_key,
            openai_api_key=openai_api_key
        )
        
        logger.info(f"🚀 Initialized pipeline for book: {book_name}")
        if openai_api_key:
            logger.info("✅ OpenAI API key found - summary generation enabled")
        else:
            logger.warning("⚠️ OpenAI API key not found - summary generation disabled")
    
    def create_directory_structure(self):
        """Create the directory structure for the book processing."""
        directories = [
            self.book_dir,
            os.path.join(self.book_dir, "raw_pdfs"),
            os.path.join(self.book_dir, "index_data"),
            os.path.join(self.book_dir, "chapter_pdfs"),
            os.path.join(self.book_dir, "ocr_output"),
            os.path.join(self.book_dir, "processed_chapters"),
            os.path.join(self.book_dir, "stored_in_vdb"),
            os.path.join(self.book_dir, "logs")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        logger.info(f"📁 Created directory structure: {self.book_dir}")
    
    def copy_input_files(self, index_pdf: str, full_pdf: str):
        """Copy input PDFs to the book directory."""
        try:
            # Copy index PDF
            index_dest = os.path.join(self.book_dir, "raw_pdfs", "index.pdf")
            shutil.copy2(index_pdf, index_dest)
            logger.info(f"📄 Copied index PDF: {index_dest}")
            
            # Copy full book PDF
            full_dest = os.path.join(self.book_dir, "raw_pdfs", "full_book.pdf")
            shutil.copy2(full_pdf, full_dest)
            logger.info(f"📄 Copied full book PDF: {full_dest}")
            
            return index_dest, full_dest
            
        except Exception as e:
            logger.error(f"❌ Error copying input files: {e}")
            raise
    
    def step1_parse_index(self, index_pdf: str) -> Dict[str, Any]:
        """Step 1: Parse the index PDF to extract chapter information."""
        logger.info("🔍 Step 1: Parsing index PDF...")
        
        try:
            index_data = self.index_parser.parse_index_pdf(index_pdf)
            
            # Save index data
            index_file = os.path.join(self.book_dir, "index_data", "chapter_index.json")
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Index parsed successfully: {len(index_data.get('chapters', []))} chapters found")
            logger.info(f"📄 Index data saved: {index_file}")
            
            return index_data
            
        except Exception as e:
            logger.error(f"❌ Error parsing index: {e}")
            raise
    
    def step2_split_chapters(self, full_pdf: str, index_data: Dict[str, Any]) -> List[str]:
        """Step 2: Split the full book PDF into individual chapter PDFs."""
        logger.info("✂️ Step 2: Splitting PDF into chapters...")
        
        try:
            chapter_pdfs = self.chapter_splitter.split_pdf_by_chapters(
                full_pdf, 
                index_data,
                output_dir=os.path.join(self.book_dir, "chapter_pdfs")
            )
            
            logger.info(f"✅ PDF split successfully: {len(chapter_pdfs)} chapter PDFs created")
            
            return chapter_pdfs
            
        except Exception as e:
            logger.error(f"❌ Error splitting PDF: {e}")
            raise
    
    def step3_ocr_extraction(self, chapter_pdfs: List[str]) -> List[str]:
        """Step 3: Perform OCR extraction on each chapter PDF."""
        logger.info("🔤 Step 3: Performing OCR extraction...")
        
        try:
            ocr_outputs = []
            
            for i, chapter_pdf in enumerate(chapter_pdfs, 1):
                logger.info(f"   Processing chapter {i}/{len(chapter_pdfs)}: {os.path.basename(chapter_pdf)}")
                
                output_file = self.ocr_extractor.process_chapter_pdf(
                    chapter_pdf,
                    output_dir=os.path.join(self.book_dir, "ocr_output"),
                    book_name=self.book_name
                )
                
                ocr_outputs.append(output_file)
            
            logger.info(f"✅ OCR extraction completed: {len(ocr_outputs)} files processed")
            
            return ocr_outputs
            
        except Exception as e:
            logger.error(f"❌ Error in OCR extraction: {e}")
            raise
    
    def step4_create_structured_json(self, ocr_outputs: List[str]) -> List[str]:
        """Step 4: Create structured JSON files for each chapter."""
        logger.info("📋 Step 4: Creating structured JSON files...")
        
        try:
            structured_files = []
            
            for ocr_file in ocr_outputs:
                # Load OCR data
                with open(ocr_file, 'r', encoding='utf-8') as f:
                    ocr_data = json.load(f)
                
                # Create structured output
                structured_data = self.create_structured_chapter_data(ocr_data)
                
                # Save structured file
                base_name = os.path.basename(ocr_file).replace('_ocr.json', '_processed.json')
                structured_file = os.path.join(self.book_dir, "processed_chapters", base_name)
                
                with open(structured_file, 'w', encoding='utf-8') as f:
                    json.dump(structured_data, f, indent=2, ensure_ascii=False)
                
                structured_files.append(structured_file)
                logger.info(f"   Created structured file: {base_name}")
            
            logger.info(f"✅ Structured JSON files created: {len(structured_files)} files")
            
            return structured_files
            
        except Exception as e:
            logger.error(f"❌ Error creating structured JSON: {e}")
            raise
    
    def create_structured_chapter_data(self, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create structured data from OCR output."""
        structured_data = {
            "book_name": self.book_name,
            "processing_date": datetime.now().isoformat(),
            "pages": []
        }
        
        # Process each page
        for page_data in ocr_data.get('pages', []):
            structured_page = {
                "page_number": page_data.get('page_number'),
                "content": page_data.get('content', ''),
                "metadata": {
                    "book_name": self.book_name,
                    "book_type": "UPSC_Study_Material",
                    "subject": "Environment",  # Can be made configurable
                    "chapter_name": page_data.get('metadata', {}).get('chapter_name', ''),
                    "chapter_number": page_data.get('metadata', {}).get('chapter_number', ''),
                    "document_type": "text_with_images",
                    "summary": page_data.get('metadata', {}).get('summary', ''),
                    "topic_tags": page_data.get('metadata', {}).get('topic_tags', []),
                    "key_concepts": page_data.get('metadata', {}).get('key_concepts', []),
                    "difficulty_level": page_data.get('metadata', {}).get('difficulty_level', 'intermediate'),
                    "learning_objectives": page_data.get('metadata', {}).get('learning_objectives', []),
                    "related_chapters": page_data.get('metadata', {}).get('related_chapters', []),
                    "prerequisites": page_data.get('metadata', {}).get('prerequisites', []),
                    "common_mistakes": page_data.get('metadata', {}).get('common_mistakes', []),
                    "content_analysis": page_data.get('metadata', {}).get('content_analysis', {}),
                    "image_count": page_data.get('metadata', {}).get('image_count', 0),
                    "integrated_content_length": len(page_data.get('content', '')),
                    "file_id": page_data.get('metadata', {}).get('file_id', ''),
                    "image_bbox": page_data.get('metadata', {}).get('image_bbox', []),
                    "page_metadata": page_data.get('metadata', {}).get('page_metadata', {})
                }
            }
            
            structured_data["pages"].append(structured_page)
        
        return structured_data
    
    def step5_supabase_ingestion(self, structured_files: List[str]):
        """Step 5: Ingest structured data into Supabase."""
        logger.info("🗄️ Step 5: Ingesting data into Supabase...")
        
        try:
            # Create a custom batch ingest script for this book
            self.create_custom_batch_ingest(structured_files)
            
            # Run the custom batch ingest
            import subprocess
            result = subprocess.run(['python3', 'temp_batch_ingest.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Supabase ingestion completed successfully")
            else:
                logger.error(f"❌ Supabase ingestion failed: {result.stderr}")
                raise Exception("Supabase ingestion failed")
            
        except Exception as e:
            logger.error(f"❌ Error in Supabase ingestion: {e}")
            raise
    
    def create_custom_batch_ingest(self, structured_files: List[str]):
        """Create a custom batch ingest script for this book."""
        script_content = f'''#!/usr/bin/env python3
import os
import sys
sys.path.append('.')

# Import the batch ingest functions
from batch_supabase_ingest import generate_embeddings, load_data, check_existing, insert_chunks, process_file, move_file

# Set custom paths for this book
SOURCE_DIR = "{os.path.join(self.book_dir, 'processed_chapters')}"
STORED_DIR = "{os.path.join(self.book_dir, 'stored_in_vdb')}"

def main():
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting custom batch ingest for {self.book_name}")
    
    # Get all structured files
    json_files = []
    for file in os.listdir(SOURCE_DIR):
        if file.endswith('.json') and 'processed' in file:
            json_files.append(os.path.join(SOURCE_DIR, file))
    
    json_files.sort()
    logger.info(f"Found {{len(json_files)}} files to process")
    
    # Process files
    results = []
    total_chunks = 0
    
    for i, json_file in enumerate(json_files, 1):
        logger.info(f"Processing {{i}}/{{len(json_files)}}: {{os.path.basename(json_file)}}")
        
        result = process_file(json_file)
        results.append(result)
        total_chunks += result['chunks']
        
        if result['status'] in ['success', 'skipped']:
            move_file(json_file)
    
    logger.info(f"Completed: {{len(results)}} files, {{total_chunks}} chunks")

if __name__ == "__main__":
    main()
'''
        
        with open('temp_batch_ingest.py', 'w') as f:
            f.write(script_content)
    
    def create_pipeline_summary(self, index_data: Dict[str, Any], chapter_pdfs: List[str], 
                              ocr_outputs: List[str], structured_files: List[str]):
        """Create a summary of the pipeline execution."""
        summary = {
            "book_name": self.book_name,
            "processing_date": datetime.now().isoformat(),
            "pipeline_version": "1.0",
            "steps_completed": {
                "step1_index_parsing": True,
                "step2_chapter_splitting": True,
                "step3_ocr_extraction": True,
                "step4_structured_json": True,
                "step5_supabase_ingestion": True
            },
            "statistics": {
                "total_chapters": len(index_data.get('chapters', [])),
                "chapter_pdfs_created": len(chapter_pdfs),
                "ocr_files_processed": len(ocr_outputs),
                "structured_files_created": len(structured_files)
            },
            "file_locations": {
                "index_data": os.path.join(self.book_dir, "index_data"),
                "chapter_pdfs": os.path.join(self.book_dir, "chapter_pdfs"),
                "ocr_output": os.path.join(self.book_dir, "ocr_output"),
                "processed_chapters": os.path.join(self.book_dir, "processed_chapters"),
                "stored_in_vdb": os.path.join(self.book_dir, "stored_in_vdb")
            }
        }
        
        # Save summary
        summary_file = os.path.join(self.book_dir, "pipeline_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Pipeline summary saved: {summary_file}")
        return summary
    
    def run_pipeline(self, index_pdf: str, full_pdf: str) -> Dict[str, Any]:
        """Run the complete pipeline."""
        logger.info("🚀 Starting UPSC Book Processing Pipeline")
        logger.info("=" * 60)
        
        try:
            # Copy input files
            index_dest, full_dest = self.copy_input_files(index_pdf, full_pdf)
            
            # Step 1: Parse index
            index_data = self.step1_parse_index(index_dest)
            
            # Step 2: Split chapters
            chapter_pdfs = self.step2_split_chapters(full_dest, index_data)
            
            # Step 3: OCR extraction
            ocr_outputs = self.step3_ocr_extraction(chapter_pdfs)
            
            # Step 4: Create structured JSON
            structured_files = self.step4_create_structured_json(ocr_outputs)
            
            # Step 5: Supabase ingestion
            self.step5_supabase_ingestion(structured_files)
            
            # Create summary
            summary = self.create_pipeline_summary(index_data, chapter_pdfs, ocr_outputs, structured_files)
            
            logger.info("=" * 60)
            logger.info("🎉 Pipeline completed successfully!")
            logger.info(f"📁 All files organized in: {self.book_dir}")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            raise


def main():
    """Main function to run the pipeline."""
    parser = argparse.ArgumentParser(description="UPSC Book Processing Pipeline")
    parser.add_argument("--index-pdf", required=True, help="Path to the indexed PDF")
    parser.add_argument("--full-pdf", required=True, help="Path to the full book PDF")
    parser.add_argument("--book-name", required=True, help="Name of the book")
    parser.add_argument("--output-dir", default="processed_books", help="Output directory")
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.index_pdf):
        logger.error(f"Index PDF not found: {args.index_pdf}")
        sys.exit(1)
    
    if not os.path.exists(args.full_pdf):
        logger.error(f"Full book PDF not found: {args.full_pdf}")
        sys.exit(1)
    
    try:
        # Initialize and run pipeline
        pipeline = UPSCBookPipeline(args.book_name, args.output_dir)
        summary = pipeline.run_pipeline(args.index_pdf, args.full_pdf)
        
        print("\n" + "=" * 60)
        print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📚 Book: {summary['book_name']}")
        print(f"📊 Chapters processed: {summary['statistics']['total_chapters']}")
        print(f"📁 Output directory: {pipeline.book_dir}")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 