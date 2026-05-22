"""Tests for ingestion module."""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from zaza.ingestion import ingest_txt, ingest_csv, ingest_markdown, ingest_file, IngestionError


def test_ingest_txt():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("Hello world test file")
        f.flush()
        text = ingest_txt(Path(f.name))
        assert "Hello world test file" in text
    os.unlink(f.name)


def test_ingest_csv():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write("name,age,city\nAlice,30,Paris\nBob,25,Lyon\n")
        f.flush()
        text = ingest_csv(Path(f.name))
        assert "Alice" in text
        assert "Paris" in text
    os.unlink(f.name)


def test_ingest_markdown():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write("# Title\n\nThis is **bold** and *italic* text.\n\n[Link](http://example.com)\n")
        f.flush()
        text = ingest_markdown(Path(f.name))
        assert "Title" in text
        assert "bold" in text
        assert "italic" in text
        assert "http" not in text  # Link URL should be stripped
    os.unlink(f.name)


def test_ingest_unsupported():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
        f.write("test")
        f.flush()
        try:
            ingest_file(Path(f.name))
            assert False, "Should raise IngestionError"
        except IngestionError:
            pass
    os.unlink(f.name)


def test_ingest_nonexistent():
    try:
        ingest_file(Path("/nonexistent/file.txt"))
        assert False, "Should raise IngestionError"
    except IngestionError:
        pass


def test_ingest_txt_empty():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("")
        f.flush()
        text = ingest_txt(Path(f.name))
        assert text == ""
    os.unlink(f.name)
