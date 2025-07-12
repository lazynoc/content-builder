#!/usr/bin/env python3
"""
Test Supabase Ingestion - Upload first 5 questions from optimized Grok analysis
"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv('../.env')

class SupabaseIngestionTester:
    def __init__(self):
        self.supabase_url = os.getenv('VITE_SUPABASE_URL')
        self.supabase_key = os.getenv('VITE_SUPABASE_ANON_KEY')
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
    
    def transform_question_for_supabase(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Transform question data to match Supabase schema"""
        
        # Helper function to truncate strings to varchar limits
        def truncate_string(value, max_length):
            if value and len(str(value)) > max_length:
                return str(value)[:max_length-3] + "..."
            return value
        
        # Create tags list
        tags = []
        if question.get('primary_type'):
            tags.append(question['primary_type'])
        if question.get('secondary_type'):
            tags.append(question['secondary_type'])
        tags.extend(['UPPSC', 'Prelims', 'UP'])
        
        # Transform to Supabase format (exact schema match)
        supabase_question = {
            'question_number': str(question['question_number']),  # varchar(10)
            'year': question['year'],  # integer
            'section': truncate_string(question['section'], 100),  # varchar(100)
            'question_text': question['question_text'],  # text
            'correct_answer': question['correct_answer'],  # char(1)
            'explanation': question.get('explanation', ''),  # text
            'options': question['options'],  # jsonb - keep as JSON object
            'primary_type': truncate_string(question.get('primary_type'), 50),  # varchar(50)
            'secondary_type': truncate_string(question.get('secondary_type'), 50),  # varchar(50)
            'difficulty_level': truncate_string(question.get('difficulty_level'), 20),  # varchar(20)
            'difficulty_reason': question.get('difficulty_reason'),  # text
            'knowledge_requirement': truncate_string(question.get('knowledge_requirement'), 100),  # varchar(100)
            'testing_objective': question.get('testing_objective'),  # text
            'question_design_strategy': question.get('question_design_strategy'),  # text
            'trap_setting': question.get('trap_setting'),  # text
            'discrimination_potential': question.get('discrimination_potential'),  # text
            'options_analysis': question.get('options_analysis'),  # jsonb
            'key_concepts': question.get('key_concepts'),  # jsonb
            'common_mistakes': question.get('common_mistakes'),  # jsonb
            'elimination_technique': question.get('elimination_technique'),  # text
            'memory_hooks': question.get('memory_hooks'),  # jsonb
            'related_topics': question.get('related_topics'),  # jsonb
            'current_affairs_connection': question.get('current_affairs_connection'),  # text
            'time_management': question.get('time_management'),  # text
            'confidence_calibration': question.get('confidence_calibration'),  # text
            'source_material': question.get('source_material'),  # text
            'source_type': truncate_string(question.get('source_type'), 100),  # varchar(100)
            'test_series_reference': question.get('test_series_reference'),  # text
            'extraction_order': question.get('extraction_order'),  # integer
            'chunk_number': question.get('chunk_number'),  # integer
            'tags': tags,  # jsonb - list of strings
            'motivation': question.get('motivation'),  # text
            'examiner_thought_process': question.get('examiner_thought_process'),  # jsonb
            'learning_insights': question.get('learning_insights'),  # text
            'openai_analysis_date': question.get('grok_analysis_date'),  # timestamp
            'exam_type': 'UPPSC'  # varchar(50) - set to UPPSC
        }
        
        return supabase_question
    
    def upload_questions_to_supabase(self, questions: List[Dict[str, Any]]) -> bool:
        """Upload questions to Supabase"""
        
        transformed_questions = []
        for question in questions:
            transformed_question = self.transform_question_for_supabase(question)
            transformed_questions.append(transformed_question)
        
        print(f"Uploading {len(transformed_questions)} questions to Supabase...")
        
        try:
            response = requests.post(
                f"{self.supabase_url}/rest/v1/pyq_question_table",
                headers=self.headers,
                json=transformed_questions
            )
            
            if response.status_code == 201:
                print(f"✅ Successfully uploaded {len(transformed_questions)} questions to Supabase!")
                return True
            else:
                print(f"❌ Upload failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error uploading to Supabase: {e}")
            return False
    
    def test_supabase_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/pyq_question_table?select=count",
                headers=self.headers
            )
            
            if response.status_code == 200:
                print("✅ Supabase connection successful!")
                return True
            else:
                print(f"❌ Supabase connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting to Supabase: {e}")
            return False

def main():
    """Main function to test Supabase ingestion"""
    
    # Load the optimized Grok analysis
    with open('uppsc_questions_grok_optimized.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get first 5 questions for testing
    questions = data['questions'][:5]
    
    print(f"Testing Supabase ingestion with {len(questions)} questions...")
    print(f"Questions: {[q['question_number'] for q in questions]}")
    
    # Initialize Supabase tester
    tester = SupabaseIngestionTester()
    
    # Test connection first
    if not tester.test_supabase_connection():
        print("❌ Cannot proceed without Supabase connection")
        return
    
    # Upload questions
    success = tester.upload_questions_to_supabase(questions)
    
    if success:
        print("\n🎉 Test successful! You can now:")
        print("1. Check your Supabase dashboard")
        print("2. Start building your frontend")
        print("3. Query the data using Supabase client")
        print("\nNext steps:")
        print("- Wait for full 150 questions analysis to complete")
        print("- Upload all questions when ready")
        print("- Build frontend features using this data")
    else:
        print("\n❌ Test failed. Check the error messages above.")

if __name__ == "__main__":
    main() 