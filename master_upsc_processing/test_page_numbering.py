#!/usr/bin/env python3
"""
Test Page Numbering Logic
=========================

This script demonstrates how page numbering works across chapters.
"""

def calculate_page_numbers():
    """Demonstrate page numbering logic for NCERT books."""
    
    print("📚 NCERT Book Page Numbering Logic")
    print("=" * 50)
    
    # Example: Geography Class 9 - contemporary India I
    book_name = "contemporary India I"
    estimated_pages_per_chapter = 20
    
    print(f"📖 Book: {book_name}")
    print(f"📄 Estimated pages per chapter: {estimated_pages_per_chapter}")
    print()
    
    # Show page numbering for multiple chapters
    chapters = [1, 2, 3, 4, 5]
    
    for chapter_num in chapters:
        # Calculate starting page for this chapter
        chapter_start_page = (chapter_num - 1) * estimated_pages_per_chapter + 1
        chapter_end_page = chapter_num * estimated_pages_per_chapter
        
        print(f"📑 Chapter {chapter_num}:")
        print(f"   Start Page: {chapter_start_page}")
        print(f"   End Page: {chapter_end_page}")
        print(f"   Page Range: {chapter_start_page}-{chapter_end_page}")
        print()
    
    print("✅ This ensures continuous page numbering across the entire book!")
    print("   Each chapter's pages continue from where the previous chapter ended.")

if __name__ == "__main__":
    calculate_page_numbers() 