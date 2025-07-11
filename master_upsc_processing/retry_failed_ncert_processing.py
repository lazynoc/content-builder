#!/usr/bin/env python3
"""
Retry Failed NCERT Processing Script
Retries processing of files that failed due to API authorization issues
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from pipeline_components.upsc_book_ocr_extractor import UPSCBookOCRExtractor

def load_failed_files():
    """Load the list of failed files from the most recent retry report, or fall back to the enhanced processing report"""
    retry_report_path = "master_upsc_processing/Books/NCERT_Books/processed_json/retry_report.json"
    enhanced_report_path = "master_upsc_processing/Books/NCERT_Books/processed_json/enhanced_processing_report.json"

    if os.path.exists(retry_report_path):
        with open(retry_report_path, 'r') as f:
            report = json.load(f)
        # The failed files are under 'failed_retries', each is a dict with 'file' key
        failed_files = [error['file'] for error in report.get('failed_retries', [])]
        if failed_files:
            print(f"Loaded failed files from retry_report.json ({len(failed_files)} files)")
            return failed_files
        else:
            print("No failed files found in retry_report.json, falling back to enhanced_processing_report.json")

    if os.path.exists(enhanced_report_path):
        with open(enhanced_report_path, 'r') as f:
            report = json.load(f)
        failed_files = [error['file'] for error in report.get('errors', [])]
        if failed_files:
            print(f"Loaded failed files from enhanced_processing_report.json ({len(failed_files)} files)")
            return failed_files
        else:
            print("No failed files found in enhanced_processing_report.json.")
            return []
    else:
        print("❌ No retry or enhanced processing report found!")
        return []

def build_ncert_pdf_mapping():
    """Build a mapping from filename to full path for all NCERT PDFs, using the same logic as batch/enhanced batch processors."""
    ncert_structure = {
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
    base_path = Path("master_upsc_processing/Books/NCERT_Books")
    pdf_map = {}
    for subject, classes in ncert_structure.items():
        for class_num, books in classes.items():
            for book in books:
                book_path = base_path / subject / class_num / book
                if book_path.exists():
                    for pdf_file in book_path.glob("*.pdf"):
                        pdf_map[pdf_file.name] = str(pdf_file)
    return pdf_map

def find_file_path(filename, pdf_map):
    """Find the full path of a failed file using the prebuilt mapping."""
    return pdf_map.get(filename)

def retry_failed_processing():
    """Retry processing of failed files"""
    print("🔄 RETRYING FAILED NCERT PROCESSING")
    print("=" * 50)
    
    # Load failed files
    failed_files = load_failed_files()
    
    if not failed_files:
        print("✅ No failed files found to retry!")
        return
    
    print(f"📋 Found {len(failed_files)} failed files to retry")
    print()
    
    # Load API keys from environment
    api_key = os.getenv('MISTRAL_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ Error: MISTRAL_API_KEY environment variable not set")
        print("Please set your Mistral API key:")
        print("export MISTRAL_API_KEY='your_api_key_here'")
        return
    
    if not openai_api_key:
        print("⚠️  Warning: OPENAI_API_KEY not set. Summaries will be basic.")
    
    # Initialize OCR extractor
    extractor = UPSCBookOCRExtractor(api_key, openai_api_key=openai_api_key)
    
    # Track results
    successful_retries = []
    failed_retries = []
    
    # Build mapping of all available NCERT PDFs
    pdf_map = build_ncert_pdf_mapping()
    
    for i, filename in enumerate(failed_files, 1):
        print(f"🔄 Retrying {i}/{len(failed_files)}: {filename}")
        
        # Find file path using mapping
        file_path = find_file_path(filename, pdf_map)
        if not file_path:
            print(f"❌ File not found: {filename}")
            failed_retries.append({
                'file': filename,
                'error': 'File not found'
            })
            continue
        
        try:
            # Extract file ID from filename
            file_id = filename.replace('.pdf', '')
            
            # Extract data
            result = extractor.extract_upsc_book_data(file_path, file_id)
            
            if result and len(result) > 0:
                print(f"✅ Successfully retried: {filename}")
                successful_retries.append(filename)
                
                # Save individual chapter result
                output_dir = "master_upsc_processing/Books/NCERT_Books/processed_json/retry_results"
                os.makedirs(output_dir, exist_ok=True)
                
                output_file = os.path.join(output_dir, f"retry_{filename.replace('.pdf', '.json')}")
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                
            else:
                print(f"❌ Still failed: {filename}")
                failed_retries.append({
                    'file': filename,
                    'error': 'No data extracted'
                })
                
        except Exception as e:
            print(f"❌ Error retrying {filename}: {str(e)}")
            failed_retries.append({
                'file': filename,
                'error': str(e)
            })
        
        print()
    
    # Save retry report
    retry_report = {
        'retry_date': datetime.now().isoformat(),
        'summary': {
            'total_retried': len(failed_files),
            'successful_retries': len(successful_retries),
            'failed_retries': len(failed_retries),
            'success_rate': f"{(len(successful_retries) / len(failed_files) * 100):.1f}%"
        },
        'successful_retries': successful_retries,
        'failed_retries': failed_retries
    }
    
    report_path = "master_upsc_processing/Books/NCERT_Books/processed_json/retry_report.json"
    with open(report_path, 'w') as f:
        json.dump(retry_report, f, indent=2)
    
    print("=" * 50)
    print("🎉 RETRY PROCESSING COMPLETE")
    print("=" * 50)
    print(f"📊 Total Retried: {len(failed_files)}")
    print(f"✅ Successful Retries: {len(successful_retries)}")
    print(f"❌ Failed Retries: {len(failed_retries)}")
    print(f"📈 Success Rate: {retry_report['summary']['success_rate']}")
    print(f"📋 Report saved to: {report_path}")
    print("=" * 50)

if __name__ == "__main__":
    retry_failed_processing() 