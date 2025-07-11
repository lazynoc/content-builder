# Master UPSC Processing

This folder contains the essential files for processing UPSC books with improved OCR and AI-generated summaries.

## Structure

```
master_upsc_processing/
├── pipeline_components/          # Core OCR processing components
│   └── upsc_book_ocr_extractor.py  # Main OCR extractor with AI summaries
├── Books/                        # Input PDF files and output
│   └── Environment_Book_Chapters/
│       ├── smart_sequential/     # Input PDF chapters
│       └── complete_processed_with_summaries/  # Output JSON files
├── launch_processing.py          # Main launcher script
├── test_single_chapter_ocr.py    # Test script for single chapter
├── requirements.txt              # Python dependencies
└── README.md                     # Original project README
```

## Quick Start

1. **Set Environment Variables:**
   ```bash
   export MISTRAL_API_KEY="your_mistral_api_key"
   export OPENAI_API_KEY="your_openai_api_key"
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Full Processing:**
   ```bash
   python3 launch_processing.py
   ```

4. **Test Single Chapter:**
   ```bash
   python3 test_single_chapter_ocr.py
   ```

## Features

- **Dynamic Book Detection**: Automatically detects book subject from file paths
- **AI-Generated Summaries**: 1-2 line summaries for each page
- **AI-Generated Keywords**: 5-8 relevant keywords per page
- **Rich Metadata**: Complete metadata structure for database ingestion
- **Image Integration**: Combines text and image descriptions
- **Generic Processing**: Works with any UPSC book subject

## Output

Each chapter generates a JSON file with:
- Page-by-page content with OCR text
- AI-generated summaries and keywords
- Complete metadata structure
- Image descriptions and positions
- Chapter and subject information

## Files Included

- **pipeline_components/**: All core processing components
- **Books/**: Complete book structure with input PDFs
- **launch_processing.py**: Main processing script
- **test_single_chapter_ocr.py**: Test script
- **requirements.txt**: Dependencies
- **README.md**: Original documentation 