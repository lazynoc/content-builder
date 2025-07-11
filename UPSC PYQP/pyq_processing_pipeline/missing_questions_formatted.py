import json
import os

def format_missing_questions():
    """Format missing questions in an easy-to-fill format."""
    
    # Missing questions by year (from our analysis)
    missing_by_year = {
        2024: [],  # No file found
        2022: [14, 15, 16, 82, 83, 84, 85, 86, 87, 88],
        2021: [30, 31, 32, 33, 34, 38, 39, 40, 41, 42, 43, 44, 65, 100],
        2020: [17, 18, 19, 20, 21, 22, 23, 24, 27, 28, 29, 30, 31, 32, 33, 40, 41, 42, 43, 44],
        2019: [24, 54, 55, 56, 57],
        2018: [15, 23, 25, 39, 40, 41, 68, 70, 73, 77, 78, 79, 92, 93, 94],
        2017: [10, 15, 16, 17, 18],
        2016: [92, 93, 94, 95, 96],
        2014: [21, 22, 24, 26, 28, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52],
        2013: [],  # No file found
        2012: [],  # No file found
        2011: []   # No file found
    }
    
    def group_consecutive(numbers):
        """Group consecutive numbers together."""
        if not numbers:
            return []
        
        numbers.sort()
        groups = []
        start = numbers[0]
        prev = start
        
        for num in numbers[1:]:
            if num != prev + 1:
                groups.append((start, prev))
                start = num
            prev = num
        groups.append((start, prev))
        
        return groups
    
    print("MISSING QUESTIONS - PAGE NUMBERS NEEDED")
    print("=" * 60)
    print("Format: q [start]-[end] pn [page_number]")
    print("=" * 60)
    
    for year in sorted(missing_by_year.keys(), reverse=True):
        missing = missing_by_year[year]
        
        if not missing:
            if year in [2024, 2013, 2012, 2011]:
                print(f"\n{year}: NO FILE FOUND - NEED TO PROCESS FULL YEAR")
            else:
                print(f"\n{year}: ✅ COMPLETE")
            continue
        
        print(f"\n{year}: {len(missing)} missing questions")
        print("-" * 40)
        
        groups = group_consecutive(missing)
        
        for start, end in groups:
            if start == end:
                print(f"q {start} pn -")
            else:
                print(f"q {start}-{end} pn -")
    
    print("\n" + "=" * 60)
    print("INSTRUCTIONS:")
    print("1. Fill in the page numbers after 'pn -'")
    print("2. For single questions: q 24 pn 15")
    print("3. For ranges: q 14-16 pn 12-14")
    print("4. Send back the completed list")
    print("=" * 60)

if __name__ == "__main__":
    format_missing_questions() 