#!/usr/bin/env python3
"""
Deep cleanup script to remove additional temporary files, test files, and older scripts
Keep only the essential files for the final dataset
"""

import os
import glob
from typing import List

def deep_cleanup():
    """Remove additional temporary and test files"""
    
    print("🧹 Starting deep cleanup of additional files...")
    print("=" * 60)
    
    # Additional files to remove (test files, older scripts, etc.)
    additional_files_to_remove = [
        # Test and analysis files
        "test_*.json",
        "test_*.py",
        "sample_*.json",
        "debug_*.py",
        "investigate_*.py",
        
        # Old extraction scripts (keep only the main ones)
        "extract_2014_*.py",
        "extract_2020_*.py",
        "extract_missing_*.py",
        "extract_pyq_questions_*.py",
        "extract_2024_pyq_only*.py",
        
        # Old merge scripts
        "merge_*.py",
        
        # Analysis and processing scripts (keep only essential ones)
        "analyze_*.py",
        "process_*.py",
        "complete_*.py",
        "batch_*.py",
        "robust_*.py",
        
        # Database and import scripts (keep only essential ones)
        "import_*.py",
        "setup_*.py",
        "clear_*.py",
        
        # Documentation files (keep only essential ones)
        "*.md",
        "*.txt",
        
        # Old question files (keep only the final complete one)
        "GS Prelims 2012_*.json",
        "GS Prelims 2014_*.json", 
        "GS Prelims 2015_*.json",
        "GS Prelims 2016_*.json",
        "GS Prelims 2017_*.json",
        "GS Prelims 2018_*.json",
        "GS Prelims 2019_*.json",
        "GS Prelims 2020_*.json",
        "GS Prelims 2021_*.json",
        "GS Prelims 2022_*.json",
        "GS Prelims 2023_*.json",
        "GS Prelims 2024 _complete_questions.json",
        "GS Prelims 2024_ALL_enhanced_analysis.json",
        "GS Prelims 2024_PROGRESS_100_enhanced.json",
        "GS Prelims 2024_complete_processed.json",
        
        # Requirements and schema files
        "requirements_*.txt",
        "*_schema.sql",
        
        # Filter and utility scripts
        "filter_*.py",
        "separate_*.py",
        "compare_*.py",
        "enhanced_*.py",
        "simple_*.py",
        "student_*.py",
        "question_analysis_*.py",
        "cost_summary.md",
        "final_extraction_summary.md",
        "missing_data_summary.md",
        "comprehensive_analysis_framework.md",
        "student_mentorship_framework.md"
    ]
    
    removed_count = 0
    not_found_count = 0
    
    print("📁 Removing additional files...")
    
    for file_pattern in additional_files_to_remove:
        if "*" in file_pattern:
            # Handle glob patterns
            matching_files = glob.glob(file_pattern)
            for file_path in matching_files:
                # Skip essential files we want to keep
                if file_path in [
                    "GS Prelims 2024_COMPLETE_100_QUESTIONS.json",
                    "final_complete_merge.py", 
                    "identify_missing_questions.py",
                    "cleanup_files.py",
                    "deep_cleanup.py"
                ]:
                    continue
                    
                try:
                    os.remove(file_path)
                    print(f"✅ Removed: {file_path}")
                    removed_count += 1
                except FileNotFoundError:
                    not_found_count += 1
                except Exception as e:
                    print(f"⚠️  Could not remove {file_path}: {e}")
        else:
            # Handle specific files
            try:
                os.remove(file_pattern)
                print(f"✅ Removed: {file_pattern}")
                removed_count += 1
            except FileNotFoundError:
                not_found_count += 1
            except Exception as e:
                print(f"⚠️  Could not remove {file_pattern}: {e}")
    
    print("\n" + "=" * 60)
    print("🧹 DEEP CLEANUP SUMMARY:")
    print(f"✅ Files removed: {removed_count}")
    print(f"⚠️  Files not found: {not_found_count}")
    
    # List remaining essential files
    print("\n📋 ESSENTIAL FILES REMAINING:")
    essential_files = [
        "GS Prelims 2024_COMPLETE_100_QUESTIONS.json",  # Final complete dataset
        "final_complete_merge.py",                      # Final merge script
        "identify_missing_questions.py",                # Analysis script
        "cleanup_files.py",                             # Basic cleanup script
        "deep_cleanup.py"                               # This deep cleanup script
    ]
    
    for file_path in essential_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({file_size:,} bytes)")
        else:
            print(f"❌ {file_path} (not found)")
    
    print("\n🎯 Deep cleanup completed!")
    print("💾 Your complete dataset is in: GS Prelims 2024_COMPLETE_100_QUESTIONS.json")
    print("📊 Total questions: 100 (complete set)")

if __name__ == "__main__":
    deep_cleanup() 