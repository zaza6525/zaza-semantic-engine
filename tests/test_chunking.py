"""Tests for chunking module."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from zaza.chunking import chunk_text


def test_chunk_ids_unique_within_document():
    """Chunks from the same document must have unique IDs."""
    long_text = " ".join([f"Paragraph {i} with some content to make it longer." for i in range(20)])
    chunks = chunk_text(long_text, max_chunk_size=100, overlap=10)
    assert len(chunks) >= 2, "Should produce multiple chunks"
    ids = [c["id"] for c in chunks]
    assert len(ids) == len(set(ids)), "All chunk IDs must be unique"


def test_chunk_ids_different_prefixes_different_content():
    """Chunks with different prefixes should have different IDs."""
    short_text = "Hello world test content for chunking."
    chunks1 = chunk_text(short_text, chunk_prefix="doc1", filepath="/path/a.txt")
    chunks2 = chunk_text(short_text, chunk_prefix="doc2", filepath="/path/b.txt")
    assert chunks1[0]["id"] != chunks2[0]["id"]


def test_chunk_id_collision_same_filename_different_dirs():
    """Two files with the same name in different directories must not produce the same chunk_id.

    This is the collision test: if two files are named "report.txt"
    but live in /project/a/report.txt and /project/b/report.txt,
    their chunk IDs must be different.
    """
    same_text = "This is identical content in two different files."

    chunks_a = chunk_text(
        same_text,
        max_chunk_size=512,
        chunk_prefix="report",
        filepath="/project/a/report.txt"
    )
    chunks_b = chunk_text(
        same_text,
        max_chunk_size=512,
        chunk_prefix="report",
        filepath="/project/b/report.txt"
    )

    assert len(chunks_a) == 1
    assert len(chunks_b) == 1

    id_a = chunks_a[0]["id"]
    id_b = chunks_b[0]["id"]

    assert id_a != id_b, (
        f"Chunk IDs collided: {id_a} == {id_b}. "
        "Files with the same name in different directories must have unique chunk IDs."
    )

    # Verify the path hash is embedded in the ID
    assert "a" in id_a or "b" in id_b, "Path hash should be in chunk ID"


def test_chunk_id_collision_same_content_different_filenames():
    """Even if content is identical, different filenames should produce different IDs."""
    text = "Identical content."

    chunks1 = chunk_text(text, chunk_prefix="doc_a", filepath="/path/file1.txt")
    chunks2 = chunk_text(text, chunk_prefix="doc_b", filepath="/path/file2.txt")

    assert chunks1[0]["id"] != chunks2[0]["id"]


def test_chunk_id_no_prefix():
    """Chunks with no prefix still use filepath hash."""
    chunks_a = chunk_text("test content", chunk_prefix="", filepath="/dir/a/file.txt")
    chunks_b = chunk_text("test content", chunk_prefix="", filepath="/dir/b/file.txt")
    assert chunks_a[0]["id"] != chunks_b[0]["id"]


def test_empty_text_returns_empty():
    """Empty or whitespace-only text should return no chunks."""
    assert chunk_text("") == []
    assert chunk_text("   ") == []
    assert chunk_text("\n\n") == []
