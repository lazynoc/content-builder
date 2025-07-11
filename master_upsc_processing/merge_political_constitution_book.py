import json
import os
from pathlib import Path

# Paths
original_path = Path("master_upsc_processing/Books/NCERT_Books/processed_json/political_11_indian_constitution_at_work_complete_book.json")
retry_dir = Path("master_upsc_processing/Books/NCERT_Books/processed_json/retry_results/")
output_path = Path("master_upsc_processing/Books/NCERT_Books/processed_json/political_11_indian_constitution_at_work_complete_book_merged.json")

# Chapters to add (as per your info)
new_chapters = [8, 9, 10]

# Helper to get retry file for a chapter
def get_retry_file(chapter_num):
    return retry_dir / f"retry_political_class_11_book_indian_constitution_at_work_chapter_{chapter_num}.json"

# Load original book
with open(original_path, 'r') as f:
    book = json.load(f)

# Extract existing pages and chapters
pages = book['pages']
chapters = book['chapters']

# Find last page number in original (end of chapter 7)
if pages:
    last_page_number = max(p['page_number'] for p in pages)
else:
    last_page_number = 0

# Merge new chapters
for chapter_num in new_chapters:
    retry_file = get_retry_file(chapter_num)
    if not retry_file.exists():
        print(f"❌ Retry file not found for chapter {chapter_num}: {retry_file}")
        continue
    with open(retry_file, 'r') as f:
        chapter_pages = json.load(f)
    # Renumber pages
    for i, page in enumerate(chapter_pages):
        page['page_number'] = last_page_number + i + 1
        if 'metadata' in page:
            page['metadata']['page_number'] = page['page_number']
        page['chapter_number'] = chapter_num
    # Add to pages
    pages.extend(chapter_pages)
    # Add to chapters metadata
    chapters.append({
        'chapter_number': chapter_num,
        'filename': f'political_class_11_book_indian_constitution_at_work_chapter_{chapter_num}.pdf',
        'pages': len(chapter_pages)
    })
    last_page_number += len(chapter_pages)
    print(f"✅ Added chapter {chapter_num} ({len(chapter_pages)} pages, now up to page {last_page_number})")

# Sort chapters and pages by chapter/page number
chapters = sorted(chapters, key=lambda c: c['chapter_number'])
pages = sorted(pages, key=lambda p: p['page_number'])

# Update book-level metadata
book['chapters'] = chapters
book['pages'] = pages
book['book_info']['total_chapters'] = len(chapters)
book['book_info']['total_pages'] = len(pages)
book['book_info']['page_range'] = f"{pages[0]['page_number']}-{pages[-1]['page_number']}"

# Save merged book
with open(output_path, 'w') as f:
    json.dump(book, f, indent=2, ensure_ascii=False)

print(f"\n🎉 Merged book saved to: {output_path}") 