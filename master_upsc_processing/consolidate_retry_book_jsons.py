import json
import re
from pathlib import Path
from collections import defaultdict

def extract_chapter_number_from_name(chapter_name):
    match = re.search(r"Chapter\s*(\d+)", chapter_name, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def extract_chapter_number_from_filename(filename):
    match = re.search(r"chapter_(\d+)", filename, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def consolidate_book(book_key, output_name=None):
    retry_dir = Path("master_upsc_processing/Books/NCERT_Books/processed_json/retry_results/")
    # Find all retry files for this book
    def safe_chapter_sort_key(p):
        num = extract_chapter_number_from_filename(p.name)
        return num if num is not None else 0
    retry_files = sorted(retry_dir.glob(f"retry_{book_key}_chapter_*.json"), key=safe_chapter_sort_key)
    if not retry_files:
        print(f"❌ No retry files found for book: {book_key}")
        return
    all_pages = []
    chapters_meta = []
    page_counter = 1
    for retry_file in retry_files:
        with open(retry_file, 'r') as f:
            chapter_pages = json.load(f)
        if not chapter_pages:
            continue
        # Get chapter number from first page's chapter_name or filename
        ch_name = chapter_pages[0].get('chapter_name', '')
        ch_num = extract_chapter_number_from_name(ch_name)
        if ch_num is None:
            ch_num = extract_chapter_number_from_filename(retry_file.name)
        # Renumber pages and fix chapter_number in metadata
        for i, page in enumerate(chapter_pages):
            page['page_number'] = page_counter
            page['chapter_number'] = ch_num
            if 'metadata' in page and isinstance(page['metadata'], dict):
                page['metadata']['page_number'] = page_counter
                page['metadata']['chapter_number'] = ch_num
            page_counter += 1
        all_pages.extend(chapter_pages)
        chapters_meta.append({
            'chapter_number': ch_num,
            'filename': retry_file.name.replace('retry_', '').replace('.json', '.pdf'),
            'pages': len(chapter_pages)
        })
    # Sort chapters and pages
    chapters_meta = sorted(chapters_meta, key=lambda c: c['chapter_number'])
    all_pages = sorted(all_pages, key=lambda p: p['page_number'])
    # Book-level metadata
    book_info = {
        'book_key': book_key,
        'total_chapters': len(chapters_meta),
        'total_pages': len(all_pages),
        'page_range': f"{all_pages[0]['page_number']}-{all_pages[-1]['page_number']}",
        'processing_date': all_pages[0].get('created_at') if all_pages else None,
        'subject': all_pages[0].get('subject') if all_pages else None,
        'class': all_pages[0].get('class') if all_pages else None,
        'book_name': all_pages[0].get('book_name') if all_pages else None
    }
    book_json = {
        'book_info': book_info,
        'chapters': chapters_meta,
        'pages': all_pages
    }
    # Output path
    if not output_name:
        output_name = f"{book_key}_complete_book.json"
    output_path = retry_dir.parent / output_name
    with open(output_path, 'w') as f:
        json.dump(book_json, f, indent=2, ensure_ascii=False)
    print(f"✅ Consolidated book saved to: {output_path}")

if __name__ == "__main__":
    # Example usage for the two books you mentioned:
    consolidate_book("political_class_11_book_political_theory")
    consolidate_book("political_class_12_book_contemporary_world_politics")
    consolidate_book("political_class_12_book_politics_in_India_since_independence")
    consolidate_book("fine_arts_class_11_book_an_introduction_to_indian_art_part_1") 