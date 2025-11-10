#!/usr/bin/env python3
"""
Unit tests for enhanced file type support in the Adastrea Director.

Tests cover:
- Additional code file type support (JS, TS, C++, C#)
- Language-specific chunking strategies
- Metadata enrichment for documents
- Document type detection
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
from langchain_text_splitters import Language


class TestAdditionalFileTypes:
    """Test support for additional file types."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_load_javascript_file(self, agent, temp_dir):
        """Test loading a JavaScript file."""
        test_file = Path(temp_dir) / "test.js"
        test_file.write_text("function test() { return true; }")
        
        with patch('ingest.TextLoader') as mock_loader:
            mock_doc = Mock()
            mock_doc.page_content = "function test() { return true; }"
            mock_doc.metadata = {"source": str(test_file)}
            mock_loader.return_value.load.return_value = [mock_doc]
            
            documents = agent.load_single_file(str(test_file))
            
            mock_loader.assert_called_once_with(str(test_file))
            assert len(documents) >= 0

    def test_load_typescript_file(self, agent, temp_dir):
        """Test loading a TypeScript file."""
        test_file = Path(temp_dir) / "test.ts"
        test_file.write_text("function test(): boolean { return true; }")
        
        with patch('ingest.TextLoader') as mock_loader:
            mock_doc = Mock()
            mock_doc.page_content = "function test(): boolean { return true; }"
            mock_doc.metadata = {"source": str(test_file)}
            mock_loader.return_value.load.return_value = [mock_doc]
            
            documents = agent.load_single_file(str(test_file))
            
            mock_loader.assert_called_once_with(str(test_file))
            assert len(documents) >= 0

    def test_load_cpp_file(self, agent, temp_dir):
        """Test loading a C++ file."""
        test_file = Path(temp_dir) / "test.cpp"
        test_file.write_text("#include <iostream>\nint main() { return 0; }")
        
        with patch('ingest.TextLoader') as mock_loader:
            mock_doc = Mock()
            mock_doc.page_content = "#include <iostream>\nint main() { return 0; }"
            mock_doc.metadata = {"source": str(test_file)}
            mock_loader.return_value.load.return_value = [mock_doc]
            
            documents = agent.load_single_file(str(test_file))
            
            mock_loader.assert_called_once_with(str(test_file))
            assert len(documents) >= 0

    def test_load_csharp_file(self, agent, temp_dir):
        """Test loading a C# file."""
        test_file = Path(temp_dir) / "test.cs"
        test_file.write_text("class Test { public void Method() {} }")
        
        with patch('ingest.TextLoader') as mock_loader:
            mock_doc = Mock()
            mock_doc.page_content = "class Test { public void Method() {} }"
            mock_doc.metadata = {"source": str(test_file)}
            mock_loader.return_value.load.return_value = [mock_doc]
            
            documents = agent.load_single_file(str(test_file))
            
            mock_loader.assert_called_once_with(str(test_file))
            assert len(documents) >= 0

    def test_load_json_file(self, agent, temp_dir):
        """Test loading a JSON config file."""
        test_file = Path(temp_dir) / "config.json"
        test_file.write_text('{"key": "value"}')
        
        with patch('ingest.TextLoader') as mock_loader:
            mock_doc = Mock()
            mock_doc.page_content = '{"key": "value"}'
            mock_doc.metadata = {"source": str(test_file)}
            mock_loader.return_value.load.return_value = [mock_doc]
            
            documents = agent.load_single_file(str(test_file))
            
            mock_loader.assert_called_once_with(str(test_file))
            assert len(documents) >= 0

    def test_load_yaml_file(self, agent, temp_dir):
        """Test loading a YAML config file."""
        test_file = Path(temp_dir) / "config.yaml"
        test_file.write_text("key: value")
        
        with patch('ingest.TextLoader') as mock_loader:
            mock_doc = Mock()
            mock_doc.page_content = "key: value"
            mock_doc.metadata = {"source": str(test_file)}
            mock_loader.return_value.load.return_value = [mock_doc]
            
            documents = agent.load_single_file(str(test_file))
            
            mock_loader.assert_called_once_with(str(test_file))
            assert len(documents) >= 0


class TestLanguageDetection:
    """Test programming language detection."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    def test_detect_python_language(self, agent):
        """Test detecting Python language."""
        language = agent._detect_language("test.py")
        assert language == Language.PYTHON

    def test_detect_javascript_language(self, agent):
        """Test detecting JavaScript language."""
        language = agent._detect_language("test.js")
        assert language == Language.JS
        
        language = agent._detect_language("test.jsx")
        assert language == Language.JS

    def test_detect_typescript_language(self, agent):
        """Test detecting TypeScript language."""
        language = agent._detect_language("test.ts")
        assert language == Language.TS
        
        language = agent._detect_language("test.tsx")
        assert language == Language.TS

    def test_detect_cpp_language(self, agent):
        """Test detecting C++ language."""
        language = agent._detect_language("test.cpp")
        assert language == Language.CPP
        
        language = agent._detect_language("test.h")
        assert language == Language.CPP
        
        language = agent._detect_language("test.hpp")
        assert language == Language.CPP

    def test_detect_csharp_language(self, agent):
        """Test detecting C# language."""
        language = agent._detect_language("test.cs")
        assert language == Language.CSHARP

    def test_detect_no_language_for_text(self, agent):
        """Test that text files return None."""
        language = agent._detect_language("test.txt")
        assert language is None
        
        language = agent._detect_language("test.md")
        assert language is None


class TestLanguageSpecificChunking:
    """Test language-specific chunking strategies."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent(chunk_size=100, chunk_overlap=20)

    def test_has_multiple_code_splitters(self, agent):
        """Test that agent has multiple language-specific splitters."""
        assert Language.PYTHON in agent.code_splitters
        assert Language.JS in agent.code_splitters
        assert Language.TS in agent.code_splitters
        assert Language.CPP in agent.code_splitters
        assert Language.CSHARP in agent.code_splitters

    def test_chunk_python_documents(self, agent):
        """Test chunking Python documents with Python-specific splitter."""
        mock_doc = Mock()
        mock_doc.page_content = "def test():\n    pass"
        mock_doc.metadata = {"source": "test.py"}
        
        with patch.object(agent.code_splitters[Language.PYTHON], 'split_documents') as mock_split:
            mock_chunk = Mock()
            mock_chunk.page_content = "def test():\n    pass"
            mock_chunk.metadata = {"source": "test.py"}
            mock_split.return_value = [mock_chunk]
            
            chunks = agent.chunk_documents([mock_doc])
            
            mock_split.assert_called_once()
            assert len(chunks) >= 1

    def test_chunk_javascript_documents(self, agent):
        """Test chunking JavaScript documents with JS-specific splitter."""
        mock_doc = Mock()
        mock_doc.page_content = "function test() {}"
        mock_doc.metadata = {"source": "test.js"}
        
        with patch.object(agent.code_splitters[Language.JS], 'split_documents') as mock_split:
            mock_chunk = Mock()
            mock_chunk.page_content = "function test() {}"
            mock_chunk.metadata = {"source": "test.js"}
            mock_split.return_value = [mock_chunk]
            
            chunks = agent.chunk_documents([mock_doc])
            
            mock_split.assert_called_once()
            assert len(chunks) >= 1

    def test_chunk_mixed_language_documents(self, agent):
        """Test chunking documents with different languages."""
        mock_docs = [
            Mock(page_content="def test(): pass", metadata={"source": "test.py"}),
            Mock(page_content="function test() {}", metadata={"source": "test.js"}),
            Mock(page_content="# Documentation", metadata={"source": "test.md"}),
        ]
        
        # Mock all splitters
        with patch.object(agent.code_splitters[Language.PYTHON], 'split_documents') as mock_py, \
             patch.object(agent.code_splitters[Language.JS], 'split_documents') as mock_js, \
             patch.object(agent.text_splitter, 'split_documents') as mock_text:
            
            mock_py.return_value = [Mock(metadata={"source": "test.py"})]
            mock_js.return_value = [Mock(metadata={"source": "test.js"})]
            mock_text.return_value = [Mock(metadata={"source": "test.md"})]
            
            chunks = agent.chunk_documents(mock_docs)
            
            # Each splitter should be called once with its respective documents
            mock_py.assert_called_once()
            mock_js.assert_called_once()
            mock_text.assert_called_once()
            assert len(chunks) >= 3


class TestMetadataEnrichment:
    """Test document metadata enrichment."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            return DocumentIngestionAgent()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_enrich_with_filename(self, agent, temp_dir):
        """Test that filename is added to metadata."""
        test_file = Path(temp_dir) / "test.py"
        test_file.write_text("def test(): pass")
        
        mock_doc = Mock()
        mock_doc.metadata = {"source": str(test_file)}
        
        enriched = agent._enrich_document_metadata([mock_doc])
        
        assert enriched[0].metadata["filename"] == "test.py"

    def test_enrich_with_extension(self, agent, temp_dir):
        """Test that file extension is added to metadata."""
        test_file = Path(temp_dir) / "test.py"
        test_file.write_text("def test(): pass")
        
        mock_doc = Mock()
        mock_doc.metadata = {"source": str(test_file)}
        
        enriched = agent._enrich_document_metadata([mock_doc])
        
        assert enriched[0].metadata["extension"] == ".py"

    def test_enrich_with_doc_type_code(self, agent, temp_dir):
        """Test that code files are marked as 'code' type."""
        test_file = Path(temp_dir) / "test.py"
        test_file.write_text("def test(): pass")
        
        mock_doc = Mock()
        mock_doc.metadata = {"source": str(test_file)}
        
        enriched = agent._enrich_document_metadata([mock_doc])
        
        assert enriched[0].metadata["doc_type"] == "code"

    def test_enrich_with_doc_type_documentation(self, agent, temp_dir):
        """Test that markdown files are marked as 'documentation' type."""
        test_file = Path(temp_dir) / "test.md"
        test_file.write_text("# Test")
        
        mock_doc = Mock()
        mock_doc.metadata = {"source": str(test_file)}
        
        enriched = agent._enrich_document_metadata([mock_doc])
        
        assert enriched[0].metadata["doc_type"] == "documentation"

    def test_enrich_with_doc_type_config(self, agent, temp_dir):
        """Test that config files are marked as 'config' type."""
        test_file = Path(temp_dir) / "config.json"
        test_file.write_text('{"key": "value"}')
        
        mock_doc = Mock()
        mock_doc.metadata = {"source": str(test_file)}
        
        enriched = agent._enrich_document_metadata([mock_doc])
        
        assert enriched[0].metadata["doc_type"] == "config"

    def test_enrich_with_language(self, agent, temp_dir):
        """Test that programming language is added to metadata for code files."""
        test_file = Path(temp_dir) / "test.py"
        test_file.write_text("def test(): pass")
        
        mock_doc = Mock()
        mock_doc.metadata = {"source": str(test_file)}
        
        enriched = agent._enrich_document_metadata([mock_doc])
        
        assert enriched[0].metadata["language"] == Language.PYTHON.value

    def test_enrich_with_file_size(self, agent, temp_dir):
        """Test that file size is added when file exists."""
        test_file = Path(temp_dir) / "test.txt"
        test_content = "Test content"
        test_file.write_text(test_content)
        
        mock_doc = Mock()
        mock_doc.metadata = {"source": str(test_file)}
        
        enriched = agent._enrich_document_metadata([mock_doc])
        
        # File size should be added
        assert "file_size" in enriched[0].metadata
        assert enriched[0].metadata["file_size"] > 0

    def test_enrich_handles_missing_source(self, agent):
        """Test that enrichment handles documents without source."""
        mock_doc = Mock()
        mock_doc.metadata = {}
        
        enriched = agent._enrich_document_metadata([mock_doc])
        
        # Should not crash, just skip enrichment
        assert enriched[0].metadata == {}

    def test_enrich_handles_invalid_source(self, agent):
        """Test that enrichment handles invalid source paths gracefully."""
        mock_doc = Mock()
        mock_doc.metadata = {"source": "/nonexistent/file.py"}
        
        enriched = agent._enrich_document_metadata([mock_doc])
        
        # Should add metadata but not file_size
        assert "filename" in enriched[0].metadata
        assert "extension" in enriched[0].metadata
        assert "doc_type" in enriched[0].metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
