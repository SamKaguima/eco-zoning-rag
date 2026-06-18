# Task: Parse PDF Module

Create `src/parse.py` with the following — no placeholders, fully implemented.

## Summary
This module takes in a pdf file and extracts text from it, returning the text as a string

## Functions

`parse_pdf(pdf_path: str) -> str`
- Takes in a path to a pdf file 
- Uses pymupdf to extract text from the pdf file
- returns a string of the remaining important data
- Strip the following repeated text that appears on every page:
    - "DEPARTMENT OF CITY PLANNING"
    - "GENERALIZED SUMMARY OF ZONING REGULATIONS"
    - "Updated January 2026"
    - "CP-7150 (1.20.2026) Page [number]"
    - The disclaimer line starting with "This summary is only a guide..."


## Imports
Only these imports should be used:
- 'import fitz'

## Main block
When run directly from project root (`python src/parse.py`):
1. set pdf_path = "data\raw\LA-zoning-regulations.pdf"
2. Call  parse_pdf() with that path 
3. print the total character count of the extracted text 
4. print the first 500 characters of the extracted text

## What not to do
- Do not split or chunk the text in any way — return it as one single string
- Do not use any library other than fitz (pymupdf)
- Do not use OCR — the PDF is digital text, not scanned
- Do not add any metadata, labels, or zone tags to the text — that is chunk.py's job
- Do not remove table content — tables contain the zone regulations and must be kept
- Do not remove section headers like "Table 1a" or zone names like "R1", "A1" — these are content not noise
- Do not normalize or reformat whitespace beyond basic stripping
- Do not return a list, dict, or any other type — return type is str only
- Do not open or read any file other than the pdf_path argument passed in
- Do not print anything inside the function itself — printing only happens in the main block
- Do not hardcode any file paths inside the function