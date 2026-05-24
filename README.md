# Zaza Semantic Engine

Local-first semantic search and document indexing engine.

## Features

- **Multi-format ingestion**: PDF, TXT, Markdown, JSON, YAML, CSV, EPUB
- **Semantic search**: Hybrid search with local embeddings
- **CLI**: Full command-line interface
- **REST API**: FastAPI server with 5 endpoints
- **Reporting**: JSON and CSV reports
- **Local-only**: No external API calls, all processing on your machine

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Ingest documents
zaza ingest ./my-documents/

# Search
zaza search "your query"

# View stats
zaza stats

# Start API server
zaza server
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `zaza ingest <path>` | Index documents from a directory or file |
| `zaza search <query>` | Search indexed documents |
| `zaza stats` | Show indexing statistics |
| `zaza documents` | List all indexed documents |
| `zaza report [format]` | Generate report (json/csv) |
| `zaza server` | Start the REST API server |
| `zaza analyze --text "..."` | Analyze text semantically |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/summary` | Engine summary |
| GET | `/documents` | List documents |
| GET | `/search?q=` | Search documents |
| POST | `/analyze` | Semantic analysis |

## Configuration

Edit `config.yaml` to customize paths, embedding models, and search settings.

## License

MIT
