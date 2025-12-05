# -*- coding: utf-8 -*-
"""
SQLite database module for archaeologist.
Handles persistent storage of documents, metadata, and embeddings.
"""
import sqlite3
import json
import pickle
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from contextlib import contextmanager


class DatabaseError(Exception):
    """Base exception for database operations"""
    pass


class Database:
    """
    Manages SQLite database for document analysis results.

    Schema:
    - documents: Core document information
    - metadata: Extracted metadata (language, topic, keywords, etc.)
    - embeddings: Vector embeddings for similarity search
    - documents_fts: Full-text search index
    """

    def __init__(self, db_path: Path):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_schema()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise DatabaseError(f"Database operation failed: {e}") from e
        finally:
            conn.close()

    def _ensure_schema(self):
        """Create database schema if it doesn't exist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Main documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    filepath TEXT UNIQUE NOT NULL,
                    source_extension TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    original_text TEXT NOT NULL,
                    wordcount INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    processed_at TEXT NOT NULL,
                    UNIQUE(filepath)
                )
            """)

            # Metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    language TEXT,
                    topic TEXT,
                    keywords TEXT,  -- JSON array
                    summary TEXT,
                    is_prompt INTEGER DEFAULT 0,
                    is_llm_output INTEGER DEFAULT 0,
                    git_project TEXT,
                    confidence REAL,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
                )
            """)

            # Embeddings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    embedding BLOB NOT NULL,
                    dimensions INTEGER NOT NULL,
                    model TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
                )
            """)

            # Duplicates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS duplicates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    duplicate_of_id INTEGER NOT NULL,
                    similarity_score REAL NOT NULL,
                    detected_at TEXT NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                    FOREIGN KEY (duplicate_of_id) REFERENCES documents(id) ON DELETE CASCADE
                )
            """)

            # Full-text search virtual table (FTS5)
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                    filename,
                    filepath,
                    original_text,
                    content='documents',
                    content_rowid='id'
                )
            """)

            # Trigger to keep FTS in sync with documents table
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                    INSERT INTO documents_fts(rowid, filename, filepath, original_text)
                    VALUES (new.id, new.filename, new.filepath, new.original_text);
                END
            """)

            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                    DELETE FROM documents_fts WHERE rowid = old.id;
                END
            """)

            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
                    UPDATE documents_fts
                    SET filename = new.filename,
                        filepath = new.filepath,
                        original_text = new.original_text
                    WHERE rowid = old.id;
                END
            """)

            # Indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_filepath ON documents(filepath)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metadata_document_id ON metadata(document_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_embeddings_document_id ON embeddings(document_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_duplicates_document_id ON duplicates(document_id)")

    def insert_document(
        self,
        filename: str,
        filepath: str,
        source_extension: str,
        source_type: str,
        original_text: str,
        wordcount: int,
        created_at: str,
        metadata: Dict[str, Any],
        embedding: Optional[List[float]] = None,
        embedding_model: str = "unknown"
    ) -> int:
        """
        Insert a document with metadata and optional embedding.

        Args:
            filename: Document filename
            filepath: Full path to document
            source_extension: File extension (.txt, .pdf, etc.)
            source_type: Type classification (text, pdf, code, etc.)
            original_text: Full text content
            wordcount: Word count
            created_at: File creation timestamp
            metadata: Dictionary with language, topic, keywords, summary, etc.
            embedding: Optional embedding vector
            embedding_model: Model used for embeddings

        Returns:
            Document ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            processed_at = datetime.now().isoformat()

            # Insert document
            cursor.execute("""
                INSERT INTO documents (
                    filename, filepath, source_extension, source_type,
                    original_text, wordcount, created_at, processed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                filename, filepath, source_extension, source_type,
                original_text, wordcount, created_at, processed_at
            ))

            doc_id = cursor.lastrowid

            # Insert metadata
            keywords_json = json.dumps(metadata.get('keywords', []))
            cursor.execute("""
                INSERT INTO metadata (
                    document_id, language, topic, keywords, summary,
                    is_prompt, is_llm_output, git_project, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id,
                metadata.get('language', ''),
                metadata.get('topic', ''),
                keywords_json,
                metadata.get('summary', ''),
                1 if metadata.get('is_prompt', False) else 0,
                1 if metadata.get('is_llm_output', False) else 0,
                metadata.get('git_project', ''),
                metadata.get('confidence', 0.0)
            ))

            # Insert embedding if provided
            if embedding:
                embedding_blob = pickle.dumps(embedding)
                cursor.execute("""
                    INSERT INTO embeddings (
                        document_id, embedding, dimensions, model, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    doc_id,
                    embedding_blob,
                    len(embedding),
                    embedding_model,
                    processed_at
                ))

            return doc_id

    def document_exists(self, filepath: str) -> bool:
        """Check if document already exists in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM documents WHERE filepath = ?", (filepath,))
            return cursor.fetchone() is not None

    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """Get document with metadata by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    d.*,
                    m.language, m.topic, m.keywords, m.summary,
                    m.is_prompt, m.is_llm_output, m.git_project, m.confidence
                FROM documents d
                LEFT JOIN metadata m ON d.id = m.document_id
                WHERE d.id = ?
            """, (doc_id,))

            row = cursor.fetchone()
            if not row:
                return None

            doc = dict(row)
            doc['keywords'] = json.loads(doc['keywords']) if doc.get('keywords') else []
            doc['is_prompt'] = bool(doc.get('is_prompt', 0))
            doc['is_llm_output'] = bool(doc.get('is_llm_output', 0))

            return doc

    def get_embedding(self, doc_id: int) -> Optional[List[float]]:
        """Get embedding vector for document"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT embedding FROM embeddings WHERE document_id = ?",
                (doc_id,)
            )
            row = cursor.fetchone()
            if row:
                return pickle.loads(row['embedding'])
            return None

    def get_all_embeddings(self) -> List[Tuple[int, List[float]]]:
        """Get all embeddings with their document IDs"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT document_id, embedding FROM embeddings")
            return [
                (row['document_id'], pickle.loads(row['embedding']))
                for row in cursor.fetchall()
            ]

    def mark_as_duplicate(
        self,
        doc_id: int,
        duplicate_of_id: int,
        similarity_score: float
    ):
        """Mark a document as duplicate of another"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO duplicates (
                    document_id, duplicate_of_id, similarity_score, detected_at
                ) VALUES (?, ?, ?, ?)
            """, (doc_id, duplicate_of_id, similarity_score, datetime.now().isoformat()))

    def search_fulltext(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Full-text search across documents.

        Args:
            query: Search query (FTS5 syntax supported)
            limit: Maximum results to return

        Returns:
            List of matching documents with metadata
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    d.*,
                    m.language, m.topic, m.keywords, m.summary,
                    m.is_prompt, m.is_llm_output, m.git_project,
                    rank
                FROM documents_fts
                JOIN documents d ON documents_fts.rowid = d.id
                LEFT JOIN metadata m ON d.id = m.document_id
                WHERE documents_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit))

            results = []
            for row in cursor.fetchall():
                doc = dict(row)
                doc['keywords'] = json.loads(doc['keywords']) if doc.get('keywords') else []
                doc['is_prompt'] = bool(doc.get('is_prompt', 0))
                doc['is_llm_output'] = bool(doc.get('is_llm_output', 0))
                results.append(doc)

            return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) as total FROM documents")
            total_docs = cursor.fetchone()['total']

            cursor.execute("SELECT COUNT(*) as total FROM embeddings")
            total_embeddings = cursor.fetchone()['total']

            cursor.execute("SELECT COUNT(*) as total FROM duplicates")
            total_duplicates = cursor.fetchone()['total']

            cursor.execute("SELECT language, COUNT(*) as count FROM metadata GROUP BY language")
            languages = {row['language']: row['count'] for row in cursor.fetchall()}

            cursor.execute("""
                SELECT source_type, COUNT(*) as count
                FROM documents
                GROUP BY source_type
            """)
            file_types = {row['source_type']: row['count'] for row in cursor.fetchall()}

            return {
                'total_documents': total_docs,
                'total_embeddings': total_embeddings,
                'total_duplicates': total_duplicates,
                'languages': languages,
                'file_types': file_types
            }

    def get_all_documents(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all documents with pagination"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    d.*,
                    m.language, m.topic, m.keywords, m.summary,
                    m.is_prompt, m.is_llm_output, m.git_project
                FROM documents d
                LEFT JOIN metadata m ON d.id = m.document_id
                ORDER BY d.processed_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

            results = []
            for row in cursor.fetchall():
                doc = dict(row)
                doc['keywords'] = json.loads(doc['keywords']) if doc.get('keywords') else []
                doc['is_prompt'] = bool(doc.get('is_prompt', 0))
                doc['is_llm_output'] = bool(doc.get('is_llm_output', 0))
                results.append(doc)

            return results
