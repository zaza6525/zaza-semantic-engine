#!/usr/bin/env python3
"""CLI wrapper for semantic search — designed to be called by Hermes Agent.

Usage:
    zaza search-docs "query text" [--top 5]
    python -m zaza.search_docs "query text" [--top 5]

Returns structured JSON output suitable for LLM processing.
"""

import sys
import json
import argparse

from zaza.engine import SemanticEngine


def main():
    parser = argparse.ArgumentParser(description="Semantic search in ingested documents")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--top", "-n", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")
    parser.add_argument("--engine-dir", default=None, help="Engine data directory")
    args = parser.parse_args()

    try:
        engine = SemanticEngine(config_path=args.engine_dir) if args.engine_dir else SemanticEngine()
        results = engine.search_semantic(args.query, n_results=args.top)

        if args.as_json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            if not results:
                print(f"No results for: {args.query}")
                return
            for i, r in enumerate(results, 1):
                print(f"#{i} [{r.get('filename', '?')}] (score: {r.get('score', 0):.2f})")
                print(f"    {r.get('excerpt', '')}")
                print(f"    Filetype: {r.get('filetype', '?')}, Chunk: {r.get('chunk_index', 0)}/{r.get('total_chunks', 1)}")
                print()
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
