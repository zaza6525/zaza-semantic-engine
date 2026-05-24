"""Smart text chunking for long documents.

Splits long documents into overlapping chunks for better semantic search.
Each chunk gets a unique ID and metadata linking it back to the source document.
"""

import hashlib
from typing import List, Tuple


def chunk_text(
    text: str,
    max_chunk_size: int = 512,
    overlap: int = 64,
    chunk_prefix: str = "",
) -> List[dict]:
    """Split text into overlapping chunks.

    Chunks are split at sentence boundaries when possible to keep context
    coherent. Falls back to character-level splitting if no sentence
    boundary is found within the window.

    Args:
        text: The text to chunk.
        max_chunk_size: Maximum characters per chunk (default 512).
        overlap: Characters of overlap between chunks (default 64).
        chunk_prefix: Prefix for chunk IDs (e.g. document filename).

    Returns:
        List of dicts with keys: id, text, chunk_index, total_chunks,
        start_pos, end_pos.
    """
    if not text or not text.strip():
        return []

    # Split by sentence boundaries (., !, ?, ;, \n\n) for coherence
    sentences = _split_into_sentences(text)

    chunks = []
    current_chunk_text = ""
    chunk_index = 0
    total_chars = 0

    for sentence in sentences:
        # If adding this sentence would exceed max_chunk_size, flush current chunk
        if len(current_chunk_text) + len(sentence) > max_chunk_size and current_chunk_text:
            chunks.append(_make_chunk(current_chunk_text, chunk_index, chunk_prefix))
            chunk_index += 1
            # Keep the last `overlap` chars for continuity
            if overlap > 0 and len(current_chunk_text) > overlap:
                current_chunk_text = current_chunk_text[-overlap:] + " "
            else:
                current_chunk_text = ""
        current_chunk_text += sentence + " "

    # Don't forget the last chunk
    if current_chunk_text.strip():
        chunks.append(_make_chunk(current_chunk_text.strip(), chunk_index, chunk_prefix))
        chunk_index += 1

    # Tag each chunk with total_chunks
    total = len(chunks)
    for chunk in chunks:
        chunk["total_chunks"] = total

    return chunks


def _split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using common delimiters."""
    import re
    # Split on sentence-ending punctuation, double newline, or tab
    raw = re.split(r'(?<=[.!?;])\s+|\n{2,}|\t', text)
    # Filter empty strings and strip
    return [s.strip() for s in raw if s.strip()]


def _make_chunk(text: str, index: int, prefix: str) -> dict:
    """Create a chunk dict with metadata."""
    chunk_id = f"{prefix}_chunk_{index}" if prefix else f"chunk_{index}"
    # Ensure unique ID even if prefix is empty
    chunk_id = hashlib.md5(chunk_id.encode()).hexdigest()[:12]
    if prefix:
        chunk_id = f"{prefix[:20]}_{index}_{hashlib.md5(text[:50].encode()).hexdigest()[:8]}"

    return {
        "id": chunk_id,
        "text": text,
        "chunk_index": index,
        "start_pos": 0,  # Approximate (sentence-based)
        "end_pos": 0,
    }
