# ZAZA Semantic Engine

A multi-format document ingestion and semantic analysis engine with persistent storage.

## What it does

ZAZA ingests documents (TXT, PDF, CSV, Markdown), extracts semantic metrics (word count, lexical density, top words, readability), and stores everything in a SQLite database with queryable history.

## Features

- **Multi-format ingestion** — TXT, PDF, CSV, Markdown
- **Semantic analysis** — word frequency, lexical density, readability scores, top keywords
- **Persistent storage** — SQLite database with full query history
- **CLI** — `zaza ingest`, `zaza stats`, `zaza documents`, `zaza search`
- **Reports** — JSON and CSV export
- **Configurable** — YAML config for all settings
- **27 tests** — all passing

## Installation

```bash
git clone https://github.com/zaza6525/-ZAZA-Semantic-Engine.git
cd -ZAZA-Semantic-Engine
pip install -e ".[dev]"
```

## Usage

### Ingest a directory

```bash
zaza ingest ./data
```

### Ingest a single file

```bash
zaza ingest --file ./data/report.pdf
```

### View statistics

```bash
zaza stats
zaza stats --json
```

### List all documents

```bash
zaza documents
zaza documents --search report
```

### Search documents

```bash
zaza search quarterly
```

### Generate reports

```bash
zaza report --text
zaza report  # saves JSON + CSV to output/
```

## Configuration

Edit `config.yaml`:

```yaml
database:
  path: "./data/zaza.db"

ingestion:
  data_dir: "./data"
  extensions: [".txt", ".pdf", ".csv", ".md"]

analysis:
  top_words: 20
  min_word_length: 3
  stop_words_language: "fr"

output:
  dir: "./output"
  formats: ["json", "csv"]
```

## Architecture

```
data/          ← Place your documents here
src/zaza/
  config.py       ← YAML config loader
  ingestion.py    ← Multi-format file readers
  analysis.py     ← Semantic analysis engine
  database.py     ← SQLite storage layer
  reporting.py    ← Report generation
  engine.py       ← Main orchestrator
  cli.py          ← CLI entry point
tests/          ← 27 tests (100% passing)
output/         ← Generated reports
config.yaml     ← Configuration file
```

## License

MIT
