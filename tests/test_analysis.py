"""Tests for analysis module."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from zaza.analysis import analyze_text, STOP_WORDS


def test_analyze_empty():
    result = analyze_text("")
    assert result["word_count"] == 0
    assert result["lexical_density"] == 0.0


def test_analyze_basic():
    text = "Hello world hello python world hello"
    result = analyze_text(text, stop_words_lang="en")
    assert result["word_count"] > 0
    assert result["unique_words"] > 0
    assert result["lexical_density"] > 0
    assert result["lexical_density"] <= 1.0


def test_analyze_french():
    text = "Le chat est sur la table et le chien est dans le jardin"
    result = analyze_text(text, stop_words_lang="fr")
    assert result["word_count"] > 0
    # Should filter stop words like "le", "est", "sur", "la", "et", "dans"
    assert result["unique_words"] < result["word_count"]


def test_analyze_top_words():
    text = "python python python java java python c c c c"
    result = analyze_text(text, top_words=5, min_word_length=1, stop_words_lang="en")
    top = result["top_words"]
    assert len(top) <= 5
    assert top[0]["word"] == "python"
    assert top[0]["count"] == 4


def test_analyze_min_word_length():
    text = "a ab abc abcd abcde"
    result = analyze_text(text, min_word_length=4, stop_words_lang="en")
    meaningful_words = result["word_count"]  # This counts all clean words
    # Words with >= 4 chars: abcd, abcde
    assert result["avg_word_length"] >= 4


def test_analyze_long_text():
    """Test with a realistic paragraph."""
    text = """
    La programmation est un art. La programmation requiert de la patience.
    Un bon programmeur écrit du code propre et testé.
    Le testing est essentiel pour la qualité du logiciel.
    """
    result = analyze_text(text, stop_words_lang="fr")
    assert result["word_count"] > 10
    assert result["sentence_count"] > 0
    assert len(result["top_words"]) > 0


def test_stop_words_filtered():
    text = "le le le un un un chat"
    result = analyze_text(text, stop_words_lang="fr")
    # "le" and "un" should be filtered, "chat" remains
    top_words = [w["word"] for w in result["top_words"]]
    assert "le" not in top_words
    assert "un" not in top_words
