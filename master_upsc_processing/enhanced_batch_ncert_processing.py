#!/usr/bin/env python3
"""
Enhanced Batch NCERT Processing Script

This script processes all NCERT books across all subjects and classes,
with proper cumulative page numbering across chapters within the same book.
"""

import os
import json
import glob
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import sys
import re

# Add the pipeline components to the path
sys.path.append('pipeline_components')

from upsc_book_ocr_extractor import UPSCBookOCRExtractor

class EnhancedNCERTBatchProcessor:
    def __init__(self, api_key: str, openai_api_key: str = None):
        """
        Initialize the enhanced NCERT batch processor.
        
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
    
    def extract_chapter_number(self, filename: str) -> int:
        """
        Extract chapter number from filename.
        
        Args:
            filename: The filename (e.g., "geography_class_9_book_contemporary_India_I_chapter_1")
            
        Returns:
            Chapter number as integer
        """
        try:
            # Extract chapter number from pattern: ..._chapter_X
            match = re.search(r'_chapter_(\d+)$', filename)
            if match:
                return int(match.group(1))
            return 1  # Default to chapter 1
        except:
            return 1
    
    def get_all_ncert_files_by_book(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all NCERT PDF files organized by book.
        
        Returns:
            Dictionary with book keys and lists of file information
        """
        files_by_book = {}
        base_path = Path("Books/NCERT_Books")
        
        for subject, classes in self.ncert_structure.items():
            for class_num, books in classes.items():
                for book in books:
                    # Construct the path pattern
                    book_path = base_path / subject / class_num / book
                    
                    if book_path.exists():
                        # Find all PDF files in this book directory
                        pdf_files = list(book_path.glob("*.pdf"))
                        
                        # Create book key
                        book_key = f"{subject}_{class_num}_{book}"
                        files_by_book[book_key] = []
                        
                        for pdf_file in pdf_files:
                            # Extract file ID from filename
                            filename = pdf_file.stem  # Remove .pdf extension
                            chapter_num = self.extract_chapter_number(filename)
                            
                            # Create file info
                            file_info = {
                                'file_path': str(pdf_file),
                                'file_id': filename,
                                'subject': subject,
                                'class': class_num,
                                'book_name': book,
                                'filename': pdf_file.name,
                                'chapter_number': chapter_num
                            }
                            
                            files_by_book[book_key].append(file_info)
        
        # Sort chapters within each book
        for book_key in files_by_book:
            files_by_book[book_key].sort(key=lambda x: x['chapter_number'])
        
        return files_by_book
    
    def process_book_with_cumulative_pages(self, book_key: str, files: List[Dict[str, Any]]) -> bool:
        """
        Process all chapters of a book with cumulative page numbering.
        
        Args:
            book_key: The book identifier
            files: List of file information for all chapters
            
        Returns:
            True if successful, False otherwise
        """
        print(f"\n📚 Processing Book: {book_key}")
        print(f"📑 Chapters: {len(files)}")
        print("-" * 50)
        
        cumulative_page_count = 0
        all_processed_data = []
        
        for i, file_info in enumerate(files):
            try:
                print(f"\n📖 Chapter {file_info['chapter_number']} ({i+1}/{len(files)})")
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
                    continue
                
                # Update page numbers with cumulative count
                for page_data in processed_data:
                    page_data['page_number'] = cumulative_page_count + page_data['page_number']
                    page_data['metadata']['page_number'] = page_data['page_number']
                
                # Update cumulative page count
                cumulative_page_count += len(processed_data)
                
                # Add to all processed data
                all_processed_data.extend(processed_data)
                
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
                print(f"📄 Page Range: {processed_data[0]['page_number']}-{processed_data[-1]['page_number']}")
                
            except Exception as e:
                print(f"❌ Error processing {file_info['filename']}: {e}")
                self.stats['failed_files'] += 1
                self.stats['errors'].append({
                    'file': file_info['filename'],
                    'error': str(e)
                })
                continue
        
        # Save consolidated book data
        if all_processed_data:
            output_filename = f"{book_key}_complete_book.json"
            output_path = self.output_dir / output_filename
            
            # Create book-level metadata
            book_metadata = {
                'book_info': {
                    'book_key': book_key,
                    'subject': all_processed_data[0]['subject'],
                    'class': all_processed_data[0]['metadata']['class'],
                    'book_name': all_processed_data[0]['book_name'],
                    'total_chapters': len(files),
                    'total_pages': len(all_processed_data),
                    'page_range': f"{all_processed_data[0]['page_number']}-{all_processed_data[-1]['page_number']}",
                    'processing_date': datetime.now().isoformat()
                },
                'chapters': [
                    {
                        'chapter_number': file_info['chapter_number'],
                        'filename': file_info['filename'],
                        'pages': len([p for p in all_processed_data if p['chapter_number'] == file_info['chapter_number']])
                    }
                    for file_info in files
                ],
                'pages': all_processed_data
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(book_metadata, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Saved complete book to: {output_path}")
            print(f"📊 Total pages in book: {len(all_processed_data)}")
            print(f"📄 Book page range: {all_processed_data[0]['page_number']}-{all_processed_data[-1]['page_number']}")
            
            return True
        
        return False
    
    def process_all_books(self) -> Dict[str, Any]:
        """
        Process all NCERT books with cumulative page numbering.
        
        Returns:
            Processing statistics
        """
        print("🚀 Starting Enhanced Batch NCERT Processing")
        print("=" * 60)
        
        # Get all files organized by book
        files_by_book = self.get_all_ncert_files_by_book()
        total_files = sum(len(files) for files in files_by_book.values())
        self.stats['total_files'] = total_files
        
        print(f"📁 Found {len(files_by_book)} books with {total_files} total chapters")
        print(f"📂 Output directory: {self.output_dir}")
        print("=" * 60)
        
        # Process each book
        for i, (book_key, files) in enumerate(files_by_book.items(), 1):
            print(f"\n[{i}/{len(files_by_book)}] Processing book...")
            self.process_book_with_cumulative_pages(book_key, files)
        
        # Generate summary report
        self.generate_summary_report()
        
        return self.stats
    
    def generate_summary_report(self):
        """Generate and save a summary report."""
        report = {
            'processing_date': datetime.now().isoformat(),
            'summary': {
                'total_books': len(self.get_all_ncert_files_by_book()),
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
        report_path = self.output_dir / "enhanced_processing_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎉 ENHANCED BATCH PROCESSING COMPLETE")
        print("=" * 60)
        print(f"📚 Total Books: {report['summary']['total_books']}")
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
    """Main function to run the enhanced batch processing."""
    # Check if API key is provided
    api_key = os.getenv('MISTRAL_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ Error: MISTRAL_API_KEY environment variable not set")
        print("Please set your Mistral API key:")
        print("export MISTRAL_API_KEY='your_api_key_here'")
        return
    
    if not openai_api_key:
        print("⚠️  Warning: OPENAI_API_KEY not set. Summaries will be basic.")
    
    # Initialize processor
    processor = EnhancedNCERTBatchProcessor(api_key, openai_api_key)
    
    # Process all books
    stats = processor.process_all_books()
    
    # Exit with error code if any files failed
    if stats['failed_files'] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main() 