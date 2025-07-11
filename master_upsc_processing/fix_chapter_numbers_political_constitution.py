import json
import re
from pathlib import Path

input_path = Path("master_upsc_processing/Books/NCERT_Books/processed_json/political_11_indian_constitution_at_work_complete_book_merged.json")
output_path = Path("master_upsc_processing/Books/NCERT_Books/processed_json/political_11_indian_constitution_at_work_complete_book_chapterfix.json")

def extract_chapter_number(chapter_name):
    match = re.search(r"Chapter\s*(\d+)", chapter_name, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

# Load merged book
with open(input_path, 'r') as f:
    book = json.load(f)

pages = book['pages']

# Fix chapter_number in pages and metadata
for page in pages:
    ch_name = page.get('chapter_name')
    ch_num = extract_chapter_number(ch_name) if ch_name else None
    if ch_num is not None:
        page['chapter_number'] = ch_num
        if 'metadata' in page and isinstance(page['metadata'], dict):
            page['metadata']['chapter_number'] = ch_num

# Fix chapter_number in chapters list
for chapter in book['chapters']:
    # Try to extract from filename if possible
    match = re.search(r"chapter_(\d+)", chapter.get('filename', ''), re.IGNORECASE)
    if match:
        chapter['chapter_number'] = int(match.group(1))
    else:
        # Fallback: find first page for this chapter and use its chapter_number
        for page in pages:
            if page.get('chapter_name') and chapter.get('filename', '').replace('.pdf','') in page.get('metadata', {}).get('file_id', ''):
                chapter['chapter_number'] = page['chapter_number']
                break

# Sort chapters and pages by chapter_number/page_number
book['chapters'] = sorted(book['chapters'], key=lambda c: c['chapter_number'])
book['pages'] = sorted(book['pages'], key=lambda p: p['page_number'])

# Save fixed book
with open(output_path, 'w') as f:
    json.dump(book, f, indent=2, ensure_ascii=False)

print(f"✅ Chapter numbers fixed and saved to: {output_path}") 