#!/usr/bin/env python3
"""
Supabase Ingest Script for UPSC PYQ Questions
Ingests processed JSON files into the Supabase database
"""

import json
import os
import sys
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import uuid
from tqdm import tqdm

# Load environment variables
load_dotenv('../../../.env')

# Database configuration
DB_CONFIG = {
    'host': os.getenv('SUPABASE_HOST'),
    'database': os.getenv('SUPABASE_DB_NAME'),
    'user': os.getenv('SUPABASE_DB_USER'),
    'password': os.getenv('SUPABASE_DB_PASSWORD'),
    'port': os.getenv('SUPABASE_DB_PORT', '5432')
}

class SupabaseIngester:
    def __init__(self):
        self.connection: Any = None
        self.cursor: Any = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("✅ Connected to Supabase database")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔌 Database connection closed")
    
    def load_json_file(self, file_path: str) -> Dict[str, Any]:
        """Load JSON file and return data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return {}
    
    def validate_question_data(self, question: Dict[str, Any]) -> bool:
        """Validate question data structure"""
        required_fields = ['id', 'question_number', 'question_text', 'options']
        
        for field in required_fields:
            if field not in question:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Validate options structure
        if not isinstance(question['options'], list):
            print(f"❌ Options must be a list for question {question.get('question_number', 'unknown')}")
            return False
        
        for option in question['options']:
            if not isinstance(option, dict) or 'letter' not in option or 'text' not in option:
                print(f"❌ Invalid option structure for question {question.get('question_number', 'unknown')}")
                return False
        
        return True
    
    def insert_question(self, question: Dict[str, Any], year: int) -> bool:
        """Insert a single question into the database"""
        try:
            # Prepare the data
            question_data = {
                'id': question['id'],
                'question_number': question['question_number'],
                'year': year,
                'exam_type': 'UPSC',
                'exam_stage': 'Prelims',
                'question_text': question['question_text'],
                'question_type': question.get('type', 'mcq'),
                'difficulty': question.get('difficulty', 'Medium'),
                'subject': question.get('subject', 'General Studies'),
                'topic': None,  # Will be populated by Grok analysis later
                'options': json.dumps(question['options']),
                'exam_info': question.get('exam_info', f'Prelims {year}'),
                'paper': 'General Studies Paper I',
                'section': None,  # Will be populated by Grok analysis later
                'source': 'Official'
            }
            
            # SQL query
            query = """
                INSERT INTO question_bank (
                    id, question_number, year, exam_type, exam_stage, question_text, 
                    question_type, difficulty, subject, topic, options, exam_info, paper, section, source
                ) VALUES (
                    %(id)s, %(question_number)s, %(year)s, %(exam_type)s, %(exam_stage)s, %(question_text)s,
                    %(question_type)s, %(difficulty)s, %(subject)s, %(topic)s, %(options)s::jsonb, 
                    %(exam_info)s, %(paper)s, %(section)s, %(source)s
                ) ON CONFLICT (id) DO UPDATE SET
                    question_text = EXCLUDED.question_text,
                    question_type = EXCLUDED.question_type,
                    difficulty = EXCLUDED.difficulty,
                    subject = EXCLUDED.subject,
                    topic = EXCLUDED.topic,
                    options = EXCLUDED.options,
                    exam_info = EXCLUDED.exam_info,
                    paper = EXCLUDED.paper,
                    section = EXCLUDED.section,
                    updated_at = NOW()
            """
            
            self.cursor.execute(query, question_data)
            return True
            
        except Exception as e:
            print(f"❌ Error inserting question {question.get('question_number', 'unknown')}: {e}")
            return False
    
    def ingest_year(self, year: int) -> bool:
        """Ingest all questions for a specific year"""
        json_file = f"../json_files/upsc_prelims_{year}_structured_for_frontend.json"
        
        if not os.path.exists(json_file):
            print(f"❌ JSON file not found: {json_file}")
            return False
        
        print(f"📁 Loading {year} data from {json_file}")
        data = self.load_json_file(json_file)
        
        if not data or 'questions' not in data:
            print(f"❌ Invalid JSON structure for {year}")
            return False
        
        questions = data['questions']
        print(f"📊 Found {len(questions)} questions for {year}")
        
        success_count = 0
        error_count = 0
        
        for question in tqdm(questions, desc=f"Processing {year}"):
            if self.validate_question_data(question):
                if self.insert_question(question, year):
                    success_count += 1
                else:
                    error_count += 1
            else:
                error_count += 1
        
        # Commit the transaction
        self.connection.commit()
        
        print(f"✅ {year}: {success_count} questions inserted, {error_count} errors")
        return error_count == 0
    
    def ingest_all_years(self, years: List[int] = [2021, 2022, 2023, 2024, 2025]) -> bool:
        """Ingest all available years"""
        
        print("🚀 Starting Supabase ingestion process")
        print("=" * 50)
        
        self.connect()
        
        try:
            all_success = True
            for year in years:
                print(f"\n📅 Processing year {year}")
                if not self.ingest_year(year):
                    all_success = False
                    print(f"⚠️  Issues found with {year}")
            
            if all_success:
                print("\n🎉 All years processed successfully!")
            else:
                print("\n⚠️  Some years had issues. Check the logs above.")
            
            return all_success
            
        finally:
            self.disconnect()
    
    def verify_ingestion(self) -> Dict[str, Any]:
        """Verify the ingestion by counting questions per year"""
        self.connect()
        
        try:
            query = """
                SELECT 
                    exam_type,
                    year,
                    COUNT(*) as question_count,
                    COUNT(DISTINCT subject) as subjects,
                    MIN(created_at) as first_insert,
                    MAX(created_at) as last_insert
                FROM question_bank 
                GROUP BY exam_type, year 
                ORDER BY exam_type, year DESC
            """
            
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            print("\n📊 Ingestion Verification Results:")
            print("=" * 40)
            
            total_questions = 0
            for row in results:
                print(f"{row['exam_type']} {row['year']}: {row['question_count']} questions, {row['subjects']} subjects")
                total_questions += row['question_count']
            
            print(f"\nTotal questions in database: {total_questions}")
            
            return {
                'years_processed': len(results),
                'total_questions': total_questions,
                'year_details': [dict(row) for row in results]
            }
            
        finally:
            self.disconnect()

def main():
    """Main function"""
    ingester = SupabaseIngester()
    
    # Check if specific year is provided as argument
    if len(sys.argv) > 1:
        try:
            year = int(sys.argv[1])
            if year in [2021, 2022, 2023, 2024, 2025]:
                ingester.ingest_all_years([year])
            else:
                print(f"❌ Invalid year: {year}. Must be 2021-2025")
        except ValueError:
            print("❌ Invalid year format. Use: python3 supabase_ingest.py 2025")
    else:
        # Ingest all years
        ingester.ingest_all_years()
    
    # Verify ingestion
    ingester.verify_ingestion()

if __name__ == "__main__":
    main() 