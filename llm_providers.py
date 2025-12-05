# -*- coding: utf-8 -*-
"""
Multi-provider LLM module for Never-tired-archaeologist.
Supports Claude (Anthropic) and Gemini (Google) APIs.

Based on research dated Dec 2025:
- Claude: Haiku 4.5, Sonnet 4.5, Opus 4.5
- Gemini: 3.0 Pro, 2.5 Flash, embedding-001
"""
import os
import time
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
from datetime import datetime, timedelta


class LLMProviderError(Exception):
    """Base exception for LLM provider errors"""
    pass


class RateLimitError(LLMProviderError):
    """Raised when rate limit is exceeded"""
    pass


class AnalysisProvider(ABC):
    """Abstract base class for text analysis providers"""

    @abstractmethod
    def analyze_text(
        self,
        text: str,
        filename: str,
        source_extension: str,
        source_type: str
    ) -> Dict[str, Any]:
        """
        Analyze text and extract metadata.

        Returns:
            Dict with keys: language, topic, keywords, summary,
                          is_prompt, is_llm_output, git_project, confidence
        """
        pass


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""

    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        pass

    @abstractmethod
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        pass


class ClaudeProvider(AnalysisProvider):
    """
    Anthropic Claude API provider for text analysis.
    Uses Haiku 4.5 by default for cost-efficiency.
    """

    # Metadata extraction schema for Claude Tool Use
    METADATA_SCHEMA = {
        "name": "extract_metadata",
        "description": "Extracts structured metadata from a document.",
        "input_schema": {
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "description": "ISO 639-1 language code (e.g., 'de', 'en', 'fr')"
                },
                "topic": {
                    "type": "string",
                    "description": "Main topic in 3-5 keywords"
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 10,
                    "description": "Key entities or concepts"
                },
                "summary": {
                    "type": "string",
                    "description": "Concise summary (max 3 sentences)"
                },
                "content_type": {
                    "type": "string",
                    "enum": [
                        "system_prompt",
                        "llm_output",
                        "code",
                        "documentation",
                        "email",
                        "notes",
                        "other"
                    ],
                    "description": "Classification of content type"
                },
                "is_prompt": {
                    "type": "boolean",
                    "description": "Is this a system prompt or instruction?"
                },
                "is_llm_output": {
                    "type": "boolean",
                    "description": "Is this output from an LLM?"
                },
                "git_project": {
                    "type": "string",
                    "description": "Related git project name (or empty string)"
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Confidence score of analysis"
                }
            },
            "required": [
                "language", "topic", "keywords", "summary",
                "content_type", "is_prompt", "is_llm_output",
                "git_project", "confidence"
            ]
        }
    }

    SYSTEM_PROMPT = """You are a precise document analyst for the 'Never-tired-archaeologist' system.
Your task is to extract metadata from unstructured texts.
Analyze the content, context, and technical nature of the document.

Guidelines:
- Detect the primary language (ISO 639-1 code)
- Identify the main topic concisely
- Extract meaningful keywords (avoid generic terms)
- Classify content type accurately
- Determine if text is a prompt, LLM output, code, documentation, etc.
- If the document references a git project, extract its name
- Provide a confidence score (0.0-1.0) for your analysis
"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-haiku-latest"
    ):
        """
        Initialize Claude provider.

        Args:
            api_key: Anthropic API key (or from ANTHROPIC_API_KEY env var)
            model: Claude model to use (default: Haiku 4.5)
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise LLMProviderError(
                "anthropic package not installed. Run: pip install anthropic"
            )

        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise LLMProviderError(
                "ANTHROPIC_API_KEY not found in environment or parameters"
            )

        self.client = Anthropic(api_key=self.api_key)
        self.model = model

    def analyze_text(
        self,
        text: str,
        filename: str,
        source_extension: str,
        source_type: str
    ) -> Dict[str, Any]:
        """
        Analyze text using Claude with structured output via Tool Use.

        Args:
            text: Document text content
            filename: Original filename
            source_extension: File extension (.txt, .py, etc.)
            source_type: File type classification

        Returns:
            Metadata dictionary
        """
        try:
            # Truncate text if too long (Claude context limit)
            max_chars = 100000  # ~25k tokens
            truncated_text = text[:max_chars]
            if len(text) > max_chars:
                truncated_text += "\n\n[... text truncated ...]"

            user_prompt = f"""Analyze the following document:

Filename: {filename}
Extension: {source_extension}
Type: {source_type}

Content:
{truncated_text}
"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
                tools=[self.METADATA_SCHEMA],
                tool_choice={"type": "tool", "name": "extract_metadata"}
            )

            # Extract structured data from tool use
            for content in response.content:
                if content.type == 'tool_use' and content.name == 'extract_metadata':
                    metadata = content.input

                    # Ensure all required fields exist
                    return {
                        'language': metadata.get('language', ''),
                        'topic': metadata.get('topic', ''),
                        'keywords': metadata.get('keywords', []),
                        'summary': metadata.get('summary', ''),
                        'is_prompt': bool(metadata.get('is_prompt', False)),
                        'is_llm_output': bool(metadata.get('is_llm_output', False)),
                        'git_project': metadata.get('git_project', ''),
                        'confidence': float(metadata.get('confidence', 0.0))
                    }

            # Fallback if no tool use found (shouldn't happen with tool_choice)
            raise LLMProviderError("No structured output received from Claude")

        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(f"Claude rate limit exceeded: {e}")
            raise LLMProviderError(f"Claude analysis failed: {e}")


class GeminiProvider(EmbeddingProvider):
    """
    Google Gemini API provider for embeddings.
    Uses gemini-embedding-001 model.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-embedding-001",
        dimensions: int = 768
    ):
        """
        Initialize Gemini provider.

        Args:
            api_key: Google API key (or from GOOGLE_API_KEY env var)
            model: Embedding model name
            dimensions: Output dimensionality (128-768 for MRL support)
        """
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            raise LLMProviderError(
                "google-genai package not installed. Run: pip install google-genai"
            )

        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise LLMProviderError(
                "GOOGLE_API_KEY or GEMINI_API_KEY not found in environment"
            )

        self.genai = genai
        self.types = types
        self.client = genai.Client(api_key=self.api_key)
        self.model = f"models/{model}" if not model.startswith("models/") else model
        self.dimensions = dimensions

        # Rate limiting state (Free tier: 15 RPM, 1.5M tokens/day)
        self._requests_this_minute = 0
        self._tokens_today = 0
        self._minute_start = datetime.now()
        self._day_start = datetime.now()
        self._rpm_limit = 15
        self._daily_token_limit = 1_500_000

    def _wait_if_needed(self, estimated_tokens: int = 2000):
        """
        Rate limiting implementation for Gemini Free Tier.

        Args:
            estimated_tokens: Estimated tokens for this request
        """
        now = datetime.now()

        # Reset minute counter
        if (now - self._minute_start) > timedelta(minutes=1):
            self._requests_this_minute = 0
            self._minute_start = now

        # Reset day counter
        if (now - self._day_start) > timedelta(days=1):
            self._tokens_today = 0
            self._day_start = now

        # Check RPM limit
        if self._requests_this_minute >= self._rpm_limit:
            sleep_time = 60 - (now - self._minute_start).seconds
            if sleep_time > 0:
                time.sleep(sleep_time)
            self._requests_this_minute = 0
            self._minute_start = datetime.now()

        # Check daily token limit
        if self._tokens_today + estimated_tokens > self._daily_token_limit:
            raise RateLimitError(
                f"Gemini daily token limit reached ({self._daily_token_limit}). "
                "Switch to paid tier or use local embeddings."
            )

        self._requests_this_minute += 1
        self._tokens_today += estimated_tokens

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed (max ~8000 tokens)

        Returns:
            Embedding vector (list of floats)
        """
        # Truncate if too long
        max_chars = 30000  # ~8k tokens
        truncated = text[:max_chars]

        self._wait_if_needed(estimated_tokens=len(truncated.split()))

        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=[truncated],
                config=self.types.EmbedContentConfig(
                    task_type="retrieval_document",
                    output_dimensionality=self.dimensions
                )
            )

            return response.embeddings[0].values

        except Exception as e:
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                raise RateLimitError(f"Gemini rate/quota limit: {e}")
            raise LLMProviderError(f"Gemini embedding failed: {e}")

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        embeddings = []
        batch_size = 100  # Gemini allows up to 100 per request

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            truncated_batch = [t[:30000] for t in batch]

            # Estimate tokens for rate limiting
            total_tokens = sum(len(t.split()) for t in truncated_batch)
            self._wait_if_needed(estimated_tokens=total_tokens)

            try:
                response = self.client.models.embed_content(
                    model=self.model,
                    contents=truncated_batch,
                    config=self.types.EmbedContentConfig(
                        task_type="retrieval_document",
                        output_dimensionality=self.dimensions
                    )
                )

                batch_embeddings = [emb.values for emb in response.embeddings]
                embeddings.extend(batch_embeddings)

            except Exception as e:
                if "quota" in str(e).lower() or "limit" in str(e).lower():
                    raise RateLimitError(f"Gemini rate/quota limit: {e}")
                raise LLMProviderError(f"Gemini batch embedding failed: {e}")

        return embeddings


class MultiProvider:
    """
    Unified interface for multiple LLM providers.
    Combines Claude for analysis and Gemini for embeddings.
    """

    def __init__(
        self,
        analysis_provider: Optional[AnalysisProvider] = None,
        embedding_provider: Optional[EmbeddingProvider] = None
    ):
        """
        Initialize multi-provider.

        Args:
            analysis_provider: Provider for text analysis (default: Claude Haiku 4.5)
            embedding_provider: Provider for embeddings (default: Gemini)
        """
        self.analysis_provider = analysis_provider or ClaudeProvider()
        self.embedding_provider = embedding_provider or GeminiProvider()

    def analyze_document(
        self,
        text: str,
        filename: str,
        source_extension: str,
        source_type: str,
        generate_embedding: bool = True
    ) -> Tuple[Dict[str, Any], Optional[List[float]]]:
        """
        Analyze document with metadata extraction and optional embedding.

        Args:
            text: Document text
            filename: Original filename
            source_extension: File extension
            source_type: File type
            generate_embedding: Whether to generate embedding vector

        Returns:
            Tuple of (metadata_dict, embedding_vector or None)
        """
        # Get metadata from analysis provider
        metadata = self.analysis_provider.analyze_text(
            text=text,
            filename=filename,
            source_extension=source_extension,
            source_type=source_type
        )

        # Optionally generate embedding
        embedding = None
        if generate_embedding:
            try:
                embedding = self.embedding_provider.generate_embedding(text)
            except RateLimitError:
                # If rate limited, continue without embedding
                # Can be generated later
                pass

        return metadata, embedding


def get_default_provider() -> MultiProvider:
    """
    Get default multi-provider instance.
    Uses Claude Haiku 4.5 + Gemini Embedding-001.
    """
    return MultiProvider()
