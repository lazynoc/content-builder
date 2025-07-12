#!/usr/bin/env python3
"""
Optimized Grok Analysis Script - Streamlined fields + latest model + retry logic
"""

import json
import os
import time
import requests
from datetime import datetime
from typing import Dict, List, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv('../.env')

class OptimizedGrokAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('GROK_API_KEY')
        self.base_url = "https://api.x.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_question_with_grok(self, question_data, max_retries=3):
        """Analyze a single question with Grok API for UPPSC-specific insights"""
        
        prompt = f"""
You are an expert UPPSC (Uttar Pradesh Public Service Commission) mentor and question analyst. Analyze the following UPPSC 2024 Prelims question with detailed, UPPSC-specific insights.

Question: {question_data['question_text']}
Options: {json.dumps(question_data['options'], indent=2)}
Correct Answer: {question_data['correct_answer']}

Provide a comprehensive UPPSC-focused analysis in JSON format with these exact fields:

{{
  "explanation": "Detailed explanation of why the answer is correct",
  "primary_type": "Main subject area (History/Geography/Polity/Economics/Environment/Science/Current Affairs)",
  "secondary_type": "Specific sub-topic",
  "difficulty_level": "Easy/Medium/Hard",
  "difficulty_reason": "Why this difficulty level for UPPSC aspirants",
  "learning_objectives": "What knowledge is needed and what UPPSC is testing here",
  "question_strategy": "How the question is designed and what traps are set",
  "options_analysis": {{
    "a": "Detailed analysis of option A",
    "b": "Detailed analysis of option B", 
    "c": "Detailed analysis of option C",
    "d": "Detailed analysis of option D"
  }},
  "key_concepts": ["List of key concepts tested"],
  "common_mistakes": ["Common mistakes UPPSC aspirants make"],
  "elimination_technique": "How to eliminate wrong options",
  "memory_hooks": ["Memory techniques for UPPSC preparation"],
  "related_topics": ["Related topics for UPPSC preparation"],
  "exam_strategy": "Time management and confidence assessment for UPPSC prelims",
  "source_material": "Recommended sources for UPPSC preparation",
  "motivation": "Why this is important for UPPSC PCS preparation",
  "examiner_thought_process": "What UPPSC examiner is thinking when creating this question"
}}

Focus on UPPSC-specific context, UP state relevance, and practical preparation strategies. Be detailed and specific.
"""

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": "grok-4-0709",
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 3000
                    },
                    timeout=120  # 120 seconds timeout
                )
                
                response.raise_for_status()
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Try to extract JSON from the response
                try:
                    # Look for JSON content between triple backticks
                    if '```json' in content:
                        json_start = content.find('```json') + 7
                        json_end = content.find('```', json_start)
                        json_content = content[json_start:json_end].strip()
                    else:
                        # Try to find JSON content directly
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        json_content = content[json_start:json_end]
                    
                    analysis = json.loads(json_content)
                    return analysis
                    
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error (attempt {attempt + 1}): {e}")
                    if attempt == max_retries - 1:
                        print(f"Content: {content[:200]}...")
                        return None
                    time.sleep(5)  # Wait before retry
                    continue
                    
            except requests.exceptions.Timeout:
                print(f"Timeout error (attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    return None
                time.sleep(10)  # Wait longer before retry
                continue
                
            except Exception as e:
                print(f"API call error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(5)
                continue
        
        return None

    def analyze_batch_questions(self, questions: List[Dict[str, Any]], batch_size: int = 5) -> List[Dict[str, Any]]:
        """Analyze questions in batches with improved error handling"""
        
        analyzed_questions = []
        total_questions = len(questions)
        
        for i in range(0, total_questions, batch_size):
            batch = questions[i:i + batch_size]
            print(f"Analyzing batch {i//batch_size + 1}/{(total_questions + batch_size - 1)//batch_size}")
            
            for j, question in enumerate(batch):
                print(f"  Analyzing question {question['question_number']} ({i + j + 1}/{total_questions})")
                
                analysis = self.analyze_question_with_grok(question)
                
                if analysis:
                    # Merge analysis with original question
                    question.update(analysis)
                    question['grok_analysis_date'] = datetime.now().isoformat()
                    print(f"    ✅ Success - Got detailed analysis")
                else:
                    # Create fallback analysis
                    fallback = self._create_fallback_analysis(question)
                    question.update(fallback)
                    question['grok_analysis_date'] = datetime.now().isoformat()
                    print(f"    ⚠️  Fallback - Using generic analysis")
                
                analyzed_questions.append(question)
                
                # Rate limiting
                time.sleep(3)
            
            # Batch delay
            if i + batch_size < total_questions:
                print("Waiting between batches...")
                time.sleep(15)
        
        return analyzed_questions

    def _create_fallback_analysis(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic fallback analysis when API fails"""
        return {
            "explanation": f"Detailed explanation for question {question['question_number']}",
            "primary_type": "General Studies",
            "secondary_type": "Mixed",
            "difficulty_level": "Medium",
            "difficulty_reason": "Standard UPPSC question",
            "learning_objectives": "Basic understanding and conceptual clarity",
            "question_strategy": "Multiple choice with distractors and common misconceptions",
            "options_analysis": {
                "a": "Option A analysis",
                "b": "Option B analysis", 
                "c": "Option C analysis",
                "d": "Option D analysis"
            },
            "key_concepts": ["Concept 1", "Concept 2"],
            "common_mistakes": ["Mistake 1", "Mistake 2"],
            "elimination_technique": "Process of elimination",
            "memory_hooks": ["Hook 1", "Hook 2"],
            "related_topics": ["Topic 1", "Topic 2"],
            "exam_strategy": "1-2 minutes, assess confidence based on knowledge",
            "source_material": "Standard UPPSC sources",
            "motivation": "Important for UPPSC PCS preparation",
            "examiner_thought_process": "Testing conceptual clarity"
        }

def main():
    """Main function to run the optimized Grok analysis"""
    
    # Load the Supabase-ready questions
    with open('uppsc_questions_supabase_ready.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data['questions']
    
    # Process all 150 questions
    # questions = questions[:5]  # Commented out for full run
    
    # Initialize optimized Grok analyzer
    analyzer = OptimizedGrokAnalyzer()
    
    print(f"Starting Optimized Grok analysis for {len(questions)} questions...")
    print(f"Using model: grok-4-0709")
    print(f"Timeout: 120 seconds")
    print(f"Max retries: 3")
    print(f"Optimized fields: 17 (reduced from 25)")
    
    # Analyze questions
    analyzed_questions = analyzer.analyze_batch_questions(questions, batch_size=5)
    
    # Create final output
    final_data = {
        "metadata": {
            "source": "UPPSC_2024_Prelims_GS1",
            "analysis_date": datetime.now().isoformat(),
            "total_questions": len(analyzed_questions),
            "exam_type": "UPPSC",
            "year": 2024,
            "section": "UPPSC_Prelims_GS1",
            "analysis_method": "Grok-4_AI_Optimized",
            "note": "Optimized analysis with streamlined fields (17 instead of 25), latest model, 120s timeout, and retry logic"
        },
        "questions": analyzed_questions
    }
    
    # Save the analyzed data
    with open('uppsc_questions_grok_optimized.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Analysis complete! Saved {len(analyzed_questions)} analyzed questions")
    print(f"📁 Output file: uppsc_questions_grok_optimized.json")

if __name__ == "__main__":
    main() 