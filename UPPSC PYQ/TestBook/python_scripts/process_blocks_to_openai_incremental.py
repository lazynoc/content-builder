import json
import os
import re
import time
import uuid
from typing import List, Dict, Any
import openai
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def read_markdown_blocks(file_path: str) -> List[str]:
    """Read markdown file and split into blocks by '---'"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Split by the separator (three dashes)
    blocks = [block.strip() for block in content.split('---') if block.strip()]
    return blocks

def clean_block_for_openai(block: str) -> str:
    """Clean and format block for OpenAI processing"""
    # Remove any remaining separators or artifacts
    block = re.sub(r'---', '', block)
    
    # Clean up extra whitespace
    block = re.sub(r'\n\s*\n\s*\n', '\n\n', block)
    
    # Ensure proper line breaks for readability
    block = block.strip()
    
    return block

def extract_question_number_from_block(block: str) -> int:
    """Extract question number from the markdown block"""
    # Look for patterns like "Physics\n22" or "Question 22" or just "22"
    lines = block.split('\n')
    for line in lines:
        # Look for standalone numbers (question numbers)
        match = re.search(r'^(\d+)$', line.strip())
        if match:
            return int(match.group(1))
    
    # If no standalone number found, look for numbers in context
    for line in lines:
        match = re.search(r'(\d+)', line.strip())
        if match:
            return int(match.group(1))
    
    return 0

def generate_question_id(question_number: int) -> str:
    """Generate a consistent ID based on question number"""
    return f"uppsc-2024-q{question_number:03d}"

def create_openai_prompt(blocks: List[str]) -> str:
    """Create a comprehensive prompt for OpenAI"""
    prompt = """You are an expert at converting educational content into structured question bank format. 

Process the following 5 question blocks and convert them into a structured JSON format suitable for a test-taking environment.

CRITICAL REQUIREMENTS:
1. Use the EXACT question numbers from the markdown blocks (e.g., if block shows "22", use question_number: 22)
2. Break lines where they naturally break in the original content
3. If there are tables, format them as structured data that frontend can easily recognize
4. If there are formulas, preserve them in proper mathematical format
5. Make questions suitable for test-taking - clear, concise, and well-formatted
6. Ensure options are properly numbered and formatted
7. Preserve all technical accuracy and educational value

IMPORTANT FORMATTING RULES:
- "question_text" should contain ONLY the question statement, NOT the options
- Remove all option numbers (1, 2, 3, 4) from the question_text
- Put all options in the separate "options" array
- Clean up any "You: 00:00 Avg: 00:20 | +1.33 -0.44" timestamps from question_text

DYNAMIC FORMATTING GUIDELINES:
- Analyze the content structure and choose the most appropriate format:
  * For tables: Use pipe-separated format, HTML table tags, or structured arrays depending on complexity
  * For lists: Use bullet points (•), numbered lists, or structured arrays based on content type
  * For matching questions: Use clear column separation or structured format that's easy to read
  * For mathematical formulas: Use proper mathematical notation
  * For code snippets: Use code blocks or inline formatting
  * For diagrams: Use ASCII art or structured text representation
- Choose the format that will be most readable and user-friendly in a test-taking interface
- Ensure the format is consistent and easy to parse by frontend applications

OUTPUT FORMAT:
Return a JSON array with each question having this structure:
{
  "question_number": <EXACT number from markdown>,
  "type": "mcq",
  "difficulty": "Easy/Medium/Hard",
  "subject": "<subject category>",
  "exam_info": "UPPSC Prelims 2024",
  "question_text": "<ONLY the question statement, no options, with proper formatting for tables/lists>",
  "options": [
    {"letter": "1", "text": "<option text>"},
    {"letter": "2", "text": "<option text>"},
    {"letter": "3", "text": "<option text>"},
    {"letter": "4", "text": "<option text>"}
  ],
  "correct_answer": <1-4>,
  "explanation": "<detailed explanation with proper formatting>"
}

IMPORTANT: Return ONLY valid JSON. Do not include any text before or after the JSON array.

Here are the 5 question blocks to process:

"""
    
    for i, block in enumerate(blocks, 1):
        prompt += f"\n--- BLOCK {i} ---\n{clean_block_for_openai(block)}\n"
    
    prompt += "\n\nProcess these blocks and return ONLY the JSON array. Do not include any explanatory text outside the JSON."
    
    return prompt

def process_batch_with_openai(blocks: List[str], batch_num: int) -> List[Dict[str, Any]]:
    """Process a batch of blocks with OpenAI"""
    print(f"🔄 Processing batch {batch_num} with {len(blocks)} blocks...")
    
    # Extract question numbers from blocks for reference
    block_numbers = [extract_question_number_from_block(block) for block in blocks]
    print(f"📝 Question numbers in this batch: {block_numbers}")
    
    prompt = create_openai_prompt(blocks)
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational content processor with deep understanding of formatting for test-taking interfaces. Convert question blocks into structured JSON format that will be displayed in a user-friendly test environment. IMPORTANT: Use the exact question numbers from the markdown blocks and choose the most appropriate formatting for each content type (tables, lists, formulas, etc.) to ensure optimal readability and user experience."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=4000
        )
        
        # Extract JSON from response
        content = response.choices[0].message.content
        if content:
            content = content.strip()
        else:
            raise Exception("Empty response from OpenAI")
        
        print(f"🔍 Raw response length: {len(content)} characters")
        print(f"🔍 Response preview: {content[:200]}...")
        
        # Try to extract JSON if it's wrapped in markdown
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        
        # Clean up any leading/trailing whitespace
        content = content.strip()
        
        # Parse JSON
        try:
            questions = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"🔍 Content that failed to parse: {content[:500]}...")
            raise Exception(f"Invalid JSON response: {e}")
        
        # Add IDs and ensure proper question numbers
        for i, question in enumerate(questions):
            # Use the question number from the response, or fall back to block number
            q_num = question.get('question_number', block_numbers[i] if i < len(block_numbers) else 0)
            question['id'] = generate_question_id(q_num)
            question['question_number'] = q_num
        
        print(f"✅ Batch {batch_num} processed successfully - {len(questions)} questions extracted")
        return questions
        
    except Exception as e:
        print(f"❌ Error processing batch {batch_num}: {str(e)}")
        if 'content' in locals() and content:
            print(f"Response content: {content[:500]}...")
        return []

def load_existing_questions(output_file: str) -> List[Dict[str, Any]]:
    """Load existing questions from JSON file if it exists"""
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                # Simple array of questions
                questions = data
                print(f"📂 Loaded {len(questions)} existing questions from {output_file}")
            elif isinstance(data, dict) and 'questions' in data:
                # Object with questions array
                questions = data['questions']
                print(f"📂 Loaded {len(questions)} existing questions from {output_file}")
            else:
                # Unknown structure, start fresh
                print(f"⚠️ Unknown JSON structure in {output_file}. Starting fresh.")
                questions = []
            
            return questions
        except Exception as e:
            print(f"⚠️ Error loading existing file: {e}. Starting fresh.")
            return []
    return []

def save_questions_incremental(questions: List[Dict[str, Any]], output_file: str, batch_num: int):
    """Save questions to JSON file, updating existing file"""
    try:
        # Check if file exists and get its structure
        existing_data = None
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        
        # Load existing questions
        all_questions = load_existing_questions(output_file)
        
        # Add new questions
        all_questions.extend(questions)
        
        # Create the main structure (always use the same format)
        main_data = {
            "exam_info": {
                "exam_name": "UPPSC Civil Services Preliminary Examination",
                "year": 2024,
                "paper": "General Studies Paper I",
                "total_questions": len(all_questions),
                "processing_date": f"2025-01-17 (Batch {batch_num} completed)",
                "version": "3.0-openai"
            },
            "questions": all_questions
        }
        
        # Save updated file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(main_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Updated {output_file} with {len(questions)} new questions (Total: {len(all_questions)})")
        
        return len(all_questions)
        
    except Exception as e:
        print(f"❌ Error saving questions: {e}")
        return 0

def main():
    # File paths
    markdown_file = "../markdown_files/2024_pyq_missing_cleaned.md"
    output_dir = "../json_files"
    output_file = os.path.join(output_dir, "uppsc_prelims_2024_structured_for_frontend_missing.json")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read all blocks
    print("📖 Reading markdown blocks...")
    blocks = read_markdown_blocks(markdown_file)
    print(f"📊 Found {len(blocks)} total blocks")
    
    # Process in batches of 5
    batch_size = 5
    total_questions = 0
    
    for i in range(0, len(blocks), batch_size):
        batch_num = (i // batch_size) + 1
        batch_blocks = blocks[i:i + batch_size]
        
        print(f"\n{'='*50}")
        print(f"Processing batch {batch_num} of {(len(blocks) + batch_size - 1) // batch_size}")
        print(f"{'='*50}")
        
        # Process batch
        questions = process_batch_with_openai(batch_blocks, batch_num)
        
        if questions:
            # Save incrementally to main file
            total_questions = save_questions_incremental(questions, output_file, batch_num)
        else:
            print(f"⚠️ No questions extracted from batch {batch_num}")
        
        # Add delay between batches to avoid rate limiting
        if i + batch_size < len(blocks):
            print("⏳ Waiting 2 seconds before next batch...")
            time.sleep(2)
    
    print(f"\n🎉 Processing complete!")
    print(f"📊 Total questions in final file: {total_questions}")
    print(f"💾 Final file: {output_file}")

if __name__ == "__main__":
    main()