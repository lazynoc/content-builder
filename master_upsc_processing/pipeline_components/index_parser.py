#!/usr/bin/env python3
"""
Index Parser for UPSC Books
Extracts chapter names and page ranges from OCR'd index files
"""

import json
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class ChapterInfo:
    chapter_number: int
    chapter_name: str
    start_page: int
    end_page: int
    part: str

def parse_index_json(json_file_path: str) -> List[ChapterInfo]:
    """
    Parse the index JSON file and extract chapter information
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chapters = []
    current_part = "Environmental Ecology"  # Default part
    
    # Extract all content from pages
    full_content = ""
    for page in data['pages']:
        full_content += page['content'] + "\n"
    
    # Parse parts and chapters
    lines = full_content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Detect parts
        if 'PART-I' in line and 'ENVIRONMENTAL ECOLOGY' in line:
            current_part = "Environmental Ecology"
        elif 'PART-II' in line and 'BIODIVERSITY' in line:
            current_part = "Biodiversity"
        elif 'PART-III' in line and 'CLIMATE CHANGE' in line:
            current_part = "Climate Change"
        elif 'PART-IV' in line and 'AGRICULTURE' in line:
            current_part = "Agriculture"
        elif 'PART-V' in line:
            current_part = "Acts and Policies"

        # Special case for chapter 29: $34{ }^{1-346}$ means 341-346
        special_29 = re.search(r'29\.\s+ENVIRONMENT ISSUES AND HEALTH EFFECTS\s*\.+\s*\$34\{ \}\^\{1-346\}\$', line)
        if special_29:
            chapter_num = 29
            chapter_name = "ENVIRONMENT ISSUES AND HEALTH EFFECTS"
            start_page = 341
            end_page = 346
            if not any(c.chapter_number == chapter_num for c in chapters):
                chapters.append(ChapterInfo(
                    chapter_number=chapter_num,
                    chapter_name=chapter_name,
                    start_page=start_page,
                    end_page=end_page,
                    part=current_part
                ))
            continue

        # Parse chapter entries with more flexible patterns
        chapter_patterns = [
            r'(\d+)\.\s+([^\.]+?)\s*\.+\s*(\d+)-(\d+)',
            r'(\d+)\.\s+([^\.]+?)\s*\.+\s*\$(\d+)-(\d+)\$'
        ]
        for i, pattern in enumerate(chapter_patterns):
            match = re.search(pattern, line)
            if match:
                chapter_num = int(match.group(1))
                chapter_name = match.group(2).strip()
                start_page = int(match.group(3))
                end_page = int(match.group(4))
                chapter_name = re.sub(r'\s+', ' ', chapter_name).strip()
                if not any(c.chapter_number == chapter_num for c in chapters):
                    chapters.append(ChapterInfo(
                        chapter_number=chapter_num,
                        chapter_name=chapter_name,
                        start_page=start_page,
                        end_page=end_page,
                        part=current_part
                    ))
                break
    
    # Sort by chapter number
    chapters.sort(key=lambda x: x.chapter_number)

    # Special handling for first chapter: start from page 1 instead of the index start page
    if chapters:
        chapters[0].start_page = 1
    
    # Update end_page: for each chapter, set end_page to the page before the next chapter's start_page
    for i in range(len(chapters) - 1):
        chapters[i].end_page = chapters[i+1].start_page - 1
    # The last chapter keeps its original end_page
    
    return chapters

def print_chapter_summary(chapters: List[ChapterInfo]):
    """
    Print a summary of extracted chapters
    """
    print("=" * 80)
    print("CHAPTER INDEX EXTRACTION RESULTS")
    print("=" * 80)
    
    current_part = None
    for chapter in chapters:
        if chapter.part != current_part:
            current_part = chapter.part
            print(f"\n📚 {current_part.upper()}")
            print("-" * 50)
        
        print(f"{chapter.chapter_number:2d}. {chapter.chapter_name}")
        print(f"    Pages: {chapter.start_page}-{chapter.end_page}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total Chapters: {len(chapters)}")
    print(f"   Parts: {len(set(c.part for c in chapters))}")
    print(f"   Page Range: {min(c.start_page for c in chapters)}-{max(c.end_page for c in chapters)}")

def save_chapter_list(chapters: List[ChapterInfo], output_file: str):
    """
    Save chapter list to JSON file
    """
    chapter_data = []
    for chapter in chapters:
        chapter_data.append({
            'chapter_number': chapter.chapter_number,
            'chapter_name': chapter.chapter_name,
            'start_page': chapter.start_page,
            'end_page': chapter.end_page,
            'part': chapter.part,
            'page_count': chapter.end_page - chapter.start_page + 1
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'book_name': 'Environment by Shankar IAS Academy',
            'total_chapters': len(chapters),
            'chapters': chapter_data
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Chapter list saved to: {output_file}")

if __name__ == "__main__":
    # Parse the index file
    index_file = "Books/Environment_Book_Chapters/proper_chapters/Environment by Shankar IAS Academy (UpscStdEbooks) Indexed_consolidated.json"
    chapters = parse_index_json(index_file)
    
    # Print summary
    print_chapter_summary(chapters)
    
    # Save to file
    save_chapter_list(chapters, "Books/Environment_Book_Chapters/proper_chapters/chapter_index.json") 