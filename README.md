---
title: Zaza Semantic Engine
emoji: 🧠
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
short_description: Local-first multilingual semantic search (50+ languages)
---

# Zaza Semantic Engine

Local-first multi-format document ingestion engine with **real semantic search**.

[![Tests](https://github.com/zaza6525/zaza-semantic-engine/actions/workflows/test.yml/badge.svg)](https://github.com/zaza6525/zaza-semantic-engine/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/zaza-semantic-engine.svg)](https://pypi.org/project/zaza-semantic-engine/)

## Why Zaza?

Most document tools fall into two camps: cloud-based SaaS (your docs leave your machine) or dumb keyword search (finds exact word matches, misses the point). Zaza does both **locally** and **semantically**.

- **Local-first** — your documents never leave your machine. No API keys, no data leaks.
- **Semantic search** — find documents by *meaning*, not just keywords. Search "budget" and it finds "financial analysis", "quarterly results".
- **Multi-format** — TXT, PDF, Markdown, DOCX, JSON, YAML, EPUB, CSV, HTML, XML. Ingest anything.
- **50+ languages** — built on `paraphrase-multilingual-MiniLM-L12-v2`. Search in French, English, Arabic, or any supported language.
- **Zero config** — `zaza ingest ./docs/` and you're done.

## Installation

```bash
# Core package
pip install -e .

# With API support
pip install -e ".[api]"

# With semantic search (embeddings + multilingual model)
pip install -e ".[semantic]"

# Full installation
pip install -e ".[all]"
```

## Quick Start

```bash
# Ingest documents
zaza ingest ./my-documents/

# Keyword search (by filename)
zaza search "report"

# Semantic search (by meaning)
zaza search-semantic "financial analysis quarterly results" --top 5

# View stats
zaza stats

# Start API server (V3: either form works)
zaza api
zaza server
```

## Semantic Search in Action

This project uses **sentence-transformers** (`paraphrase-multilingual-MiniLM-L12-v2`) to generate embeddings and **ChromaDB** for vector storage.

Unlike keyword search, semantic search finds documents with *related concepts* even when the exact words differ:

| Query | Keyword Search | Semantic Search |
|-------|---------------|-----------------|
| "budget" | Only files named "budget" | Finds "financial report", "quarterly analysis", "cost breakdown" |
| "rapport financier" | Only French files with exact match | Finds "financial analysis", "balance sheet", "revenue summary" |

## Demo

Try it live on Hugging Face: [**Zaza Semantic Search Space**](https://huggingface.co/spaces/ffffre/zaza-semantic-search)

## CLI Commands

| Command | Description |
|---------|-------------|
| `zaza ingest <path>` | Index documents from a directory or file (use `-r` for recursive) |
| `zaza search <query>` | Search documents by filename (keyword) |
| `zaza search-semantic <query>` | Semantic search using embeddings |
| `zaza stats` | Show indexing statistics |
| `zaza documents` | List all indexed documents |
| `zaza report [format]` | Generate report (json/csv) |
| `zaza api` | Start the REST API server |
| `zaza server` | **V3 alias** — same as `zaza api` |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/summary` | Engine summary |
| GET | `/documents` | List documents |
| GET | `/search?q=` | Keyword search |
| GET | `/search-semantic?q=&top=10` | Semantic search |
| GET | `/embeddings/status` | Check embedding store |
| POST | `/analyze` | Analyze raw text |
| POST | `/ingest/file` | Upload and ingest a file |
| POST | `/ingest/directory` | Ingest all files from directory |

## Supported Formats

| Format | Extension | Method |
|--------|-----------|--------|
| Plain text | `.txt` | Direct read |
| Markdown | `.md`, `.markdown` | Syntax stripped |
| PDF | `.pdf` | via `pypdf` |
| CSV | `.csv` | Converted to key-value |
| HTML | `.html`, `.htm` | via `BeautifulSoup` |
| XML | `.xml` | Standard library |
| Word | `.docx` | via `python-docx` |
| JSON | `.json` | Recursive key-value (V3) |
| YAML | `.yaml`, `.yml` | Recursive key-value (V3) |
| ePUB | `.epub` | via `ebooklib` (V3, requires `[semantic]`) |

## Model Caching (V3)

The embedding model is cached globally within a single process. `zaza ingest` + `zaza search-semantic` doesn't reload the model — it reuses the cached instance. Startup time drops significantly.

## Configuration

Edit `config.yaml` to customize paths, embedding models, and search settings.

```yaml
semantic:
  enabled: true                    # Set false to disable embeddings
  model_name: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  embed_dir: "./data/embeddings"   # ChromaDB persist directory
  max_search_results: 10
```

## License

MIT
