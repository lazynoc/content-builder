# UPPSC PDF Splitter

This directory contains scripts to split the UPPSC 2024 question paper PDF into separate Hindi and English versions.

## Files

- `UPPCS_2024_Prelims_GS1_Question_Paper.pdf` - Original bilingual PDF
- `split_uppsc_pdf.py` - Basic PDF splitting script
- `split_uppsc_pdf_advanced.py` - Advanced PDF splitting script with custom options
- `split_versions/` - Directory containing the split PDFs

## Installation

Install the required dependencies:

```bash
pip3 install PyMuPDF==1.23.8
```

## Usage

### Basic Script

Run the basic script to split the PDF into equal halves:

```bash
python3 split_uppsc_pdf.py
```

This will create:
- `split_versions/UPPCS_2024_Prelims_GS1_Question_Paper_Hindi.pdf` (left half)
- `split_versions/UPPCS_2024_Prelims_GS1_Question_Paper_English.pdf` (right half)

### Advanced Script

The advanced script offers more options:

#### Analyze PDF Layout
```bash
python3 split_uppsc_pdf_advanced.py --analyze
```

#### Custom Split Ratio
```bash
python3 split_uppsc_pdf_advanced.py --split-ratio 0.48
```

#### Add Margin Between Sections
```bash
python3 split_uppsc_pdf_advanced.py --split-ratio 0.5 --margin 10
```

#### Custom Input/Output
```bash
python3 split_uppsc_pdf_advanced.py --input "your_file.pdf" --output-dir "custom_output"
```

### Command Line Options

- `--input, -i`: Input PDF file path (default: UPPCS_2024_Prelims_GS1_Question_Paper.pdf)
- `--output-dir, -o`: Output directory (default: split_versions)
- `--split-ratio, -r`: Split ratio from 0.0 to 1.0 (default: 0.5)
- `--margin, -m`: Margin between split sections in points (default: 0)
- `--analyze, -a`: Analyze PDF layout and suggest optimal split ratio

## Output

The scripts will create two separate PDF files:
1. **Hindi version**: Contains the left half of each page (Hindi questions)
2. **English version**: Contains the right half of each page (English questions)

## Notes

- The original PDF has 39 pages
- Each split version maintains the same page count
- File sizes are approximately 0.5 MB each
- The scripts preserve the original formatting and quality

## Troubleshooting

If you encounter issues:

1. Ensure PyMuPDF is installed correctly
2. Check that the input PDF file exists
3. Verify you have write permissions in the output directory
4. Try the `--analyze` option to get layout suggestions

## Example Output

```
Processing 39 pages...
Processed page 1/39
...
Processed page 39/39

Split completed successfully!
Hindi version saved as: split_versions/UPPCS_2024_Prelims_GS1_Question_Paper_Hindi.pdf
English version saved as: split_versions/UPPCS_2024_Prelims_GS1_Question_Paper_English.pdf

File sizes:
Hindi version: 0.50 MB
English version: 0.50 MB
``` 