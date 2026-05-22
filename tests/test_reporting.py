"""Tests for reporting module."""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from zaza.reporting import Reporter


def test_format_summary():
    r = Reporter()
    summary = {
        "total_documents": 5,
        "total_words": 1234,
        "total_characters": 6789,
        "average_lexical_density": 0.45,
        "first_ingestion": "2026-01-01",
        "last_ingestion": "2026-05-21",
    }
    text = r.format_summary_text(summary)
    assert "ZAZA" in text
    assert "5" in text
    assert "1,234" in text


def test_format_documents():
    r = Reporter()
    docs = [
        {"filename": "test.txt", "filetype": ".txt", "word_count": 100,
         "unique_words": 50, "lexical_density": 0.5, "ingested_at": "2026-01-01"},
    ]
    text = r.format_documents_text(docs)
    assert "test.txt" in text
    assert "100" in text


def test_save_json(tmp_path):
    r = Reporter(str(tmp_path))
    report = {"test": "data", "count": 42}
    path = r.save_json(report, "test.json")
    
    assert path.exists()
    content = json.loads(path.read_text())
    assert content["test"] == "data"


def test_save_csv(tmp_path):
    r = Reporter(str(tmp_path))
    docs = [
        {"filename": "a.txt", "word_count": 10, "filetype": ".txt"},
        {"filename": "b.txt", "word_count": 20, "filetype": ".txt"},
    ]
    path = r.save_csv(docs, "test.csv")
    
    assert path.exists()
    content = path.read_text()
    assert "filename" in content
    assert "a.txt" in content


def test_save_csv_empty(tmp_path):
    r = Reporter(str(tmp_path))
    path = r.save_csv([], "empty.csv")
    assert path.exists()
