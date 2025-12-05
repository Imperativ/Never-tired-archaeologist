# -*- coding: utf-8 -*-
"""
Comprehensive tests for text_extractor module.
Tests all supported file formats and edge cases.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from text_extractor import (
    readable_extension,
    infer_source_type,
    extract_text,
    _read_text_fallback
)


class TestReadableExtension:
    """Test readable_extension() function"""

    def test_txt_is_readable(self):
        """TXT files should be readable"""
        assert readable_extension('.txt') is True
        assert readable_extension('.TXT') is True

    def test_md_is_readable(self):
        """Markdown files should be readable"""
        assert readable_extension('.md') is True
        assert readable_extension('.MD') is True

    def test_pdf_is_readable(self):
        """PDF files should be readable"""
        assert readable_extension('.pdf') is True
        assert readable_extension('.PDF') is True

    def test_py_is_readable(self):
        """Python files should be readable"""
        assert readable_extension('.py') is True
        assert readable_extension('.PY') is True

    def test_json_is_readable(self):
        """JSON files should be readable"""
        assert readable_extension('.json') is True
        assert readable_extension('.JSON') is True

    def test_csv_is_readable(self):
        """CSV files should be readable"""
        assert readable_extension('.csv') is True
        assert readable_extension('.CSV') is True

    def test_html_is_readable(self):
        """HTML files should be readable"""
        assert readable_extension('.html') is True
        assert readable_extension('.HTML') is True

    def test_unsupported_extensions(self):
        """Unsupported extensions should return False"""
        assert readable_extension('.docx') is False
        assert readable_extension('.exe') is False
        assert readable_extension('.zip') is False
        assert readable_extension('.jpg') is False

    def test_case_insensitive(self):
        """Extension check should be case-insensitive"""
        assert readable_extension('.TxT') is True
        assert readable_extension('.Pdf') is True
        assert readable_extension('.PY') is True

    def test_none_extension(self):
        """None extension should return False"""
        assert readable_extension(None) is False

    def test_empty_string(self):
        """Empty string should return False"""
        assert readable_extension('') is False

    def test_extension_without_dot(self):
        """Extension without dot should return False"""
        assert readable_extension('txt') is False
        assert readable_extension('pdf') is False


class TestInferSourceType:
    """Test infer_source_type() function"""

    def test_txt_type(self):
        """TXT should map to 'text'"""
        assert infer_source_type('.txt') == 'text'
        assert infer_source_type('.TXT') == 'text'

    def test_md_type(self):
        """MD should map to 'markdown'"""
        assert infer_source_type('.md') == 'markdown'
        assert infer_source_type('.MD') == 'markdown'

    def test_pdf_type(self):
        """PDF should map to 'pdf'"""
        assert infer_source_type('.pdf') == 'pdf'

    def test_py_type(self):
        """PY should map to 'python'"""
        assert infer_source_type('.py') == 'python'

    def test_json_type(self):
        """JSON should map to 'json'"""
        assert infer_source_type('.json') == 'json'

    def test_csv_type(self):
        """CSV should map to 'csv'"""
        assert infer_source_type('.csv') == 'csv'

    def test_html_type(self):
        """HTML should map to 'html'"""
        assert infer_source_type('.html') == 'html'

    def test_unknown_extension(self):
        """Unknown extension should return 'unknown'"""
        assert infer_source_type('.docx') == 'unknown'
        assert infer_source_type('.exe') == 'unknown'
        assert infer_source_type('.xyz') == 'unknown'

    def test_none_extension(self):
        """None extension should return 'unknown'"""
        assert infer_source_type(None) == 'unknown'

    def test_empty_string(self):
        """Empty string should return 'unknown'"""
        assert infer_source_type('') == 'unknown'

    def test_case_insensitive(self):
        """Type inference should be case-insensitive"""
        assert infer_source_type('.TxT') == 'text'
        assert infer_source_type('.Pdf') == 'pdf'
        assert infer_source_type('.PY') == 'python'


class TestReadTextFallback:
    """Test _read_text_fallback() function"""

    def test_read_simple_text(self, tmp_path):
        """Should read simple text file"""
        test_file = tmp_path / "test.txt"
        content = "Hello, World!"
        test_file.write_text(content, encoding='utf-8')

        result = _read_text_fallback(test_file)
        assert result == content

    def test_read_multiline_text(self, tmp_path):
        """Should read multiline text"""
        test_file = tmp_path / "test.txt"
        content = "Line 1\nLine 2\nLine 3"
        test_file.write_text(content, encoding='utf-8')

        result = _read_text_fallback(test_file)
        assert result == content

    def test_read_unicode_text(self, tmp_path):
        """Should handle Unicode characters"""
        test_file = tmp_path / "test.txt"
        content = "Ümlaute: äöü\n日本語\nEmoji: 🔥🎉"
        test_file.write_text(content, encoding='utf-8')

        result = _read_text_fallback(test_file)
        assert result == content

    def test_read_empty_file(self, tmp_path):
        """Should handle empty file"""
        test_file = tmp_path / "empty.txt"
        test_file.write_text('', encoding='utf-8')

        result = _read_text_fallback(test_file)
        assert result == ''

    def test_handles_encoding_errors(self, tmp_path):
        """Should replace invalid encoding with replacement character"""
        test_file = tmp_path / "binary.txt"
        # Write some binary data that's not valid UTF-8
        test_file.write_bytes(b'\x80\x81\x82\x83')

        result = _read_text_fallback(test_file)
        # Should not raise, but replace invalid chars
        assert isinstance(result, str)


class TestExtractTextPlainFiles:
    """Test extract_text() for plain text files"""

    def test_extract_txt(self, tmp_path):
        """Should extract text from .txt file"""
        test_file = tmp_path / "test.txt"
        content = "This is a text file."
        test_file.write_text(content, encoding='utf-8')

        result = extract_text(test_file)
        assert result == content

    def test_extract_md(self, tmp_path):
        """Should extract text from .md file"""
        test_file = tmp_path / "test.md"
        content = "# Markdown Header\n\nSome **bold** text."
        test_file.write_text(content, encoding='utf-8')

        result = extract_text(test_file)
        assert result == content

    def test_extract_py(self, tmp_path):
        """Should extract text from .py file"""
        test_file = tmp_path / "test.py"
        content = "def hello():\n    print('Hello, World!')"
        test_file.write_text(content, encoding='utf-8')

        result = extract_text(test_file)
        assert result == content

    def test_extract_json(self, tmp_path):
        """Should extract text from .json file"""
        test_file = tmp_path / "test.json"
        content = '{"key": "value", "number": 42}'
        test_file.write_text(content, encoding='utf-8')

        result = extract_text(test_file)
        assert result == content

    def test_extract_csv(self, tmp_path):
        """Should extract text from .csv file"""
        test_file = tmp_path / "test.csv"
        content = "name,age,city\nAlice,30,Berlin\nBob,25,Munich"
        test_file.write_text(content, encoding='utf-8')

        result = extract_text(test_file)
        assert result == content

    def test_extract_html(self, tmp_path):
        """Should extract text from .html file"""
        test_file = tmp_path / "test.html"
        content = "<html><body><h1>Title</h1><p>Content</p></body></html>"
        test_file.write_text(content, encoding='utf-8')

        result = extract_text(test_file)
        assert result == content

    def test_case_insensitive_extension(self, tmp_path):
        """Should handle uppercase extensions"""
        test_file = tmp_path / "test.TXT"
        content = "UPPERCASE EXTENSION"
        test_file.write_text(content, encoding='utf-8')

        result = extract_text(test_file)
        assert result == content


class TestExtractTextPDF:
    """Test extract_text() for PDF files"""

    def test_extract_pdf_single_page(self, tmp_path):
        """Should extract text from single-page PDF"""
        test_file = tmp_path / "test.pdf"
        test_file.touch()

        # Mock PyMuPDF
        mock_page = Mock()
        mock_page.get_text.return_value = "PDF content on page 1"

        mock_doc = MagicMock()
        mock_doc.__enter__.return_value = [mock_page]
        mock_doc.__exit__.return_value = None

        mock_fitz = Mock()
        mock_fitz.open.return_value = mock_doc

        # Patch the import inside extract_text
        with patch.dict('sys.modules', {'fitz': mock_fitz}):
            result = extract_text(test_file)
            assert result == "PDF content on page 1"
            mock_fitz.open.assert_called_once_with(str(test_file))

    def test_extract_pdf_multiple_pages(self, tmp_path):
        """Should extract and combine text from multiple pages"""
        test_file = tmp_path / "test.pdf"
        test_file.touch()

        # Mock multiple pages
        mock_page1 = Mock()
        mock_page1.get_text.return_value = "Page 1 content"
        mock_page2 = Mock()
        mock_page2.get_text.return_value = "Page 2 content"
        mock_page3 = Mock()
        mock_page3.get_text.return_value = "Page 3 content"

        mock_doc = MagicMock()
        mock_doc.__enter__.return_value = [mock_page1, mock_page2, mock_page3]
        mock_doc.__exit__.return_value = None

        mock_fitz = Mock()
        mock_fitz.open.return_value = mock_doc

        with patch.dict('sys.modules', {'fitz': mock_fitz}):
            result = extract_text(test_file)
            assert result == "Page 1 content\nPage 2 content\nPage 3 content"

    def test_extract_pdf_empty_pages(self, tmp_path):
        """Should handle PDFs with empty pages"""
        test_file = tmp_path / "test.pdf"
        test_file.touch()

        mock_page1 = Mock()
        mock_page1.get_text.return_value = "Content"
        mock_page2 = Mock()
        mock_page2.get_text.return_value = ""  # Empty page
        mock_page3 = Mock()
        mock_page3.get_text.return_value = "More content"

        mock_doc = MagicMock()
        mock_doc.__enter__.return_value = [mock_page1, mock_page2, mock_page3]
        mock_doc.__exit__.return_value = None

        mock_fitz = Mock()
        mock_fitz.open.return_value = mock_doc

        with patch.dict('sys.modules', {'fitz': mock_fitz}):
            result = extract_text(test_file)
            assert result == "Content\n\nMore content"

    def test_extract_pdf_without_pymupdf(self, tmp_path):
        """Should raise RuntimeError if PyMuPDF not installed"""
        test_file = tmp_path / "test.pdf"
        test_file.touch()

        # Remove fitz from sys.modules if present
        import sys
        fitz_backup = sys.modules.get('fitz')
        if 'fitz' in sys.modules:
            del sys.modules['fitz']

        try:
            # Mock the import to fail
            with patch('builtins.__import__', side_effect=ImportError("No module named 'fitz'")):
                with pytest.raises(RuntimeError, match="PyMuPDF.*nicht installiert"):
                    extract_text(test_file)
        finally:
            # Restore fitz if it was present
            if fitz_backup is not None:
                sys.modules['fitz'] = fitz_backup

    def test_extract_pdf_with_unicode(self, tmp_path):
        """Should handle Unicode in PDF content"""
        test_file = tmp_path / "test.pdf"
        test_file.touch()

        mock_page = Mock()
        mock_page.get_text.return_value = "Ümlaute: äöü, 日本語, 🎉"

        mock_doc = MagicMock()
        mock_doc.__enter__.return_value = [mock_page]
        mock_doc.__exit__.return_value = None

        mock_fitz = Mock()
        mock_fitz.open.return_value = mock_doc

        with patch.dict('sys.modules', {'fitz': mock_fitz}):
            result = extract_text(test_file)
            assert "äöü" in result
            assert "日本語" in result


class TestExtractTextEdgeCases:
    """Test edge cases and error handling"""

    def test_unsupported_extension(self, tmp_path):
        """Should return empty string for unsupported extension"""
        test_file = tmp_path / "test.docx"
        test_file.write_bytes(b'fake docx content')

        result = extract_text(test_file)
        assert result == ""

    def test_no_extension(self, tmp_path):
        """Should return empty string for file without extension"""
        test_file = tmp_path / "README"
        test_file.write_text("content")

        result = extract_text(test_file)
        assert result == ""

    def test_mixed_case_extension(self, tmp_path):
        """Should handle mixed case extensions"""
        test_file = tmp_path / "test.TxT"
        content = "Mixed case extension"
        test_file.write_text(content, encoding='utf-8')

        result = extract_text(test_file)
        assert result == content

    def test_very_large_text_file(self, tmp_path):
        """Should handle large text files"""
        test_file = tmp_path / "large.txt"
        # Create a large text (1MB)
        large_content = "Lorem ipsum dolor sit amet. " * 40000
        test_file.write_text(large_content, encoding='utf-8')

        result = extract_text(test_file)
        assert len(result) > 1_000_000
        assert result == large_content

    def test_file_with_only_whitespace(self, tmp_path):
        """Should handle files with only whitespace"""
        test_file = tmp_path / "whitespace.txt"
        test_file.write_text("   \n\n\t\t   \n   ")

        result = extract_text(test_file)
        assert result == "   \n\n\t\t   \n   "

    def test_file_with_special_characters(self, tmp_path):
        """Should preserve special characters"""
        test_file = tmp_path / "special.txt"
        content = "Special: @#$%^&*()_+-=[]{}|;':\",./<>?"
        test_file.write_text(content, encoding='utf-8')

        result = extract_text(test_file)
        assert result == content


class TestExtractTextIntegration:
    """Integration tests for extract_text()"""

    def test_all_supported_formats(self, tmp_path):
        """Should successfully extract from all supported formats"""
        formats = {
            '.txt': 'Text content',
            '.md': '# Markdown',
            '.py': 'print("Hello")',
            '.json': '{"key": "value"}',
            '.csv': 'a,b,c',
            '.html': '<html><body>HTML</body></html>'
        }

        for ext, content in formats.items():
            test_file = tmp_path / f"test{ext}"
            test_file.write_text(content, encoding='utf-8')

            result = extract_text(test_file)
            assert result == content, f"Failed for {ext}"

    def test_realistic_python_file(self, tmp_path):
        """Should extract realistic Python code"""
        test_file = tmp_path / "example.py"
        content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example Python module
"""

def calculate_sum(a: int, b: int) -> int:
    """Calculate sum of two numbers"""
    return a + b

if __name__ == "__main__":
    result = calculate_sum(5, 10)
    print(f"Result: {result}")
'''
        test_file.write_text(content, encoding='utf-8')

        result = extract_text(test_file)
        assert result == content
        assert "calculate_sum" in result
        assert "# -*- coding: utf-8 -*-" in result

    def test_realistic_markdown_file(self, tmp_path):
        """Should extract realistic Markdown"""
        test_file = tmp_path / "README.md"
        content = '''# Project Title

## Description

This is a **bold** statement with *italic* text.

### Features

- Feature 1
- Feature 2
- Feature 3

```python
def hello():
    print("Hello, World!")
```

[Link](https://example.com)
'''
        test_file.write_text(content, encoding='utf-8')

        result = extract_text(test_file)
        assert result == content
        assert "# Project Title" in result
        assert "**bold**" in result

    def test_realistic_json_file(self, tmp_path):
        """Should extract realistic JSON"""
        test_file = tmp_path / "config.json"
        content = '''{
  "name": "archaeologist",
  "version": "3.0.0",
  "settings": {
    "embeddings": true,
    "threshold": 0.95
  }
}'''
        test_file.write_text(content, encoding='utf-8')

        result = extract_text(test_file)
        assert result == content
        assert "archaeologist" in result
