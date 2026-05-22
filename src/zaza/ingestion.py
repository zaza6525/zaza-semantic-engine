"""Multi-format file ingestion."""

from pathlib import Path
from typing import Optional
import csv
import io


class IngestionError(Exception):
    """Raised when file ingestion fails."""
    pass


def _read_text(path: Path, encoding: str, fallback: str) -> str:
    """Read a text file with fallback encoding."""
    try:
        return path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        return path.read_text(encoding=fallback)


def ingest_txt(path: Path, encoding: str = "utf-8", fallback: str = "latin-1") -> str:
    """Read a .txt file."""
    return _read_text(path, encoding, fallback)


def ingest_pdf(path: Path) -> str:
    """Extract text from a PDF file using pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError:
        raise IngestionError("pypdf is required for PDF support. Install: pip install pypdf")
    
    reader = PdfReader(str(path))
    texts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            texts.append(page_text)
    return "\n\n".join(texts)


def ingest_csv(path: Path, encoding: str = "utf-8") -> str:
    """Read a CSV file and return formatted text."""
    text = _read_text(path, encoding, "latin-1")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    
    if not rows:
        return ""
    
    # Convert to readable text: header: value per row
    lines = []
    headers = list(rows[0].keys())
    for row in rows:
        parts = []
        for h in headers:
            val = row.get(h, "").strip()
            if val:
                parts.append(f"{h}: {val}")
        if parts:
            lines.append(" | ".join(parts))
    
    return "\n".join(lines)


def ingest_markdown(path: Path, encoding: str = "utf-8", fallback: str = "latin-1") -> str:
    """Read a Markdown file, stripping most markdown syntax to get clean text."""
    text = _read_text(path, encoding, fallback)
    
    # Remove code blocks
    import re
    text = re.sub(r'```[\s\S]*?```', '', text)
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links, keep text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove headers markers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)
    text = re.sub(r'_{1,2}([^_]+)_{1,2}', r'\1', text)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
    # Clean extra blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


INGESTORS = {
    ".txt": ingest_txt,
    ".md": ingest_markdown,
    ".markdown": ingest_markdown,
    ".pdf": ingest_pdf,
    ".csv": ingest_csv,
}


def get_ingestor(extension: str):
    """Get the appropriate ingestor function for a file extension."""
    ext = Path(extension).suffix.lower()
    return INGESTORS.get(ext)


def ingest_file(path: Path, encoding: str = "utf-8", fallback: str = "latin-1") -> str:
    """Ingest a file based on its extension."""
    if not path.exists():
        raise IngestionError(f"File not found: {path}")
    
    ext = path.suffix.lower()
    ingestor = get_ingestor(ext)
    
    if ingestor is None:
        raise IngestionError(f"Unsupported file type: {ext}. Supported: {list(INGESTORS.keys())}")
    
    if ext == ".txt":
        return ingest_txt(path, encoding, fallback)
    elif ext in (".md", ".markdown"):
        return ingest_markdown(path, encoding, fallback)
    elif ext == ".pdf":
        return ingest_pdf(path)
    elif ext == ".csv":
        return ingest_csv(path, encoding)
    
    raise IngestionError(f"No ingestor for extension: {ext}")
