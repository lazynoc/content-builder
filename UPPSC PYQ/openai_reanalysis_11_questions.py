#!/usr/bin/env python3
"""
Script to re-analyze question 86 and 10 poor quality questions using OpenAI
"""

import json
import os
import time
import openai
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv('../.env')

# Configure OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def analyze_question_with_openai(question_data):
    """Analyze a single question using OpenAI"""
    
    question_text = question_data['question_text']
    options = question_data['options']
    correct_answer = question_data['correct_answer']
    
    prompt = f"""
You are an expert UPPSC (Uttar Pradesh Public Service Commission) exam mentor. Analyze this question and provide detailed insights for UPPSC aspirants.

Question: {question_text}

Options:
a) {options['a']}
b) {options['b']}
c) {options['c']}
d) {options['d']}

Correct Answer: {correct_answer}

Please provide a comprehensive analysis in JSON format with the following fields:

{{
    "subject": "Main subject area of the question",
    "topic": "Specific topic within the subject",
    "difficulty_level": "Easy/Medium/Hard",
    "question_type": "Type of question (e.g., factual, analytical, matching, etc.)",
    "key_concepts": ["List of key concepts tested"],
    "explanation": "Detailed explanation of the correct answer",
    "why_others_are_wrong": "Why other options are incorrect",
    "uppsc_relevance": "Why this topic is important for UPPSC",
    "related_topics": ["Related topics for UPPSC preparation"],
    "study_tips": "How to prepare for similar questions",
    "examiner_thought_process": "What the examiner is testing",
    "common_mistakes": "Common mistakes students make",
    "time_management": "How much time to spend on such questions",
    "confidence_level": "How confident should a well-prepared student be",
    "priority_level": "High/Medium/Low priority for UPPSC preparation"
}}

Focus on UPPSC-specific context and provide actionable insights for UPPSC aspirants.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert UPPSC exam mentor with deep knowledge of the syllabus and exam patterns."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=2000
        )
        
        analysis_text = response.choices[0].message.content
        if analysis_text:
            analysis_text = analysis_text.strip()
        else:
            analysis_text = ""
        
        # Try to parse JSON response
        try:
            analysis = json.loads(analysis_text)
            return {
                "success": True,
                "analysis": analysis,
                "raw_response": analysis_text
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "analysis": None,
                "raw_response": analysis_text,
                "error": "Failed to parse JSON response"
            }
            
    except Exception as e:
        return {
            "success": False,
            "analysis": None,
            "raw_response": None,
            "error": str(e)
        }

def main():
    # Load the questions
    with open('uppsc_questions_complete_final.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Questions that need re-analysis (all poor quality questions + question 86)
    questions_to_analyze = [1, 16, 18, 23, 26, 30, 31, 32, 51, 71, 86]  # All 11 questions
    
    results = []
    
    for question_num in questions_to_analyze:
        # Find the question
        question_data = None
        for q in data['questions']:
            if int(q['question_number']) == question_num:
                question_data = q
                break
        
        if question_data:
            print(f"Analyzing Question {question_num}...")
            
            # Add analysis
            analysis_result = analyze_question_with_openai(question_data)
            
            result = {
                "question_number": question_num,
                "question_text": question_data['question_text'],
                "correct_answer": question_data['correct_answer'],
                "analysis_result": analysis_result
            }
            
            results.append(result)
            
            # Add delay to avoid rate limiting
            time.sleep(2)
        else:
            print(f"Question {question_num} not found!")
    
    # Save results
    output_file = 'openai_reanalysis_all_poor_quality_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis complete! Results saved to {output_file}")
    
    # Print summary
    successful = sum(1 for r in results if r['analysis_result']['success'])
    total = len(results)
    print(f"Successfully analyzed: {successful}/{total} questions")

if __name__ == "__main__":
    main() 