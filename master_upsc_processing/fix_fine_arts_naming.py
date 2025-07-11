#!/usr/bin/env python3
"""
Fix Fine Arts Book Naming Pattern
=================================

This script fixes the Fine Arts book naming pattern to be consistent with other subjects.
Changes 'book_name' to 'book' in filenames.
"""

import os
import re
from pathlib import Path

def fix_fine_arts_naming():
    """Fix Fine Arts book naming pattern."""
    ncert_dir = Path("Books/NCERT_Books")
    
    if not ncert_dir.exists():
        print("❌ NCERT_Books directory not found")
        return
    
    print("🔧 Fixing Fine Arts Book Naming Pattern")
    print("=" * 50)
    
    # Find all Fine Arts files with 'book_name' pattern
    fine_arts_files = list(ncert_dir.glob("fine_*book_name_*.pdf"))
    print(f"📁 Found {len(fine_arts_files)} Fine Arts files to fix")
    
    renamed_count = 0
    
    for pdf_file in fine_arts_files:
        original_name = pdf_file.name
        
        # Replace 'book_name' with 'book'
        new_name = original_name.replace('book_name_', 'book_')
        
        if original_name != new_name:
            new_path = pdf_file.parent / new_name
            
            # Check if target file already exists
            if new_path.exists():
                print(f"⚠️  Skipping {original_name} - target already exists")
                continue
            
            try:
                pdf_file.rename(new_path)
                print(f"✅ {original_name} → {new_name}")
                renamed_count += 1
            except Exception as e:
                print(f"❌ Error renaming {original_name}: {e}")
        else:
            print(f"ℹ️  {original_name} (already fixed)")
    
    print(f"\n🎉 Fine Arts Naming Fix Complete!")
    print(f"📊 Files renamed: {renamed_count}")

if __name__ == "__main__":
    fix_fine_arts_naming() 