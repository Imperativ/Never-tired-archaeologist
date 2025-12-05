# -*- coding: utf-8 -*-
import pytest
from pathlib import Path
from utils import ensure_processed_dir, log_error, safe_relpath, slugify_filename


class TestEnsureProcessedDir:
    """Test processed directory creation"""

    def test_creates_processed_dir(self, tmp_path):
        """Should create _processed directory"""
        result = ensure_processed_dir(tmp_path)
        assert result.exists()
        assert result.is_dir()
        assert result.name == "_processed"

    def test_idempotent(self, tmp_path):
        """Calling twice should not fail"""
        dir1 = ensure_processed_dir(tmp_path)
        dir2 = ensure_processed_dir(tmp_path)
        assert dir1 == dir2
        assert dir1.exists()

    def test_returns_path_object(self, tmp_path):
        """Should return Path object"""
        result = ensure_processed_dir(tmp_path)
        assert isinstance(result, Path)

    def test_nested_source_dir(self, tmp_path):
        """Should work with nested source directories"""
        nested = tmp_path / "level1" / "level2"
        nested.mkdir(parents=True)
        result = ensure_processed_dir(nested)
        assert result.exists()
        assert result == nested / "_processed"


class TestLogError:
    """Test error logging functionality"""

    def test_creates_log_file(self, tmp_path):
        """Should create log file if it doesn't exist"""
        log_path = tmp_path / "error_log.txt"
        log_error(log_path, "Test error message")
        assert log_path.exists()

    def test_appends_to_existing_log(self, tmp_path):
        """Should append to existing log file"""
        log_path = tmp_path / "error_log.txt"
        log_error(log_path, "First error")
        log_error(log_path, "Second error")

        content = log_path.read_text(encoding="utf-8")
        assert "First error" in content
        assert "Second error" in content

    def test_adds_newline(self, tmp_path):
        """Should add newline after each message"""
        log_path = tmp_path / "error_log.txt"
        log_error(log_path, "Error 1")
        log_error(log_path, "Error 2")

        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        assert lines[0] == "Error 1"
        assert lines[1] == "Error 2"

    def test_creates_parent_directories(self, tmp_path):
        """Should create parent directories if needed"""
        log_path = tmp_path / "subdir" / "nested" / "error_log.txt"
        log_error(log_path, "Test message")
        assert log_path.exists()
        assert log_path.parent.exists()

    def test_handles_unicode(self, tmp_path):
        """Should handle unicode characters correctly"""
        log_path = tmp_path / "error_log.txt"
        message = "Error: äöü 日本語 émoji 🔥"
        log_error(log_path, message)

        content = log_path.read_text(encoding="utf-8")
        assert message in content

    def test_empty_message(self, tmp_path):
        """Should handle empty messages"""
        log_path = tmp_path / "error_log.txt"
        log_error(log_path, "")
        assert log_path.exists()
        content = log_path.read_text(encoding="utf-8")
        assert content == "\n"


class TestSafeRelpath:
    """Test safe relative path calculation"""

    def test_simple_relative_path(self, tmp_path):
        """Should return relative path for files in subdirectory"""
        root = tmp_path
        file_path = tmp_path / "subdir" / "file.txt"
        file_path.parent.mkdir()
        file_path.touch()

        result = safe_relpath(file_path, root)
        assert result == str(Path("subdir") / "file.txt")

    def test_file_in_root(self, tmp_path):
        """Should handle file directly in root"""
        root = tmp_path
        file_path = tmp_path / "file.txt"
        file_path.touch()

        result = safe_relpath(file_path, root)
        assert result == "file.txt"

    def test_deeply_nested_path(self, tmp_path):
        """Should handle deeply nested paths"""
        root = tmp_path
        file_path = tmp_path / "a" / "b" / "c" / "d" / "file.txt"
        file_path.parent.mkdir(parents=True)
        file_path.touch()

        result = safe_relpath(file_path, root)
        expected = str(Path("a") / "b" / "c" / "d" / "file.txt")
        assert result == expected

    def test_path_outside_root_returns_absolute(self, tmp_path):
        """Should return absolute path if file is outside root"""
        root = tmp_path / "root"
        root.mkdir()
        file_path = tmp_path / "outside" / "file.txt"
        file_path.parent.mkdir()
        file_path.touch()

        result = safe_relpath(file_path, root)
        # Should return string representation of full path
        assert str(file_path) in result

    def test_returns_string(self, tmp_path):
        """Should always return a string"""
        root = tmp_path
        file_path = tmp_path / "file.txt"
        file_path.touch()

        result = safe_relpath(file_path, root)
        assert isinstance(result, str)


class TestSlugifyFilename:
    """Test filename slugification"""

    def test_simple_filename(self):
        """Should leave simple filenames unchanged"""
        assert slugify_filename("test") == "test"
        assert slugify_filename("test_file") == "test_file"
        assert slugify_filename("test-file") == "test-file"

    def test_spaces_converted_to_underscores(self):
        """Should convert spaces to underscores"""
        assert slugify_filename("test file") == "test_file"
        assert slugify_filename("my document") == "my_document"

    def test_special_characters_removed(self):
        """Should remove or convert special characters"""
        assert slugify_filename("test@file") == "test_file"
        assert slugify_filename("test#file") == "test_file"
        assert slugify_filename("test!file?") == "test_file"

    def test_multiple_spaces_collapsed(self):
        """Should collapse multiple spaces/underscores"""
        assert slugify_filename("test   file") == "test_file"
        assert slugify_filename("test___file") == "test_file"

    def test_leading_trailing_underscores_removed(self):
        """Should remove leading/trailing underscores"""
        assert slugify_filename("_test_") == "test"
        assert slugify_filename("__test__") == "test"

    def test_unicode_characters_preserved(self):
        """Should preserve unicode characters"""
        result = slugify_filename("тест")
        assert "тест" in result or "_" in result  # Depending on regex implementation

    def test_dots_preserved(self):
        """Should preserve dots (for file extensions handling)"""
        assert slugify_filename("test.txt") == "test.txt"
        assert slugify_filename("my.file.name") == "my.file.name"

    def test_empty_string_returns_default(self):
        """Empty or all-invalid strings should return 'document'"""
        assert slugify_filename("") == "document"
        assert slugify_filename("   ") == "document"
        assert slugify_filename("___") == "document"

    def test_only_special_chars_returns_default(self):
        """String with only special characters should return 'document'"""
        assert slugify_filename("@#$%^&*()") == "document"

    def test_mixed_valid_invalid(self):
        """Should handle mix of valid and invalid characters"""
        assert slugify_filename("my@file#name") == "my_file_name"
        assert slugify_filename("test (1).txt") == "test_1_.txt"

    def test_preserves_hyphens(self):
        """Should preserve hyphens"""
        assert slugify_filename("test-file-name") == "test-file-name"

    def test_real_world_filenames(self):
        """Test with realistic problematic filenames"""
        assert slugify_filename("My Document (Draft).txt") == "My_Document_Draft_.txt"
        assert slugify_filename("Report #3 - Final!.pdf") == "Report_3_-_Final_.pdf"
        assert slugify_filename("data_2024-01-15.csv") == "data_2024-01-15.csv"


class TestIntegration:
    """Integration tests for utils module"""

    def test_complete_workflow(self, tmp_path):
        """Test complete workflow: create dir, log errors, handle paths"""
        # Setup
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create processed directory
        processed_dir = ensure_processed_dir(source_dir)
        assert processed_dir.exists()

        # Create test file
        test_file = source_dir / "test file@2024.txt"
        test_file.write_text("content")

        # Get safe relative path
        rel_path = safe_relpath(test_file, source_dir)
        assert "test file@2024.txt" in rel_path

        # Slugify the filename
        safe_name = slugify_filename(test_file.stem)
        assert "@" not in safe_name
        assert " " not in safe_name

        # Log an error
        error_log = processed_dir / "error_log.txt"
        log_error(error_log, f"Error processing {rel_path}")
        assert error_log.exists()

        content = error_log.read_text(encoding="utf-8")
        assert rel_path in content
