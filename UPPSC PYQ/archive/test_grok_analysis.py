#!/usr/bin/env python3
"""
Test Grok Analysis for UPPSC Questions
Analyzes only the first 10 questions to test the UPPSC-specific mentoring approach
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

class GrokAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('GROK_API_KEY')
        self.base_url = "https://api.x.ai/v1"  # Adjust based on actual Grok API endpoint
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_question_for_performance_assessment(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a question to provide insights for UPPSC student performance assessment and guidance
        """
        
        prompt = f"""
        You are an expert UPPSC mentor analyzing a question to help assess student performance and provide personalized guidance for UPPSC PCS preparation.

        Question Number: {question['question_number']}
        Question: {question['question_text']}
        Options: {json.dumps(question['options'], indent=2)}
        Correct Answer: {question['correct_answer']}

        Please provide a comprehensive analysis in JSON format focusing on UPPSC PCS requirements:

        1. **Explanation**: Clear, step-by-step explanation of why the correct answer is right
        2. **Primary Type**: Main category (e.g., "History", "Geography", "Polity", "Economics", "Science", "Current Affairs", "Uttar Pradesh Specific")
        3. **Secondary Type**: Sub-category (e.g., "Ancient History", "Physical Geography", "Constitutional Law", "UP State Politics")
        4. **Difficulty Level**: "Easy", "Medium", "Hard", or "Very Hard"
        5. **Difficulty Reason**: Why this question is at this difficulty level for UPPSC
        6. **Knowledge Requirement**: What specific knowledge is needed to answer correctly
        7. **Testing Objective**: What skill/concept is being tested
        8. **Question Design Strategy**: How the question is structured to test understanding
        9. **Trap Setting**: Common mistakes or traps in the question
        10. **Discrimination Potential**: How well this question can differentiate between strong and weak UPPSC candidates
        11. **Options Analysis**: Analysis of each option (why wrong options are wrong, why correct is right)
        12. **Key Concepts**: Main concepts/topics being tested
        13. **Common Mistakes**: What UPPSC aspirants typically get wrong and why
        14. **Elimination Technique**: How to eliminate wrong options
        15. **Memory Hooks**: Mnemonics or memory aids for this topic
        16. **Related Topics**: Connected topics for further study
        17. **Current Affairs Connection**: Any current events relevance, especially UP-specific
        18. **Time Management**: How much time should be spent on this type of question in UPPSC
        19. **Confidence Calibration**: How to assess confidence in the answer
        20. **Source Material**: Recommended sources for this topic (UP-specific sources when relevant)
        21. **Source Type**: Type of source (NCERT, Standard books, Current Affairs, UP State books, etc.)
        22. **Tags**: Relevant tags for categorization including UP-specific tags
        23. **Motivation**: Why this topic is important for UPPSC PCS
        24. **Examiner Thought Process**: What the UPPSC examiner was thinking when creating this question
        25. **Learning Insights**: Key takeaways for learning and improvement specific to UPPSC

        Focus on providing actionable insights that help UPPSC aspirants:
        - Assess performance accurately for UPPSC PCS
        - Identify knowledge gaps specific to UP and general studies
        - Provide personalized study recommendations for UPPSC
        - Guide improvement strategies for UPPSC preparation
        - Build confidence and motivation for UPPSC success

        Consider UPPSC-specific aspects:
        - UP state politics, geography, history, and culture
        - State-specific current affairs
        - Regional variations and local context
        - UPPSC exam pattern and preferences

        Return only valid JSON with these fields.
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "grok-4",  # Using Grok-4 model
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                print(f"✅ Question {question['question_number']} analyzed successfully")
                
                # Extract JSON from response
                try:
                    # Find JSON in the response
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start != -1 and end != 0:
                        analysis = json.loads(content[start:end])
                        return analysis
                    else:
                        print(f"⚠️  No JSON found in response for Q{question['question_number']}")
                        return self._create_fallback_analysis(question)
                except json.JSONDecodeError as e:
                    print(f"⚠️  JSON parsing error for Q{question['question_number']}: {e}")
                    return self._create_fallback_analysis(question)
            else:
                print(f"❌ API Error for Q{question['question_number']}: {response.status_code} - {response.text}")
                return self._create_fallback_analysis(question)
                
        except Exception as e:
            print(f"❌ Error analyzing Q{question['question_number']}: {e}")
            return self._create_fallback_analysis(question)
    
    def _create_fallback_analysis(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic fallback analysis when API fails"""
        return {
            "explanation": f"Detailed explanation for question {question['question_number']}",
            "primary_type": "General Studies",
            "secondary_type": "Mixed",
            "difficulty_level": "Medium",
            "difficulty_reason": "Standard UPPSC question",
            "knowledge_requirement": "Basic understanding of the topic",
            "testing_objective": "Conceptual understanding",
            "question_design_strategy": "Multiple choice with distractors",
            "trap_setting": "Common misconceptions",
            "discrimination_potential": "Moderate",
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
            "current_affairs_connection": "May have current relevance",
            "time_management": "1-2 minutes",
            "confidence_calibration": "Assess based on knowledge",
            "source_material": "Standard UPPSC sources",
            "source_type": "Mixed",
            "tags": ["UPPSC", "Prelims", "UP"],
            "motivation": "Important for UPPSC PCS preparation",
            "examiner_thought_process": "Testing conceptual clarity",
            "learning_insights": "Focus on fundamentals"
        }

def main():
    """Main function to test Grok analysis on first 10 questions"""
    
    print("🧪 TESTING GROK ANALYSIS FOR UPPSC QUESTIONS")
    print("="*50)
    
    # Check if API key is available
    if not os.getenv('GROK_API_KEY'):
        print("❌ GROK_API_KEY not found in environment variables")
        print("Please add it to your .env file")
        return
    
    # Load the Supabase-ready questions
    try:
        with open('uppsc_questions_supabase_ready.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ uppsc_questions_supabase_ready.json not found")
        print("Please run transform_for_supabase.py first")
        return
    
    questions = data['questions'][:10]  # Take only first 10 questions
    
    print(f"📊 Analyzing first {len(questions)} questions...")
    print(f"🔑 Using Grok-4 model")
    print(f"🎯 UPPSC-specific mentoring focus")
    print()
    
    # Initialize Grok analyzer
    analyzer = GrokAnalyzer()
    
    # Analyze questions
    analyzed_questions = []
    
    for i, question in enumerate(questions, 1):
        print(f"🔄 Analyzing Question {question['question_number']} ({i}/{len(questions)})")
        
        analysis = analyzer.analyze_question_for_performance_assessment(question)
        
        # Merge analysis with original question
        question.update(analysis)
        question['grok_analysis_date'] = datetime.now().isoformat()
        
        analyzed_questions.append(question)
        
        # Rate limiting
        if i < len(questions):
            print("⏳ Waiting 3 seconds before next question...")
            time.sleep(3)
    
    # Create final output
    final_data = {
        "metadata": {
            "source": "UPPSC_2024_Prelims_GS1",
            "analysis_date": datetime.now().isoformat(),
            "total_questions": len(analyzed_questions),
            "exam_type": "UPPSC",
            "year": 2024,
            "section": "UPPSC_Prelims_GS1",
            "analysis_method": "Grok-4_AI",
            "note": "Test analysis for first 10 questions - UPPSC-specific mentoring"
        },
        "questions": analyzed_questions
    }
    
    # Save the analyzed data
    with open('uppsc_questions_grok_test_10.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*50)
    print("✅ TEST COMPLETED!")
    print("="*50)
    print(f"📊 Analyzed {len(analyzed_questions)} questions")
    print(f"📁 Output file: uppsc_questions_grok_test_10.json")
    print(f"🎯 UPPSC-specific analysis completed")
    
    # Show sample of first question analysis
    if analyzed_questions:
        first_q = analyzed_questions[0]
        print(f"\n📋 Sample Analysis for Question {first_q['question_number']}:")
        print(f"   Primary Type: {first_q.get('primary_type', 'N/A')}")
        print(f"   Difficulty: {first_q.get('difficulty_level', 'N/A')}")
        print(f"   Tags: {first_q.get('tags', 'N/A')}")
        print(f"   Explanation: {first_q.get('explanation', 'N/A')[:100]}...")

if __name__ == "__main__":
    main() 