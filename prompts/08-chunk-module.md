# Task: Chunk Module

Create `src/chunk.py` with the following — no placeholders, fully implemented.

## Summary
This module is responsible for chunking text into the acceptable format with, Text, zone, topic, and source. 

## Functions

`chunk(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[dict]`:
- takes a string of text and returns a list of dictionaries with the following keys:
  - `text`: the original text
  - `zone`: the zone of the text
  - `topic`: "zoning_regulations"
  - 'doc_type' : "ordinance"
  - `source`: "LA-zoning-regulations.pdf"
- The zone is to be determined using a regex pattern: a short text of uppercase letters mixed with numbers but the first character must be a letter and may contain periods. For example A1, RD1.5. 


## Imports
Only these imports should be used:
- 'import re'
- 'from langchain_text_splitters import RecursiveCharacterTextSplitter'
- 'from parse import parse_pdf'



## Main block
When run directly from project root (`python src/chunk.py`):
1. set pdf_path = "data/raw/LA-zoning-regulations.pdf"
2. call parse_pdf() to get the text from the pdf_path
3. Call chunk() with the text 
4. print a count of the number of dictionaries returned by chunk()
5. print the 5 first dictionaries returned by chunk().

## What not to do
- Do not use any other imports than the ones specified above.
- Do not use any placeholders in the code. The code should be fully implemented and functional.
- Do not include any additional functionality beyond what is specified in the task description.
