#!/usr/bin/env python3
"""
Debug single question insert for pyq_question_table
"""

import json
import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv(dotenv_path='../../.env')

def debug_single_insert():
    """Test inserting a single question with correct column count"""
    
    # Load a sample question
    with open('GS Prelims 2024_WITH_OPENAI_ANALYSIS.json', 'r') as f:
        data = json.load(f)
    
    sample_question = data['questions'][0]
    print(f"Testing with question {sample_question.get('question_number', 'unknown')}")
    
    # Connect to database
    db_url = os.getenv('SUPABASE_DB_URL')
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    try:
        # Extract data
        question_nature = sample_question.get('question_nature', {})
        examiner_thought = sample_question.get('examiner_thought_process', {})
        learning_insights = sample_question.get('learning_insights', {})
        options_analysis = sample_question.get('options_analysis', {})
        
        # Prepare tags
        tags = []
        if question_nature.get('primary_type'):
            tags.append(question_nature['primary_type'])
        if question_nature.get('secondary_type'):
            tags.append(question_nature['secondary_type'])
        if sample_question.get('difficulty_level'):
            tags.append(sample_question['difficulty_level'])
        if sample_question.get('section'):
            tags.append(sample_question['section'])
        
        # Prepare arrays for TEXT[] fields
        key_concepts = learning_insights.get('key_concepts', [])
        common_mistakes = learning_insights.get('common_mistakes', [])
        memory_hooks = learning_insights.get('memory_hooks', [])
        related_topics = learning_insights.get('related_topics', [])
        
        # Truncate function
        def truncate_field(value, max_length):
            if value and len(str(value)) > max_length:
                return str(value)[:max_length]
            return value
        
        # Prepare values (36 columns, excluding id, created_at, updated_at)
        values = (
            str(sample_question.get('question_number')),  # 1
            2024,  # 2
            truncate_field(sample_question.get('section', 'General Studies'), 100),  # 3
            sample_question.get('question_text', ''),  # 4
            sample_question.get('correct_answer', ''),  # 5
            sample_question.get('explanation', ''),  # 6
            json.dumps(sample_question.get('options', {})),  # 7
            truncate_field(question_nature.get('primary_type'), 50),  # 8
            truncate_field(question_nature.get('secondary_type'), 50),  # 9
            truncate_field(sample_question.get('difficulty_level'), 20),  # 10
            question_nature.get('difficulty_reason'),  # 11
            truncate_field(question_nature.get('knowledge_requirement'), 100),  # 12
            examiner_thought.get('testing_objective'),  # 13
            examiner_thought.get('question_design_strategy'),  # 14
            examiner_thought.get('trap_setting'),  # 15
            examiner_thought.get('discrimination_potential'),  # 16
            json.dumps(options_analysis),  # 17
            key_concepts,  # 18
            common_mistakes,  # 19
            learning_insights.get('elimination_technique'),  # 20
            memory_hooks,  # 21
            related_topics,  # 22
            learning_insights.get('current_affairs_connection'),  # 23
            sample_question.get('time_management'),  # 24
            sample_question.get('confidence_calibration'),  # 25
            sample_question.get('source_material', ''),  # 26
            truncate_field(sample_question.get('source_type', ''), 100),  # 27
            sample_question.get('test_series_reference', ''),  # 28
            sample_question.get('extraction_order'),  # 29
            sample_question.get('chunk_number'),  # 30
            tags,  # 31
            sample_question.get('motivation'),  # 32
            json.dumps(examiner_thought),  # 33
            json.dumps(learning_insights),  # 34
            sample_question.get('openai_analysis_date')  # 35
        )
        
        print(f"Number of values: {len(values)}")
        
        # Execute insert with correct column count
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
        """, values)
        
        conn.commit()
        print("✅ Single question inserted successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    debug_single_insert() 