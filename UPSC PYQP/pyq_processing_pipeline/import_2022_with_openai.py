#!/usr/bin/env python3
"""
Script to import 2022 UPSC GS Prelims questions with OpenAI analysis into Supabase
"""

import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='../../.env')

class SupabaseImport2022:
    def __init__(self):
        self.connection = None
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_password = os.getenv('SUPABASE_PASSWORD')
        self.supabase_db = os.getenv('SUPABASE_DB', 'postgres')
        self.supabase_user = os.getenv('SUPABASE_USER', 'postgres')
        self.supabase_host = os.getenv('SUPABASE_HOST', 'db.supabase.co')
        self.supabase_port = os.getenv('SUPABASE_PORT', '5432')

    def connect(self):
        """Connect to Supabase PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=self.supabase_host,
                port=self.supabase_port,
                database=self.supabase_db,
                user=self.supabase_user,
                password=self.supabase_password
            )
            print("✅ Connected to Supabase database")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            raise

    def create_schema(self):
        """Create the table schema if it doesn't exist"""
        cursor = self.connection.cursor()
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS pyq_question_table (
            id SERIAL PRIMARY KEY,
            question_number VARCHAR(10),
            year INTEGER,
            section VARCHAR(100),
            question_text TEXT,
            options JSONB,
            correct_answer VARCHAR(10),
            explanation TEXT,
            motivation TEXT,
            difficulty_level VARCHAR(10),
            question_nature JSONB,
            source_material TEXT,
            source_type VARCHAR(50),
            test_series_reference TEXT,
            examiner_thought_process JSONB,
            learning_insights JSONB,
            options_analysis JSONB,
            openai_analysis_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            cursor.execute(create_table_sql)
            self.connection.commit()
            print("✅ Table schema created/verified")
        except Exception as e:
            print(f"❌ Error creating schema: {e}")
            raise
        finally:
            cursor.close()

    def clear_existing_questions(self):
        """Check if 2022 questions already exist"""
        print("🔍 Checking for existing 2022 questions...")
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM pyq_question_table WHERE year = 2022;")
        existing_count = cursor.fetchone()[0]
        cursor.close()
        
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing 2022 questions. Skipping deletion to preserve data.")
            return False
        else:
            print("✅ No existing 2022 questions found. Proceeding with import.")
            return True

    def import_questions(self, json_file_path: str):
        """Import questions from JSON file"""
        print(f"📖 Loading questions from {json_file_path}...")
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        questions = data.get('questions', [])
        print(f"📊 Found {len(questions)} questions to import")
        
        cursor = self.connection.cursor()
        imported_count = 0
        
        for question in questions:
            try:
                self.insert_question(cursor, question, 2022)
                imported_count += 1
                
                if imported_count % 10 == 0:
                    print(f"   ✅ Imported {imported_count}/{len(questions)} questions")
                    
            except Exception as e:
                print(f"❌ Error importing question {question.get('question_number', 'unknown')}: {e}")
                continue
        
        self.connection.commit()
        cursor.close()
        
        print(f"✅ Successfully imported {imported_count}/{len(questions)} questions")
        return imported_count

    def insert_question(self, cursor, question: dict, year: int):
        """Insert a single question into the database"""
        
        def truncate_field(value, max_length):
            """Truncate field if it exceeds max length"""
            if value and len(str(value)) > max_length:
                return str(value)[:max_length-3] + "..."
            return value
        
        # Extract OpenAI analysis fields
        examiner_thought_process = question.get('examiner_thought_process', {})
        learning_insights = question.get('learning_insights', {})
        options_analysis = question.get('options_analysis', {})
        question_nature = question.get('question_nature', {})
        
        # Parse OpenAI analysis date
        openai_date = None
        if question.get('openai_analysis_date'):
            try:
                openai_date = datetime.fromisoformat(question['openai_analysis_date'].replace('Z', '+00:00'))
            except:
                openai_date = datetime.now()
        
        insert_sql = """
        INSERT INTO pyq_question_table (
            question_number, year, section, question_text, options, correct_answer,
            explanation, motivation, difficulty_level, question_nature, source_material,
            source_type, test_series_reference, examiner_thought_process, learning_insights,
            options_analysis, openai_analysis_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_sql, (
            question.get('question_number'),
            year,
            truncate_field(question.get('section'), 100),
            question.get('question_text'),
            json.dumps(question.get('options', {})),
            question.get('correct_answer'),
            question.get('explanation'),
            question.get('motivation'),
            question.get('difficulty_level'),
            json.dumps(question_nature),
            question.get('source_material'),
            question.get('source_type'),
            question.get('test_series_reference'),
            json.dumps(examiner_thought_process),
            json.dumps(learning_insights),
            json.dumps(options_analysis),
            openai_date
        ))

    def verify_import(self):
        """Verify the import by counting questions"""
        cursor = self.connection.cursor()
        
        # Count total questions for 2022
        cursor.execute("SELECT COUNT(*) FROM pyq_question_table WHERE year = 2022;")
        total_count = cursor.fetchone()[0]
        
        # Count questions with OpenAI analysis
        cursor.execute("""
            SELECT COUNT(*) FROM pyq_question_table 
            WHERE year = 2022 AND examiner_thought_process IS NOT NULL 
            AND examiner_thought_process != '{}';
        """)
        openai_count = cursor.fetchone()[0]
        
        # Get sample questions
        cursor.execute("""
            SELECT question_number, section, examiner_thought_process 
            FROM pyq_question_table 
            WHERE year = 2022 
            LIMIT 3;
        """)
        sample_questions = cursor.fetchall()
        
        cursor.close()
        
        print(f"\n📊 IMPORT VERIFICATION:")
        print(f"   Total 2022 questions: {total_count}")
        print(f"   Questions with OpenAI analysis: {openai_count}")
        
        if sample_questions:
            print(f"\n📝 Sample imported questions:")
            for q in sample_questions:
                has_analysis = "✅" if q[2] and q[2] != {} else "❌"
                print(f"   Q{q[0]} ({q[1]}) - OpenAI Analysis: {has_analysis}")

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("🔌 Database connection closed")

def main():
    """Main function to run the import"""
    
    # Check environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set these in your .env file")
        return
    
    # Initialize importer
    importer = SupabaseImport2022()
    
    try:
        # Connect to database
        importer.connect()
        
        # Create schema
        importer.create_schema()
        
        # Check for existing 2022 questions
        should_import = importer.clear_existing_questions()
        
        if should_import:
            # Import questions
            json_file = "GS Prelims 2022_WITH_OPENAI_ANALYSIS.json"
            imported_count = importer.import_questions(json_file)
        else:
            print("⏭️  Skipping import since 2022 questions already exist in database")
            imported_count = 0
        
        # Verify import
        importer.verify_import()
        
        print(f"\n🎉 SUCCESS! Imported {imported_count} 2022 questions with OpenAI analysis")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        raise
    finally:
        importer.close()

if __name__ == "__main__":
    main() 