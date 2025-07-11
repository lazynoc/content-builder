#!/usr/bin/env python3
"""
Import 2024 UPSC questions into pyq_question_table
"""

import os
import sys
from import_2024_pyq_table import PyqTableImport

def main():
    """Run the import process for pyq_question_table"""
    
    # Check if we're in the right directory
    if not os.path.exists('GS Prelims 2024_WITH_OPENAI_ANALYSIS.json'):
        print("❌ Error: GS Prelims 2024_WITH_OPENAI_ANALYSIS.json not found in current directory")
        print("   Please run this script from the pyq_processing_pipeline directory")
        return 1
    
    # Check environment variables
    if not os.getenv('SUPABASE_DB_URL'):
        print("❌ Please set SUPABASE_DB_URL environment variable")
        print("   Format: postgresql://username:password@host:port/database")
        return 1
    
    importer = None
    try:
        print("🚀 Starting 2024 UPSC Questions Import (pyq_question_table)...")
        print("=" * 60)
        
        # Initialize importer
        importer = PyqTableImport()
        
        # Check existing questions
        existing_count = importer.check_existing_questions()
        
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing questions for 2024")
            print("   The script will update existing questions and add new ones.")
        
        # Import 2024 questions
        print("\n📥 Importing 2024 questions...")
        importer.import_2024_questions('GS Prelims 2024_WITH_OPENAI_ANALYSIS.json')
        
        # Verify import
        print("\n🔍 Verifying import...")
        importer.verify_import()
        
        print("\n" + "=" * 60)
        print("🎉 Import completed successfully!")
        print("   Your 2024 UPSC GS Prelims questions are now in pyq_question_table.")
        print("   You can use this data for your mock test application.")
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        print("   Please check your database connection and try again.")
        return 1
    
    finally:
        if importer:
            importer.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 