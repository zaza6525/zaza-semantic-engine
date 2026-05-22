"""Semantic analysis engine."""

from collections import Counter
from typing import List, Dict, Tuple


# Simple stop words for French and English
STOP_WORDS = {
    "fr": {
        "au", "aux", "avec", "ce", "ces", "dans", "de", "des", "du", "elle", "en",
        "et", "etant", "eu", "il", "ils", "je", "juste", "la", "le", "les", "leur",
        "lui", "ma", "mais", "me", "mes", "mon", "ne", "nos", "notre", "nous", "on",
        "ou", "par", "pas", "pour", "qu", "que", "qui", "sa", "se", "ses", "son",
        "sur", "ta", "te", "tes", "toi", "ton", "tu", "un", "une", "vos", "votre",
        "vous", "c", "d", "j", "l", "m", "n", "s", "t", "y", "est", "sont", "was",
        "been", "has", "have", "had", "a", "i", "it", "at", "be", "this", "that",
        "were", "are", "been", "being",
    },
    "en": {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of",
        "with", "by", "from", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "shall", "should",
        "can", "could", "may", "might", "must", "this", "that", "these", "those",
        "i", "you", "he", "she", "it", "we", "they", "what", "which", "who", "whom",
        "if", "then", "than", "so", "as", "about", "up", "out", "into", "through",
    },
}


def analyze_text(content: str, top_words: int = 20, min_word_length: int = 3,
                 stop_words_lang: str = "fr") -> Dict:
    """Perform semantic analysis on text content.
    
    Returns a dict with metrics and extracted data.
    """
    if not content or not content.strip():
        return {
            "word_count": 0,
            "char_count": 0,
            "sentence_count": 0,
            "unique_words": 0,
            "lexical_density": 0.0,
            "top_words": [],
            "avg_word_length": 0.0,
            "readability": {},
        }
    
    # Basic metrics
    words = content.split()
    chars = len(content)
    sentences = len([s for s in content.replace('\n', ' ').split('.') 
                     if s.strip()])
    
    # Clean words for analysis
    import re
    clean_words = re.findall(r'[a-zA-Z\u00C0-\u024F\u0400-\u04FF]+', content.lower())
    
    # Filter by min length
    filtered_words = [w for w in clean_words if len(w) >= min_word_length]
    
    # Stop words
    sw = STOP_WORDS.get(stop_words_lang, STOP_WORDS["en"])
    meaningful = [w for w in filtered_words if w not in sw]
    
    # Word frequency
    word_counts = Counter(meaningful)
    top = word_counts.most_common(top_words)
    
    # Lexical density
    density = round(len(set(meaningful)) / max(len(meaningful), 1), 4)
    
    # Average word length
    avg_len = round(sum(len(w) for w in meaningful) / max(len(meaningful), 1), 2)
    
    return {
        "word_count": len(clean_words),
        "char_count": chars,
        "sentence_count": max(sentences, 1),
        "unique_words": len(set(meaningful)),
        "lexical_density": density,
        "top_words": [{"word": w, "count": c} for w, c in top],
        "avg_word_length": avg_len,
        "readability": {
            "words_per_sentence": round(len(meaningful) / max(sentences, 1), 2),
        },
    }
