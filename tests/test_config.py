"""Tests for config module."""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from zaza.config import load_config, Config, SemanticConfig, OutputConfig, IngestionConfig


def test_load_config_defaults():
    """Test that load_config returns default Config when no file exists."""
    import zaza.config as config_mod
    orig = config_mod.DEFAULT_CONFIG_PATH
    try:
        config_mod.DEFAULT_CONFIG_PATH = Path("/tmp/nonexistent_config_zaza_test.yaml")
        cfg = load_config()
        assert isinstance(cfg, Config)
        assert cfg.semantic.enabled is True
        assert cfg.semantic.max_chunk_size == 512
        assert cfg.semantic.overlap == 64
        assert cfg.output.formats == ["json", "csv"]
        assert cfg.ingestion.extensions == [".txt", ".pdf", ".csv", ".md"]
    finally:
        config_mod.DEFAULT_CONFIG_PATH = orig


def test_load_config_semantic_from_yaml():
    """Test that semantic section is loaded from config.yaml.

    Verifies that semantic.max_chunk_size and semantic.overlap
    are read from config.yaml and not just using defaults.
    """
    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.yaml', delete=False, encoding='utf-8'
    )
    try:
        tmp.write("""
database:
  path: "./data/test.db"

ingestion:
  data_dir: "./my_data"
  extensions:
    - ".txt"
    - ".pdf"

analysis:
  top_words: 50
  min_word_length: 5

output:
  dir: "./results"
  formats:
    - "json"
    - "csv"
    - "html"

semantic:
  enabled: false
  model_name: "custom/model-name"
  embed_dir: "./custom_embed"
  max_search_results: 5
  max_chunk_size: 256
  overlap: 32
""")
        tmp.flush()
        cfg = load_config(tmp.name)

        # Verify semantic fields
        assert cfg.semantic.enabled is False
        assert cfg.semantic.model_name == "custom/model-name"
        assert cfg.semantic.embed_dir == "./custom_embed"
        assert cfg.semantic.max_search_results == 5
        assert cfg.semantic.max_chunk_size == 256
        assert cfg.semantic.overlap == 32

        # Verify other sections still load correctly
        assert cfg.output.formats == ["json", "csv", "html"]
        assert cfg.ingestion.data_dir == "./my_data"
        assert cfg.ingestion.extensions == [".txt", ".pdf"]
        assert cfg.database.path == "./data/test.db"
    finally:
        os.unlink(tmp.name)


def test_load_config_partial_semantic():
    """Test that partial semantic section works (only some fields set)."""
    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.yaml', delete=False, encoding='utf-8'
    )
    try:
        tmp.write("""
semantic:
  enabled: true
  max_chunk_size: 1024
""")
        tmp.flush()
        cfg = load_config(tmp.name)

        assert cfg.semantic.enabled is True
        assert cfg.semantic.max_chunk_size == 1024
        # Fields not in YAML should use defaults
        assert cfg.semantic.overlap == 64  # default
        assert cfg.semantic.model_name == "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # default
    finally:
        os.unlink(tmp.name)


def test_load_config_empty_yaml():
    """Test that empty YAML file returns default Config."""
    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.yaml', delete=False, encoding='utf-8'
    )
    try:
        tmp.write("")
        tmp.flush()
        cfg = load_config(tmp.name)
        assert isinstance(cfg, Config)
        assert cfg.semantic.max_chunk_size == 512  # default
    finally:
        os.unlink(tmp.name)
