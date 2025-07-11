#!/usr/bin/env python3
"""
Test single question insert to debug the issue
"""

import json
from import_2024_simple import SimpleSupabaseImport

def test_single_insert():
    """Test inserting a single question"""
    
    # Load a sample question
    with open('GS Prelims 2024_WITH_OPENAI_ANALYSIS.json', 'r') as f:
        data = json.load(f)
    
    sample_question = data['questions'][0]
    print(f"Testing with question {sample_question.get('question_number', 'unknown')}")
    
    # Initialize importer
    importer = SimpleSupabaseImport()
    
    try:
        # Create schema
        print("Creating schema...")
        importer.create_schema()
        
        # Try to insert the question
        print("Attempting to insert question...")
        cursor = importer.connection.cursor()
        
        # Extract data like in the original function
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
        
        # Truncate function
        def truncate_field(value, max_length):
            if value and len(str(value)) > max_length:
                return str(value)[:max_length]
            return value
        
        # Prepare values
        values = (
            sample_question.get('question_number'),
            2024,  # Year
            truncate_field(sample_question.get('section', 'General Studies'), 100),
            sample_question.get('question_text', ''),
            sample_question.get('correct_answer', ''),
            sample_question.get('explanation', ''),
            json.dumps(sample_question.get('options', {})),  # Options as JSON
            truncate_field(question_nature.get('primary_type'), 50),
            truncate_field(question_nature.get('secondary_type'), 50),
            truncate_field(sample_question.get('difficulty_level'), 20),
            question_nature.get('difficulty_reason'),
            truncate_field(question_nature.get('knowledge_requirement'), 100),
            examiner_thought.get('testing_objective'),
            examiner_thought.get('question_design_strategy'),
            examiner_thought.get('trap_setting'),
            examiner_thought.get('discrimination_potential'),
            json.dumps(options_analysis),  # Options analysis as JSON
            learning_insights.get('key_concepts'),
            learning_insights.get('common_mistakes'),
            learning_insights.get('elimination_technique'),
            learning_insights.get('memory_hooks'),
            learning_insights.get('related_topics'),
            learning_insights.get('current_affairs_connection'),
            sample_question.get('time_management'),
            sample_question.get('confidence_calibration'),
            sample_question.get('source_material', ''),
            truncate_field(sample_question.get('source_type', ''), 100),
            sample_question.get('test_series_reference', ''),
            sample_question.get('extraction_order'),
            sample_question.get('chunk_number'),
            tags,
            sample_question.get('motivation'),
            json.dumps(examiner_thought),  # Full examiner thought process as JSON
            json.dumps(learning_insights),  # Full learning insights as JSON
            sample_question.get('openai_analysis_date')
        )
        
        print(f"Number of values: {len(values)}")
        print("Values:")
        for i, val in enumerate(values, 1):
            print(f"  {i:2d}. {type(val).__name__}: {str(val)[:50]}{'...' if len(str(val)) > 50 else ''}")
        
        # Execute insert
        cursor.execute("""
            INSERT INTO questions (
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
                %s, %s, %s, %s
            )
        """, values)
        
        importer.connection.commit()
        print("✅ Single question inserted successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        importer.close()

if __name__ == "__main__":
    test_single_insert() 