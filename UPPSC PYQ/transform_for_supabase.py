import json
import uuid
from datetime import datetime

def transform_uppsc_to_supabase_format():
    """Transform UPPSC questions to Supabase database format"""
    
    # Load the UPPSC questions
    with open('uppsc_questions_complete_final.json', 'r', encoding='utf-8') as f:
        uppsc_data = json.load(f)
    
    # Transform each question
    supabase_questions = []
    
    for question in uppsc_data['questions']:
        # Skip duplicate question 132 (keep only the first one)
        if question['question_number'] == '132' and len(question['question_text']) < 50:
            continue
            
        # Create Supabase format question
        supabase_question = {
            "id": str(uuid.uuid4()),
            "question_number": question['question_number'],
            "year": 2024,
            "section": "UPPSC_Prelims_GS1",
            "question_text": question['question_text'],
            "correct_answer": question['correct_answer'],
            "explanation": None,  # Will be filled by Grok analysis
            "options": question['options'],
            "primary_type": None,  # Will be filled by Grok analysis
            "secondary_type": None,  # Will be filled by Grok analysis
            "difficulty_level": None,  # Will be filled by Grok analysis
            "difficulty_reason": None,  # Will be filled by Grok analysis
            "knowledge_requirement": None,  # Will be filled by Grok analysis
            "testing_objective": None,  # Will be filled by Grok analysis
            "question_design_strategy": None,  # Will be filled by Grok analysis
            "trap_setting": None,  # Will be filled by Grok analysis
            "discrimination_potential": None,  # Will be filled by Grok analysis
            "options_analysis": None,  # Will be filled by Grok analysis
            "key_concepts": None,  # Will be filled by Grok analysis
            "common_mistakes": None,  # Will be filled by Grok analysis
            "elimination_technique": None,  # Will be filled by Grok analysis
            "memory_hooks": None,  # Will be filled by Grok analysis
            "related_topics": None,  # Will be filled by Grok analysis
            "current_affairs_connection": None,  # Will be filled by Grok analysis
            "time_management": None,  # Will be filled by Grok analysis
            "confidence_calibration": None,  # Will be filled by Grok analysis
            "source_material": None,  # Will be filled by Grok analysis
            "source_type": None,  # Will be filled by Grok analysis
            "test_series_reference": None,  # Will be filled by Grok analysis
            "extraction_order": question.get('extraction_order'),
            "chunk_number": question.get('chunk_number'),
            "tags": None,  # Will be filled by Grok analysis
            "motivation": None,  # Will be filled by Grok analysis
            "examiner_thought_process": None,  # Will be filled by Grok analysis
            "learning_insights": None,  # Will be filled by Grok analysis
            "openai_analysis_date": None,  # Will be updated after Grok analysis
            "exam_type": "UPPSC"
        }
        
        supabase_questions.append(supabase_question)
    
    # Save the transformed data
    output_data = {
        "metadata": {
            "source": "UPPSC_2024_Prelims_GS1",
            "transformation_date": datetime.now().isoformat(),
            "total_questions": len(supabase_questions),
            "exam_type": "UPPSC",
            "year": 2024,
            "section": "UPPSC_Prelims_GS1",
            "note": "Transformed for Supabase database insertion. Grok analysis pending."
        },
        "questions": supabase_questions
    }
    
    with open('uppsc_questions_supabase_ready.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Transformed {len(supabase_questions)} questions for Supabase")
    print(f"📁 Saved as: uppsc_questions_supabase_ready.json")
    
    return output_data

if __name__ == "__main__":
    transform_uppsc_to_supabase_format() 