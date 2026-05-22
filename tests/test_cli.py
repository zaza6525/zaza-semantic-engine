"""Tests for CLI."""

import sys
import os
import tempfile
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from zaza.cli import build_parser


def test_parser_has_commands():
    parser = build_parser()
    # Check that subparsers exist
    assert parser._subparsers is not None


def test_parser_help(capsys):
    parser = build_parser()
    try:
        parser.parse_args(["--help"])
    except SystemExit:
        pass  # --help calls sys.exit


def test_parser_ingest_command():
    parser = build_parser()
    args = parser.parse_args(["ingest", "/tmp/test"])
    assert args.command == "ingest"
    assert args.directory == "/tmp/test"


def test_parser_report_command():
    parser = build_parser()
    args = parser.parse_args(["report"])
    assert args.command == "report"


def test_parser_stats_command():
    parser = build_parser()
    args = parser.parse_args(["stats", "--json"])
    assert args.command == "stats"
    assert args.json is True


def test_parser_search_command():
    parser = build_parser()
    args = parser.parse_args(["search", "test"])
    assert args.command == "search"
    assert args.query == "test"
