# -*- coding: utf-8 -*-
"""
Comprehensive tests for exporter module.
Tests YAML frontmatter generation and Markdown export.
"""
import pytest
from pathlib import Path
from exporter import (
    _yaml_escape_scalar,
    _yaml_list,
    write_markdown_with_metadata
)


class TestYamlEscapeScalar:
    """Test _yaml_escape_scalar() function"""

    def test_simple_string(self):
        """Simple strings should not be escaped"""
        assert _yaml_escape_scalar("hello") == "hello"
        assert _yaml_escape_scalar("test123") == "test123"
        assert _yaml_escape_scalar("simple_text") == "simple_text"

    def test_none_value(self):
        """None should return empty string"""
        assert _yaml_escape_scalar(None) == ""

    def test_colon_escaped(self):
        """Strings with colons should be quoted"""
        result = _yaml_escape_scalar("key: value")
        assert result.startswith('"')
        assert result.endswith('"')
        assert "key: value" in result

    def test_dash_escaped(self):
        """Strings with dashes should be quoted"""
        result = _yaml_escape_scalar("test-value")
        assert result.startswith('"')
        assert result.endswith('"')

    def test_braces_escaped(self):
        """Strings with braces should be quoted"""
        for char in ['{', '}', '[', ']']:
            result = _yaml_escape_scalar(f"test{char}value")
            assert result.startswith('"')
            assert result.endswith('"')

    def test_comma_escaped(self):
        """Strings with commas should be quoted"""
        result = _yaml_escape_scalar("a, b, c")
        assert result.startswith('"')
        assert result.endswith('"')

    def test_hash_escaped(self):
        """Strings with # should be quoted"""
        result = _yaml_escape_scalar("test # comment")
        assert result.startswith('"')
        assert result.endswith('"')

    def test_special_yaml_chars_escaped(self):
        """All special YAML chars should trigger quoting"""
        special_chars = [':', '-', '{', '}', '[', ']', ',', '#', '&', '*', '!', '|', '>', "'", '"', '%', '@', '`']
        for char in special_chars:
            result = _yaml_escape_scalar(f"test{char}")
            assert result.startswith('"'), f"Failed for char: {char}"
            assert result.endswith('"'), f"Failed for char: {char}"

    def test_double_quotes_escaped_inside(self):
        """Double quotes inside should be escaped"""
        result = _yaml_escape_scalar('He said "hello"')
        assert result.startswith('"')
        assert result.endswith('"')
        assert '\\"' in result  # Quotes should be escaped

    def test_multiple_double_quotes(self):
        """Multiple double quotes should all be escaped"""
        result = _yaml_escape_scalar('"test" and "more"')
        assert result.count('\\"') == 4  # 4 quotes escaped

    def test_unicode_characters(self):
        """Unicode characters should be preserved"""
        result = _yaml_escape_scalar("Ümlaute äöü")
        assert "äöü" in result

    def test_number_converted_to_string(self):
        """Numbers should be converted to strings"""
        assert _yaml_escape_scalar(123) == "123"
        assert _yaml_escape_scalar(45.67) == "45.67"

    def test_boolean_converted_to_string(self):
        """Booleans should be converted to strings"""
        assert _yaml_escape_scalar(True) == "True"
        assert _yaml_escape_scalar(False) == "False"

    def test_empty_string(self):
        """Empty string should return empty string"""
        assert _yaml_escape_scalar("") == ""

    def test_whitespace_only(self):
        """Whitespace-only string should not be quoted (no special chars)"""
        assert _yaml_escape_scalar("   ") == "   "

    def test_mixed_special_characters(self):
        """String with multiple special chars should be quoted once"""
        result = _yaml_escape_scalar("test: {value, [1, 2]}")
        assert result.startswith('"')
        assert result.endswith('"')
        assert result.count('"') == 2  # Only outer quotes


class TestYamlList:
    """Test _yaml_list() function"""

    def test_empty_list(self):
        """Empty list should return []"""
        assert _yaml_list([]) == "[]"

    def test_single_string(self):
        """Single string element should be quoted"""
        result = _yaml_list(["test"])
        assert result == '["test"]'

    def test_multiple_strings(self):
        """Multiple strings should be quoted and comma-separated"""
        result = _yaml_list(["a", "b", "c"])
        assert result == '["a", "b", "c"]'

    def test_single_integer(self):
        """Single integer should not be quoted"""
        result = _yaml_list([42])
        assert result == '[42]'

    def test_multiple_integers(self):
        """Multiple integers should not be quoted"""
        result = _yaml_list([1, 2, 3])
        assert result == '[1, 2, 3]'

    def test_single_float(self):
        """Single float should be formatted with 6 decimals"""
        result = _yaml_list([3.14159])
        assert result == '[3.141590]'

    def test_multiple_floats(self):
        """Multiple floats should be formatted correctly"""
        result = _yaml_list([1.5, 2.7, 3.9])
        assert result == '[1.500000, 2.700000, 3.900000]'

    def test_mixed_types(self):
        """Mixed types should be handled correctly"""
        result = _yaml_list(["text", 42, 3.14])
        assert '"text"' in result
        assert '42' in result
        assert '3.140000' in result

    def test_strings_with_quotes_escaped(self):
        """Strings with quotes should be escaped"""
        result = _yaml_list(['He said "hello"'])
        assert '\\"' in result

    def test_unicode_in_list(self):
        """Unicode characters should be preserved"""
        result = _yaml_list(["äöü", "日本語"])
        assert 'äöü' in result
        assert '日本語' in result

    def test_empty_string_in_list(self):
        """Empty strings should be quoted"""
        result = _yaml_list([""])
        assert result == '[""]'

    def test_none_values_converted_to_string(self):
        """None values should be converted to string"""
        result = _yaml_list([None, "test"])
        assert 'None' in result or 'null' in result.lower()

    def test_no_trailing_comma(self):
        """Should not have trailing comma"""
        result = _yaml_list([1, 2, 3])
        assert not result.endswith(',]')
        assert result.endswith(']')

    def test_spaces_after_commas(self):
        """Should have space after commas"""
        result = _yaml_list([1, 2, 3])
        assert ', ' in result

    def test_large_list(self):
        """Should handle large lists"""
        large_list = list(range(100))
        result = _yaml_list(large_list)
        assert result.startswith('[')
        assert result.endswith(']')
        assert '0' in result
        assert '99' in result

    def test_embedding_like_floats(self):
        """Should handle embedding-like float lists"""
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        result = _yaml_list(embedding)
        assert result.startswith('[')
        assert result.endswith(']')
        assert '0.100000' in result
        assert '0.500000' in result


class TestWriteMarkdownWithMetadata:
    """Test write_markdown_with_metadata() function"""

    @pytest.fixture
    def basic_metadata(self):
        """Basic metadata for testing"""
        return {
            'filename': 'test.txt',
            'filepath': '/path/to/test.txt',
            'source_extension': '.txt',
            'source_type': 'text',
            'language': 'en',
            'topic': 'Testing',
            'keywords': ['test', 'python', 'code'],
            'summary': 'A test document for unit testing.',
            'is_prompt': False,
            'is_llm_output': False,
            'git_project': '',
            'created_at': '2025-01-01',
            'wordcount': 42,
            'confidence': 0.95
        }

    def test_creates_markdown_file(self, tmp_path, basic_metadata):
        """Should create a markdown file"""
        original_path = Path('/path/to/test.txt')
        text = "This is the content."

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        assert result.exists()
        assert result.suffix == '.md'
        assert result.parent == tmp_path

    def test_creates_base_directory(self, tmp_path, basic_metadata):
        """Should create base directory if it doesn't exist"""
        base_dir = tmp_path / "output" / "processed"
        original_path = Path('/path/to/test.txt')
        text = "Content"

        result = write_markdown_with_metadata(
            base_dir=base_dir,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        assert base_dir.exists()
        assert result.parent == base_dir

    def test_yaml_frontmatter_structure(self, tmp_path, basic_metadata):
        """Should create valid YAML frontmatter"""
        original_path = Path('/path/to/test.txt')
        text = "Content"

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        content = result.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Should start with ---
        assert lines[0] == '---'

        # Should have closing ---
        assert '---' in lines[1:]

        # Find closing --- position
        closing_idx = lines.index('---', 1)
        frontmatter = '\n'.join(lines[1:closing_idx])

        # Check key fields present
        assert 'filename:' in frontmatter
        assert 'filepath:' in frontmatter
        assert 'language:' in frontmatter
        assert 'topic:' in frontmatter
        assert 'keywords:' in frontmatter

    def test_content_after_frontmatter(self, tmp_path, basic_metadata):
        """Content should appear after frontmatter"""
        original_path = Path('/path/to/test.txt')
        text = "This is the original text content."

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        content = result.read_text(encoding='utf-8')

        # Should have header
        assert '# Originaltext' in content

        # Original text should be present
        assert text in content

    def test_keywords_as_yaml_list(self, tmp_path, basic_metadata):
        """Keywords should be formatted as YAML list"""
        basic_metadata['keywords'] = ['keyword1', 'keyword2', 'keyword3']
        original_path = Path('/path/to/test.txt')
        text = "Content"

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        content = result.read_text(encoding='utf-8')
        assert 'keywords: ["keyword1", "keyword2", "keyword3"]' in content

    def test_boolean_values_formatted(self, tmp_path, basic_metadata):
        """Boolean values should be formatted as true/false"""
        basic_metadata['is_prompt'] = True
        basic_metadata['is_llm_output'] = False
        original_path = Path('/path/to/test.txt')
        text = "Content"

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        content = result.read_text(encoding='utf-8')
        assert 'is_prompt: true' in content
        assert 'is_llm_output: false' in content

    def test_float_confidence_formatted(self, tmp_path, basic_metadata):
        """Float confidence should be formatted with 6 decimals"""
        basic_metadata['confidence'] = 0.87654321
        original_path = Path('/path/to/test.txt')
        text = "Content"

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        content = result.read_text(encoding='utf-8')
        assert 'confidence: 0.876543' in content

    def test_embedding_as_list(self, tmp_path, basic_metadata):
        """Embedding should be formatted as float list"""
        basic_metadata['embedding'] = [0.1, 0.2, 0.3, 0.4, 0.5]
        original_path = Path('/path/to/test.txt')
        text = "Content"

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        content = result.read_text(encoding='utf-8')
        assert 'embedding: [0.100000, 0.200000, 0.300000, 0.400000, 0.500000]' in content

    def test_duplicate_metadata_fields(self, tmp_path, basic_metadata):
        """Should handle duplicate-related metadata fields"""
        basic_metadata['duplicate_of'] = 123
        basic_metadata['similarity_score'] = 0.98
        original_path = Path('/path/to/test.txt')
        text = "Content"

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        content = result.read_text(encoding='utf-8')
        assert 'duplicate_of: 123' in content
        assert 'similarity_score: 0.980000' in content

    def test_slugified_filename(self, tmp_path, basic_metadata):
        """Output filename should be slugified"""
        original_path = Path('/path/to/My Test File (2024).txt')
        text = "Content"

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        # Should not contain spaces or special chars
        assert ' ' not in result.name
        assert '(' not in result.name
        assert ')' not in result.name
        assert result.name.endswith('.md')

    def test_text_with_trailing_newline(self, tmp_path, basic_metadata):
        """Text with trailing newline should be preserved"""
        original_path = Path('/path/to/test.txt')
        text = "Content with newline\n"

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        content = result.read_text(encoding='utf-8')
        assert content.endswith('\n')

    def test_text_without_trailing_newline(self, tmp_path, basic_metadata):
        """Text without trailing newline should get one added"""
        original_path = Path('/path/to/test.txt')
        text = "Content without newline"

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        content = result.read_text(encoding='utf-8')
        # Should end with the text plus a newline
        assert content.rstrip().endswith(text)
        assert content.endswith('\n')

    def test_unicode_content(self, tmp_path, basic_metadata):
        """Should handle Unicode content correctly"""
        original_path = Path('/path/to/test.txt')
        text = "Ümlaute: äöü\n日本語テキスト\nEmoji: 🎉🔥"

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        content = result.read_text(encoding='utf-8')
        assert 'äöü' in content
        assert '日本語' in content
        assert '🎉' in content

    def test_multiline_text_content(self, tmp_path, basic_metadata):
        """Should preserve multiline text content"""
        original_path = Path('/path/to/test.txt')
        text = """Line 1
Line 2
Line 3

Line 5 (with empty line above)"""

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        content = result.read_text(encoding='utf-8')
        assert 'Line 1' in content
        assert 'Line 5' in content
        assert content.count('\n') >= text.count('\n')

    def test_special_yaml_chars_in_metadata(self, tmp_path, basic_metadata):
        """Should properly escape special YAML chars in metadata"""
        basic_metadata['topic'] = 'Testing: Advanced Techniques'
        basic_metadata['summary'] = 'A summary with "quotes" and special chars'
        original_path = Path('/path/to/test.txt')
        text = "Content"

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        content = result.read_text(encoding='utf-8')
        # Should be properly quoted/escaped
        assert 'topic: "Testing: Advanced Techniques"' in content
        assert '\\"' in content  # Quotes should be escaped

    def test_empty_metadata_values(self, tmp_path, basic_metadata):
        """Should handle empty metadata values"""
        basic_metadata['git_project'] = ''
        basic_metadata['keywords'] = []
        original_path = Path('/path/to/test.txt')
        text = "Content"

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        content = result.read_text(encoding='utf-8')
        assert 'git_project:' in content
        assert 'keywords: []' in content

    def test_returns_path_object(self, tmp_path, basic_metadata):
        """Should return Path object"""
        original_path = Path('/path/to/test.txt')
        text = "Content"

        result = write_markdown_with_metadata(
            base_dir=tmp_path,
            original_path=original_path,
            text=text,
            metadata=basic_metadata
        )

        assert isinstance(result, Path)


class TestExporterIntegration:
    """Integration tests for exporter module"""

    def test_complete_export_workflow(self, tmp_path):
        """Test complete export workflow"""
        metadata = {
            'filename': 'document.txt',
            'filepath': '/documents/important/document.txt',
            'source_extension': '.txt',
            'source_type': 'text',
            'language': 'de',
            'topic': 'KI & Machine Learning',
            'keywords': ['AI', 'ML', 'Python'],
            'summary': 'Ein Dokument über "KI" und ML.',
            'is_prompt': True,
            'is_llm_output': False,
            'git_project': 'my-ai-project',
            'created_at': '2025-01-01T12:00:00',
            'wordcount': 150,
            'confidence': 0.92,
            'embedding': [0.1, 0.2, 0.3],
            'duplicate_of': 42,
            'similarity_score': 0.97
        }

        original_text = """# Machine Learning Grundlagen

Dies ist ein Tutorial über Machine Learning.

## Einführung

KI und ML sind wichtige Themen.
"""

        output_dir = tmp_path / "exports"
        original_path = Path('/documents/important/document.txt')

        result = write_markdown_with_metadata(
            base_dir=output_dir,
            original_path=original_path,
            text=original_text,
            metadata=metadata
        )

        # Verify file was created
        assert result.exists()
        assert output_dir.exists()

        # Read and verify content
        content = result.read_text(encoding='utf-8')

        # Check frontmatter
        assert content.startswith('---\n')
        assert 'language: de' in content
        assert 'topic: "KI & Machine Learning"' in content
        assert 'keywords: ["AI", "ML", "Python"]' in content
        assert 'is_prompt: true' in content
        assert 'is_llm_output: false' in content
        assert 'wordcount: 150' in content
        assert 'confidence: 0.920000' in content
        assert 'embedding: [0.100000, 0.200000, 0.300000]' in content
        assert 'duplicate_of: 42' in content
        assert 'similarity_score: 0.970000' in content

        # Check content section
        assert '# Originaltext' in content
        assert '# Machine Learning Grundlagen' in content
        assert 'KI und ML sind wichtige Themen.' in content

    def test_multiple_exports_same_directory(self, tmp_path):
        """Should handle multiple exports to same directory"""
        metadata_base = {
            'filename': 'test.txt',
            'filepath': '/path/test.txt',
            'source_extension': '.txt',
            'source_type': 'text',
            'language': 'en',
            'topic': 'Test',
            'keywords': [],
            'summary': '',
            'wordcount': 10,
            'confidence': 0.9
        }

        for i in range(3):
            metadata = metadata_base.copy()
            metadata['filename'] = f'doc{i}.txt'
            metadata['filepath'] = f'/path/doc{i}.txt'

            result = write_markdown_with_metadata(
                base_dir=tmp_path,
                original_path=Path(metadata['filepath']),
                text=f"Content {i}",
                metadata=metadata
            )

            assert result.exists()

        # Should have 3 files
        md_files = list(tmp_path.glob('*.md'))
        assert len(md_files) == 3
