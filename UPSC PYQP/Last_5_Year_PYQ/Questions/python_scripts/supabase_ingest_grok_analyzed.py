#!/usr/bin/env python3
"""
Supabase Ingest Script for Grok-Analyzed UPSC PYQ Questions
Ingests the new two-tier analysis structure into Supabase
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
load_dotenv('../../../../.env')

# Database configuration - parse from SUPABASE_DB_URL
def parse_db_url():
    """Parse database URL to extract connection parameters"""
    db_url = os.getenv('SUPABASE_DB_URL')
    if not db_url:
        raise ValueError("SUPABASE_DB_URL not found in environment variables")
    
    # Parse: postgresql://user:password@host:port/database
    # Remove postgresql:// prefix
    url_without_prefix = db_url.replace('postgresql://', '')
    
    # Split into credentials and host/database
    credentials, host_db = url_without_prefix.split('@')
    user, password = credentials.split(':')
    
    # Split host/database
    host_port, database = host_db.split('/')
    if ':' in host_port:
        host, port = host_port.split(':')
    else:
        host = host_port
        port = '5432'
    
    return {
        'host': host,
        'database': database,
        'user': user,
        'password': password,
        'port': port
    }

DB_CONFIG = parse_db_url()

class GrokAnalyzedSupabaseIngester:
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
    
    def load_grok_analyzed_file(self, file_path: str) -> Dict[str, Any]:
        """Load Grok-analyzed JSON file and return data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return {}
    
    def validate_grok_analyzed_question(self, question: Dict[str, Any]) -> bool:
        """Validate Grok-analyzed question data structure"""
        required_fields = ['question_number', 'question_text', 'options']
        
        for field in required_fields:
            if field not in question:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check for Grok analysis structure
        if 'student_facing_analysis' not in question:
            print(f"❌ Missing student_facing_analysis for question {question.get('question_number', 'unknown')}")
            return False
        
        if 'detailed_backend_analysis' not in question:
            print(f"❌ Missing detailed_backend_analysis for question {question.get('question_number', 'unknown')}")
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
    
    def insert_grok_analyzed_question(self, question: Dict[str, Any], year: int) -> bool:
        """Insert a Grok-analyzed question into the database"""
        try:
            # Generate unique ID if not present
            if 'id' not in question:
                question['id'] = str(uuid.uuid4())
            
            # Extract student-facing analysis
            student_analysis = question.get('student_facing_analysis', {})
            detailed_analysis = question.get('detailed_backend_analysis', {})
            
            # Prepare the data
            question_data = {
                'id': question['id'],
                'question_number': question['question_number'],
                'year': year,
                'exam_type': 'UPSC',
                'exam_stage': 'Prelims',
                'question_text': question['question_text'],
                'question_type': question.get('type', 'mcq'),
                'difficulty': student_analysis.get('difficulty_level', question.get('difficulty', 'Medium')),
                'subject': detailed_analysis.get('primary_type', question.get('subject', 'General Studies')),
                'topic': detailed_analysis.get('secondary_type', None),
                'options': json.dumps(question['options']),
                'correct_answer': question.get('correct_answer', None),
                'exam_info': question.get('exam_info', f'Prelims {year}'),
                'paper': 'General Studies Paper I',
                'section': None,
                'source': 'Official',
                
                # Student-facing analysis (for frontend)
                'explanation': student_analysis.get('explanation', ''),
                'learning_objectives': student_analysis.get('learning_objectives', ''),
                'question_strategy': student_analysis.get('question_strategy', ''),
                'key_concepts': json.dumps(student_analysis.get('key_concepts', [])),
                'time_management': student_analysis.get('time_management', ''),
                
                # Detailed backend analysis (for LLM feedback)
                'detailed_analysis': json.dumps(detailed_analysis),
                'grok_analysis_date': question.get('grok_analysis_date', None)
            }
            
            # SQL query
            query = """
                INSERT INTO question_bank (
                    id, question_number, year, exam_type, exam_stage, question_text, 
                    question_type, difficulty, subject, topic, options, correct_answer,
                    exam_info, paper, section, source, explanation, learning_objectives,
                    question_strategy, key_concepts, time_management, detailed_analysis,
                    grok_analysis_date
                ) VALUES (
                    %(id)s, %(question_number)s, %(year)s, %(exam_type)s, %(exam_stage)s, %(question_text)s,
                    %(question_type)s, %(difficulty)s, %(subject)s, %(topic)s, %(options)s::jsonb, 
                    %(correct_answer)s, %(exam_info)s, %(paper)s, %(section)s, %(source)s,
                    %(explanation)s, %(learning_objectives)s, %(question_strategy)s, 
                    %(key_concepts)s::jsonb, %(time_management)s, %(detailed_analysis)s::jsonb,
                    %(grok_analysis_date)s
                ) ON CONFLICT (id) DO UPDATE SET
                    question_text = EXCLUDED.question_text,
                    question_type = EXCLUDED.question_type,
                    difficulty = EXCLUDED.difficulty,
                    subject = EXCLUDED.subject,
                    topic = EXCLUDED.topic,
                    options = EXCLUDED.options,
                    correct_answer = EXCLUDED.correct_answer,
                    explanation = EXCLUDED.explanation,
                    learning_objectives = EXCLUDED.learning_objectives,
                    question_strategy = EXCLUDED.question_strategy,
                    key_concepts = EXCLUDED.key_concepts,
                    time_management = EXCLUDED.time_management,
                    detailed_analysis = EXCLUDED.detailed_analysis,
                    grok_analysis_date = EXCLUDED.grok_analysis_date,
                    updated_at = NOW()
            """
            
            self.cursor.execute(query, question_data)
            return True
            
        except Exception as e:
            print(f"❌ Error inserting question {question.get('question_number', 'unknown')}: {e}")
            return False
    
    def ingest_grok_analyzed_year(self, year: int) -> bool:
        """Ingest Grok-analyzed questions for a specific year"""
        json_file = f"../json_files/upsc_prelims_{year}_grok_analyzed.json"
        
        if not os.path.exists(json_file):
            print(f"❌ Grok-analyzed JSON file not found: {json_file}")
            return False
        
        print(f"📁 Loading Grok-analyzed {year} data from {json_file}")
        data = self.load_grok_analyzed_file(json_file)
        
        if not data or 'questions' not in data:
            print(f"❌ Invalid JSON structure for {year}")
            return False
        
        questions = data['questions']
        print(f"📊 Found {len(questions)} Grok-analyzed questions for {year}")
        
        success_count = 0
        error_count = 0
        
        for question in tqdm(questions, desc=f"Processing Grok-analyzed {year}"):
            if self.validate_grok_analyzed_question(question):
                if self.insert_grok_analyzed_question(question, year):
                    success_count += 1
                else:
                    error_count += 1
            else:
                error_count += 1
        
        # Commit the transaction
        self.connection.commit()
        
        print(f"✅ {year}: {success_count} Grok-analyzed questions inserted, {error_count} errors")
        return error_count == 0
    
    def ingest_grok_analyzed_years(self, years: List[int] = [2024, 2025]) -> bool:
        """Ingest Grok-analyzed questions for specified years"""
        
        print("🚀 Starting Grok-Analyzed Supabase ingestion process")
        print("=" * 60)
        
        self.connect()
        
        try:
            all_success = True
            
            for year in years:
                print(f"\n📚 Processing UPSC {year} (Grok-analyzed)")
                print("-" * 40)
                
                success = self.ingest_grok_analyzed_year(year)
                if not success:
                    all_success = False
                    print(f"⚠️  Issues with {year} ingestion")
            
            if all_success:
                print("\n🎉 All Grok-analyzed years ingested successfully!")
                self.verify_grok_ingestion(years)
            else:
                print("\n⚠️  Some years had ingestion issues. Check logs above.")
            
            return all_success
            
        finally:
            self.disconnect()
    
    def verify_grok_ingestion(self, years: List[int]) -> Dict[str, Any]:
        """Verify the ingested Grok-analyzed data"""
        print("\n🔍 Verifying Grok-analyzed data ingestion...")
        print("=" * 50)
        
        try:
            # Check total questions by year
            for year in years:
                self.cursor.execute("""
                    SELECT COUNT(*) as count, 
                           COUNT(CASE WHEN explanation IS NOT NULL AND explanation != '' THEN 1 END) as with_explanation,
                           COUNT(CASE WHEN detailed_analysis IS NOT NULL THEN 1 END) as with_detailed_analysis
                    FROM question_bank 
                    WHERE year = %s AND exam_type = 'UPSC'
                """, (year,))
                
                result = self.cursor.fetchone()
                if result:
                    print(f"📊 UPSC {year}:")
                    print(f"   Total questions: {result['count']}")
                    print(f"   With explanations: {result['with_explanation']}")
                    print(f"   With detailed analysis: {result['with_detailed_analysis']}")
            
            # Check overall stats
            self.cursor.execute("""
                SELECT COUNT(*) as total_questions,
                       COUNT(CASE WHEN detailed_analysis IS NOT NULL THEN 1 END) as grok_analyzed
                FROM question_bank 
                WHERE exam_type = 'UPSC'
            """)
            
            result = self.cursor.fetchone()
            if result:
                print(f"\n📈 Overall Stats:")
                print(f"   Total UPSC questions: {result['total_questions']}")
                print(f"   Grok-analyzed questions: {result['grok_analyzed']}")
                print(f"   Analysis coverage: {(result['grok_analyzed']/result['total_questions']*100):.1f}%")
            
            return {"status": "success"}
            
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return {"status": "error", "message": str(e)}

def main():
    """Main function to run the Grok-analyzed ingestion"""
    
    print("🎯 Grok-Analyzed UPSC Questions Supabase Ingestion")
    print("=" * 60)
    
    ingester = GrokAnalyzedSupabaseIngester()
    
    # Ingest 2024 and 2025 Grok-analyzed questions
    success = ingester.ingest_grok_analyzed_years([2024, 2025])
    
    if success:
        print("\n✅ Grok-analyzed ingestion completed successfully!")
        print("🎉 Your PAI Mentor platform now has comprehensive question analysis!")
    else:
        print("\n❌ Grok-analyzed ingestion had issues. Check the logs above.")

if __name__ == "__main__":
    main() 