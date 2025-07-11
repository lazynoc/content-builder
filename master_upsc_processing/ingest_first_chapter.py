#!/usr/bin/env python3
"""
Ingest First Chapter Script
===========================

This script processes the first chapter JSON file and moves it to 'stored_in_vdb' folder.
"""

import os
import json
import uuid
import logging
import shutil
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_ANON_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY]):
    logger.error("❌ Missing environment variables")
    exit(1)

# Type assertion since we've already checked they're not None
supabase: Client = create_client(str(SUPABASE_URL), str(SUPABASE_KEY))
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Directory paths
SOURCE_DIR = "Books/Environment_Book_Chapters/complete_processed_with_summaries"
STORED_DIR = "Books/Environment_Book_Chapters/stored_in_vdb"
TABLE_NAME = "book_chunks_hybrid_test"

# Create stored directory
os.makedirs(STORED_DIR, exist_ok=True)


def generate_embeddings(texts, batch_size=10):
    """Generate OpenAI embeddings."""
    embeddings = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings", leave=False):
        batch = texts[i:i+batch_size]
        try:
            response = openai_client.embeddings.create(model="text-embedding-3-small", input=batch)
            embeddings.extend([embedding.embedding for embedding in response.data])
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            embeddings.extend([[0.0] * 1536] * len(batch))
    return embeddings


def load_data(json_file):
    """Load JSON data."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['pages'] if isinstance(data, dict) and 'pages' in data else data


def check_existing(file_id):
    """Check if file already exists in database."""
    try:
        response = supabase.table(TABLE_NAME).select("id").eq("metadata->file_id", file_id).execute()
        return len(response.data) > 0
    except:
        return False


def insert_chunks(chunks_data, embeddings, file_id):
    """Insert chunks into Supabase."""
    inserted_ids = []
    
    for chunk_data, embedding in tqdm(zip(chunks_data, embeddings), total=len(chunks_data), desc="Inserting", leave=False):
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
            "created_at": chunk_data.get('created_at'),
            "metadata": page_metadata,
            "section_name": chunk_data.get('section_name'),
            "embedding": embedding
        }
        
        try:
            response = supabase.table(TABLE_NAME).insert(record).execute()
            if response.data:
                inserted_ids.append(chunk_id)
        except Exception as e:
            logger.error(f"Insert error: {e}")
    
    return inserted_ids


def process_file(json_file):
    """Process a single file."""
    file_name = os.path.basename(json_file)
    logger.info(f"📄 Processing: {file_name}")
    
    try:
        chunks_data = load_data(json_file)
        logger.info(f"   Loaded {len(chunks_data)} chunks")
        
        file_id = chunks_data[0].get('metadata', {}).get('file_id', file_name.replace('.json', ''))
        
        if check_existing(file_id):
            logger.warning(f"   ⚠️  Already exists, skipping...")
            return {'status': 'skipped', 'chunks': 0}
        
        contents = [chunk.get('content', '') for chunk in chunks_data]
        embeddings = generate_embeddings(contents)
        inserted_ids = insert_chunks(chunks_data, embeddings, file_id)
        
        logger.info(f"   ✅ Inserted {len(inserted_ids)} chunks")
        return {'status': 'success', 'chunks': len(inserted_ids)}
        
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return {'status': 'error', 'chunks': 0}


def move_file(json_file):
    """Move file to stored directory."""
    try:
        file_name = os.path.basename(json_file)
        destination = os.path.join(STORED_DIR, file_name)
        shutil.move(json_file, destination)
        logger.info(f"   📁 Moved to stored_in_vdb")
        return True
    except Exception as e:
        logger.error(f"   ❌ Move error: {e}")
        return False


def main():
    """Main function."""
    logger.info("🚀 Starting First Chapter Processing")
    logger.info("=" * 40)
    
    # Get the first chapter file
    if not os.path.exists(SOURCE_DIR):
        logger.error(f"Source directory not found: {SOURCE_DIR}")
        return
    
    json_files = []
    for file in os.listdir(SOURCE_DIR):
        if file.endswith('.json') and 'with_summaries' in file:
            json_files.append(os.path.join(SOURCE_DIR, file))
    
    json_files.sort()
    
    if not json_files:
        logger.error("No files found to process")
        return
    
    # Process only the first file
    json_file = json_files[0]
    logger.info(f"Found {len(json_files)} files, processing first one")
    
    result = process_file(json_file)
    
    # Move file if successful or skipped
    if result['status'] in ['success', 'skipped']:
        move_file(json_file)
    
    # Summary
    logger.info("\n" + "=" * 40)
    logger.info("📊 SUMMARY")
    logger.info("=" * 40)
    logger.info(f"Status: {result['status']}")
    logger.info(f"Chunks processed: {result['chunks']}")
    logger.info("=" * 40)


if __name__ == "__main__":
    main() 