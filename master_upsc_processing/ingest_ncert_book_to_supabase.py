import os
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client
from tqdm import tqdm
import glob
import shutil

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_ANON_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

assert SUPABASE_URL and SUPABASE_KEY, "Supabase credentials missing in environment variables."
assert OPENAI_API_KEY, "OpenAI API key missing in environment variables."

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

PROCESSED_JSON_DIR = "master_upsc_processing/Books/NCERT_Books/processed_json"
STORE_IN_VDB_DIR = os.path.join(PROCESSED_JSON_DIR, "store_in_vdb")
os.makedirs(STORE_IN_VDB_DIR, exist_ok=True)
TABLE_NAME = "book_chunks_hybrid_test"

SAMPLE_PROCESSED_BOOK = "history_12_themes_in_indian_history_3_complete_book.json"


def generate_openai_embeddings(texts: List[str], batch_size: int = 10) -> List[List[float]]:
    embeddings = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Generating OpenAI embeddings"):
        batch = texts[i:i+batch_size]
        try:
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=batch
            )
            batch_embeddings = [embedding.embedding for embedding in response.data]
            embeddings.extend(batch_embeddings)
        except Exception as e:
            print(f"Error generating embeddings for batch {i}: {e}")
            for _ in batch:
                embeddings.append([0.0] * 1536)  # Fallback: zero vector
    return embeddings


def load_book_pages(json_file_path: str) -> List[Dict[str, Any]]:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['pages']


def insert_chunks_supabase(chunks_data: List[Dict[str, Any]], embeddings: List[List[float]]):
    for chunk_data, embedding in tqdm(zip(chunks_data, embeddings), total=len(chunks_data), desc="Inserting into Supabase"):
        chunk_id = str(uuid.uuid4())
        page_metadata = chunk_data.get('metadata', {})
        record = {
            "id": chunk_id,
            "book_type": chunk_data.get('book_type'),
            "subject": chunk_data.get('subject'),
            "chapter_name": chunk_data.get('chapter_name'),
            "chapter_number": chunk_data.get('chapter_number'),
            "page_number": chunk_data.get('page_number'),
            "content": chunk_data.get('content'),
            "source_url": chunk_data.get('source_url'),
            "book_name": chunk_data.get('book_name'),
            "created_at": chunk_data.get('created_at', datetime.now().isoformat()),
            "metadata": page_metadata,
            "section_name": chunk_data.get('section_name', f"Page {chunk_data.get('page_number')} - {chunk_data.get('chapter_name', 'Unknown')}"),
            "embedding": embedding
        }
        try:
            response = supabase.table(TABLE_NAME).insert(record).execute()
            if response.data:
                print(f"✅ Inserted page {chunk_data.get('page_number')}")
            else:
                print(f"❌ Failed to insert page {chunk_data.get('page_number')}: {response}")
        except Exception as e:
            print(f"❌ Error inserting page {chunk_data.get('page_number')}: {e}")


def get_all_book_jsons(directory: str) -> List[str]:
    files = glob.glob(f"{directory}/*_complete_book.json")
    # Exclude report files, retry_results dir, and the already processed sample book
    files = [f for f in files if not f.endswith("report.json") and "/retry_results/" not in f]
    files = [f for f in files if not f.endswith(SAMPLE_PROCESSED_BOOK)]
    return files


def main():
    book_files = get_all_book_jsons(PROCESSED_JSON_DIR)
    print(f"Found {len(book_files)} books to ingest.")
    for book_json in book_files:
        print(f"\n--- Ingesting book: {book_json} ---")
        pages = load_book_pages(book_json)
        print(f"Loaded {len(pages)} pages.")
        contents = [page['content'] for page in pages]
        embeddings = generate_openai_embeddings(contents)
        insert_chunks_supabase(pages, embeddings)
        # After successful ingestion, move the file
        dest_path = os.path.join(STORE_IN_VDB_DIR, os.path.basename(book_json))
        shutil.move(book_json, dest_path)
        print(f"Moved {book_json} to {dest_path}")
        print(f"✅ Done ingesting book: {book_json}")

if __name__ == "__main__":
    main() 