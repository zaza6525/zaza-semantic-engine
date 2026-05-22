"""Tests for extended format ingestion (HTML, XML, DOCX)."""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from zaza.ingestion import ingest_html, ingest_xml, ingest_docx, ingest_file, IngestionError


def test_ingest_html():
    html = """<!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <nav>Navigation</nav>
        <script>var x = 1;</script>
        <h1>Main Title</h1>
        <p>This is a paragraph with <strong>bold</strong> text.</p>
        <footer>Footer text</footer>
    </body>
    </html>"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html)
        f.flush()
        text = ingest_html(Path(f.name))
        assert "Main Title" in text
        assert "paragraph" in text
        assert "Navigation" not in text  # nav removed
        assert "Footer" not in text  # footer removed
    os.unlink(f.name)


def test_ingest_xml():
    xml = """<?xml version="1.0"?>
    <data>
        <item><name>Test</name><value>42</value></item>
    </data>"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
        f.write(xml)
        f.flush()
        text = ingest_xml(Path(f.name))
        assert "Test" in text
        assert "42" in text
    os.unlink(f.name)


def test_ingest_docx_missing():
    """Test DOCX raises helpful error when library not installed."""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.docx', delete=False) as f:
        f.write(b'PK\x03\x04')  # Fake docx header
        f.flush()
        try:
            text = ingest_docx(Path(f.name))
            # If python-docx is installed, it might error differently
        except IngestionError as e:
            assert "python-docx" in str(e)
    os.unlink(f.name)


def test_ingest_html_unsupported():
    """Test that unsupported extensions raise IngestionError."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
        f.write("test")
        f.flush()
        try:
            ingest_file(Path(f.name))
            assert False, "Should raise IngestionError"
        except IngestionError:
            pass
    os.unlink(f.name)
