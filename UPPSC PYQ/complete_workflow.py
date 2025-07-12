#!/usr/bin/env python3
"""
Complete Workflow for UPPSC Questions Processing and Database Upload

This script performs the following steps:
1. Transform UPPSC questions to Supabase format
2. Run Grok analysis for performance assessment
3. Upload to Supabase database

Requirements:
- GROK_API_KEY in .env file
- SUPABASE_URL and SUPABASE_ANON_KEY in .env file
- uppsc_questions_complete_final.json file
"""

import json
import os
import sys
from datetime import datetime

# Import our modules
from transform_for_supabase import transform_uppsc_to_supabase_format
from grok_analysis_script import GrokAnalyzer
from supabase_upload_script import SupabaseUploader, prepare_questions_for_upload

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check environment variables
    required_env_vars = ['GROK_API_KEY', 'SUPABASE_URL', 'SUPABASE_ANON_KEY']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please add them to your .env file")
        return False
    
    # Check input file
    if not os.path.exists('uppsc_questions_complete_final.json'):
        print("❌ Missing input file: uppsc_questions_complete_final.json")
        return False
    
    print("✅ All requirements met!")
    return True

def step1_transform():
    """Step 1: Transform questions to Supabase format"""
    print("\n" + "="*50)
    print("STEP 1: TRANSFORMING QUESTIONS FOR SUPABASE")
    print("="*50)
    
    try:
        data = transform_uppsc_to_supabase_format()
        print(f"✅ Step 1 completed: {len(data['questions'])} questions transformed")
        return True
    except Exception as e:
        print(f"❌ Step 1 failed: {e}")
        return False

def step2_grok_analysis():
    """Step 2: Run Grok analysis"""
    print("\n" + "="*50)
    print("STEP 2: GROK ANALYSIS FOR PERFORMANCE ASSESSMENT")
    print("="*50)
    
    try:
        # Load the Supabase-ready questions
        with open('uppsc_questions_supabase_ready.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        questions = data['questions']
        
        # Initialize Grok analyzer
        analyzer = GrokAnalyzer()
        
        print(f"Starting Grok analysis for {len(questions)} questions...")
        
        # Ask user for confirmation
        confirm = input("This will take time and use API credits. Continue? (y/n): ").lower().strip()
        if confirm != 'y':
            print("Grok analysis skipped.")
            return True
        
        # Analyze questions
        analyzed_questions = analyzer.analyze_batch_questions(questions, batch_size=5)
        
        # Create final output
        final_data = {
            "metadata": {
                "source": "UPPSC_2024_Prelims_GS1",
                "analysis_date": datetime.now().isoformat(),
                "total_questions": len(analyzed_questions),
                "exam_type": "UPPSC",
                "year": 2024,
                "section": "UPPSC_Prelims_GS1",
                "analysis_method": "Grok_AI",
                "note": "Complete analysis for student performance assessment and personalized guidance"
            },
            "questions": analyzed_questions
        }
        
        # Save the analyzed data
        with open('uppsc_questions_with_grok_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Step 2 completed: {len(analyzed_questions)} questions analyzed")
        return True
        
    except Exception as e:
        print(f"❌ Step 2 failed: {e}")
        return False

def step3_upload_to_supabase():
    """Step 3: Upload to Supabase"""
    print("\n" + "="*50)
    print("STEP 3: UPLOAD TO SUPABASE DATABASE")
    print("="*50)
    
    try:
        # Check if analyzed file exists
        if not os.path.exists('uppsc_questions_with_grok_analysis.json'):
            print("❌ Missing analyzed questions file. Please run Step 2 first.")
            return False
        
        # Load the analyzed questions
        with open('uppsc_questions_with_grok_analysis.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        questions = data['questions']
        
        # Initialize uploader
        uploader = SupabaseUploader()
        
        # Check if we want to replace existing questions
        year = 2024
        exam_type = "UPPSC"
        
        existing_questions = uploader.check_existing_questions(year, exam_type)
        
        if existing_questions:
            print(f"Found {len(existing_questions)} existing questions for {exam_type} {year}")
            replace = input("Do you want to replace existing questions? (y/n): ").lower().strip()
            
            if replace == 'y':
                if uploader.delete_existing_questions(year, exam_type):
                    print("Proceeding with upload...")
                else:
                    print("Failed to delete existing questions. Aborting.")
                    return False
            else:
                print("Upload cancelled.")
                return False
        
        # Prepare questions for upload
        prepared_questions = prepare_questions_for_upload(questions)
        
        # Upload to Supabase
        result = uploader.upload_questions(prepared_questions, batch_size=10)
        
        # Save upload report
        report = {
            "metadata": {
                "upload_date": datetime.now().isoformat(),
                "source_file": "uppsc_questions_with_grok_analysis.json",
                "exam_type": exam_type,
                "year": year
            },
            "upload_result": result
        }
        
        with open('supabase_upload_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "="*50)
        print("UPLOAD SUMMARY")
        print("="*50)
        print(f"Total Questions: {result['total_questions']}")
        print(f"Successful Uploads: {result['successful_uploads']}")
        print(f"Failed Uploads: {result['failed_uploads']}")
        print(f"Success Rate: {(result['successful_uploads']/result['total_questions']*100):.1f}%")
        
        if result['errors']:
            print(f"\nErrors ({len(result['errors'])}):")
            for error in result['errors'][:3]:  # Show first 3 errors
                print(f"  - {error}")
            if len(result['errors']) > 3:
                print(f"  ... and {len(result['errors']) - 3} more errors")
        
        print(f"\n📁 Upload report saved as: supabase_upload_report.json")
        
        return result['successful_uploads'] > 0
        
    except Exception as e:
        print(f"❌ Step 3 failed: {e}")
        return False

def main():
    """Main workflow function"""
    print("🚀 UPPSC QUESTIONS COMPLETE WORKFLOW")
    print("="*50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Run all steps
    steps = [
        ("Transform Questions", step1_transform),
        ("Grok Analysis", step2_grok_analysis),
        ("Upload to Supabase", step3_upload_to_supabase)
    ]
    
    results = []
    
    for step_name, step_func in steps:
        print(f"\n🔄 Running: {step_name}")
        success = step_func()
        results.append((step_name, success))
        
        if not success:
            print(f"❌ Workflow stopped at: {step_name}")
            break
    
    # Final summary
    print("\n" + "="*50)
    print("WORKFLOW SUMMARY")
    print("="*50)
    
    for step_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{step_name}: {status}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n🎉 All steps completed successfully!")
        print("Your UPPSC questions are now in the database with Grok analysis.")
    else:
        print("\n⚠️  Some steps failed. Check the output above for details.")
    
    print(f"\n📁 Generated files:")
    files = [
        "uppsc_questions_supabase_ready.json",
        "uppsc_questions_with_grok_analysis.json", 
        "supabase_upload_report.json"
    ]
    
    for file in files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (not created)")

if __name__ == "__main__":
    main() 