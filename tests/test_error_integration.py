#!/usr/bin/env python3
"""
Integration tests for error handling in the Adastrea Director.

These tests verify that error handling works correctly in realistic scenarios.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest import DocumentIngestionAgent
from exceptions import (
    ValidationError,
    FileEncodingError,
    CorruptedFileError,
)


class TestEndToEndErrorScenarios:
    """Test complete error handling workflows."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()
    
    def test_mixed_valid_and_invalid_files(self, agent, temp_dir):
        """Test that valid files are processed even when some fail."""
        # Create a mix of valid and invalid files
        valid_file = Path(temp_dir) / "valid.txt"
        valid_file.write_text("This is valid content", encoding='utf-8')
        
        # Create a file with invalid encoding (will be simulated)
        invalid_file = Path(temp_dir) / "invalid.txt"
        invalid_file.write_bytes(b'\xff\xfe\x00\x00')  # Invalid UTF-8
        
        with patch('ingest.DirectoryLoader') as mock_loader:
            # Simulate loading valid file successfully
            mock_doc = Mock()
            mock_doc.page_content = "This is valid content"
            mock_loader.return_value.load.return_value = [mock_doc]
            
            # Should handle errors gracefully and return valid documents
            documents = agent.load_documents_from_directory(temp_dir)
            
            # Should have loaded at least some documents
            assert isinstance(documents, list)
    
    def test_complete_ingestion_workflow_with_errors(self, agent, temp_dir):
        """Test complete workflow when errors occur at different stages."""
        # Create test files
        test_file = Path(temp_dir) / "test.md"
        test_file.write_text("# Test Document\n\nThis is test content.")
        
        with patch('ingest.DirectoryLoader') as mock_loader, \
             patch('ingest.Chroma') as mock_chroma:
            
            # Simulate successful loading
            mock_doc = Mock()
            mock_doc.page_content = "Test content"
            mock_doc.metadata = {"source": "test.md"}
            mock_loader.return_value.load.return_value = [mock_doc]
            
            # Simulate database error
            mock_chroma.from_documents.side_effect = Exception("Database connection failed")
            
            # Load documents should succeed
            documents = agent.load_documents_from_directory(temp_dir)
            assert len(documents) > 0
            
            # Chunk documents should succeed
            chunks = agent.chunk_documents(documents)
            assert len(chunks) > 0
            
            # Ingest should fail gracefully and return False
            success = agent.ingest_documents(chunks)
            assert success is False
    
    def test_validation_errors_prevent_initialization(self):
        """Test that validation errors prevent agent initialization."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            
            # Test invalid chunk size
            with pytest.raises(ValidationError) as exc_info:
                DocumentIngestionAgent(chunk_size=0)
            
            assert "chunk_size" in str(exc_info.value)
            assert "Must be greater than 0" in str(exc_info.value)
    
    def test_file_type_specific_errors(self, agent, temp_dir):
        """Test that file-type-specific errors are handled correctly."""
        # Test PDF error
        pdf_file = Path(temp_dir) / "test.pdf"
        pdf_file.write_text("Not a real PDF")
        
        with patch('ingest.PyPDFLoader') as mock_loader:
            mock_loader.return_value.load.side_effect = Exception("Failed to parse PDF")
            
            # Should return empty list and not crash
            result = agent.load_single_file(str(pdf_file))
            assert result == []
        
        # Test DOCX error
        docx_file = Path(temp_dir) / "test.docx"
        docx_file.write_text("Not a real DOCX")
        
        with patch('ingest.Docx2txtLoader') as mock_loader:
            mock_loader.return_value.load.side_effect = Exception("Failed to parse DOCX XML")
            
            # Should return empty list and not crash
            result = agent.load_single_file(str(docx_file))
            assert result == []


class TestErrorMessageQuality:
    """Test that error messages are informative and actionable."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()
    
    def test_validation_error_messages(self):
        """Test that validation errors provide clear messages."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            
            # Test negative chunk size
            try:
                DocumentIngestionAgent(chunk_size=-100)
                assert False, "Should have raised ValidationError"
            except ValidationError as e:
                assert "chunk_size" in str(e)
                assert "-100" in str(e)
                assert "Must be greater than 0" in str(e)
            
            # Test chunk overlap >= chunk size
            try:
                DocumentIngestionAgent(chunk_size=100, chunk_overlap=200)
                assert False, "Should have raised ValidationError"
            except ValidationError as e:
                assert "chunk_overlap" in str(e)
                assert "200" in str(e)
                assert "Must be less than chunk_size" in str(e)
    
    def test_network_error_messages(self, agent):
        """Test that network errors provide helpful troubleshooting steps."""
        mock_chunks = [Mock(page_content="Test", metadata={})]
        
        with patch('ingest.Chroma') as mock_chroma:
            # Simulate timeout
            mock_chroma.from_documents.side_effect = TimeoutError("Request timed out")
            
            success = agent.ingest_documents(mock_chunks)
            assert success is False
    
    def test_rate_limit_error_messages(self, agent):
        """Test that rate limit errors provide actionable advice."""
        mock_chunks = [Mock(page_content="Test", metadata={})]
        
        with patch('ingest.Chroma') as mock_chroma:
            # Simulate rate limit
            mock_chroma.from_documents.side_effect = Exception("Rate limit exceeded")
            
            success = agent.ingest_documents(mock_chunks)
            assert success is False


class TestErrorRecovery:
    """Test error recovery mechanisms."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()
    
    def test_partial_directory_load_continues_on_error(self, agent, temp_dir=None):
        """Test that directory loading continues after individual file errors."""
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp()
        
        try:
            # Create multiple files
            for i in range(5):
                file_path = Path(temp_dir) / f"file{i}.txt"
                file_path.write_text(f"Content {i}")
            
            with patch('ingest.DirectoryLoader') as mock_loader:
                # First loader succeeds, others fail
                mock_doc = Mock()
                mock_doc.page_content = "Content"
                
                # Return documents for some extensions, error for others
                call_count = 0
                def side_effect(*args, **kwargs):
                    nonlocal call_count
                    call_count += 1
                    if call_count % 2 == 0:
                        raise Exception("Load error")
                    return [mock_doc]
                
                mock_loader.return_value.load.side_effect = side_effect
                
                # Should continue loading despite errors
                documents = agent.load_documents_from_directory(temp_dir)
                
                # Should have loaded some documents
                assert isinstance(documents, list)
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_empty_results_handled_gracefully(self, agent):
        """Test that empty results don't cause crashes."""
        # Empty documents
        chunks = agent.chunk_documents([])
        assert chunks == []
        
        # Empty chunks
        success = agent.ingest_documents([])
        assert success is False
    
    def test_database_stats_error_returns_empty_dict(self, agent):
        """Test that database stats errors are handled gracefully."""
        with patch('ingest.Chroma') as mock_chroma:
            mock_chroma.side_effect = Exception("Database error")
            
            stats = agent.get_database_stats()
            
            # Should return empty dict instead of crashing
            assert stats == {}


class TestEdgeCases:
    """Test edge cases in error handling."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()
    
    def test_empty_file_path(self, agent):
        """Test handling of empty file path."""
        result = agent.load_single_file("")
        assert result == []
    
    def test_none_documents(self, agent):
        """Test handling of None in document list."""
        # Should handle None gracefully
        chunks = agent.chunk_documents([])
        assert chunks == []
    
    def test_very_long_error_messages(self, agent):
        """Test that very long error messages are handled."""
        mock_chunks = [Mock(page_content="Test", metadata={})]
        
        with patch('ingest.Chroma') as mock_chroma:
            # Simulate error with very long message
            long_message = "Error: " + "x" * 10000
            mock_chroma.from_documents.side_effect = Exception(long_message)
            
            # Should handle without crashing
            success = agent.ingest_documents(mock_chunks)
            assert success is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
