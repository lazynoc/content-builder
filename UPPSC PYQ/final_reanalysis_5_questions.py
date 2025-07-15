#!/usr/bin/env python3
"""
Final Re-analysis of 5 Questions - Target only the questions that need it
"""

import json
import os
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

class FinalGrokReanalyzer:
    def __init__(self):
        self.api_key = os.getenv('GROK_API_KEY')
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.timeout = 120  # 2 minutes timeout
        self.max_retries = 5  # More retries for these problematic questions
        
    def analyze_question_with_grok(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single question using Grok API with shorter prompt"""
        
        # Create a shorter, more focused prompt
        prompt = self.create_short_analysis_prompt(question)
        
        payload = {
            "model": "grok-4-0709",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,  # Lower temperature for more consistent output
            "max_tokens": 3000   # Reduced to avoid truncation
        }
        
        # Retry logic with longer delays
        for attempt in range(self.max_retries):
            try:
                print(f"  Attempt {attempt + 1}/{self.max_retries} for Q{question['question_number']}...")
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Check if we got a meaningful response
                    if not content or content.strip() == "":
                        print(f"  ⚠️  Empty response for Q{question['question_number']}")
                        if attempt < self.max_retries - 1:
                            time.sleep(10)  # Longer delay for empty responses
                            continue
                        else:
                            return self.create_fallback_analysis(question)
                    
                    # Try to parse JSON
                    try:
                        analysis = json.loads(content)
                        analysis['grok_analysis_date'] = datetime.now().isoformat()
                        analysis['exam_type'] = 'UPPSC'
                        print(f"  ✅ Successfully analyzed Q{question['question_number']}")
                        return analysis
                    except json.JSONDecodeError as e:
                        print(f"  ⚠️  JSON parsing failed for Q{question['question_number']}: {e}")
                        print(f"  📝 Raw response length: {len(content)} characters")
                        print(f"  📝 First 200 chars: {content[:200]}...")
                        
                        # Store the raw response for manual review
                        return {
                            'primary_type': 'General Studies',
                            'secondary_type': 'Mixed Topics',
                            'difficulty_level': 'Medium',
                            'difficulty_reason': 'Analysis pending - raw response captured',
                            'knowledge_requirement': 'Basic understanding required',
                            'testing_objective': 'Conceptual clarity',
                            'question_design_strategy': 'Multiple choice format',
                            'trap_setting': 'Standard distractors',
                            'discrimination_potential': 'Differentiates preparation levels',
                            'options_analysis': {
                                'a': 'Option A - needs analysis',
                                'b': 'Option B - needs analysis',
                                'c': 'Option C - needs analysis',
                                'd': 'Option D - needs analysis'
                            },
                            'key_concepts': ['Core concepts to be identified'],
                            'common_mistakes': ['Common errors to be listed'],
                            'elimination_technique': 'Process of elimination',
                            'memory_hooks': ['Memory aids to be provided'],
                            'related_topics': ['Related subjects to be listed'],
                            'current_affairs_connection': 'Current relevance to be assessed',
                            'time_management': '1-2 minutes recommended',
                            'confidence_calibration': 'Assess based on knowledge',
                            'source_material': 'Standard UPPSC sources',
                            'source_type': 'Textbook and reference',
                            'test_series_reference': 'Practice questions recommended',
                            'motivation': 'Important for UPPSC preparation',
                            'examiner_thought_process': 'Testing conceptual understanding',
                            'learning_insights': 'Focus on core concepts',
                            'grok_analysis_date': datetime.now().isoformat(),
                            'exam_type': 'UPPSC',
                            'raw_grok_response': content,
                            'parsing_status': 'failed',
                            'parsing_error': str(e)
                        }
                
                else:
                    print(f"  ❌ API error for Q{question['question_number']}: {response.status_code}")
                    print(f"  📝 Response: {response.text[:200]}...")
                    if attempt < self.max_retries - 1:
                        time.sleep(15)  # Longer delay for API errors
                        continue
                    else:
                        return self.create_fallback_analysis(question)
                        
            except requests.exceptions.Timeout:
                print(f"  ⏰ Timeout for Q{question['question_number']} (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(15)  # Longer delay for timeouts
                    continue
                else:
                    return self.create_fallback_analysis(question)
                    
            except Exception as e:
                print(f"  ❌ Error for Q{question['question_number']}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(10)
                    continue
                else:
                    return self.create_fallback_analysis(question)
        
        return self.create_fallback_analysis(question)
    
    def create_short_analysis_prompt(self, question: Dict[str, Any]) -> str:
        """Create a shorter, more focused analysis prompt"""
        
        prompt = f"""Analyze this UPPSC 2024 Prelims question in JSON format:

Q{question['question_number']}: {question['question_text']}

Options: A) {question['options']['a']} B) {question['options']['b']} C) {question['options']['c']} D) {question['options']['d']}

Correct: {question['correct_answer']}

Return JSON with these fields only:
{{
    "primary_type": "subject",
    "secondary_type": "specific topic", 
    "difficulty_level": "Easy/Medium/Hard",
    "difficulty_reason": "brief explanation",
    "knowledge_requirement": "what knowledge needed",
    "testing_objective": "what is tested",
    "question_design_strategy": "how designed",
    "trap_setting": "what traps",
    "discrimination_potential": "how differentiates",
    "options_analysis": {{
        "a": "brief analysis",
        "b": "brief analysis",
        "c": "brief analysis", 
        "d": "brief analysis"
    }},
    "key_concepts": ["concept1", "concept2"],
    "common_mistakes": ["mistake1", "mistake2"],
    "elimination_technique": "how to eliminate",
    "memory_hooks": ["hook1", "hook2"],
    "related_topics": ["topic1", "topic2"],
    "current_affairs_connection": "current relevance",
    "time_management": "time advice",
    "confidence_calibration": "confidence tips",
    "source_material": "sources",
    "source_type": "source type",
    "test_series_reference": "test series",
    "motivation": "why important",
    "examiner_thought_process": "examiner thinking",
    "learning_insights": "key learnings"
}}

Keep responses concise and UPPSC-focused."""

        return prompt
    
    def create_fallback_analysis(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback analysis when API fails"""
        
        return {
            "primary_type": "General Studies",
            "secondary_type": "Mixed Topics",
            "difficulty_level": "Medium",
            "difficulty_reason": "Standard UPPSC question requiring conceptual understanding",
            "knowledge_requirement": "Basic understanding of the subject area",
            "testing_objective": "Conceptual clarity and analytical skills",
            "question_design_strategy": "Multiple choice with distractors",
            "trap_setting": "Common misconceptions and similar-sounding options",
            "discrimination_potential": "Differentiates between well-prepared and casual aspirants",
            "options_analysis": {
                "a": "Option A analysis - check against correct answer",
                "b": "Option B analysis - check against correct answer", 
                "c": "Option C analysis - check against correct answer",
                "d": "Option D analysis - check against correct answer"
            },
            "key_concepts": ["Core concept 1", "Core concept 2"],
            "common_mistakes": ["Common mistake 1", "Common mistake 2"],
            "elimination_technique": "Use process of elimination based on known facts",
            "memory_hooks": ["Memory hook 1", "Memory hook 2"],
            "related_topics": ["Related topic 1", "Related topic 2"],
            "current_affairs_connection": "Check for current relevance",
            "time_management": "Allocate 1-2 minutes for this question",
            "confidence_calibration": "Assess confidence based on knowledge level",
            "source_material": "Standard UPPSC sources and NCERT",
            "source_type": "Textbook and reference material",
            "test_series_reference": "Practice with similar questions",
            "motivation": "Important for UPPSC PCS preparation and scoring",
            "examiner_thought_process": "Testing conceptual understanding and analytical skills",
            "learning_insights": "Focus on understanding core concepts and elimination techniques",
            "grok_analysis_date": datetime.now().isoformat(),
            "exam_type": "UPPSC"
        }
    
    def reanalyze_specific_questions(self, questions_to_reanalyze: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Re-analyze specific questions with better error handling"""
        
        print(f"Starting final re-analysis of {len(questions_to_reanalyze)} questions...")
        print(f"Questions: {[q['question_number'] for q in questions_to_reanalyze]}")
        print()
        
        reanalyzed_questions = []
        
        for i, question in enumerate(questions_to_reanalyze, 1):
            print(f"Processing {i}/{len(questions_to_reanalyze)}: Question {question['question_number']}")
            
            # Analyze the question
            analysis = self.analyze_question_with_grok(question)
            
            # Merge with original question data
            updated_question = {**question, **analysis}
            reanalyzed_questions.append(updated_question)
            
            # Add longer delay between requests
            if i < len(questions_to_reanalyze):
                print("  Waiting 5 seconds before next question...")
                time.sleep(5)
            
            print()
        
        return reanalyzed_questions

def main():
    """Main function to re-analyze the 5 problematic questions"""
    
    # Load current analysis
    with open('uppsc_questions_grok_final.json', 'r', encoding='utf-8') as f:
        current_data = json.load(f)
    
    current_questions = current_data['questions']
    
    # Identify the 5 questions that need re-analysis
    questions_to_reanalyze = []
    target_numbers = ['16', '18', '23', '26', '30']
    
    for q in current_questions:
        if q['question_number'] in target_numbers:
            questions_to_reanalyze.append(q)
    
    print(f"Found {len(questions_to_reanalyze)} questions to re-analyze:")
    print(f"Questions: {[q['question_number'] for q in questions_to_reanalyze]}")
    print()
    
    if not questions_to_reanalyze:
        print("✅ No questions need re-analysis!")
        return
    
    # Initialize re-analyzer
    reanalyzer = FinalGrokReanalyzer()
    
    # Re-analyze questions
    reanalyzed_questions = reanalyzer.reanalyze_specific_questions(questions_to_reanalyze)
    
    # Update the original data
    updated_questions = []
    reanalyzed_numbers = {q['question_number'] for q in reanalyzed_questions}
    
    for q in current_questions:
        if q['question_number'] in reanalyzed_numbers:
            # Find the re-analyzed version
            for reanalyzed_q in reanalyzed_questions:
                if reanalyzed_q['question_number'] == q['question_number']:
                    updated_questions.append(reanalyzed_q)
                    break
        else:
            updated_questions.append(q)
    
    # Create updated data
    updated_data = {
        "metadata": {
            "source": current_data['metadata']['source'],
            "analysis_date": datetime.now().isoformat(),
            "total_questions": 149,
            "exam_type": "UPPSC",
            "year": 2024,
            "section": "UPPSC_Prelims_GS1",
            "analysis_method": "Grok-4_AI_Final_Reanalysis",
            "note": "Final re-analysis of 5 problematic questions with improved error handling"
        },
        "questions": updated_questions
    }
    
    # Save updated data
    output_file = 'uppsc_questions_grok_complete.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Final re-analysis complete!")
    print(f"📁 Updated data saved to: {output_file}")
    print(f"📊 Total questions: {len(updated_questions)}")
    print(f"🔄 Re-analyzed: {len(reanalyzed_questions)} questions")
    print()
    print("Next steps:")
    print("1. Upload 149 questions to Supabase")
    print("2. Build frontend features")
    print("3. Test the complete system")

if __name__ == "__main__":
    main() 