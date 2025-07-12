import json
import uuid
from datetime import datetime

def fix_question_86_analysis():
    # Load the enhanced JSON
    with open('uppsc_questions_complete_enhanced.json', 'r', encoding='utf-8') as f:
        enhanced_data = json.load(f)
    
    # Load the OpenAI reanalysis results
    with open('openai_reanalysis_all_poor_quality_results.json', 'r', encoding='utf-8') as f:
        openai_results = json.load(f)
    
    # Find question 86 in the enhanced data (questions array)
    question_86_enhanced = None
    for question in enhanced_data['questions']:
        if question.get('question_number') == '86':
            question_86_enhanced = question
            break
    
    # Find question 86 in the OpenAI results
    question_86_openai = None
    for question in openai_results:
        if question.get('question_number') == 86:  # Note: OpenAI results have integer
            question_86_openai = question
            break
    
    if question_86_enhanced and question_86_openai:
        print("Found both question 86 entries")
        
        # Update the enhanced question with OpenAI analysis
        analysis_result = question_86_openai.get('analysis_result', {})
        if analysis_result.get('success'):
            analysis = analysis_result.get('analysis', {})
            
            # Update the enhanced question with analysis fields
            question_86_enhanced.update({
                'explanation': analysis.get('explanation', ''),
                'primary_type': analysis.get('subject', ''),
                'secondary_type': analysis.get('topic', ''),
                'difficulty_level': analysis.get('difficulty_level', ''),
                'key_concepts': analysis.get('key_concepts', []),
                'related_topics': analysis.get('related_topics', []),
                'study_tips': analysis.get('study_tips', ''),
                'examiner_thought_process': analysis.get('examiner_thought_process', ''),
                'common_mistakes': analysis.get('common_mistakes', ''),
                'time_management': analysis.get('time_management', ''),
                'confidence_level': analysis.get('confidence_level', ''),
                'priority_level': analysis.get('priority_level', ''),
                'uppsc_relevance': analysis.get('uppsc_relevance', ''),
                'why_others_are_wrong': analysis.get('why_others_are_wrong', {}),
                'analysis_source': 'OpenAI_Reanalysis',
                'openai_analysis_date': datetime.now().isoformat(),
                'year': 2024,
                'section': 'UPPSC_Prelims_GS1'
            })
            
            print("Successfully updated question 86 with OpenAI analysis")
        else:
            print("OpenAI analysis for question 86 was not successful")
    else:
        print("Could not find question 86 in one or both files")
        if not question_86_enhanced:
            print("Question 86 not found in enhanced JSON")
        if not question_86_openai:
            print("Question 86 not found in OpenAI results")
    
    # Save the updated enhanced JSON
    with open('uppsc_questions_complete_enhanced_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
    
    print("Saved updated enhanced JSON as 'uppsc_questions_complete_enhanced_fixed.json'")

if __name__ == "__main__":
    fix_question_86_analysis() 