"""Multi-format file ingestion."""

from pathlib import Path
from typing import Optional, List, Dict
import csv
import io
import json
import re

from zaza.chunking import chunk_text


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


def ingest_html(path: Path, encoding: str = "utf-8", fallback: str = "latin-1") -> str:
    """Extract text from an HTML file using BeautifulSoup."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise IngestionError("beautifulsoup4 is required for HTML support. Install: pip install beautifulsoup4")
    
    text = _read_text(path, encoding, fallback)
    soup = BeautifulSoup(text, 'html.parser')
    
    # Remove script and style elements
    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        tag.decompose()
    
    # Get text, normalize whitespace
    text = soup.get_text(separator='\n')
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def ingest_xml(path: Path, encoding: str = "utf-8", fallback: str = "latin-1") -> str:
    """Extract text from an XML file using standard library xml.etree."""
    import xml.etree.ElementTree as ET
    
    text = _read_text(path, encoding, fallback)
    root = ET.fromstring(text)
    
    lines = []
    for elem in root.iter():
        if elem.text and elem.text.strip():
            lines.append(elem.text.strip())
    return "\n".join(lines)


def ingest_docx(path: Path) -> str:
    """Extract text from a DOCX (Word) file."""
    try:
        from docx import Document
    except ImportError:
        raise IngestionError("python-docx is required for DOCX support. Install: pip install python-docx")
    
    try:
        doc = Document(str(path))
    except Exception as e:
        raise IngestionError(f"Invalid DOCX file: {e}")
    
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def ingest_json(path: Path, encoding: str = "utf-8", fallback: str = "latin-1") -> str:
    """Read a JSON file and convert to readable text."""
    text = _read_text(path, encoding, fallback)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise IngestionError(f"Invalid JSON: {e}")
    # Convert structured JSON to readable flat text
    lines = _json_to_text(data, indent=0)
    return "\n".join(lines)


def _json_to_text(obj, indent: int = 0) -> list:
    """Recursively convert JSON to flat text lines."""
    lines = []
    prefix = "  " * indent
    if isinstance(obj, dict):
        for key, val in obj.items():
            if isinstance(val, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.extend(_json_to_text(val, indent + 1))
            elif val is None:
                lines.append(f"{prefix}{key}: null")
            else:
                lines.append(f"{prefix}{key}: {val}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.extend(_json_to_text(item, indent + 1))
            else:
                lines.append(f"{prefix}- {item}")
    else:
        lines.append(f"{prefix}{obj}")
    return lines


def ingest_yaml(path: Path, encoding: str = "utf-8", fallback: str = "latin-1") -> str:
    """Read a YAML file and convert to readable text."""
    text = _read_text(path, encoding, fallback)
    try:
        import yaml as pyyaml
    except ImportError:
        raise IngestionError("PyYAML is required for YAML support (already installed).")
    try:
        data = pyyaml.safe_load(text)
    except pyyaml.YAMLError as e:
        raise IngestionError(f"Invalid YAML: {e}")
    if data is None:
        return ""
    lines = _yaml_to_text(data, indent=0)
    return "\n".join(lines)


def _yaml_to_text(obj, indent: int = 0) -> list:
    """Recursively convert YAML data to flat text lines."""
    return _json_to_text(obj, indent)


def ingest_epub(path: Path) -> str:
    """Extract text from an EPUB file using ebooklib."""
    try:
        from ebooklib import epub
    except ImportError:
        raise IngestionError("ebooklib is required for EPUB support. Install: pip install ebooklib")
    
    try:
        book = epub.read_epub(str(path), options={"ignore_ncx": True})
    except Exception as e:
        raise IngestionError(f"Failed to read EPUB: {e}")
    
    texts = []
    for item in book.get_items_of_type(epub.ITEM_DOCUMENT):
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(item.get_content(), "html.parser")
            # Remove script/style/nav
            for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
                tag.decompose()
            text = soup.get_text(separator="\n")
            if text.strip():
                texts.append(text.strip())
        except Exception:
            continue
    
    if not texts:
        return ""
    return "\n\n".join(texts)


INGESTORS = {
    ".txt": ingest_txt,
    ".md": ingest_markdown,
    ".markdown": ingest_markdown,
    ".pdf": ingest_pdf,
    ".csv": ingest_csv,
    ".html": ingest_html,
    ".htm": ingest_html,
    ".xml": ingest_xml,
    ".docx": ingest_docx,
    ".json": ingest_json,
    ".yaml": ingest_yaml,
    ".yml": ingest_yaml,
    ".epub": ingest_epub,
}


def get_ingestor(extension: str):
    """Get the appropriate ingestor function for a file extension."""
    ext = Path(extension).suffix.lower()
    if not ext:
        # extension was already like ".txt" — Path() stripped it
        ext = extension.lower()
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
    elif ext in (".html", ".htm"):
        return ingest_html(path, encoding, fallback)
    elif ext == ".xml":
        return ingest_xml(path, encoding, fallback)
    elif ext == ".docx":
        return ingest_docx(path)
    elif ext in (".json",):
        return ingest_json(path, encoding, fallback)
    elif ext in (".yaml", ".yml"):
        return ingest_yaml(path, encoding, fallback)
    elif ext == ".epub":
        return ingest_epub(path)
    
    raise IngestionError(f"No ingestor for extension: {ext}")


def chunk_and_embed(
    path: Path,
    embed_store,
    encoding: str = "utf-8",
    fallback: str = "latin-1",
    max_chunk_size: int = 512,
    overlap: int = 64,
) -> Dict:
    """Ingest a file, chunk it, and embed each chunk in the store.

    Each chunk gets metadata: filepath, filename, filetype, file_size,
    ingested_at, chunk_id, chunk_index, total_chunks.

    Returns a dict with: filename, chunk_count, total_words, status, error (if any).
    """
    try:
        text = ingest_file(path, encoding, fallback)
    except IngestionError as e:
        return {"filename": path.name, "chunk_count": 0, "status": f"error: {e}"}
    except Exception as e:
        return {"filename": path.name, "chunk_count": 0, "status": f"error: {e}"}

    if not text or not text.strip():
        return {"filename": path.name, "chunk_count": 0, "status": "empty"}

    # Chunk the text
    chunks = chunk_text(text, max_chunk_size=max_chunk_size, overlap=overlap,
                        chunk_prefix=path.name[:30].replace(" ", "_").replace(".", "_"),
                        filepath=str(path))

    if not chunks:
        return {"filename": path.name, "chunk_count": 0, "status": "success", "total_words": 0}

    # Store each chunk with metadata
    ingested_at = _now_iso()
    file_size = path.stat().st_size
    total_words = sum(len(c["text"].split()) for c in chunks)

    added = 0
    for chunk in chunks:
        chunk_id = chunk["id"]
        try:
            embed_store.add_document(
                doc_id=chunk_id,
                text=chunk["text"],
                metadata={
                    "filepath": str(path),
                    "filename": path.name,
                    "filetype": path.suffix.lower(),
                    "file_size": file_size,
                    "ingested_at": ingested_at,
                    "chunk_index": chunk["chunk_index"],
                    "total_chunks": chunk["total_chunks"],
                    "_full_text": text[:8192],  # Full text for reference
                },
            )
            added += 1
        except Exception as e:
            print(f"    ⚠️  Embedding error for {path.name} chunk {chunk['chunk_index']}: {e}")

    return {
        "filename": path.name,
        "chunk_count": added,
        "total_words": total_words,
        "status": "success",
    }


def _now_iso():
    from datetime import datetime
    return datetime.now().isoformat()
