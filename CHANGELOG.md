# Changelog

All notable changes to [Zaza Semantic Engine](https://github.com/zaza6525/zaza-semantic-engine) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v3.2.0] — 2026-05-27

### Added
- Smart chunking with semantic-aware segmentation
- Enriched metadata extraction per chunk
- Grouped search results for better readability
- Web UI (`search_ui.html`) for visual semantic search
- New CLI command `zaza search-docs` as dedicated search entry point
- Chunking and config unit tests
- `config_dir` to default configuration

### Fixed
- Version consistency across modules (all aligned to 3.2.0)
- Format configuration edge cases
- Directory security checks during ingestion
- Safe temporary file uploads via API
- Recursive ingestion for nested directories
- Unified chunking strategy (consistent across CLI and API)
- Chunk ID collision prevention

## [v3.0.2] — 2026-05-25

### Fixed
- ChromaDB lazy import — no crash when `[semantic]` extras not installed
- DOCX error handling for malformed files
- Pytest skipif checks for optional dependencies

## [v3.0.1] — 2026-05-25

### Added
- Hugging Face Space with Gradio web app
- Space requirements and frontmatter for deployment

## [v3.0.0] — 2026-05-24

### Added
- JSON and YAML ingestion with recursive key-value extraction
- EPUB support via `ebooklib` (requires `[semantic]` extras)
- Embedding model caching — single-process reuse across commands
- `zaza server` CLI alias (same as `zaza api`)
- Multilingual embedding model: `paraphrase-multilingual-MiniLM-L12-v2` (50+ languages)
- Full test suite — 57/57 tests passing

### Changed
- REST API: added `pydantic` to `[api]` dependencies
- CI workflow added (GitHub Actions, Python 3.10/3.11/3.12)
- Improved HF Space integration

## [v2.1] — 2026-05-23

### Added
- Extended format support: HTML (via BeautifulSoup), XML, DOCX (via python-docx)
- REST API server (`zaza api`) with endpoints: `/health`, `/search`, `/search-semantic`, `/analyze`, `/ingest/file`, `/ingest/directory`

## [v2.0.0] — 2026-05-22

### Added
- Complete rewrite from v1 monolith
- Real semantic search pipeline with `sentence-transformers` + `ChromaDB`
- Multi-format ingestion: TXT, PDF, Markdown, CSV
- CLI tool: `zaza ingest`, `zaza search`, `zaza search-semantic`, `zaza stats`, `zaza documents`
- Local-first architecture — no API keys, no data leaves your machine
- Configuration via `config.yaml`
