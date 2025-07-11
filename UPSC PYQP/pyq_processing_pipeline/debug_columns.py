#!/usr/bin/env python3
"""
Debug script to check column count mismatch
"""

import json
from import_2024_simple import SimpleSupabaseImport

def debug_column_count():
    """Debug the column count issue"""
    
    # Load a sample question to see the structure
    with open('GS Prelims 2024_WITH_OPENAI_ANALYSIS.json', 'r') as f:
        data = json.load(f)
    
    sample_question = data['questions'][0]
    print("Sample question keys:")
    for key in sample_question.keys():
        print(f"  - {key}")
    
    print(f"\nTotal keys in sample question: {len(sample_question.keys())}")
    
    # Count columns in our INSERT statement
    insert_columns = [
        'question_number', 'year', 'section', 'question_text', 'correct_answer',
        'explanation', 'options', 'primary_type', 'secondary_type', 'difficulty_level',
        'difficulty_reason', 'knowledge_requirement', 'testing_objective',
        'question_design_strategy', 'trap_setting', 'discrimination_potential',
        'options_analysis', 'key_concepts', 'common_mistakes', 'elimination_technique',
        'memory_hooks', 'related_topics', 'current_affairs_connection',
        'time_management', 'confidence_calibration', 'source_material',
        'source_type', 'test_series_reference', 'extraction_order', 'chunk_number', 'tags',
        'motivation', 'examiner_thought_process', 'learning_insights', 'openai_analysis_date'
    ]
    
    print(f"\nColumns in INSERT statement: {len(insert_columns)}")
    for i, col in enumerate(insert_columns, 1):
        print(f"  {i:2d}. {col}")
    
    # Check schema columns
    schema_columns = [
        'id', 'question_number', 'year', 'section', 'question_text', 'correct_answer',
        'explanation', 'options', 'primary_type', 'secondary_type', 'difficulty_level',
        'difficulty_reason', 'knowledge_requirement', 'testing_objective',
        'question_design_strategy', 'trap_setting', 'discrimination_potential',
        'options_analysis', 'key_concepts', 'common_mistakes', 'elimination_technique',
        'memory_hooks', 'related_topics', 'current_affairs_connection',
        'time_management', 'confidence_calibration', 'source_material',
        'source_type', 'test_series_reference', 'extraction_order', 'chunk_number', 'tags',
        'motivation', 'examiner_thought_process', 'learning_insights', 'openai_analysis_date',
        'created_at', 'updated_at'
    ]
    
    print(f"\nColumns in schema: {len(schema_columns)}")
    for i, col in enumerate(schema_columns, 1):
        print(f"  {i:2d}. {col}")
    
    # Auto-generated columns (should not be in INSERT)
    auto_columns = ['id', 'created_at', 'updated_at']
    manual_columns = [col for col in schema_columns if col not in auto_columns]
    
    print(f"\nManual columns (should be in INSERT): {len(manual_columns)}")
    for i, col in enumerate(manual_columns, 1):
        print(f"  {i:2d}. {col}")
    
    print(f"\nINSERT columns count: {len(insert_columns)}")
    print(f"Manual schema columns count: {len(manual_columns)}")
    
    if len(insert_columns) != len(manual_columns):
        print("❌ MISMATCH DETECTED!")
        missing_in_insert = set(manual_columns) - set(insert_columns)
        extra_in_insert = set(insert_columns) - set(manual_columns)
        
        if missing_in_insert:
            print(f"Missing in INSERT: {missing_in_insert}")
        if extra_in_insert:
            print(f"Extra in INSERT: {extra_in_insert}")
    else:
        print("✅ Column counts match!")

if __name__ == "__main__":
    debug_column_count() 