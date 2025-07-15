#!/usr/bin/env python3
"""
Script to merge OpenAI analyses with Grok file and update for all 150 questions
"""

import json
from datetime import datetime

def merge_analyses():
    # Load the OpenAI analysis results
    with open('openai_reanalysis_all_poor_quality_results.json', 'r', encoding='utf-8') as f:
        openai_results = json.load(f)
    
    # Load the Grok analysis file
    with open('uppsc_questions_grok_final.json', 'r', encoding='utf-8') as f:
        grok_data = json.load(f)
    
    # Create a mapping of question numbers to OpenAI analyses
    openai_analyses = {}
    for result in openai_results:
        if result['analysis_result']['success']:
            openai_analyses[int(result['question_number'])] = result['analysis_result']['analysis']
    
    # Update the Grok data with OpenAI analyses
    updated_questions = []
    
    for question in grok_data['questions']:
        question_num = int(question['question_number'])
        
        # If this question has OpenAI analysis, replace the Grok analysis
        if question_num in openai_analyses:
            openai_analysis = openai_analyses[question_num]
            
            # Update the question with OpenAI analysis
            updated_question = question.copy()
            
            # Map OpenAI fields to Grok structure
            updated_question.update({
                'primary_type': openai_analysis.get('subject', question.get('primary_type')),
                'secondary_type': openai_analysis.get('topic', question.get('secondary_type')),
                'difficulty_level': openai_analysis.get('difficulty_level', question.get('difficulty_level')),
                'difficulty_reason': f"OpenAI Analysis: {openai_analysis.get('difficulty_level', 'Medium')} difficulty",
                'knowledge_requirement': openai_analysis.get('explanation', ''),
                'testing_objective': openai_analysis.get('examiner_thought_process', ''),
                'question_design_strategy': openai_analysis.get('question_type', ''),
                'trap_setting': openai_analysis.get('common_mistakes', ''),
                'discrimination_potential': openai_analysis.get('confidence_level', ''),
                'options_analysis': openai_analysis.get('why_others_are_wrong', {}),
                'key_concepts': openai_analysis.get('key_concepts', []),
                'common_mistakes': [openai_analysis.get('common_mistakes', '')] if openai_analysis.get('common_mistakes') else [],
                'elimination_technique': openai_analysis.get('study_tips', ''),
                'memory_hooks': [],
                'related_topics': openai_analysis.get('related_topics', []),
                'current_affairs_connection': '',
                'time_management': openai_analysis.get('time_management', ''),
                'confidence_calibration': openai_analysis.get('confidence_level', ''),
                'source_material': '',
                'source_type': '',
                'test_series_reference': '',
                'tags': None,
                'motivation': openai_analysis.get('uppsc_relevance', ''),
                'examiner_thought_process': openai_analysis.get('examiner_thought_process', ''),
                'learning_insights': [openai_analysis.get('study_tips', '')] if openai_analysis.get('study_tips') else [],
                'openai_analysis_date': datetime.now().isoformat(),
                'learning_objectives': 'Enhanced understanding through OpenAI analysis',
                'question_strategy': openai_analysis.get('question_type', ''),
                'exam_strategy': openai_analysis.get('time_management', ''),
                'grok_analysis_date': question.get('grok_analysis_date', ''),
                'analysis_source': 'OpenAI_Enhanced'
            })
            
            print(f"✅ Updated Q{question_num} with OpenAI analysis")
        else:
            # Keep the original Grok analysis
            updated_question = question.copy()
            updated_question['analysis_source'] = 'Grok_Original'
            print(f"📝 Kept Q{question_num} with original Grok analysis")
        
        updated_questions.append(updated_question)
    
    # Load the complete questions file to get all 150 questions
    with open('uppsc_questions_complete_final.json', 'r', encoding='utf-8') as f:
        complete_data = json.load(f)
    
    # Create final dataset with all 150 questions
    final_questions = []
    
    for complete_question in complete_data['questions']:
        question_num = int(complete_question['question_number'])
        
        # Find corresponding updated question
        updated_question = None
        for q in updated_questions:
            if int(q['question_number']) == question_num:
                updated_question = q
                break
        
        if updated_question:
            # Merge complete question data with analysis
            final_question = complete_question.copy()
            final_question.update(updated_question)
            final_questions.append(final_question)
        else:
            # If no analysis found, use complete question data
            final_question = complete_question.copy()
            final_question['analysis_source'] = 'No_Analysis'
            final_questions.append(final_question)
    
    # Create final output
    final_data = {
        "metadata": {
            "source": "UPPSC_2024_Prelims_GS1",
            "analysis_date": datetime.now().isoformat(),
            "total_questions": 151,
            "exam_type": "UPPSC",
            "year": 2024,
            "section": "UPPSC_Prelims_GS1",
            "analysis_method": "Grok_OpenAI_Hybrid",
            "note": "Complete dataset with 151 questions. OpenAI analysis for 11 poor-quality questions, Grok analysis for others.",
            "openai_enhanced_questions": list(openai_analyses.keys()),
            "grok_original_questions": len([q for q in final_questions if q.get('analysis_source') == 'Grok_Original']),
            "no_analysis_questions": len([q for q in final_questions if q.get('analysis_source') == 'No_Analysis'])
        },
        "questions": final_questions
    }
    
    # Save the final dataset
    output_file = 'uppsc_questions_complete_enhanced.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ MERGE COMPLETE!")
    print(f"   Output: {output_file}")
    print(f"   Total questions: {len(final_questions)}")
    print(f"   OpenAI enhanced: {len(openai_analyses)}")
    print(f"   Grok original: {len([q for q in final_questions if q.get('analysis_source') == 'Grok_Original'])}")
    print(f"   No analysis: {len([q for q in final_questions if q.get('analysis_source') == 'No_Analysis'])}")

if __name__ == "__main__":
    merge_analyses() 