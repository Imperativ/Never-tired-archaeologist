# -*- coding: utf-8 -*-
"""
Basic tests for llm_providers module.
Full integration tests require actual API keys.
"""
import pytest
from llm_providers import (
    MultiProvider,
    LLMProviderError,
    RateLimitError
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


class TestMultiProviderBasics:
    """Basic tests for MultiProvider (without SDKs)"""
    
    def test_initialization_without_sdks_raises_error(self):
        """Should raise error if SDKs not installed"""
        with pytest.raises(LLMProviderError, match="not installed"):
            MultiProvider()
    
    def test_module_imports(self):
        """Module should export expected classes"""
        from llm_providers import (
            AnalysisProvider,
            EmbeddingProvider,
            ClaudeProvider,
            GeminiProvider,
            get_default_provider
        )
        
        assert AnalysisProvider is not None
        assert EmbeddingProvider is not None
        assert ClaudeProvider is not None
        assert GeminiProvider is not None
        assert get_default_provider is not None


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
