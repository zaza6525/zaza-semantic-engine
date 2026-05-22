"""FastAPI REST API for ZAZA Semantic Engine."""

from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize engine on startup."""
    from zaza.engine import SemanticEngine
    app.state.engine = SemanticEngine()
    yield
    # Cleanup on shutdown
    app.state.engine = None


app = FastAPI(
    title="ZAZA Semantic Engine",
    description="Multi-format document ingestion and semantic analysis API",
    version="2.0.0",
    lifespan=lifespan,
)


class DocumentInfo(BaseModel):
    filename: str
    filetype: str
    word_count: int
    unique_words: int
    lexical_density: float
    ingested_at: str


class SummaryResponse(BaseModel):
    total_documents: int
    total_words: int
    total_characters: int
    average_lexical_density: float
    first_ingestion: Optional[str]
    last_ingestion: Optional[str]


class AnalysisResponse(BaseModel):
    filename: str
    word_count: int
    char_count: int
    sentence_count: int
    unique_words: int
    lexical_density: float
    avg_word_length: float
    top_words: List[Dict[str, Any]]


class IngestResult(BaseModel):
    filename: str
    status: str
    word_count: Optional[int] = None
    top_words: Optional[list] = None
    error: Optional[str] = None


@app.post("/ingest/file")
async def ingest_single_file(file: UploadFile = File(...)):
    """Ingest a single file."""
    engine = app.state.engine
    if not engine:
        raise HTTPException(500, "Engine not initialized")
    
    # Save temp file
    tmp_path = Path(f"/tmp/{file.filename}")
    with open(tmp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        result = engine.ingest_file(str(tmp_path))
        return result
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        tmp_path.unlink(missing_ok=True)


@app.post("/ingest/directory")
async def ingest_directory(dir_path: Optional[str] = None):
    """Ingest all files from a directory."""
    engine = app.state.engine
    if not engine:
        raise HTTPException(500, "Engine not initialized")
    
    results = engine.ingest_directory(dir_path)
    return results


@app.get("/summary")
async def get_summary():
    """Get overall analysis summary."""
    engine = app.state.engine
    if not engine:
        raise HTTPException(500, "Engine not initialized")
    
    return engine.get_summary()


@app.get("/documents", response_model=List[DocumentInfo])
async def get_documents(search: Optional[str] = None):
    """List all ingested documents."""
    engine = app.state.engine
    if not engine:
        raise HTTPException(500, "Engine not initialized")
    
    if search:
        docs = engine.search(search)
    else:
        docs = engine.get_documents()
    
    return docs


@app.get("/search")
async def search_documents(query: str):
    """Search documents by name."""
    engine = app.state.engine
    if not engine:
        raise HTTPException(500, "Engine not initialized")
    
    return engine.search(query)


@app.post("/analyze")
async def analyze_text(text: str, language: str = "fr"):
    """Analyze raw text (no file needed)."""
    from zaza.analysis import analyze_text as analyze
    result = analyze(text, stop_words_lang=language)
    return result


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "version": "2.0.0"}
