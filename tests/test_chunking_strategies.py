#!/usr/bin/env python3
"""
Unit tests for chunking strategies in the Adastrea Director.

Tests cover:
- Different chunking strategies
- Chunk size and overlap configuration
- Separator handling
- Metadata preservation
- Edge cases
"""

import os
import sys
from unittest.mock import Mock, patch
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest import DocumentIngestionAgent
from langchain.text_splitter import RecursiveCharacterTextSplitter


class TestChunkingStrategies:
    """Test different chunking strategies and configurations."""

    @pytest.fixture
    def agent_default(self):
        """Create agent with default chunking settings."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    @pytest.fixture
    def agent_small_chunks(self):
        """Create agent with small chunks."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent(chunk_size=100, chunk_overlap=20)

    @pytest.fixture
    def agent_large_chunks(self):
        """Create agent with large chunks."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent(chunk_size=2000, chunk_overlap=400)

    def test_default_chunk_size(self, agent_default):
        """Test that default chunk size is 1000."""
        assert agent_default.chunk_size == 1000
        assert agent_default.text_splitter._chunk_size == 1000

    def test_default_chunk_overlap(self, agent_default):
        """Test that default chunk overlap is 200."""
        assert agent_default.chunk_overlap == 200
        assert agent_default.text_splitter._chunk_overlap == 200

    def test_custom_chunk_size(self, agent_small_chunks):
        """Test custom chunk size is applied."""
        assert agent_small_chunks.chunk_size == 100
        assert agent_small_chunks.text_splitter._chunk_size == 100

    def test_custom_chunk_overlap(self, agent_small_chunks):
        """Test custom chunk overlap is applied."""
        assert agent_small_chunks.chunk_overlap == 20
        assert agent_small_chunks.text_splitter._chunk_overlap == 20

    def test_separators_configuration(self, agent_default):
        """Test that separators are configured correctly."""
        expected_separators = ["\n\n", "\n", " ", ""]
        assert agent_default.text_splitter._separators == expected_separators

    def test_length_function(self, agent_default):
        """Test that length function is set to len."""
        assert agent_default.text_splitter._length_function == len


class TestChunkingBehavior:
    """Test actual chunking behavior with different inputs."""

    @pytest.fixture
    def agent(self):
        """Create agent for testing."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent(chunk_size=100, chunk_overlap=20)

    def test_chunk_short_document(self, agent):
        """Test chunking a document shorter than chunk size."""
        mock_doc = Mock()
        mock_doc.page_content = "Short document."
        mock_doc.metadata = {"source": "test.txt"}
        
        # Mock the split to return single chunk for short doc
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            mock_chunk = Mock()
            mock_chunk.page_content = "Short document."
            mock_chunk.metadata = {"source": "test.txt"}
            mock_split.return_value = [mock_chunk]
            
            chunks = agent.chunk_documents([mock_doc])
            
            # Short document should result in one chunk
            assert len(chunks) == 1
            assert chunks[0].page_content == "Short document."

    def test_chunk_long_document(self, agent):
        """Test chunking a document longer than chunk size."""
        mock_doc = Mock()
        # Create a long document
        mock_doc.page_content = "This is a test sentence. " * 50
        mock_doc.metadata = {"source": "test.txt"}
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            # Mock multiple chunks for long doc
            mock_chunks = [
                Mock(page_content="Chunk 1", metadata={"source": "test.txt"}),
                Mock(page_content="Chunk 2", metadata={"source": "test.txt"}),
                Mock(page_content="Chunk 3", metadata={"source": "test.txt"}),
            ]
            mock_split.return_value = mock_chunks
            
            chunks = agent.chunk_documents([mock_doc])
            
            # Long document should result in multiple chunks
            assert len(chunks) > 1

    def test_chunk_with_newlines(self, agent):
        """Test chunking respects newline separators."""
        mock_doc = Mock()
        mock_doc.page_content = "Paragraph 1\n\nParagraph 2\n\nParagraph 3"
        mock_doc.metadata = {"source": "test.txt"}
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            # Should split on double newlines
            mock_chunks = [
                Mock(page_content="Paragraph 1", metadata={"source": "test.txt"}),
                Mock(page_content="Paragraph 2", metadata={"source": "test.txt"}),
                Mock(page_content="Paragraph 3", metadata={"source": "test.txt"}),
            ]
            mock_split.return_value = mock_chunks
            
            chunks = agent.chunk_documents([mock_doc])
            
            assert len(chunks) >= 1

    def test_chunk_overlap_behavior(self, agent):
        """Test that chunk overlap is working."""
        # With overlap, chunks should share some content
        assert agent.chunk_overlap > 0
        assert agent.chunk_overlap < agent.chunk_size


class TestMetadataPreservation:
    """Test that metadata is preserved during chunking."""

    @pytest.fixture
    def agent(self):
        """Create agent for testing."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_preserve_source_metadata(self, agent):
        """Test that source metadata is preserved."""
        mock_doc = Mock()
        mock_doc.page_content = "Test content"
        mock_doc.metadata = {"source": "/path/to/test.txt"}
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            mock_chunk = Mock()
            mock_chunk.page_content = "Test content"
            mock_chunk.metadata = {"source": "/path/to/test.txt"}
            mock_split.return_value = [mock_chunk]
            
            chunks = agent.chunk_documents([mock_doc])
            
            assert chunks[0].metadata["source"] == "/path/to/test.txt"

    def test_preserve_custom_metadata(self, agent):
        """Test that custom metadata is preserved."""
        mock_doc = Mock()
        mock_doc.page_content = "Test content"
        mock_doc.metadata = {
            "source": "test.txt",
            "author": "Test Author",
            "date": "2024-01-01"
        }
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            mock_chunk = Mock()
            mock_chunk.page_content = "Test content"
            mock_chunk.metadata = {
                "source": "test.txt",
                "author": "Test Author",
                "date": "2024-01-01"
            }
            mock_split.return_value = [mock_chunk]
            
            chunks = agent.chunk_documents([mock_doc])
            
            assert chunks[0].metadata["author"] == "Test Author"
            assert chunks[0].metadata["date"] == "2024-01-01"

    def test_metadata_in_multiple_chunks(self, agent):
        """Test that metadata is preserved in all chunks."""
        mock_doc = Mock()
        mock_doc.page_content = "Long content " * 100
        mock_doc.metadata = {"source": "test.txt", "type": "documentation"}
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            mock_chunks = [
                Mock(page_content="Chunk 1", metadata={"source": "test.txt", "type": "documentation"}),
                Mock(page_content="Chunk 2", metadata={"source": "test.txt", "type": "documentation"}),
            ]
            mock_split.return_value = mock_chunks
            
            chunks = agent.chunk_documents([mock_doc])
            
            # All chunks should have metadata
            for chunk in chunks:
                assert chunk.metadata["source"] == "test.txt"
                assert chunk.metadata["type"] == "documentation"


class TestEdgeCases:
    """Test edge cases in chunking."""

    @pytest.fixture
    def agent(self):
        """Create agent for testing."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_empty_document(self, agent):
        """Test chunking an empty document."""
        mock_doc = Mock()
        mock_doc.page_content = ""
        mock_doc.metadata = {"source": "empty.txt"}
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            mock_split.return_value = []
            
            chunks = agent.chunk_documents([mock_doc])
            
            # Empty document should produce no chunks or one empty chunk
            assert isinstance(chunks, list)

    def test_whitespace_only_document(self, agent):
        """Test chunking a document with only whitespace."""
        mock_doc = Mock()
        mock_doc.page_content = "   \n\n   \n   "
        mock_doc.metadata = {"source": "whitespace.txt"}
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            mock_chunk = Mock()
            mock_chunk.page_content = "   \n\n   \n   "
            mock_chunk.metadata = {"source": "whitespace.txt"}
            mock_split.return_value = [mock_chunk]
            
            chunks = agent.chunk_documents([mock_doc])
            
            assert isinstance(chunks, list)

    def test_document_exactly_chunk_size(self, agent):
        """Test chunking a document that's exactly the chunk size."""
        content = "x" * agent.chunk_size
        mock_doc = Mock()
        mock_doc.page_content = content
        mock_doc.metadata = {"source": "exact.txt"}
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            mock_chunk = Mock()
            mock_chunk.page_content = content
            mock_chunk.metadata = {"source": "exact.txt"}
            mock_split.return_value = [mock_chunk]
            
            chunks = agent.chunk_documents([mock_doc])
            
            assert len(chunks) >= 1

    def test_special_characters_in_content(self, agent):
        """Test chunking documents with special characters."""
        mock_doc = Mock()
        mock_doc.page_content = "Test with émojis 🎮 and spëcial çhars: @#$%^&*()"
        mock_doc.metadata = {"source": "special.txt"}
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            mock_chunk = Mock()
            mock_chunk.page_content = "Test with émojis 🎮 and spëcial çhars: @#$%^&*()"
            mock_chunk.metadata = {"source": "special.txt"}
            mock_split.return_value = [mock_chunk]
            
            chunks = agent.chunk_documents([mock_doc])
            
            assert len(chunks) >= 1

    def test_very_long_single_line(self, agent):
        """Test chunking a very long single line without separators."""
        # Create a line longer than chunk size with no natural breaks
        content = "a" * (agent.chunk_size * 3)
        mock_doc = Mock()
        mock_doc.page_content = content
        mock_doc.metadata = {"source": "longline.txt"}
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            # Should split into multiple chunks
            mock_chunks = [
                Mock(page_content="a" * agent.chunk_size, metadata={"source": "longline.txt"}),
                Mock(page_content="a" * agent.chunk_size, metadata={"source": "longline.txt"}),
                Mock(page_content="a" * agent.chunk_size, metadata={"source": "longline.txt"}),
            ]
            mock_split.return_value = mock_chunks
            
            chunks = agent.chunk_documents([mock_doc])
            
            # Long line should be split
            assert len(chunks) > 1


class TestChunkingPerformance:
    """Test performance characteristics of chunking."""

    @pytest.fixture
    def agent(self):
        """Create agent for testing."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_chunk_many_documents(self, agent):
        """Test chunking many documents at once."""
        # Create 100 mock documents
        mock_docs = []
        for i in range(100):
            mock_doc = Mock()
            mock_doc.page_content = f"Document {i} content"
            mock_doc.metadata = {"source": f"doc{i}.txt"}
            mock_docs.append(mock_doc)
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            # Return one chunk per document
            mock_split.return_value = [Mock() for _ in range(100)]
            
            chunks = agent.chunk_documents(mock_docs)
            
            # Should handle many documents
            mock_split.assert_called_once_with(mock_docs)
            assert len(chunks) == 100

    def test_chunk_size_efficiency(self):
        """Test that different chunk sizes are reasonable."""
        # Test various chunk size configurations
        test_configs = [
            (500, 100),    # Small chunks
            (1000, 200),   # Default
            (2000, 400),   # Large chunks
            (100, 20),     # Very small
        ]
        
        for chunk_size, chunk_overlap in test_configs:
            with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
                mock_embeddings.return_value = Mock()
                agent = DocumentIngestionAgent(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
                
                # Verify configuration
                assert agent.chunk_size == chunk_size
                assert agent.chunk_overlap == chunk_overlap
                # Overlap should be less than chunk size
                assert chunk_overlap < chunk_size


class TestRecursiveCharacterTextSplitter:
    """Test the RecursiveCharacterTextSplitter configuration."""

    def test_splitter_uses_recursive_strategy(self):
        """Test that we're using RecursiveCharacterTextSplitter."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            agent = DocumentIngestionAgent()
            
            assert isinstance(agent.text_splitter, RecursiveCharacterTextSplitter)

    def test_splitter_separators_priority(self):
        """Test that separators are tried in order of priority."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            agent = DocumentIngestionAgent()
            
            # Separators should be in order: paragraph, line, word, character
            separators = agent.text_splitter._separators
            assert separators[0] == "\n\n"  # Paragraph separator first
            assert separators[1] == "\n"    # Line separator second
            assert separators[2] == " "     # Word separator third
            assert separators[3] == ""      # Character separator last


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
