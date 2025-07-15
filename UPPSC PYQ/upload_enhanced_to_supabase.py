#!/usr/bin/env python3
"""
Script to upload enhanced UPPSC questions to Supabase (pyq_question_table)
"""
import json
import os
import psycopg2
import uuid
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from parent directory
load_dotenv('../.env')
DB_URL = os.getenv('SUPABASE_DB_URL')

def truncate_text(text, max_length=200):
    if text and len(str(text)) > max_length:
        return str(text)[:max_length-3] + "..."
    return text

def to_jsonb(val):
    if val is None:
        return None
    if isinstance(val, str):
        try:
            return json.loads(val)
        except Exception:
            return [val]
    return val

def upload_to_supabase():
    with open('uppsc_questions_complete_enhanced_fixed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    questions = data['questions']
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    print(f"📤 UPLOADING {len(questions)} ENHANCED UPPSC QUESTIONS TO SUPABASE (pyq_question_table)")
    print("=" * 60)
    success_count = 0
    error_count = 0
    for i, question in enumerate(questions, 1):
        try:
            # Required fields
            question_number = str(question.get('question_number'))
            year = int(question.get('year', 2024))
            section = truncate_text(question.get('section', 'UPPSC_Prelims_GS1'), 100)
            question_text = question.get('question_text')
            correct_answer = question.get('correct_answer')
            explanation = question.get('explanation')
            options = question.get('options')
            primary_type = truncate_text(question.get('primary_type', ''), 200)
            secondary_type = truncate_text(question.get('secondary_type', ''), 200)
            difficulty_level = truncate_text(question.get('difficulty_level', ''), 20)
            difficulty_reason = question.get('difficulty_reason')
            knowledge_requirement = truncate_text(question.get('knowledge_requirement', ''), 100)
            testing_objective = question.get('testing_objective')
            question_design_strategy = question.get('question_design_strategy')
            trap_setting = question.get('trap_setting')
            discrimination_potential = question.get('discrimination_potential')
            options_analysis = to_jsonb(question.get('options_analysis'))
            key_concepts = to_jsonb(question.get('key_concepts'))
            common_mistakes = to_jsonb(question.get('common_mistakes'))
            elimination_technique = question.get('elimination_technique')
            memory_hooks = to_jsonb(question.get('memory_hooks'))
            related_topics = to_jsonb(question.get('related_topics'))
            current_affairs_connection = question.get('current_affairs_connection')
            time_management = question.get('time_management')
            confidence_calibration = question.get('confidence_calibration')
            source_material = question.get('source_material')
            source_type = truncate_text(question.get('source_type', ''), 100)
            test_series_reference = question.get('test_series_reference')
            extraction_order = question.get('extraction_order')
            chunk_number = question.get('chunk_number')
            tags = to_jsonb(question.get('tags'))
            motivation = question.get('motivation')
            examiner_thought_process = to_jsonb(question.get('examiner_thought_process'))
            learning_insights = to_jsonb(question.get('learning_insights'))
            openai_analysis_date = question.get('openai_analysis_date')
            created_at = question.get('created_at') or datetime.now()
            updated_at = datetime.now()
            exam_type = truncate_text(question.get('exam_type', 'UPPSC'), 50)
            insert_query = """
            INSERT INTO pyq_question_table (
                id, question_number, year, section, question_text, correct_answer, explanation, options, primary_type, secondary_type, difficulty_level, difficulty_reason, knowledge_requirement, testing_objective, question_design_strategy, trap_setting, discrimination_potential, options_analysis, key_concepts, common_mistakes, elimination_technique, memory_hooks, related_topics, current_affairs_connection, time_management, confidence_calibration, source_material, source_type, test_series_reference, extraction_order, chunk_number, tags, motivation, examiner_thought_process, learning_insights, openai_analysis_date, created_at, updated_at, exam_type
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (year, question_number, exam_type)
            DO UPDATE SET
                section = EXCLUDED.section,
                question_text = EXCLUDED.question_text,
                correct_answer = EXCLUDED.correct_answer,
                explanation = EXCLUDED.explanation,
                options = EXCLUDED.options,
                primary_type = EXCLUDED.primary_type,
                secondary_type = EXCLUDED.secondary_type,
                difficulty_level = EXCLUDED.difficulty_level,
                difficulty_reason = EXCLUDED.difficulty_reason,
                knowledge_requirement = EXCLUDED.knowledge_requirement,
                testing_objective = EXCLUDED.testing_objective,
                question_design_strategy = EXCLUDED.question_design_strategy,
                trap_setting = EXCLUDED.trap_setting,
                discrimination_potential = EXCLUDED.discrimination_potential,
                options_analysis = EXCLUDED.options_analysis,
                key_concepts = EXCLUDED.key_concepts,
                common_mistakes = EXCLUDED.common_mistakes,
                elimination_technique = EXCLUDED.elimination_technique,
                memory_hooks = EXCLUDED.memory_hooks,
                related_topics = EXCLUDED.related_topics,
                current_affairs_connection = EXCLUDED.current_affairs_connection,
                time_management = EXCLUDED.time_management,
                confidence_calibration = EXCLUDED.confidence_calibration,
                source_material = EXCLUDED.source_material,
                source_type = EXCLUDED.source_type,
                test_series_reference = EXCLUDED.test_series_reference,
                extraction_order = EXCLUDED.extraction_order,
                chunk_number = EXCLUDED.chunk_number,
                tags = EXCLUDED.tags,
                motivation = EXCLUDED.motivation,
                examiner_thought_process = EXCLUDED.examiner_thought_process,
                learning_insights = EXCLUDED.learning_insights,
                openai_analysis_date = EXCLUDED.openai_analysis_date,
                updated_at = EXCLUDED.updated_at,
                exam_type = EXCLUDED.exam_type
            """
            # Use existing ID from JSON
            question_id = question.get('id')
            
            values_tuple = (
                question_id, question_number, year, section, question_text, correct_answer, explanation, json.dumps(options), primary_type, secondary_type, difficulty_level, difficulty_reason, knowledge_requirement, testing_objective, question_design_strategy, trap_setting, discrimination_potential, json.dumps(options_analysis) if options_analysis is not None else None, json.dumps(key_concepts) if key_concepts is not None else None, json.dumps(common_mistakes) if common_mistakes is not None else None, elimination_technique, json.dumps(memory_hooks) if memory_hooks is not None else None, json.dumps(related_topics) if related_topics is not None else None, current_affairs_connection, time_management, confidence_calibration, source_material, source_type, test_series_reference, extraction_order, chunk_number, json.dumps(tags) if tags is not None else None, motivation, json.dumps(examiner_thought_process) if examiner_thought_process is not None else None, json.dumps(learning_insights) if learning_insights is not None else None, openai_analysis_date, created_at, updated_at, exam_type
            )
            if i == 1:
                print(f"DEBUG: Tuple length: {len(values_tuple)}")
                print(f"DEBUG: Expected columns: 39")
                print(f"DEBUG: First few values: {values_tuple[:5]}")
                print(f"DEBUG: Last few values: {values_tuple[-5:]}")
            cursor.execute(insert_query, values_tuple)
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