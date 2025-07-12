#!/usr/bin/env python3
"""
Mistral OCR Processor for UPPSC Question Paper
Based on official Mistral OCR documentation
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import time
import base64

# Load environment variables from parent directory
load_dotenv('../.env')

class MistralOCRProcessor:
    def __init__(self):
        """Initialize the Mistral OCR processor."""
        self.api_key = os.getenv('MISTRAL_API_KEY')
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        
        self.base_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def extract_text_with_mistral_ocr(self, pdf_path):
        """
        Extract text from PDF using Mistral OCR API.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text from the PDF
        """
        print(f"Extracting text from: {pdf_path}")
        
        # Read the PDF file
        with open(pdf_path, 'rb') as file:
            pdf_content = file.read()
        
        # Encode PDF as base64
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        
        # Prepare the request payload for Mistral OCR
        payload = {
            "model": "mistral-ocr-latest",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text from this PDF document, preserving the structure of questions and options. Return the text in a clean, readable format."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:application/pdf;base64,{pdf_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 8000,
            "temperature": 0.1
        }
        
        try:
            print("Calling Mistral OCR API...")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            extracted_text = result['choices'][0]['message']['content']
            
            print(f"Successfully extracted {len(extracted_text)} characters")
            return extracted_text
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Mistral OCR API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            return None
    
    def parse_questions_with_mistral(self, extracted_text):
        """
        Use Mistral to parse the extracted text into structured questions and options.
        
        Args:
            extracted_text (str): Raw text extracted from PDF
            
        Returns:
            list: List of dictionaries containing questions and options
        """
        print("Using Mistral to parse questions and options...")
        
        # Truncate text if too long to avoid token limits
        text_sample = extracted_text[:6000] if len(extracted_text) > 6000 else extracted_text
        
        prompt = f"""
        Parse the following text from a UPSC question paper and extract all questions with their options.
        
        Return the result as a valid JSON array where each question object has:
        - "question_number": the question number (string)
        - "question_text": the full question text (string)
        - "options": array of objects with "option" (a/b/c/d) and "text" (option text)
        
        Text to parse:
        {text_sample}
        
        Return only valid JSON array, no additional text or explanations.
        """
        
        payload = {
            "model": "mistral-large-latest",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 4000
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Try to extract JSON from the response
            try:
                # Look for JSON array in the response
                start_idx = content.find('[')
                end_idx = content.rfind(']') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = content[start_idx:end_idx]
                    questions = json.loads(json_str)
                    return questions
                else:
                    # Try parsing the entire response as JSON
                    questions = json.loads(content)
                    return questions
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON from Mistral response: {e}")
                print(f"Response content: {content[:500]}...")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error calling Mistral Chat API: {e}")
            return None
    
    def parse_questions_manually(self, extracted_text):
        """
        Manual parsing as fallback method.
        
        Args:
            extracted_text (str): Raw text extracted from PDF
            
        Returns:
            list: List of dictionaries containing questions and options
        """
        print("Using manual parsing as fallback...")
        
        lines = extracted_text.split('\n')
        questions = []
        current_question = None
        current_options = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Question detection patterns
            if (line[0].isdigit() and '.' in line[:5]) or \
               line.startswith('Q') or \
               line.startswith('Question') or \
               (len(line) > 2 and line[0].isdigit() and line[1] == '.'):
                
                # Save previous question if exists
                if current_question:
                    questions.append({
                        'question_number': current_question['number'],
                        'question_text': current_question['text'],
                        'options': current_options
                    })
                
                # Start new question
                if line.startswith('Q'):
                    parts = line.split('.', 1) if '.' in line else [line[1:], '']
                elif line.startswith('Question'):
                    parts = line.split(' ', 2)[1:] if len(line.split(' ', 2)) > 2 else [line, '']
                else:
                    parts = line.split('.', 1)
                
                if len(parts) == 2:
                    current_question = {
                        'number': parts[0].strip(),
                        'text': parts[1].strip()
                    }
                    current_options = []
            
            # Option detection patterns
            elif (line.startswith('(') and len(line) > 2 and line[1].lower() in 'abcd' and line[2] == ')') or \
                 (line.startswith('a)') or line.startswith('b)') or line.startswith('c)') or line.startswith('d)')) or \
                 (len(line) > 1 and line[0].lower() in 'abcd' and line[1] == ')'):
                
                if line.startswith('('):
                    option_text = line[3:].strip()
                    option_letter = line[1].lower()
                elif line.startswith('a)') or line.startswith('b)') or line.startswith('c)') or line.startswith('d)'):
                    option_text = line[2:].strip()
                    option_letter = line[0].lower()
                else:
                    option_text = line[2:].strip()
                    option_letter = line[0].lower()
                
                if option_text:
                    current_options.append({
                        'option': option_letter,
                        'text': option_text
                    })
            
            # Continuation of question text
            elif current_question and not current_options:
                current_question['text'] += ' ' + line
        
        # Add the last question
        if current_question:
            questions.append({
                'question_number': current_question['number'],
                'question_text': current_question['text'],
                'options': current_options
            })
        
        return questions
    
    def save_structured_output(self, questions, output_path):
        """
        Save the structured questions and options to a JSON file.
        
        Args:
            questions (list): List of question dictionaries
            output_path (str): Path to save the JSON file
        """
        output_data = {
            'source_pdf': 'UPPCS_2024_Prelims_GS1_Question_Paper_English.pdf',
            'total_questions': len(questions),
            'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'questions': questions
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Structured output saved to: {output_path}")
    
    def process_pdf(self, pdf_path, output_path):
        """
        Complete pipeline to process PDF and extract structured questions.
        
        Args:
            pdf_path (str): Path to the English PDF
            output_path (str): Path to save the JSON output
        """
        # Step 1: Extract text using Mistral OCR
        extracted_text = self.extract_text_with_mistral_ocr(pdf_path)
        
        if not extracted_text:
            print("Failed to extract text from PDF")
            return None
        
        print(f"Extracted {len(extracted_text)} characters of text")
        
        # Step 2: Try parsing with Mistral Chat API first
        questions = self.parse_questions_with_mistral(extracted_text)
        
        if not questions:
            print("Mistral parsing failed, trying manual parsing...")
            questions = self.parse_questions_manually(extracted_text)
        
        if not questions:
            print("All parsing methods failed")
            return None
        
        print(f"Parsed {len(questions)} questions")
        
        # Step 3: Save structured output
        self.save_structured_output(questions, output_path)
        
        return questions

def main():
    """Main function to execute the OCR processing."""
    
    # Input and output paths
    pdf_path = "split_versions/UPPCS_2024_Prelims_GS1_Question_Paper_English.pdf"
    output_path = "uppsc_questions_extracted.json"
    
    # Check if input file exists
    if not os.path.exists(pdf_path):
        print(f"Error: Input file '{pdf_path}' not found!")
        print("Please run the PDF splitting script first.")
        return
    
    try:
        # Initialize the processor
        processor = MistralOCRProcessor()
        
        # Process the PDF
        questions = processor.process_pdf(pdf_path, output_path)
        
        if questions:
            print(f"\nProcessing completed successfully!")
            print(f"Total questions extracted: {len(questions)}")
            print(f"Output saved to: {output_path}")
            
            # Show a sample of the first question
            if questions:
                first_q = questions[0]
                print(f"\nSample question:")
                print(f"Q{first_q['question_number']}: {first_q['question_text']}")
                for option in first_q['options']:
                    print(f"  {option['option']}) {option['text']}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main() 