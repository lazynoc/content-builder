import json
import os
import time
from typing import Dict, List, Any
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid

# Load environment variables
load_dotenv(dotenv_path='../../.env')

class PyqTableImport:
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
    
    def check_existing_questions(self):
        """Check if questions already exist for 2024"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM pyq_question_table WHERE year = 2024")
            result = cursor.fetchone()
            count = result[0] if result else 0
            cursor.close()
            
            print(f"📊 Found {count} existing questions for 2024")
            return count
            
        except Exception as e:
            print(f"❌ Error checking existing questions: {e}")
            return 0
    
    def import_2024_questions(self, json_file_path: str):
        """Import 2024 questions with enhanced analysis"""
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
            updated_count = 0
            
            for question in questions:
                try:
                    # Check only core required fields
                    question_number = question.get('question_number')
                    question_text = question.get('question_text', '').strip()
                    correct_answer = question.get('correct_answer', '').strip()
                    options = question.get('options', {})
                    
                    # Skip if core fields are missing
                    if not question_number or not question_text or not correct_answer or not options:
                        print(f"⚠️  Skipping question {question.get('question_number', 'unknown')}: Missing core fields")
                        skipped_count += 1
                        continue
                    
                    # Skip if correct_answer is invalid
                    if correct_answer not in ['A', 'B', 'C', 'D']:
                        print(f"⚠️  Skipping question {question.get('question_number', 'unknown')}: Invalid correct_answer '{correct_answer}'")
                        skipped_count += 1
                        continue
                    
                    # Check if question already exists
                    cursor.execute("SELECT id FROM pyq_question_table WHERE year = %s AND question_number = %s", 
                                 (2024, str(question_number)))
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update existing question
                        self.update_question(cursor, question, existing[0])
                        updated_count += 1
                    else:
                        # Insert new question
                        self.insert_question(cursor, question)
                        imported_count += 1
                    
                    if (imported_count + updated_count) % 10 == 0:
                        print(f"  ✅ Processed {imported_count + updated_count}/{len(questions)} questions")
                        self.connection.commit()
                        
                except Exception as e:
                    print(f"❌ Error processing question {question.get('question_number', 'unknown')}: {e}")
                    continue
            
            self.connection.commit()
            cursor.close()
            
            print(f"🎉 Import completed!")
            print(f"   Questions imported: {imported_count}")
            print(f"   Questions updated: {updated_count}")
            print(f"   Questions skipped: {skipped_count}")
            
        except Exception as e:
            print(f"❌ Error during import: {e}")
            if self.connection:
                self.connection.rollback()
            raise
    
    def insert_question(self, cursor, question: Dict[str, Any]):
        """Insert a new question with all enhanced analysis"""
        
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
        
        # Prepare arrays for TEXT[] fields
        key_concepts = learning_insights.get('key_concepts', [])
        common_mistakes = learning_insights.get('common_mistakes', [])
        memory_hooks = learning_insights.get('memory_hooks', [])
        related_topics = learning_insights.get('related_topics', [])
        
        # Insert question with all data
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
            str(question.get('question_number')),
            2024,  # Year
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
            key_concepts,  # TEXT[] array
            common_mistakes,  # TEXT[] array
            learning_insights.get('elimination_technique'),
            memory_hooks,  # TEXT[] array
            related_topics,  # TEXT[] array
            learning_insights.get('current_affairs_connection'),
            question.get('time_management'),
            question.get('confidence_calibration'),
            question.get('source_material', ''),
            truncate_field(question.get('source_type', ''), 100),
            question.get('test_series_reference', ''),
            question.get('extraction_order'),
            question.get('chunk_number'),
            tags,  # TEXT[] array
            question.get('motivation'),
            json.dumps(examiner_thought),  # Full examiner thought process as JSON
            json.dumps(learning_insights),  # Full learning insights as JSON
            question.get('openai_analysis_date')
        ))
    
    def update_question(self, cursor, question: Dict[str, Any], question_id):
        """Update an existing question with new analysis data"""
        
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
        
        # Prepare arrays for TEXT[] fields
        key_concepts = learning_insights.get('key_concepts', [])
        common_mistakes = learning_insights.get('common_mistakes', [])
        memory_hooks = learning_insights.get('memory_hooks', [])
        related_topics = learning_insights.get('related_topics', [])
        
        # Update question with enhanced analysis
        cursor.execute("""
            UPDATE pyq_question_table SET
                section = %s, question_text = %s, correct_answer = %s, explanation = %s,
                options = %s, primary_type = %s, secondary_type = %s, difficulty_level = %s,
                difficulty_reason = %s, knowledge_requirement = %s, testing_objective = %s,
                question_design_strategy = %s, trap_setting = %s, discrimination_potential = %s,
                options_analysis = %s, key_concepts = %s, common_mistakes = %s, elimination_technique = %s,
                memory_hooks = %s, related_topics = %s, current_affairs_connection = %s,
                time_management = %s, confidence_calibration = %s, source_material = %s,
                source_type = %s, test_series_reference = %s, tags = %s, updated_at = NOW()
            WHERE id = %s
        """, (
            truncate_field(question.get('section', 'General Studies'), 100),
            question.get('question_text', ''),
            question.get('correct_answer', ''),
            question.get('explanation', ''),
            json.dumps(question.get('options', {})),
            truncate_field(question_nature.get('primary_type'), 50),
            truncate_field(question_nature.get('secondary_type'), 50),
            truncate_field(question.get('difficulty_level'), 20),
            question_nature.get('difficulty_reason'),
            truncate_field(question_nature.get('knowledge_requirement'), 100),
            examiner_thought.get('testing_objective'),
            examiner_thought.get('question_design_strategy'),
            examiner_thought.get('trap_setting'),
            examiner_thought.get('discrimination_potential'),
            json.dumps(options_analysis),
            key_concepts,
            common_mistakes,
            learning_insights.get('elimination_technique'),
            memory_hooks,
            related_topics,
            learning_insights.get('current_affairs_connection'),
            question.get('time_management'),
            question.get('confidence_calibration'),
            question.get('source_material', ''),
            truncate_field(question.get('source_type', ''), 100),
            question.get('test_series_reference', ''),
            tags,
            question_id
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
    """Main function to import data into pyq_question_table"""
    
    # Check environment variables
    if not os.getenv('SUPABASE_DB_URL'):
        print("❌ Please set SUPABASE_DB_URL environment variable")
        print("   Format: postgresql://username:password@host:port/database")
        return 1
    
    importer = None
    try:
        print("🚀 Starting 2024 UPSC Questions Import (pyq_question_table)...")
        print("=" * 60)
        
        # Initialize importer
        importer = PyqTableImport()
        
        # Check existing questions
        existing_count = importer.check_existing_questions()
        
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing questions for 2024")
            print("   The script will update existing questions and add new ones.")
        
        # Import 2024 questions
        print("\n📥 Importing 2024 questions...")
        importer.import_2024_questions('GS Prelims 2024_WITH_OPENAI_ANALYSIS.json')
        
        # Verify import
        print("\n🔍 Verifying import...")
        importer.verify_import()
        
        print("\n" + "=" * 60)
        print("🎉 Import completed successfully!")
        print("   Your 2024 UPSC GS Prelims questions are now in pyq_question_table.")
        print("   You can use this data for your mock test application.")
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        print("   Please check your database connection and try again.")
        return 1
    
    finally:
        if importer:
            importer.close()
    
    return 0

if __name__ == "__main__":
    main() 