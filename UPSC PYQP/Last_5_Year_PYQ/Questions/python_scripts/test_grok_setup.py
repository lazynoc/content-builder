#!/usr/bin/env python3
"""
Test script for UPSC Grok Analysis Setup
"""

import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../../../.env')

def test_grok_api_key():
    """Test if GROK_API_KEY is available"""
    api_key = os.getenv('GROK_API_KEY')
    if api_key:
        print("✅ GROK_API_KEY found")
        print(f"   Key starts with: {api_key[:10]}...")
        return True
    else:
        print("❌ GROK_API_KEY not found in environment variables")
        print("   Please add GROK_API_KEY to your .env file")
        return False

def test_input_file():
    """Test if input file exists and is readable"""
    input_file = '../json_files/upsc_prelims_2025_structured_for_frontend.json'
    
    if os.path.exists(input_file):
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            questions = data['questions']
            print(f"✅ Input file found: {input_file}")
            print(f"   Total questions: {len(questions)}")
            print(f"   First question: {questions[0]['question_number']}")
            return True, questions
        except Exception as e:
            print(f"❌ Error reading input file: {e}")
            return False, None
    else:
        print(f"❌ Input file not found: {input_file}")
        return False, None

def test_single_question_analysis():
    """Test analysis of a single question"""
    from grok_analysis_upsc_2025 import UPSCGrokAnalyzer
    
    # Test with first question
    success, questions = test_input_file()
    if not success or questions is None:
        return False
    
    analyzer = UPSCGrokAnalyzer()
    test_question = questions[0]
    
    print(f"\n🧪 Testing analysis of question {test_question['question_number']}...")
    
    try:
        analysis = analyzer.analyze_question_with_grok(test_question)
        if analysis:
            print("✅ Single question analysis successful!")
            print(f"   Explanation: {analysis.get('explanation', 'N/A')[:100]}...")
            print(f"   Primary type: {analysis.get('primary_type', 'N/A')}")
            print(f"   Difficulty: {analysis.get('difficulty_level', 'N/A')}")
            return True
        else:
            print("❌ Single question analysis failed")
            return False
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Testing UPSC Grok Analysis Setup...\n")
    
    # Test 1: API Key
    api_key_ok = test_grok_api_key()
    
    # Test 2: Input file
    file_ok, questions = test_input_file()
    
    # Test 3: Single question analysis (only if first two tests pass)
    if api_key_ok and file_ok:
        analysis_ok = test_single_question_analysis()
    else:
        analysis_ok = False
        print("\n⏭️  Skipping analysis test due to setup issues")
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"   API Key: {'✅' if api_key_ok else '❌'}")
    print(f"   Input File: {'✅' if file_ok else '❌'}")
    print(f"   Analysis: {'✅' if analysis_ok else '❌'}")
    
    if api_key_ok and file_ok and analysis_ok:
        print(f"\n🎉 All tests passed! Ready to run full analysis.")
        print(f"   Run: python grok_analysis_upsc_2025.py")
    else:
        print(f"\n⚠️  Some tests failed. Please fix issues before running full analysis.")

if __name__ == "__main__":
    main() 