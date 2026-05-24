# Zaza Semantic Engine

Local-first multi-format document ingestion engine with **real semantic search**.

## Features

- **Multi-format ingestion**: TXT, Markdown, PDF, CSV, HTML, XML, DOCX
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

# With semantic search (embeddings)
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

# Start API server
zaza api
```

## Semantic Search

This project uses **sentence-transformers** (`all-MiniLM-L6-v2`) to generate embeddings and **ChromaDB** for vector storage. Unlike simple keyword search, semantic search understands context and can find relevant documents even when the exact words don't match.

Example: searching for "budget report" will also find documents about "quarterly financial results" because the embeddings capture the semantic similarity.

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
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
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

## License

MIT
