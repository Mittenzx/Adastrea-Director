#!/usr/bin/env python3
"""
Unit tests for embedding provider selection in the Adastrea Director.

Tests cover:
- Default HuggingFace embeddings
- OpenAI embeddings via environment variable
- Custom HuggingFace model selection
- Custom embeddings passed to constructor
- Error handling for missing packages
"""

import os
import sys
from unittest.mock import Mock, patch
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEmbeddingProviderSelection:
    """Test embedding provider selection logic."""

    def test_default_uses_huggingface(self):
        """Test that HuggingFace embeddings are used by default."""
        # Clear any existing environment variables
        env_backup = {}
        for key in ['EMBEDDING_PROVIDER', 'OPENAI_API_KEY', 'HUGGINGFACE_MODEL_NAME']:
            env_backup[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]
        
        try:
            # Patch where HuggingFaceEmbeddings is imported FROM
            with patch('langchain_community.embeddings.HuggingFaceEmbeddings') as mock_hf:
                mock_hf.return_value = Mock()
                from ingest import DocumentIngestionAgent
                
                agent = DocumentIngestionAgent()
                
                # Verify HuggingFaceEmbeddings was called with default model
                mock_hf.assert_called_once_with(model_name='all-MiniLM-L6-v2')
                assert agent.embeddings == mock_hf.return_value
        finally:
            # Restore environment
            for key, value in env_backup.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]

    def test_custom_huggingface_model(self):
        """Test using a custom HuggingFace model via environment variable."""
        custom_model = "sentence-transformers/all-mpnet-base-v2"
        
        env_backup = os.environ.get('HUGGINGFACE_MODEL_NAME')
        os.environ['HUGGINGFACE_MODEL_NAME'] = custom_model
        
        try:
            with patch('langchain_community.embeddings.HuggingFaceEmbeddings') as mock_hf:
                mock_hf.return_value = Mock()
                from ingest import DocumentIngestionAgent
                
                agent = DocumentIngestionAgent()
                
                # Verify HuggingFaceEmbeddings was called with custom model
                mock_hf.assert_called_once_with(model_name=custom_model)
        finally:
            if env_backup is not None:
                os.environ['HUGGINGFACE_MODEL_NAME'] = env_backup
            elif 'HUGGINGFACE_MODEL_NAME' in os.environ:
                del os.environ['HUGGINGFACE_MODEL_NAME']

    def test_openai_provider_selection(self):
        """Test selecting OpenAI embeddings via environment variable."""
        env_backup = {
            'EMBEDDING_PROVIDER': os.environ.get('EMBEDDING_PROVIDER'),
            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
        }
        
        os.environ['EMBEDDING_PROVIDER'] = 'openai'
        os.environ['OPENAI_API_KEY'] = 'test-key'
        
        try:
            with patch('langchain_openai.OpenAIEmbeddings') as mock_openai:
                mock_openai.return_value = Mock()
                from ingest import DocumentIngestionAgent
                
                agent = DocumentIngestionAgent()
                
                # Verify OpenAIEmbeddings was called
                mock_openai.assert_called_once()
                assert agent.embeddings == mock_openai.return_value
        finally:
            for key, value in env_backup.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]

    def test_custom_embeddings_parameter(self):
        """Test passing custom embeddings to constructor."""
        custom_embeddings = Mock()
        
        # Mock HuggingFace and OpenAI embeddings imports to ensure consistent behavior
        with patch('langchain_community.embeddings.HuggingFaceEmbeddings', new=Mock()), \
             patch('langchain_openai.OpenAIEmbeddings', new=Mock()):
            from ingest import DocumentIngestionAgent
            agent = DocumentIngestionAgent(embeddings=custom_embeddings)
            
            # Verify custom embeddings were used
            assert agent.embeddings == custom_embeddings

    def test_huggingface_import_error_handling(self):
        """Test error handling when HuggingFaceEmbeddings raises an ImportError."""
        env_backup = os.environ.get('EMBEDDING_PROVIDER')
        if 'EMBEDDING_PROVIDER' in os.environ:
            del os.environ['EMBEDDING_PROVIDER']
        
        try:
            # Mock ImportError when trying to instantiate HuggingFaceEmbeddings
            # We patch the class to raise an ImportError when called (not imported)
            import langchain_community.embeddings
            
            def mock_hf_init(*args, **kwargs):
                raise ImportError("No module named 'sentence_transformers'")
            
            with patch.object(langchain_community.embeddings, 'HuggingFaceEmbeddings', side_effect=mock_hf_init):
                from ingest import DocumentIngestionAgent
                
                with pytest.raises(SystemExit):
                    DocumentIngestionAgent()
        finally:
            if env_backup is not None:
                os.environ['EMBEDDING_PROVIDER'] = env_backup

    def test_openai_missing_api_key(self):
        """Test error handling when OpenAI is selected but API key is missing."""
        env_backup = {
            'EMBEDDING_PROVIDER': os.environ.get('EMBEDDING_PROVIDER'),
            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
        }
        
        os.environ['EMBEDDING_PROVIDER'] = 'openai'
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        try:
            with patch('langchain_openai.OpenAIEmbeddings', side_effect=Exception("API key not found")):
                from ingest import DocumentIngestionAgent
                from exceptions import APIKeyError
                
                with pytest.raises((SystemExit, APIKeyError)):
                    DocumentIngestionAgent()
        finally:
            for key, value in env_backup.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]


class TestEmbeddingProviderCaseInsensitive:
    """Test that provider selection is case-insensitive."""

    def test_hf_lowercase(self):
        """Test 'hf' as provider."""
        os.environ['EMBEDDING_PROVIDER'] = 'hf'
        try:
            with patch('langchain_community.embeddings.HuggingFaceEmbeddings') as mock_hf:
                mock_hf.return_value = Mock()
                from ingest import DocumentIngestionAgent
                DocumentIngestionAgent()
                assert mock_hf.called
        finally:
            if 'EMBEDDING_PROVIDER' in os.environ:
                del os.environ['EMBEDDING_PROVIDER']

    def test_huggingface_full(self):
        """Test 'huggingface' as provider."""
        os.environ['EMBEDDING_PROVIDER'] = 'huggingface'
        try:
            with patch('langchain_community.embeddings.HuggingFaceEmbeddings') as mock_hf:
                mock_hf.return_value = Mock()
                from ingest import DocumentIngestionAgent
                DocumentIngestionAgent()
                assert mock_hf.called
        finally:
            if 'EMBEDDING_PROVIDER' in os.environ:
                del os.environ['EMBEDDING_PROVIDER']

    def test_openai_mixed_case(self):
        """Test 'OpenAI' with mixed case."""
        os.environ['EMBEDDING_PROVIDER'] = 'OpenAI'
        os.environ['OPENAI_API_KEY'] = 'test-key'
        try:
            with patch('langchain_openai.OpenAIEmbeddings') as mock_openai:
                mock_openai.return_value = Mock()
                from ingest import DocumentIngestionAgent
                DocumentIngestionAgent()
                assert mock_openai.called
        finally:
            for key in ['EMBEDDING_PROVIDER', 'OPENAI_API_KEY']:
                if key in os.environ:
                    del os.environ[key]


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""

    def test_agent_initialization_without_embeddings_param(self):
        """Test that agent can be initialized without embeddings parameter."""
        with patch('langchain_community.embeddings.HuggingFaceEmbeddings') as mock_hf:
            mock_hf.return_value = Mock()
            from ingest import DocumentIngestionAgent
            
            # Old style initialization should still work
            agent = DocumentIngestionAgent(
                collection_name="test_collection",
                persist_directory="./test_db",
                chunk_size=500,
                chunk_overlap=100,
            )
            
            assert agent.collection_name == "test_collection"
            assert agent.persist_directory == "./test_db"
            assert agent.chunk_size == 500
            assert agent.chunk_overlap == 100
            assert mock_hf.called

    def test_ingest_game_repo_compatibility(self):
        """Test that ingest_game_repo.py pattern still works."""
        with patch('langchain_community.embeddings.HuggingFaceEmbeddings') as mock_hf:
            mock_hf.return_value = Mock()
            from ingest import DocumentIngestionAgent
            
            # Pattern used in ingest_game_repo.py
            agent = DocumentIngestionAgent(
                collection_name="adastrea_game_docs",
                persist_directory="./chroma_db_adastrea",
                chunk_size=1000,
                chunk_overlap=200,
            )
            
            assert agent.embeddings is not None
            assert mock_hf.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
