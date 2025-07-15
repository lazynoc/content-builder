#!/usr/bin/env python3
"""
UPPSC Question Extractor using Mistral OCR with Document Annotations (Chunked Processing)
This script processes the PDF in 8-page chunks to work around the Document Annotations page limit.
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

# Load environment variables from parent directory
load_dotenv('../.env')

# Define the structured output format for questions and options
class Option(BaseModel):
    option_letter: str = Field(..., description="The option letter (a, b, c, or d)")
    option_text: str = Field(..., description="The text content of the option")

class Question(BaseModel):
    question_number: str = Field(..., description="The question number (e.g., '1', '2', etc.)")
    question_text: str = Field(..., description="The complete question text")
    options: List[Option] = Field(..., description="List of options (a, b, c, d) for this question")

class UPSCQuestionPaper(BaseModel):
    exam_name: str = Field(..., description="Name of the exam (e.g., 'UPPSC 2024 Prelims GS1')")
    total_questions: int = Field(..., description="Total number of questions extracted")
    questions: List[Question] = Field(..., description="List of all questions with their options")

def upload_pdf_to_mistral(client, pdf_path):
    """
    Upload PDF to Mistral and get signed URL.
    
    Args:
        client: Mistral client instance
        pdf_path: Path to the PDF file
        
    Returns:
        str: Signed URL for the uploaded PDF
    """
    print(f"Uploading PDF: {pdf_path}")
    
    try:
        # Upload the PDF
        uploaded_pdf = client.files.upload(
            file={
                "file_name": os.path.basename(pdf_path),
                "content": open(pdf_path, "rb"),
            },
            purpose="ocr"
        )
        
        print(f"PDF uploaded successfully with ID: {uploaded_pdf.id}")
        
        # Get signed URL
        signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)
        
        print(f"Signed URL obtained: {signed_url.url[:50]}...")
        
        return signed_url.url
        
    except Exception as e:
        print(f"Error uploading PDF: {e}")
        return None

def extract_questions_from_chunk(client, signed_url, start_page, end_page):
    """
    Extract questions from a specific page range using Mistral OCR.
    
    Args:
        client: Mistral client instance
        signed_url: Signed URL of the uploaded PDF
        start_page: Starting page number (0-indexed)
        end_page: Ending page number (exclusive)
        
    Returns:
        dict: Structured data containing questions from this chunk
    """
    print(f"Processing pages {start_page} to {end_page-1}...")
    
    try:
        from mistralai.extra import response_format_from_pydantic_model
        
        # Create page range
        pages = list(range(start_page, end_page))
        
        response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": signed_url
            },
            pages=pages,
            document_annotation_format=response_format_from_pydantic_model(UPSCQuestionPaper),
            include_image_base64=False
        )
        
        print(f"Successfully processed pages {start_page} to {end_page-1}")
        
        # Extract the structured data
        if hasattr(response, 'document_annotation') and response.document_annotation:
            # Convert to dict if it's a Pydantic model
            if hasattr(response.document_annotation, 'model_dump'):
                return response.document_annotation.model_dump()
            elif isinstance(response.document_annotation, dict):
                return response.document_annotation
            else:
                print(f"Unexpected document_annotation type: {type(response.document_annotation)}")
                return None
        else:
            print(f"No document annotation found for pages {start_page} to {end_page-1}")
            return None
            
    except Exception as e:
        print(f"Error processing pages {start_page} to {end_page-1}: {e}")
        return None

def combine_question_chunks(chunks):
    """
    Combine questions from multiple chunks into a single structure.
    
    Args:
        chunks: List of question data from different chunks
        
    Returns:
        dict: Combined question data
    """
    if not chunks:
        return None
    
    combined_questions = []
    total_questions = 0
    
    for chunk in chunks:
        if chunk and isinstance(chunk, dict):
            if 'questions' in chunk and isinstance(chunk['questions'], list):
                combined_questions.extend(chunk['questions'])
                total_questions += chunk.get('total_questions', len(chunk['questions']))
            else:
                print(f"Warning: Invalid chunk format: {chunk}")
    
    # Create combined structure
    combined_data = {
        'exam_name': 'UPPSC 2024 Prelims GS1',
        'total_questions': total_questions,
        'questions': combined_questions
    }
    
    return combined_data

def extract_questions_with_mistral_ocr_chunked(client, pdf_path):
    """
    Extract questions and options using Mistral OCR with chunked processing.
    Only processes the first 5 pages (0-4).
    """
    print("Starting question extraction for first 5 pages with Mistral OCR...")
    
    # First, upload the PDF and get signed URL
    signed_url = upload_pdf_to_mistral(client, pdf_path)
    
    if not signed_url:
        print("Failed to upload PDF")
        return None
    
    # Only process pages 0-4
    start_page = 0
    end_page = 5
    chunks = []
    chunk_data = extract_questions_from_chunk(client, signed_url, start_page, end_page)
    if chunk_data:
        chunks.append(chunk_data)
        print(f"Chunk 1: Found {chunk_data.get('total_questions', 0)} questions")
    else:
        print("Chunk 1: No data found")
    
    # Combine (trivial, just one chunk)
    combined_data = combine_question_chunks(chunks)
    
    if combined_data:
        print(f"Successfully processed first 5 pages.")
        return combined_data
    else:
        print("Failed to process first 5 pages")
        return None

def save_structured_output(data, output_path):
    """
    Save the structured questions and options to a JSON file.
    
    Args:
        data: Structured data from Mistral OCR
        output_path: Path to save the JSON file
    """
    output_data = {
        'source_pdf': 'UPPCS_2024_Prelims_GS1_Question_Paper_English.pdf',
        'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'extraction_method': 'Mistral OCR with Document Annotations (Chunked)',
        'data': data
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Structured output saved to: {output_path}")

def display_sample_questions(data, num_samples=3):
    """
    Display sample questions for verification.
    
    Args:
        data: Structured data containing questions
        num_samples: Number of sample questions to display
    """
    if not data or 'questions' not in data:
        print("No questions found in the data")
        return
    
    questions = data['questions']
    print(f"\n{'='*60}")
    print(f"SAMPLE QUESTIONS (showing first {min(num_samples, len(questions))} questions)")
    print(f"{'='*60}")
    
    for i, question in enumerate(questions[:num_samples]):
        if isinstance(question, dict):
            print(f"\nQ{question.get('question_number', '?')}: {question.get('question_text', 'No text')}")
            options = question.get('options', [])
            for option in options:
                if isinstance(option, dict):
                    print(f"  {option.get('option_letter', '?')}) {option.get('option_text', 'No text')}")
        
        if i < num_samples - 1:
            print("-" * 40)

def main():
    """Main function to execute the question extraction."""
    
    # Check if Mistral API key is available
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        print("Error: MISTRAL_API_KEY not found in environment variables")
        print("Please set your Mistral API key in the .env file")
        return
    
    # Input and output paths
    pdf_path = "split_versions/UPPCS_2024_Prelims_GS1_Question_Paper_English.pdf"
    output_path = "uppsc_questions_structured_first5.json"
    
    # Check if input file exists
    if not os.path.exists(pdf_path):
        print(f"Error: Input file '{pdf_path}' not found!")
        print("Please run the PDF splitting script first.")
        return
    
    try:
        # Initialize Mistral client
        from mistralai import Mistral
        client = Mistral(api_key=api_key)
        
        print("Mistral client initialized successfully")
        
        # Extract questions using Mistral OCR for first 5 pages
        structured_data = extract_questions_with_mistral_ocr_chunked(client, pdf_path)
        
        if structured_data:
            print(f"\nExtraction completed successfully!")
            print(f"Total questions extracted: {structured_data.get('total_questions', 'Unknown')}")
            
            # Display sample questions
            display_sample_questions(structured_data, num_samples=5)
            
            # Save structured output
            save_structured_output(structured_data, output_path)
            
            print(f"\nProcessing completed successfully!")
            print(f"Output saved to: {output_path}")
            
        else:
            print("Failed to extract questions from PDF")
        
    except ImportError as e:
        print(f"Error: Missing required package - {e}")
        print("Please install the Mistral AI client: pip install mistralai")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 