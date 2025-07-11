import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MissingQuestionsImporter:
    def __init__(self):
        self.connection = None
    
    def connect(self):
        """Connect to Supabase PostgreSQL database"""
        try:
            db_url = os.getenv('SUPABASE_DB_URL')
            if not db_url:
                raise ValueError("SUPABASE_DB_URL environment variable not set")
            
            self.connection = psycopg2.connect(db_url)
            print("✅ Connected to Supabase database")
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def import_missing_questions(self, json_file_path: str):
        """Import only the missing questions (22, 25, 66, 84, etc.)"""
        try:
            if not self.connection:
                raise RuntimeError("Database connection is not established.")
            
            # Load JSON data
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Extract questions array from the JSON structure
            questions_data = data.get('questions', [])
            
            # Filter for missing questions
            missing_question_numbers = [22, 25, 66, 84]  # Add any others that failed
            questions_to_import = []
            
            for question in questions_data:
                if question.get('question_number') in missing_question_numbers:
                    questions_to_import.append(question)
            
            print(f"📥 Found {len(questions_to_import)} missing questions to import")
            
            cursor = self.connection.cursor()
            imported_count = 0
            
            for question in questions_to_import:
                try:
                    self.insert_question_simple(cursor, question)
                    imported_count += 1
                    print(f"✅ Imported question {question.get('question_number')}")
                    
                except Exception as e:
                    print(f"❌ Error importing question {question.get('question_number')}: {e}")
                    self.connection.rollback()
                    continue
            
            self.connection.commit()
            cursor.close()
            
            print(f"\n🎉 Missing questions import completed!")
            print(f"   Questions imported: {imported_count}")
            print(f"   Questions attempted: {len(questions_to_import)}")
            
        except Exception as e:
            print(f"❌ Error during import: {e}")
            if self.connection:
                self.connection.rollback()
            raise
    
    def insert_question_simple(self, cursor, question: Dict[str, Any]):
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
            json.dumps(learning_insights.get('key_concepts', [])),  # Key concepts as JSON
            json.dumps(learning_insights.get('common_mistakes', [])),  # Common mistakes as JSON
            learning_insights.get('elimination_technique'),
            json.dumps(learning_insights.get('memory_hooks', [])),  # Memory hooks as JSON
            json.dumps(learning_insights.get('related_topics', [])),  # Related topics as JSON
            learning_insights.get('current_affairs_connection'),
            question.get('time_management'),
            question.get('confidence_calibration'),
            question.get('source_material', ''),
            truncate_field(question.get('source_type', ''), 100),
            question.get('test_series_reference', ''),
            question.get('extraction_order'),
            question.get('chunk_number'),
            json.dumps(tags),  # Tags as JSON
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
            
            # Check specific missing questions
            cursor.execute("""
                SELECT question_number FROM pyq_question_table 
                WHERE year = 2024 AND question_number IN (22, 25, 66, 84)
                ORDER BY question_number
            """)
            imported_missing = [row[0] for row in cursor.fetchall()]
            
            cursor.close()
            
            print(f"\n📊 Import Verification:")
            print(f"   Total questions in database: {questions_count}")
            print(f"   Previously missing questions now imported: {imported_missing}")
            
        except Exception as e:
            print(f"❌ Error during verification: {e}")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("🔌 Database connection closed")

def main():
    """Main function to import missing questions"""
    
    # Check environment variables
    if not os.getenv('SUPABASE_DB_URL'):
        print("❌ Please set SUPABASE_DB_URL environment variable")
        print("   Format: postgresql://username:password@host:port/database")
        return
    
    importer = None
    try:
        # Initialize importer
        importer = MissingQuestionsImporter()
        
        # Connect to database
        importer.connect()
        
        # Import missing questions
        print("\n📥 Importing missing questions...")
        importer.import_missing_questions('GS Prelims 2024_WITH_OPENAI_ANALYSIS.json')
        
        # Verify import
        print("\n🔍 Verifying import...")
        importer.verify_import()
        
        print("\n🎉 Missing questions import completed successfully!")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
    
    finally:
        if importer:
            importer.close()

if __name__ == "__main__":
    main() 