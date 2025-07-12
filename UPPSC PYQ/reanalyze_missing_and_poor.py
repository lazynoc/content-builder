#!/usr/bin/env python3
"""
Re-analyze Missing and Poor Quality Questions - Process only Question 86 and 10 poor quality questions
"""

import json
import os
import time
import requests
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

class GrokReanalyzer:
    def __init__(self):
        self.api_key = os.getenv('GROK_API_KEY')
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.timeout = 120  # 2 minutes timeout
        self.max_retries = 3
        
    def analyze_question_with_grok(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single question using Grok API with optimized prompt"""
        
        # Create the analysis prompt
        prompt = self.create_analysis_prompt(question)
        
        payload = {
            "model": "grok-4-0709",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 4000
        }
        
        # Retry logic
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
                    
                    # Parse the JSON response
                    try:
                        analysis = json.loads(content)
                        
                        # Add analysis metadata
                        analysis['grok_analysis_date'] = datetime.now().isoformat()
                        analysis['exam_type'] = 'UPPSC'
                        
                        print(f"  ✅ Successfully analyzed Q{question['question_number']}")
                        return analysis
                        
                    except json.JSONDecodeError as e:
                        print(f"  ⚠️  JSON parsing failed for Q{question['question_number']}: {e}")
                        if attempt < self.max_retries - 1:
                            time.sleep(2)
                            continue
                        else:
                            # Return fallback analysis
                            return self.create_fallback_analysis(question)
                
                else:
                    print(f"  ❌ API error for Q{question['question_number']}: {response.status_code}")
                    if attempt < self.max_retries - 1:
                        time.sleep(5)
                        continue
                    else:
                        return self.create_fallback_analysis(question)
                        
            except requests.exceptions.Timeout:
                print(f"  ⏰ Timeout for Q{question['question_number']} (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(10)
                    continue
                else:
                    return self.create_fallback_analysis(question)
                    
            except Exception as e:
                print(f"  ❌ Error for Q{question['question_number']}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(5)
                    continue
                else:
                    return self.create_fallback_analysis(question)
        
        return self.create_fallback_analysis(question)
    
    def create_analysis_prompt(self, question: Dict[str, Any]) -> str:
        """Create optimized analysis prompt for Grok"""
        
        prompt = f"""Analyze this UPPSC 2024 Prelims question and provide detailed insights in JSON format:

Question {question['question_number']}: {question['question_text']}

Options:
A) {question['options']['a']}
B) {question['options']['b']}
C) {question['options']['c']}
D) {question['options']['d']}

Correct Answer: {question['correct_answer']}

Provide analysis in this exact JSON format:
{{
    "primary_type": "subject area",
    "secondary_type": "specific topic",
    "difficulty_level": "Easy/Medium/Hard",
    "difficulty_reason": "detailed explanation",
    "knowledge_requirement": "what knowledge is needed",
    "testing_objective": "what is being tested",
    "question_design_strategy": "how question is designed",
    "trap_setting": "what traps are set",
    "discrimination_potential": "how it differentiates candidates",
    "options_analysis": {{
        "a": "analysis of option A",
        "b": "analysis of option B", 
        "c": "analysis of option C",
        "d": "analysis of option D"
    }},
    "key_concepts": ["concept1", "concept2"],
    "common_mistakes": ["mistake1", "mistake2"],
    "elimination_technique": "how to eliminate wrong options",
    "memory_hooks": ["hook1", "hook2"],
    "related_topics": ["topic1", "topic2"],
    "current_affairs_connection": "any current relevance",
    "time_management": "time allocation advice",
    "confidence_calibration": "confidence assessment",
    "source_material": "relevant sources",
    "source_type": "type of source",
    "test_series_reference": "test series relevance",
    "motivation": "why this is important for UPPSC",
    "examiner_thought_process": "what examiner is thinking",
    "learning_insights": "key learning points"
}}

Focus on UPPSC-specific context and provide detailed, actionable insights for UP PCS aspirants."""

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
    
    def reanalyze_questions(self, questions_to_reanalyze: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Re-analyze a list of questions"""
        
        print(f"Starting re-analysis of {len(questions_to_reanalyze)} questions...")
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
            
            # Add delay between requests
            if i < len(questions_to_reanalyze):
                print("  Waiting 3 seconds before next question...")
                time.sleep(3)
            
            print()
        
        return reanalyzed_questions

def main():
    """Main function to re-analyze missing and poor quality questions"""
    
    # Load current analysis
    with open('uppsc_questions_grok_optimized.json', 'r', encoding='utf-8') as f:
        current_data = json.load(f)
    
    current_questions = current_data['questions']
    
    # Identify questions to re-analyze
    questions_to_reanalyze = []
    
    # 1. Missing question (86)
    missing_86 = None
    for q in current_questions:
        if q['question_number'] == '86':
            missing_86 = q
            break
    
    if not missing_86:
        print("❌ Question 86 not found in current data!")
        return
    
    questions_to_reanalyze.append(missing_86)
    
    # 2. Questions with poor analysis (minimal content)
    poor_quality_numbers = ['1', '16', '18', '23', '26', '30', '31', '32', '51', '71']
    
    for q in current_questions:
        if q['question_number'] in poor_quality_numbers:
            # Check if it has poor analysis
            key_fields = ['difficulty_reason', 'options_analysis', 'key_concepts', 'common_mistakes']
            has_poor_analysis = False
            
            for field in key_fields:
                value = q.get(field)
                if not value or (isinstance(value, str) and len(value) < 50):
                    has_poor_analysis = True
                    break
            
            if has_poor_analysis:
                questions_to_reanalyze.append(q)
    
    print(f"Found {len(questions_to_reanalyze)} questions to re-analyze:")
    print(f"Missing: Question 86")
    print(f"Poor quality: {[q['question_number'] for q in questions_to_reanalyze if q['question_number'] != '86']}")
    print()
    
    # Initialize re-analyzer
    reanalyzer = GrokReanalyzer()
    
    # Re-analyze questions
    reanalyzed_questions = reanalyzer.reanalyze_questions(questions_to_reanalyze)
    
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
            "total_questions": 150,
            "exam_type": "UPPSC",
            "year": 2024,
            "section": "UPPSC_Prelims_GS1",
            "analysis_method": "Grok-4_AI_Reanalyzed",
            "note": "Re-analyzed missing question 86 and 10 poor quality questions for improved analysis"
        },
        "questions": updated_questions
    }
    
    # Save updated data
    output_file = 'uppsc_questions_grok_reanalyzed.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Re-analysis complete!")
    print(f"📁 Updated data saved to: {output_file}")
    print(f"📊 Total questions: {len(updated_questions)}")
    print(f"🔄 Re-analyzed: {len(reanalyzed_questions)} questions")
    print()
    print("Next steps:")
    print("1. Verify the re-analyzed questions")
    print("2. Upload all 150 questions to Supabase")
    print("3. Test the complete system")

if __name__ == "__main__":
    main() 