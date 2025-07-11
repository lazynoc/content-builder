import json
import os
import time
from typing import Dict, List, Any
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import argparse

# Load environment variables
load_dotenv(dotenv_path='../../.env')

class SimpleSupabaseImport:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Connect to Supabase PostgreSQL database"""
        try:
            # Get connection details from environment variables
            db_url = os.getenv('SUPABASE_DB_URL')
            if not db_url:
                raise ValueError("SUPABASE_DB_URL environment variable not set")
            
            self.connection = psycopg2.connect(db_url)
            print("✅ Connected to Supabase database")
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def create_schema(self):
        """Create the database schema"""
        try:
            print("🔧 Creating database schema...")
            
            # Check if connection exists
            if not self.connection:
                raise RuntimeError("Database connection is not established.")
            
            with open('simple_supabase_schema.sql', 'r') as f:
                sql_content = f.read()
            
            cursor = self.connection.cursor()
            cursor.execute(sql_content)
            self.connection.commit()
            cursor.close()
            
            print("✅ Database schema created successfully")
            
        except Exception as e:
            print(f"❌ Error creating schema: {e}")
            if self.connection:
                self.connection.rollback()
            raise
    
    def clear_existing_questions(self, year=None):
        """Delete questions of the specified year from the table"""
        if year is None:
            print("🧹 Deleting existing 2023 and 2024 questions from pyq_question_table...")
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM pyq_question_table WHERE year IN (2023, 2024);")
            self.connection.commit()
            cursor.close()
            print("✅ Existing 2023 and 2024 questions deleted.")
        else:
            print(f"🧹 Deleting existing {year} questions from pyq_question_table...")
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM pyq_question_table WHERE year = %s;", (year,))
            self.connection.commit()
            cursor.close()
            print(f"✅ Existing {year} questions deleted.")

    def import_questions(self, json_file_path: str, year: int, clear_existing=True):
        if clear_existing:
            self.clear_existing_questions(year)
        try:
            print(f"📥 Importing questions from {json_file_path}...")
            # Load questions data
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            questions = data.get('questions', [])
            print(f"Found {len(questions)} questions to import")
            if not self.connection:
                raise RuntimeError("Database connection is not established.")
            cursor = self.connection.cursor()
            imported_count = 0
            skipped_count = 0
            for question in questions:
                try:
                    question_number = question.get('question_number')
                    question_text = question.get('question_text', '').strip()
                    correct_answer = question.get('correct_answer', '').strip()
                    options = question.get('options', {})
                    if not question_number or not question_text or not correct_answer or not options:
                        print(f"⚠️  Skipping question {question.get('question_number', 'unknown')}: Missing core fields")
                        skipped_count += 1
                        continue
                    if correct_answer not in ['A', 'B', 'C', 'D']:
                        print(f"⚠️  Skipping question {question.get('question_number', 'unknown')}: Invalid correct_answer '{correct_answer}'")
                        skipped_count += 1
                        continue
                    self.insert_question_simple(cursor, question, year)
                    imported_count += 1
                    if imported_count % 10 == 0:
                        print(f"  ✅ Imported {imported_count}/{len(questions)} questions")
                        self.connection.commit()
                except Exception as e:
                    print(f"❌ Error importing question {question.get('question_number', 'unknown')}: {e}")
                    continue
            self.connection.commit()
            cursor.close()
            print(f"🎉 Import completed!")
            print(f"   Questions imported: {imported_count}")
            print(f"   Questions skipped: {skipped_count}")
        except Exception as e:
            print(f"❌ Error importing questions: {e}")
            if self.connection:
                self.connection.rollback()
            raise

    def insert_question_simple(self, cursor, question: dict, year: int):
        """Insert a single question with all enhanced analysis"""
        
        # Extract enhanced analysis data
        question_nature = question.get('question_nature', {})
        examiner_thought = question.get('examiner_thought_process', {})
        learning_insights = question.get('learning_insights', {})
        options_analysis = question.get('options_analysis', {})
        
        # Truncate fields that might exceed VARCHAR limits
        def truncate_field(value, max_length):
            if value and len(str(value)) > max_length:
                return str(value)[:max_length]
            return value
        
        # Prepare tags
        tags = []
        if question_nature.get('primary_type'):
            tags.append(question_nature['primary_type'])
        if question_nature.get('secondary_type'):
            tags.append(question_nature['secondary_type'])
        if question.get('difficulty_level'):
            tags.append(question['difficulty_level'])
        if question.get('section'):
            tags.append(question['section'])
        
        # Insert question with all data in one row
        cursor.execute("""
            INSERT INTO pyq_question_table (
                question_number, year, section, question_text, correct_answer,
                explanation, options, primary_type, secondary_type, difficulty_level,
                difficulty_reason, knowledge_requirement, testing_objective,
                question_design_strategy, trap_setting, discrimination_potential,
                options_analysis, key_concepts, common_mistakes, elimination_technique,
                memory_hooks, related_topics, current_affairs_connection,
                time_management, confidence_calibration, source_material,
                source_type, test_series_reference, extraction_order, chunk_number, tags,
                motivation, examiner_thought_process, learning_insights, openai_analysis_date
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s
            )
        """, (
            question.get('question_number'),
            year,  # Year
            truncate_field(question.get('section', 'General Studies'), 100),
            question.get('question_text', ''),
            question.get('correct_answer', ''),
            question.get('explanation', ''),
            json.dumps(question.get('options', {})),  # Options as JSON
            truncate_field(question_nature.get('primary_type'), 50),
            truncate_field(question_nature.get('secondary_type'), 50),
            truncate_field(question.get('difficulty_level'), 20),
            question_nature.get('difficulty_reason'),
            truncate_field(question_nature.get('knowledge_requirement'), 100),
            examiner_thought.get('testing_objective'),
            examiner_thought.get('question_design_strategy'),
            examiner_thought.get('trap_setting'),
            examiner_thought.get('discrimination_potential'),
            json.dumps(options_analysis),  # Options analysis as JSON
            json.dumps(learning_insights.get('key_concepts', [])),  # Key concepts as JSONB
            json.dumps(learning_insights.get('common_mistakes', [])),  # Common mistakes as JSONB
            learning_insights.get('elimination_technique'),
            json.dumps(learning_insights.get('memory_hooks', [])),  # Memory hooks as JSONB
            json.dumps(learning_insights.get('related_topics', [])),  # Related topics as JSONB
            learning_insights.get('current_affairs_connection'),
            question.get('time_management'),
            question.get('confidence_calibration'),
            question.get('source_material', ''),
            truncate_field(question.get('source_type', ''), 100),
            question.get('test_series_reference', ''),
            question.get('extraction_order'),
            question.get('chunk_number'),
            json.dumps(tags),  # Tags as JSONB
            question.get('motivation'),
            json.dumps(examiner_thought),  # Full examiner thought process as JSON
            json.dumps(learning_insights),  # Full learning insights as JSON
            question.get('openai_analysis_date')
        ))
    
    def verify_import(self):
        """Verify the import by checking counts and sample data"""
        try:
            if not self.connection:
                raise RuntimeError("Database connection is not established.")
            
            cursor = self.connection.cursor()
            
            # Check questions count
            cursor.execute("SELECT COUNT(*) FROM pyq_question_table WHERE year = 2024")
            result = cursor.fetchone()
            questions_count = result[0] if result else 0
            
            # Check sections
            cursor.execute("""
                SELECT section, COUNT(*) FROM pyq_question_table 
                WHERE year = 2024 
                GROUP BY section
            """)
            sections = cursor.fetchall()
            
            # Check difficulty distribution
            cursor.execute("""
                SELECT difficulty_level, COUNT(*) FROM pyq_question_table 
                WHERE year = 2024 
                GROUP BY difficulty_level
            """)
            difficulties = cursor.fetchall()
            
            # Check question types
            cursor.execute("""
                SELECT primary_type, COUNT(*) FROM pyq_question_table 
                WHERE year = 2024 
                GROUP BY primary_type
            """)
            types = cursor.fetchall()
            
            # Sample question
            cursor.execute("""
                SELECT question_number, question_text, options, difficulty_level, primary_type
                FROM pyq_question_table WHERE year = 2024 LIMIT 1
            """)
            sample = cursor.fetchone()
            
            cursor.close()
            
            print(f"\n📊 Import Verification:")
            print(f"   Questions in database: {questions_count}")
            print(f"   Sections:")
            for section, count in sections:
                print(f"     {section}: {count} questions")
            print(f"   Difficulty levels:")
            for difficulty, count in difficulties:
                print(f"     {difficulty}: {count} questions")
            print(f"   Question types:")
            for qtype, count in types:
                print(f"     {qtype}: {count} questions")
            
            if sample:
                print(f"\n📝 Sample question:")
                print(f"   Q{sample[0]}: {sample[1][:100]}...")
                print(f"   Options: {sample[2]}")
                print(f"   Difficulty: {sample[3]}, Type: {sample[4]}")
            
        except Exception as e:
            print(f"❌ Error during verification: {e}")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("🔌 Database connection closed")

def main():
    parser = argparse.ArgumentParser(description="Import UPSC GS Prelims questions into Supabase.")
    parser.add_argument('--json', required=True, help='Path to the JSON file')
    parser.add_argument('--year', required=True, type=int, help='Year to assign to imported questions')
    parser.add_argument('--clear_existing', default='True', help='Whether to clear existing questions (True/False)')
    args = parser.parse_args()

    clear_existing = args.clear_existing.lower() == 'true'
    importer = SimpleSupabaseImport()
    importer.create_schema()
    importer.import_questions(args.json, args.year, clear_existing)
    importer.verify_import()
    importer.close()

if __name__ == "__main__":
    main()