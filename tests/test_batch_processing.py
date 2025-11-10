#!/usr/bin/env python3
"""
Unit tests for batch processing in the Adastrea Director.

Tests cover:
- Batch document ingestion
- Progress tracking
- Memory efficiency
- Error handling in batch mode
"""

import os
import sys
from unittest.mock import Mock, patch, call
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest import DocumentIngestionAgent


class TestBatchIngestion:
    """Test batch document ingestion functionality."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_batch_ingest_empty_documents(self, agent):
        """Test batch ingestion with empty document list."""
        success = agent.ingest_documents_batch([])
        assert success is False

    def test_batch_ingest_single_batch(self, agent):
        """Test batch ingestion with documents fitting in one batch."""
        mock_chunks = [
            Mock(page_content=f"Chunk {i}", metadata={"source": "test.txt"})
            for i in range(50)
        ]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_vectorstore = Mock()
            mock_chroma.from_documents.return_value = mock_vectorstore
            
            success = agent.ingest_documents_batch(mock_chunks, batch_size=100, show_progress=False)
            
            # Should create vectorstore once for first batch
            mock_chroma.from_documents.assert_called_once()
            mock_vectorstore.persist.assert_called_once()
            assert success is True

    def test_batch_ingest_multiple_batches(self, agent):
        """Test batch ingestion with documents requiring multiple batches."""
        mock_chunks = [
            Mock(page_content=f"Chunk {i}", metadata={"source": "test.txt"})
            for i in range(250)
        ]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_vectorstore = Mock()
            mock_chroma.from_documents.return_value = mock_vectorstore
            mock_chroma.return_value = mock_vectorstore
            
            success = agent.ingest_documents_batch(mock_chunks, batch_size=100, show_progress=False)
            
            # Should create vectorstore once, then add documents twice more
            mock_chroma.from_documents.assert_called_once()
            # Chroma is called for loading vectorstore in batches 2 and 3
            assert mock_chroma.call_count >= 2  # Called at least twice (once from_documents, once for loading)
            assert mock_vectorstore.persist.call_count == 3  # Once per batch
            assert success is True

    def test_batch_size_configuration(self, agent):
        """Test that batch size is respected."""
        mock_chunks = [
            Mock(page_content=f"Chunk {i}", metadata={"source": "test.txt"})
            for i in range(150)
        ]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_vectorstore = Mock()
            mock_chroma.from_documents.return_value = mock_vectorstore
            mock_chroma.return_value = mock_vectorstore
            
            # Test with batch_size=50
            success = agent.ingest_documents_batch(mock_chunks, batch_size=50, show_progress=False)
            
            # Should create 3 batches: 50 + 50 + 50
            assert success is True
            # Verify that add_documents was called for batches 2 and 3
            assert mock_vectorstore.add_documents.call_count == 2

    def test_batch_ingest_with_progress(self, agent):
        """Test batch ingestion with progress bar enabled."""
        mock_chunks = [
            Mock(page_content=f"Chunk {i}", metadata={"source": "test.txt"})
            for i in range(100)
        ]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_vectorstore = Mock()
            mock_chroma.from_documents.return_value = mock_vectorstore
            mock_chroma.return_value = mock_vectorstore
            
            # Just test that batch with progress works without error
            success = agent.ingest_documents_batch(mock_chunks, batch_size=50, show_progress=True)
            
            # Should succeed even with progress bar
            assert success is True

    def test_batch_ingest_error_handling(self, agent):
        """Test error handling during batch ingestion."""
        mock_chunks = [Mock(page_content="Test", metadata={})]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_chroma.from_documents.side_effect = Exception("Batch ingestion error")
            
            success = agent.ingest_documents_batch(mock_chunks, show_progress=False)
            
            assert success is False

    def test_batch_ingest_rate_limit_error(self, agent):
        """Test rate limit error handling in batch mode."""
        mock_chunks = [Mock(page_content="Test", metadata={})]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_chroma.from_documents.side_effect = Exception("rate limit exceeded")
            
            success = agent.ingest_documents_batch(mock_chunks, show_progress=False)
            
            assert success is False

    def test_batch_ingest_preserves_metadata(self, agent):
        """Test that metadata is preserved during batch ingestion."""
        mock_chunks = [
            Mock(
                page_content=f"Chunk {i}",
                metadata={"source": f"test{i}.txt", "doc_type": "code"}
            )
            for i in range(150)
        ]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_vectorstore = Mock()
            mock_chroma.from_documents.return_value = mock_vectorstore
            mock_chroma.return_value = mock_vectorstore
            
            success = agent.ingest_documents_batch(mock_chunks, batch_size=100, show_progress=False)
            
            # Verify first batch call includes metadata
            first_call_docs = mock_chroma.from_documents.call_args[1]['documents']
            assert all(hasattr(doc, 'metadata') for doc in first_call_docs)
            assert success is True


class TestBatchProcessingPerformance:
    """Test performance characteristics of batch processing."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_large_document_set(self, agent):
        """Test batch processing with large document set."""
        # Simulate 1000 documents
        mock_chunks = [
            Mock(page_content=f"Chunk {i}", metadata={"source": "test.txt"})
            for i in range(1000)
        ]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_vectorstore = Mock()
            mock_chroma.from_documents.return_value = mock_vectorstore
            mock_chroma.return_value = mock_vectorstore
            
            success = agent.ingest_documents_batch(
                mock_chunks, 
                batch_size=100, 
                show_progress=False
            )
            
            # Should handle large set without issues
            assert success is True
            # Should have persisted 10 times (1000 / 100)
            assert mock_vectorstore.persist.call_count == 10

    def test_various_batch_sizes(self, agent):
        """Test batch processing with different batch sizes."""
        mock_chunks = [
            Mock(page_content=f"Chunk {i}", metadata={"source": "test.txt"})
            for i in range(300)
        ]
        
        batch_sizes = [50, 100, 150]
        
        for batch_size in batch_sizes:
            with patch('ingest.Chroma') as mock_chroma:
                mock_vectorstore = Mock()
                mock_chroma.from_documents.return_value = mock_vectorstore
                mock_chroma.return_value = mock_vectorstore
                
                success = agent.ingest_documents_batch(
                    mock_chunks,
                    batch_size=batch_size,
                    show_progress=False
                )
                
                expected_batches = (300 + batch_size - 1) // batch_size
                assert success is True
                assert mock_vectorstore.persist.call_count == expected_batches

    def test_batch_memory_efficiency(self, agent):
        """Test that batch processing processes documents incrementally."""
        mock_chunks = [
            Mock(page_content=f"Chunk {i}", metadata={"source": "test.txt"})
            for i in range(500)
        ]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_vectorstore = Mock()
            mock_chroma.from_documents.return_value = mock_vectorstore
            mock_chroma.return_value = mock_vectorstore
            
            # Each batch should be processed separately
            agent.ingest_documents_batch(mock_chunks, batch_size=100, show_progress=False)
            
            # Verify that documents are added in chunks, not all at once
            from_docs_call = mock_chroma.from_documents.call_args
            first_batch = from_docs_call[1]['documents']
            assert len(first_batch) == 100  # First batch should be exactly batch_size


class TestBatchVsRegularIngestion:
    """Compare batch and regular ingestion methods."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_small_set_regular_vs_batch(self, agent):
        """Test that both methods work for small document sets."""
        mock_chunks = [
            Mock(page_content=f"Chunk {i}", metadata={"source": "test.txt"})
            for i in range(50)
        ]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_vectorstore = Mock()
            mock_chroma.from_documents.return_value = mock_vectorstore
            
            # Test regular ingestion
            success1 = agent.ingest_documents(mock_chunks)
            assert success1 is True
            
        with patch('ingest.Chroma') as mock_chroma:
            mock_vectorstore = Mock()
            mock_chroma.from_documents.return_value = mock_vectorstore
            mock_chroma.return_value = mock_vectorstore
            
            # Test batch ingestion
            success2 = agent.ingest_documents_batch(mock_chunks, show_progress=False)
            assert success2 is True

    def test_batch_handles_all_document_types(self, agent):
        """Test that batch ingestion works with different document types."""
        mock_chunks = [
            Mock(page_content="Python code", metadata={"source": "test.py", "doc_type": "code"}),
            Mock(page_content="JavaScript code", metadata={"source": "test.js", "doc_type": "code"}),
            Mock(page_content="Documentation", metadata={"source": "test.md", "doc_type": "documentation"}),
            Mock(page_content="Config", metadata={"source": "config.json", "doc_type": "config"}),
        ] * 50  # Multiply to get 200 documents
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_vectorstore = Mock()
            mock_chroma.from_documents.return_value = mock_vectorstore
            mock_chroma.return_value = mock_vectorstore
            
            success = agent.ingest_documents_batch(mock_chunks, batch_size=100, show_progress=False)
            
            assert success is True
            # Should process in 2 batches
            assert mock_vectorstore.persist.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
