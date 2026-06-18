import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from parse import parse_pdf


def chunk(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[dict]:
    """Split text into chunks and attach metadata: text, zone, topic, doc_type, source.

    Zone detection uses a regex where the first character is an uppercase letter
    followed by uppercase letters, digits or periods, and must contain at least
    one digit (e.g., A1, RD1.5).
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    pieces = splitter.split_text(text)

    pattern = re.compile(r"(?<!\d)(?<!\.)\b([A-Z]{1,2}\d{1,2}(?:\.\d+)?|[A-Z]{2})\b")
    results: list[dict] = []
    for p in pieces:
        m = pattern.search(p)
        zone = m.group(0) if m else "UNKNOWN"
        results.append({
            "text": p,
            "zone": zone,
            "topic": "zoning_regulations",
            "doc_type": "ordinance",
            "source": "LA-zoning-regulations.pdf",
        })

    return results


if __name__ == "__main__":
    pdf_path = "data/raw/LA-zoning-regulations.pdf"
    text = parse_pdf(pdf_path)
    chunks = chunk(text)
    print(f"Total chunks: {len(chunks)}")
    for i, c in enumerate(chunks[:5], 1):
        print(f"--- Chunk {i} ---")
        print(c)
