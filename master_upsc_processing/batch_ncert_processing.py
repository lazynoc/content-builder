#!/usr/bin/env python3
"""
Batch NCERT Processing Script

This script processes all NCERT books across all subjects and classes,
extracting OCR data with proper metadata and saving to JSON files.
"""

import os
import json
import glob
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import sys

# Add the pipeline components to the path
sys.path.append('pipeline_components')

from upsc_book_ocr_extractor import UPSCBookOCRExtractor

class NCERTBatchProcessor:
    def __init__(self, api_key: str, openai_api_key: str = None):
        """
        Initialize the NCERT batch processor.
        
        Args:
            api_key: OCR API key
            openai_api_key: OpenAI API key for summaries (optional)
        """
        self.api_key = api_key
        self.openai_api_key = openai_api_key
        self.extractor = UPSCBookOCRExtractor(api_key, openai_api_key=openai_api_key)
        
        # Define NCERT book structure
        self.ncert_structure = {
            'geography': {
                '9': ['contemporary_India_I'],
                '10': ['contemporary_India_II'],
                '11': ['fundamental_of_physical_geography', 'india_physical_environment', 'practical_work_in_geography_I'],
                '12': ['fundamental_of_human_geography', 'india_people_and_economy', 'practical_work_in_geography_2']
            },
            'history': {
                '9': ['india_and_contemporary_world_2'],
                '10': ['india_and_contemporary_world_2'],
                '11': ['themes_in_world_history'],
                '12': ['themes_in_indian_history_1', 'themes_in_indian_history_2', 'themes_in_indian_history_3']
            },
            'political': {
                '11': ['indian_constitution_at_work', 'political_theory'],
                '12': ['contemporary_world_politics', 'politics_in_India_since_independence']
            },
            'fine_arts': {
                '11': ['an_introduction_to_indian_art_part_1']
            }
        }
        
        # Output directory for processed files
        self.output_dir = Path("Books/NCERT_Books/processed_json")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics tracking
        self.stats = {
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'total_pages': 0,
            'subjects_processed': set(),
            'classes_processed': set(),
            'errors': []
        }
    
    def get_all_ncert_files(self) -> List[Dict[str, Any]]:
        """
        Get all NCERT PDF files with their metadata.
        
        Returns:
            List of file information dictionaries
        """
        files = []
        base_path = Path("Books/NCERT_Books")
        
        for subject, classes in self.ncert_structure.items():
            for class_num, books in classes.items():
                for book in books:
                    # Construct the path pattern
                    book_path = base_path / subject / class_num / book
                    
                    if book_path.exists():
                        # Find all PDF files in this book directory
                        pdf_files = list(book_path.glob("*.pdf"))
                        
                        for pdf_file in pdf_files:
                            # Extract file ID from filename
                            filename = pdf_file.stem  # Remove .pdf extension
                            
                            # Create file info
                            file_info = {
                                'file_path': str(pdf_file),
                                'file_id': filename,
                                'subject': subject,
                                'class': class_num,
                                'book_name': book,
                                'filename': pdf_file.name
                            }
                            
                            files.append(file_info)
        
        return files
    
    def process_single_file(self, file_info: Dict[str, Any]) -> bool:
        """
        Process a single NCERT file.
        
        Args:
            file_info: Dictionary containing file information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\n📚 Processing: {file_info['subject'].title()} Class {file_info['class']} - {file_info['book_name']}")
            print(f"📄 File: {file_info['filename']}")
            print(f"🆔 File ID: {file_info['file_id']}")
            
            # Extract OCR data
            processed_data = self.extractor.extract_upsc_book_data(
                pdf_path=file_info['file_path'],
                file_id=file_info['file_id'],
                include_images=True
            )
            
            if not processed_data:
                print(f"❌ Failed to process {file_info['filename']}")
                self.stats['failed_files'] += 1
                self.stats['errors'].append({
                    'file': file_info['filename'],
                    'error': 'No data extracted'
                })
                return False
            
            # Create output filename
            output_filename = f"{file_info['file_id']}_processed.json"
            output_path = self.output_dir / output_filename
            
            # Save to JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False)
            
            # Update statistics
            self.stats['successful_files'] += 1
            self.stats['total_pages'] += len(processed_data)
            self.stats['subjects_processed'].add(file_info['subject'])
            self.stats['classes_processed'].add(file_info['class'])
            
            # Print summary
            first_page = processed_data[0] if processed_data else {}
            print(f"✅ Successfully processed {len(processed_data)} pages")
            print(f"📊 Metadata: Subject: {first_page.get('subject', 'Unknown')}, "
                  f"Class: {first_page.get('metadata', {}).get('class', 'Unknown')}, "
                  f"Chapter: {first_page.get('chapter_number', 'Unknown')}")
            print(f"💾 Saved to: {output_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing {file_info['filename']}: {e}")
            self.stats['failed_files'] += 1
            self.stats['errors'].append({
                'file': file_info['filename'],
                'error': str(e)
            })
            return False
    
    def process_all_files(self) -> Dict[str, Any]:
        """
        Process all NCERT files.
        
        Returns:
            Processing statistics
        """
        print("🚀 Starting Batch NCERT Processing")
        print("=" * 60)
        
        # Get all files
        files = self.get_all_ncert_files()
        self.stats['total_files'] = len(files)
        
        print(f"📁 Found {len(files)} NCERT files to process")
        print(f"📂 Output directory: {self.output_dir}")
        print("=" * 60)
        
        # Process each file
        for i, file_info in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] Processing file...")
            self.process_single_file(file_info)
        
        # Generate summary report
        self.generate_summary_report()
        
        return self.stats
    
    def generate_summary_report(self):
        """Generate and save a summary report."""
        report = {
            'processing_date': datetime.now().isoformat(),
            'summary': {
                'total_files': self.stats['total_files'],
                'successful_files': self.stats['successful_files'],
                'failed_files': self.stats['failed_files'],
                'total_pages': self.stats['total_pages'],
                'success_rate': f"{(self.stats['successful_files'] / self.stats['total_files'] * 100):.1f}%" if self.stats['total_files'] > 0 else "0%"
            },
            'subjects_processed': list(self.stats['subjects_processed']),
            'classes_processed': list(self.stats['classes_processed']),
            'errors': self.stats['errors']
        }
        
        # Save report
        report_path = self.output_dir / "processing_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎉 BATCH PROCESSING COMPLETE")
        print("=" * 60)
        print(f"📊 Total Files: {self.stats['total_files']}")
        print(f"✅ Successful: {self.stats['successful_files']}")
        print(f"❌ Failed: {self.stats['failed_files']}")
        print(f"📄 Total Pages: {self.stats['total_pages']}")
        print(f"📈 Success Rate: {report['summary']['success_rate']}")
        print(f"📚 Subjects: {', '.join(self.stats['subjects_processed'])}")
        print(f"🎓 Classes: {', '.join(sorted(self.stats['classes_processed']))}")
        print(f"📋 Report saved to: {report_path}")
        print("=" * 60)

def main():
    """Main function to run the batch processing."""
    # Check if API key is provided
    api_key = os.getenv('OCR_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ Error: OCR_API_KEY environment variable not set")
        print("Please set your OCR API key:")
        print("export OCR_API_KEY='your_api_key_here'")
        return
    
    if not openai_api_key:
        print("⚠️  Warning: OPENAI_API_KEY not set. Summaries will be basic.")
    
    # Initialize processor
    processor = NCERTBatchProcessor(api_key, openai_api_key)
    
    # Process all files
    stats = processor.process_all_files()
    
    # Exit with error code if any files failed
    if stats['failed_files'] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main() 