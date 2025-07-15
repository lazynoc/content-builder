#!/usr/bin/env python3
"""
Monitor Optimized Grok Analysis Progress
Shows current status for single-file approach
"""

import os
import json
import glob
from datetime import datetime

def get_latest_log_file():
    """Get the most recent log file"""
    log_files = glob.glob("logs/grok_analysis_*.log")
    if not log_files:
        return None
    return max(log_files, key=os.path.getctime)

def check_output_files():
    """Check the status of output files"""
    output_files = {
        2025: '../json_files/upsc_prelims_2025_grok_analyzed.json',
        2024: '../json_files/upsc_prelims_2024_grok_analyzed.json'
    }
    
    status = {}
    for year, file_path in output_files.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                questions_count = len(data['questions'])
                last_updated = data['metadata'].get('last_updated', 'Unknown')
                
                status[year] = {
                    'exists': True,
                    'questions': questions_count,
                    'last_updated': last_updated,
                    'complete': questions_count >= 100  # Assuming 100 questions per year
                }
            except Exception as e:
                status[year] = {
                    'exists': True,
                    'error': str(e),
                    'complete': False
                }
        else:
            status[year] = {
                'exists': False,
                'questions': 0,
                'complete': False
            }
    
    return status

def analyze_progress():
    """Analyze current progress"""
    
    print("📊 Optimized UPSC Grok Analysis Progress Monitor")
    print("=" * 60)
    
    # Check log file
    log_file = get_latest_log_file()
    if log_file:
        print(f"📁 Latest log: {log_file}")
        
        # Get last few lines of log
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    print(f"🕒 Last activity: {lines[-1].strip()}")
        except:
            pass
    else:
        print("❌ No log files found")
    
    print()
    
    # Check output files
    status = check_output_files()
    
    for year in [2025, 2024]:
        print(f"📚 UPSC {year} Status:")
        print("-" * 30)
        
        if status[year]['exists']:
            if 'error' in status[year]:
                print(f"  ❌ Error: {status[year]['error']}")
            else:
                questions = status[year]['questions']
                last_updated = status[year]['last_updated']
                complete = status[year]['complete']
                
                print(f"  ✅ Questions analyzed: {questions}/100")
                print(f"  📊 Completion: {questions/100*100:.1f}%")
                print(f"  🕒 Last updated: {last_updated}")
                
                if complete:
                    print(f"  🎉 COMPLETE!")
                else:
                    print(f"  🔄 In progress...")
        else:
            print(f"  ⏳ File not created yet - not started")
        
        print()
    
    # Summary
    total_questions = sum(status[year]['questions'] for year in [2025, 2024] if status[year]['exists'] and 'error' not in status[year])
    total_complete = sum(1 for year in [2025, 2024] if status[year]['exists'] and status[year].get('complete', False))
    
    print("📈 Overall Progress:")
    print("-" * 30)
    print(f"  📊 Total questions: {total_questions}/200")
    print(f"  🎯 Years complete: {total_complete}/2")
    print(f"  📊 Overall completion: {total_questions/200*100:.1f}%")
    
    print()
    print("💡 Commands:")
    print("  tail -f logs/grok_analysis_*.log  # Monitor live progress")
    print("  python3 monitor_optimized_analysis.py  # Check this status again")

def main():
    """Main function"""
    analyze_progress()

if __name__ == "__main__":
    main() 