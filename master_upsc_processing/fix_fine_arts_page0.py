import json
from pathlib import Path

input_path = Path("master_upsc_processing/Books/NCERT_Books/processed_json/fine_arts_class_11_book_an_introduction_to_indian_art_part_1_complete_book.json")

# Load the book
with open(input_path, 'r') as f:
    book = json.load(f)

pages = book['pages']

if not pages:
    print("❌ No pages found!")
    exit(1)

# Set first page to 0
pages[0]['page_number'] = 0
if 'metadata' in pages[0] and isinstance(pages[0]['metadata'], dict):
    pages[0]['metadata']['page_number'] = 0

# Renumber all subsequent pages starting from 1
for i, page in enumerate(pages[1:], start=1):
    page['page_number'] = i
    if 'metadata' in page and isinstance(page['metadata'], dict):
        page['metadata']['page_number'] = i

# Update book_info and page_range
book['pages'] = pages
book['book_info']['total_pages'] = len(pages)
book['book_info']['page_range'] = f"0-{len(pages)-1}"

# Save (overwrite original)
with open(input_path, 'w') as f:
    json.dump(book, f, indent=2, ensure_ascii=False)

print(f"✅ Fine Arts book updated: first page is 0, rest renumbered, saved to {input_path}") 