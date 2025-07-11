#!/usr/bin/env python3
"""
Extract final 4 missing questions from 2022 GS Prelims
Questions 26-28: pages 29-31
Question 48: page 46
"""

import fitz  # PyMuPDF
import re
import json
from datetime import datetime
import uuid

def extract_text_from_pdf(pdf_path, start_page, end_page):
    """Extract text from specific pages of PDF"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        
        for page_num in range(start_page - 1, min(end_page, len(doc))):
            page = doc.load_page(page_num)
            text += page.get_text()
        
        doc.close()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def extract_questions_from_text(text, target_questions, start_page, end_page):
    """Extract specific questions from text"""
    questions = []
    
    # Split text into lines
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        # Look for question patterns
        for question_num in target_questions:
            # Pattern for question numbers
            patterns = [
                rf'^{question_num}\.',
                rf'^{question_num}\)',
                rf'^{question_num}\s',
                rf'Q\.{question_num}',
                rf'Question {question_num}'
            ]
            
            for pattern in patterns:
                if re.search(pattern, line.strip(), re.IGNORECASE):
                    # Found question start, collect until next question or end
                    question_text = line.strip()
                    j = i + 1
                    
                    # Collect subsequent lines until we hit another question or options
                    while j < len(lines):
                        next_line = lines[j].strip()
                        
                        # Stop if we hit another question number
                        if re.match(r'^\d+[\.\)]', next_line):
                            break
                        
                        # Stop if we hit options (A, B, C, D)
                        if re.match(r'^[A-D][\.\)]', next_line):
                            break
                        
                        # Add line to question if not empty
                        if next_line:
                            question_text += " " + next_line
                        
                        j += 1
                    
                    # Extract options
                    options = {}
                    option_patterns = {
                        'A': r'^A[\.\)]\s*(.+)',
                        'B': r'^B[\.\)]\s*(.+)', 
                        'C': r'^C[\.\)]\s*(.+)',
                        'D': r'^D[\.\)]\s*(.+)'
                    }
                    
                    # Look for options in the text after the question
                    for k in range(j, min(j + 20, len(lines))):  # Look ahead 20 lines
                        option_line = lines[k].strip()
                        for opt, pattern in option_patterns.items():
                            match = re.match(pattern, option_line, re.IGNORECASE)
                            if match and opt not in options:
                                options[opt] = match.group(1).strip()
                    
                    # Create question object
                    question_obj = {
                        "id": str(uuid.uuid4()),
                        "question_number": question_num,
                        "question_text": question_text,
                        "options": options,
                        "extraction_method": "final_4_missing_2022",
                        "extraction_date": datetime.now().isoformat(),
                        "source_pdf": "GS Prelims 2022.pdf",
                        "page_range": f"{start_page}-{end_page}"
                    }
                    
                    questions.append(question_obj)
                    print(f"✅ Extracted Q{question_num}")
                    break
    
    return questions

def main():
    pdf_path = "../PYQP With Answer/GS Prelims 2022.pdf"
    
    print("🔍 EXTRACTING FINAL 4 MISSING 2022 QUESTIONS")
    print("=" * 50)
    
    all_questions = []
    
    # Extract questions 26-28 from pages 29-31
    print(f"\n📄 Extracting Q26-28 from pages 29-31")
    text_26_28 = extract_text_from_pdf(pdf_path, 29, 31)
    if text_26_28:
        questions_26_28 = extract_questions_from_text(text_26_28, ['26', '27', '28'], 29, 31)
        all_questions.extend(questions_26_28)
        print(f"   Found {len(questions_26_28)} questions in pages 29-31")
    else:
        print(f"   ❌ Could not extract text from pages 29-31")
    
    # Extract question 48 from page 46
    print(f"\n📄 Extracting Q48 from page 46")
    text_48 = extract_text_from_pdf(pdf_path, 46, 46)
    if text_48:
        questions_48 = extract_questions_from_text(text_48, ['48'], 46, 46)
        all_questions.extend(questions_48)
        print(f"   Found {len(questions_48)} questions in page 46")
    else:
        print(f"   ❌ Could not extract text from page 46")
    
    print(f"\n{'='*50}")
    print(f"📊 EXTRACTION RESULTS:")
    print(f"   Total extracted: {len(all_questions)}")
    
    if all_questions:
        extracted_nums = [q['question_number'] for q in all_questions]
        print(f"   Extracted: {extracted_nums}")
        
        # Save to file
        output_data = {
            "metadata": {
                "pdf_name": "GS Prelims 2022.pdf",
                "extraction_date": datetime.now().isoformat(),
                "extraction_method": "final_4_missing_2022",
                "target_questions": ['26', '27', '28', '48'],
                "extracted_questions": extracted_nums,
                "page_ranges": {
                    "26-28": "29-31",
                    "48": "46"
                },
                "note": "Final 4 missing questions extraction for 2022"
            },
            "questions": all_questions
        }
        
        output_file = "GS Prelims 2022_FINAL_4_MISSING.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Saved to: {output_file}")
        
        # Show what's still missing
        target_questions = ['26', '27', '28', '48']
        still_missing = set(target_questions) - set(extracted_nums)
        if still_missing:
            print(f"   ❌ Still missing: {sorted(still_missing)}")
        else:
            print(f"   ✅ All 4 target questions extracted!")
    else:
        print(f"   ❌ No questions extracted")

if __name__ == "__main__":
    main() 