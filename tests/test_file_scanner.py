# -*- coding: utf-8 -*-
import pytest
from pathlib import Path
from file_scanner import iter_supported_files, SUPPORTED_EXTS


class TestFileScannerBasics:
    """Test basic file scanning functionality"""

    def test_supported_extensions_constant(self):
        """Verify SUPPORTED_EXTS contains expected extensions"""
        expected = {".txt", ".md", ".pdf", ".py", ".json", ".csv", ".html"}
        assert SUPPORTED_EXTS == expected

    def test_empty_directory(self, tmp_path):
        """Empty directory should yield no files"""
        result = list(iter_supported_files(tmp_path))
        assert result == []

    def test_single_supported_file(self, tmp_path):
        """Should find a single supported file"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        result = list(iter_supported_files(tmp_path))
        assert len(result) == 1
        assert result[0] == test_file

    def test_multiple_supported_files(self, tmp_path):
        """Should find all supported files"""
        files = [
            tmp_path / "test1.txt",
            tmp_path / "test2.md",
            tmp_path / "test3.py",
        ]
        for f in files:
            f.write_text("content")

        result = list(iter_supported_files(tmp_path))
        assert len(result) == 3
        assert set(result) == set(files)


class TestFileScannerFiltering:
    """Test filtering logic"""

    def test_unsupported_extension_ignored(self, tmp_path):
        """Unsupported file extensions should be ignored"""
        (tmp_path / "test.docx").write_text("content")
        (tmp_path / "test.exe").write_text("content")
        (tmp_path / "test.zip").write_text("content")

        result = list(iter_supported_files(tmp_path))
        assert result == []

    def test_mixed_supported_and_unsupported(self, tmp_path):
        """Should only return supported files from mixed directory"""
        (tmp_path / "good.txt").write_text("content")
        (tmp_path / "bad.docx").write_text("content")
        (tmp_path / "good.md").write_text("content")
        (tmp_path / "bad.exe").write_text("content")

        result = list(iter_supported_files(tmp_path))
        assert len(result) == 2
        assert all(f.suffix in SUPPORTED_EXTS for f in result)

    def test_hidden_files_skipped(self, tmp_path):
        """Hidden files (starting with .) should be skipped"""
        (tmp_path / ".hidden.txt").write_text("content")
        (tmp_path / "visible.txt").write_text("content")

        result = list(iter_supported_files(tmp_path))
        assert len(result) == 1
        assert result[0].name == "visible.txt"

    def test_processed_directory_skipped(self, tmp_path):
        """_processed directory should be skipped"""
        processed_dir = tmp_path / "_processed"
        processed_dir.mkdir()
        (processed_dir / "file.txt").write_text("content")
        (tmp_path / "regular.txt").write_text("content")

        result = list(iter_supported_files(tmp_path))
        assert len(result) == 1
        assert result[0].name == "regular.txt"


class TestFileScannerRecursion:
    """Test recursive directory scanning"""

    def test_nested_directories(self, tmp_path):
        """Should recursively find files in subdirectories"""
        (tmp_path / "level1").mkdir()
        (tmp_path / "level1" / "level2").mkdir()

        files = [
            tmp_path / "root.txt",
            tmp_path / "level1" / "sub.txt",
            tmp_path / "level1" / "level2" / "deep.txt",
        ]
        for f in files:
            f.write_text("content")

        result = list(iter_supported_files(tmp_path))
        assert len(result) == 3
        assert set(result) == set(files)

    def test_deeply_nested_processed_dir(self, tmp_path):
        """_processed should be skipped even when nested"""
        nested = tmp_path / "level1" / "level2"
        nested.mkdir(parents=True)
        processed = nested / "_processed"
        processed.mkdir()

        (tmp_path / "root.txt").write_text("content")
        (processed / "skip.txt").write_text("content")

        result = list(iter_supported_files(tmp_path))
        assert len(result) == 1
        assert result[0].name == "root.txt"


class TestFileScannerEdgeCases:
    """Test edge cases and error conditions"""

    def test_case_insensitive_extensions(self, tmp_path):
        """File extensions should be case-insensitive"""
        files = [
            tmp_path / "test.TXT",
            tmp_path / "test.Md",
            tmp_path / "test.PDF",
        ]
        for f in files:
            f.write_text("content")

        result = list(iter_supported_files(tmp_path))
        assert len(result) == 3

    def test_files_without_extension(self, tmp_path):
        """Files without extension should be ignored"""
        (tmp_path / "README").write_text("content")
        (tmp_path / "test.txt").write_text("content")

        result = list(iter_supported_files(tmp_path))
        assert len(result) == 1
        assert result[0].name == "test.txt"

    def test_directories_not_yielded(self, tmp_path):
        """Directories themselves should not be yielded"""
        (tmp_path / "subdir.txt").mkdir()  # Directory with .txt "extension"
        (tmp_path / "file.txt").write_text("content")

        result = list(iter_supported_files(tmp_path))
        assert len(result) == 1
        assert result[0].is_file()

    def test_symlinks_handled(self, tmp_path):
        """Should handle symlinks gracefully (if supported by OS)"""
        real_file = tmp_path / "real.txt"
        real_file.write_text("content")

        # Symlinks might not work on all systems, skip if unavailable
        try:
            link_file = tmp_path / "link.txt"
            link_file.symlink_to(real_file)

            result = list(iter_supported_files(tmp_path))
            # Should find at least the real file
            assert len(result) >= 1
        except (OSError, NotImplementedError):
            pytest.skip("Symlinks not supported on this system")
