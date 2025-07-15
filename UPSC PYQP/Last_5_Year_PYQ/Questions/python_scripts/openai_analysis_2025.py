#!/usr/bin/env python3
"""
OpenAI GPT-4.1 Analysis for UPSC 2025 Questions
Uses the same prompt structure as Grok for comparison
"""

import json
import os
import time
import requests
import logging
from datetime import datetime
from typing import Dict, List, Any
import sys

# Load environment variables
from dotenv import load_dotenv
load_dotenv('../../../../.env')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('openai_analysis_2025.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class OpenAIUPSCAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logging.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY required")
        
        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logging.info("OpenAI Analyzer initialized successfully")
    
    def create_batch_prompt(self, questions_batch: List[Dict[str, Any]], year: int) -> str:
        """Create a batch prompt for 5 questions with enhanced option analysis"""
        
        # Format questions for batch processing
        questions_text = ""
        for i, question in enumerate(questions_batch, 1):
            options_text = ""
            for option in question['options']:
                options_text += f"{option['letter']}. {option['text']}\n"
            
            questions_text += f"""
QUESTION {i}:
Question Number: {question['question_number']}
Subject: {question['subject']}
Difficulty: {question['difficulty']}
Type: {question['type']}
Correct Answer: {question.get('correct_answer', 'Not provided')}

Question: {question['question_text']}

Options:
{options_text}
"""
        
        prompt = f"""
You are PAI Mentor - an expert UPSC Civil Services mentor and coach who provides personalized guidance to aspirants. You're not just analyzing questions; you're mentoring students to understand, learn, and improve their preparation strategy.

SHARED CONTEXT FOR ALL QUESTIONS:
- UPSC {year} Prelims examination
- Focus on mentorship and actionable insights
- Help students understand concepts, not just memorize
- Provide encouraging, growth-focused guidance
- Connect to broader UPSC preparation strategy

QUESTIONS TO ANALYZE:
{questions_text}

For each question, provide comprehensive analysis in JSON format with TWO sections:

1. STUDENT_FACING_ANALYSIS: Key insights for immediate student consumption
2. DETAILED_BACKEND_ANALYSIS: Comprehensive data for future LLM-powered feedback and micro-analysis

{{
  "question_1": {{
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
  }},
  "question_2": {{ same structure as question_1 }},
  "question_3": {{ same structure as question_1 }},
  "question_4": {{ same structure as question_1 }},
  "question_5": {{ same structure as question_1 }}
}}

Focus on providing actionable insights that would help UPSC aspirants understand the question better and improve their preparation strategy. For the elimination techniques, be specific and practical. Make option analysis detailed enough to provide personalized feedback based on which option a student chooses.
"""
        
        return prompt

    def analyze_batch_with_openai(self, questions_batch: List[Dict[str, Any]], year: int, max_retries=3):
        """Analyze a batch of 5 questions with OpenAI GPT-4.1"""
        
        prompt = self.create_batch_prompt(questions_batch, year)
        
        for attempt in range(max_retries):
            try:
                logging.info(f"Attempting batch analysis with OpenAI (attempt {attempt + 1}/{max_retries})")
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.1,
                        "max_tokens": 8000
                    },
                    timeout=60
                )
                
                response.raise_for_status()
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Try to extract JSON from the response
                try:
                    # Method 1: Look for JSON content between triple backticks
                    if '```json' in content:
                        json_start = content.find('```json') + 7
                        json_end = content.find('```', json_start)
                        json_content = content[json_start:json_end].strip()
                    elif '```' in content:
                        # Method 2: Look for any code block
                        json_start = content.find('```') + 3
                        json_end = content.find('```', json_start)
                        json_content = content[json_start:json_end].strip()
                    else:
                        # Method 3: Try to find JSON content directly
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        json_content = content[json_start:json_end]
                    
                    # Clean up the JSON content
                    json_content = json_content.strip()
                    
                    # Remove any leading/trailing text that might break JSON
                    if not json_content.startswith('{'):
                        json_start = json_content.find('{')
                        json_content = json_content[json_start:]
                    
                    analysis = json.loads(json_content)
                    logging.info("OpenAI batch analysis completed successfully")
                    return analysis
                    
                except json.JSONDecodeError as e:
                    logging.warning(f"JSON parsing error (attempt {attempt + 1}): {e}")
                    if attempt == max_retries - 1:
                        logging.error(f"Failed to parse JSON after {max_retries} attempts")
                        return None
                    time.sleep(3)
                    continue
                    
            except requests.exceptions.Timeout:
                logging.warning(f"Timeout error (attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    logging.error("Batch failed after all timeout retries")
                    return None
                time.sleep(10)
                continue
                
            except Exception as e:
                logging.error(f"API call error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(5)
                continue
        
        return None

    def analyze_year_questions(self, year: int, batch_size: int = 5) -> List[Dict[str, Any]]:
        """Analyze all questions for a specific year in batches"""
        
        # Load questions for the year
        input_file = f'../json_files/upsc_prelims_{year}_structured_for_frontend.json'
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            questions = data['questions']
            logging.info(f"Loaded {len(questions)} questions for UPSC {year}")
            
        except FileNotFoundError:
            logging.error(f"Input file not found: {input_file}")
            return []
        except Exception as e:
            logging.error(f"Error loading questions for {year}: {e}")
            return []
        
        analyzed_questions = []
        total_questions = len(questions)
        total_batches = (total_questions + batch_size - 1) // batch_size
        
        logging.info(f"Starting OpenAI analysis for UPSC {year}")
        logging.info(f"Total questions: {total_questions}")
        logging.info(f"Batch size: {batch_size}")
        logging.info(f"Total batches: {total_batches}")
        logging.info(f"Estimated API calls: {total_batches} (vs {total_questions} individual calls)")
        
        start_time = time.time()
        
        for i in range(0, total_questions, batch_size):
            batch = questions[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            logging.info(f"Processing batch {batch_num}/{total_batches} (Questions {i+1}-{min(i+batch_size, total_questions)})")
            
            # Analyze batch
            batch_analysis = self.analyze_batch_with_openai(batch, year)
            
            if batch_analysis:
                # Merge analysis with original questions
                for j, question in enumerate(batch):
                    question_num = j + 1
                    analysis_key = f"question_{question_num}"
                    
                    if analysis_key in batch_analysis:
                        question.update(batch_analysis[analysis_key])
                        question['openai_analysis_date'] = datetime.now().isoformat()
                        logging.info(f"  ✅ Q{question['question_number']}: OpenAI analysis added")
                    else:
                        # Create fallback analysis
                        fallback = self._create_fallback_analysis(question)
                        question.update(fallback)
                        question['openai_analysis_date'] = datetime.now().isoformat()
                        logging.warning(f"  ⚠️  Q{question['question_number']}: Fallback analysis")
                
                analyzed_questions.extend(batch)
                logging.info(f"  📊 Batch {batch_num} completed successfully")
                
            else:
                # Create fallback analysis for all questions in batch
                for question in batch:
                    fallback = self._create_fallback_analysis(question)
                    question.update(fallback)
                    question['openai_analysis_date'] = datetime.now().isoformat()
                    logging.error(f"  ❌ Q{question['question_number']}: Fallback analysis (batch failed)")
                
                analyzed_questions.extend(batch)
                logging.warning(f"  ⚠️  Batch {batch_num} failed, using fallback analysis")
            
            # Save progress after each batch
            self._save_progress(analyzed_questions, year, batch_num, total_batches)
            
            # Calculate and log progress
            elapsed_time = time.time() - start_time
            avg_time_per_batch = elapsed_time / batch_num
            estimated_remaining = avg_time_per_batch * (total_batches - batch_num)
            
            logging.info(f"  ⏱️  Progress: {batch_num}/{total_batches} batches ({batch_num/total_batches*100:.1f}%)")
            logging.info(f"  ⏱️  Elapsed: {elapsed_time/60:.1f} minutes, Estimated remaining: {estimated_remaining/60:.1f} minutes")
            
            # Rate limiting between batches
            if i + batch_size < total_questions:
                logging.info("  ⏳ Waiting 10 seconds before next batch...")
                time.sleep(10)
        
        total_time = time.time() - start_time
        logging.info(f"✅ UPSC {year} OpenAI analysis complete in {total_time/60:.1f} minutes")
        
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

    def _save_progress(self, analyzed_questions: List[Dict[str, Any]], year: int, batch_num: int, total_batches: int):
        """Save progress after each batch"""
        
        # Create progress data
        progress_data = {
            "metadata": {
                "source": f"UPSC_{year}_Prelims_GS1",
                "analysis_date": datetime.now().isoformat(),
                "total_questions": len(analyzed_questions),
                "exam_type": "UPSC",
                "year": year,
                "section": "UPSC_Prelims_GS1",
                "analysis_method": "OpenAI_GPT4o_Mini_Batch_Processing",
                "batch_progress": f"{batch_num}/{total_batches}",
                "note": f"OpenAI analysis with {len(analyzed_questions)} questions analyzed so far"
            },
            "questions": analyzed_questions
        }
        
        # Save to single file per year (updates with each batch)
        output_file = f'../json_files/upsc_prelims_{year}_openai_analyzed.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"  💾 Updated output file: {output_file} ({len(analyzed_questions)} questions)")

    def run_analysis(self):
        """Run OpenAI analysis for 2025"""
        
        logging.info("🚀 Starting OpenAI GPT-4.1 Analysis for UPSC 2025")
        logging.info("=" * 60)
        
        # Process 2025
        logging.info("📚 Processing UPSC 2025 Questions with OpenAI")
        logging.info("-" * 40)
        
        questions_2025 = self.analyze_year_questions(2025)
        
        if questions_2025:
            logging.info(f"✅ UPSC 2025 OpenAI analysis complete! Processed {len(questions_2025)} questions")
            logging.info("📁 Check output file: ../json_files/upsc_prelims_2025_openai_analyzed.json")
        else:
            logging.error("❌ UPSC 2025 OpenAI analysis failed")

def main():
    """Main function to run the OpenAI analysis"""
    
    print("🎯 OpenAI GPT-4.1 Analysis for UPSC 2025 Questions")
    print("=" * 60)
    
    analyzer = OpenAIUPSCAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main() 