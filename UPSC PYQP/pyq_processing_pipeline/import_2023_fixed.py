#!/usr/bin/env python3
"""
Import script for 2023 UPSC GS Prelims questions with fixed options
Clears existing 2023 questions and imports all 100 questions
"""

import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('/Users/shahrukhmalik/Documents/GitHub/UPSC BOOKS/.env')

class FixedSupabaseImport:
    def __init__(self):
        self.connection = None
        self.supabase_url = os.getenv('SUPABASE_DB_URL')
        
        if not self.supabase_url:
            print("❌ Error: SUPABASE_DB_URL environment variable must be set")
            sys.exit(1)

    def connect(self):
        """Connect to Supabase PostgreSQL database"""
        try:
            # Extract host, port, database from SUPABASE_URL
            # Format: postgresql://postgres:[password]@[host]:[port]/postgres
            url_parts = self.supabase_url.replace('postgresql://', '').split('@')
            credentials = url_parts[0].split(':')
            host_port_db = url_parts[1].split('/')
            host_port = host_port_db[0].split(':')
            
            host = host_port[0]
            port = host_port[1] if len(host_port) > 1 else '5432'
            database = host_port_db[1] if len(host_port_db) > 1 else 'postgres'
            user = credentials[0]
            password = credentials[1]
            
            self.connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            print("✅ Connected to Supabase PostgreSQL database")
            
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            sys.exit(1)

    def create_schema(self):
        """Create the table schema if it doesn't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Create the table with JSONB fields for list-like data
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS pyq_question_table (
                id SERIAL PRIMARY KEY,
                question_number INTEGER NOT NULL,
                year INTEGER NOT NULL,
                section VARCHAR(100),
                question_text TEXT NOT NULL,
                correct_answer VARCHAR(10),
                explanation TEXT,
                motivation TEXT,
                difficulty_level VARCHAR(50),
                question_nature JSONB,
                source_material TEXT,
                source_type VARCHAR(50),
                test_series_reference TEXT,
                options JSONB,
                options_extracted BOOLEAN,
                processing_date TIMESTAMP,
                examiner_thought_process JSONB,
                options_analysis JSONB,
                learning_insights JSONB,
                time_management TEXT,
                confidence_calibration TEXT,
                openai_analysis_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            cursor.execute(create_table_sql)
            self.connection.commit()
            print("✅ Table schema created/verified")
            cursor.close()
            
        except Exception as e:
            print(f"❌ Error creating schema: {e}")
            sys.exit(1)

    def clear_existing_questions(self):
        """Delete all 2023 and 2024 questions from the table"""
        print("🧹 Deleting existing 2023 and 2024 questions from pyq_question_table...")
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM pyq_question_table WHERE year IN (2023, 2024);")
        self.connection.commit()
        cursor.close()
        print("✅ Existing 2023 and 2024 questions deleted.")

    def import_2023_questions(self, json_file_path: str, clear_existing=True):
        """Import 2023 questions from the original JSON file"""
        if clear_existing:
            self.clear_existing_questions()
        try:
            print(f"📖 Loading questions from {json_file_path}...")
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            questions = data.get('questions', [])
            total_questions = len(questions)
            print(f"📊 Found {total_questions} questions to import")
            
            # Clear existing 2023 questions
            print("🧹 Clearing existing 2023 questions...")
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM pyq_question_table WHERE year = 2023;")
            deleted_count = cursor.rowcount
            self.connection.commit()
            cursor.close()
            print(f"🗑️  Deleted {deleted_count} existing 2023 questions")
            
            # Import questions
            imported_count = 0
            skipped_count = 0
            skipped_questions = []
            
            for question in questions:
                try:
                    if self.insert_question_fixed(cursor, question):
                        imported_count += 1
                    else:
                        skipped_count += 1
                        skipped_questions.append(question.get('question_number', 'Unknown'))
                except Exception as e:
                    print(f"❌ Error importing question {question.get('question_number', 'Unknown')}: {e}")
                    skipped_count += 1
                    skipped_questions.append(question.get('question_number', 'Unknown'))
            
            print(f"\n📈 Import Summary:")
            print(f"   ✅ Successfully imported: {imported_count}")
            print(f"   ⏭️  Skipped: {skipped_count}")
            
            if skipped_questions:
                print(f"   📝 Skipped question numbers: {', '.join(map(str, skipped_questions))}")
            
            return imported_count, skipped_count, skipped_questions
            
        except Exception as e:
            print(f"❌ Error importing questions: {e}")
            return 0, 0, []

    def insert_question_fixed(self, cursor, question: Dict[str, Any]) -> bool:
        """Insert a single question with proper data handling"""
        try:
            # Validate required fields
            required_fields = ['question_number', 'question_text', 'correct_answer']
            for field in required_fields:
                if not question.get(field):
                    print(f"⚠️  Question {question.get('question_number', 'Unknown')} missing {field}")
                    return False
            
            # Prepare data with proper handling of JSONB fields
            insert_data = {
                'question_number': int(question['question_number']),
                'year': 2023,
                'section': question.get('section', ''),
                'question_text': question['question_text'],
                'correct_answer': question['correct_answer'],
                'explanation': question.get('explanation', ''),
                'motivation': question.get('motivation', ''),
                'difficulty_level': question.get('difficulty_level', ''),
                'question_nature': json.dumps(question.get('question_nature', {})),
                'source_material': question.get('source_material', ''),
                'source_type': question.get('source_type', ''),
                'test_series_reference': question.get('test_series_reference', ''),
                'options': json.dumps(question.get('options', {})),
                'options_extracted': question.get('options_extracted', False),
                'processing_date': question.get('processing_date'),
                'examiner_thought_process': json.dumps(question.get('examiner_thought_process', {})),
                'options_analysis': json.dumps(question.get('options_analysis', {})),
                'learning_insights': json.dumps(question.get('learning_insights', {})),
                'time_management': question.get('time_management', ''),
                'confidence_calibration': question.get('confidence_calibration', ''),
                'openai_analysis_date': question.get('openai_analysis_date')
            }
            
            # Truncate text fields if too long
            def truncate_field(value, max_length):
                if value and len(str(value)) > max_length:
                    return str(value)[:max_length-3] + "..."
                return value
            
            insert_data['question_text'] = truncate_field(insert_data['question_text'], 5000)
            insert_data['explanation'] = truncate_field(insert_data['explanation'], 5000)
            insert_data['motivation'] = truncate_field(insert_data['motivation'], 1000)
            insert_data['source_material'] = truncate_field(insert_data['source_material'], 1000)
            insert_data['test_series_reference'] = truncate_field(insert_data['test_series_reference'], 1000)
            insert_data['time_management'] = truncate_field(insert_data['time_management'], 500)
            insert_data['confidence_calibration'] = truncate_field(insert_data['confidence_calibration'], 500)
            
            # Insert the question
            cursor = self.connection.cursor()
            insert_sql = """
            INSERT INTO pyq_question_table (
                question_number, year, section, question_text, correct_answer, 
                explanation, motivation, difficulty_level, question_nature, 
                source_material, source_type, test_series_reference, options, 
                options_extracted, processing_date, examiner_thought_process, 
                options_analysis, learning_insights, time_management, 
                confidence_calibration, openai_analysis_date
            ) VALUES (
                %(question_number)s, %(year)s, %(section)s, %(question_text)s, %(correct_answer)s,
                %(explanation)s, %(motivation)s, %(difficulty_level)s, %(question_nature)s,
                %(source_material)s, %(source_type)s, %(test_series_reference)s, %(options)s,
                %(options_extracted)s, %(processing_date)s, %(examiner_thought_process)s,
                %(options_analysis)s, %(learning_insights)s, %(time_management)s,
                %(confidence_calibration)s, %(openai_analysis_date)s
            )
            """
            
            cursor.execute(insert_sql, insert_data)
            self.connection.commit()
            cursor.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Error inserting question {question.get('question_number', 'Unknown')}: {e}")
            return False

    def verify_import(self):
        """Verify the import by counting questions"""
        try:
            cursor = self.connection.cursor()
            
            # Count total questions
            cursor.execute("SELECT COUNT(*) FROM pyq_question_table;")
            total_count = cursor.fetchone()[0]
            
            # Count 2023 questions
            cursor.execute("SELECT COUNT(*) FROM pyq_question_table WHERE year = 2023;")
            count_2023 = cursor.fetchone()[0]
            
            # Count 2024 questions
            cursor.execute("SELECT COUNT(*) FROM pyq_question_table WHERE year = 2024;")
            count_2024 = cursor.fetchone()[0]
            
            # Check for questions with missing options
            cursor.execute("""
                SELECT question_number, year 
                FROM pyq_question_table 
                WHERE options = '{}' OR options IS NULL;
            """)
            missing_options = cursor.fetchall()
            
            cursor.close()
            
            print(f"\n📊 Database Verification:")
            print(f"   📈 Total questions: {total_count}")
            print(f"   📅 2023 questions: {count_2023}")
            print(f"   📅 2024 questions: {count_2024}")
            
            if missing_options:
                print(f"   ⚠️  Questions with missing options: {len(missing_options)}")
                for q_num, year in missing_options:
                    print(f"      - Q{q_num} ({year})")
            else:
                print(f"   ✅ All questions have options")
            
            return count_2023, count_2024, missing_options
            
        except Exception as e:
            print(f"❌ Error verifying import: {e}")
            return 0, 0, []

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("🔌 Database connection closed")

def main():
    """Main function to run the import"""
    print("🚀 Starting 2023 UPSC questions import (ORIGINAL FILE)...")
    
    # Initialize importer
    importer = FixedSupabaseImport()
    
    try:
        # Connect to database
        importer.connect()
        
        # Create schema
        importer.create_schema()
        
        # Import 2023 questions from original file
        json_file = "GS Prelims 2023_WITH_OPENAI_ANALYSIS.json"
        
        if not os.path.exists(json_file):
            print(f"❌ Error: {json_file} not found!")
            print("Please run the fix_2023_missing_options.py script first")
            return
        
        imported, skipped, skipped_list = importer.import_2023_questions(json_file)
        
        # Verify import
        count_2023, count_2024, missing_options = importer.verify_import()
        
        print(f"\n🎉 Import completed!")
        print(f"📊 Final status:")
        print(f"   ✅ 2023 questions in database: {count_2023}")
        print(f"   ✅ 2024 questions in database: {count_2024}")
        print(f"   📈 Total questions: {count_2023 + count_2024}")
        
        if count_2023 == 100:
            print("🎯 SUCCESS: All 100 2023 questions imported!")
        else:
            print(f"⚠️  WARNING: Only {count_2023}/100 2023 questions imported")
        
    except Exception as e:
        print(f"❌ Error during import: {e}")
    
    finally:
        importer.close()

if __name__ == "__main__":
    main() 