# -*- coding: utf-8 -*-
"""
Tests for main.py GUI application, focusing on search functionality.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from datetime import datetime


class TestSearchFunctionality:
    """Tests for document search feature in GUI"""

    @pytest.fixture
    def mock_tk_components(self):
        """Mock Tkinter components"""
        with patch('main.Tk') as mock_tk, \
             patch('main.StringVar') as mock_stringvar, \
             patch('main.IntVar') as mock_intvar, \
             patch('main.Button') as mock_button, \
             patch('main.Label') as mock_label, \
             patch('main.Text') as mock_text, \
             patch('main.Frame') as mock_frame, \
             patch('main.Checkbutton') as mock_checkbutton, \
             patch('main.Scrollbar') as mock_scrollbar:

            # Setup string var mocks
            mock_source_dir = Mock()
            mock_source_dir.get.return_value = "/test/path"
            mock_source_dir.set = Mock()

            mock_search_query = Mock()
            mock_search_query.get = Mock()
            mock_search_query.set = Mock()

            mock_stringvar.side_effect = [mock_source_dir, mock_search_query]

            # Setup int var mocks
            mock_intvar.side_effect = [Mock(), Mock()]

            yield {
                'tk': mock_tk,
                'stringvar': mock_stringvar,
                'source_dir': mock_source_dir,
                'search_query': mock_search_query,
                'intvar': mock_intvar,
                'button': mock_button,
                'label': mock_label,
                'text': mock_text,
                'frame': mock_frame,
                'checkbutton': mock_checkbutton,
                'scrollbar': mock_scrollbar
            }

    @pytest.fixture
    def app_instance(self, mock_tk_components):
        """Create a mocked App instance for testing"""
        from main import App

        mock_master = Mock()
        mock_master.title = Mock()
        mock_master.geometry = Mock()
        mock_master.after = Mock()

        with patch.object(App, '_build_gui'), \
             patch.object(App, 'drain_queue'):
            app = App(mock_master)

            # Setup necessary attributes
            mock_db_path = Mock(spec=Path)
            mock_db_path.exists.return_value = True
            mock_db_path.__str__ = Mock(return_value="/test/db/archaeologist.db")
            app.db_path = mock_db_path
            app.log = Mock()
            app.set_status = Mock()
            app.msg_queue = Mock()

            return app

    def test_search_documents_success(self, app_instance):
        """Search should display results when documents are found"""
        # Arrange
        app_instance.search_query = Mock()
        app_instance.search_query.get.return_value = "Python"

        mock_results = [
            {
                'id': 1,
                'filename': 'test.py',
                'filepath': '/test/test.py',
                'language': 'en',
                'topic': 'Programming',
                'keywords': ['python', 'code'],
                'summary': 'A Python test file',
                'wordcount': 100,
                'created_at': '2024-01-01T00:00:00'
            },
            {
                'id': 2,
                'filename': 'tutorial.md',
                'filepath': '/test/tutorial.md',
                'language': 'en',
                'topic': 'Tutorial',
                'keywords': ['python', 'tutorial'],
                'summary': 'Python tutorial',
                'wordcount': 500,
                'created_at': '2024-01-02T00:00:00'
            }
        ]

        with patch('main.Database') as mock_db_class:
            mock_db = Mock()
            mock_db.search_fulltext.return_value = mock_results
            mock_db_class.return_value = mock_db

            # Act
            from main import App
            App.search_documents(app_instance)

            # Assert
            mock_db.search_fulltext.assert_called_once_with("Python", limit=50)

            # Check that results were logged
            assert app_instance.log.call_count >= 4  # Header + separator + results

            # Verify result header was logged
            calls = [str(call) for call in app_instance.log.call_args_list]
            assert any('SUCHERGEBNISSE' in str(call) for call in calls)
            assert any('2 Treffer' in str(call) or '2 Dokumente' in str(call) for call in calls)

    def test_search_documents_no_results(self, app_instance):
        """Search should handle empty results gracefully"""
        # Arrange
        app_instance.search_query = Mock()
        app_instance.search_query.get.return_value = "nonexistent"

        with patch('main.Database') as mock_db_class:
            mock_db = Mock()
            mock_db.search_fulltext.return_value = []
            mock_db_class.return_value = mock_db

            # Act
            from main import App
            App.search_documents(app_instance)

            # Assert
            mock_db.search_fulltext.assert_called_once()

            # Should log a warning about no results
            warn_calls = [call for call in app_instance.log.call_args_list
                          if len(call[0]) > 1 and call[0][1] == "WARN"]
            assert len(warn_calls) > 0
            assert any('Keine' in str(call[0][0]) for call in warn_calls)

    def test_search_documents_empty_query(self, app_instance):
        """Search should reject empty query"""
        # Arrange
        app_instance.search_query = Mock()
        app_instance.search_query.get.return_value = "   "  # Whitespace only

        # Act
        from main import App
        App.search_documents(app_instance)

        # Assert
        # Should log warning, not call database
        warn_calls = [call for call in app_instance.log.call_args_list
                      if len(call[0]) > 1 and call[0][1] == "WARN"]
        assert len(warn_calls) > 0

    def test_search_documents_no_database(self, app_instance):
        """Search should handle missing database gracefully"""
        # Arrange
        app_instance.search_query = Mock()
        app_instance.search_query.get.return_value = "test"
        app_instance.db_path = None  # No database

        # Act
        from main import App
        App.search_documents(app_instance)

        # Assert
        warn_calls = [call for call in app_instance.log.call_args_list
                      if len(call[0]) > 1 and call[0][1] == "WARN"]
        assert len(warn_calls) > 0
        assert any('Datenbank' in str(call[0][0]) for call in warn_calls)

    def test_search_documents_nonexistent_database_file(self, app_instance, tmp_path):
        """Search should handle non-existent database file"""
        # Arrange
        app_instance.search_query = Mock()
        app_instance.search_query.get.return_value = "test"
        app_instance.db_path = tmp_path / "nonexistent.db"  # File doesn't exist

        # Act
        from main import App
        App.search_documents(app_instance)

        # Assert
        warn_calls = [call for call in app_instance.log.call_args_list
                      if len(call[0]) > 1 and call[0][1] == "WARN"]
        assert len(warn_calls) > 0

    def test_search_documents_database_error(self, app_instance):
        """Search should handle database errors gracefully"""
        # Arrange
        app_instance.search_query = Mock()
        app_instance.search_query.get.return_value = "test"

        with patch('main.Database') as mock_db_class:
            mock_db_class.side_effect = Exception("Database connection failed")

            # Act
            from main import App
            # Clear previous log calls
            app_instance.log.reset_mock()
            App.search_documents(app_instance)

            # Assert
            error_calls = [call for call in app_instance.log.call_args_list
                           if len(call[0]) > 1 and call[0][1] == "ERROR"]
            assert len(error_calls) > 0

    def test_search_documents_with_limit(self, app_instance):
        """Search should pass limit parameter to database"""
        # Arrange
        app_instance.search_query = Mock()
        app_instance.search_query.get.return_value = "test query"

        with patch('main.Database') as mock_db_class:
            mock_db = Mock()
            mock_db.search_fulltext.return_value = []
            mock_db_class.return_value = mock_db

            # Act
            from main import App
            App.search_documents(app_instance)

            # Assert
            # Should call with default limit
            mock_db.search_fulltext.assert_called_once()
            call_args = mock_db.search_fulltext.call_args
            assert 'limit' in call_args.kwargs or len(call_args.args) > 1

    def test_search_results_formatting(self, app_instance):
        """Search results should be properly formatted in output"""
        # Arrange
        app_instance.search_query = Mock()
        app_instance.search_query.get.return_value = "test"

        mock_result = {
            'id': 1,
            'filename': 'example.txt',
            'filepath': '/path/to/example.txt',
            'language': 'de',
            'topic': 'Testing',
            'keywords': ['test', 'example'],
            'summary': 'This is a test document',
            'wordcount': 250,
            'created_at': '2024-01-15T10:30:00'
        }

        with patch('main.Database') as mock_db_class:
            mock_db = Mock()
            mock_db.search_fulltext.return_value = [mock_result]
            mock_db_class.return_value = mock_db

            # Act
            from main import App
            # Clear previous log calls
            app_instance.log.reset_mock()
            App.search_documents(app_instance)

            # Assert
            # Check that key information was logged
            all_logs = [str(call[0][0]) for call in app_instance.log.call_args_list]
            combined_logs = ' '.join(all_logs)

            assert 'example.txt' in combined_logs
            assert 'Testing' in combined_logs or 'test' in combined_logs.lower()

    def test_search_with_special_characters(self, app_instance):
        """Search should handle queries with special characters"""
        # Arrange
        app_instance.search_query = Mock()
        app_instance.search_query.get.return_value = "test AND query OR special"

        with patch('main.Database') as mock_db_class:
            mock_db = Mock()
            mock_db.search_fulltext.return_value = []
            mock_db_class.return_value = mock_db

            # Act
            from main import App
            App.search_documents(app_instance)

            # Assert
            # Should pass query as-is to database (FTS5 supports operators)
            mock_db.search_fulltext.assert_called_once()
            call_args = mock_db.search_fulltext.call_args
            assert "test AND query OR special" in str(call_args)
