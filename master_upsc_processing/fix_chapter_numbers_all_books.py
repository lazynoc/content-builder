import json
import re
from pathlib import Path

# Books to skip (already fixed today)
skip_books = {
    "political_class_11_book_political_theory_complete_book.json",
    "political_class_12_book_contemporary_world_politics_complete_book.json",
    "political_class_12_book_politics_in_India_since_independence_complete_book.json",
    "fine_arts_class_11_book_an_introduction_to_indian_art_part_1_complete_book.json"
}

# Only process economics and sociology books
ECON_SUBJECTS = ("economic", "sociology")

def extract_chapter_number(chapter_name):
    match = re.search(r"Chapter\s*(\d+)", chapter_name or "", re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

processed_dir = Path("master_upsc_processing/Books/NCERT_Books/processed_json")
for book_file in processed_dir.glob("*_complete_book.json"):
    print(f"🔧 Fixing {book_file.name}")
    with open(book_file, 'r') as f:
        book = json.load(f)
    pages = book.get('pages', [])
    chapters = book.get('chapters', [])
    # Update book_type in all pages
    for page in pages:
        page['book_type'] = 'UPSC-NCERT-2025-26'
    # Update book_type at book level if present
    if 'book_type' in book:
        book['book_type'] = 'UPSC-NCERT-2025-26'
    if 'book_info' in book and 'book_type' in book['book_info']:
        book['book_info']['book_type'] = 'UPSC-NCERT-2025-26'
    # Identify glossary chapter and pages
    glossary_chapter = None
    glossary_pages = []
    for chapter in chapters:
        if 'glossary' in chapter.get('filename', '').lower():
            glossary_chapter = chapter
            break
    if glossary_chapter:
        # Remove glossary from chapters
        chapters = [ch for ch in chapters if ch != glossary_chapter]
    # Find glossary pages
    for page in pages:
        if 'glossary' in page.get('metadata', {}).get('file_id', '').lower() or 'glossary' in page.get('chapter_name', '').lower():
            glossary_pages.append(page)
    if glossary_pages:
        # Remove glossary pages from main list
        pages = [p for p in pages if p not in glossary_pages]
    # Fix chapter_number in pages and metadata
    for page in pages:
        ch_name = page.get('chapter_name')
        ch_num = extract_chapter_number(ch_name)
        if ch_num is not None:
            page['chapter_number'] = ch_num
            if 'metadata' in page and isinstance(page['metadata'], dict):
                page['metadata']['chapter_number'] = ch_num
    # Fix chapter_number in chapters list
    for chapter in chapters:
        match = re.search(r"chapter_(\d+)", chapter.get('filename', ''), re.IGNORECASE)
        if match:
            chapter['chapter_number'] = int(match.group(1))
        else:
            # Fallback: find first page for this chapter and use its chapter_number
            for page in pages:
                if page.get('chapter_name') and chapter.get('filename', '').replace('.pdf','') in page.get('metadata', {}).get('file_id', ''):
                    chapter['chapter_number'] = page['chapter_number']
                    break
    # If glossary exists, append it at the end
    if glossary_chapter and glossary_pages:
        # Set chapter_name and chapter_number for glossary
        for page in glossary_pages:
            page['chapter_name'] = 'Glossary'
            page['chapter_number'] = 'Glossary'
            if 'metadata' in page and isinstance(page['metadata'], dict):
                page['metadata']['chapter_name'] = 'Glossary'
                page['metadata']['chapter_number'] = 'Glossary'
        glossary_chapter['chapter_name'] = 'Glossary'
        glossary_chapter['chapter_number'] = 'Glossary'
        chapters.append(glossary_chapter)
        pages.extend(glossary_pages)
    # Sort chapters and pages
    def chapter_sort_key(c):
        if c.get('chapter_number') == 'Glossary':
            return 9999
        return c.get('chapter_number', 0)
    def page_sort_key(p):
        if p.get('chapter_number') == 'Glossary':
            return 9999
        return p.get('page_number', 0)
    chapters = sorted(chapters, key=chapter_sort_key)
    pages = sorted(pages, key=page_sort_key)
    # Re-number pages to be continuous
    for i, page in enumerate(pages, 1):
        page['page_number'] = i
        if 'metadata' in page and isinstance(page['metadata'], dict):
            page['metadata']['page_number'] = i
    # Overwrite file
    book['chapters'] = chapters
    book['pages'] = pages
    with open(book_file, 'w') as f:
        json.dump(book, f, indent=2, ensure_ascii=False)
    print(f"✅ Fixed: {book_file.name}") 