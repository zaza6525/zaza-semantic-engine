# Contributing to Zaza Semantic Engine

Thanks for wanting to contribute! This project is local-first and privacy-respecting — all contributions should follow the same principle.

## Quick Start

### 1. Fork and clone

```bash
gh repo fork zaza6525/zaza-semantic-engine
git clone <your-fork-url>
cd zaza-semantic-engine
```

### 2. Set up your environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[all,dev]"
```

### 3. Run tests

```bash
pytest -v --tb=short
```

All tests must pass before opening a PR. The CI runs on Python 3.10, 3.11, and 3.12 — your code should work on all three.

### 4. Make your changes

- Follow PEP 8 for Python code.
- Add type hints where they make sense.
- Add tests for new features — use the existing `tests/` as templates.
- Update the README if you change CLI commands or API endpoints.
- Update the CHANGELOG.md under an `## [Unreleased]` section.

### 5. Submit a Pull Request

- Use a descriptive title: `feat: add support for RTF files` or `fix: handle empty DOCX gracefully`
- Reference any related issues.
- Keep PRs focused — one feature or one fix per PR.

## Project structure

```
src/zaza/          # Core engine modules
tests/             # Unit tests
.github/workflows/ # CI
config.yaml        # Default configuration
README.md          # User documentation
```

## Reporting bugs

Use the [GitHub Issues](https://github.com/zaza6525/zaza-semantic-engine/issues) with:

- Python version
- OS (Linux, macOS, Windows)
- Steps to reproduce
- Expected vs actual behavior
- Relevant log output

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Be respectful, constructive, and assume good faith.

## Questions?

Open a Discussion or an Issue — happy to help.
