#!/usr/bin/env python3
"""
Analyze the correct page ranges for missing questions in GS Prelims 2023
"""

import json

def analyze_missing_pages():
    # Load the first extraction results
    with open('GS Prelims 2023_PYQ_ONLY_chunked.json', 'r') as f:
        data = json.load(f)
    
    questions = data['questions']
    missing = [5, 27, 32, 33, 34, 35, 36, 66, 89]
    
    print("🔍 MISSING QUESTIONS PAGE ANALYSIS")
    print("=" * 50)
    print(f"Missing questions: {missing}")
    print()
    
    # Create a mapping of question numbers to page ranges
    q_to_pages = {}
    for q in questions:
        q_num = int(q['question_number'])
        q_to_pages[q_num] = q.get('page_range', 'N/A')
    
    print("📋 SURROUNDING QUESTIONS AND THEIR PAGES:")
    print("-" * 40)
    
    # Analyze each missing question
    for missing_q in missing:
        print(f"\n🔍 MISSING Q{missing_q}:")
        
        # Find questions before and after
        before_q = None
        after_q = None
        
        for q_num in sorted(q_to_pages.keys()):
            if q_num < missing_q:
                before_q = q_num
            elif q_num > missing_q:
                after_q = q_num
                break
        
        if before_q:
            print(f"   Before: Q{before_q} on pages {q_to_pages[before_q]}")
        if after_q:
            print(f"   After: Q{after_q} on pages {q_to_pages[after_q]}")
        
        # Estimate the page range for missing question
        if before_q and after_q:
            before_pages = q_to_pages[before_q]
            after_pages = q_to_pages[after_q]
            
            if before_pages != 'N/A' and after_pages != 'N/A':
                # Extract page numbers
                before_end = int(before_pages.split('-')[1])
                after_start = int(after_pages.split('-')[0])
                
                # Estimate: missing question should be between these pages
                estimated_start = before_end
                estimated_end = after_start
                
                print(f"   📍 ESTIMATED for Q{missing_q}: pages {estimated_start}-{estimated_end}")
            else:
                print(f"   ❓ Cannot estimate - missing page data")
        else:
            print(f"   ❓ Cannot estimate - no surrounding questions")
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY OF ESTIMATED PAGE RANGES:")
    print("-" * 40)
    
    # Group consecutive missing questions
    missing_groups = []
    current_group = [missing[0]]
    
    for i in range(1, len(missing)):
        if missing[i] == missing[i-1] + 1:
            current_group.append(missing[i])
        else:
            missing_groups.append(current_group)
            current_group = [missing[i]]
    
    missing_groups.append(current_group)
    
    for group in missing_groups:
        if len(group) == 1:
            q_num = group[0]
            before_q = max([q for q in q_to_pages.keys() if q < q_num], default=None)
            after_q = min([q for q in q_to_pages.keys() if q > q_num], default=None)
            
            if before_q and after_q:
                before_end = int(q_to_pages[before_q].split('-')[1])
                after_start = int(q_to_pages[after_q].split('-')[0])
                print(f"Q{q_num}: pages {before_end}-{after_start}")
            else:
                print(f"Q{q_num}: needs manual page determination")
        else:
            start_q = group[0]
            end_q = group[-1]
            before_q = max([q for q in q_to_pages.keys() if q < start_q], default=None)
            after_q = min([q for q in q_to_pages.keys() if q > end_q], default=None)
            
            if before_q and after_q:
                before_end = int(q_to_pages[before_q].split('-')[1])
                after_start = int(q_to_pages[after_q].split('-')[0])
                print(f"Q{start_q}-Q{end_q}: pages {before_end}-{after_start}")
            else:
                print(f"Q{start_q}-Q{end_q}: needs manual page determination")

if __name__ == "__main__":
    analyze_missing_pages() 