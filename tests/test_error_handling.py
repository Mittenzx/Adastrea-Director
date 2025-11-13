#!/usr/bin/env python3
"""
Unit tests for error handling in the Adastrea Director.

Tests cover:
- Missing API keys
- Invalid file paths
- Network errors
- Database errors
- Invalid configurations
- Exception handling
"""

import os
import sys
from unittest.mock import Mock, patch
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest import DocumentIngestionAgent
from main import QueryAgent
from exceptions import (
    APIKeyError,
    ValidationError,
    ChunkingError,
)


class TestAPIKeyErrors:
    """Test error handling for missing or invalid API keys.
    
    With HuggingFace as the default provider, API keys are only required
    when explicitly using OpenAI embeddings via EMBEDDING_PROVIDER=openai.
    """

    @patch.dict(os.environ, {}, clear=True)
    def test_huggingface_no_key_required_ingest(self):
        """Test that HuggingFace embeddings work without API keys."""
        # Mock HuggingFace embeddings to avoid downloading models
        with patch('langchain_community.embeddings.HuggingFaceEmbeddings') as mock_hf:
            mock_hf.return_value = Mock()
            
            # Should succeed without any API key
            agent = DocumentIngestionAgent()
            assert agent is not None

    @patch.dict(os.environ, {'EMBEDDING_PROVIDER': 'openai'}, clear=True)
    def test_missing_openai_key_when_provider_selected(self):
        """Test that missing OpenAI key is handled when OpenAI provider is explicitly selected."""
        # Mock OpenAI to simulate missing key error
        with patch('langchain_openai.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.side_effect = Exception("API key not found")
            
            # Should exit with error when OpenAI is selected but key is missing
            with pytest.raises(SystemExit):
                DocumentIngestionAgent()

    def test_invalid_api_key_format(self):
        """Test handling of invalid API key format when using OpenAI embeddings.
        
        This test is only relevant when EMBEDDING_PROVIDER=openai.
        By default, HuggingFace embeddings are used (no API key required).
        """
        # Mock OpenAI embeddings to simulate API key error
        with patch('langchain_openai.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.side_effect = Exception("Invalid API key format")
            
            # Set environment to use OpenAI
            with patch.dict(os.environ, {'EMBEDDING_PROVIDER': 'openai'}):
                with pytest.raises(SystemExit):
                    # Should exit with error when OpenAI is configured but key is invalid
                    DocumentIngestionAgent()


class TestFilePathErrors:
    """Test error handling for file path issues.
    
    Uses HuggingFace embeddings by default (no API key required).
    """

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        # Use mock embeddings to avoid downloading models during tests
        mock_embeddings = Mock()
        return DocumentIngestionAgent(embeddings=mock_embeddings)

    def test_nonexistent_directory(self, agent):
        """Test loading from nonexistent directory."""
        result = agent.load_documents_from_directory("/this/path/does/not/exist")
        assert result == []

    def test_nonexistent_file(self, agent):
        """Test loading nonexistent file."""
        result = agent.load_single_file("/this/file/does/not/exist.txt")
        assert result == []

    def test_invalid_path_characters(self, agent):
        """Test handling paths with invalid characters."""
        # Different invalid paths for different platforms
        invalid_paths = [
            "/path/with/\x00/null",
            "",  # Empty path
        ]
        
        for path in invalid_paths:
            if path:  # Skip empty path for directory test
                result = agent.load_documents_from_directory(path)
                assert isinstance(result, list)

    def test_path_permission_error(self, agent):
        """Test handling permission errors."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            with patch('ingest.DirectoryLoader') as mock_loader:
                mock_loader.side_effect = PermissionError("Permission denied")
                
                # Should handle error gracefully
                result = agent.load_documents_from_directory("/protected/path")
                assert isinstance(result, list)


class TestDatabaseErrors:
    """Test error handling for database operations."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_database_connection_error(self, agent):
        """Test handling database connection errors."""
        mock_chunks = [Mock(page_content="Test", metadata={})]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_chroma.from_documents.side_effect = Exception("Connection refused")
            
            result = agent.ingest_documents(mock_chunks)
            
            assert result is False

    def test_database_write_error(self, agent):
        """Test handling database write errors."""
        mock_chunks = [Mock(page_content="Test", metadata={})]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_vectorstore = Mock()
            mock_vectorstore.persist.side_effect = Exception("Write failed")
            mock_chroma.from_documents.return_value = mock_vectorstore
            
            result = agent.ingest_documents(mock_chunks)
            
            assert result is False

    def test_database_stats_error(self, agent):
        """Test handling errors when getting database stats."""
        with patch('ingest.Chroma') as mock_chroma:
            mock_chroma.side_effect = Exception("Stats retrieval failed")
            
            stats = agent.get_database_stats()
            
            assert stats == {}

    def test_empty_database_query(self):
        """Test querying empty database."""
        with patch('main.OpenAIEmbeddings') as mock_embeddings, \
             patch('main.Chroma') as mock_chroma, \
             patch('main.sys.exit') as mock_exit:
            
            mock_embeddings.return_value = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 0  # Empty database
            mock_vectorstore = Mock()
            mock_vectorstore._collection = mock_collection
            mock_chroma.return_value = mock_vectorstore
            
            QueryAgent()
            
            # Should exit when database is empty
            mock_exit.assert_called_with(1)


class TestNetworkErrors:
    """Test error handling for network-related issues."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_embedding_api_timeout(self, agent):
        """Test handling API timeout during embedding."""
        mock_chunks = [Mock(page_content="Test", metadata={})]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_chroma.from_documents.side_effect = TimeoutError("API timeout")
            
            result = agent.ingest_documents(mock_chunks)
            
            assert result is False

    def test_embedding_api_rate_limit(self, agent):
        """Test handling API rate limit errors."""
        mock_chunks = [Mock(page_content="Test", metadata={})]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_chroma.from_documents.side_effect = Exception("Rate limit exceeded")
            
            result = agent.ingest_documents(mock_chunks)
            
            assert result is False

    def test_query_api_network_error(self):
        """Test handling network errors during query."""
        with patch('main.OpenAIEmbeddings') as mock_embeddings, \
             patch('main.ChatOpenAI') as mock_llm, \
             patch('main.Chroma') as mock_chroma, \
             patch('main.ConversationalRetrievalChain') as mock_chain:
            
            mock_embeddings.return_value = Mock()
            mock_llm.return_value = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 10
            mock_vectorstore = Mock()
            mock_vectorstore._collection = mock_collection
            mock_vectorstore.as_retriever.return_value = Mock()
            mock_chroma.return_value = mock_vectorstore
            mock_chain.from_llm.return_value = Mock()
            
            agent = QueryAgent()
            agent.qa_chain = Mock()
            agent.qa_chain.side_effect = Exception("Network error")
            
            result = agent.process_query("Test query")
            
            assert "error" in result["answer"].lower()


class TestConfigurationErrors:
    """Test error handling for invalid configurations."""

    def test_invalid_chunk_size(self):
        """Test handling invalid chunk size."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            
            # Negative chunk size should raise ValidationError
            with pytest.raises(ValidationError):
                DocumentIngestionAgent(chunk_size=-100)

    def test_invalid_chunk_overlap(self):
        """Test handling invalid chunk overlap."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            
            # Overlap larger than chunk size should raise ValidationError
            with pytest.raises(ValidationError):
                DocumentIngestionAgent(chunk_size=100, chunk_overlap=200)

    def test_invalid_collection_name(self):
        """Test handling invalid collection name."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            
            # Empty collection name
            agent = DocumentIngestionAgent(collection_name="")
            assert agent.collection_name == ""

    def test_invalid_persist_directory(self):
        """Test handling invalid persist directory."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            
            # Invalid directory path
            agent = DocumentIngestionAgent(persist_directory="/invalid/\x00/path")
            assert agent.persist_directory == "/invalid/\x00/path"


class TestDocumentLoadingErrors:
    """Test error handling during document loading."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_corrupted_file_loading(self, agent):
        """Test handling corrupted files."""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('ingest.TextLoader') as mock_loader:
            
            mock_exists.return_value = True
            mock_loader.return_value.load.side_effect = Exception("Corrupted file")
            
            result = agent.load_single_file("/path/to/corrupted.txt")
            
            assert result == []

    def test_unsupported_encoding(self, agent):
        """Test handling files with unsupported encoding."""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('ingest.TextLoader') as mock_loader:
            
            mock_exists.return_value = True
            mock_loader.return_value.load.side_effect = UnicodeDecodeError(
                'utf-8', b'', 0, 1, 'invalid start byte'
            )
            
            result = agent.load_single_file("/path/to/file.txt")
            
            assert result == []

    def test_loader_import_error(self, agent):
        """Test handling missing loader dependencies."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            with patch('ingest.PyPDFLoader') as mock_loader:
                mock_loader.side_effect = ImportError("PyPDF2 not installed")
                
                # Should return empty list on error
                result = agent.load_single_file("/path/to/file.pdf")
                assert result == []

    def test_directory_loader_error(self, agent):
        """Test handling errors in directory loading."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            with patch('ingest.DirectoryLoader') as mock_loader:
                mock_loader.return_value.load.side_effect = Exception("Load error")
                
                result = agent.load_documents_from_directory("/path/to/dir")
                
                # Should handle error and continue
                assert isinstance(result, list)


class TestChunkingErrors:
    """Test error handling during chunking."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_chunking_with_none_documents(self, agent):
        """Test chunking with None in document list."""
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            mock_split.side_effect = AttributeError("'NoneType' object has no attribute")
            
            with pytest.raises(ChunkingError):
                agent.chunk_documents([None])

    def test_chunking_with_invalid_document(self, agent):
        """Test chunking with invalid document object."""
        invalid_doc = "not a document object"
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            mock_split.side_effect = AttributeError("Invalid document")
            
            with pytest.raises(ChunkingError):
                agent.chunk_documents([invalid_doc])

    def test_chunking_memory_error(self, agent):
        """Test handling memory errors during chunking."""
        mock_doc = Mock()
        mock_doc.page_content = "x" * 10000000  # Very large content
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            mock_split.side_effect = MemoryError("Not enough memory")
            
            with pytest.raises(ChunkingError):
                agent.chunk_documents([mock_doc])


class TestQueryErrors:
    """Test error handling during query processing."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('main.OpenAIEmbeddings') as mock_embeddings, \
             patch('main.ChatOpenAI') as mock_llm, \
             patch('main.Chroma') as mock_chroma, \
             patch('main.ConversationalRetrievalChain') as mock_chain:
            
            mock_embeddings.return_value = Mock()
            mock_llm.return_value = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 10
            mock_vectorstore = Mock()
            mock_vectorstore._collection = mock_collection
            mock_vectorstore.as_retriever.return_value = Mock()
            mock_chroma.return_value = mock_vectorstore
            mock_chain.from_llm.return_value = Mock()
            
            return QueryAgent()

    def test_empty_query_string(self, agent):
        """Test processing empty query string."""
        agent.qa_chain = Mock()
        agent.qa_chain.return_value = {
            "answer": "Please provide a question.",
            "source_documents": []
        }
        
        result = agent.process_query("")
        
        assert result is not None
        assert "answer" in result

    def test_very_long_query(self, agent):
        """Test processing very long query."""
        long_query = "What is " * 1000  # Very long query
        
        agent.qa_chain = Mock()
        agent.qa_chain.return_value = {
            "answer": "Query processed",
            "source_documents": []
        }
        
        result = agent.process_query(long_query)
        
        assert result is not None

    def test_special_characters_in_query(self, agent):
        """Test processing query with special characters."""
        special_query = "What about émojis 🎮 and spëcial çhars?"
        
        agent.qa_chain = Mock()
        agent.qa_chain.return_value = {
            "answer": "Answer with special chars",
            "source_documents": []
        }
        
        result = agent.process_query(special_query)
        
        assert result is not None

    def test_llm_api_error(self, agent):
        """Test handling LLM API errors."""
        agent.qa_chain = Mock()
        agent.qa_chain.side_effect = Exception("LLM API error")
        
        result = agent.process_query("Test query")
        
        assert "error" in result["answer"].lower()
        assert result["source_documents"] == []


class TestRecoveryMechanisms:
    """Test error recovery mechanisms."""

    def test_retry_on_transient_failure(self):
        """Test that transient failures can be retried."""
        # This test demonstrates that the system allows retries
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            # First call fails, second succeeds
            mock_embeddings.side_effect = [
                Exception("Transient error"),
                Mock()
            ]
            
            # First attempt fails
            with patch('ingest.sys.exit'):
                DocumentIngestionAgent()
            
            # Second attempt succeeds
            agent = DocumentIngestionAgent()
            assert agent is not None

    def test_graceful_degradation(self):
        """Test that system degrades gracefully on errors."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            agent = DocumentIngestionAgent()
            
            # Even with errors, system should not crash
            result = agent.load_documents_from_directory("/nonexistent")
            assert result == []  # Returns empty list, doesn't crash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
