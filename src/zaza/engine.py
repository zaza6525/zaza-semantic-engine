"""Main orchestrator engine."""

from pathlib import Path
from typing import List, Dict, Optional

from zaza.config import load_config, Config
from zaza.ingestion import ingest_file, chunk_and_embed, IngestionError
from zaza.analysis import analyze_text
from zaza.database import Database
from zaza.reporting import Reporter


class SemanticEngine:
    """Main engine orchestrating ingestion, analysis, and reporting."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = load_config(config_path)
        self.db = Database(self.config.database.path)
        self.reporter = Reporter(self.config.output.dir)
        self.embed_store = None
        if self.config.semantic.enabled:
            try:
                from zaza.embeddings import get_cached_store
                self.embed_store = get_cached_store(
                    self.config.semantic.embed_dir,
                    self.config.semantic.model_name
                )
            except Exception as e:
                print(f"  ⚠️  Semantic embeddings disabled: {e}")
    
    def ingest_directory(self, dir_path: Optional[str] = None, recursive: bool = False) -> List[Dict]:
        """Ingest all supported files from a directory."""
        target = Path(dir_path) if dir_path else Path(self.config.ingestion.data_dir)
        
        if not target.exists() or not target.is_dir():
            print(f"  ⚠️  Directory not found: {target}")
            return []
        
        extensions = self.config.ingestion.extensions
        if recursive:
            files = [f for f in target.rglob('*') if f.is_file() and f.suffix.lower() in extensions]
        else:
            files = [f for f in target.iterdir() if f.is_file() and f.suffix.lower() in extensions]
        
        if not files:
            print(f"  ℹ️  No supported files found in {target}")
            return []
        
        print(f"  📂 Found {len(files)} file(s) in {target}")
        results = []
        
        for file_path in files:
            try:
                text = ingest_file(
                    file_path,
                    encoding=self.config.ingestion.encoding,
                    fallback=self.config.ingestion.fallback_encoding
                )
                
                # Store in DB
                doc_id = self.db.add_document(
                    filepath=str(file_path),
                    filename=file_path.name,
                    filetype=file_path.suffix.lower(),
                    file_size=file_path.stat().st_size
                )
                
                # Analyze
                analysis = analyze_text(
                    text,
                    top_words=self.config.analysis.top_words,
                    min_word_length=self.config.analysis.min_word_length,
                    stop_words_lang=self.config.analysis.stop_words_language
                )
                
                # Store analysis
                self.db.add_analysis(doc_id, analysis)
                
               # Chunk and embed semantic vectors
                if self.embed_store:
                    try:
                        result = chunk_and_embed(
                            file_path,
                            self.embed_store,
                            encoding=self.config.ingestion.encoding,
                            fallback=self.config.ingestion.fallback_encoding,
                            max_chunk_size=self.config.semantic.max_chunk_size,
                            overlap=self.config.semantic.overlap,
                        )
                        chunk_count = result.get("chunk_count", 0)
                        print(f"  ✅ {file_path.name} — {analysis['word_count']} words, {chunk_count} chunks")
                    except Exception as e:
                        print(f"  ⚠️  Semantic embedding error for {file_path.name}: {e}")
                        chunk_count = 0
                
                results.append({
                    "filename": file_path.name,
                    "filetype": file_path.suffix.lower(),
                    "word_count": analysis["word_count"],
                    "top_words": analysis["top_words"][:5],
                    "status": "success",
                })
                
                print(f"  ✅ {file_path.name} — {analysis['word_count']} words")
                
            except Exception as e:
                print(f"  ❌ {file_path.name} — Error: {e}")
                results.append({
                    "filename": file_path.name,
                    "filetype": file_path.suffix.lower(),
                    "status": f"error: {e}",
                })
        
        print(f"  🏁 Ingestion complete: {len(results)} file(s) processed.")
        return results
    
    def ingest_file(self, file_path: str) -> Dict:
        """Ingest a single file — uses the same chunking pipeline as ingest_directory."""
        path = Path(file_path)
        text = ingest_file(path, self.config.ingestion.encoding, self.config.ingestion.fallback_encoding)
        
        doc_id = self.db.add_document(
            filepath=str(path),
            filename=path.name,
            filetype=path.suffix.lower(),
            file_size=path.stat().st_size
        )
        
        analysis = analyze_text(
            text,
            top_words=self.config.analysis.top_words,
            min_word_length=self.config.analysis.min_word_length,
            stop_words_lang=self.config.analysis.stop_words_language
        )
        
        self.db.add_analysis(doc_id, analysis)
        
        # Store semantic embedding using same chunking pipeline as directory ingest
        if self.embed_store:
            try:
                from zaza.ingestion import chunk_and_embed
                result = chunk_and_embed(
                    path,
                    self.embed_store,
                    encoding=self.config.ingestion.encoding,
                    fallback=self.config.ingestion.fallback_encoding,
                    max_chunk_size=self.config.semantic.max_chunk_size,
                    overlap=self.config.semantic.overlap,
                )
            except Exception as e:
                print(f"  ⚠️  Semantic embedding error for {path.name}: {e}")
        
        return {
            "filename": path.name,
            "word_count": analysis["word_count"],
            "top_words": analysis["top_words"][:5],
        }
    
    def get_summary(self) -> dict:
        """Get database summary."""
        return self.db.get_summary()
    
    def get_documents(self) -> List[Dict]:
        """List all documents."""
        return self.db.get_documents()
    
    def search(self, query: str) -> List[Dict]:
        """Search documents by name."""
        return self.db.search(query)

    def search_semantic(self, query: str, n_results: Optional[int] = None) -> List[Dict]:
        """Semantic search across all ingested documents."""
        if not self.embed_store:
            return []
        
        max_results = n_results or self.config.semantic.max_search_results
        return self.db.search_semantic(query, self.embed_store)[:max_results]
    
    def generate_reports(self, output_formats: Optional[List[str]] = None):
        """Generate all reports."""
        formats = output_formats or self.config.output.formats
        summary = self.get_summary()
        documents = self.get_documents()
        
        if "json" in formats:
            path = self.reporter.save_json(self.reporter.summary_report(summary))
            print(f"  📄 Summary JSON: {path}")
        
        if "csv" in formats and documents:
            path = self.reporter.save_csv(documents)
            print(f"  📄 Documents CSV: {path}")
        
        return summary, documents
