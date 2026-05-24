# Zaza Semantic Engine

Local-first multi-format document ingestion engine with **real semantic search**.

## Features

- **Multi-format ingestion**: TXT, Markdown, PDF, CSV, HTML, XML, DOCX, **JSON, YAML, EPUB**
- **Semantic search**: Hybrid search using sentence-transformers embeddings stored in ChromaDB
- **Keyword search**: Fuzzy filename matching (backward compatible)
- **CLI**: Full command-line interface
- **REST API**: FastAPI server with 8 endpoints
- **Analysis**: Word frequency, lexical density, readability metrics
- **Reporting**: JSON and CSV reports
- **Local-only**: No external API calls — all processing on your machine

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

## Semantic Search

This project uses **sentence-transformers** (`paraphrase-multilingual-MiniLM-L12-v2`) to generate embeddings and **ChromaDB** for vector storage. The multilingual model supports **50+ languages** including French, English, Arabic, and more.

Unlike simple keyword search, semantic search understands context and can find relevant documents even when the exact words don't match.

Example: searching for "rapport budgétaire" will also find documents about "quarterly financial results" because the embeddings capture the semantic similarity.

## CLI Commands

| Command | Description |
|---------|-------------|
| `zaza ingest <path>` | Index documents from a directory or file |
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

## Configuration

Edit `config.yaml` to customize paths, embedding models, and search settings.

### Semantic Configuration

```yaml
semantic:
  enabled: true                    # Set false to disable embeddings
  model_name: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  embed_dir: "./data/embeddings"   # ChromaDB persist directory
  max_search_results: 10
```

### Supported Formats

- `.txt` — Plain text
- `.md` / `.markdown` — Markdown (syntax stripped)
- `.pdf` — PDF (via pypdf)
- `.csv` — CSV (converted to key-value format)
- `.html` / `.htm` — HTML (via BeautifulSoup)
- `.xml` — XML (via standard library)
- `.docx` — Word documents (via python-docx)
- `.json` — **V3** JSON files (recursive key-value extraction)
- `.yaml` / `.yml` — **V3** YAML files (recursive key-value extraction)
- `.epub` — **V3** ePUB books (via ebooklib, requires `[semantic]` extras)

### Model Caching (V3)

The embedding model is now cached globally within a single process. Calling `zaza ingest` followed by `zaza search-semantic` will **not** reload the model — it reuses the cached instance. This significantly reduces startup time when running multiple CLI commands in sequence.

## License

MIT
