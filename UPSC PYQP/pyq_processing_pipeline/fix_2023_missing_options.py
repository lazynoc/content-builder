#!/usr/bin/env python3
"""
Script to fix missing options for 2023 UPSC questions
Fixes questions 13, 20, 62, 94 which have empty options
"""

import json
import os

def fix_2023_missing_options():
    """Fix missing options for 2023 questions in the original file"""
    
    # Load the original 2023 file with OpenAI analysis
    input_file = "GS Prelims 2023_WITH_OPENAI_ANALYSIS.json"
    
    print(f"📖 Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Define the missing options for each question with correct options
    missing_options = {
        "13": {
            "A": "It determines the objective for the making of necessary laws.",
            "B": "It enables the creation of political offices and a government.",
            "C": "It defines and limits the powers of government.",
            "D": "It secures social justice, social equality and social security."
        },
        "20": {
            "A": "Both Statements-I and Statement-II are correct and Statement-II is the correct explanation for Statement-I",
            "B": "Both Statement-I and Statement-II are correct and Statement-II is not the correct explanation for Statement-I", 
            "C": "Statement-I is correct but Statement-II is incorrect",
            "D": "Statement-I is incorrect but Statement-II is correct"
        },
        "62": {
            "A": "Only one",
            "B": "Only two", 
            "C": "All three",
            "D": "None"
        },
        "94": {
            "A": "Only one",
            "B": "Only two",
            "C": "All three", 
            "D": "None"
        }
    }
    
    # Fix each question
    fixed_count = 0
    for question in data["questions"]:
        q_num = question["question_number"]
        
        if q_num in missing_options:
            print(f"🔧 Fixing Q{q_num}...")
            
            # Add the missing options
            question["options"] = missing_options[q_num]
            question["options_extracted"] = True
            
            fixed_count += 1
    
    # Save back to the original file
    print(f"💾 Saving fixes to original file {input_file}...")
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Fixed {fixed_count} questions with missing options in original file!")
    print(f"📁 Original file updated: {input_file}")
    
    return input_file

def verify_fixes():
    """Verify that the fixes were applied correctly"""
    
    input_file = "GS Prelims 2023_WITH_OPENAI_ANALYSIS.json"
    
    print(f"\n🔍 Verifying fixes in {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check the fixed questions
    for question in data["questions"]:
        q_num = question["question_number"]
        
        if q_num in ["13", "20", "62", "94"]:
            options = question.get("options", {})
            options_extracted = question.get("options_extracted", False)
            
            print(f"Q{q_num}:")
            print(f"  - Options present: {len(options) > 0}")
            print(f"  - Options extracted: {options_extracted}")
            print(f"  - Number of options: {len(options)}")
            
            if len(options) > 0:
                for key, value in options.items():
                    print(f"    {key}: {value}")
            print()

if __name__ == "__main__":
    print("🚀 Starting 2023 UPSC questions options fix (ORIGINAL FILE)...")
    
    # Fix the missing options in original file
    output_file = fix_2023_missing_options()
    
    # Verify the fixes
    verify_fixes()
    
    print("\n🎉 2023 UPSC questions options fix completed!")
    print("📝 Next steps:")
    print("   1. Original file has been updated")
    print("   2. Run the import script with the original file")
    print("   3. Verify all 100 questions are imported successfully") 