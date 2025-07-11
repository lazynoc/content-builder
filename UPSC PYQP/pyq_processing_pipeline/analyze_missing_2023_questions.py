#!/usr/bin/env python3
"""
Script to run OpenAI analysis for the 4 missing 2023 questions (13, 20, 62, 94)
These questions likely didn't get proper analysis due to missing options
"""

import json
import os
import openai
from typing import Dict, Any, List
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('/Users/shahrukhmalik/Documents/GitHub/UPSC BOOKS/.env')

# Set up OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    print("❌ Error: OPENAI_API_KEY environment variable must be set")
    sys.exit(1)

def get_openai_analysis(question_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get OpenAI analysis for a single question"""
    
    question_text = question_data.get('question_text', '')
    options = question_data.get('options', {})
    correct_answer = question_data.get('correct_answer', '')
    explanation = question_data.get('explanation', '')
    
    # Format options for the prompt
    options_text = ""
    for key, value in options.items():
        options_text += f"{key}. {value}\n"
    
    prompt = f"""
You are an expert UPSC (Union Public Service Commission) mentor and educator. Analyze this UPSC GS Prelims question and provide comprehensive insights.

Question: {question_text}

Options:
{options_text}

Correct Answer: {correct_answer}

Explanation: {explanation}

Please provide a detailed analysis in the following JSON format:

{{
    "key_concepts": ["concept1", "concept2", "concept3"],
    "difficulty_level": "Easy/Medium/Hard",
    "topic_category": "Polity/Economy/Geography/History/Environment/Science/Current Affairs",
    "sub_topic": "specific subtopic",
    "common_mistakes": ["mistake1", "mistake2", "mistake3"],
    "memory_hooks": ["hook1", "hook2", "hook3"],
    "related_topics": ["topic1", "topic2", "topic3"],
    "tags": ["tag1", "tag2", "tag3"],
    "strategic_importance": "Why this topic is important for UPSC",
    "learning_objectives": ["objective1", "objective2", "objective3"],
    "micro_analysis": {{
        "concept_clarity": "How well does this test understanding of the concept",
        "application_ability": "How well does this test application of knowledge",
        "analytical_skills": "How well does this test analytical thinking",
        "current_affairs_linkage": "Link to current affairs if any"
    }},
    "mentoring_insights": {{
        "strength_areas": ["area1", "area2"],
        "weakness_areas": ["area1", "area2"],
        "improvement_suggestions": ["suggestion1", "suggestion2"],
        "study_recommendations": ["recommendation1", "recommendation2"]
    }}
}}

Provide only the JSON response, no additional text.
"""

    try:
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert UPSC mentor and educator. Provide detailed analysis in JSON format only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        # Extract the JSON response
        analysis_text = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
        
        # Try to parse the JSON response
        try:
            analysis = json.loads(analysis_text)
            return analysis
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error for question {question_data.get('question_number', 'unknown')}: {e}")
            print(f"Raw response: {analysis_text}")
            return {}
            
    except Exception as e:
        print(f"❌ OpenAI API error for question {question_data.get('question_number', 'unknown')}: {e}")
        return {}

def analyze_missing_questions():
    """Analyze the 4 missing questions with OpenAI"""
    
    # Load the original 2023 file
    input_file = "GS Prelims 2023_WITH_OPENAI_ANALYSIS.json"
    
    print(f"📖 Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get the questions array from the data
    questions = data.get('questions', [])
    
    # Questions to analyze (13, 20, 62, 94)
    target_questions = ["13", "20", "62", "94"]
    
    print(f"🔍 Analyzing {len(target_questions)} questions with OpenAI...")
    
    updated_count = 0
    
    for question in questions:
        question_num = question.get('question_number', '')
        
        if question_num in target_questions:
            print(f"\n📝 Analyzing Question {question_num}...")
            
            # Get OpenAI analysis
            analysis = get_openai_analysis(question)
            
            if analysis:
                # Update the question with new analysis
                question.update(analysis)
                updated_count += 1
                print(f"✅ Question {question_num} analyzed and updated")
            else:
                print(f"❌ Failed to analyze Question {question_num}")
    
    # Save the updated file
    print(f"\n💾 Saving updated file...")
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Successfully updated {updated_count} questions with OpenAI analysis")
    print(f"📁 Updated file: {input_file}")

if __name__ == "__main__":
    analyze_missing_questions() 