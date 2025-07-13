import json
import os
import openai
from tqdm import tqdm
import time
from dotenv import load_dotenv

# Explicitly load parent .env file
load_dotenv('../.env')

# Set your OpenAI API key (or use environment variable)
openai.api_key = os.getenv('OPENAI_API_KEY')
MODEL = 'gpt-4-1106-preview'  # 4.1 mini, update if needed
BATCH_SIZE = 30  # Adjust for context window
INPUT_FILE = 'uppsc_questions_complete_final.json'
OUTPUT_FILE = 'flagged_incomplete_questions.json'

PROMPT = (
    "You are an expert at reviewing exam question datasets. "
    "Here is a JSON array of multiple-choice questions. For each question, check if it is incomplete, malformed, or suspicious "
    "(e.g., missing or partial question text, missing or incomplete options, options that are not meaningful, missing question number, etc.).\n\n"
    "Return a JSON array of objects, each with:\n"
    "- 'question_number' (or 'id' if available)\n"
    "- 'reason' (why it is flagged as incomplete or suspicious)\n\n"
    "Only include questions that are incomplete or suspicious. Do not return the full questions, just the list of issues."
)

def batch_questions(questions, batch_size):
    for i in range(0, len(questions), batch_size):
        yield questions[i:i+batch_size]

def call_openai_flag_batch(batch):
    # The OpenAI v1 API expects a list of dicts for messages; type checkers may warn, but this works at runtime.
    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": json.dumps(batch)}
    ]  # type: ignore
    for _ in range(3):  # Retry up to 3 times
        try:
            response = openai.chat.completions.create(
                model=MODEL,
                messages=messages,  # type: ignore
                temperature=0.0,
                max_tokens=800
            )
            content = response.choices[0].message.content
            if content is not None:
                # Try to parse JSON from response
                try:
                    flagged = json.loads(content)
                    if isinstance(flagged, list):
                        return flagged
                except Exception:
                    # Try to extract JSON from text
                    start = content.find('[')
                    end = content.rfind(']')
                    if start != -1 and end != -1:
                        try:
                            flagged = json.loads(content[start:end+1])
                            if isinstance(flagged, list):
                                return flagged
                        except Exception:
                            pass
            return []
        except Exception as e:
            print(f"OpenAI API error: {e}. Retrying...")
            time.sleep(5)
    print("Failed to get response from OpenAI after 3 attempts.")
    return []

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    questions = data['questions']
    all_flagged = []
    for batch in tqdm(list(batch_questions(questions, BATCH_SIZE)), desc="Flagging batches"):
        flagged = call_openai_flag_batch(batch)
        if flagged:
            all_flagged.extend(flagged)
        time.sleep(1.5)  # To avoid rate limits
    print(f"Total flagged questions: {len(all_flagged)}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_flagged, f, indent=2, ensure_ascii=False)
    print(f"Flagged questions saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main() 