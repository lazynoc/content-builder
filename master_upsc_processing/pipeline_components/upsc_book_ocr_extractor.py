#!/usr/bin/env python3
"""
UPSC Book OCR Extractor with Vector Database Integration
========================================================

This script extracts structured data from UPSC books using Mistral AI's OCR API
and stores the results in a PostgreSQL vector database for chatbot functionality.

Features:
- Specialized for UPSC book content
- Extracts chapter information, subject details, and page metadata
- Structured data extraction with custom Pydantic models
- PostgreSQL database integration
- Vector database ready for chatbot queries
- Metadata extraction matching the required schema

Author: Adapted from Mistral AI Cookbook for UPSC Books
"""

import os
import json
import base64
import argparse
import uuid
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Third-party imports
from pydantic import BaseModel, Field
from enum import Enum
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from openai import OpenAI

# Mistral AI imports
from mistralai import Mistral
from mistralai.models import OCRResponse
from mistralai.extra import response_format_from_pydantic_model

# Load environment variables
load_dotenv()


class ImageType(str, Enum):
    """Enumeration for different types of images that can be detected."""
    GRAPH = "graph"
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    CHART = "chart"
    DIAGRAM = "diagram"
    PHOTO = "photo"
    FIGURE = "figure"


class UPSCBookImage(BaseModel):
    """Model for UPSC book image annotations."""
    image_type: ImageType = Field(..., description="The type of the image detected.")
    subject: str = Field(..., description="The subject or topic of the content (e.g., 'Environment', 'Geography', 'History').")
    chapter_name: str = Field(..., description="The name of the chapter or section.")
    chapter_number: Optional[str] = Field(None, description="The chapter number if available.")
    class_name: str = Field(default="UPSC", description="The class or level (default: UPSC).")
    page_number: Optional[int] = Field(None, description="The page number if visible.")
    short_description: str = Field(..., description="A brief description of the content or image.")
    file_name: Optional[str] = Field(None, description="The original file name of the document.")
    document_type: str = Field(..., description="The type of document content (e.g., 'text', 'table', 'diagram').")
    summary: Optional[str] = Field(None, description="A summary of the content if applicable.")


class UPSCBookDocument(BaseModel):
    """Model for UPSC book document-level annotations."""
    language: str = Field(default="en", description="The primary language of the document.")
    title: str = Field(..., description="The title or main heading of the document.")
    subject: str = Field(..., description="The main subject of the book (e.g., 'Environment', 'Geography').")
    book_name: str = Field(..., description="The name of the book or document.")
    class_name: str = Field(default="UPSC", description="The class or level.")
    summary: str = Field(..., description="A comprehensive summary of the document content.")
    document_type: str = Field(..., description="The type of document (e.g., 'textbook', 'study_material').")
    page_count: int = Field(..., description="Total number of pages in the document.")
    extracted_date: Optional[str] = Field(None, description="Date when the document was processed.")


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, db_url: str):
        """
        Initialize database connection.
        
        Args:
            db_url: PostgreSQL connection string
        """
        self.db_url = db_url
        self.conn = None
    
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(self.db_url)
            print("Database connection established successfully!")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")
    
    def insert_book_chunk(self, chunk_data: Dict[str, Any]) -> str:
        """
        Insert a book chunk into the database.
        
        Args:
            chunk_data: Dictionary containing chunk data
            
        Returns:
            The UUID of the inserted record
        """
        if not self.conn:
            raise Exception("Database connection not established")
        
        chunk_id = str(uuid.uuid4())
        
        query = """
        INSERT INTO public.book_chunks_hybrid_test (
            id, book_type, subject, chapter_name, chapter_number, page_number,
            content, source_url, book_name, created_at, metadata, section_name
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (
                    chunk_id,
                    chunk_data.get('book_type'),
                    chunk_data.get('subject'),
                    chunk_data.get('chapter_name'),
                    chunk_data.get('chapter_number'),
                    chunk_data.get('page_number'),
                    chunk_data.get('content'),
                    chunk_data.get('source_url'),
                    chunk_data.get('book_name'),
                    chunk_data.get('created_at'),
                    json.dumps(chunk_data.get('metadata', {})),
                    chunk_data.get('section_name')
                ))
                self.conn.commit()
                print(f"Inserted chunk with ID: {chunk_id}")
                return chunk_id
        except Exception as e:
            self.conn.rollback()
            print(f"Error inserting chunk: {e}")
            raise
    
    def get_existing_chunks(self, file_id: str) -> List[str]:
        """
        Get existing chunk IDs for a given file to avoid duplicates.
        
        Args:
            file_id: The file identifier
            
        Returns:
            List of existing chunk IDs
        """
        if not self.conn:
            raise Exception("Database connection not established")
        
        query = """
        SELECT id FROM public.book_chunks_hybrid_test 
        WHERE metadata->>'file_id' = %s
        """
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (file_id,))
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching existing chunks: {e}")
            return []


class UPSCBookOCRExtractor:
    """Main class for UPSC book OCR extraction using Mistral AI."""
    
    def __init__(self, api_key: str, db_manager: Optional[DatabaseManager] = None, openai_api_key: Optional[str] = None):
        """
        Initialize the UPSC Book OCR Extractor.
        
        Args:
            api_key: Mistral AI API key
            db_manager: Optional database manager for storing results
            openai_api_key: Optional OpenAI API key for summary generation
        """
        self.client = Mistral(api_key=api_key)
        self.model = "mistral-ocr-latest"
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.db_manager = db_manager
    
    def encode_pdf(self, pdf_path: str) -> Optional[str]:
        """
        Encode PDF file to base64 string.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Base64 encoded string or None if error
        """
        try:
            with open(pdf_path, "rb") as pdf_file:
                return base64.b64encode(pdf_file.read()).decode('utf-8')
        except FileNotFoundError:
            print(f"Error: The file {pdf_path} was not found.")
            return None
        except Exception as e:
            print(f"Error encoding PDF: {e}")
            return None
    
    def extract_upsc_book_data(self, 
                              pdf_path: str, 
                              file_id: str,
                              source_url: Optional[str] = None,
                              pages: Optional[List[int]] = None,
                              include_images: bool = False) -> Optional[List[Dict[str, Any]]]:
        
        # Detect if this is an NCERT book based on filename pattern
        is_ncert = '_class_' in file_id and '_book_' in file_id
        
        if is_ncert:
            # Use NCERT-specific metadata extraction
            ncert_info = self._extract_ncert_info_from_filename(file_id)
            chapter_info = {
                "chapter_number": ncert_info.get("chapter_number"),
                "chapter_name": ncert_info.get("chapter_name"),
                "start_page": None,  # NCERT files don't have page ranges in filename
                "end_page": None,
                "part": ncert_info.get("part")
            }
        else:
            # Use Environment book metadata extraction
            chapter_info = self._extract_chapter_info_from_filename(file_id)
        """
        Extract structured data from UPSC book PDF using official Mistral OCR with annotations.
        Handles large PDFs by processing in chunks (BBox annotations have no page limit).
        
        Args:
            pdf_path: Path to the PDF file
            file_id: Unique identifier for the file
            source_url: Optional source URL for the document
            pages: List of page indices to process (None for all pages)
            include_images: Whether to include base64 encoded images
            
        Returns:
            List of dictionaries containing extracted data per page
        """
        print(f"Extracting UPSC book data from {pdf_path}...")
        
        base64_pdf = self.encode_pdf(pdf_path)
        if not base64_pdf:
            return None
        
        # If specific pages are requested, process them in chunks of 8
        if pages:
            return self._process_pages_in_chunks(base64_pdf, pages, file_id, source_url, include_images, is_ncert)
        
        # If no pages specified, process the entire document in chunks
        try:
            # Process all pages in chunks (no page limit with BBox annotations)
            all_pages = list(range(50))  # Assume max 50 pages, will be truncated if less
            return self._process_pages_in_chunks(base64_pdf, all_pages, file_id, source_url, include_images, is_ncert)
            
        except Exception as e:
            print(f"Error during UPSC book extraction: {e}")
            return None
    
    def _process_pages_in_chunks(self, base64_pdf: str, pages: List[int], file_id: str, 
                                source_url: Optional[str], include_images: bool, is_ncert: bool = False) -> List[Dict[str, Any]]:
        """
        Process all pages at once (Mistral can handle large files efficiently).
        
        Args:
            base64_pdf: Base64 encoded PDF
            pages: List of page indices to process
            file_id: File identifier
            source_url: Optional source URL
            include_images: Whether to include images
            
        Returns:
            Combined results from all pages
        """
        print(f"Processing all {len(pages)} pages at once...")
        
        results = self._process_single_chunk(base64_pdf, pages, file_id, source_url, include_images, is_ncert)
        if results:
            return results
        else:
            print(f"Failed to process file")
            return []
    
    def _process_single_chunk(self, base64_pdf: str, pages: List[int], file_id: str,
                             source_url: Optional[str], include_images: bool, is_ncert: bool = False) -> Optional[List[Dict[str, Any]]]:
        """
        Process a single chunk of pages with BBox annotations.
        
        Args:
            base64_pdf: Base64 encoded PDF
            pages: List of page indices
            file_id: File identifier
            source_url: Optional source URL
            include_images: Whether to include images
            
        Returns:
            Processed results for the chunk
        """
        
        try:
            response = self.client.ocr.process(
                model=self.model,
                pages=pages,
                document={
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{base64_pdf}"
                },
                bbox_annotation_format=response_format_from_pydantic_model(UPSCBookImage),
                # Removed document_annotation_format to avoid 8-page limit
                # We only need BBox annotations for image descriptions
                include_image_base64=include_images
            )
            
            return self._process_upsc_response(response, file_id, source_url, is_ncert)
            
        except Exception as e:
            print(f"Error processing chunk: {e}")
            return None
    
    def _process_upsc_response(self, ocr_response: OCRResponse, file_id: str, source_url: Optional[str] = None, is_ncert: bool = False) -> List[Dict[str, Any]]:
        """
        Process OCR response into the required UPSC book format with advanced metadata propagation.
        
        Args:
            ocr_response: OCR response object
            file_id: Unique identifier for the file
            source_url: Optional source URL
            
        Returns:
            List of processed page data with intelligent metadata propagation
        """
        processed_pages = []
        
        # Track current metadata for propagation - now dynamic
        current_metadata = {
            "subject": "Unknown",
            "chapter_name": "Unknown", 
            "chapter_number": None,
            "book_name": "Unknown",
            "document_type": "textbook",
            "class": "UPSC"
        }
        
        # Try to extract book info from filename or first page content
        if is_ncert:
            # Use NCERT-specific book info extraction
            ncert_info = self._extract_ncert_info_from_filename(file_id)
            current_metadata["subject"] = ncert_info.get("subject", "Unknown")
            current_metadata["book_name"] = ncert_info.get("book_name", "Unknown")
            current_metadata["class"] = ncert_info.get("class", "UPSC")
            current_metadata["chapter_name"] = ncert_info.get("chapter_name", "Unknown")
            current_metadata["chapter_number"] = ncert_info.get("chapter_number")
            current_metadata["part"] = ncert_info.get("part")
            # NCERT books don't have page ranges in filename, so set to None
            start_page = None
            end_page = None
        else:
            # Use Environment book info extraction
            book_info = self._extract_book_info_from_filename(file_id)
            if book_info and book_info.get("book_name"):
                current_metadata["book_name"] = book_info["book_name"]
            if book_info and book_info.get("subject"):
                current_metadata["subject"] = book_info["subject"]
            
            # Extract chapter info including page range from filename - PRIORITY 1
            chapter_info = self._extract_chapter_info_from_filename(file_id)
            start_page = chapter_info.get("start_page")
            end_page = chapter_info.get("end_page")
            
            # Use filename-extracted chapter info as PRIMARY source (hardcoded)
            if chapter_info.get("chapter_name"):
                current_metadata["chapter_name"] = chapter_info["chapter_name"]
            if chapter_info.get("chapter_number"):
                current_metadata["chapter_number"] = chapter_info["chapter_number"]
            if chapter_info.get("part"):
                current_metadata["part"] = chapter_info["part"]
        
        # Track chapter progression for fallback
        chapter_counter = 1
        seen_chapters = set()
        
        for page in ocr_response.pages:
            images = page.images or []
            
            # Find the first image with a valid annotation
            annotation = {}
            image_data = None
            
            for img in images:
                if hasattr(img, 'image_annotation') and img.image_annotation:
                    image_data = img
                    try:
                        annotation = (img.image_annotation if isinstance(img.image_annotation, dict) 
                                    else json.loads(img.image_annotation))
                        break
                    except (json.JSONDecodeError, TypeError):
                        annotation = {}
            
            # Fallback if no annotated image found
            image_data = image_data or (images[0] if images else {})
            
            # Safe value accessor
            def safe(val, fallback="Unknown"):
                return val if val is not None and val != "Unknown" else fallback
            
            # Analyze content for chapter detection
            content_analysis = self._analyze_page_content(page.markdown or "")
            
            # Update current metadata with new annotations (if any)
            # For NCERT books, prioritize filename-extracted metadata over OCR annotations
            if not is_ncert and annotation.get('subject') and annotation['subject'] != "Unknown":
                current_metadata["subject"] = annotation['subject']
            
            if annotation.get('file_name') and annotation['file_name'] != "Unknown":
                current_metadata["book_name"] = annotation['file_name']
            
            if annotation.get('document_type'):
                current_metadata["document_type"] = annotation['document_type']
            
            # DISABLED: OCR-based chapter detection - using hardcoded metadata from filename instead
            new_chapter_detected = False
            
            # Update chapter number logic
            chapter_number = current_metadata["chapter_number"]
            
            # Priority 1: Use annotation chapter number
            if annotation.get('chapter_number') and annotation['chapter_number'] != "N/A":
                try:
                    chapter_number = int(annotation['chapter_number'])
                    current_metadata["chapter_number"] = chapter_number
                except (ValueError, TypeError):
                    chapter_number = annotation['chapter_number']
                    current_metadata["chapter_number"] = chapter_number
            
            # Priority 2: Use content analysis chapter number
            elif content_analysis.get('chapter_number'):
                chapter_number = content_analysis['chapter_number']
                current_metadata["chapter_number"] = chapter_number
            
            # Priority 3: Auto-increment chapter number for new chapters
            elif new_chapter_detected and current_metadata["chapter_name"] not in seen_chapters:
                seen_chapters.add(current_metadata["chapter_name"])
                chapter_number = chapter_counter
                current_metadata["chapter_number"] = chapter_number
                chapter_counter += 1
            
            # Priority 4: Use existing chapter number
            else:
                chapter_number = current_metadata["chapter_number"]
            
            # Generate intelligent section name
            section_name = self._generate_section_name(
                annotation.get('short_description'),
                content_analysis,
                page.index + 1,
                current_metadata["chapter_name"]
            )
            
            # CREATE INTEGRATED CONTENT FLOW - Combine text and image descriptions
            integrated_content = self._create_integrated_content(page.markdown or "", images)
            
            # Generate page summary and keywords using OpenAI
            summary_data = self._generate_page_summary_with_keywords(integrated_content)
            page_summary = summary_data.get("summary")
            page_keywords = summary_data.get("keywords", [])
            
            # Calculate actual page number
            actual_page_number = None
            if is_ncert:
                # For NCERT books: Calculate cumulative page numbers across chapters
                # Use the actual page index within this chapter file
                chapter_num = current_metadata.get("chapter_number", 1)
                if isinstance(chapter_num, str):
                    try:
                        chapter_num = int(chapter_num)
                    except (ValueError, TypeError):
                        chapter_num = 1
                
                # For now, use page.index + 1 for the current chapter
                # TODO: In a future enhancement, we could track cumulative pages across chapters
                # by processing chapters in order and maintaining a running total
                actual_page_number = page.index + 1
            elif start_page is not None and end_page is not None:
                # For Environment books: Use existing page range logic
                actual_page_number = start_page + page.index
            else:
                # Fallback to annotation or page index
                actual_page_number = annotation.get('page_number') or (page.index + 1)
            
            # Create page data structure with integrated content
            page_data = {
                "book_type": "UPSC-NCERT" if is_ncert else "UPSC",
                "subject": current_metadata["subject"],
                "chapter_name": current_metadata["chapter_name"],
                "chapter_number": chapter_number,
                "page_number": actual_page_number,
                "content": integrated_content,  # Use integrated content instead of raw markdown
                "source_url": source_url,
                "book_name": current_metadata["book_name"],
                "created_at": datetime.now().isoformat(),
                "section_name": section_name,
                "metadata": {
                    "file_id": file_id,
                    "document_type": current_metadata["document_type"],
                    "short_description": section_name,
                    "summary": page_summary or annotation.get('summary') or content_analysis.get('summary'),
                    "page_number": actual_page_number,
                    "subject": current_metadata["subject"],
                    "class": current_metadata["class"],
                    "chapter_name": current_metadata["chapter_name"],
                    "chapter_number": chapter_number,
                    "file_name": current_metadata["book_name"],
                    "part": current_metadata.get("part"),
                    "start_page": start_page,
                    "end_page": end_page,
                    "image_id": getattr(image_data, 'id', None) if image_data else None,
                    "image_bbox": {
                        "top_left_x": getattr(image_data, 'top_left_x', 0) if image_data else 0,
                        "top_left_y": getattr(image_data, 'top_left_y', 0) if image_data else 0,
                        "bottom_right_x": getattr(image_data, 'bottom_right_x', 0) if image_data else 0,
                        "bottom_right_y": getattr(image_data, 'bottom_right_y', 0) if image_data else 0
                    },
                    "dimensions": getattr(page, 'dimensions', None).dict() if getattr(page, 'dimensions', None) and hasattr(getattr(page, 'dimensions', None), 'dict') else getattr(page, 'dimensions', None),
                    "content_analysis": content_analysis,
                    "image_count": len(images),
                    "integrated_content_length": len(integrated_content),
                    # Add rich metadata like the original files
                    "topic_tags": content_analysis.get('key_topics', []),
                    "key_concepts": content_analysis.get('key_topics', []),
                    "keywords": page_keywords,  # Add AI-generated keywords
                    "difficulty_level": "intermediate",
                    "learning_objectives": [],
                    "related_chapters": [],
                    "prerequisites": [],
                    "common_mistakes": []
                }
            }
            
            processed_pages.append(page_data)
        
        return processed_pages
    
    def _create_integrated_content(self, markdown_content: str, images: List[Any]) -> str:
        """
        Create integrated content flow by combining text and image descriptions in reading order.
        
        Args:
            markdown_content: The raw markdown content from OCR
            images: List of image objects with annotations
            
        Returns:
            Integrated content string with text and image descriptions in natural flow
        """
        if not markdown_content and not images:
            return ""
        
        # Extract image references and their positions from markdown
        import re
        image_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', markdown_content)
        
        # Create a map of image filenames to their descriptions
        image_descriptions = {}
        for img in images:
            if hasattr(img, 'image_annotation') and img.image_annotation:
                try:
                    annotation = (img.image_annotation if isinstance(img.image_annotation, dict) 
                                else json.loads(img.image_annotation))
                    # Get image filename from annotation or generate one
                    img_filename = getattr(img, 'id', f'img-{len(image_descriptions)}.jpeg')
                    image_descriptions[img_filename] = annotation.get('short_description', '')
                except (json.JSONDecodeError, TypeError):
                    continue
        
        # If no image descriptions found, return original content
        if not image_descriptions:
            return markdown_content
        
        # Replace image references with integrated descriptions
        integrated_content = markdown_content
        
        for alt_text, img_filename in image_refs:
            if img_filename in image_descriptions:
                description = image_descriptions[img_filename]
                # Create a more descriptive image reference
                enhanced_ref = f"\n\n**[IMAGE: {description}]**\n\n"
                integrated_content = integrated_content.replace(f"![{alt_text}]({img_filename})", enhanced_ref)
        
        # Add any remaining image descriptions that weren't referenced in markdown
        referenced_images = {ref[1] for ref in image_refs}
        for img_filename, description in image_descriptions.items():
            if img_filename not in referenced_images and description:
                integrated_content += f"\n\n**[ADDITIONAL IMAGE: {description}]**\n\n"
        
        return integrated_content
    
    def _analyze_page_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze page content to extract chapter information and generate summaries.
        
        Args:
            content: The page content text
            
        Returns:
            Dictionary with analysis results
        """
        import re
        
        analysis = {
            "chapter_name": None,
            "chapter_number": None,
            "summary": None,
            "content_type": "text",
            "key_topics": [],
            "is_front_matter": False,
            "confidence": 0.0
        }
        
        if not content:
            return analysis
        
        content_lower = content.lower()
        content_upper = content.upper()
        
        # Check if this is front matter (dedication, introduction, etc.)
        front_matter_indicators = [
            'dedication', 'introduction', 'preface', 'acknowledgment', 'copyright',
            'isbn', 'published by', 'shankar ias academy', 'sculpting minds',
            'part -', 'chapter -', 'table of contents', 'index'
        ]
        
        if any(indicator in content_lower for indicator in front_matter_indicators):
            analysis["is_front_matter"] = True
            analysis["confidence"] = 0.1
            return analysis
        
        # Much more flexible chapter detection patterns for UPSC books
        chapter_patterns = [
            # Pattern 1: "Chapter 1: Ecology" or "CHAPTER 1: ECOLOGY"
            r'chapter\s+(\d+)[:\s]*([^.\n\r]{3,100})',
            # Pattern 2: "1. Ecology" or "1 ECOLOGY"
            r'^(\d+)[.\s]+([^.\n\r]{3,100})',
            # Pattern 3: "CHAPTER 1 ECOLOGY" (all caps)
            r'chapter\s+(\d+)\s+([A-Z\s]{3,100})',
            # Pattern 4: "1 ECOLOGY" (all caps)
            r'^(\d+)\s+([A-Z\s]{3,100})',
            # Pattern 5: "Chapter 1 Function of an Ecosystem"
            r'chapter\s+(\d+)\s+([^.\n\r]{3,100})',
            # Pattern 6: "1 Function of an Ecosystem"
            r'^(\d+)\s+([^.\n\r]{3,100})',
            # Pattern 7: Just "ECOLOGY" (standalone chapter title)
            r'^ECOLOGY$',
            # Pattern 8: Just "FUNCTION OF AN ECOSYSTEM" (standalone chapter title)
            r'^FUNCTION OF AN ECOSYSTEM$',
            # Pattern 9: "ECOLOGY" at start of line
            r'^ECOLOGY\s',
            # Pattern 10: "FUNCTION OF AN ECOSYSTEM" at start of line
            r'^FUNCTION OF AN ECOSYSTEM\s',
            # Pattern 11: Any line that starts with a number followed by text (more flexible)
            r'^(\d+)\s*[.\-\s]*([A-Z][^.\n\r]{2,100})',
            # Pattern 12: Look for "ECOLOGY" anywhere in the first few lines
            r'ECOLOGY',
            # Pattern 13: Look for "FUNCTION OF AN ECOSYSTEM" anywhere in the first few lines
            r'FUNCTION OF AN ECOSYSTEM',
        ]
        
        best_match = None
        best_confidence = 0.0
        
        for i, pattern in enumerate(chapter_patterns):
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    # Handle different pattern types
                    if i >= 6 and i <= 9:  # Patterns 7-10: Standalone chapter titles
                        if 'ecology' in pattern.lower():
                            chapter_num = 1
                            chapter_name = "Ecology"
                        elif 'function' in pattern.lower():
                            chapter_num = 2
                            chapter_name = "Function of an Ecosystem"
                        else:
                            continue
                    elif i >= 10:  # Patterns 11-13: More flexible patterns
                        if 'ecology' in pattern.lower() and 'ecology' in content.lower():
                            chapter_num = 1
                            chapter_name = "Ecology"
                            confidence = 0.8
                        elif 'function' in pattern.lower() and 'function' in content.lower():
                            chapter_num = 2
                            chapter_name = "Function of an Ecosystem"
                            confidence = 0.8
                        else:
                            # Try to extract from numbered patterns
                            if match.groups():
                                chapter_num = int(match.group(1))
                                chapter_name = match.group(2).strip()
                            else:
                                continue
                    else:  # Patterns 1-6: Standard numbered patterns
                        chapter_num = int(match.group(1))
                        chapter_name = match.group(2).strip()
                    
                    # Validate chapter name quality
                    if len(chapter_name) > 3 and not chapter_name.isdigit():
                        # Check if it contains meaningful words for UPSC Environment chapters
                        meaningful_words = ['ecology', 'ecosystem', 'environment', 'biodiversity', 'conservation', 
                                          'pollution', 'climate', 'sustainable', 'development', 'natural',
                                          'function', 'structure', 'components', 'types', 'classification']
                        
                        # Check if it looks like a real chapter title (not a section)
                        is_likely_chapter = (
                            len(chapter_name.split()) <= 8 and  # Not too long
                            not any(word in chapter_name.lower() for word in ['diversity', 'organisations', 'policies', 'issues']) and  # Avoid section titles
                            (any(word in chapter_name.lower() for word in meaningful_words) or
                             len(chapter_name.split()) <= 4)  # Short titles are often chapters
                        )
                        
                        if is_likely_chapter:
                            confidence = 0.9
                        elif len(chapter_name.split()) >= 2:
                            confidence = 0.5
                        else:
                            confidence = 0.2
                        
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = (chapter_num, chapter_name)
                            
                except (ValueError, IndexError):
                    continue
        
        if best_match:
            analysis["chapter_number"] = best_match[0]
            analysis["chapter_name"] = best_match[1].title()
            analysis["confidence"] = best_confidence
        
        # Detect content type with better accuracy
        if any(word in content_lower for word in ['diagram', 'figure', 'chart', 'graph', 'illustration']):
            analysis["content_type"] = "diagram"
        elif any(word in content_lower for word in ['table', 'list', 'bullet', 'enumeration']):
            analysis["content_type"] = "table"
        elif len(content.split()) < 50:  # Very short content
            analysis["content_type"] = "header"
        
        # Extract key topics with better context
        upsc_keywords = [
            'ecosystem', 'environment', 'biodiversity', 'conservation', 'pollution', 
            'climate', 'sustainable', 'development', 'natural', 'resources',
            'forest', 'wildlife', 'marine', 'atmosphere', 'soil', 'water',
            'energy', 'renewable', 'carbon', 'greenhouse', 'ozone', 'acid rain'
        ]
        analysis["key_topics"] = [word for word in upsc_keywords if word in content_lower]
        
        # Generate better summary
        if len(content) > 100 and not analysis["is_front_matter"]:
            # Remove headers and get meaningful content
            lines = content.split('\n')
            meaningful_lines = [line.strip() for line in lines if len(line.strip()) > 20]
            
            if meaningful_lines:
                summary = meaningful_lines[0][:200]
                if len(summary) == 200:
                    summary += "..."
                analysis["summary"] = summary
        
        return analysis
    
    def _generate_page_summary(self, content: str, max_words: int = 500) -> Optional[str]:
        """
        Generate a 1-2 line summary of the page content using OpenAI.
        
        Args:
            content: The page content text
            max_words: Maximum number of words to consider for summary
            
        Returns:
            Generated summary or None if OpenAI is not available
        """
        if not self.openai_client or not content:
            return None
        
        try:
            # Import configuration
            try:
                from config.pipeline_config import OPENAI_CONFIG
                config = OPENAI_CONFIG
            except ImportError:
                # Fallback configuration
                config = {
                    "summary_model": "gpt-4o-mini",
                    "summary_max_tokens": 100,
                    "summary_temperature": 0.3,
                    "content_sample_words": 500
                }
            
            # Take first N words of content based on config
            words = content.split()
            sample_words = config.get("content_sample_words", max_words)
            if len(words) > sample_words:
                content_sample = ' '.join(words[:sample_words])
            else:
                content_sample = content
            
            # Create prompt for summary generation
            prompt = f"""Generate a concise 1-2 line summary of the following UPSC study material content. 
            Focus on the main topic, key concepts, or important information covered.
            
            Content:
            {content_sample}
            
            Summary:"""
            
            response = self.openai_client.chat.completions.create(
                model=config.get("summary_model", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise summaries of UPSC study material."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=config.get("summary_max_tokens", 100),
                temperature=config.get("summary_temperature", 0.3)
            )
            
            summary = response.choices[0].message.content.strip()
            return summary if summary else None
            
        except Exception as e:
            print(f"Error generating summary with OpenAI: {e}")
            return None
    
    def _generate_page_summary_with_keywords(self, content: str, max_words: int = 500) -> Dict[str, Any]:
        """Generate a summary and keywords for the page content using OpenAI."""
        if not self.openai_client or not content.strip():
            return {"summary": None, "keywords": []}
        
        try:
            # Truncate content to max_words for efficiency
            words = content.split()
            if len(words) > max_words:
                content = ' '.join(words[:max_words]) + "..."
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that analyzes UPSC study material. Provide a concise summary and extract relevant keywords that would be useful for exam preparation and search."
                    },
                    {
                        "role": "user", 
                        "content": f"""Analyze the following UPSC study material content and provide:
1. A 1-2 line summary
2. 5-8 relevant keywords (comma-separated)

Content:
{content}

Format your response as:
Summary: [your summary here]
Keywords: [keyword1, keyword2, keyword3, ...]"""
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse the response
            summary = None
            keywords = []
            
            lines = response_text.split('\n')
            for line in lines:
                if line.startswith('Summary:'):
                    summary = line.replace('Summary:', '').strip()
                elif line.startswith('Keywords:'):
                    keywords_text = line.replace('Keywords:', '').strip()
                    keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
            
            return {
                "summary": summary,
                "keywords": keywords
            }
            
        except Exception as e:
            print(f"Error generating summary with keywords: {e}")
            return {"summary": None, "keywords": []}
    
    def _generate_section_name(self, annotation_desc: Optional[str], content_analysis: Dict[str, Any], page_index: int, chapter_name: str) -> str:
        """
        Generate intelligent section names based on available information.
        
        Args:
            annotation_desc: Description from annotation
            content_analysis: Content analysis results
            page_index: Page index
            chapter_name: Current chapter name
            
        Returns:
            Generated section name
        """
        if annotation_desc and annotation_desc != "Unknown":
            return annotation_desc
        
        if content_analysis.get("content_type") == "diagram":
            return f"Diagram in {chapter_name}"
        elif content_analysis.get("content_type") == "table":
            return f"Table in {chapter_name}"
        elif content_analysis.get("key_topics"):
            topics = ", ".join(content_analysis["key_topics"][:2])
            return f"{topics.title()} content in {chapter_name}"
        else:
            return f"Page {page_index + 1} content in {chapter_name}"
    
    def _infer_chapter_number(self, content: str) -> Optional[int]:
        """
        Try to infer chapter number from content text.
        
        Args:
            content: The page content text
            
        Returns:
            Inferred chapter number or None
        """
        import re
        
        # Common patterns for chapter numbers
        patterns = [
            r'chapter\s+(\d+)',
            r'chapter\s+(\d+):',
            r'chapter\s+(\d+)\s*[-\u2013]',
            r'(\d+)\.\s*chapter',
            r'chapter\s+(\d+)\.',
            r'(\d+)\s*\.\s*[A-Z]',  # Number followed by dot and capital letter
        ]
        
        content_lower = content.lower()
        
        for pattern in patterns:
            match = re.search(pattern, content_lower)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _extract_chapter_info_from_filename(self, file_id: str) -> Dict[str, Any]:
        """
        Extract chapter information from filename.
        
        Args:
            file_id: The file ID (e.g., Chapter_01_ECOLOGY_pages_1-10)
            
        Returns:
            Dictionary with chapter information
        """
        chapter_info = {
            "chapter_number": None,
            "chapter_name": None,
            "start_page": None,
            "end_page": None,
            "part": None
        }
        
        try:
            # Extract chapter number (e.g., Chapter_01, Chapter_02)
            import re
            ch_match = re.search(r'Chapter_(\d+)_', file_id)
            if ch_match:
                chapter_info['chapter_number'] = int(ch_match.group(1))
            
            # Extract chapter name (everything between Chapter_XX_ and _pages)
            ch_name_match = re.search(r'Chapter_\d+_(.+?)_pages', file_id)
            if ch_name_match:
                chapter_name = ch_name_match.group(1)
                # Replace underscores with spaces for better readability
                chapter_info['chapter_name'] = chapter_name.replace('_', ' ')
            
            # Extract page range from filename
            page_match = re.search(r'pages_(\d+)-(\d+)', file_id)
            if page_match:
                chapter_info['start_page'] = int(page_match.group(1))
                chapter_info['end_page'] = int(page_match.group(2))
            
            # Determine part based on chapter number
            if chapter_info['chapter_number']:
                if chapter_info['chapter_number'] <= 24:
                    chapter_info['part'] = "Environmental Ecology"
                else:
                    chapter_info['part'] = "Acts and Policies"
                
        except Exception as e:
            print(f"Error extracting chapter info from filename: {e}")
        
        return chapter_info
    
    def _extract_ncert_info_from_filename(self, file_id: str) -> Dict[str, Any]:
        """
        Extract NCERT book information from filename.
        
        Args:
            file_id: The file ID (e.g., geography_class_9_book_contemporary_India_I_chapter_6)
            
        Returns:
            Dictionary with NCERT book information
        """
        ncert_info = {
            "subject": None,
            "class": None,
            "book_name": None,
            "chapter_number": None,
            "chapter_name": None,
            "part": None
        }
        
        try:
            # Parse filename pattern: subject_class_X_book_bookname_chapter_Y
            parts = file_id.split('_')
            
            # Extract subject (first part)
            subject = parts[0].title()  # Capitalize first letter
            
            # Map subject names to proper names
            subject_mapping = {
                "Political": "Political Science",
                "Fine": "Fine Arts"
            }
            
            ncert_info['subject'] = subject_mapping.get(subject, subject)
            
            # Find class (after 'class')
            class_index = parts.index('class')
            ncert_info['class'] = parts[class_index + 1]
            
            # Find book name (between 'book' and 'chapter')
            book_index = parts.index('book')
            chapter_index = parts.index('chapter')
            book_name_parts = parts[book_index + 1:chapter_index]
            ncert_info['book_name'] = ' '.join(book_name_parts).replace('_', ' ')
            
            # Extract chapter number
            chapter_num = parts[chapter_index + 1]
            ncert_info['chapter_number'] = int(chapter_num)
            
            # Generate chapter name based on subject and chapter number
            # This is a fallback since NCERT files don't have chapter names in filename
            ncert_info['chapter_name'] = f"Chapter {chapter_num}"
            
            # Determine part based on subject and class
            if ncert_info['subject'] == 'Geography':
                if int(ncert_info['class']) <= 10:
                    ncert_info['part'] = "Physical Geography"
                else:
                    ncert_info['part'] = "Human Geography"
            elif ncert_info['subject'] == 'History':
                ncert_info['part'] = "Indian History"
            elif ncert_info['subject'] == 'Political':
                ncert_info['part'] = "Political Science"
            elif ncert_info['subject'] == 'Fine':
                ncert_info['part'] = "Indian Art and Culture"
            else:
                ncert_info['part'] = ncert_info['subject']
                
        except Exception as e:
            print(f"Error extracting NCERT info from filename: {e}")
        
        return ncert_info
    
    def _extract_book_info_from_filename(self, file_id: str) -> Optional[Dict[str, str]]:
        """Extract book information from filename or file path."""
        try:
            # Try to extract from file path or filename
            if '/' in file_id:
                # Extract from path like: "Books/Environment_Book_Chapters/proper_chapters/Chapter_01_ECOLOGY_pages_1-10.pdf"
                path_parts = file_id.split('/')
                
                # Extract subject from folder name like "Environment_Book_Chapters"
                subject = None
                for part in path_parts:
                    if '_Book_Chapters' in part:
                        subject = part.replace('_Book_Chapters', '')
                        break
                
                # Get book name from original book file in the same folder structure
                book_name = None
                if subject:
                    # Look for the original book file in the parent folder
                    # Path pattern: Books/Environment_Book/Environment by Shankar IAS Academy (UpscStdEbooks)(page 1-346).pdf
                    book_folder = f"Books/{subject}_Book"
                    book_files = [
                        f"{subject} by Shankar IAS Academy (UpscStdEbooks)(page 1-346).pdf",
                        f"{subject} by Shankar IAS Academy (UpscStdEbooks) Indexed.pdf",
                        f"{subject} by Shankar IAS Academy.pdf"
                    ]
                    
                    # Try to find the actual book file
                    import os
                    for book_file in book_files:
                        book_path = os.path.join(book_folder, book_file)
                        if os.path.exists(book_path):
                            book_name = book_file.replace('.pdf', '')
                            break
                    
                    # If no actual file found, use the standard naming convention
                    if not book_name:
                        book_name = f"{subject} by Shankar IAS Academy"
                
                if subject and book_name:
                    return {
                        "subject": subject,
                        "book_name": book_name
                    }
            
            # Fallback: try to extract from filename itself
            if 'Environment' in file_id or 'ECOLOGY' in file_id:
                return {
                    "subject": "Environment",
                    "book_name": "Environment by Shankar IAS Academy"
                }
            elif 'Geography' in file_id:
                return {
                    "subject": "Geography", 
                    "book_name": "Geography by Shankar IAS Academy"
                }
            elif 'History' in file_id:
                return {
                    "subject": "History",
                    "book_name": "History by Shankar IAS Academy"
                }
            elif 'Polity' in file_id:
                return {
                    "subject": "Polity",
                    "book_name": "Polity by Shankar IAS Academy"
                }
            elif 'Economics' in file_id:
                return {
                    "subject": "Economics",
                    "book_name": "Economics by Shankar IAS Academy"
                }
            
            return None
        except Exception as e:
            print(f"Error extracting book info from filename: {e}")
            return None
    
    def save_to_database(self, processed_data: List[Dict[str, Any]]) -> List[str]:
        """
        Save processed data to the database.
        
        Args:
            processed_data: List of processed page data
            
        Returns:
            List of inserted chunk IDs
        """
        if not self.db_manager:
            print("No database manager provided. Skipping database save.")
            return []
        
        chunk_ids = []
        for chunk_data in processed_data:
            try:
                chunk_id = self.db_manager.insert_book_chunk(chunk_data)
                chunk_ids.append(chunk_id)
            except Exception as e:
                print(f"Error saving chunk to database: {e}")
                continue
        
        print(f"Successfully saved {len(chunk_ids)} chunks to database")
        return chunk_ids
    
    def save_to_files(self, 
                     processed_data: List[Dict[str, Any]], 
                     output_dir: str, 
                     filename: str) -> None:
        """
        Save UPSC book extraction results to a single consolidated JSON file.
        
        Args:
            processed_data: List of processed page data
            output_dir: Directory to save results
            filename: Base filename (without extension)
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create consolidated data structure
        consolidated_data = {
            "file_info": {
                "file_id": processed_data[0]["metadata"]["file_id"] if processed_data else None,
                "book_name": processed_data[0]["book_name"] if processed_data else "Unknown",
                "subject": processed_data[0]["subject"] if processed_data else "Unknown",
                "total_pages": len(processed_data),
                "extraction_date": datetime.now().isoformat(),
                "source_url": processed_data[0].get("source_url") if processed_data else None
            },
            "summary": {
                "subjects": list(set(page["subject"] for page in processed_data if page["subject"] != "Unknown")),
                "chapters": list(set(page["chapter_name"] for page in processed_data if page["chapter_name"] != "Unknown")),
                "chapter_numbers": list(set(page["chapter_number"] for page in processed_data if page["chapter_number"] is not None)),
                "content_types": list(set(page["metadata"].get("content_analysis", {}).get("content_type", "text") for page in processed_data))
            },
            "pages": processed_data
        }
        
        # Save consolidated JSON
        output_file = output_path / f"{filename}_consolidated.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
        
        print(f"UPSC book results saved to {output_file}")
        print(f"Processed {len(processed_data)} pages")
        print(f"Subjects found: {consolidated_data['summary']['subjects']}")
        print(f"Chapters found: {consolidated_data['summary']['chapters']}")
        print(f"Chapter numbers: {consolidated_data['summary']['chapter_numbers']}")
        print(f"Content types: {consolidated_data['summary']['content_types']}")


def main():
    """Main function to run the UPSC book OCR extractor."""
    parser = argparse.ArgumentParser(description="Extract structured data from UPSC books using Mistral AI OCR")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--api-key", help="Mistral AI API key (or set MISTRAL_API_KEY env var)")
    parser.add_argument("--file-id", required=True, help="Unique identifier for the file")
    parser.add_argument("--source-url", help="Source URL for the document")
    parser.add_argument("--db-url", help="PostgreSQL connection string (or set DATABASE_URL env var)")
    parser.add_argument("--output-dir", default="./upsc_output", help="Output directory for results")
    parser.add_argument("--pages", type=int, nargs="+", help="Specific pages to process (0-indexed)")
    parser.add_argument("--include-images", action="store_true", help="Include base64 encoded images in output")
    parser.add_argument("--no-save", action="store_true", help="Don't save results to files")
    parser.add_argument("--no-db", action="store_true", help="Don't save results to database")
    
    args = parser.parse_args()
    
    # Get API key from args or environment
    api_key = args.api_key or os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("Error: Mistral AI API key is required. Set --api-key or MISTRAL_API_KEY environment variable.")
        return
    
    # Initialize database manager if database URL is provided
    db_manager = None
    if not args.no_db:
        db_url = args.db_url or os.getenv("DATABASE_URL")
        if db_url:
            db_manager = DatabaseManager(db_url)
            try:
                db_manager.connect()
            except Exception as e:
                print(f"Warning: Could not connect to database: {e}")
                print("Continuing without database integration...")
                db_manager = None
        else:
            print("Warning: No database URL provided. Skipping database integration.")
    
    # Get OpenAI API key for summaries
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Initialize extractor
    extractor = UPSCBookOCRExtractor(api_key, db_manager, openai_api_key)
    
    # Extract UPSC book data
    processed_data = extractor.extract_upsc_book_data(
        args.pdf_path, 
        args.file_id,
        source_url=args.source_url,
        pages=args.pages,
        include_images=args.include_images
    )
    
    if not processed_data:
        print("UPSC book extraction failed!")
        return
    
    # Display results
    print("\n" + "="*60)
    print("UPSC BOOK EXTRACTION RESULTS")
    print("="*60)
    
    for i, page_data in enumerate(processed_data):
        print(f"\nPage {i+1}:")
        print(f"  Subject: {page_data['subject']}")
        print(f"  Chapter: {page_data['chapter_name']}")
        if page_data['chapter_number']:
            print(f"  Chapter Number: {page_data['chapter_number']}")
        print(f"  Section: {page_data['section_name']}")
        print(f"  Content Length: {len(page_data['content'])} characters")
    
    # Save to database if requested
    if db_manager and not args.no_db:
        try:
            chunk_ids = extractor.save_to_database(processed_data)
            print(f"Saved {len(chunk_ids)} chunks to database")
        except Exception as e:
            print(f"Error saving to database: {e}")
    
    # Save to files if requested
    if not args.no_save:
        filename = Path(args.pdf_path).stem
        extractor.save_to_files(processed_data, args.output_dir, filename)
    
    # Cleanup
    if db_manager:
        db_manager.disconnect()


if __name__ == "__main__":
    main() 