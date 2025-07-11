import os
import sys
import json
import uuid
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the OCR extractor from the main pipeline (reuse logic)
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / 'master_upsc_processing' / 'pipeline_components'))
from mistralai import Mistral
from pydantic import BaseModel, Field

# --- CONFIG ---
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
OUTPUT_DIR = Path(__file__).parent

# --- TABLE SCHEMA ---
class PYQTableRow(BaseModel):
    qn: Optional[str] = Field(None, description="Question number")
    section: Optional[str] = Field(None, description="Section of the question")
    question: Optional[str] = Field(None, description="Question text")
    answer: Optional[str] = Field(None, description="Correct answer")
    explanation: Optional[str] = Field(None, description="Detailed explanation")
    motivation: Optional[str] = Field(None, description="Motivation or current affairs context")
    level: Optional[str] = Field(None, description="Difficulty level")
    nature: Optional[str] = Field(None, description="Nature of question")
    source: Optional[str] = Field(None, description="Source material")
    source_type: Optional[str] = Field(None, description="Type of source")
    reference: Optional[str] = Field(None, description="Reference or extra information")

def parse_markdown_table(markdown_text: str) -> List[Dict[str, str]]:
    """Parse markdown table and return list of dictionaries."""
    rows = []
    lines = markdown_text.strip().split('\n')
    
    # Find the start of the table (line with | QN |)
    table_start = -1
    for i, line in enumerate(lines):
        if '|' in line and 'QN' in line and 'Section' in line:
            table_start = i
            break
    
    if table_start == -1:
        print("No table found in markdown content")
        return rows
    
    # Get table lines starting from the header
    table_lines = lines[table_start:]
    
    # Parse header (first line and potentially more lines)
    header_lines = []
    i = 0
    while i < len(table_lines) and '|' in table_lines[i]:
        header_lines.append(table_lines[i])
        i += 1
        # Stop if we hit the separator line
        if i < len(table_lines) and '---' in table_lines[i]:
            break
    
    # Combine header lines to get the full header
    full_header = ' '.join(header_lines)
    print(f"Full header: {full_header}")
    
    # Manually define the expected headers based on the table structure
    # This is more reliable than parsing the OCR output
    headers = [
        'QN',
        'Section', 
        'Questions',
        'Answer',
        'Explanation',
        'Motivation / Current Affairs',
        'Level',
        'Nature',
        'Source',
        'Source Type',
        'VisionIAS Test Series/Sandhan/PT 365/Open Test/Abhyaas'
    ]
    
    print(f"Using predefined headers: {headers}")
    print(f"Number of headers: {len(headers)}")
    
    # Find separator line (line with ---)
    separator_index = -1
    for i, line in enumerate(table_lines):
        if '---' in line and '|' in line:
            separator_index = i
            break
    
    if separator_index == -1:
        print("No separator line found")
        return rows
    
    print(f"Separator found at line {separator_index}")
    
    # Process data rows (everything after separator)
    current_row = {}
    current_cell = ""
    cell_index = 0
    
    for i, line in enumerate(table_lines[separator_index + 1:], separator_index + 1):
        line = line.strip()
        
        if line.startswith('|') and line.endswith('|'):
            # This is a complete table row
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            print(f"Row {len(rows)+1}: {len(cells)} cells, headers: {len(headers)}")
            if len(cells) == len(headers):
                row_dict = dict(zip(headers, cells))
                rows.append(row_dict)
        elif line.startswith('|'):
            # This might be a continuation of a table row
            # For now, let's just look for complete rows
            pass
    
    return rows

def merge_pyq_rows(rows: List[Dict[str, str]]) -> List[PYQTableRow]:
    """Merge multi-page questions by combining rows with missing QN."""
    merged_questions = []
    current_question = None
    
    for row in rows:
        # Skip separator rows (all values are "---" or empty)
        if all(value.strip() in ['---', ''] for value in row.values()):
            continue
            
        # Check if this is a new question (has QN)
        if row.get('QN') and row['QN'].strip() and row['QN'].strip() != '---':
            # Save previous question if exists
            if current_question:
                merged_questions.append(current_question)
            
            # Start new question
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
            # This is a continuation of the previous question
            if current_question:
                # Merge fields (append to existing content)
                for field in ['question', 'explanation', 'motivation', 'source', 'reference']:
                    current_value = getattr(current_question, field) or ""
                    new_value = row.get(field.replace('_', ' ').title(), '').strip()
                    if new_value and new_value != '---':
                        setattr(current_question, field, f"{current_value} {new_value}".strip())
    
    # Add the last question
    if current_question:
        merged_questions.append(current_question)
    
    return merged_questions

def extract_pyq_questions(pdf_path: str) -> List[PYQTableRow]:
    """Extract PYQ questions from PDF using Mistral OCR and markdown table parsing."""
    import base64
    
    print(f"Extracting tables from {pdf_path} using markdown table parsing...")
    
    # Encode PDF to base64
    with open(pdf_path, "rb") as pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    
    # Initialize Mistral client
    client = Mistral(api_key=MISTRAL_API_KEY)
    
    # Process PDF with OCR
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_pdf}"
        },
        include_image_base64=False
    )
    
    # Collect all markdown content from pages 3 onwards (where table starts)
    all_markdown = ""
    for page in ocr_response.pages[2:]:  # Skip first 2 pages
        all_markdown += page.markdown + "\n"
    
    # DEBUG: Print raw markdown content
    print(f"\n--- RAW MARKDOWN CONTENT (first 500 chars) ---")
    print(all_markdown[:500])
    print("---")
    
    # Parse markdown table
    table_rows = parse_markdown_table(all_markdown)
    
    # DEBUG: Print what was parsed
    print(f"\n--- PARSED TABLE ROWS ({len(table_rows)} rows) ---")
    for i, row in enumerate(table_rows[:3]):  # Show first 3 rows
        print(f"Row {i+1}: {row}")
        print("---")
    
    # Merge multi-page questions
    merged_questions = merge_pyq_rows(table_rows)
    return merged_questions

def main():
    import argparse
    import base64
    
    parser = argparse.ArgumentParser(description="Extract PYQ questions from PDF")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    # Extract questions
    questions = extract_pyq_questions(args.pdf_path)
    
    # Prepare output
    output_data = {
        "metadata": {
            "pdf_name": Path(args.pdf_path).name,
            "extraction_date": datetime.now().isoformat(),
            "total_questions": len(questions)
        },
        "questions": []
    }
    
    # Add unique ID to each question
    for i, question in enumerate(questions):
        question_dict = question.model_dump()
        question_dict['id'] = str(uuid.uuid4())
        question_dict['question_number'] = i + 1
        output_data["questions"].append(question_dict)
    
    # Save to file
    output_path = args.output or OUTPUT_DIR / f"{Path(args.pdf_path).stem}_structured_questions.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(questions)} structured questions to {output_path}")

if __name__ == "__main__":
    main() 