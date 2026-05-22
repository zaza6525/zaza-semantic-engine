"""Tests for database module."""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from zaza.database import Database


def test_db_create_and_add():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        
        doc_id = db.add_document(
            filepath="/tmp/test.txt",
            filename="test.txt",
            filetype=".txt",
            file_size=1234
        )
        assert doc_id is not None
        
        db.add_analysis(doc_id, {
            "word_count": 100,
            "char_count": 500,
            "sentence_count": 5,
            "unique_words": 50,
            "lexical_density": 0.5,
            "avg_word_length": 4.5,
            "top_words": [{"word": "test", "count": 10}],
        })
        
        summary = db.get_summary()
        assert summary["total_documents"] == 1
        assert summary["total_words"] == 100
        
        docs = db.get_documents()
        assert len(docs) == 1
        assert docs[0]["filename"] == "test.txt"
        
        results = db.search("test")
        assert len(results) == 1
        
    finally:
        os.unlink(db_path)


def test_db_duplicate_document():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        
        id1 = db.add_document("/tmp/a.txt", "a.txt", ".txt", 100)
        id2 = db.add_document("/tmp/a.txt", "a.txt", ".txt", 100)
        
        assert id1 == id2
        
        docs = db.get_documents()
        assert len(docs) == 1
        
    finally:
        os.unlink(db_path)


def test_db_empty_summary():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        summary = db.get_summary()
        assert summary["total_documents"] == 0
        assert summary["total_words"] == 0
    finally:
        os.unlink(db_path)
