"""
Pydantic models for document metadata extraction.
"""

from pydantic import BaseModel, Field
from typing import List


class DocumentMetadata(BaseModel):
    """
    Structured metadata extracted from documents via LLM analysis.

    Attributes:
        title: Document title or main topic
        language: ISO 639-1 language code (e.g., 'en', 'de')
        topics: List of main topics/themes identified
        summary: Concise summary of document content
        keywords: Key terms and concepts extracted
    """
    title: str = Field(..., description="Document title or main subject")
    language: str = Field(..., description="ISO 639-1 language code (e.g., 'en', 'de', 'fr')")
    topics: List[str] = Field(default_factory=list, description="Main topics/themes")
    summary: str = Field(..., description="Concise document summary")
    keywords: List[str] = Field(default_factory=list, description="Key terms and concepts")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Introduction to Machine Learning",
                "language": "en",
                "topics": ["artificial intelligence", "neural networks", "data science"],
                "summary": "An overview of fundamental machine learning concepts and algorithms.",
                "keywords": ["ML", "supervised learning", "training data", "model"]
            }
        }
