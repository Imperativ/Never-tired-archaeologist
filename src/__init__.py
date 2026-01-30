"""
Never-Tired-Archaeologist: Semantic Document Analysis Tool

A local Python tool for semantic document analysis using:
- SQLite for data storage
- Anthropic Claude for metadata extraction
- Sentence-Transformers for local embeddings (CPU-optimized)
"""

from .models import DocumentMetadata
from .database import DocDatabase
from .embedder import LocalEmbedder
from .llm import Analyzer

__version__ = "2.0.0"
__all__ = ["DocumentMetadata", "DocDatabase", "LocalEmbedder", "Analyzer"]
