import fitz


def parse_pdf(pdf_path: str) -> str:
    """Extract full text from a PDF at pdf_path and return it as a single string.

    Repeated header/footer lines that appear on every page are removed:
    - "DEPARTMENT OF CITY PLANNING"
    - "GENERALIZED SUMMARY OF ZONING REGULATIONS"
    - "Updated January 2026"
    - Lines starting with "CP-7150 (1.20.2026) Page"
    - The disclaimer line starting with "This summary is only a guide"

    The text is returned as one string; tables and headers are preserved.
    """
    doc = fitz.open(pdf_path)
    kept_lines = []

    for page in doc:
        text = page.get_text("text")
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            # Skip exact repeated headers/footers and common fragments
            if line in (
                "DEPARTMENT OF CITY PLANNING",
                "GENERALIZED SUMMARY OF ZONING REGULATIONS",
                "Updated January 2026",
                "CP-7150 (1.20.2026)",
            ):
                continue
            # Skip page number lines like 'Page 1' or 'Page 12'
            if line.startswith("Page "):
                remainder = line[5:].strip()
                if remainder.isdigit():
                    continue
            # Skip combined footer like 'CP-7150 (1.20.2026) Page 1'
            if line.startswith("CP-7150 (1.20.2026) Page"):
                continue
            # Skip disclaimer fragment anywhere on the line
            if "This summary is only a guide" in line:
                continue
            kept_lines.append(line)

    return "\n".join(kept_lines)


if __name__ == "__main__":
    pdf_path = r"data\raw\LA-zoning-regulations.pdf"
    text = parse_pdf(pdf_path)
    print(len(text))
    print(text[:500])
