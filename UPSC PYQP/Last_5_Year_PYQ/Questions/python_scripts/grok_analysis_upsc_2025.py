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

Question Number: {question_data['question_number']}
Subject: {question_data['subject']}
Difficulty: {question_data['difficulty']}
Type: {question_data['type']}
Correct Answer: {question_data.get('correct_answer', 'Not provided')}

Question: {question_data['question_text']}

Options:
{options_text}

As a PAI Mentor coach, provide comprehensive analysis in JSON format with these exact fields. Think like you're personally mentoring a student - be encouraging, actionable, and focused on their growth:

{{
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

def main():
    """Main function to run the UPSC Grok analysis"""
    
    # Load the UPSC 2025 questions with answers
    input_file = '../json_files/upsc_prelims_2025_structured_for_frontend.json'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data['questions']
    
    # Process all 100 questions
    # questions = questions[:5]  # Uncomment for testing with first 5 questions
    
    # Initialize UPSC Grok analyzer
    analyzer = UPSCGrokAnalyzer()
    
    print(f"Starting UPSC 2025 Grok analysis for {len(questions)} questions...")
    print(f"Using model: grok-4-0709")
    print(f"Timeout: 120 seconds")
    print(f"Max retries: 3")
    print(f"Optimized fields: 18 comprehensive analysis fields")
    
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
            "analysis_method": "Grok-4_AI_Optimized",
            "note": "Comprehensive UPSC analysis with 18 fields, latest model, 120s timeout, and retry logic"
        },
        "questions": analyzed_questions
    }
    
    # Save the analyzed data
    output_file = '../json_files/upsc_prelims_2025_grok_analyzed.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Analysis complete! Saved {len(analyzed_questions)} analyzed questions")
    print(f"📁 Output file: {output_file}")

if __name__ == "__main__":
    main() 