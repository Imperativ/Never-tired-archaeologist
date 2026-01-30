"""
Local embedding generation using sentence-transformers (CPU-optimized).
"""

import logging
from typing import List, Optional
from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)


class LocalEmbedder:
    """
    Generates semantic embeddings using local sentence-transformers model.

    Uses 'all-MiniLM-L6-v2' model:
    - Lightweight (80MB)
    - Fast on CPU
    - 384-dimensional embeddings
    - Good balance of speed and quality
    """

    _instance: Optional['LocalEmbedder'] = None
    _model: Optional[SentenceTransformer] = None

    def __new__(cls):
        """Singleton pattern - ensure only one model instance is loaded."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding model.

        Args:
            model_name: HuggingFace model identifier
        """
        # Only initialize once (singleton pattern)
        if self._model is None:
            logger.info(f"Loading embedding model: {model_name}")
            try:
                self._model = SentenceTransformer(model_name)
                logger.info(f"Model loaded successfully. Embedding dimension: {self.get_embedding_dimension()}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise RuntimeError(f"Could not initialize embedding model: {e}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for input text.

        Args:
            text: Input text to embed

        Returns:
            List of float values representing the embedding vector

        Raises:
            ValueError: If text is empty
            RuntimeError: If model is not initialized
        """
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty text")

        if self._model is None:
            raise RuntimeError("Embedding model not initialized")

        try:
            # Generate embedding (returns numpy array)
            embedding = self._model.encode(text, convert_to_numpy=True)

            # Convert to Python list for JSON serialization
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise RuntimeError(f"Embedding generation failed: {e}")

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (more efficient than single calls).

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            ValueError: If texts list is empty
            RuntimeError: If model is not initialized
        """
        if not texts:
            raise ValueError("Cannot generate embeddings for empty text list")

        if self._model is None:
            raise RuntimeError("Embedding model not initialized")

        try:
            # Batch encoding is more efficient
            embeddings = self._model.encode(texts, convert_to_numpy=True)

            # Convert to list of lists
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise RuntimeError(f"Batch embedding generation failed: {e}")

    def get_embedding_dimension(self) -> int:
        """
        Get the dimensionality of the embedding vectors.

        Returns:
            Embedding dimension (e.g., 384 for all-MiniLM-L6-v2)
        """
        if self._model is None:
            raise RuntimeError("Embedding model not initialized")

        return self._model.get_sentence_embedding_dimension()

    def get_model_name(self) -> str:
        """
        Get the name of the loaded model.

        Returns:
            Model name/identifier
        """
        if self._model is None:
            raise RuntimeError("Embedding model not initialized")

        # Try to get model name from various attributes
        if hasattr(self._model, 'model_name'):
            return self._model.model_name
        elif hasattr(self._model, '_model_card_data'):
            return str(self._model._model_card_data.get('model_id', 'unknown'))
        else:
            return "all-MiniLM-L6-v2"  # default fallback
