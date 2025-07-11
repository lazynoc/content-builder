#!/usr/bin/env python3
"""
Simple script to import 2024 UPSC GS Prelims questions into Supabase
"""

import os
import sys
from import_2024_simple import SimpleSupabaseImport

def main():
    """Run the import process"""
    
    # Check if we're in the right directory
    if not os.path.exists('GS Prelims 2024_WITH_OPENAI_ANALYSIS.json'):
        print("❌ Error: GS Prelims 2024_WITH_OPENAI_ANALYSIS.json not found in current directory")
        print("   Please run this script from the pyq_processing_pipeline directory")
        return
    
    # Check environment variables
    if not os.getenv('SUPABASE_DB_URL'):
        print("❌ Please set SUPABASE_DB_URL environment variable")
        print("   Format: postgresql://username:password@host:port/database")
        return
    
    importer = None
    try:
        print("🚀 Starting 2024 UPSC Questions Import Process...")
        print("=" * 60)
        
        # Initialize importer
        importer = SimpleSupabaseImport()
        
        # Step 1: Create schema
        print("\n🔧 Step 1: Setting up database schema...")
        importer.create_schema()
        
        # Step 2: Import 2024 questions
        print("\n📥 Step 2: Importing 2024 questions...")
        importer.import_2024_questions('GS Prelims 2024_WITH_OPENAI_ANALYSIS.json')
        
        # Step 3: Verify import
        print("\n🔍 Step 3: Verifying import...")
        importer.verify_import()
        
        print("\n" + "=" * 60)
        print("🎉 Import completed successfully!")
        print("   Your 2024 UPSC GS Prelims questions are now in Supabase.")
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