"""
SQLite database management for document storage and retrieval.
"""

import sqlite3
import hashlib
import json
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime

from .models import DocumentMetadata


class DocDatabase:
    """
    Manages SQLite database for document storage with embeddings and metadata.

    Schema:
        - documents: Main table storing document content, hash, and metadata
        - embeddings: Stored as JSON array in the documents table
    """

    def __init__(self, db_path: str = "archaeologist.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self.init_db()

    def _connect(self) -> None:
        """Establish database connection."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to connect to database: {e}")

    def init_db(self) -> None:
        """
        Create database tables if they don't exist.

        Tables:
            documents:
                - id: Primary key
                - content_hash: SHA256 hash for duplicate detection
                - content: Full document text
                - metadata_json: JSON string of DocumentMetadata
                - embedding_json: JSON array of embedding vector
                - created_at: Timestamp of insertion
        """
        if not self.conn:
            raise RuntimeError("Database connection not established")

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_hash TEXT UNIQUE NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    embedding_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create index on content_hash for fast duplicate lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_content_hash
                ON documents(content_hash)
            """)

            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to initialize database: {e}")

    def _compute_hash(self, content: str) -> str:
        """
        Compute SHA256 hash of document content.

        Args:
            content: Document text

        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def document_exists(self, content_hash: str) -> bool:
        """
        Check if document already exists in database.

        Args:
            content_hash: SHA256 hash of document content

        Returns:
            True if document exists, False otherwise
        """
        if not self.conn:
            raise RuntimeError("Database connection not established")

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT 1 FROM documents WHERE content_hash = ? LIMIT 1",
                (content_hash,)
            )
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to check document existence: {e}")

    def add_document(
        self,
        content: str,
        metadata: DocumentMetadata,
        embedding: Optional[List[float]] = None
    ) -> int:
        """
        Add new document to database.

        Args:
            content: Full document text
            metadata: Extracted metadata (Pydantic model)
            embedding: Optional embedding vector

        Returns:
            Document ID of inserted record

        Raises:
            ValueError: If document already exists
            RuntimeError: On database errors
        """
        if not self.conn:
            raise RuntimeError("Database connection not established")

        content_hash = self._compute_hash(content)

        # Check for duplicates
        if self.document_exists(content_hash):
            raise ValueError(f"Document with hash {content_hash[:16]}... already exists")

        try:
            cursor = self.conn.cursor()

            # Convert metadata to JSON
            metadata_json = metadata.model_dump_json()

            # Convert embedding to JSON if provided
            embedding_json = json.dumps(embedding) if embedding else None

            cursor.execute("""
                INSERT INTO documents (content_hash, content, metadata_json, embedding_json)
                VALUES (?, ?, ?, ?)
            """, (content_hash, content, metadata_json, embedding_json))

            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to add document: {e}")

    def get_document(self, doc_id: int) -> Optional[Tuple[str, DocumentMetadata, Optional[List[float]]]]:
        """
        Retrieve document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Tuple of (content, metadata, embedding) or None if not found
        """
        if not self.conn:
            raise RuntimeError("Database connection not established")

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT content, metadata_json, embedding_json FROM documents WHERE id = ?",
                (doc_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            content = row[0]
            metadata = DocumentMetadata.model_validate_json(row[1])
            embedding = json.loads(row[2]) if row[2] else None

            return (content, metadata, embedding)
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to retrieve document: {e}")

    def get_all_documents(self) -> List[Tuple[int, str, DocumentMetadata]]:
        """
        Retrieve all documents (ID, content, metadata).

        Returns:
            List of tuples (id, content, metadata)
        """
        if not self.conn:
            raise RuntimeError("Database connection not established")

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, content, metadata_json FROM documents")

            results = []
            for row in cursor.fetchall():
                doc_id = row[0]
                content = row[1]
                metadata = DocumentMetadata.model_validate_json(row[2])
                results.append((doc_id, content, metadata))

            return results
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to retrieve documents: {e}")

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures connection is closed."""
        self.close()
