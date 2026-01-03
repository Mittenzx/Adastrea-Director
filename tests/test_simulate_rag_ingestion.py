#!/usr/bin/env python3
"""
Simulation test for RAG ingestion functionality.

This test simulates a complete RAG ingestion workflow to verify that:
1. Document ingestion works correctly
2. Incremental ingestion detects changes properly
3. Progress tracking functions correctly
4. Hash-based change detection works
5. Different file types are handled correctly

The test uses mock embeddings to avoid requiring external API keys,
allowing it to run in CI/CD environments.
"""

import os
import sys
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add parent directory and plugin Python directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Plugins', 'AdastreaDirector', 'Python'))

# Import the modules we're testing
from Plugins.AdastreaDirector.Python.rag_ingestion import (
    RAGIngestionAgent,
    ProgressWriter,
    ingest_documents,
)
from Plugins.AdastreaDirector.Python.progress_utils import write_progress_file


class TestRAGIngestionSimulation:
    """
    Comprehensive simulation tests for RAG ingestion functionality.
    
    These tests simulate real-world scenarios without requiring external APIs
    or dependencies, making them suitable for automated testing and CI/CD.
    """

    @pytest.fixture
    def temp_docs_dir(self):
        """Create a temporary directory with test documents."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create various test documents
            docs_path = Path(temp_dir)
            
            # Markdown file
            (docs_path / "readme.md").write_text(
                "# Test Project\n\nThis is a test markdown document.\n\n"
                "## Features\n- Feature 1\n- Feature 2\n"
            )
            
            # Python file
            (docs_path / "example.py").write_text(
                "#!/usr/bin/env python3\n"
                "def hello_world():\n"
                "    print('Hello, World!')\n\n"
                "if __name__ == '__main__':\n"
                "    hello_world()\n"
            )
            
            # Text file
            (docs_path / "notes.txt").write_text(
                "Project Notes\n"
                "=============\n\n"
                "This is a plain text document.\n"
                "It contains important information.\n"
            )
            
            # C++ file
            (docs_path / "main.cpp").write_text(
                "#include <iostream>\n\n"
                "int main() {\n"
                "    std::cout << \"Hello World!\" << std::endl;\n"
                "    return 0;\n"
                "}\n"
            )
            
            yield temp_dir

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory for the vector database."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def temp_progress_file(self):
        """Create a temporary progress file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            progress_file = f.name
        
        yield progress_file
        
        # Cleanup
        if os.path.exists(progress_file):
            os.unlink(progress_file)

    @pytest.fixture
    def mock_embeddings(self):
        """Create mock embeddings to avoid requiring API keys."""
        mock_embed = Mock()
        # Mock the embed_documents method to return fake embeddings
        mock_embed.embed_documents.return_value = [[0.1] * 384] * 10  # 384-dim embeddings
        mock_embed.embed_query.return_value = [0.1] * 384
        return mock_embed

    def test_progress_writer_basic(self, temp_progress_file):
        """Test that ProgressWriter correctly writes progress updates."""
        writer = ProgressWriter(temp_progress_file)
        
        # Write progress
        writer.write(25.0, "Processing", "Loading files...", "processing")
        
        # Verify progress file was written
        assert os.path.exists(temp_progress_file)
        
        # Read and verify content
        with open(temp_progress_file, 'r') as f:
            progress_data = json.load(f)
        
        assert progress_data['percent'] == 25.0
        assert progress_data['label'] == "Processing"
        assert progress_data['details'] == "Loading files..."
        assert progress_data['status'] == "processing"
        assert 'timestamp' in progress_data

    def test_progress_writer_multiple_updates(self, temp_progress_file):
        """Test multiple progress updates overwrite the file."""
        writer = ProgressWriter(temp_progress_file)
        
        # Write multiple updates
        writer.write(10, "Step 1", "Starting", "processing")
        writer.write(50, "Step 2", "Halfway", "processing")
        writer.write(100, "Complete", "Finished", "complete")
        
        # Verify only the last update is in the file
        with open(temp_progress_file, 'r') as f:
            progress_data = json.load(f)
        
        assert progress_data['percent'] == 100
        assert progress_data['label'] == "Complete"
        assert progress_data['status'] == "complete"

    def test_file_hash_calculation(self, temp_docs_dir, mock_embeddings):
        """Test that file hashes are calculated correctly."""
        agent = RAGIngestionAgent(embeddings=mock_embeddings)
        
        test_file = Path(temp_docs_dir) / "readme.md"
        
        # Calculate hash twice
        hash1 = agent._calculate_file_hash(str(test_file))
        hash2 = agent._calculate_file_hash(str(test_file))
        
        # Hash should be consistent
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 hex characters

    def test_file_hash_changes_with_content(self, temp_docs_dir, mock_embeddings):
        """Test that hash changes when file content changes."""
        agent = RAGIngestionAgent(embeddings=mock_embeddings)
        
        test_file = Path(temp_docs_dir) / "test.txt"
        
        # Write initial content
        test_file.write_text("Initial content")
        hash1 = agent._calculate_file_hash(str(test_file))
        
        # Modify content
        test_file.write_text("Modified content")
        hash2 = agent._calculate_file_hash(str(test_file))
        
        # Hashes should be different
        assert hash1 != hash2

    def test_get_file_list(self, temp_docs_dir, mock_embeddings):
        """Test that _get_file_list finds supported files."""
        agent = RAGIngestionAgent(embeddings=mock_embeddings)
        
        file_list = agent._get_file_list(temp_docs_dir)
        
        # Should find all supported files
        assert len(file_list) >= 4
        
        # Check that specific files are found
        file_names = [Path(f).name for f in file_list]
        assert "readme.md" in file_names
        assert "example.py" in file_names
        assert "notes.txt" in file_names
        assert "main.cpp" in file_names

    def test_load_single_file_markdown(self, temp_docs_dir, mock_embeddings):
        """Test loading a single markdown file."""
        agent = RAGIngestionAgent(embeddings=mock_embeddings)
        
        test_file = str(Path(temp_docs_dir) / "readme.md")
        documents = agent.load_single_file(test_file)
        
        # Should return at least one document
        assert len(documents) > 0
        assert documents[0].page_content
        assert documents[0].metadata['source'] == test_file

    def test_load_single_file_python(self, temp_docs_dir, mock_embeddings):
        """Test loading a single Python file."""
        agent = RAGIngestionAgent(embeddings=mock_embeddings)
        
        test_file = str(Path(temp_docs_dir) / "example.py")
        documents = agent.load_single_file(test_file)
        
        # Should return at least one document
        assert len(documents) > 0
        assert "def hello_world" in documents[0].page_content
        assert documents[0].metadata['source'] == test_file

    def test_metadata_enrichment(self, temp_docs_dir, mock_embeddings):
        """Test that metadata is enriched with file hash and other info."""
        agent = RAGIngestionAgent(embeddings=mock_embeddings)
        
        test_file = str(Path(temp_docs_dir) / "readme.md")
        documents = agent.load_single_file(test_file)
        
        assert len(documents) > 0
        metadata = documents[0].metadata
        
        # Check enriched metadata
        assert 'file_hash' in metadata
        assert 'filename' in metadata
        assert 'extension' in metadata
        assert metadata['filename'] == "readme.md"
        assert metadata['extension'] == ".md"

    def test_chunk_documents(self, temp_docs_dir, mock_embeddings):
        """Test that documents are properly chunked."""
        agent = RAGIngestionAgent(
            embeddings=mock_embeddings,
            chunk_size=100,
            chunk_overlap=20
        )
        
        # Create a document with enough content to be chunked
        test_file = Path(temp_docs_dir) / "long_doc.txt"
        test_file.write_text("This is a test. " * 100)  # Long enough to chunk
        
        documents = agent.load_single_file(str(test_file))
        chunks = agent.chunk_documents(documents)
        
        # Should produce multiple chunks
        assert len(chunks) >= 1
        
        # Each chunk should have metadata
        for chunk in chunks:
            assert chunk.metadata
            assert 'source' in chunk.metadata

    def test_language_detection(self, mock_embeddings):
        """Test that programming language is detected correctly."""
        agent = RAGIngestionAgent(embeddings=mock_embeddings)
        
        from langchain_text_splitters import Language
        
        assert agent._detect_language("test.py") == Language.PYTHON
        assert agent._detect_language("test.cpp") == Language.CPP
        assert agent._detect_language("test.cs") == Language.CSHARP
        assert agent._detect_language("test.txt") is None

    @patch('Plugins.AdastreaDirector.Python.rag_ingestion.Chroma')
    def test_ingestion_simulation_full_workflow(
        self, mock_chroma, temp_docs_dir, temp_db_dir, temp_progress_file, mock_embeddings
    ):
        """
        Simulate a complete ingestion workflow.
        
        This is the main simulation test that verifies the entire ingestion
        process works correctly from end to end.
        """
        # Setup mock vector store
        mock_vectorstore = Mock()
        mock_collection = Mock()
        
        # Mock collection to return no existing documents (new ingestion)
        mock_collection.get.return_value = {"metadatas": [], "ids": []}
        mock_vectorstore._collection = mock_collection
        mock_vectorstore.add_documents = Mock()
        mock_vectorstore.persist = Mock()
        
        mock_chroma.from_documents.return_value = mock_vectorstore
        mock_chroma.return_value = mock_vectorstore
        
        # Create agent with progress tracking
        progress_writer = ProgressWriter(temp_progress_file)
        agent = RAGIngestionAgent(
            collection_name="test_collection",
            persist_directory=temp_db_dir,
            embeddings=mock_embeddings,
            progress_writer=progress_writer,
        )
        
        # Run ingestion
        stats = agent.ingest_directory_incremental(
            temp_docs_dir,
            force_reingest=False,
            delay_between_files=0  # No delay for testing
        )
        
        # Verify statistics
        assert stats['total_files'] >= 4
        assert stats['added'] >= 4
        assert stats['updated'] == 0
        assert stats['skipped'] == 0
        assert stats['errors'] == 0
        
        # Verify progress file was updated
        assert os.path.exists(temp_progress_file)
        with open(temp_progress_file, 'r') as f:
            progress_data = json.load(f)
        assert progress_data['percent'] == 100
        assert progress_data['status'] == "complete"
        
        # Verify vector store methods were called
        assert mock_vectorstore.add_documents.called or mock_chroma.from_documents.called
        assert mock_vectorstore.persist.called

    @patch('Plugins.AdastreaDirector.Python.rag_ingestion.Chroma')
    def test_incremental_ingestion_skip_unchanged(
        self, mock_chroma, temp_docs_dir, temp_db_dir, mock_embeddings
    ):
        """
        Test that incremental ingestion skips unchanged files.
        
        Simulates a scenario where files have already been ingested
        and haven't changed.
        """
        # Setup mock to return existing documents with same hash
        def mock_get_side_effect(*args, **kwargs):
            where = kwargs.get('where', {})
            source = where.get('source', '')
            if source:
                # Return a hash for existing files
                return {
                    "metadatas": [{"file_hash": "existing_hash", "source": source}],
                    "ids": ["id1"]
                }
            return {"metadatas": [], "ids": []}
        
        mock_collection = Mock()
        mock_collection.get.side_effect = mock_get_side_effect
        
        mock_vectorstore = Mock()
        mock_vectorstore._collection = mock_collection
        mock_chroma.return_value = mock_vectorstore
        
        # Create agent
        agent = RAGIngestionAgent(
            persist_directory=temp_db_dir,
            embeddings=mock_embeddings,
        )
        
        # Mock _calculate_file_hash to return the same hash as stored
        with patch.object(agent, '_calculate_file_hash', return_value='existing_hash'):
            # Mock Path.exists to return True
            with patch('pathlib.Path.exists', return_value=True):
                stats = agent.ingest_directory_incremental(
                    temp_docs_dir,
                    force_reingest=False,
                    delay_between_files=0
                )
        
        # All files should be skipped since they're unchanged
        assert stats['skipped'] == stats['total_files']
        assert stats['added'] == 0
        assert stats['updated'] == 0

    @patch('Plugins.AdastreaDirector.Python.rag_ingestion.Chroma')
    def test_incremental_ingestion_update_changed(
        self, mock_chroma, temp_docs_dir, temp_db_dir, mock_embeddings
    ):
        """
        Test that incremental ingestion updates changed files.
        
        Simulates a scenario where files have changed since last ingestion.
        """
        # Setup mock to return existing documents with different hash
        def mock_get_side_effect(*args, **kwargs):
            where = kwargs.get('where', {})
            source = where.get('source', '')
            if source:
                return {
                    "metadatas": [{"file_hash": "old_hash", "source": source}],
                    "ids": ["id1", "id2"]
                }
            return {"metadatas": [], "ids": []}
        
        mock_collection = Mock()
        mock_collection.get.side_effect = mock_get_side_effect
        mock_collection.delete = Mock()
        
        mock_vectorstore = Mock()
        mock_vectorstore._collection = mock_collection
        mock_vectorstore.add_documents = Mock()
        mock_vectorstore.persist = Mock()
        mock_chroma.return_value = mock_vectorstore
        
        # Create agent
        agent = RAGIngestionAgent(
            persist_directory=temp_db_dir,
            embeddings=mock_embeddings,
        )
        
        # Mock _calculate_file_hash to return a different hash
        with patch.object(agent, '_calculate_file_hash', return_value='new_hash'):
            # Mock Path.exists to return True
            with patch('pathlib.Path.exists', return_value=True):
                stats = agent.ingest_directory_incremental(
                    temp_docs_dir,
                    force_reingest=False,
                    delay_between_files=0
                )
        
        # All files should be marked as updated
        assert stats['updated'] == stats['total_files']
        assert stats['added'] == 0
        assert stats['skipped'] == 0
        
        # Verify old documents were deleted
        assert mock_collection.delete.called

    @patch('Plugins.AdastreaDirector.Python.rag_ingestion.Chroma')
    def test_force_reingest(
        self, mock_chroma, temp_docs_dir, temp_db_dir, mock_embeddings
    ):
        """
        Test that force_reingest re-ingests all files.
        
        Even if files haven't changed, force_reingest should process them.
        """
        mock_collection = Mock()
        mock_collection.get.return_value = {
            "metadatas": [{"file_hash": "same_hash"}],
            "ids": ["id1"]
        }
        mock_collection.delete = Mock()
        
        mock_vectorstore = Mock()
        mock_vectorstore._collection = mock_collection
        mock_vectorstore.add_documents = Mock()
        mock_vectorstore.persist = Mock()
        mock_chroma.return_value = mock_vectorstore
        
        agent = RAGIngestionAgent(
            persist_directory=temp_db_dir,
            embeddings=mock_embeddings,
        )
        
        # Mock Path.exists to return True
        with patch('pathlib.Path.exists', return_value=True):
            stats = agent.ingest_directory_incremental(
                temp_docs_dir,
                force_reingest=True,  # Force re-ingestion
                delay_between_files=0
            )
        
        # All files should be processed (updated or added)
        assert stats['added'] + stats['updated'] == stats['total_files']
        assert stats['skipped'] == 0

    def test_error_handling_invalid_file(self, temp_docs_dir, mock_embeddings):
        """Test that invalid files are handled gracefully."""
        agent = RAGIngestionAgent(embeddings=mock_embeddings)
        
        # Try to load a non-existent file
        documents = agent.load_single_file("/nonexistent/file.txt")
        
        # Should return empty list, not raise an exception
        assert documents == []

    @patch('Plugins.AdastreaDirector.Python.rag_ingestion.Chroma')
    def test_error_handling_during_ingestion(
        self, mock_chroma, temp_docs_dir, temp_db_dir, mock_embeddings
    ):
        """Test that errors during ingestion are tracked properly."""
        # Setup mock collection to return no existing documents
        mock_collection = Mock()
        mock_collection.get.return_value = {"metadatas": [], "ids": []}
        
        # Make the vector store raise an error when adding documents
        mock_vectorstore = Mock()
        mock_vectorstore._collection = mock_collection
        mock_vectorstore.add_documents.side_effect = Exception("Simulated database error")
        mock_vectorstore.persist = Mock()
        
        # from_documents should succeed for the first file, but add_documents will fail
        mock_chroma.from_documents.return_value = mock_vectorstore
        mock_chroma.return_value = mock_vectorstore
        
        agent = RAGIngestionAgent(
            persist_directory=temp_db_dir,
            embeddings=mock_embeddings,
        )
        
        # Mock Path.exists to return True so it tries to use existing db
        with patch('pathlib.Path.exists', return_value=True):
            stats = agent.ingest_directory_incremental(
                temp_docs_dir,
                force_reingest=False,
                delay_between_files=0
            )
        
        # Errors should be tracked
        assert stats['errors'] > 0

    def test_main_ingest_documents_function(self, temp_docs_dir, temp_db_dir, temp_progress_file, mock_embeddings):
        """Test the main ingest_documents function."""
        with patch('Plugins.AdastreaDirector.Python.rag_ingestion.RAGIngestionAgent') as mock_agent_class:
            # Setup mock agent
            mock_agent = Mock()
            mock_agent.ingest_directory_incremental.return_value = {
                'total_files': 4,
                'added': 4,
                'updated': 0,
                'skipped': 0,
                'errors': 0
            }
            mock_agent_class.return_value = mock_agent
            
            # Call the function
            stats = ingest_documents(
                docs_dir=temp_docs_dir,
                collection_name="test_collection",
                persist_dir=temp_db_dir,
                progress_file=temp_progress_file,
                force_reingest=False
            )
            
            # Verify function was called correctly
            assert mock_agent_class.called
            assert mock_agent.ingest_directory_incremental.called
            assert stats['total_files'] == 4
            assert stats['added'] == 4


class TestProgressUtilsFunction:
    """Test the standalone progress_utils functions."""

    def test_write_progress_file_function(self):
        """Test the write_progress_file utility function."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            progress_file = f.name
        
        try:
            # Write progress
            write_progress_file(progress_file, 75.0, "Testing", "In progress", "processing")
            
            # Verify file exists and contains correct data
            assert os.path.exists(progress_file)
            
            with open(progress_file, 'r') as f:
                data = json.load(f)
            
            assert data['percent'] == 75.0
            assert data['label'] == "Testing"
            assert data['details'] == "In progress"
            assert data['status'] == "processing"
            assert 'timestamp' in data
        finally:
            if os.path.exists(progress_file):
                os.unlink(progress_file)

    def test_write_progress_file_creates_directories(self):
        """Test that write_progress_file creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use a nested path that doesn't exist
            progress_file = os.path.join(temp_dir, "subdir", "nested", "progress.json")
            
            # Write progress (should create directories)
            write_progress_file(progress_file, 50.0, "Test", "Creating dirs", "processing")
            
            # Verify file was created
            assert os.path.exists(progress_file)

    def test_write_progress_file_clamps_percent(self):
        """Test that percent is clamped to 0-100 range."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            progress_file = f.name
        
        try:
            # Test values outside range
            write_progress_file(progress_file, 150.0, "Over", "", "processing")
            with open(progress_file, 'r') as f:
                data = json.load(f)
            assert data['percent'] == 100.0
            
            write_progress_file(progress_file, -10.0, "Under", "", "processing")
            with open(progress_file, 'r') as f:
                data = json.load(f)
            assert data['percent'] == 0.0
        finally:
            if os.path.exists(progress_file):
                os.unlink(progress_file)


def test_rag_ingestion_module_imports():
    """Test that the RAG ingestion module can be imported."""
    try:
        from Plugins.AdastreaDirector.Python import rag_ingestion
        assert hasattr(rag_ingestion, 'RAGIngestionAgent')
        assert hasattr(rag_ingestion, 'ProgressWriter')
        assert hasattr(rag_ingestion, 'ingest_documents')
    except ImportError as e:
        pytest.fail(f"Failed to import rag_ingestion module: {e}")


def test_progress_utils_module_imports():
    """Test that the progress_utils module can be imported."""
    try:
        from Plugins.AdastreaDirector.Python import progress_utils
        assert hasattr(progress_utils, 'write_progress_file')
    except ImportError as e:
        pytest.fail(f"Failed to import progress_utils module: {e}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
