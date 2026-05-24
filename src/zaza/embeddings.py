"""Semantic embedding and search pipeline.

Uses sentence-transformers to generate embeddings and ChromaDB for
vector-based document search.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import chromadb


class EmbeddingStore:
    """ChromaDB-backed embedding store for semantic search."""

    def __init__(self, persist_directory: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.model_name = model_name
        self._model = None
        self._client = None
        self._collection = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    @property
    def client(self):
        if self._client is None:
            self._client = chromadb.PersistentClient(path=str(self.persist_directory))
        return self._client

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict] = None):
        """Add a document and its embedding to the store."""
        # Truncate text to model's max tokens (rough estimate: 256 chars safe for MiniLM)
        truncated = text[:2048]
        embedding = self.model.encode(truncated).tolist()

        meta = metadata or {}
        meta["_full_text"] = text[:4096]  # Store a bit more for reference
        meta["_truncated_text"] = truncated

        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[truncated],
            metadatas=[meta],
        )

    def search(self, query: str, n_results: int = 10) -> List[Dict]:
        """Semantic search for a query. Returns ranked results."""
        query_embedding = self.model.encode(query).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["metadatas", "documents", "distances"],
        )

        docs = []
        for i in range(len(results["ids"][0])):
            doc = {
                "id": results["ids"][0][i],
                "distance": results["distances"][0][i],  # Lower = more similar
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
            }
            docs.append(doc)
        
        return docs

    def delete_document(self, doc_id: str):
        """Remove a document from the store."""
        self.collection.delete(ids=[doc_id])

    def get_metadata(self, doc_id: str) -> Optional[Dict]:
        """Get metadata for a specific document."""
        result = self.collection.get(ids=[doc_id])
        if result and result["metadatas"]:
            return result["metadatas"][0]
        return None

    def get_all_metadata(self) -> List[Dict]:
        """Get metadata for all stored documents."""
        result = self.collection.get(include=["metadatas"])
        if result and result["metadatas"]:
            return result["metadatas"]
        return []

    def count(self) -> int:
        """Return number of stored embeddings."""
        return self.collection.count()
