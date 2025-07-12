import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv('../.env')

class SupabaseUploader:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
    
    def upload_questions(self, questions: List[Dict[str, Any]], batch_size: int = 10) -> Dict[str, Any]:
        """Upload questions to Supabase in batches"""
        
        total_questions = len(questions)
        successful_uploads = 0
        failed_uploads = 0
        errors = []
        
        print(f"Starting upload of {total_questions} questions to Supabase...")
        
        for i in range(0, total_questions, batch_size):
            batch = questions[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_questions + batch_size - 1) // batch_size
            
            print(f"Uploading batch {batch_num}/{total_batches} ({len(batch)} questions)")
            
            try:
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/pyq_question_table",
                    headers=self.headers,
                    json=batch,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    successful_uploads += len(batch)
                    print(f"✅ Batch {batch_num} uploaded successfully")
                else:
                    failed_uploads += len(batch)
                    error_msg = f"Batch {batch_num} failed: {response.status_code} - {response.text}"
                    errors.append(error_msg)
                    print(f"❌ {error_msg}")
                    
            except Exception as e:
                failed_uploads += len(batch)
                error_msg = f"Batch {batch_num} error: {str(e)}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
        
        return {
            "total_questions": total_questions,
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
            "errors": errors,
            "upload_date": datetime.now().isoformat()
        }
    
    def check_existing_questions(self, year: int, exam_type: str) -> List[str]:
        """Check for existing questions to avoid duplicates"""
        
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/pyq_question_table",
                headers=self.headers,
                params={
                    "select": "question_number",
                    "year": f"eq.{year}",
                    "exam_type": f"eq.{exam_type}"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                existing_questions = response.json()
                return [q['question_number'] for q in existing_questions]
            else:
                print(f"Warning: Could not check existing questions: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Warning: Error checking existing questions: {e}")
            return []
    
    def delete_existing_questions(self, year: int, exam_type: str) -> bool:
        """Delete existing questions for the given year and exam type"""
        
        try:
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/pyq_question_table",
                headers=self.headers,
                params={
                    "year": f"eq.{year}",
                    "exam_type": f"eq.{exam_type}"
                },
                timeout=30
            )
            
            if response.status_code in [200, 204]:
                print(f"✅ Deleted existing questions for {exam_type} {year}")
                return True
            else:
                print(f"❌ Failed to delete existing questions: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting existing questions: {e}")
            return False

def prepare_questions_for_upload(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare questions for Supabase upload by cleaning and formatting data"""
    
    prepared_questions = []
    
    for question in questions:
        # Create a clean version for upload
        upload_question = {
            "id": question.get('id'),
            "question_number": question['question_number'],
            "year": question['year'],
            "section": question['section'],
            "question_text": question['question_text'],
            "correct_answer": question['correct_answer'],
            "explanation": question.get('explanation'),
            "options": question['options'],
            "primary_type": question.get('primary_type'),
            "secondary_type": question.get('secondary_type'),
            "difficulty_level": question.get('difficulty_level'),
            "difficulty_reason": question.get('difficulty_reason'),
            "knowledge_requirement": question.get('knowledge_requirement'),
            "testing_objective": question.get('testing_objective'),
            "question_design_strategy": question.get('question_design_strategy'),
            "trap_setting": question.get('trap_setting'),
            "discrimination_potential": question.get('discrimination_potential'),
            "options_analysis": question.get('options_analysis'),
            "key_concepts": question.get('key_concepts'),
            "common_mistakes": question.get('common_mistakes'),
            "elimination_technique": question.get('elimination_technique'),
            "memory_hooks": question.get('memory_hooks'),
            "related_topics": question.get('related_topics'),
            "current_affairs_connection": question.get('current_affairs_connection'),
            "time_management": question.get('time_management'),
            "confidence_calibration": question.get('confidence_calibration'),
            "source_material": question.get('source_material'),
            "source_type": question.get('source_type'),
            "test_series_reference": question.get('test_series_reference'),
            "extraction_order": question.get('extraction_order'),
            "chunk_number": question.get('chunk_number'),
            "tags": question.get('tags'),
            "motivation": question.get('motivation'),
            "examiner_thought_process": question.get('examiner_thought_process'),
            "learning_insights": question.get('learning_insights'),
            "openai_analysis_date": question.get('grok_analysis_date'),  # Use Grok analysis date
            "exam_type": question['exam_type']
        }
        
        # Remove None values to avoid database issues
        upload_question = {k: v for k, v in upload_question.items() if v is not None}
        
        prepared_questions.append(upload_question)
    
    return prepared_questions

def main():
    """Main function to upload questions to Supabase"""
    
    # Load the analyzed questions
    with open('uppsc_questions_complete_enhanced_fixed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data['questions']
    
    # Initialize uploader
    uploader = SupabaseUploader()
    
    # Check if we want to replace existing questions
    year = 2024
    exam_type = "UPPSC"
    
    existing_questions = uploader.check_existing_questions(year, exam_type)
    
    if existing_questions:
        print(f"Found {len(existing_questions)} existing questions for {exam_type} {year}")
        replace = input("Do you want to replace existing questions? (y/n): ").lower().strip()
        
        if replace == 'y':
            if uploader.delete_existing_questions(year, exam_type):
                print("Proceeding with upload...")
            else:
                print("Failed to delete existing questions. Aborting.")
                return
        else:
            print("Upload cancelled.")
            return
    
    # Prepare questions for upload
    prepared_questions = prepare_questions_for_upload(questions)
    
    # Upload to Supabase
    result = uploader.upload_questions(prepared_questions, batch_size=10)
    
    # Save upload report
    report = {
        "metadata": {
            "upload_date": datetime.now().isoformat(),
            "source_file": "uppsc_questions_with_grok_analysis.json",
            "exam_type": exam_type,
            "year": year
        },
        "upload_result": result
    }
    
    with open('supabase_upload_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*50)
    print("UPLOAD SUMMARY")
    print("="*50)
    print(f"Total Questions: {result['total_questions']}")
    print(f"Successful Uploads: {result['successful_uploads']}")
    print(f"Failed Uploads: {result['failed_uploads']}")
    print(f"Success Rate: {(result['successful_uploads']/result['total_questions']*100):.1f}%")
    
    if result['errors']:
        print(f"\nErrors ({len(result['errors'])}):")
        for error in result['errors'][:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(result['errors']) > 5:
            print(f"  ... and {len(result['errors']) - 5} more errors")
    
    print(f"\n📁 Upload report saved as: supabase_upload_report.json")

if __name__ == "__main__":
    main() 