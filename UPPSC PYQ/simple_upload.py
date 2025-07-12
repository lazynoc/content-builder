#!/usr/bin/env python3
"""
Simple upload script with only essential fields
"""
import json
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from parent directory
load_dotenv('../.env')
DB_URL = os.getenv('SUPABASE_DB_URL')

def upload_to_supabase():
    with open('uppsc_questions_complete_enhanced.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    questions = data['questions']
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    print(f"📤 UPLOADING {len(questions)} UPPSC QUESTIONS (ESSENTIAL FIELDS ONLY)")
    print("=" * 60)
    success_count = 0
    error_count = 0
    
    for i, question in enumerate(questions, 1):
        try:
            # Essential fields only
            question_number = str(question.get('question_number'))
            year = int(question.get('year', 2024))
            section = question.get('section', 'UPPSC_Prelims_GS1')
            question_text = question.get('question_text')
            correct_answer = question.get('correct_answer')
            explanation = question.get('explanation')
            options = question.get('options')
            exam_type = question.get('exam_type', 'UPPSC')
            
            insert_query = """
            INSERT INTO pyq_question_table (
                question_number, year, section, question_text, correct_answer, 
                explanation, options, exam_type
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (year, question_number, exam_type)
            DO UPDATE SET
                question_text = EXCLUDED.question_text,
                correct_answer = EXCLUDED.correct_answer,
                explanation = EXCLUDED.explanation,
                options = EXCLUDED.options
            """
            
            cursor.execute(insert_query, (
                question_number, year, section, question_text, correct_answer,
                explanation, json.dumps(options), exam_type
            ))
            
            success_count += 1
            print(f"✅ Q{question_number} uploaded successfully ({i}/{len(questions)})")
            
        except Exception as e:
            error_count += 1
            print(f"❌ Error uploading Q{question.get('question_number', 'N/A')}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"\n🎉 UPLOAD COMPLETE!")
    print(f"   Successfully uploaded: {success_count}")
    print(f"   Errors: {error_count}")
    print(f"   Total processed: {len(questions)}")

if __name__ == "__main__":
    upload_to_supabase() 