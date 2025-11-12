#!/usr/bin/env python3
"""
Unit tests for incremental document ingestion in the Adastrea Director.

Tests cover:
- File hash calculation
- Change detection based on file hashes
- Incremental ingestion (skip unchanged, update changed, add new files)
- Force re-ingestion flag
- Document deletion by source
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest import DocumentIngestionAgent


class TestFileHashing:
    """Test file hash calculation functionality."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_calculate_file_hash(self, agent):
        """Test that file hash is calculated correctly."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content for hashing")
            temp_file = f.name
        
        try:
            hash1 = agent._calculate_file_hash(temp_file)
            assert hash1
            assert len(hash1) == 64  # SHA-256 produces 64 hex characters
            
            # Hash should be consistent
            hash2 = agent._calculate_file_hash(temp_file)
            assert hash1 == hash2
        finally:
            os.unlink(temp_file)

    def test_calculate_file_hash_different_content(self, agent):
        """Test that different content produces different hashes."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Content A")
            temp_file1 = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Content B")
            temp_file2 = f.name
        
        try:
            hash1 = agent._calculate_file_hash(temp_file1)
            hash2 = agent._calculate_file_hash(temp_file2)
            assert hash1 != hash2
        finally:
            os.unlink(temp_file1)
            os.unlink(temp_file2)

    def test_calculate_file_hash_nonexistent_file(self, agent):
        """Test that hash calculation handles nonexistent files gracefully."""
        hash_result = agent._calculate_file_hash("/nonexistent/file.txt")
        assert hash_result == ""


class TestChangeDetection:
    """Test change detection based on file hashes."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_check_file_changed_force_reingest(self, agent):
        """Test that force_reingest always returns True."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content")
            temp_file = f.name
        
        try:
            has_changed, old_hash, current_hash = agent._check_file_changed(temp_file, force_reingest=True)
            assert has_changed is True
            assert old_hash is None
            assert current_hash  # Hash should be calculated
        finally:
            os.unlink(temp_file)

    def test_check_file_changed_new_file(self, agent):
        """Test change detection for a new file (not in database)."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("New file content")
            temp_file = f.name
        
        try:
            with patch.object(agent, '_calculate_file_hash') as mock_hash:
                mock_hash.return_value = "abc123"
                
                # Mock Chroma to return no existing documents
                with patch('ingest.Chroma') as mock_chroma:
                    mock_collection = Mock()
                    mock_collection.get.return_value = {"metadatas": []}
                    mock_vectorstore = Mock()
                    mock_vectorstore._collection = mock_collection
                    mock_chroma.return_value = mock_vectorstore
                    
                    has_changed, old_hash, current_hash = agent._check_file_changed(temp_file, force_reingest=False)
                    
                    assert has_changed is True
                    assert old_hash is None
                    assert current_hash == "abc123"
        finally:
            os.unlink(temp_file)

    def test_check_file_changed_unchanged_file(self, agent):
        """Test change detection for an unchanged file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Unchanged content")
            temp_file = f.name
        
        try:
            with patch.object(agent, '_calculate_file_hash') as mock_hash:
                mock_hash.return_value = "abc123"
                
                # Mock Chroma to return existing document with same hash
                with patch('ingest.Chroma') as mock_chroma:
                    mock_collection = Mock()
                    mock_collection.get.return_value = {
                        "metadatas": [{"file_hash": "abc123", "source": temp_file}]
                    }
                    mock_vectorstore = Mock()
                    mock_vectorstore._collection = mock_collection
                    mock_chroma.return_value = mock_vectorstore
                    
                    has_changed, old_hash, current_hash = agent._check_file_changed(temp_file, force_reingest=False)
                    
                    assert has_changed is False
                    assert old_hash == "abc123"
                    assert current_hash == "abc123"
        finally:
            os.unlink(temp_file)

    def test_check_file_changed_modified_file(self, agent):
        """Test change detection for a modified file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Modified content")
            temp_file = f.name
        
        try:
            with patch.object(agent, '_calculate_file_hash') as mock_hash:
                mock_hash.return_value = "newHash456"
                
                # Mock Chroma to return existing document with different hash
                with patch('ingest.Chroma') as mock_chroma:
                    mock_collection = Mock()
                    mock_collection.get.return_value = {
                        "metadatas": [{"file_hash": "oldHash123", "source": temp_file}]
                    }
                    mock_vectorstore = Mock()
                    mock_vectorstore._collection = mock_collection
                    mock_chroma.return_value = mock_vectorstore
                    
                    has_changed, old_hash, current_hash = agent._check_file_changed(temp_file, force_reingest=False)
                    
                    assert has_changed is True
                    assert old_hash == "oldHash123"
                    assert current_hash == "newHash456"
        finally:
            os.unlink(temp_file)


class TestDocumentDeletion:
    """Test document deletion by source."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_delete_document_by_source(self, agent):
        """Test deletion of document chunks by source."""
        with patch('ingest.Chroma') as mock_chroma:
            mock_collection = Mock()
            mock_collection.get.return_value = {
                "ids": ["id1", "id2", "id3"]
            }
            mock_vectorstore = Mock()
            mock_vectorstore._collection = mock_collection
            mock_chroma.return_value = mock_vectorstore
            
            result = agent._delete_document_by_source("/path/to/file.txt")
            
            assert result is True
            mock_collection.delete.assert_called_once_with(ids=["id1", "id2", "id3"])

    def test_delete_document_by_source_not_found(self, agent):
        """Test deletion when document is not found."""
        with patch('ingest.Chroma') as mock_chroma:
            mock_collection = Mock()
            mock_collection.get.return_value = {"ids": []}
            mock_vectorstore = Mock()
            mock_vectorstore._collection = mock_collection
            mock_chroma.return_value = mock_vectorstore
            
            result = agent._delete_document_by_source("/path/to/nonexistent.txt")
            
            assert result is False
            mock_collection.delete.assert_not_called()


class TestMetadataEnrichment:
    """Test metadata enrichment with file hashes."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_enrich_metadata_with_hash(self, agent):
        """Test that file hash is added to metadata."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content")
            temp_file = f.name
        
        try:
            mock_doc = Mock()
            mock_doc.metadata = {"source": temp_file}
            
            documents = agent._enrich_document_metadata([mock_doc], file_hash="abc123def")
            
            assert "file_hash" in documents[0].metadata
            assert documents[0].metadata["file_hash"] == "abc123def"
        finally:
            os.unlink(temp_file)

    def test_enrich_metadata_calculates_hash_if_not_provided(self, agent):
        """Test that hash is calculated if not provided."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content")
            temp_file = f.name
        
        try:
            mock_doc = Mock()
            mock_doc.metadata = {"source": temp_file}
            
            with patch.object(agent, '_calculate_file_hash') as mock_hash:
                mock_hash.return_value = "calculated_hash"
                
                documents = agent._enrich_document_metadata([mock_doc])
                
                assert "file_hash" in documents[0].metadata
                assert documents[0].metadata["file_hash"] == "calculated_hash"
                mock_hash.assert_called_once_with(temp_file)
        finally:
            os.unlink(temp_file)


class TestIncrementalIngestion:
    """Test incremental ingestion functionality."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_get_file_list(self, agent):
        """Test getting list of supported files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            (Path(temp_dir) / "test.txt").write_text("Test")
            (Path(temp_dir) / "test.py").write_text("# Python")
            (Path(temp_dir) / "test.md").write_text("# Markdown")
            (Path(temp_dir) / "test.unsupported").write_text("Unsupported")
            
            file_list = agent._get_file_list(temp_dir)
            
            assert len(file_list) == 3
            assert any("test.txt" in f for f in file_list)
            assert any("test.py" in f for f in file_list)
            assert any("test.md" in f for f in file_list)
            assert not any("test.unsupported" in f for f in file_list)

    def test_incremental_ingestion_skip_unchanged(self, agent):
        """Test that unchanged files are skipped."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Unchanged content")
            
            with patch.object(agent, '_get_file_list') as mock_get_files:
                mock_get_files.return_value = [str(test_file)]
                
                with patch.object(agent, '_check_file_changed') as mock_check:
                    mock_check.return_value = (False, "hash123", "hash123")  # File unchanged
                    
                    stats = agent.ingest_directory_incremental(temp_dir, delay_between_files=0)
                    
                    assert stats['skipped'] == 1
                    assert stats['added'] == 0
                    assert stats['updated'] == 0

    def test_incremental_ingestion_add_new_file(self, agent):
        """Test that new files are added."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "new.txt"
            test_file.write_text("New content")
            
            with patch.object(agent, '_get_file_list') as mock_get_files:
                mock_get_files.return_value = [str(test_file)]
                
                with patch.object(agent, '_check_file_changed') as mock_check:
                    mock_check.return_value = (True, None, "new_hash")  # New file
                    
                    with patch.object(agent, 'load_single_file') as mock_load:
                        mock_doc = Mock()
                        mock_doc.page_content = "New content"
                        mock_doc.metadata = {"source": str(test_file)}
                        mock_load.return_value = [mock_doc]
                        
                        with patch.object(agent, 'chunk_documents') as mock_chunk:
                            mock_chunk.return_value = [mock_doc]
                            
                            with patch('ingest.Chroma') as mock_chroma:
                                mock_vectorstore = Mock()
                                mock_chroma.from_documents.return_value = mock_vectorstore
                                
                                stats = agent.ingest_directory_incremental(temp_dir, delay_between_files=0)
                                
                                assert stats['added'] == 1
                                assert stats['skipped'] == 0
                                assert stats['updated'] == 0

    def test_incremental_ingestion_update_changed_file(self, agent):
        """Test that changed files are updated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "changed.txt"
            test_file.write_text("Modified content")
            
            with patch.object(agent, '_get_file_list') as mock_get_files:
                mock_get_files.return_value = [str(test_file)]
                
                with patch.object(agent, '_check_file_changed') as mock_check:
                    mock_check.return_value = (True, "old_hash", "new_hash")  # File changed
                    
                    with patch.object(agent, 'load_single_file') as mock_load:
                        mock_doc = Mock()
                        mock_doc.page_content = "Modified content"
                        mock_doc.metadata = {"source": str(test_file)}
                        mock_load.return_value = [mock_doc]
                        
                        with patch.object(agent, 'chunk_documents') as mock_chunk:
                            mock_chunk.return_value = [mock_doc]
                            
                            with patch.object(agent, '_delete_document_by_source') as mock_delete:
                                mock_delete.return_value = True
                                
                                with patch('ingest.Chroma') as mock_chroma:
                                    mock_vectorstore = Mock()
                                    mock_chroma.return_value = mock_vectorstore
                                    
                                    # Mock Path.exists to return True
                                    with patch('pathlib.Path.exists', return_value=True):
                                        stats = agent.ingest_directory_incremental(temp_dir, delay_between_files=0)
                                        
                                        assert stats['updated'] == 1
                                        assert stats['skipped'] == 0
                                        assert stats['added'] == 0
                                        mock_delete.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
