"""Reporting and output generation."""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class Reporter:
    """Generate reports in various formats."""
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def summary_report(self, summary: dict) -> dict:
        """Create a summary report from database stats."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": summary,
        }
        return report
    
    def document_report(self, documents: List[Dict]) -> dict:
        """Create a report for individual documents."""
        return {
            "generated_at": datetime.now().isoformat(),
            "document_count": len(documents),
            "documents": documents,
        }
    
    def save_json(self, report: dict, filename=None):
        """Save report as JSON."""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = self.output_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return path
    
    def save_csv(self, documents: List[Dict], filename=None):
        """Save documents as CSV."""
        if filename is None:
            filename = f"documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path = self.output_dir / filename
        
        if not documents:
            path.write_text("No documents to export\n")
            return path
        
        fieldnames = list(documents[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for doc in documents:
                writer.writerow(doc)
        return path
    
    def format_summary_text(self, summary: dict) -> str:
        """Format summary as human-readable text."""
        lines = [
            "═══ ZAZA Semantic Engine — Summary ═══",
            f"  Documents analyzed : {summary.get('total_documents', 0)}",
            f"  Total words        : {summary.get('total_words', 0):,}",
            f"  Total characters   : {summary.get('total_characters', 0):,}",
            f"  Avg lexical density: {summary.get('average_lexical_density', 0):.4f}",
            f"  First analysis     : {summary.get('first_ingestion', 'N/A')}",
            f"  Last analysis      : {summary.get('last_ingestion', 'N/A')}",
        ]
        return "\n".join(lines)
    
    def format_documents_text(self, documents: List[Dict]) -> str:
        """Format documents list as human-readable text."""
        if not documents:
            return "  No documents found."
        
        lines = ["═══ ZAZA Semantic Engine — Documents ═══"]
        for doc in documents:
            lines.append(f"  • {doc.get('filename', '?')} ({doc.get('filetype', '?')})")
            lines.append(f"    Words: {doc.get('word_count', 0):,} | Unique: {doc.get('unique_words', 0)} | Density: {doc.get('lexical_density', 0):.4f}")
            lines.append(f"    Ingested: {doc.get('ingested_at', '?')}")
        return "\n".join(lines)
