import os
import sys
import json
import uuid
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import argparse

# Load environment variables from .env file
load_dotenv()

# Import the OCR extractor from the main pipeline (reuse logic)
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / 'master_upsc_processing' / 'pipeline_components'))
from mistralai import Mistral

MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

# --- TABLE SCHEMA ---
class PYQTableRow:
    def __init__(self, qn=None, section=None, question=None, answer=None, explanation=None, motivation=None, level=None, nature=None, source=None, source_type=None, reference=None):
        self.qn = qn
        self.section = section
        self.question = question
        self.answer = answer
        self.explanation = explanation
        self.motivation = motivation
        self.level = level
        self.nature = nature
        self.source = source
        self.source_type = source_type
        self.reference = reference
    def to_dict(self):
        return self.__dict__

def parse_markdown_table(markdown_text: str) -> List[Dict[str, str]]:
    rows = []
    lines = markdown_text.strip().split('\n')
    table_start = -1
    for i, line in enumerate(lines):
        if '|' in line and 'QN' in line and 'Section' in line:
            table_start = i
            break
    if table_start == -1:
        return rows
    table_lines = lines[table_start:]
    headers = [
        'QN', 'Section', 'Questions', 'Answer', 'Explanation',
        'Motivation / Current Affairs', 'Level', 'Nature', 'Source',
        'Source Type', 'VisionIAS Test Series/Sandhan/PT 365/Open Test/Abhyaas'
    ]
    separator_index = -1
    for i, line in enumerate(table_lines):
        if '---' in line and '|' in line:
            separator_index = i
            break
    if separator_index == -1:
        return rows
    for i, line in enumerate(table_lines[separator_index + 1:], separator_index + 1):
        line = line.strip()
        if line.startswith('|') and line.endswith('|'):
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(cells) == len(headers):
                row_dict = dict(zip(headers, cells))
                rows.append(row_dict)
    return rows

def merge_pyq_rows(rows: List[Dict[str, str]]) -> List[PYQTableRow]:
    merged_questions = []
    current_question = None
    for row in rows:
        if all(value.strip() in ['---', ''] for value in row.values()):
            continue
        if row.get('QN') and row['QN'].strip() and row['QN'].strip() != '---':
            if current_question:
                merged_questions.append(current_question)
            current_question = PYQTableRow(
                qn=row.get('QN', '').strip(),
                section=row.get('Section', '').strip(),
                question=row.get('Questions', '').strip(),
                answer=row.get('Answer', '').strip(),
                explanation=row.get('Explanation', '').strip(),
                motivation=row.get('Motivation / Current Affairs', '').strip(),
                level=row.get('Level', '').strip(),
                nature=row.get('Nature', '').strip(),
                source=row.get('Source', '').strip(),
                source_type=row.get('Source Type', '').strip(),
                reference=row.get('VisionIAS Test Series/Sandhan/PT 365/Open Test/Abhyaas', '').strip()
            )
        else:
            if current_question:
                for field in ['question', 'explanation', 'motivation', 'source', 'reference']:
                    current_value = getattr(current_question, field) or ""
                    new_value = row.get(field.replace('_', ' ').title(), '').strip()
                    if new_value and new_value != '---':
                        setattr(current_question, field, f"{current_value} {new_value}".strip())
    if current_question:
        merged_questions.append(current_question)
    return merged_questions

def extract_missing_question(pdf_path: str, start_page: int, end_page: int, question_number: str, output: str):
    import base64
    if not MISTRAL_API_KEY:
        print("❌ MISTRAL_API_KEY not found in environment variables")
        return
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    print(f"🔍 Extracting Question {question_number} from pages {start_page}-{end_page}...")
    with open(pdf_path, "rb") as pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    client = Mistral(api_key=MISTRAL_API_KEY)
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_pdf}"
        },
        include_image_base64=False
    )
    # Extract markdown from specified pages (0-indexed)
    page_texts = []
    for i in range(start_page-1, end_page):
        if i < len(ocr_response.pages):
            page_text = ocr_response.pages[i].markdown
            page_texts.append(f"--- PAGE {i+1} ---\n{page_text}")
    combined_text = "\n\n".join(page_texts)
    # Save raw text for debugging
    with open(f"Question_{question_number}_raw_text.txt", "w", encoding="utf-8") as f:
        f.write(combined_text)
    # Parse markdown table
    table_rows = parse_markdown_table(combined_text)
    merged_questions = merge_pyq_rows(table_rows)
    # Find the specific question
    found = None
    for q in merged_questions:
        if q.qn == str(question_number):
            found = q
            break
    if found:
        result = found.to_dict()
        result['id'] = str(uuid.uuid4())
        result['extraction_method'] = f"chunked_ocr_pages_{start_page}_{end_page}"
        result['source_pages'] = f"{start_page}-{end_page}"
        result['extraction_timestamp'] = datetime.now().isoformat()
        result['source_file'] = pdf_path
        with open(output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"✅ Question {question_number} extracted and saved to {output}")
    else:
        print(f"❌ Question {question_number} not found in the specified pages.")

def main():
    parser = argparse.ArgumentParser(description="Extract a specific missing question from a PDF using OCR and markdown table parsing.")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--start-page", type=int, required=True, help="Start page (1-indexed)")
    parser.add_argument("--end-page", type=int, required=True, help="End page (1-indexed, inclusive)")
    parser.add_argument("--question-number", type=str, required=True, help="Question number to extract")
    parser.add_argument("--output", type=str, default=None, help="Output JSON file path")
    args = parser.parse_args()
    output = args.output or f"Question_{args.question_number}_extracted.json"
    extract_missing_question(args.pdf_path, args.start_page, args.end_page, args.question_number, output)

if __name__ == "__main__":
    main() 