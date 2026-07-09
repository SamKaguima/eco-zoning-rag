import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from parse import parse_pdf, extract_zone_token


def chunk(
    blocks: list[dict],
    source: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[dict]:
    """Convert content blocks from parse_pdf into chunks with metadata:
    text, zone, topic, doc_type, source.

    Text blocks are split with RecursiveCharacterTextSplitter; zone detection
    falls back to a regex (first uppercase-letter token containing a digit,
    e.g. A1, RD1.5). Table blocks become one chunk per row, rendered as
    'Zone: R1 | Use: ... | Maximum Height - Feet: 45 | ...'; the zone comes
    from column 0, or column 1 when column 0 is empty — never from regex.
    """
    if not isinstance(blocks, list):
        raise TypeError("blocks must be a list of content blocks")

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    pattern = re.compile(r"(?<!\d)(?<!\.)\b([A-Z]{1,2}\d{1,2}(?:\.\d+)?|[A-Z]{2})\b")

    results: list[dict] = []
    for block in blocks:
        if block["type"] == "text":
            for piece in splitter.split_text(block["content"]):
                m = pattern.search(piece)
                zone = m.group(0) if m else "UNKNOWN"
                results.append(_make_chunk(piece, zone, source))
        elif block["type"] == "table":
            header = block["header"]
            for row in block["rows"]:
                zone = (
                    extract_zone_token(row[0])
                    or (extract_zone_token(row[1]) if len(row) > 1 else None)
                    or "UNKNOWN"
                )
                fields = [f"Zone: {zone}"]
                for name, value in zip(header, row):
                    if not value or value == zone:
                        continue
                    fields.append(f"{name}: {value}")
                results.append(_make_chunk(" | ".join(fields), zone, source))

    return results


def _make_chunk(text: str, zone: str, source: str) -> dict:
    return {
        "text": text,
        "zone": zone,
        "topic": "zoning_regulations",
        "doc_type": "ordinance",
        "source": source,
    }


if __name__ == "__main__":
    pdf_path = "data/raw/LA-zoning-regulations.pdf"
    blocks = parse_pdf(pdf_path)
    chunks = chunk(blocks, source="LA-zoning-regulations.pdf")
    print(f"Total chunks: {len(chunks)}")
    table_chunks = [c for c in chunks if c["text"].startswith("Zone: ")]
    unknown = [c for c in chunks if c["zone"] == "UNKNOWN"]
    print(f"Table chunks: {len(table_chunks)}, text chunks: {len(chunks) - len(table_chunks)}")
    print(f"UNKNOWN zones: {len(unknown)} (all from text blocks: {all(not c['text'].startswith('Zone: ') for c in unknown)})")
    print(f"Zones: {sorted({c['zone'] for c in table_chunks})}")
    print("\n--- Sample table chunk ---")
    print(table_chunks[0]["text"])
    print("\n--- Sample text chunk ---")
    print(chunks[0])
