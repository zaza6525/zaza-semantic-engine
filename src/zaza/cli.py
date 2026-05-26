"""Command-line interface for ZAZA Semantic Engine."""

import argparse
import sys
import json
from pathlib import Path

from zaza.engine import SemanticEngine
from zaza.config import load_config


def cmd_ingest(args):
    """Handle the ingest command."""
    engine = SemanticEngine(args.config)
    
    target = args.directory or args.file
    if args.file and Path(args.file).is_file():
        print(f"  Ingesting single file: {args.file}")
        result = engine.ingest_file(args.file)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"  Scanning directory: {target}")
        recursive = getattr(args, 'recursive', False)
        results = engine.ingest_directory(target, recursive=recursive)
        if results:
            print(json.dumps(results, indent=2, ensure_ascii=False))


def cmd_report(args):
    """Handle the report command."""
    engine = SemanticEngine(args.config)
    summary, documents = engine.generate_reports(args.format)
    
    if args.text:
        from zaza.reporting import Reporter
        r = Reporter()
        print(r.format_summary_text(summary))
        if documents:
            print()
            print(r.format_documents_text(documents))
    else:
        print(json.dumps(summary, indent=2, ensure_ascii=False))


def cmd_stats(args):
    """Handle the stats command."""
    engine = SemanticEngine(args.config)
    summary = engine.get_summary()
    
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        from zaza.reporting import Reporter
        r = Reporter()
        print(r.format_summary_text(summary))


def cmd_documents(args):
    """Handle the documents command."""
    engine = SemanticEngine(args.config)
    
    if args.search:
        docs = engine.search(args.search)
        print(f"  🔍 Search results for '{args.search}':")
    else:
        docs = engine.get_documents()
        print(f"  📄 All documents:")
    
    if docs:
        from zaza.reporting import Reporter
        r = Reporter()
        print(r.format_documents_text(docs))
    else:
        print("  No documents found.")


def cmd_search(args):
    """Handle the search command."""
    engine = SemanticEngine(args.config)
    docs = engine.search(args.query)
    
    if docs:
        from zaza.reporting import Reporter
        r = Reporter()
        print(f"  🔍 Found {len(docs)} document(s) matching '{args.query}':")
        print(r.format_documents_text(docs))
    else:
        print(f"  No documents matching '{args.query}'.")


def cmd_search_semantic(args):
    """Handle the semantic search command."""
    engine = SemanticEngine(args.config)
    docs = engine.search_semantic(args.query, n_results=args.top)
    
    if docs:
        print(f"  🔍 Semantic search results for '{args.query}':")
        for i, doc in enumerate(docs, 1):
            score = doc.get("score", 0)
            doc_id = doc.get("id", "")
            preview = doc.get("document", "")[:200]
            print(f"  {i}. (score: {score:.3f}) [{doc_id}]")
            print(f"     {preview}")
            print()
    else:
        print(f"  No semantic matches for '{args.query}'.")


def cmd_api(args):
    """Handle the api command - start the FastAPI server."""
    try:
        import uvicorn
    except ImportError:
        print("  uvicorn is required for API mode. Install: pip install uvicorn")
        sys.exit(1)
    
    from zaza.api import app
    print(f"  🌐 Starting ZAZA API server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)


def cmd_server(args):
    """Handle the server command - alias for 'api'."""
    cmd_api(args)



def build_parser():
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="zaza",
        description="ZAZA Semantic Engine — Multi-format document analysis"
    )
    parser.add_argument("-c", "--config", help="Path to config.yaml")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # ingest
    p_ingest = subparsers.add_parser("ingest", help="Ingest files from directory")
    p_ingest.add_argument("directory", nargs="?", default=None, help="Directory to scan")
    p_ingest.add_argument("-f", "--file", help="Single file to ingest")
    p_ingest.add_argument("-r", "--recursive", action="store_true", help="Scan directories recursively")
    p_ingest.set_defaults(func=cmd_ingest)
    
    # report
    p_report = subparsers.add_parser("report", help="Generate analysis report")
    p_report.add_argument("--format", nargs="+", default=["json", "csv"], help="Output formats")
    p_report.add_argument("--text", action="store_true", help="Text format output")
    p_report.set_defaults(func=cmd_report)
    
    # stats
    p_stats = subparsers.add_parser("stats", help="Show analysis statistics")
    p_stats.add_argument("--json", action="store_true", help="JSON output")
    p_stats.set_defaults(func=cmd_stats)
    
    # documents
    p_docs = subparsers.add_parser("documents", help="List ingested documents")
    p_docs.add_argument("--search", help="Filter by filename")
    p_docs.set_defaults(func=cmd_documents)
    
    # search
    p_search = subparsers.add_parser("search", help="Search documents by name")
    p_search.add_argument("query", help="Search query")
    p_search.set_defaults(func=cmd_search)
    
    # search-semantic
    p_search_sem = subparsers.add_parser("search-semantic", help="Semantic search using embeddings")
    p_search_sem.add_argument("query", help="Search query")
    p_search_sem.add_argument("--top", type=int, default=10, help="Number of results (default: 10)")
    p_search_sem.set_defaults(func=cmd_search_semantic)
    
    # api
    p_api = subparsers.add_parser("api", help="Start the REST API server")
    p_api.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    p_api.add_argument("--port", type=int, default=8000, help="Port to bind to")
    p_api.set_defaults(func=cmd_api)
    
    # server (alias for api)
    p_server = subparsers.add_parser("server", help="Start the REST API server (alias for 'api')")
    p_server.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    p_server.add_argument("--port", type=int, default=8000, help="Port to bind to")
    p_server.set_defaults(func=cmd_server)
    
    return parser


def main():
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    args.func(args)


if __name__ == "__main__":
    main()
