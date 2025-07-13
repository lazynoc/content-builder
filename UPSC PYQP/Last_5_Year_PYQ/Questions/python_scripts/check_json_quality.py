import json
from collections import Counter
import sys

def check_json_quality(file_path):
    """Check the quality and completeness of the UPSC questions JSON"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data['questions']
    metadata = data['metadata']
    
    print("=" * 60)
    print(f"UPSC PRELIMS {metadata.get('title', 'QUESTION BANK').split()[-2]} QUALITY CHECK")
    print("=" * 60)
    
    # Basic statistics
    print(f"\n📊 BASIC STATISTICS:")
    print(f"Total questions: {len(questions)}")
    print(f"Expected questions: {metadata.get('total_questions', 'N/A')}")
    print(f"JSON version: {metadata.get('version', 'N/A')}")
    
    # Check for missing fields
    print(f"\n🔍 FIELD COMPLETENESS CHECK:")
    missing_fields = {
        'question_text': 0,
        'subject': 0,
        'difficulty': 0,
        'exam_info': 0,
        'options': 0
    }
    
    questions_with_issues = []
    
    for i, q in enumerate(questions, 1):
        # Check for missing essential fields
        if not q.get('question_text', '').strip():
            missing_fields['question_text'] += 1
            questions_with_issues.append(f"Q{i}: Missing question text")
            
        if not q.get('subject', '').strip():
            missing_fields['subject'] += 1
            questions_with_issues.append(f"Q{i}: Missing subject")
            
        if not q.get('difficulty', '').strip():
            missing_fields['difficulty'] += 1
            questions_with_issues.append(f"Q{i}: Missing difficulty")
            
        if not q.get('exam_info', '').strip():
            missing_fields['exam_info'] += 1
            questions_with_issues.append(f"Q{i}: Missing exam info")
            
        # Check options
        options = q.get('options', [])
        if len(options) != 4:
            missing_fields['options'] += 1
            questions_with_issues.append(f"Q{i}: Expected 4 options, found {len(options)}")
        else:
            for j, opt in enumerate(options):
                if not opt.get('text', '').strip():
                    questions_with_issues.append(f"Q{i}: Option {chr(65+j)} is empty")
    
    # Print missing field counts
    for field, count in missing_fields.items():
        status = "✅" if count == 0 else f"❌ ({count})"
        print(f"  {field.replace('_', ' ').title()}: {status}")
    
    # Subject distribution
    print(f"\n📚 SUBJECT DISTRIBUTION:")
    subjects = Counter(q.get('subject', 'Unknown') for q in questions)
    for subject, count in subjects.most_common():
        print(f"  {subject}: {count} questions")
    
    # Difficulty distribution
    print(f"\n🎯 DIFFICULTY DISTRIBUTION:")
    difficulties = Counter(q.get('difficulty', 'Unknown') for q in questions)
    for difficulty, count in difficulties.most_common():
        print(f"  {difficulty}: {count} questions")
    
    # Question text length analysis
    print(f"\n📝 QUESTION TEXT ANALYSIS:")
    text_lengths = [len(q.get('question_text', '')) for q in questions]
    avg_length = sum(text_lengths) / len(text_lengths)
    min_length = min(text_lengths)
    max_length = max(text_lengths)
    
    print(f"  Average length: {avg_length:.1f} characters")
    print(f"  Shortest: {min_length} characters")
    print(f"  Longest: {max_length} characters")
    
    # Options analysis
    print(f"\n🔘 OPTIONS ANALYSIS:")
    option_lengths = []
    for q in questions:
        for opt in q.get('options', []):
            option_lengths.append(len(opt.get('text', '')))
    
    if option_lengths:
        avg_opt_length = sum(option_lengths) / len(option_lengths)
        print(f"  Average option length: {avg_opt_length:.1f} characters")
        print(f"  Total options: {len(option_lengths)}")
    
    # Table questions count
    table_questions = sum(1 for q in questions if 'table_data' in q)
    if table_questions > 0:
        print(f"\n📊 TABLE QUESTIONS: {table_questions}")
    
    # Issues summary
    if questions_with_issues:
        print(f"\n⚠️  ISSUES FOUND ({len(questions_with_issues)}):")
        for issue in questions_with_issues[:10]:  # Show first 10 issues
            print(f"  {issue}")
        if len(questions_with_issues) > 10:
            print(f"  ... and {len(questions_with_issues) - 10} more issues")
    else:
        print(f"\n✅ NO ISSUES FOUND!")
    
    # Overall quality score
    total_checks = len(questions) * 5  # 5 checks per question
    passed_checks = total_checks - sum(missing_fields.values())
    quality_score = (passed_checks / total_checks) * 100
    
    print(f"\n🏆 OVERALL QUALITY SCORE: {quality_score:.1f}%")
    
    if quality_score >= 95:
        print("🎉 EXCELLENT QUALITY!")
    elif quality_score >= 90:
        print("👍 GOOD QUALITY!")
    elif quality_score >= 80:
        print("⚠️  ACCEPTABLE QUALITY")
    else:
        print("❌ NEEDS IMPROVEMENT")
    
    print("=" * 60)
    
    return questions_with_issues

if __name__ == "__main__":
    # Use command line argument if provided, otherwise default to 2025 file
    file_path = sys.argv[1] if len(sys.argv) > 1 else "upsc_prelims_2025_question_bank.json"
    check_json_quality(file_path) 