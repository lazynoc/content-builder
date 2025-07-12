#!/usr/bin/env python3
"""
Analyze Grok Analysis Status - Check what questions are analyzed and what's missing
"""

import json
from typing import Dict, List, Set

def analyze_grok_status():
    """Analyze the current status of Grok analysis"""
    
    # Load the optimized Grok analysis
    with open('uppsc_questions_grok_optimized.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get metadata
    metadata = data['metadata']
    questions = data['questions']
    
    print("=== GROK ANALYSIS STATUS REPORT ===")
    print(f"Source: {metadata['source']}")
    print(f"Analysis Date: {metadata['analysis_date']}")
    print(f"Total Questions in File: {metadata['total_questions']}")
    print(f"Actual Questions Analyzed: {len(questions)}")
    print(f"Analysis Method: {metadata['analysis_method']}")
    print(f"Exam Type: {metadata['exam_type']}")
    print(f"Year: {metadata['year']}")
    print()
    
    # Get question numbers that are analyzed
    analyzed_numbers = set()
    for q in questions:
        analyzed_numbers.add(int(q['question_number']))
    
    # Expected question numbers (1-150)
    expected_numbers = set(range(1, 151))
    
    # Find missing questions
    missing_numbers = expected_numbers - analyzed_numbers
    
    print("=== ANALYSIS RESULTS ===")
    print(f"✅ Successfully Analyzed: {len(analyzed_numbers)} questions")
    print(f"❌ Missing Analysis: {len(missing_numbers)} questions")
    print(f"📊 Completion Rate: {(len(analyzed_numbers)/150)*100:.1f}%")
    print()
    
    if missing_numbers:
        print("=== MISSING QUESTIONS ===")
        missing_list = sorted(list(missing_numbers))
        print(f"Missing question numbers: {missing_list}")
        print()
        
        # Group missing questions for easier processing
        print("=== MISSING QUESTIONS GROUPED ===")
        if len(missing_list) <= 20:
            print(f"All missing: {missing_list}")
        else:
            print(f"First 10 missing: {missing_list[:10]}")
            print(f"Last 10 missing: {missing_list[-10:]}")
            print(f"Total missing: {len(missing_list)} questions")
        print()
        
        # Check for patterns in missing questions
        print("=== PATTERN ANALYSIS ===")
        consecutive_missing = []
        current_group = []
        
        for i, num in enumerate(missing_list):
            if not current_group:
                current_group = [num]
            elif num == current_group[-1] + 1:
                current_group.append(num)
            else:
                if len(current_group) > 1:
                    consecutive_missing.append(current_group)
                current_group = [num]
        
        if current_group and len(current_group) > 1:
            consecutive_missing.append(current_group)
        
        if consecutive_missing:
            print("Consecutive missing ranges:")
            for group in consecutive_missing:
                print(f"  {group[0]}-{group[-1]} ({len(group)} questions)")
        else:
            print("No consecutive missing ranges found")
        print()
        
        return missing_list
    else:
        print("🎉 ALL 150 QUESTIONS HAVE BEEN ANALYZED!")
        return []

def check_analysis_quality():
    """Check the quality of analyzed questions"""
    
    with open('uppsc_questions_grok_optimized.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data['questions']
    
    print("=== ANALYSIS QUALITY CHECK ===")
    
    # Check for questions with minimal analysis (fallback responses)
    minimal_analysis = []
    good_analysis = []
    
    for q in questions:
        # Check if key fields have substantial content
        key_fields = ['difficulty_reason', 'options_analysis', 'key_concepts', 'common_mistakes']
        has_substantial_content = True
        
        for field in key_fields:
            value = q.get(field)
            if not value or (isinstance(value, str) and len(value) < 50):
                has_substantial_content = False
                break
        
        if has_substantial_content:
            good_analysis.append(q['question_number'])
        else:
            minimal_analysis.append(q['question_number'])
    
    print(f"✅ Good Analysis: {len(good_analysis)} questions")
    print(f"⚠️  Minimal Analysis: {len(minimal_analysis)} questions")
    
    if minimal_analysis:
        print(f"Questions with minimal analysis: {minimal_analysis[:10]}{'...' if len(minimal_analysis) > 10 else ''}")
    
    print()

def main():
    """Main function"""
    
    print("Analyzing Grok analysis status...\n")
    
    # Analyze status
    missing_questions = analyze_grok_status()
    
    # Check quality
    check_analysis_quality()
    
    # Summary
    print("=== SUMMARY ===")
    if missing_questions:
        print(f"❌ Need to re-run Grok analysis for {len(missing_questions)} questions")
        print(f"📝 Missing questions: {sorted(missing_questions)}")
        print("\nNext steps:")
        print("1. Create a script to process only missing questions")
        print("2. Re-run Grok analysis with retry logic")
        print("3. Merge results with existing analysis")
    else:
        print("🎉 All questions analyzed! Ready for Supabase upload.")
        print("\nNext steps:")
        print("1. Upload all 150 questions to Supabase")
        print("2. Build frontend features")
        print("3. Test the complete system")

if __name__ == "__main__":
    main() 