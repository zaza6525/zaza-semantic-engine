"""Tests for V3 features: JSON, YAML, EPUB ingestion."""

import pytest
import tempfile
import shutil
import json
import os
from pathlib import Path

from zaza.ingestion import (
    ingest_json,
    ingest_yaml,
    IngestionError,
    _json_to_text,
)


class TestJsonIngestion:
    """Test JSON file ingestion."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        yield
        shutil.rmtree(str(self.tmpdir), ignore_errors=True)

    def test_simple_json(self):
        """Test simple key-value JSON."""
        data = {"name": "Alice", "age": 30, "city": "Paris"}
        path = self.tmpdir / "simple.json"
        path.write_text(json.dumps(data))
        result = ingest_json(path)
        assert "name: Alice" in result
        assert "age: 30" in result
        assert "city: Paris" in result

    def test_nested_json(self):
        """Test nested JSON structure."""
        data = {
            "person": {
                "name": "Bob",
                "address": {
                    "street": "123 Rue de la Paix",
                    "city": "Lille"
                }
            }
        }
        path = self.tmpdir / "nested.json"
        path.write_text(json.dumps(data))
        result = ingest_json(path)
        assert "person:" in result
        assert "name: Bob" in result
        assert "street: 123 Rue de la Paix" in result
        assert "city: Lille" in result

    def test_json_list(self):
        """Test JSON array."""
        data = {"items": ["apple", "banana", "cherry"]}
        path = self.tmpdir / "list.json"
        path.write_text(json.dumps(data))
        result = ingest_json(path)
        assert "- apple" in result
        assert "- banana" in result
        assert "- cherry" in result

    def test_json_nested_list(self):
        """Test nested list in JSON."""
        data = {
            "teams": [
                {"name": "Alpha", "members": ["Alice", "Bob"]},
                {"name": "Beta", "members": ["Charlie"]}
            ]
        }
        path = self.tmpdir / "nested_list.json"
        path.write_text(json.dumps(data))
        result = ingest_json(path)
        assert "teams:" in result
        assert "name: Alpha" in result
        assert "- Alice" in result
        assert "- Charlie" in result

    def test_invalid_json(self):
        """Test error on invalid JSON."""
        path = self.tmpdir / "invalid.json"
        path.write_text("{broken json")
        with pytest.raises(IngestionError, match="Invalid JSON"):
            ingest_json(path)

    def test_json_null_value(self):
        """Test JSON with null values."""
        data = {"name": "Test", "value": None}
        path = self.tmpdir / "null.json"
        path.write_text(json.dumps(data))
        result = ingest_json(path)
        assert "value: null" in result

    def test_json_complex(self):
        """Test complex nested JSON similar to real-world config."""
        data = {
            "project": "zaza-semantic-engine",
            "version": "3.0.0",
            "features": ["semantic-search", "multi-format", "multilingual"],
            "config": {
                "semantic": {
                    "enabled": True,
                    "model": "paraphrase-multilingual-MiniLM-L12-v2"
                },
                "ingestion": {
                    "formats": ["txt", "pdf", "json", "yaml", "epub"]
                }
            }
        }
        path = self.tmpdir / "complex.json"
        path.write_text(json.dumps(data))
        result = ingest_json(path)
        assert "project: zaza-semantic-engine" in result
        assert "version: 3.0.0" in result
        assert "semantic-search" in result
        assert "multilingual" in result
        assert "paraphrase-multilingual-MiniLM-L12-v2" in result


class TestYamlIngestion:
    """Test YAML file ingestion."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        yield
        shutil.rmtree(str(self.tmpdir), ignore_errors=True)

    def test_simple_yaml(self):
        """Test simple YAML."""
        yaml_content = """
name: ZAZA Semantic Engine
version: 3.0.0
enabled: true
"""
        path = self.tmpdir / "simple.yaml"
        path.write_text(yaml_content)
        result = ingest_yaml(path)
        assert "name: ZAZA Semantic Engine" in result
        assert "version: 3.0.0" in result
        assert "enabled: True" in result

    def test_nested_yaml(self):
        """Test nested YAML."""
        yaml_content = """
semantic:
  model: paraphrase-multilingual-MiniLM-L12-v2
  embed_dir: ./data/embeddings
  max_results: 10
"""
        path = self.tmpdir / "nested.yaml"
        path.write_text(yaml_content)
        result = ingest_yaml(path)
        assert "semantic:" in result
        assert "model: paraphrase-multilingual-MiniLM-L12-v2" in result
        assert "max_results: 10" in result

    def test_yaml_list(self):
        """Test YAML with lists."""
        yaml_content = """
formats:
  - txt
  - pdf
  - json
  - yaml
  - epub
"""
        path = self.tmpdir / "list.yaml"
        path.write_text(yaml_content)
        result = ingest_yaml(path)
        assert "- txt" in result
        assert "- epub" in result

    def test_yaml_invalid(self):
        """Test error on invalid YAML."""
        path = self.tmpdir / "invalid.yaml"
        path.write_text("  invalid:\n    bad indent:  [")
        # PyYAML should raise YAMLError
        with pytest.raises(IngestionError, match="Invalid YAML"):
            ingest_yaml(path)

    def test_yaml_file(self):
        """Test .yml extension."""
        yaml_content = "project: test\nversion: 1.0\n"
        path = self.tmpdir / "config.yml"
        path.write_text(yaml_content)
        result = ingest_yaml(path)
        assert "project: test" in result


class TestCacheModel:
    """Test EmbeddingStore model caching."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.tmpdir = tempfile.mkdtemp()
        yield
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @pytest.mark.skipif(
        not all([
            True  # sentence_transformers check
        ]),
        reason="sentence-transformers not installed"
    )
    def test_cache_same_model(self):
        """Test that same model returns cached instance."""
        from zaza.embeddings import get_cached_store

        store1 = get_cached_store(self.tmpdir, "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        store2 = get_cached_store(self.tmpdir, "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        assert store1 is store2

    @pytest.mark.skipif(
        not all([
            True
        ]),
        reason="sentence-transformers not installed"
    )
    def test_cache_different_model(self):
        """Test that different model returns different instance."""
        from zaza.embeddings import get_cached_store

        store1 = get_cached_store(self.tmpdir, "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        store2 = get_cached_store(self.tmpdir, "sentence-transformers/all-MiniLM-L6-v2")
        assert store1 is not store2

    @pytest.mark.skipif(
        not all([
            True
        ]),
        reason="sentence-transformers not installed"
    )
    def test_cache_different_dir(self):
        """Test that different directory returns different instance."""
        from zaza.embeddings import get_cached_store

        dir2 = self.tmpdir + "/other"
        store1 = get_cached_store(self.tmpdir, "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        store2 = get_cached_store(dir2, "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        assert store1 is not store2


class TestJsonToTextHelper:
    """Test the _json_to_text helper function."""

    def test_dict(self):
        result = _json_to_text({"a": 1, "b": 2})
        assert "a: 1" in result
        assert "b: 2" in result

    def test_list(self):
        result = _json_to_text([1, 2, 3])
        assert "- 1" in result
        assert "- 3" in result

    def test_deep_nested(self):
        data = {
            "level1": {
                "level2": {
                    "level3": "deep"
                }
            }
        }
        result = _json_to_text(data)
        text = "\n".join(result)
        assert "level1:" in text
        assert "level2:" in text
        assert "level3: deep" in text
