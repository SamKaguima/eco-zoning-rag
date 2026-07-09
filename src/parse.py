import re
from collections import Counter

import pdfplumber

# Unicode punctuation normalized to ASCII equivalents
_PUNCT_MAP = {
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "–": "-",
    "—": "-",
    " ": " ",
    "�": "'",
}

# Zone codes: letters + digits (R1, RE40, RD1.5, MR1) or 1-2 bare letters (RS, CM, P, OS)
_ZONE_TOKEN_RE = re.compile(r"^(?:[A-Z]{1,3}\d{1,2}(?:\.\d+)?|[A-Z]{1,2})$")

# A block (text or table content) shorter than this is discarded as noise
_MIN_BLOCK_CHARS = 10

# Header cells are short labels; a longer filled cell marks a content row
_MAX_HEADER_CELL_CHARS = 30

# A prose line appearing verbatim on at least this fraction of pages is boilerplate
_BOILERPLATE_PAGE_FRACTION = 0.5


def normalize_text(text: str) -> str:
    """Replace unicode punctuation (smart quotes, dashes, nbsp) with ASCII."""
    for bad, good in _PUNCT_MAP.items():
        text = text.replace(bad, good)
    return text


def clean_cell(cell: str | None) -> str:
    """Normalize a table cell: None -> '', collapse internal whitespace/newlines."""
    if cell is None:
        return ""
    return normalize_text(" ".join(cell.split()))


def extract_zone_token(cell: str | None) -> str | None:
    """Return the zone code from a table cell, or None if the cell has none.

    Uses only the first line before any parenthetical, so
    'R1\\n(including R1V, R1F, ...)' -> 'R1' and 'RD1.5' -> 'RD1.5'.
    """
    if not cell:
        return None
    lines = normalize_text(cell).strip().splitlines()
    if not lines:
        return None
    first_line = lines[0].split("(")[0].strip()
    if not first_line:
        return None
    token = first_line.split()[0].rstrip(",;:")
    return token if _ZONE_TOKEN_RE.match(token) else None


def _table_ncols(table: "pdfplumber.table.Table") -> int:
    return max(len(row.cells) for row in table.rows) if table.rows else 0


def _is_nested(table: "pdfplumber.table.Table", tables: list) -> bool:
    """True if table's bbox sits inside another table's bbox (spurious re-detection)."""
    x0, top, x1, bottom = table.bbox
    for other in tables:
        if other is table:
            continue
        ox0, otop, ox1, obottom = other.bbox
        if x0 >= ox0 - 1 and top >= otop - 1 and x1 <= ox1 + 1 and bottom <= obottom + 1:
            return True
    return False


def _column_centers(table: "pdfplumber.table.Table") -> list[float]:
    """X-center per column, taken from the narrowest cell seen in each column.

    Spanning cells (banners, merged headers) are wide, so the narrowest cell
    is the best estimate of the true column position.
    """
    ncols = _table_ncols(table)
    best: list[tuple[float, float] | None] = [None] * ncols
    for row in table.rows:
        for j, cell_bbox in enumerate(row.cells):
            if cell_bbox is None:
                continue
            x0, _, x1, _ = cell_bbox
            width = x1 - x0
            if best[j] is None or width < best[j][0]:
                best[j] = (width, (x0 + x1) / 2)
    return [b[1] if b is not None else -1.0 for b in best]


def _merge_header(header_rows: list[tuple[list, list]], centers: list[float]) -> list[str]:
    """Build one label per body column from stacked header rows.

    Each header cell labels every body column whose x-center falls inside the
    cell's bbox, so a spanning 'Maximum Height' cell covers both the Stories
    and Feet columns; stacked labels join as 'Maximum Height - Stories'.
    """
    labels: list[list[str]] = [[] for _ in centers]
    for cell_bboxes, cell_texts in header_rows:
        for cell_bbox, text in zip(cell_bboxes, cell_texts):
            text = clean_cell(text)
            if cell_bbox is None or not text:
                continue
            x0, _, x1, _ = cell_bbox
            for j, center in enumerate(centers):
                if x0 <= center <= x1:
                    labels[j].append(text)
    header: list[str] = []
    for j, parts in enumerate(labels):
        deduped: list[str] = []
        for part in parts:
            if part not in deduped:
                deduped.append(part)
        header.append(" - ".join(deduped) if deduped else f"Column {j + 1}")
    return header


def _floating_header_cells(
    page: "pdfplumber.page.Page", band: tuple[float, float], table_bboxes: list[tuple]
) -> list[tuple[list, list]]:
    """Header labels rendered outside any table cell (e.g. 'Zone', 'Parking').

    Words vertically inside the header band but outside every table bbox are
    treated as one-cell header rows, padded horizontally so they cover the
    column they sit over.
    """
    band_top, band_bottom = band
    pad = 10
    cells: list[tuple[list, list]] = []
    for word in sorted(page.extract_words(), key=lambda w: (w["top"], w["x0"])):
        y = (word["top"] + word["bottom"]) / 2
        if not band_top <= y <= band_bottom:
            continue
        x = (word["x0"] + word["x1"]) / 2
        if any(
            bx0 <= x <= bx1 and btop <= y <= bbottom
            for bx0, btop, bx1, bbottom in table_bboxes
        ):
            continue
        bbox = (word["x0"] - pad, word["top"], word["x1"] + pad, word["bottom"])
        cells.append(([bbox], [word["text"]]))
    return cells


def _extract_page_tables(
    page: "pdfplumber.page.Page", header_carry: list[tuple[list, list]]
) -> tuple[list[dict], list[tuple], list[tuple[list, list]], tuple[float, float] | None]:
    """Extract table blocks from one page.

    Returns (table_blocks, kept_table_bboxes, header_rows, header_band) where
    header_rows is this page's header band (or the carried-over one) for reuse
    on continuation pages, and header_band is the y-range of this page's own
    header rows (None if the page has none).
    """
    tables = page.find_tables()
    kept = [t for t in tables if _table_ncols(t) >= 2 and not _is_nested(t, tables)]
    kept.sort(key=lambda t: t.bbox[1])
    bboxes = [t.bbox for t in kept]

    # First pass: classify each table's rows. Zone-led rows are data rows.
    # Non-data rows above the first data row with >= 3 filled short cells are
    # header rows; single-short-cell rows are banners ('Agricultural') and are
    # skipped; everything else is real content in a grid this parser can't
    # structure (e.g. height-district tables) and is flattened to a text block.
    page_header_rows: list[tuple[list, list]] = []
    bodies: list[tuple] = []
    blocks: list[dict] = []
    for table in kept:
        data = table.extract()
        data_row_indexes = [
            i
            for i, row in enumerate(data)
            if extract_zone_token(row[0] if len(row) > 0 else None)
            or extract_zone_token(row[1] if len(row) > 1 else None)
        ]
        first_data = data_row_indexes[0] if data_row_indexes else len(data)
        flattened: list[str] = []
        for i, texts in enumerate(data):
            if i in data_row_indexes:
                continue
            filled = [c for c in (clean_cell(t) for t in texts) if c]
            if not filled:
                continue
            is_short = all(len(c) <= _MAX_HEADER_CELL_CHARS for c in filled)
            if i < first_data and len(filled) >= 3 and is_short:
                page_header_rows.append((list(table.rows[i].cells), list(texts)))
            elif len(filled) == 1 and is_short:
                continue
            else:
                flattened.append(" | ".join(filled))
        content = "\n".join(flattened)
        if len(content) >= _MIN_BLOCK_CHARS:
            blocks.append({"type": "text", "content": content})
        if data_row_indexes:
            bodies.append((table, data, data_row_indexes))

    # Header labels like 'Zone' and 'Parking Required' float outside the
    # detected header cells — pick them up from the header band's y-range
    band: tuple[float, float] | None = None
    if page_header_rows:
        cell_bboxes = [b for cells, _ in page_header_rows for b in cells if b is not None]
        band = (min(b[1] for b in cell_bboxes), max(b[3] for b in cell_bboxes))
        page_header_rows.extend(_floating_header_cells(page, band, bboxes))

    header_source = page_header_rows if page_header_rows else header_carry

    # Second pass: emit body tables with headers aligned by x-coordinate
    for table, data, data_row_indexes in bodies:
        header = _merge_header(header_source, _column_centers(table))
        rows_out: list[list[str]] = []
        previous: list[str] | None = None
        for i in data_row_indexes:
            cleaned = [clean_cell(c) for c in data[i]]
            # Continuation rows inherit from the row above, but never in the
            # zone columns (0-1) — an empty zone cell must stay empty so the
            # column-1 fallback works instead of inheriting the wrong zone
            if previous is not None:
                for j in range(2, len(cleaned)):
                    if not cleaned[j] and j < len(previous):
                        cleaned[j] = previous[j]
            previous = cleaned
            rows_out.append(cleaned)

        if sum(len(c) for row in rows_out for c in row) < _MIN_BLOCK_CHARS:
            continue
        blocks.append({"type": "table", "header": header, "rows": rows_out})

    return blocks, bboxes, header_source, band


def _page_prose_lines(
    page: "pdfplumber.page.Page",
    table_bboxes: list[tuple],
    header_band: tuple[float, float] | None,
) -> list[str]:
    """Extract prose lines from the parts of the page outside all table bboxes.

    The header band's y-range is excluded across the full page width — its
    floating labels ('Zone', 'Parking') are captured as header cells, not prose.
    """
    if table_bboxes or header_band:

        def outside_tables(obj: dict) -> bool:
            x = (obj["x0"] + obj["x1"]) / 2
            y = (obj["top"] + obj["bottom"]) / 2
            if header_band and header_band[0] <= y <= header_band[1]:
                return False
            return not any(
                bx0 <= x <= bx1 and btop <= y <= bbottom
                for bx0, btop, bx1, bbottom in table_bboxes
            )

        page = page.filter(outside_tables)
    text = page.extract_text() or ""
    return [normalize_text(" ".join(line.split())) for line in text.splitlines()]


def parse_pdf(pdf_path: str) -> list[dict]:
    """Parse a zoning PDF into a list of content blocks.

    Each block is either:
    - {"type": "text", "content": str} for a prose paragraph
    - {"type": "table", "header": list[str], "rows": list[list[str]]} for a table

    Prose is taken only from outside table bounding boxes (no duplication),
    and lines repeated verbatim on >= 50% of pages (headers, footers,
    disclaimers) are dropped — no document-specific string matching.
    """
    pages_prose: list[list[str]] = []
    pages_tables: list[list[dict]] = []

    with pdfplumber.open(pdf_path) as pdf:
        n_pages = len(pdf.pages)
        header_carry: list[tuple[list, list]] = []
        for page in pdf.pages:
            table_blocks, table_bboxes, header_carry, band = _extract_page_tables(
                page, header_carry
            )
            pages_tables.append(table_blocks)
            pages_prose.append(_page_prose_lines(page, table_bboxes, band))

    # Boilerplate detection masks digits so page-numbered footers like
    # 'CP-7150 (1.20.2026) Page 3' count as the same line on every page
    def repetition_key(line: str) -> str:
        return re.sub(r"\d+", "#", line)

    line_page_counts: Counter = Counter()
    for lines in pages_prose:
        for key in {repetition_key(line) for line in lines if line}:
            line_page_counts[key] += 1
    threshold = max(2, int(n_pages * _BOILERPLATE_PAGE_FRACTION))
    boilerplate = {key for key, count in line_page_counts.items() if count >= threshold}

    blocks: list[dict] = []
    for lines, table_blocks in zip(pages_prose, pages_tables):
        paragraph: list[str] = []
        for line in lines + [""]:
            if line and repetition_key(line) not in boilerplate:
                paragraph.append(line)
            elif not line and paragraph:
                content = "\n".join(paragraph)
                if len(content) >= _MIN_BLOCK_CHARS:
                    blocks.append({"type": "text", "content": content})
                paragraph = []
        blocks.extend(table_blocks)

    return blocks


if __name__ == "__main__":
    pdf_path = "data/raw/LA-zoning-regulations.pdf"
    blocks = parse_pdf(pdf_path)
    text_blocks = [b for b in blocks if b["type"] == "text"]
    table_blocks = [b for b in blocks if b["type"] == "table"]
    text_chars = sum(len(b["content"]) for b in text_blocks)
    table_chars = sum(len(c) for b in table_blocks for row in b["rows"] for c in row)
    total_rows = sum(len(b["rows"]) for b in table_blocks)
    print(f"Blocks: {len(blocks)} ({len(text_blocks)} text, {len(table_blocks)} table)")
    print(f"Table rows: {total_rows}")
    print(f"Characters: {text_chars + table_chars} (text: {text_chars}, table: {table_chars})")
    print("\n--- First text block ---")
    print(text_blocks[0]["content"][:400])
    print("\n--- First table block ---")
    print("header:", table_blocks[0]["header"])
    for row in table_blocks[0]["rows"][:2]:
        print("row:", row)
