# -*- coding: utf-8 -*-
"""
Comprehensive tests for llm_providers module.
Tests focus on logic that can be tested without requiring external SDKs.
Full integration tests with real APIs are skipped by default.
"""
import pytest
import os
from unittest.mock import Mock, MagicMock, patch
from llm_providers import (
    MultiProvider,
    LLMProviderError,
    RateLimitError,
    AnalysisProvider,
    EmbeddingProvider
)


class TestExceptions:
    """Test custom exceptions"""

    def test_llm_provider_error_exists(self):
        """LLMProviderError should be defined"""
        error = LLMProviderError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_rate_limit_error_exists(self):
        """RateLimitError should be subclass of LLMProviderError"""
        error = RateLimitError("Rate limit exceeded")
        assert isinstance(error, LLMProviderError)
        assert isinstance(error, Exception)
        assert str(error) == "Rate limit exceeded"


class TestAbstractProviders:
    """Test abstract base classes"""

    def test_analysis_provider_is_abstract(self):
        """AnalysisProvider should be abstract"""
        assert hasattr(AnalysisProvider, 'analyze_text')
        # Cannot instantiate abstract class
        with pytest.raises(TypeError):
            AnalysisProvider()

    def test_embedding_provider_is_abstract(self):
        """EmbeddingProvider should be abstract"""
        assert hasattr(EmbeddingProvider, 'generate_embedding')
        assert hasattr(EmbeddingProvider, 'generate_embeddings_batch')
        # Cannot instantiate abstract class
        with pytest.raises(TypeError):
            EmbeddingProvider()


class TestMultiProviderWithMocks:
    """Test MultiProvider with mocked providers"""

    def test_initialization_with_custom_providers(self):
        """Should accept custom providers"""
        mock_analysis = Mock(spec=AnalysisProvider)
        mock_embedding = Mock(spec=EmbeddingProvider)

        provider = MultiProvider(
            analysis_provider=mock_analysis,
            embedding_provider=mock_embedding
        )

        assert provider.analysis_provider == mock_analysis
        assert provider.embedding_provider == mock_embedding

    def test_analyze_document_calls_analysis_provider(self):
        """Should call analysis provider"""
        mock_analysis = Mock(spec=AnalysisProvider)
        mock_analysis.analyze_text.return_value = {
            'language': 'en',
            'topic': 'Testing',
            'keywords': ['test', 'pytest'],
            'summary': 'A test document',
            'is_prompt': False,
            'is_llm_output': False,
            'git_project': '',
            'confidence': 0.92
        }

        mock_embedding = Mock(spec=EmbeddingProvider)
        mock_embedding.generate_embedding.return_value = [0.1, 0.2, 0.3]

        provider = MultiProvider(
            analysis_provider=mock_analysis,
            embedding_provider=mock_embedding
        )

        metadata, embedding = provider.analyze_document(
            text='Test content',
            filename='test.txt',
            source_extension='.txt',
            source_type='text',
            generate_embedding=True
        )

        # Verify analysis was called
        mock_analysis.analyze_text.assert_called_once_with(
            text='Test content',
            filename='test.txt',
            source_extension='.txt',
            source_type='text'
        )

        # Verify results
        assert metadata['language'] == 'en'
        assert metadata['topic'] == 'Testing'
        assert metadata['keywords'] == ['test', 'pytest']
        assert metadata['confidence'] == 0.92
        assert embedding == [0.1, 0.2, 0.3]

    def test_analyze_document_calls_embedding_provider_when_enabled(self):
        """Should call embedding provider when embeddings enabled"""
        mock_analysis = Mock(spec=AnalysisProvider)
        mock_analysis.analyze_text.return_value = {
            'language': 'en', 'topic': 'Test', 'keywords': [],
            'summary': '', 'is_prompt': False, 'is_llm_output': False,
            'git_project': '', 'confidence': 0.9
        }

        mock_embedding = Mock(spec=EmbeddingProvider)
        mock_embedding.generate_embedding.return_value = [0.5, 0.6, 0.7]

        provider = MultiProvider(
            analysis_provider=mock_analysis,
            embedding_provider=mock_embedding
        )

        metadata, embedding = provider.analyze_document(
            text='Test',
            filename='test.txt',
            source_extension='.txt',
            source_type='text',
            generate_embedding=True
        )

        # Verify embedding was generated
        mock_embedding.generate_embedding.assert_called_once_with('Test')
        assert embedding == [0.5, 0.6, 0.7]

    def test_analyze_document_skips_embedding_when_disabled(self):
        """Should skip embedding generation when disabled"""
        mock_analysis = Mock(spec=AnalysisProvider)
        mock_analysis.analyze_text.return_value = {
            'language': 'de', 'topic': 'Test', 'keywords': [],
            'summary': '', 'is_prompt': False, 'is_llm_output': False,
            'git_project': '', 'confidence': 0.85
        }

        mock_embedding = Mock(spec=EmbeddingProvider)

        provider = MultiProvider(
            analysis_provider=mock_analysis,
            embedding_provider=mock_embedding
        )

        metadata, embedding = provider.analyze_document(
            text='Test',
            filename='test.txt',
            source_extension='.txt',
            source_type='text',
            generate_embedding=False
        )

        # Embedding should not be called
        mock_embedding.generate_embedding.assert_not_called()
        assert embedding is None

    def test_analyze_document_continues_on_embedding_rate_limit(self):
        """Should continue with analysis even if embedding rate limited"""
        mock_analysis = Mock(spec=AnalysisProvider)
        mock_analysis.analyze_text.return_value = {
            'language': 'fr', 'topic': 'Rate Limit Test', 'keywords': ['test'],
            'summary': 'Testing rate limits', 'is_prompt': False,
            'is_llm_output': False, 'git_project': '', 'confidence': 0.88
        }

        mock_embedding = Mock(spec=EmbeddingProvider)
        mock_embedding.generate_embedding.side_effect = RateLimitError("Quota exceeded")

        provider = MultiProvider(
            analysis_provider=mock_analysis,
            embedding_provider=mock_embedding
        )

        metadata, embedding = provider.analyze_document(
            text='Test content',
            filename='test.txt',
            source_extension='.txt',
            source_type='text',
            generate_embedding=True
        )

        # Should have metadata but no embedding
        assert metadata['language'] == 'fr'
        assert metadata['topic'] == 'Rate Limit Test'
        assert embedding is None

    def test_analyze_document_preserves_all_metadata_fields(self):
        """Should preserve all metadata fields from analysis"""
        expected_metadata = {
            'language': 'es',
            'topic': 'Complex Topic',
            'keywords': ['word1', 'word2', 'word3'],
            'summary': 'Detailed summary of the document',
            'is_prompt': True,
            'is_llm_output': False,
            'git_project': 'my-project',
            'confidence': 0.97
        }

        mock_analysis = Mock(spec=AnalysisProvider)
        mock_analysis.analyze_text.return_value = expected_metadata

        mock_embedding = Mock(spec=EmbeddingProvider)

        provider = MultiProvider(
            analysis_provider=mock_analysis,
            embedding_provider=mock_embedding
        )

        metadata, _ = provider.analyze_document(
            text='Content',
            filename='test.py',
            source_extension='.py',
            source_type='python',
            generate_embedding=False
        )

        # All fields should be preserved
        assert metadata == expected_metadata

    def test_analyze_document_passes_correct_parameters(self):
        """Should pass all parameters correctly to analysis provider"""
        mock_analysis = Mock(spec=AnalysisProvider)
        mock_analysis.analyze_text.return_value = {
            'language': 'en', 'topic': 'Test', 'keywords': [],
            'summary': '', 'is_prompt': False, 'is_llm_output': False,
            'git_project': '', 'confidence': 0.9
        }

        mock_embedding = Mock(spec=EmbeddingProvider)

        provider = MultiProvider(
            analysis_provider=mock_analysis,
            embedding_provider=mock_embedding
        )

        provider.analyze_document(
            text='Sample text content',
            filename='sample.md',
            source_extension='.md',
            source_type='markdown',
            generate_embedding=False
        )

        # Verify exact parameters passed
        mock_analysis.analyze_text.assert_called_once()
        call_args = mock_analysis.analyze_text.call_args
        assert call_args[1]['text'] == 'Sample text content'
        assert call_args[1]['filename'] == 'sample.md'
        assert call_args[1]['source_extension'] == '.md'
        assert call_args[1]['source_type'] == 'markdown'


class TestModuleExports:
    """Test module exports and availability"""

    def test_all_classes_exported(self):
        """All expected classes should be exportable"""
        from llm_providers import (
            AnalysisProvider,
            EmbeddingProvider,
            ClaudeProvider,
            GeminiProvider,
            MultiProvider,
            LLMProviderError,
            RateLimitError,
            get_default_provider
        )

        assert AnalysisProvider is not None
        assert EmbeddingProvider is not None
        assert ClaudeProvider is not None
        assert GeminiProvider is not None
        assert MultiProvider is not None
        assert LLMProviderError is not None
        assert RateLimitError is not None
        assert callable(get_default_provider)

    def test_exceptions_hierarchy(self):
        """Exception hierarchy should be correct"""
        assert issubclass(RateLimitError, LLMProviderError)
        assert issubclass(LLMProviderError, Exception)


class TestProviderInitializationErrors:
    """Test provider initialization error handling"""

    def test_claude_provider_requires_anthropic_sdk(self):
        """ClaudeProvider should raise error if anthropic not installed"""
        # This will fail if anthropic is actually installed
        from llm_providers import ClaudeProvider

        # If SDK is not installed, initialization should fail
        with pytest.raises(LLMProviderError):
            ClaudeProvider()

    def test_gemini_provider_requires_genai_sdk(self):
        """GeminiProvider should raise error if google-genai not installed"""
        # This will fail if google-genai is actually installed
        from llm_providers import GeminiProvider

        # If SDK is not installed, initialization should fail
        with pytest.raises(LLMProviderError):
            GeminiProvider()

    def test_multi_provider_requires_both_sdks_for_default(self):
        """MultiProvider should raise error if SDKs not installed"""
        # Without SDKs, default initialization should fail
        with pytest.raises(LLMProviderError):
            MultiProvider()


@pytest.mark.skip(reason="Requires API keys - run manually only")
class TestRealIntegration:
    """
    Real integration tests - requires actual API keys.
    Run with: pytest tests/test_llm_providers.py::TestRealIntegration -v
    after setting ANTHROPIC_API_KEY and GOOGLE_API_KEY
    """

    def test_claude_provider_real(self):
        """Test Claude provider with real API"""
        from llm_providers import ClaudeProvider

        provider = ClaudeProvider()
        result = provider.analyze_text(
            text="This is a test document in English about Python programming.",
            filename="test.py",
            source_extension=".py",
            source_type="code"
        )

        assert 'language' in result
        assert result['language'] == 'en'
        assert 'topic' in result
        assert 'keywords' in result
        assert isinstance(result['keywords'], list)

    def test_gemini_provider_real(self):
        """Test Gemini provider with real API"""
        from llm_providers import GeminiProvider

        provider = GeminiProvider()
        embedding = provider.generate_embedding("Test text for embedding")

        assert isinstance(embedding, list)
        assert len(embedding) == 768  # Default dimensionality
        assert all(isinstance(x, float) for x in embedding[:10])

    def test_multi_provider_real(self):
        """Test complete workflow with real APIs"""
        from llm_providers import get_default_provider

        provider = get_default_provider()
        metadata, embedding = provider.analyze_document(
            text="Python is a high-level programming language.",
            filename="intro.txt",
            source_extension=".txt",
            source_type="text",
            generate_embedding=True
        )

        assert metadata['language'] == 'en'
        assert 'programming' in ' '.join(metadata['keywords']).lower() or 'python' in ' '.join(metadata['keywords']).lower()
        assert embedding is not None
        assert len(embedding) == 768
