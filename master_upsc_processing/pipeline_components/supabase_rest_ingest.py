#!/usr/bin/env python3
"""
Supabase REST API Ingestion Script for Single Chapter
====================================================

This script ingests a single chapter JSON file into Supabase PostgreSQL database
using the Supabase REST API (supabase-py) and OpenAI embeddings (text-embedding-3-small).

Author: Adapted for UPSC Books OCR Data
"""

import os
import json
import uuid
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_ANON_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("❌ Missing Supabase credentials in environment variables")
    exit(1)
if not OPENAI_API_KEY or OPENAI_API_KEY == 'your_openai_api_key_here':
    logger.error("❌ Missing OpenAI API key in environment variables")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

CHAPTER_FILE = "Books/Environment_Book_Chapters/complete_processed/shankar_env_smart_range_01_Ch01_ECOLOGY_pages_1-10_processed.json"
TABLE_NAME = "book_chunks_hybrid_test"


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
            logger.error(f"❌ Error generating embeddings for batch {i}: {e}")
            for _ in batch:
                embeddings.append([0.0] * 1536)
    return embeddings


def load_ocr_data(json_file_path: str) -> List[Dict[str, Any]]:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'pages' in data:
        return data['pages']
    elif isinstance(data, list):
        return data
    else:
        raise ValueError(f"Unexpected data structure in {json_file_path}")


def insert_chunks_supabase(chunks_data: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[str]:
    inserted_ids = []
    for chunk_data, embedding in tqdm(zip(chunks_data, embeddings), total=len(chunks_data), desc="Inserting into Supabase"):
        chunk_id = str(uuid.uuid4())
        
        # Extract metadata from the page data
        page_metadata = chunk_data.get('metadata', {})
        
        # Create a comprehensive metadata object
        full_metadata = {
            "file_id": page_metadata.get('file_id'),
            "document_type": page_metadata.get('document_type'),
            "summary": page_metadata.get('summary'),
            "image_bbox": page_metadata.get('image_bbox'),
            "created_at": datetime.now().isoformat(),
            "page_metadata": page_metadata.get('page_metadata', {}),
            "topic_tags": page_metadata.get('topic_tags', []),
            "key_concepts": page_metadata.get('key_concepts', []),
            "difficulty_level": page_metadata.get('difficulty_level'),
            "learning_objectives": page_metadata.get('learning_objectives', []),
            "related_chapters": page_metadata.get('related_chapters', []),
            "prerequisites": page_metadata.get('prerequisites', []),
            "common_mistakes": page_metadata.get('common_mistakes', []),
            "content_analysis": page_metadata.get('content_analysis', {}),
            "image_count": page_metadata.get('image_count', 0),
            "integrated_content_length": page_metadata.get('integrated_content_length', 0)
        }
        
        record = {
            "id": chunk_id,
            "book_type": page_metadata.get('book_type'),
            "subject": page_metadata.get('subject'),
            "chapter_name": page_metadata.get('chapter_name'),
            "chapter_number": page_metadata.get('chapter_number'),
            "page_number": chunk_data.get('page_number'),
            "content": chunk_data.get('content'),
            "source_url": None,  # Can be set if you have a source URL
            "book_name": page_metadata.get('book_name'),
            "created_at": datetime.now().isoformat(),
            "metadata": full_metadata,
            "section_name": f"Page {chunk_data.get('page_number')} - {page_metadata.get('chapter_name', 'Unknown')}",
            "embedding": embedding
        }
        
        try:
            response = supabase.table(TABLE_NAME).insert(record).execute()
            if response.data:
                inserted_ids.append(chunk_id)
                logger.debug(f"✅ Inserted chunk {chunk_id} for page {chunk_data.get('page_number')}")
            else:
                logger.error(f"❌ Failed to insert chunk {chunk_id}: {response}")
        except Exception as e:
            logger.error(f"❌ Error inserting chunk {chunk_id}: {e}")
    return inserted_ids


def preview_data_mapping(chunks_data: List[Dict[str, Any]]):
    """Preview the data mapping for the first chunk."""
    if not chunks_data:
        logger.warning("No chunks data to preview")
        return
    
    first_chunk = chunks_data[0]
    page_metadata = first_chunk.get('metadata', {})
    
    logger.info("📋 Data Mapping Preview (First Chunk):")
    logger.info("-" * 50)
    logger.info(f"book_type: {page_metadata.get('book_type')}")
    logger.info(f"subject: {page_metadata.get('subject')}")
    logger.info(f"chapter_name: {page_metadata.get('chapter_name')}")
    logger.info(f"chapter_number: {page_metadata.get('chapter_number')}")
    logger.info(f"page_number: {first_chunk.get('page_number')}")
    logger.info(f"book_name: {page_metadata.get('book_name')}")
    logger.info(f"content_length: {len(first_chunk.get('content', ''))}")
    logger.info(f"topic_tags: {page_metadata.get('topic_tags', [])}")
    logger.info(f"key_concepts: {page_metadata.get('key_concepts', [])}")
    logger.info(f"difficulty_level: {page_metadata.get('difficulty_level')}")
    logger.info("-" * 50)


def main():
    logger.info(f"Processing chapter file: {CHAPTER_FILE}")
    if not os.path.exists(CHAPTER_FILE):
        logger.error(f"Chapter file not found: {CHAPTER_FILE}")
        return
    
    chunks_data = load_ocr_data(CHAPTER_FILE)
    logger.info(f"Loaded {len(chunks_data)} chunks from {CHAPTER_FILE}")
    
    # Preview the data mapping
    preview_data_mapping(chunks_data)
    
    contents = [chunk.get('content', '') for chunk in chunks_data]
    embeddings = generate_openai_embeddings(contents)
    inserted_ids = insert_chunks_supabase(chunks_data, embeddings)
    logger.info(f"✅ Inserted {len(inserted_ids)} chunks into Supabase table '{TABLE_NAME}'")

if __name__ == "__main__":
    main() 