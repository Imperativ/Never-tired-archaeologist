# -*- coding: utf-8 -*-
import pytest
import tempfile
import sqlite3
from pathlib import Path
from database import Database, DatabaseError


class TestDatabaseInitialization:
    """Test database initialization and schema creation"""

    def test_creates_database_file(self, tmp_path):
        """Database file should be created"""
        db_path = tmp_path / "test.db"
        db = Database(db_path)
        assert db_path.exists()

    def test_creates_all_tables(self, tmp_path):
        """All required tables should be created"""
        db_path = tmp_path / "test.db"
        db = Database(db_path)

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN (
                'documents', 'metadata', 'embeddings', 'duplicates', 'documents_fts'
            )
        """)
        tables = [row[0] for row in cursor.fetchall()]

        assert 'documents' in tables
        assert 'metadata' in tables
        assert 'embeddings' in tables
        assert 'duplicates' in tables
        assert 'documents_fts' in tables

        conn.close()

    def test_idempotent_initialization(self, tmp_path):
        """Multiple initializations should not fail"""
        db_path = tmp_path / "test.db"
        db1 = Database(db_path)
        db2 = Database(db_path)  # Should not raise
        assert db_path.exists()


class TestDocumentInsertion:
    """Test document insertion operations"""

    @pytest.fixture
    def db(self, tmp_path):
        """Fixture providing a fresh database"""
        return Database(tmp_path / "test.db")

    def test_insert_document_basic(self, db):
        """Basic document insertion should work"""
        metadata = {
            'language': 'en',
            'topic': 'Testing',
            'keywords': ['test', 'python'],
            'summary': 'A test document',
            'is_prompt': False,
            'is_llm_output': False,
            'git_project': '',
            'confidence': 0.95
        }

        doc_id = db.insert_document(
            filename='test.txt',
            filepath='/path/to/test.txt',
            source_extension='.txt',
            source_type='text',
            original_text='This is a test document.',
            wordcount=5,
            created_at='2025-01-01T00:00:00',
            metadata=metadata
        )

        assert isinstance(doc_id, int)
        assert doc_id > 0

    def test_insert_document_with_embedding(self, db):
        """Document insertion with embedding should work"""
        metadata = {
            'language': 'en',
            'topic': 'Testing',
            'keywords': ['test'],
            'summary': 'Test',
            'confidence': 0.9
        }

        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

        doc_id = db.insert_document(
            filename='test.txt',
            filepath='/path/to/test.txt',
            source_extension='.txt',
            source_type='text',
            original_text='Test content',
            wordcount=2,
            created_at='2025-01-01T00:00:00',
            metadata=metadata,
            embedding=embedding,
            embedding_model='test-model'
        )

        # Verify embedding was stored
        retrieved = db.get_embedding(doc_id)
        assert retrieved is not None
        assert len(retrieved) == 5
        assert retrieved == embedding

    def test_duplicate_filepath_rejected(self, db):
        """Duplicate filepath should raise error"""
        metadata = {'language': 'en', 'topic': 'Test', 'keywords': [], 'summary': ''}

        db.insert_document(
            filename='test.txt',
            filepath='/same/path.txt',
            source_extension='.txt',
            source_type='text',
            original_text='First',
            wordcount=1,
            created_at='2025-01-01T00:00:00',
            metadata=metadata
        )

        with pytest.raises(DatabaseError):
            db.insert_document(
                filename='test2.txt',
                filepath='/same/path.txt',  # Same path
                source_extension='.txt',
                source_type='text',
                original_text='Second',
                wordcount=1,
                created_at='2025-01-01T00:00:00',
                metadata=metadata
            )

    def test_insert_with_complex_metadata(self, db):
        """Complex metadata should be stored correctly"""
        metadata = {
            'language': 'de',
            'topic': 'Komplexes Thema',
            'keywords': ['keyword1', 'keyword2', 'keyword3'],
            'summary': 'Eine sehr lange Zusammenfassung mit Umlauten: äöü',
            'is_prompt': True,
            'is_llm_output': False,
            'git_project': 'my-project',
            'confidence': 0.87
        }

        doc_id = db.insert_document(
            filename='complex.txt',
            filepath='/path/complex.txt',
            source_extension='.txt',
            source_type='text',
            original_text='Komplexer Text mit äöü',
            wordcount=4,
            created_at='2025-01-01T00:00:00',
            metadata=metadata
        )

        # Verify retrieval
        doc = db.get_document(doc_id)
        assert doc['language'] == 'de'
        assert doc['topic'] == 'Komplexes Thema'
        assert len(doc['keywords']) == 3
        assert doc['is_prompt'] is True
        assert doc['is_llm_output'] is False
        assert doc['git_project'] == 'my-project'


class TestDocumentRetrieval:
    """Test document retrieval operations"""

    @pytest.fixture
    def db_with_docs(self, tmp_path):
        """Fixture with pre-populated database"""
        db = Database(tmp_path / "test.db")

        for i in range(5):
            metadata = {
                'language': 'en' if i % 2 == 0 else 'de',
                'topic': f'Topic {i}',
                'keywords': [f'kw{i}'],
                'summary': f'Summary {i}',
                'confidence': 0.9
            }

            db.insert_document(
                filename=f'doc{i}.txt',
                filepath=f'/path/doc{i}.txt',
                source_extension='.txt',
                source_type='text',
                original_text=f'Content {i}',
                wordcount=2,
                created_at='2025-01-01T00:00:00',
                metadata=metadata
            )

        return db

    def test_document_exists_positive(self, db_with_docs):
        """Document exists check should return True for existing doc"""
        assert db_with_docs.document_exists('/path/doc0.txt') is True

    def test_document_exists_negative(self, db_with_docs):
        """Document exists check should return False for non-existing doc"""
        assert db_with_docs.document_exists('/nonexistent/path.txt') is False

    def test_get_document_by_id(self, db_with_docs):
        """Should retrieve document with all metadata"""
        doc = db_with_docs.get_document(1)

        assert doc is not None
        assert doc['filename'] == 'doc0.txt'
        assert doc['filepath'] == '/path/doc0.txt'
        assert doc['language'] == 'en'
        assert doc['topic'] == 'Topic 0'
        assert isinstance(doc['keywords'], list)

    def test_get_nonexistent_document(self, db_with_docs):
        """Getting non-existent document should return None"""
        doc = db_with_docs.get_document(9999)
        assert doc is None

    def test_get_all_documents(self, db_with_docs):
        """Should retrieve all documents"""
        docs = db_with_docs.get_all_documents()
        assert len(docs) == 5

    def test_get_all_documents_pagination(self, db_with_docs):
        """Pagination should work correctly"""
        docs_page1 = db_with_docs.get_all_documents(limit=2, offset=0)
        docs_page2 = db_with_docs.get_all_documents(limit=2, offset=2)

        assert len(docs_page1) == 2
        assert len(docs_page2) == 2
        assert docs_page1[0]['id'] != docs_page2[0]['id']


class TestEmbeddings:
    """Test embedding storage and retrieval"""

    @pytest.fixture
    def db(self, tmp_path):
        return Database(tmp_path / "test.db")

    def test_store_and_retrieve_embedding(self, db):
        """Embeddings should be stored and retrieved correctly"""
        metadata = {'language': 'en', 'topic': 'Test', 'keywords': [], 'summary': ''}
        embedding = [float(i) for i in range(768)]  # Typical embedding size

        doc_id = db.insert_document(
            filename='test.txt',
            filepath='/path/test.txt',
            source_extension='.txt',
            source_type='text',
            original_text='Test',
            wordcount=1,
            created_at='2025-01-01T00:00:00',
            metadata=metadata,
            embedding=embedding,
            embedding_model='test-embedding-model'
        )

        retrieved = db.get_embedding(doc_id)
        assert len(retrieved) == 768
        assert retrieved[0] == 0.0
        assert retrieved[-1] == 767.0

    def test_get_all_embeddings(self, db):
        """Should retrieve all embeddings with document IDs"""
        metadata = {'language': 'en', 'topic': 'Test', 'keywords': [], 'summary': ''}

        # Insert 3 documents with embeddings
        for i in range(3):
            db.insert_document(
                filename=f'doc{i}.txt',
                filepath=f'/path/doc{i}.txt',
                source_extension='.txt',
                source_type='text',
                original_text='Test',
                wordcount=1,
                created_at='2025-01-01T00:00:00',
                metadata=metadata,
                embedding=[float(i)] * 10,
                embedding_model='test'
            )

        all_embeddings = db.get_all_embeddings()
        assert len(all_embeddings) == 3

        # Check structure
        doc_id, embedding = all_embeddings[0]
        assert isinstance(doc_id, int)
        assert isinstance(embedding, list)
        assert len(embedding) == 10

    def test_get_embedding_for_doc_without_embedding(self, db):
        """Should return None for document without embedding"""
        metadata = {'language': 'en', 'topic': 'Test', 'keywords': [], 'summary': ''}

        doc_id = db.insert_document(
            filename='test.txt',
            filepath='/path/test.txt',
            source_extension='.txt',
            source_type='text',
            original_text='Test',
            wordcount=1,
            created_at='2025-01-01T00:00:00',
            metadata=metadata
            # No embedding provided
        )

        retrieved = db.get_embedding(doc_id)
        assert retrieved is None


class TestDuplicateDetection:
    """Test duplicate marking and tracking"""

    @pytest.fixture
    def db_with_docs(self, tmp_path):
        db = Database(tmp_path / "test.db")
        metadata = {'language': 'en', 'topic': 'Test', 'keywords': [], 'summary': ''}

        # Insert 2 documents
        for i in range(2):
            db.insert_document(
                filename=f'doc{i}.txt',
                filepath=f'/path/doc{i}.txt',
                source_extension='.txt',
                source_type='text',
                original_text=f'Content {i}',
                wordcount=2,
                created_at='2025-01-01T00:00:00',
                metadata=metadata
            )

        return db

    def test_mark_as_duplicate(self, db_with_docs):
        """Should mark document as duplicate"""
        db_with_docs.mark_as_duplicate(
            doc_id=2,
            duplicate_of_id=1,
            similarity_score=0.98
        )

        # Verify it was recorded
        stats = db_with_docs.get_statistics()
        assert stats['total_duplicates'] == 1


class TestFullTextSearch:
    """Test FTS5 full-text search functionality"""

    @pytest.fixture
    def db_with_searchable_docs(self, tmp_path):
        db = Database(tmp_path / "test.db")

        docs = [
            ('Python programming tutorial', 'This is a comprehensive Python tutorial for beginners.'),
            ('JavaScript basics', 'Learn JavaScript fundamentals and basic concepts.'),
            ('Python data science', 'Using Python for data science and machine learning.'),
            ('Java introduction', 'Introduction to Java programming language.')
        ]

        for i, (filename, content) in enumerate(docs):
            metadata = {'language': 'en', 'topic': 'Programming', 'keywords': [], 'summary': ''}
            db.insert_document(
                filename=f'{filename}.txt',
                filepath=f'/path/{filename}.txt',
                source_extension='.txt',
                source_type='text',
                original_text=content,
                wordcount=len(content.split()),
                created_at='2025-01-01T00:00:00',
                metadata=metadata
            )

        return db

    def test_search_finds_matching_documents(self, db_with_searchable_docs):
        """Search should find documents containing query term"""
        results = db_with_searchable_docs.search_fulltext('Python')
        assert len(results) == 2  # 2 docs contain "Python"

    def test_search_returns_ranked_results(self, db_with_searchable_docs):
        """Search results should be ranked by relevance"""
        results = db_with_searchable_docs.search_fulltext('JavaScript')
        assert len(results) == 1
        assert 'JavaScript' in results[0]['filename']

    def test_search_with_no_matches(self, db_with_searchable_docs):
        """Search with no matches should return empty list"""
        results = db_with_searchable_docs.search_fulltext('Rust')
        assert len(results) == 0

    def test_search_limit(self, db_with_searchable_docs):
        """Search should respect limit parameter"""
        results = db_with_searchable_docs.search_fulltext('programming', limit=1)
        assert len(results) == 1


class TestStatistics:
    """Test database statistics"""

    @pytest.fixture
    def db_with_varied_docs(self, tmp_path):
        db = Database(tmp_path / "test.db")

        # Insert docs with different languages and types
        configs = [
            ('en', 'text', 'doc1.txt'),
            ('en', 'text', 'doc2.txt'),
            ('de', 'code', 'doc3.py'),
            ('fr', 'markdown', 'doc4.md')
        ]

        for lang, src_type, filename in configs:
            metadata = {'language': lang, 'topic': 'Test', 'keywords': [], 'summary': ''}
            db.insert_document(
                filename=filename,
                filepath=f'/path/{filename}',
                source_extension='.' + filename.split('.')[-1],
                source_type=src_type,
                original_text='Content',
                wordcount=1,
                created_at='2025-01-01T00:00:00',
                metadata=metadata,
                embedding=[0.1] * 10,
                embedding_model='test'
            )

        return db

    def test_get_statistics(self, db_with_varied_docs):
        """Should return correct statistics"""
        stats = db_with_varied_docs.get_statistics()

        assert stats['total_documents'] == 4
        assert stats['total_embeddings'] == 4
        assert stats['total_duplicates'] == 0

        assert stats['languages']['en'] == 2
        assert stats['languages']['de'] == 1
        assert stats['languages']['fr'] == 1

        assert stats['file_types']['text'] == 2
        assert stats['file_types']['code'] == 1
        assert stats['file_types']['markdown'] == 1


class TestErrorHandling:
    """Test error handling"""

    @pytest.fixture
    def db(self, tmp_path):
        return Database(tmp_path / "test.db")

    def test_invalid_document_id(self, db):
        """Invalid document ID should return None"""
        doc = db.get_document(-1)
        assert doc is None

        embedding = db.get_embedding(-1)
        assert embedding is None
