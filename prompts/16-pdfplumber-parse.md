# Refactor: Table-aware PDF parsing with pdfplumber

## Goal
Replace PyMuPDF in `src/parse.py` with pdfplumber to extract table structure 
from `data/raw/LA-zoning-regulations.pdf`. Update `src/chunk.py` to handle 
the new output format, and update the two callsites in `src/main.py` and 
`src/app.py`. The rest of the pipeline (ingest, retrieve, generate) must 
remain unchanged — the chunk dict schema they consume does not change.

## Current behavior
`parse.py` returns a single flat string. Tables are extracted as space-separated 
text losing column relationships. Zone regex in `chunk.py` misidentifies zones 
because section references like "A.16" look like zone codes.

## What pdfplumber actually returns on this PDF (verified by probe — design for it)
- `page.extract_text()` STILL includes the repeated page headers 
  ("DEPARTMENT OF CITY PLANNING", "GENERALIZED SUMMARY OF ZONING REGULATIONS", 
  "Updated January 2026") and the disclaimer as prose on every page.
- `page.extract_text()` also includes all text INSIDE tables — extracting both 
  text and tables naively double-counts every table.
- Tables have a 2-row spanning header with `None` for merged cells, e.g. 
  `['Use', 'Maximum Height', None, 'Required Yards', ...]` over 
  `[None, 'Stories', 'Feet', 'Front', ...]`. pdfplumber often re-detects the 
  header band as a SEPARATE 2-row table whose column count (8) differs from 
  the body table's (12).
- Column 0 is NOT always the zone code: the RD1.5 row has an empty column 0 
  with the zone in column 1; the R1 cell is multiline 
  (`"R1\n(including\nR1V, R1F,\n..."`); continuation rows like A2 have `None` 
  merged cells that inherit from the row above; category banner rows like 
  `['', 'Agricultural', None, ...]` have no zone at all.
- Spurious fragment tables appear (e.g. a 4×1 table containing just 
  `['R1'], ['(including'], ...`) — a cell re-detected as its own table.
- Smart quotes/apostrophes come through as mojibake (`�`).

## Target behavior

### `parse.py`
`parse_pdf(pdf_path: str) -> list[dict]` returns a list of content blocks:
- `{"type": "text", "content": str}` for prose paragraphs
- `{"type": "table", "header": list[str], "rows": list[list[str]]}` for tables

Implementation requirements:
1. Use `page.find_tables()` so each table comes with its bounding box.
2. Discard junk tables: any table whose bbox is contained within another 
   table's bbox on the same page, or that has fewer than 2 columns.
3. Extract prose ONLY from outside the kept table bboxes (filter the page's 
   chars by bbox, then `extract_text()`), so table content is never duplicated 
   into text blocks. Split prose into blocks on blank lines.
4. Remove repeated boilerplate with a document-agnostic two-pass rule: collect 
   line frequency across all pages first, then drop any line that appears 
   verbatim on ≥ 50% of pages. No hardcoded string blocklists.
5. Merge the 2-row header into one `header: list[str]`: forward-fill `None` 
   cells horizontally across the top header row, then join the two rows 
   vertically per column (e.g. "Maximum Height - Stories", 
   "Maximum Height - Feet"). If the header band was detected as a separate 
   table, match it to the body table on the same page and reconcile the 
   column-count mismatch by aligning on x-coordinates (or pad/truncate to the 
   body's column count).
6. Clean rows: forward-fill `None`/empty cells from the previous row 
   (continuation rows like A2 inherit the values above them); replace newlines 
   inside cells with spaces; normalize unicode punctuation (smart quotes, 
   dashes) to ASCII.
7. Skip rows that are banner/category rows (no zone-shaped token in either of 
   the first two columns, e.g. "Agricultural", "Commercial") and skip header 
   rows — they must not be emitted as data rows.
8. Drop any block whose total content is under 10 characters.

### `chunk.py`
`chunk(blocks: list[dict], source: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[dict]`
- Text blocks: split with RecursiveCharacterTextSplitter as before; zone via 
  the existing regex as fallback.
- Table blocks: convert each row to one chunk using the table's merged header:
  "Zone: R1 | Use: One-Family Residential | Maximum Height - Feet: 45 | ..."
  One row = one chunk, never split.
- Zone extraction for table chunks: take the first zone-shaped token from 
  column 0; if column 0 is empty, fall back to column 1 (the RD1.5 case). 
  Normalize the cell first: strip parentheticals and newlines, so 
  "R1 (including R1V, R1F, ...)" → "R1".
- `source` is a parameter — no hardcoded "LA-zoning-regulations.pdf" string. 
  parse.py and chunk.py must work on ANY zoning PDF without 
  document-specific hardcoding.
- Final output remains list[dict] with the same schema: 
  text, zone, topic, doc_type, source.

### Callsites
- `src/main.py` and `src/app.py` both do `text = parse_pdf(...)` then 
  `chunks = chunk(text)` — update both to the new block-based flow and pass 
  the source filename. No other downstream module changes.

## Constraints
- pdfplumber is already installed (0.11.10, in requirements.txt)
- Do not change any module signatures downstream of chunk.py 
  (ingest, retrieve, hybrid_retrieve, generate)
- Keep the __main__ blocks in both modules working
- Run `python src/parse.py` and `python src/chunk.py` after changes and verify output
- Run `pytest tests/ -v` and keep it green

## Definition of done
- `python src/chunk.py` produces chunks where table rows have correct zone tags 
  (R1 chunks tagged R1, not A.16 or C.10)
- The RD1.5 row is tagged RD1.5 (column-1 fallback works)
- The A2 continuation row carries forward inherited values from the A1 row 
  (its chunk text is not mostly empty fields)
- No chunks produced from banner/category rows or header rows
- No table content appears duplicated inside text chunks
- Character count of extracted content (sum over all blocks) is similar to or 
  higher than the current 29,835
- No chunk has zone = "UNKNOWN" for a row that clearly starts with a zone code
