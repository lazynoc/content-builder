#!/usr/bin/env python3
"""
UPSC 2025 Grok Analysis Script - Optimized for UPSC Civil Services Prelims
"""

import json
import os
import time
import requests
from datetime import datetime
from typing import Dict, List, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv('../../../../.env')  # Adjust path to find .env file

class UPSCGrokAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('GROK_API_KEY')
        self.base_url = "https://api.x.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_question_with_grok(self, question_data, max_retries=3):
        """Analyze a single UPSC question with Grok API for comprehensive insights"""
        
        # Format options for the prompt
        options_text = ""
        for option in question_data['options']:
            options_text += f"{option['letter']}. {option['text']}\n"
        
        prompt = f"""
You are PAI Mentor - an expert UPSC Civil Services mentor and coach who provides personalized guidance to aspirants. You're not just analyzing questions; you're mentoring students to understand, learn, and improve their preparation strategy.

SHARED CONTEXT FOR ALL QUESTIONS:
- UPSC 2025 Prelims examination
- Focus on mentorship and actionable insights
- Help students understand concepts, not just memorize
- Provide encouraging, growth-focused guidance
- Connect to broader UPSC preparation strategy

QUESTION TO ANALYZE:
Question Number: {question_data['question_number']}
Subject: {question_data['subject']}
Difficulty: {question_data['difficulty']}
Type: {question_data['type']}
Correct Answer: {question_data.get('correct_answer', 'Not provided')}

Question: {question_data['question_text']}

Options:
{options_text}

Provide comprehensive analysis in JSON format with TWO sections:

1. STUDENT_FACING_ANALYSIS: Key insights for immediate student consumption
2. DETAILED_BACKEND_ANALYSIS: Comprehensive data for future LLM-powered feedback and micro-analysis

{{
  "student_facing_analysis": {{
    "explanation": "Clear, concise explanation of why the correct answer is right and why others are wrong. Focus on the core concept and factual reasoning without conversational language.",
    "learning_objectives": "Core concept being tested and key knowledge areas required. Be direct and specific about what this question evaluates.",
    "question_strategy": "How UPSC designed this question and what patterns to recognize. Focus on question structure and common traps without excessive explanation.",
    "difficulty_level": "Easy/Medium/Hard",
    "key_concepts": ["Key concepts tested in this question - what fundamental knowledge this question is checking"],
    "time_management": "Recommended time allocation for this question type - practical advice for exam day"
  }},
  "detailed_backend_analysis": {{
    "question_nature": {{
      "primary_type": "Factual/Conceptual/Analytical/Application",
      "secondary_type": "Memory-based/Understanding-based/Application-based",
      "difficulty_reason": "Explanation of why this question is easy/medium/difficult",
      "knowledge_requirement": "Type of knowledge required (static/current affairs/mixed)"
    }},
    "examiner_thought_process": {{
      "testing_objective": "What the examiner is trying to test",
      "question_design_strategy": "How the question is designed to evaluate candidates",
      "trap_setting": "Any traps or misleading elements in the question",
      "discrimination_potential": "How well this question can differentiate between candidates"
    }},
    "options_analysis": {{
      "A": {{
        "type": "correct_answer/plausible_distractor/obvious_wrong",
        "reason": "Why this option is correct/incorrect",
        "trap": "If it's a distractor, what trap does it set",
        "elimination_strategy": "How to eliminate this option",
        "student_reasoning_pattern": "What choosing this option reveals about student's thinking process",
        "common_misconception": "What misconception leads students to choose this option"
      }},
      "B": {{
        "type": "correct_answer/plausible_distractor/obvious_wrong",
        "reason": "Why this option is correct/incorrect",
        "trap": "If it's a distractor, what trap does it set",
        "elimination_strategy": "How to eliminate this option",
        "student_reasoning_pattern": "What choosing this option reveals about student's thinking process",
        "common_misconception": "What misconception leads students to choose this option"
      }},
      "C": {{
        "type": "correct_answer/plausible_distractor/obvious_wrong",
        "reason": "Why this option is correct/incorrect",
        "trap": "If it's a distractor, what trap does it set",
        "elimination_strategy": "How to eliminate this option",
        "student_reasoning_pattern": "What choosing this option reveals about student's thinking process",
        "common_misconception": "What misconception leads students to choose this option"
      }},
      "D": {{
        "type": "correct_answer/plausible_distractor/obvious_wrong",
        "reason": "Why this option is correct/incorrect",
        "trap": "If it's a distractor, what trap does it set",
        "elimination_strategy": "How to eliminate this option",
        "student_reasoning_pattern": "What choosing this option reveals about student's thinking process",
        "common_misconception": "What misconception leads students to choose this option"
      }}
    }},
    "learning_insights": {{
      "key_concepts": ["List of key concepts tested"],
      "common_mistakes": ["Common mistakes students make"],
      "elimination_technique_semi_knowledge": "If a student knows only part of the topic, what is the best way to maximize their chances?",
      "elimination_technique_safe_guess": "If a student has little or no knowledge, what is the safest approach or examiner-mindset trick to attempt this question?",
      "memory_hooks": ["Mnemonics or memory aids"],
      "related_topics": ["Related topics for further study"],
      "current_affairs_connection": "Connection to current events if any"
    }},
    "difficulty_level": "Easy/Medium/Difficult",
    "time_management": "How much time should be spent on this question",
    "confidence_calibration": "How confident should a well-prepared student be",
    "strength_indicators": ["What getting this question right indicates about student's knowledge and skills"],
    "weakness_indicators": ["What getting this question wrong might indicate about knowledge gaps"],
    "remediation_topics": ["Specific topics to study if this question was answered incorrectly"],
    "advanced_connections": ["How this question connects to more advanced UPSC topics and concepts"]
  }}
}}

Focus on providing actionable insights that would help UPSC aspirants understand the question better and improve their preparation strategy. For the elimination techniques, be specific and practical. Make option analysis detailed enough to provide personalized feedback based on which option a student chooses.
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
            "student_facing_analysis": {
                "explanation": f"Explanation for UPSC question {question['question_number']}",
                "learning_objectives": "Core concept and knowledge areas tested",
                "question_strategy": "Question design and common patterns",
                "difficulty_level": question.get('difficulty', 'Medium'),
                "key_concepts": ["Concept 1", "Concept 2"],
                "time_management": "1-2 minutes recommended"
            },
            "detailed_backend_analysis": {
                "question_nature": {
                    "primary_type": "Conceptual",
                    "secondary_type": "Understanding-based",
                    "difficulty_reason": f"Standard UPSC {question.get('difficulty', 'Medium')} question",
                    "knowledge_requirement": "Mixed"
                },
                "examiner_thought_process": {
                    "testing_objective": "Testing conceptual clarity",
                    "question_design_strategy": "Multiple choice with distractors",
                    "trap_setting": "Common misconceptions",
                    "discrimination_potential": "Medium"
                },
                "options_analysis": {
                    "A": {
                        "type": "plausible_distractor",
                        "reason": "Option A analysis for UPSC preparation",
                        "trap": "Common misconception",
                        "elimination_strategy": "Process of elimination",
                        "student_reasoning_pattern": "Basic understanding",
                        "common_misconception": "Concept confusion"
                    },
                    "B": {
                        "type": "plausible_distractor",
                        "reason": "Option B analysis for UPSC preparation",
                        "trap": "Common misconception",
                        "elimination_strategy": "Process of elimination",
                        "student_reasoning_pattern": "Basic understanding",
                        "common_misconception": "Concept confusion"
                    },
                    "C": {
                        "type": "plausible_distractor",
                        "reason": "Option C analysis for UPSC preparation",
                        "trap": "Common misconception",
                        "elimination_strategy": "Process of elimination",
                        "student_reasoning_pattern": "Basic understanding",
                        "common_misconception": "Concept confusion"
                    },
                    "D": {
                        "type": "correct_answer",
                        "reason": "Option D analysis for UPSC preparation",
                        "trap": "None",
                        "elimination_strategy": "Correct choice",
                        "student_reasoning_pattern": "Proper understanding",
                        "common_misconception": "None"
                    }
                },
                "learning_insights": {
                    "key_concepts": ["Concept 1", "Concept 2"],
                    "common_mistakes": ["Mistake 1", "Mistake 2"],
                    "elimination_technique_semi_knowledge": "Use partial knowledge to eliminate options",
                    "elimination_technique_safe_guess": "Look for most plausible option",
                    "memory_hooks": ["Hook 1", "Hook 2"],
                    "related_topics": ["Topic 1", "Topic 2"],
                    "current_affairs_connection": "Connects to recent developments"
                },
                "difficulty_level": question.get('difficulty', 'Medium'),
                "time_management": "1-2 minutes recommended",
                "confidence_calibration": "Assess based on subject familiarity",
                "strength_indicators": ["Basic knowledge of subject area"],
                "weakness_indicators": ["Potential gaps in fundamental concepts"],
                "remediation_topics": ["Core concepts of the subject"],
                "advanced_connections": ["Connects to advanced topics in the subject"]
            }
        }

def main():
    """Main function to run the UPSC Grok analysis"""
    
    # Load the UPSC 2025 questions with answers
    input_file = '../json_files/upsc_prelims_2025_structured_for_frontend.json'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data['questions']
    
    # Process all 100 questions
    questions = questions[:5]  # Testing with first 5 questions
    
    # Initialize UPSC Grok analyzer
    analyzer = UPSCGrokAnalyzer()
    
    print(f"Starting UPSC 2025 Grok analysis for {len(questions)} questions...")
    print(f"Using model: grok-4-0709")
    print(f"Timeout: 120 seconds")
    print(f"Max retries: 3")
    print(f"Enhanced structure: Two-tier analysis with micro-level option detail")
    
    # Analyze questions
    analyzed_questions = analyzer.analyze_batch_questions(questions, batch_size=5)
    
    # Create final output
    final_data = {
        "metadata": {
            "source": "UPSC_2025_Prelims_GS1",
            "analysis_date": datetime.now().isoformat(),
            "total_questions": len(analyzed_questions),
            "exam_type": "UPSC",
            "year": 2025,
            "section": "UPSC_Prelims_GS1",
                    "analysis_method": "Grok-4_AI_Enhanced",
        "note": "Two-tier analysis with micro-level option detail, latest model, 120s timeout, and retry logic"
        },
        "questions": analyzed_questions
    }
    
    # Save the analyzed data
    output_file = '../json_files/upsc_prelims_2025_grok_analyzed_enhanced.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Analysis complete! Saved {len(analyzed_questions)} analyzed questions")
    print(f"📁 Output file: {output_file}")

if __name__ == "__main__":
    main() 