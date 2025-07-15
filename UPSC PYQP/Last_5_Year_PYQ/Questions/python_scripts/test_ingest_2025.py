#!/usr/bin/env python3
"""
Test script to ingest only 2025 UPSC questions
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_ingest import SupabaseIngester

def main():
    """Test ingestion for 2025 only"""
    print("🧪 Testing 2025 UPSC questions ingestion")
    print("=" * 50)
    
    ingester = SupabaseIngester()
    
    # Test with just 2025
    success = ingester.ingest_all_years([2025])
    
    if success:
        print("\n✅ 2025 ingestion completed successfully!")
        
        # Verify the data
        print("\n🔍 Verifying ingested data...")
        ingester.verify_ingestion()
    else:
        print("\n❌ 2025 ingestion had issues. Check the logs above.")

if __name__ == "__main__":
    main() 