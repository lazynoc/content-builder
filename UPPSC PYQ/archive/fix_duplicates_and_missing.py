import json
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import base64

# Load environment variables
from dotenv import load_dotenv
load_dotenv('../.env')

# Initialize Mistral client
client = MistralClient(api_key=os.getenv('MISTRAL_API_KEY'))

def extract_question_86():
    """Extract question 86 from page 22"""
    pdf_path = "split_versions/UPPCS_2024_Prelims_GS1_Question_Paper_English.pdf"
    
    # Read the PDF and encode to base64
    with open(pdf_path, 'rb') as f:
        pdf_content = f.read()
    pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
    
    # Create the prompt for question 86 specifically
    prompt = f"""
    I have a PDF of the UPPSC 2024 Prelims GS1 question paper. I need to extract question number 86 from page 22.

    Please extract question 86 from the PDF and format it as JSON with the following structure:
    {{
        "question_number": "86",
        "question_text": "full question text here",
        "options": {{
            "a": "option a text",
            "b": "option b text", 
            "c": "option c text",
            "d": "option d text"
        }},
        "correct_answer": "A"
    }}

    Focus only on question 86 from page 22. If you cannot find it, return null.
    """
    
    try:
        response = client.chat(
            model="mistral-large-latest",
            messages=[
                ChatMessage(
                    role="user",
                    content=[
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:application/pdf;base64,{pdf_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                )
            ]
        )
        
        # Parse the response
        content = response.choices[0].message.content
        print("Mistral response for Q86:")
        print(content)
        
        # Try to extract JSON from the response
        if "{" in content and "}" in content:
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
            try:
                question_data = json.loads(json_str)
                return question_data
            except json.JSONDecodeError:
                print("Failed to parse JSON from response")
                return None
        else:
            print("No JSON found in response")
            return None
            
    except Exception as e:
        print(f"Error extracting question 86: {e}")
        return None

def clean_duplicates():
    """Remove duplicate question 132 and fix the JSON"""
    with open('uppsc_questions_complete_final.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find and remove the duplicate question 132 (the one with incomplete text)
    cleaned_questions = []
    seen_132 = False
    
    for question in data['questions']:
        if question['question_number'] == '132':
            if not seen_132:
                # Keep the first (complete) question 132
                cleaned_questions.append(question)
                seen_132 = True
            else:
                # Skip the second (incomplete) question 132
                print(f"Skipping duplicate question 132: {question['question_text'][:50]}...")
                continue
        else:
            cleaned_questions.append(question)
    
    # Update the data
    data['questions'] = cleaned_questions
    data['metadata']['total_questions'] = len(cleaned_questions)
    data['metadata']['questions_with_answers'] = len([q for q in cleaned_questions if 'correct_answer' in q])
    data['metadata']['questions_without_answers'] = len([q for q in cleaned_questions if 'correct_answer' not in q])
    
    # Save the cleaned data
    with open('uppsc_questions_cleaned.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Cleaned JSON saved. Total questions: {len(cleaned_questions)}")
    return data

def main():
    print("1. Cleaning duplicate question 132...")
    cleaned_data = clean_duplicates()
    
    print("\n2. Attempting to extract missing question 86...")
    question_86 = extract_question_86()
    
    if question_86:
        print("Successfully extracted question 86!")
        print(json.dumps(question_86, indent=2))
        
        # Add question 86 to the cleaned data
        question_86['id'] = f"missing_q86_{len(cleaned_data['questions']) + 1}"
        question_86['extraction_order'] = len(cleaned_data['questions']) + 1
        question_86['chunk_number'] = 99  # Special chunk for missing questions
        
        cleaned_data['questions'].append(question_86)
        cleaned_data['metadata']['total_questions'] = len(cleaned_data['questions'])
        cleaned_data['metadata']['questions_with_answers'] = len([q for q in cleaned_data['questions'] if 'correct_answer' in q])
        cleaned_data['metadata']['questions_without_answers'] = len([q for q in cleaned_data['questions'] if 'correct_answer' not in q])
        cleaned_data['metadata']['missing_question_86_added'] = True
        
        # Save the final data
        with open('uppsc_questions_final_complete.json', 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Final dataset saved with {len(cleaned_data['questions'])} questions!")
    else:
        print("Could not extract question 86. Saving cleaned data without it.")
        with open('uppsc_questions_final_complete.json', 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Cleaned dataset saved with {len(cleaned_data['questions'])} questions (missing Q86)")

if __name__ == "__main__":
    main() 