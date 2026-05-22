"""SQLite database for document analysis history."""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional


class Database:
    """Manages SQLite storage for analysis results."""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    
    def _init_db(self):
        """Create tables if they don't exist."""
        conn = self._get_conn()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT NOT NULL UNIQUE,
                    filename TEXT NOT NULL,
                    filetype TEXT NOT NULL,
                    file_size INTEGER,
                    ingested_at TEXT NOT NULL,
                    status TEXT DEFAULT 'success'
                );
                
                CREATE TABLE IF NOT EXISTS analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    word_count INTEGER,
                    char_count INTEGER,
                    sentence_count INTEGER,
                    unique_words INTEGER,
                    lexical_density REAL,
                    avg_word_length REAL,
                    top_words TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_docs_filepath ON documents(filepath);
                CREATE INDEX IF NOT EXISTS idx_docs_ingested ON documents(ingested_at);
                CREATE INDEX IF NOT EXISTS idx_analysis_doc ON analysis(document_id);
            """)
            conn.commit()
        finally:
            conn.close()
    
    def add_document(self, filepath: str, filename: str, filetype: str, 
                     file_size: int) -> int:
        """Register a document. Returns the document ID."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """INSERT OR IGNORE INTO documents (filepath, filename, filetype, file_size, ingested_at, status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (filepath, filename, filetype, file_size, datetime.now().isoformat(), "success")
            )
            conn.commit()
            
            # Get the ID
            row = conn.execute(
                "SELECT id FROM documents WHERE filepath = ?", (filepath,)
            ).fetchone()
            return row["id"]
        finally:
            conn.close()
    
    def add_analysis(self, document_id: int, analysis: dict):
        """Store analysis results for a document."""
        conn = self._get_conn()
        try:
            import json
            top_words_json = json.dumps(analysis.get("top_words", []))
            conn.execute(
                """INSERT INTO analysis (document_id, word_count, char_count, sentence_count,
                   unique_words, lexical_density, avg_word_length, top_words, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (document_id,
                 analysis.get("word_count"),
                 analysis.get("char_count"),
                 analysis.get("sentence_count"),
                 analysis.get("unique_words"),
                 analysis.get("lexical_density"),
                 analysis.get("avg_word_length"),
                 top_words_json,
                 datetime.now().isoformat())
            )
            conn.commit()
        finally:
            conn.close()
    
    def get_summary(self) -> dict:
        """Get overall statistics from the database."""
        conn = self._get_conn()
        try:
            stats = conn.execute("""
                SELECT 
                    COUNT(DISTINCT d.id) as total_docs,
                    COALESCE(SUM(a.word_count), 0) as total_words,
                    COALESCE(SUM(a.char_count), 0) as total_chars,
                    COALESCE(AVG(a.lexical_density), 0) as avg_density,
                    MIN(d.ingested_at) as first_ingestion,
                    MAX(d.ingested_at) as last_ingestion
                FROM documents d
                LEFT JOIN analysis a ON d.id = a.document_id
            """).fetchone()
            
            return {
                "total_documents": stats["total_docs"],
                "total_words": stats["total_words"],
                "total_characters": stats["total_chars"],
                "average_lexical_density": round(stats["avg_density"], 4),
                "first_ingestion": stats["first_ingestion"],
                "last_ingestion": stats["last_ingestion"],
            }
        finally:
            conn.close()
    
    def get_documents(self) -> list:
        """List all ingested documents."""
        conn = self._get_conn()
        try:
            rows = conn.execute("""
                SELECT d.filename, d.filetype, d.file_size, d.ingested_at,
                       a.word_count, a.unique_words, a.lexical_density
                FROM documents d
                LEFT JOIN analysis a ON d.id = a.document_id
                ORDER BY d.ingested_at DESC
            """).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
    
    def search(self, query: str) -> list:
        """Search documents by filename."""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                """SELECT d.filename, d.filetype, d.file_size, d.ingested_at,
                          a.word_count, a.unique_words, a.lexical_density
                   FROM documents d
                   LEFT JOIN analysis a ON d.id = a.document_id
                   WHERE d.filename LIKE ?
                   ORDER BY d.ingested_at DESC""",
                (f"%{query}%",)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
