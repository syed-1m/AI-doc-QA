from pypdf import PdfReader
from docx import Document as DocxDocument


def extract_text_from_pdf(file_path: str) -> list[tuple[str, int]]:
    """Returns a list of (text, page_number) tuples, one per page."""
    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append((text, i))
    return pages


def extract_text_from_docx(file_path: str) -> list[tuple[str, int]]:
    """DOCX has no native page concept, so we return everything as one 'page'."""
    doc = DocxDocument(file_path)
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [(text, 1)] if text.strip() else []


def extract_text_from_txt(file_path: str) -> list[tuple[str, int]]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return [(text, 1)] if text.strip() else []


def extract_text(file_path: str, mime_type: str) -> list[tuple[str, int]]:
    if mime_type == "application/pdf":
        return extract_text_from_pdf(file_path)
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file_path)
    elif mime_type == "text/plain":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported mime type for extraction: {mime_type}")


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 80) -> list[str]:
    """
    Splits text into overlapping chunks by approximate word count.
    chunk_size and overlap are measured in words, not tokens, for simplicity.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end >= len(words):
            break
        start = end - overlap
    return chunks