import json
from datetime import datetime

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    merged_path = 'GS Prelims 2022_COMPLETE_ALL_QUESTIONS.json'
    final4_path = 'GS Prelims 2022_FINAL_4_MISSING_MISTRAL.json'
    output_path = 'GS Prelims 2022_COMPLETE_100_QUESTIONS.json'

    merged = load_json(merged_path)
    final4 = load_json(final4_path)

    all_questions = merged['questions'] + final4['questions']
    # Deduplicate by question_number, keep the latest (from final4 if overlap)
    qdict = {}
    for q in all_questions:
        qdict[str(q['question_number'])] = q
    # Sort by question_number
    questions_sorted = [qdict[str(i)] for i in range(1, 101) if str(i) in qdict]

    # Prepare metadata
    metadata = {
        "merge_date": datetime.now().isoformat(),
        "source_files": [merged_path, final4_path],
        "note": "Merged all 2022 questions, deduplicated, sorted, 100 total",
        "total_questions": len(questions_sorted)
    }
    if 'metadata' in merged:
        metadata['original_metadata'] = merged['metadata']
    if 'metadata' in final4:
        metadata['final4_metadata'] = final4['metadata']

    result = {
        "metadata": metadata,
        "questions": questions_sorted
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"✅ Merged and saved to {output_path} with {len(questions_sorted)} questions.")

if __name__ == "__main__":
    main() 