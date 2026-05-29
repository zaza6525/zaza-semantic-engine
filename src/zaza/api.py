"""FastAPI REST API for ZAZA Semantic Engine."""

import tempfile
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Allowed root path for directory ingestion (security)
ALLOWED_INGEST_ROOT = None  # Set to a path string to restrict, None = unlimited


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
    version="3.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
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
    
    # Use tempfile for safe filename handling
    import tempfile
    import os
    safe_name = file.filename or "unnamed"
    fd, tmp_path = tempfile.mkstemp(
        suffix=Path(safe_name).suffix,
        prefix="zaza_ingest_"
    )
    try:
        content = await file.read()
        with os.fdopen(fd, 'wb') as f:
            f.write(content)
        
        result = engine.ingest_file(tmp_path)
        return result
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


@app.post("/ingest/directory")
async def ingest_directory(dir_path: Optional[str] = None):
    """Ingest all files from a directory. If ALLOWED_INGEST_ROOT is set, 
    the requested path must be under it."""
    engine = app.state.engine
    if not engine:
        raise HTTPException(500, "Engine not initialized")
    
    # Security: validate path against allowed root
    if ALLOWED_INGEST_ROOT and dir_path:
        resolved = Path(dir_path).resolve()
        allowed = Path(ALLOWED_INGEST_ROOT).resolve()
        if not str(resolved).startswith(str(allowed)):
            raise HTTPException(403, "Directory outside allowed ingest root")
    
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
    """Search documents by name (keyword)."""
    engine = app.state.engine
    if not engine:
        raise HTTPException(500, "Engine not initialized")
    
    return engine.search(query)


@app.get("/search-semantic")
async def search_semantic_documents(query: str, top: int = 10):
    """Semantic search using document embeddings."""
    engine = app.state.engine
    if not engine:
        raise HTTPException(500, "Engine not initialized")
    
    results = engine.search_semantic(query, n_results=top)
    return results


@app.get("/embeddings/status")
async def embedding_status():
    """Check embedding store status."""
    engine = app.state.engine
    if not engine:
        return {"enabled": False, "reason": "Engine not initialized"}
    
    if engine.embed_store:
        return {
            "enabled": True,
            "model": engine.embed_store.model_name,
            "documents_count": engine.embed_store.collection.count(),
        }
    return {"enabled": False, "reason": "Embeddings not available"}


class TextAnalysisRequest(BaseModel):
    text: str
    language: str = "fr"


@app.post("/analyze")
async def analyze_text(request: TextAnalysisRequest):
    """Analyze raw text (no file needed)."""
    from zaza.analysis import analyze_text as analyze
    result = analyze(request.text, stop_words_lang=request.language)
    return result


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "version": app.version}


@app.post("/ingest/audio")
async def ingest_audio(file: UploadFile = File(...)):
    """Transcribe audio via faster-whisper STT and auto-search."""
    engine = app.state.engine
    if not engine:
        raise HTTPException(500, "Engine not initialized")

    # Save temp audio
    fd, tmp_path = tempfile.mkstemp(suffix=".webm", prefix="zaza_audio_")
    try:
        content = await file.read()
        with os.fdopen(fd, "wb") as f:
            f.write(content)

        # STT via faster-whisper
        text = _transcribe_audio(tmp_path)

        if not text.strip():
            return {"text": "", "results": [], "message": "Aucune parole détectée"}

        # Auto-search
        results = []
        if engine.embed_store:
            results = engine.search_semantic(text, n_results=10)

        return {"text": text, "results": results}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _transcribe_audio(path):
    """Transcribe audio file using faster-whisper on CPU."""
    from faster_whisper import WhisperModel
    # Lazy global cache — load once, reuse
    if not hasattr(_transcribe_audio, "_model"):
        _transcribe_audio._model = WhisperModel(
            "large-v3", device="cpu", compute_type="int8"
        )
    segments, info = _transcribe_audio._model.transcribe(
        path, language="fr", beam_size=1
    )
    return " ".join(seg.text for seg in segments)


@app.get("/search-ui", response_class=HTMLResponse)
async def search_ui():
    """Serve the semantic search UI."""
    ui_path = Path(__file__).parent / "search_ui.html"
    return ui_path.read_text(encoding="utf-8")
