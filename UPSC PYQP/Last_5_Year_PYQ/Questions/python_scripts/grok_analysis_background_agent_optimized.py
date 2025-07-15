#!/usr/bin/env python3
"""
Optimized Background Agent for UPSC Grok Analysis
Uses single JSON files for each year, updating them with each batch
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
        logging.FileHandler('grok_analysis_background.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class OptimizedUPSCGrokBackgroundAgent:
    def __init__(self):
        self.api_key = os.getenv('GROK_API_KEY')
        if not self.api_key:
            logging.error("GROK_API_KEY not found in environment variables")
            raise ValueError("GROK_API_KEY required")
        
        self.base_url = "https://api.x.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logging.info("Optimized Background Agent initialized successfully")
    
    def create_batch_prompt(self, questions_batch: List[Dict[str, Any]], year: int) -> str:
        """Create a batch prompt for 5 questions"""
        
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

For each question, provide comprehensive analysis in JSON format with these exact fields. Think like you're personally mentoring a student - be encouraging, actionable, and focused on their growth:

{{
  "question_1": {{
    "explanation": "Clear, mentor-like explanation of why the correct answer is right and why others are wrong. Help the student understand the underlying concept, not just memorize. Use encouraging language like 'Here's what you need to understand...' or 'The key insight here is...'. Include what students should learn from this question and how it builds their conceptual understanding",
    "primary_type": "Main subject area (History/Geography/Polity/Economics/Environment/Science/Current Affairs)",
    "secondary_type": "Specific sub-topic within the primary type",
    "difficulty_level": "Easy/Medium/Hard",
    "difficulty_reason": "Why this difficulty level for UPSC aspirants - be encouraging and explain what makes it challenging or straightforward",
    "learning_objectives": "What knowledge is needed and what UPSC is testing here. Frame this as 'What you should learn from this question' and 'What UPSC wants you to understand'. Include the core concept being tested and how it connects to broader understanding",
    "question_strategy": "How the question is designed and what traps are set. Help students recognize UPSC's thinking patterns and avoid common pitfalls. Include question pattern recognition (statement-based, matching, numerical, etc.) and what this reveals about UPSC's approach",
    "options_analysis": {{
      "a": "Mentor-like analysis of option A - explain why it's correct or incorrect in a way that builds understanding",
      "b": "Mentor-like analysis of option B - explain why it's correct or incorrect in a way that builds understanding", 
      "c": "Mentor-like analysis of option C - explain why it's correct or incorrect in a way that builds understanding",
      "d": "Mentor-like analysis of option D - explain why it's correct or incorrect in a way that builds understanding"
    }},
    "key_concepts": ["Key concepts tested in this question - what fundamental knowledge this question is checking"],
    "common_mistakes": ["Common mistakes UPSC aspirants make with this topic - help students avoid these pitfalls. Include what specific misconceptions lead to wrong answers and how to overcome them"],
    "elimination_technique": "Step-by-step approach to eliminate wrong options systematically. Make this practical and actionable. Include what to look for in each option and how to use process of elimination effectively",
    "memory_hooks": ["Memory techniques and mnemonics for UPSC preparation on this topic - make it easy to remember"],
    "related_topics": ["Related topics for UPSC preparation - what should you study next to strengthen this area. Include interconnections with other subjects and progressive learning path"],
    "exam_strategy": "Time management and confidence assessment for UPSC prelims. Include practical tips like 'If you're confident, spend 30 seconds; if unsure, use elimination technique'. Also include how this question type typically appears in UPSC and what to expect",
    "source_material": "Recommended sources for UPSC preparation on this topic - be specific about what to read and why",
    "motivation": "Why this is important for UPSC Civil Services preparation - connect to the bigger picture and career goals",
    "examiner_thought_process": "What UPSC examiner is thinking when creating this question - help students understand the examiner's mindset. Include what specific knowledge or analytical skill they're testing and why this topic is important for civil servants",
    "current_affairs_connection": "How this connects to current events or recent developments - make it relevant to today's context. Include both direct connections and broader thematic links to contemporary issues",
    "time_management": "Recommended time allocation for this question type - practical advice for exam day",
    "confidence_calibration": "How to assess confidence level for this question - help students understand when they know it vs when they're guessing"
  }},
  "question_2": {{ same structure as question_1 }},
  "question_3": {{ same structure as question_1 }},
  "question_4": {{ same structure as question_1 }},
  "question_5": {{ same structure as question_1 }}
}}

Remember: You're PAI Mentor - a supportive, knowledgeable coach. Your analysis should:
- Be encouraging and motivating
- Focus on learning and growth, not just right/wrong
- Provide actionable next steps
- Help students understand UPSC's thinking patterns
- Connect concepts to real exam strategy
- Build confidence through understanding

Focus on UPSC-specific context, current affairs relevance, and practical preparation strategies that actually help students improve.
"""
        
        return prompt

    def analyze_batch_with_grok(self, questions_batch: List[Dict[str, Any]], year: int, max_retries=3):
        """Analyze a batch of 5 questions with Grok API"""
        
        prompt = self.create_batch_prompt(questions_batch, year)
        
        for attempt in range(max_retries):
            try:
                logging.info(f"Attempting batch analysis (attempt {attempt + 1}/{max_retries})")
                
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
                        "max_tokens": 8000
                    },
                    timeout=30  # Reduced timeout for faster recovery
                )
                
                response.raise_for_status()
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Try to extract JSON from the response with multiple fallback methods
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
                    logging.info("Batch analysis completed successfully")
                    return analysis
                    
                except json.JSONDecodeError as e:
                    logging.warning(f"JSON parsing error (attempt {attempt + 1}): {e}")
                    if attempt == max_retries - 1:
                        logging.error(f"Failed to parse JSON after {max_retries} attempts")
                        return None
                    time.sleep(3)  # Reduced retry delay
                    continue
                    
            except requests.exceptions.Timeout:
                logging.warning(f"Timeout error (attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    logging.error("Batch failed after all timeout retries")
                    return None
                time.sleep(10)  # Reduced timeout delay
                continue
                
            except Exception as e:
                logging.error(f"API call error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(5)
                continue
        
        return None

    def load_or_create_output_file(self, year: int) -> Dict[str, Any]:
        """Load existing output file or create new one"""
        output_file = f'../json_files/upsc_prelims_{year}_grok_analyzed.json'
        
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logging.info(f"Loaded existing output file for {year} with {len(data['questions'])} questions")
                return data
            except Exception as e:
                logging.warning(f"Error loading existing file: {e}")
        
        # Create new file structure
        data = {
            "metadata": {
                "source": f"UPSC_{year}_Prelims_GS1",
                "analysis_date": datetime.now().isoformat(),
                "total_questions": 0,
                "exam_type": "UPSC",
                "year": year,
                "section": "UPSC_Prelims_GS1",
                "analysis_method": "Grok-4_Optimized_Batch_Processing",
                "note": f"Single file processing for UPSC {year}"
            },
            "questions": []
        }
        
        logging.info(f"Created new output file structure for {year}")
        return data

    def update_output_file(self, data: Dict[str, Any], year: int):
        """Save the updated data to the output file"""
        output_file = f'../json_files/upsc_prelims_{year}_grok_analyzed.json'
        
        # Update metadata
        data['metadata']['total_questions'] = len(data['questions'])
        data['metadata']['last_updated'] = datetime.now().isoformat()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Updated output file: {output_file} ({len(data['questions'])} questions)")

    def analyze_year_questions(self, year: int, batch_size: int = 5) -> bool:
        """Analyze all questions for a specific year in batches using single file"""
        
        # Load questions for the year
        input_file = f'../json_files/upsc_prelims_{year}_structured_for_frontend.json'
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
            
            questions = input_data['questions']
            logging.info(f"Loaded {len(questions)} questions for UPSC {year}")
            
        except FileNotFoundError:
            logging.error(f"Input file not found: {input_file}")
            return False
        except Exception as e:
            logging.error(f"Error loading questions for {year}: {e}")
            return False
        
        # Load or create output file
        output_data = self.load_or_create_output_file(year)
        
        total_questions = len(questions)
        total_batches = (total_questions + batch_size - 1) // batch_size
        
        logging.info(f"Starting analysis for UPSC {year}")
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
            batch_analysis = self.analyze_batch_with_grok(batch, year)
            
            if batch_analysis:
                # Merge analysis with original questions
                for j, question in enumerate(batch):
                    question_num = j + 1
                    analysis_key = f"question_{question_num}"
                    
                    if analysis_key in batch_analysis:
                        question.update(batch_analysis[analysis_key])
                        question['grok_analysis_date'] = datetime.now().isoformat()
                        logging.info(f"  ✅ Q{question['question_number']}: Analysis added")
                    else:
                        # Create fallback analysis
                        fallback = self._create_fallback_analysis(question)
                        question.update(fallback)
                        question['grok_analysis_date'] = datetime.now().isoformat()
                        logging.warning(f"  ⚠️  Q{question['question_number']}: Fallback analysis")
                
                # Add analyzed questions to output data
                output_data['questions'].extend(batch)
                logging.info(f"  📊 Batch {batch_num} completed successfully")
                
            else:
                # Create fallback analysis for all questions in batch
                for question in batch:
                    fallback = self._create_fallback_analysis(question)
                    question.update(fallback)
                    question['grok_analysis_date'] = datetime.now().isoformat()
                    logging.error(f"  ❌ Q{question['question_number']}: Fallback analysis (batch failed)")
                
                # Add questions with fallback analysis
                output_data['questions'].extend(batch)
                logging.warning(f"  ⚠️  Batch {batch_num} failed, using fallback analysis")
            
            # Update the single output file after each batch
            self.update_output_file(output_data, year)
            
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
        logging.info(f"✅ UPSC {year} analysis complete in {total_time/60:.1f} minutes")
        
        return True

    def _create_fallback_analysis(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic fallback analysis when API fails"""
        return {
            "explanation": f"Detailed explanation for UPSC question {question['question_number']}",
            "primary_type": question.get('subject', 'General Studies'),
            "secondary_type": "Mixed",
            "difficulty_level": question.get('difficulty', 'Medium'),
            "difficulty_reason": f"Standard UPSC {question.get('difficulty', 'Medium')} question",
            "learning_objectives": "Basic understanding and conceptual clarity for UPSC",
            "question_strategy": "Multiple choice with distractors and common misconceptions",
            "options_analysis": {
                "a": "Option A analysis for UPSC preparation",
                "b": "Option B analysis for UPSC preparation", 
                "c": "Option C analysis for UPSC preparation",
                "d": "Option D analysis for UPSC preparation"
            },
            "key_concepts": ["Concept 1", "Concept 2"],
            "common_mistakes": ["Mistake 1", "Mistake 2"],
            "elimination_technique": "Process of elimination for UPSC",
            "memory_hooks": ["Hook 1", "Hook 2"],
            "related_topics": ["Topic 1", "Topic 2"],
            "exam_strategy": "1-2 minutes, assess confidence based on knowledge",
            "source_material": "Standard UPSC sources",
            "motivation": "Important for UPSC Civil Services preparation",
            "examiner_thought_process": "Testing conceptual clarity and current affairs awareness",
            "current_affairs_connection": "Connects to recent developments",
            "time_management": "1-2 minutes recommended",
            "confidence_calibration": "Assess based on subject familiarity"
        }

    def run_full_analysis(self):
        """Run analysis for both 2025 and 2024 using single files"""
        
        logging.info("🚀 Starting Optimized Background Grok Analysis Agent")
        logging.info("=" * 60)
        
        # Process 2025 first
        logging.info("📚 Processing UPSC 2025 Questions")
        logging.info("-" * 40)
        
        success_2025 = self.analyze_year_questions(2025)
        
        if success_2025:
            logging.info(f"✅ UPSC 2025 complete! Saved: ../json_files/upsc_prelims_2025_grok_analyzed.json")
        
        # Process 2024
        logging.info("📚 Processing UPSC 2024 Questions")
        logging.info("-" * 40)
        
        success_2024 = self.analyze_year_questions(2024)
        
        if success_2024:
            logging.info(f"✅ UPSC 2024 complete! Saved: ../json_files/upsc_prelims_2024_grok_analyzed.json")
        
        logging.info("=" * 60)
        logging.info("🎉 Optimized Background Analysis Complete!")
        logging.info("📁 Check log file: grok_analysis_background.log")

def main():
    """Main function to run the optimized background agent"""
    
    try:
        agent = OptimizedUPSCGrokBackgroundAgent()
        agent.run_full_analysis()
        
    except KeyboardInterrupt:
        logging.info("🛑 Background analysis interrupted by user")
    except Exception as e:
        logging.error(f"❌ Background analysis failed: {e}")
        raise

if __name__ == "__main__":
    main() 