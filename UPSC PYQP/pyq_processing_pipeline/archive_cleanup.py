#!/usr/bin/env python3
"""
Archive cleanup script: Move all files that would be deleted by deep_cleanup.py into 'archive_cleanup/'
"""

import os
import glob
import shutil

def archive_cleanup():
    archive_dir = "archive_cleanup"
    os.makedirs(archive_dir, exist_ok=True)
    
    files_to_archive = [
        # Test and analysis files
        "test_*.json",
        "test_*.py",
        "sample_*.json",
        "debug_*.py",
        "investigate_*.py",
        # Old extraction scripts
        "extract_2014_*.py",
        "extract_2017_*.py",
        "extract_2018_*.py",
        "extract_2019_*.py",
        "extract_2020_*.py",
        "extract_missing_*.py",
        "extract_pyq_questions_*.py",
        "extract_2024_pyq_only*.py",
        # Old merge scripts
        "merge_*.py",
        # Analysis and processing scripts
        "analyze_*.py",
        "process_*.py",
        "complete_*.py",
        "batch_*.py",
        "robust_*.py",
        # Database and import scripts
        "import_*.py",
        "setup_*.py",
        "clear_*.py",
        # Documentation files
        "*.md",
        "*.txt",
        # Old question files
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
        "GS Prelims 2024_FINAL_COMPLETE_ALL_SOURCES.json",
        "GS Prelims 2024_FINAL_COMPLETE_questions.json",
        "GS Prelims 2024_PYQ_ONLY_filtered.json",
        "GS Prelims 2024_enhanced_analysis.json",
        "GS Prelims 2024_enhanced_chunk_*.json",
        "GS Prelims 2024_restructured.json",
        "Question_48_complete.json",
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
        "missing_questions_formatted.py",
        "check_positions.py",
        "cost_summary.md",
        "final_extraction_summary.md",
        "missing_data_summary.md",
        "comprehensive_analysis_framework.md",
        "student_mentorship_framework.md"
    ]
    
    # Essential files to keep in place
    essential_files = [
        "GS Prelims 2024_COMPLETE_100_QUESTIONS.json",
        "final_complete_merge.py",
        "identify_missing_questions.py",
        "cleanup_files.py",
        "archive_cleanup.py"
    ]
    
    moved_count = 0
    already_archived = 0
    not_found = 0
    
    print(f"Moving files to '{archive_dir}/'...")
    for pattern in files_to_archive:
        for file_path in glob.glob(pattern):
            if file_path in essential_files:
                continue
            dest_path = os.path.join(archive_dir, file_path)
            # Avoid overwriting if already archived
            if os.path.exists(dest_path):
                already_archived += 1
                continue
            try:
                shutil.move(file_path, dest_path)
                print(f"📦 Moved: {file_path} -> {dest_path}")
                moved_count += 1
            except FileNotFoundError:
                not_found += 1
            except Exception as e:
                print(f"⚠️  Could not move {file_path}: {e}")
    print(f"\nSummary: {moved_count} files moved, {already_archived} already archived, {not_found} not found.")
    print(f"\nAll files are now in '{archive_dir}/'. You can delete this folder manually when ready.")

if __name__ == "__main__":
    archive_cleanup() 