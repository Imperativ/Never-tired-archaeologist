"""
LLM-based document analysis using Anthropic Claude.
"""

import logging
import os
from typing import Optional
from anthropic import Anthropic
from dotenv import load_dotenv

from .models import DocumentMetadata


logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class Analyzer:
    """
    Document analyzer using Anthropic Claude API.

    Extracts structured metadata from document text using LLM analysis.
    Uses Pydantic models for guaranteed structured output.
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        api_key: Optional[str] = None
    ):
        """
        Initialize Claude API client.

        Args:
            model: Claude model identifier (default: claude-sonnet-4-20250514)
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)

        Raises:
            ValueError: If API key is not provided or found in environment
        """
        self.model = model

        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. "
                "Provide via parameter or set ANTHROPIC_API_KEY environment variable."
            )

        try:
            self.client = Anthropic(api_key=self.api_key)
            logger.info(f"Claude API client initialized with model: {model}")
        except Exception as e:
            logger.error(f"Failed to initialize Claude client: {e}")
            raise RuntimeError(f"Could not initialize Claude API client: {e}")

    def analyze_text(self, text: str) -> DocumentMetadata:
        """
        Analyze document text and extract structured metadata.

        Args:
            text: Document content to analyze

        Returns:
            DocumentMetadata object with extracted information

        Raises:
            ValueError: If text is empty
            RuntimeError: If API call fails or response is invalid
        """
        if not text or not text.strip():
            raise ValueError("Cannot analyze empty text")

        # Truncate very long texts (Claude has context limits)
        max_chars = 100000  # ~25k tokens safety margin
        if len(text) > max_chars:
            logger.warning(f"Text truncated from {len(text)} to {max_chars} characters")
            text = text[:max_chars] + "\n\n[... text truncated ...]"

        system_prompt = """Du bist ein präziser Dokumenten-Archivar.
Deine Aufgabe ist es, Metadaten aus Dokumenten zu extrahieren und im strukturierten JSON-Format zurückzugeben.

Extrahiere folgende Informationen:
- title: Der Haupttitel oder das Hauptthema des Dokuments
- language: ISO 639-1 Sprachcode (z.B. 'en', 'de', 'fr')
- topics: Liste der Hauptthemen/Kategorien
- summary: Eine prägnante Zusammenfassung des Inhalts (2-3 Sätze)
- keywords: Liste wichtiger Schlüsselbegriffe und Konzepte

Sei präzise und objektiv. Verwende nur Informationen, die im Dokument vorhanden sind."""

        user_prompt = f"""Analysiere das folgende Dokument und extrahiere die Metadaten:

<document>
{text}
</document>

Gib die Metadaten im korrekten JSON-Format zurück."""

        try:
            logger.info("Sending analysis request to Claude API...")

            # Use Claude's structured output with response_model
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            # Extract text response
            response_text = response.content[0].text

            logger.info("Received response from Claude API")
            logger.debug(f"Raw response: {response_text}")

            # Parse response as DocumentMetadata
            try:
                # Try to extract JSON from markdown code blocks if present
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(1)
                else:
                    # Try to find JSON object directly
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        json_text = json_match.group(0)
                    else:
                        json_text = response_text

                metadata = DocumentMetadata.model_validate_json(json_text)
                logger.info(f"Successfully extracted metadata: {metadata.title}")
                return metadata

            except Exception as parse_error:
                logger.error(f"Failed to parse Claude response as DocumentMetadata: {parse_error}")
                logger.error(f"Response was: {response_text}")
                raise RuntimeError(
                    f"Claude response could not be parsed as valid metadata: {parse_error}"
                )

        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise RuntimeError(f"Document analysis failed: {e}")

    def get_model_info(self) -> dict:
        """
        Get information about the current model configuration.

        Returns:
            Dictionary with model name and other settings
        """
        return {
            "model": self.model,
            "provider": "Anthropic Claude"
        }
