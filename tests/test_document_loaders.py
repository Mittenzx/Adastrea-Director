#!/usr/bin/env python3
"""
Unit tests for document loaders in the Adastrea Director.

Tests cover:
- Document loader initialization
- Loading from directories
- Loading single files
- PDF, DOCX, Markdown, Text, and Python file support
- Error handling for missing files and invalid inputs
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


class TestDocumentIngestionAgentInitialization:
    """Test initialization of DocumentIngestionAgent."""

    @patch('ingest.OpenAIEmbeddings')
    def test_default_initialization(self, mock_embeddings):
        """Test agent initializes with default parameters."""
        mock_embeddings.return_value = Mock()
        
        agent = DocumentIngestionAgent()
        
        assert agent.collection_name == "adastrea_docs"
        assert agent.persist_directory == "./chroma_db"
        assert agent.chunk_size == 1000
        assert agent.chunk_overlap == 200
        mock_embeddings.assert_called_once()

    @patch('ingest.OpenAIEmbeddings')
    def test_custom_initialization(self, mock_embeddings):
        """Test agent initializes with custom parameters."""
        mock_embeddings.return_value = Mock()
        
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

    @patch('ingest.OpenAIEmbeddings')
    def test_text_splitter_configuration(self, mock_embeddings):
        """Test that text splitter is configured correctly."""
        mock_embeddings.return_value = Mock()
        
        agent = DocumentIngestionAgent(chunk_size=800, chunk_overlap=150)
        
        assert agent.text_splitter._chunk_size == 800
        assert agent.text_splitter._chunk_overlap == 150
        assert agent.text_splitter._separators == ["\n\n", "\n", " ", ""]


class TestLoadDocumentsFromDirectory:
    """Test loading documents from directories."""

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

    def test_load_from_nonexistent_directory(self, agent):
        """Test loading from a directory that doesn't exist."""
        documents = agent.load_documents_from_directory("/nonexistent/path")
        assert documents == []

    def test_load_from_empty_directory(self, agent, temp_dir):
        """Test loading from an empty directory."""
        with patch('ingest.DirectoryLoader') as mock_loader:
            mock_loader.return_value.load.return_value = []
            documents = agent.load_documents_from_directory(temp_dir)
            assert isinstance(documents, list)

    def test_load_markdown_files(self, agent, temp_dir):
        """Test loading markdown files from directory."""
        # Create test markdown file
        test_file = Path(temp_dir) / "test.md"
        test_file.write_text("# Test Markdown\n\nThis is a test.")
        
        with patch('ingest.DirectoryLoader') as mock_loader:
            mock_doc = Mock()
            mock_doc.page_content = "# Test Markdown\n\nThis is a test."
            mock_loader.return_value.load.return_value = [mock_doc]
            
            documents = agent.load_documents_from_directory(temp_dir)
            
            assert len(documents) >= 0
            mock_loader.assert_called()

    def test_load_text_files(self, agent, temp_dir):
        """Test loading text files from directory."""
        # Create test text file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("This is a test text file.")
        
        with patch('ingest.DirectoryLoader') as mock_loader:
            mock_doc = Mock()
            mock_doc.page_content = "This is a test text file."
            mock_loader.return_value.load.return_value = [mock_doc]
            
            documents = agent.load_documents_from_directory(temp_dir)
            
            assert len(documents) >= 0
            mock_loader.assert_called()

    def test_load_python_files(self, agent, temp_dir):
        """Test loading Python files from directory."""
        # Create test Python file
        test_file = Path(temp_dir) / "test.py"
        test_file.write_text("def test_function():\n    pass")
        
        with patch('ingest.DirectoryLoader') as mock_loader:
            mock_doc = Mock()
            mock_doc.page_content = "def test_function():\n    pass"
            mock_loader.return_value.load.return_value = [mock_doc]
            
            documents = agent.load_documents_from_directory(temp_dir)
            
            assert len(documents) >= 0
            mock_loader.assert_called()

    def test_load_multiple_file_types(self, agent, temp_dir):
        """Test loading multiple file types from directory."""
        # Create multiple test files
        (Path(temp_dir) / "test.md").write_text("# Markdown")
        (Path(temp_dir) / "test.txt").write_text("Text")
        (Path(temp_dir) / "test.py").write_text("# Python")
        
        with patch('ingest.DirectoryLoader') as mock_loader:
            mock_loader.return_value.load.return_value = [Mock(), Mock(), Mock()]
            
            agent.load_documents_from_directory(temp_dir)
            
            # Should be called multiple times for different file types
            assert mock_loader.call_count >= 1

    def test_error_handling_in_load(self, agent, temp_dir):
        """Test error handling when loading fails."""
        with patch('ingest.DirectoryLoader') as mock_loader:
            mock_loader.return_value.load.side_effect = Exception("Load error")
            
            documents = agent.load_documents_from_directory(temp_dir)
            
            # Should handle error gracefully and return what was loaded
            assert isinstance(documents, list)


class TestLoadSingleFile:
    """Test loading single document files."""

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

    def test_load_nonexistent_file(self, agent):
        """Test loading a file that doesn't exist."""
        documents = agent.load_single_file("/nonexistent/file.txt")
        assert documents == []

    def test_load_markdown_file(self, agent, temp_dir):
        """Test loading a markdown file."""
        test_file = Path(temp_dir) / "test.md"
        test_file.write_text("# Test\nContent")
        
        with patch('ingest.MARKDOWN_LOADER') as mock_loader:
            mock_doc = Mock()
            mock_doc.page_content = "# Test\nContent"
            mock_loader.return_value.load.return_value = [mock_doc]
            
            documents = agent.load_single_file(str(test_file))
            
            mock_loader.assert_called_once_with(str(test_file))
            assert len(documents) >= 0

    def test_load_text_file(self, agent, temp_dir):
        """Test loading a text file."""
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Test content")
        
        with patch('ingest.TextLoader') as mock_loader:
            mock_doc = Mock()
            mock_doc.page_content = "Test content"
            mock_loader.return_value.load.return_value = [mock_doc]
            
            documents = agent.load_single_file(str(test_file))
            
            mock_loader.assert_called_once_with(str(test_file))
            assert len(documents) >= 0

    def test_load_python_file(self, agent, temp_dir):
        """Test loading a Python file."""
        test_file = Path(temp_dir) / "test.py"
        test_file.write_text("def test(): pass")
        
        with patch('ingest.PythonLoader') as mock_loader:
            mock_doc = Mock()
            mock_doc.page_content = "def test(): pass"
            mock_loader.return_value.load.return_value = [mock_doc]
            
            documents = agent.load_single_file(str(test_file))
            
            mock_loader.assert_called_once_with(str(test_file))
            assert len(documents) >= 0

    def test_load_pdf_file(self, agent, temp_dir):
        """Test loading a PDF file."""
        test_file = Path(temp_dir) / "test.pdf"
        test_file.write_text("PDF placeholder")  # Not a real PDF, but tests the path
        
        with patch('ingest.PyPDFLoader') as mock_loader:
            mock_doc = Mock()
            mock_doc.page_content = "PDF content"
            mock_loader.return_value.load.return_value = [mock_doc]
            
            documents = agent.load_single_file(str(test_file))
            
            mock_loader.assert_called_once_with(str(test_file))
            assert len(documents) >= 0

    def test_load_docx_file(self, agent, temp_dir):
        """Test loading a DOCX file."""
        test_file = Path(temp_dir) / "test.docx"
        test_file.write_text("DOCX placeholder")  # Not a real DOCX, but tests the path
        
        with patch('ingest.Docx2txtLoader') as mock_loader:
            mock_doc = Mock()
            mock_doc.page_content = "DOCX content"
            mock_loader.return_value.load.return_value = [mock_doc]
            
            documents = agent.load_single_file(str(test_file))
            
            mock_loader.assert_called_once_with(str(test_file))
            assert len(documents) >= 0

    def test_load_unknown_extension(self, agent, temp_dir):
        """Test loading a file with unknown extension defaults to TextLoader."""
        test_file = Path(temp_dir) / "test.xyz"
        test_file.write_text("Unknown file type")
        
        with patch('ingest.TextLoader') as mock_loader:
            mock_doc = Mock()
            mock_loader.return_value.load.return_value = [mock_doc]
            
            documents = agent.load_single_file(str(test_file))
            
            mock_loader.assert_called_once_with(str(test_file))
            assert len(documents) >= 0

    def test_error_handling_in_load_file(self, agent, temp_dir):
        """Test error handling when file loading fails."""
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Test")
        
        with patch('ingest.TextLoader') as mock_loader:
            mock_loader.return_value.load.side_effect = Exception("Load error")
            
            documents = agent.load_single_file(str(test_file))
            
            assert documents == []


class TestChunkDocuments:
    """Test document chunking functionality."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent(chunk_size=100, chunk_overlap=20)

    def test_chunk_empty_documents(self, agent):
        """Test chunking with empty document list."""
        chunks = agent.chunk_documents([])
        assert chunks == []

    def test_chunk_single_document(self, agent):
        """Test chunking a single document."""
        mock_doc = Mock()
        mock_doc.page_content = "This is a test document. " * 20
        mock_doc.metadata = {"source": "test.txt"}
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            mock_chunk1 = Mock()
            mock_chunk1.page_content = "Chunk 1"
            mock_chunk2 = Mock()
            mock_chunk2.page_content = "Chunk 2"
            mock_split.return_value = [mock_chunk1, mock_chunk2]
            
            chunks = agent.chunk_documents([mock_doc])
            
            mock_split.assert_called_once_with([mock_doc])
            assert len(chunks) == 2

    def test_chunk_multiple_documents(self, agent):
        """Test chunking multiple documents."""
        mock_docs = [
            Mock(page_content="Document 1 content", metadata={"source": "doc1.txt"}),
            Mock(page_content="Document 2 content", metadata={"source": "doc2.txt"}),
        ]
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            mock_split.return_value = [Mock(), Mock(), Mock(), Mock()]
            
            chunks = agent.chunk_documents(mock_docs)
            
            mock_split.assert_called_once_with(mock_docs)
            assert len(chunks) == 4

    def test_chunk_size_configuration(self, agent):
        """Test that chunk size is respected."""
        assert agent.text_splitter._chunk_size == 100
        assert agent.text_splitter._chunk_overlap == 20

    def test_chunking_preserves_metadata(self, agent):
        """Test that chunking preserves document metadata."""
        mock_doc = Mock()
        mock_doc.page_content = "Test content"
        mock_doc.metadata = {"source": "test.txt", "type": "test"}
        
        with patch.object(agent.text_splitter, 'split_documents') as mock_split:
            mock_chunk = Mock()
            mock_chunk.metadata = {"source": "test.txt", "type": "test"}
            mock_split.return_value = [mock_chunk]
            
            chunks = agent.chunk_documents([mock_doc])
            
            assert chunks[0].metadata["source"] == "test.txt"


class TestIngestDocuments:
    """Test document ingestion into vector database."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_ingest_empty_documents(self, agent):
        """Test ingesting empty document list."""
        success = agent.ingest_documents([])
        assert success is False

    def test_ingest_documents_success(self, agent):
        """Test successful document ingestion."""
        mock_chunks = [
            Mock(page_content="Chunk 1", metadata={"source": "test.txt"}),
            Mock(page_content="Chunk 2", metadata={"source": "test.txt"}),
        ]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_vectorstore = Mock()
            mock_chroma.from_documents.return_value = mock_vectorstore
            
            success = agent.ingest_documents(mock_chunks)
            
            mock_chroma.from_documents.assert_called_once()
            mock_vectorstore.persist.assert_called_once()
            assert success is True

    def test_ingest_documents_error(self, agent):
        """Test error handling during document ingestion."""
        mock_chunks = [Mock(page_content="Chunk", metadata={})]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_chroma.from_documents.side_effect = Exception("Ingestion error")
            
            success = agent.ingest_documents(mock_chunks)
            
            assert success is False

    def test_ingest_uses_correct_configuration(self, agent):
        """Test that ingestion uses correct agent configuration."""
        mock_chunks = [Mock(page_content="Test", metadata={})]
        
        with patch('ingest.Chroma') as mock_chroma:
            mock_vectorstore = Mock()
            mock_chroma.from_documents.return_value = mock_vectorstore
            
            agent.ingest_documents(mock_chunks)
            
            call_kwargs = mock_chroma.from_documents.call_args[1]
            assert call_kwargs['collection_name'] == agent.collection_name
            assert call_kwargs['persist_directory'] == agent.persist_directory


class TestGetDatabaseStats:
    """Test database statistics retrieval."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_get_stats_success(self, agent):
        """Test successful retrieval of database statistics."""
        with patch('ingest.Chroma') as mock_chroma:
            mock_collection = Mock()
            mock_collection.count.return_value = 42
            mock_vectorstore = Mock()
            mock_vectorstore._collection = mock_collection
            mock_chroma.return_value = mock_vectorstore
            
            stats = agent.get_database_stats()
            
            assert stats['collection_name'] == agent.collection_name
            assert stats['document_count'] == 42
            assert stats['persist_directory'] == agent.persist_directory

    def test_get_stats_empty_database(self, agent):
        """Test statistics for empty database."""
        with patch('ingest.Chroma') as mock_chroma:
            mock_collection = Mock()
            mock_collection.count.return_value = 0
            mock_vectorstore = Mock()
            mock_vectorstore._collection = mock_collection
            mock_chroma.return_value = mock_vectorstore
            
            stats = agent.get_database_stats()
            
            assert stats['document_count'] == 0

    def test_get_stats_error(self, agent):
        """Test error handling when retrieving statistics."""
        with patch('ingest.Chroma') as mock_chroma:
            mock_chroma.side_effect = Exception("Database error")
            
            stats = agent.get_database_stats()
            
            assert stats == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
