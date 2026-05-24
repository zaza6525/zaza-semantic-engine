"""Configuration loader."""

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import List


@dataclass
class DatabaseConfig:
    path: str = "./data/zaza.db"


@dataclass
class IngestionConfig:
    data_dir: str = "./data"
    extensions: List[str] = field(default_factory=lambda: [".txt", ".pdf", ".csv", ".md"])
    encoding: str = "utf-8"
    fallback_encoding: str = "latin-1"


@dataclass
class AnalysisConfig:
    top_words: int = 20
    min_word_length: int = 3
    stop_words_language: str = "fr"


@dataclass
class OutputConfig:
    dir: str = "./output"
    formats: List[str] = field(default_factory=lambda: ["json", "csv"])


@dataclass
class SemanticConfig:
    enabled: bool = True
    model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embed_dir: str = "./data/embeddings"
    max_search_results: int = 10


@dataclass
class Config:
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ingestion: IngestionConfig = field(default_factory=IngestionConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    semantic: SemanticConfig = field(default_factory=SemanticConfig)


DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"


def load_config(config_path=None) -> Config:
    """Load configuration from YAML file."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    
    if not path.exists():
        return Config()
    
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    if data is None:
        return Config()
    
    cfg = Config()
    
    if "database" in data:
        cfg.database = DatabaseConfig(**data["database"])
    if "ingestion" in data:
        cfg.ingestion = IngestionConfig(**data["ingestion"])
    if "analysis" in data:
        cfg.analysis = AnalysisConfig(**data["analysis"])
    if "output" in data:
        cfg.output = OutputConfig(**data["output"])
    
    return cfg
