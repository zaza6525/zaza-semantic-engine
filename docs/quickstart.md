# Quick Start Guide

## Installation

```bash
git clone https://github.com/zaza6525/zaza-semantic-engine.git
cd zaza-semantic-engine
python -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"
```

## Ingest documents

```bash
# Ingest a single file
zaza ingest ./my-document.pdf

# Ingest a directory (recursive)
zaza ingest -r ./my-documents/
```

## Search

```bash
# Keyword search (by filename)
zaza search "report"

# Semantic search (by meaning)
zaza search-semantic "financial analysis quarterly results" --top 5

# Search in French
zaza search-semantic "analyse financière résultats trimestriels"
```

## API server

```bash
# Start on default port (127.0.0.1:8000)
zaza api

# Or with custom port
zaza server --port 9000
```

Then use:

```bash
# Health check
curl http://127.0.0.1:8000/health

# Semantic search via API
curl "http://127.0.0.1:8000/search-semantic?q=budget&top=5"

# Upload and ingest a file
curl -F "file=@document.pdf" http://127.0.0.1:8000/ingest/file
```

## Docker

```bash
docker build -t zaza .
docker run --rm -it -v $(pwd)/data:/app/data zaza ingest ./docs/
docker run --rm -it -p 8000:8000 -v $(pwd)/data:/app/data zaza api --port 8000
```

## Configuration

Edit `config.yaml` in your project root:

```yaml
semantic:
  enabled: true
  model_name: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  embed_dir: "./data/embeddings"
  max_search_results: 10
```

See [the README](../README.md) for full documentation.
