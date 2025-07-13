#!/usr/bin/env python3
"""
Quick Script to Process New UPSC PYQ Years
Usage: python3 process_new_year.py 2026
"""

import sys
import os
from openai_direct_processing import main as process_year

def update_configuration(year):
    """Update the configuration for the specified year"""
    script_path = os.path.join(os.path.dirname(__file__), 'openai_direct_processing.py')
    
    # Read the current script
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the configuration
    content = content.replace(
        "RAW_FILE = 'raw_questions_dump_pyq_2021.md'",
        f"RAW_FILE = 'markdown_files/raw_questions_dump_pyq_{year}.md'"
    )
    content = content.replace(
        "OUTPUT_FILE = 'upsc_prelims_2021_structured_for_frontend.json'",
        f"OUTPUT_FILE = 'json_files/upsc_prelims_{year}_structured_for_frontend.json'"
    )
    content = content.replace(
        "YEAR = 2021",
        f"YEAR = {year}"
    )
    
    # Write back the updated script
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Configuration updated for year {year}")

def check_files_exist(year):
    """Check if required files exist"""
    markdown_file = f"markdown_files/raw_questions_dump_pyq_{year}.md"
    
    if not os.path.exists(markdown_file):
        print(f"❌ Error: {markdown_file} not found!")
        print(f"Please create the markdown file first.")
        return False
    
    print(f"✅ Found {markdown_file}")
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 process_new_year.py <YEAR>")
        print("Example: python3 process_new_year.py 2026")
        sys.exit(1)
    
    year = sys.argv[1]
    
    try:
        year_int = int(year)
        if year_int < 2000 or year_int > 2030:
            raise ValueError("Year out of reasonable range")
    except ValueError:
        print("❌ Error: Please provide a valid year (e.g., 2026)")
        sys.exit(1)
    
    print(f"🚀 Processing UPSC PYQ for year {year}")
    print("=" * 50)
    
    # Check if files exist
    if not check_files_exist(year):
        sys.exit(1)
    
    # Update configuration
    update_configuration(year)
    
    # Change to the correct directory
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    
    # Run the processing
    print(f"🔄 Starting processing for {year}...")
    try:
        process_year()
        print(f"✅ Successfully processed {year}!")
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 