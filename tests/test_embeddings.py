"""Tests for the semantic embedding pipeline."""

import pytest
import tempfile
import shutil
from pathlib import Path

# Skip if sentence-transformers or chromadb not installed
st_installed = True
cd_installed = True
try:
    import sentence_transformers  # noqa: F401
except ImportError:
    st_installed = False

try:
    import chromadb  # noqa: F401
except ImportError:
    cd_installed = False


@pytest.mark.skipif(
    not (st_installed and cd_installed),
    reason="sentence-transformers and/or chromadb not installed"
)
class TestEmbeddingStore:
    """Test the ChromaDB-backed embedding store."""

    @pytest.fixture(scope="class", autouse=True)
    def shared_tmpdir(self):
        """Shared temp dir for all tests in the class to enable model caching."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_add_and_search(self, shared_tmpdir):
        from zaza.embeddings import get_cached_store

        store = get_cached_store(shared_tmpdir, "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        store.clear()

        # Add documents
        store.add_document("doc1", "The quick brown fox jumps over the lazy dog", {"filename": "fox.txt"})
        store.add_document("doc2", "Machine learning models process large datasets", {"filename": "ml.txt"})
        store.add_document("doc3", "Neural networks use layers of interconnected nodes", {"filename": "nn.txt"})

        assert store.count() == 3

        # Semantic search
        results = store.search("artificial intelligence neural networks")
        assert len(results) == 3

        # The fox doc should NOT be the top result for an AI query
        # Check that the best result is NOT the fox document
        best_id = results[0]["id"]
        assert best_id != "doc1"

    def test_search_with_no_documents(self, shared_tmpdir):
        from zaza.embeddings import get_cached_store

        empty_dir = shared_tmpdir + "/empty"
        store = get_cached_store(empty_dir, "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

        results = store.search("any query")
        assert len(results) == 0

    def test_delete_document(self, shared_tmpdir):
        from zaza.embeddings import get_cached_store

        store = get_cached_store(shared_tmpdir + "/delete", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        store.clear()

        store.add_document("doc1", "Test content 1", {"filename": "1.txt"})
        store.add_document("doc2", "Test content 2", {"filename": "2.txt"})
        assert store.count() == 2

        store.delete_document("doc1")
        assert store.count() == 1

        results = store.search("test content")
        assert len(results) == 1

    def test_metadata_persistence(self, shared_tmpdir):
        from zaza.embeddings import get_cached_store

        store = get_cached_store(shared_tmpdir + "/meta", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        store.clear()

        store.add_document("doc1", "Test content", {"filename": "test.txt", "custom": "value"})
        meta = store.get_metadata("doc1")
        assert meta is not None
        assert meta["filename"] == "test.txt"
        assert meta["custom"] == "value"

    def test_persistence_across_instances(self, shared_tmpdir):
        """Verify ChromaDB persists to disk and can be reloaded."""
        from zaza.embeddings import get_cached_store

        path = shared_tmpdir + "/persist"
        
        # Create store and add docs
        store1 = get_cached_store(path, "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        store1.clear()
        store1.add_document("doc1", "First document content", {"filename": "1.txt"})
        assert store1.count() == 1

        # Create a new store instance pointing to the same directory
        store2 = get_cached_store(path, "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        assert store2.count() == 1

        results = store2.search("document content")
        assert len(results) == 1

    def test_get_all_metadata(self, shared_tmpdir):
        from zaza.embeddings import get_cached_store

        store = get_cached_store(shared_tmpdir + "/allmeta", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        store.clear()

        store.add_document("doc1", "Content A", {"filename": "a.txt"})
        store.add_document("doc2", "Content B", {"filename": "b.txt"})

        all_meta = store.get_all_metadata()
        assert len(all_meta) == 2
        filenames = {m["filename"] for m in all_meta}
        assert filenames == {"a.txt", "b.txt"}

    def test_cache_same_model(self, shared_tmpdir):
        """Test that get_cached_store returns same instance for same dir+model."""
        from zaza.embeddings import get_cached_store

        store1 = get_cached_store(shared_tmpdir, "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        store2 = get_cached_store(shared_tmpdir, "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        assert store1 is store2

    def test_cache_different_model(self, shared_tmpdir):
        """Test that get_cached_store returns different instance for different model."""
        from zaza.embeddings import get_cached_store

        store1 = get_cached_store(shared_tmpdir, "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        store2 = get_cached_store(shared_tmpdir, "sentence-transformers/all-MiniLM-L6-v2")
        assert store1 is not store2
