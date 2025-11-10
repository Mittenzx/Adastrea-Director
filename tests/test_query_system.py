#!/usr/bin/env python3
"""
Unit tests for the query system in the Adastrea Director.

Tests cover:
- QueryAgent initialization
- Query processing
- Database information retrieval
- Error handling
- Memory and conversation management
"""

import os
import sys
from unittest.mock import Mock, patch
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import QueryAgent


class TestQueryAgentInitialization:
    """Test initialization of QueryAgent."""

    @patch('main.ConversationalRetrievalChain')
    @patch('main.Chroma')
    @patch('main.ChatOpenAI')
    @patch('main.OpenAIEmbeddings')
    def test_default_initialization(self, mock_embeddings, mock_llm, mock_chroma, mock_chain):
        """Test agent initializes with default parameters."""
        # Setup mocks
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
        
        assert agent.collection_name == "adastrea_docs"
        assert agent.persist_directory == "./chroma_db"
        assert agent.model_name == "gpt-3.5-turbo"
        assert agent.temperature == 0.7
        mock_embeddings.assert_called_once()

    @patch('main.ConversationalRetrievalChain')
    @patch('main.Chroma')
    @patch('main.ChatOpenAI')
    @patch('main.OpenAIEmbeddings')
    def test_custom_initialization(self, mock_embeddings, mock_llm, mock_chroma, mock_chain):
        """Test agent initializes with custom parameters."""
        # Setup mocks
        mock_embeddings.return_value = Mock()
        mock_llm.return_value = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 10
        mock_vectorstore = Mock()
        mock_vectorstore._collection = mock_collection
        mock_vectorstore.as_retriever.return_value = Mock()
        mock_chroma.return_value = mock_vectorstore
        mock_chain.from_llm.return_value = Mock()
        
        agent = QueryAgent(
            collection_name="test_collection",
            persist_directory="./test_db",
            model_name="gpt-4",
            temperature=0.5,
        )
        
        assert agent.collection_name == "test_collection"
        assert agent.persist_directory == "./test_db"
        assert agent.model_name == "gpt-4"
        assert agent.temperature == 0.5

    @patch('main.ConversationalRetrievalChain')
    @patch('main.Chroma')
    @patch('main.ChatOpenAI')
    @patch('main.OpenAIEmbeddings')
    def test_llm_configuration(self, mock_embeddings, mock_llm, mock_chroma, mock_chain):
        """Test that LLM is configured correctly."""
        # Setup mocks
        mock_embeddings.return_value = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 10
        mock_vectorstore = Mock()
        mock_vectorstore._collection = mock_collection
        mock_vectorstore.as_retriever.return_value = Mock()
        mock_chroma.return_value = mock_vectorstore
        mock_chain.from_llm.return_value = Mock()
        
        QueryAgent(model_name="gpt-4", temperature=0.3)
        
        mock_llm.assert_called_once_with(
            model_name="gpt-4",
            temperature=0.3,
        )

    @patch('main.ConversationalRetrievalChain')
    @patch('main.Chroma')
    @patch('main.ChatOpenAI')
    @patch('main.OpenAIEmbeddings')
    @patch('main.sys.exit')
    def test_empty_database_exits(self, mock_exit, mock_embeddings, mock_llm, mock_chroma, mock_chain):
        """Test that initialization exits when database is empty."""
        # Setup mocks
        mock_embeddings.return_value = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 0  # Empty database
        mock_vectorstore = Mock()
        mock_vectorstore._collection = mock_collection
        mock_chroma.return_value = mock_vectorstore
        
        QueryAgent()
        
        mock_exit.assert_called_once_with(1)

    @patch('main.ConversationalRetrievalChain')
    @patch('main.Chroma')
    @patch('main.ChatOpenAI')
    @patch('main.OpenAIEmbeddings')
    def test_retriever_configuration(self, mock_embeddings, mock_llm, mock_chroma, mock_chain):
        """Test that retriever is configured with correct search parameters."""
        # Setup mocks
        mock_embeddings.return_value = Mock()
        mock_llm.return_value = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 10
        mock_vectorstore = Mock()
        mock_vectorstore._collection = mock_collection
        mock_retriever = Mock()
        mock_vectorstore.as_retriever.return_value = mock_retriever
        mock_chroma.return_value = mock_vectorstore
        mock_chain.from_llm.return_value = Mock()
        
        QueryAgent()
        
        mock_vectorstore.as_retriever.assert_called_once_with(
            search_kwargs={"k": 5}
        )


class TestProcessQuery:
    """Test query processing functionality."""

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

    def test_process_simple_query(self, agent):
        """Test processing a simple query."""
        query = "What is the main gameplay loop?"
        expected_result = {
            "answer": "The main gameplay loop involves...",
            "source_documents": []
        }
        
        agent.qa_chain = Mock()
        agent.qa_chain.return_value = expected_result
        
        result = agent.process_query(query)
        
        agent.qa_chain.assert_called_once_with({"question": query})
        assert result["answer"] == expected_result["answer"]

    def test_process_query_with_sources(self, agent):
        """Test processing query returns source documents."""
        query = "Describe the player character"
        mock_doc = Mock()
        mock_doc.page_content = "Character description..."
        mock_doc.metadata = {"source": "design.md"}
        
        expected_result = {
            "answer": "The player character is...",
            "source_documents": [mock_doc]
        }
        
        agent.qa_chain = Mock()
        agent.qa_chain.return_value = expected_result
        
        result = agent.process_query(query)
        
        assert len(result["source_documents"]) == 1
        assert result["source_documents"][0].metadata["source"] == "design.md"

    def test_process_query_error_handling(self, agent):
        """Test error handling when query processing fails."""
        query = "Test query"
        
        agent.qa_chain = Mock()
        agent.qa_chain.side_effect = Exception("Processing error")
        
        result = agent.process_query(query)
        
        assert "error" in result["answer"].lower()
        assert result["source_documents"] == []

    def test_process_empty_query(self, agent):
        """Test processing an empty query."""
        query = ""
        
        agent.qa_chain = Mock()
        agent.qa_chain.return_value = {
            "answer": "Please provide a question.",
            "source_documents": []
        }
        
        result = agent.process_query(query)
        
        agent.qa_chain.assert_called_once_with({"question": query})
        assert result is not None

    def test_process_complex_query(self, agent):
        """Test processing a complex multi-part query."""
        query = "How should I implement the quantum phase shift mechanic and what are the performance implications?"
        
        expected_result = {
            "answer": "To implement the quantum phase shift mechanic...",
            "source_documents": [Mock(), Mock()]
        }
        
        agent.qa_chain = Mock()
        agent.qa_chain.return_value = expected_result
        
        result = agent.process_query(query)
        
        assert result["answer"] is not None
        assert len(result["source_documents"]) == 2


class TestGetDatabaseInfo:
    """Test database information retrieval."""

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

    def test_get_database_info_success(self, agent):
        """Test successful retrieval of database information."""
        agent.vectorstore._collection.count.return_value = 42
        
        info = agent.get_database_info()
        
        assert info['collection_name'] == agent.collection_name
        assert info['document_count'] == 42
        assert info['persist_directory'] == agent.persist_directory

    def test_get_database_info_empty(self, agent):
        """Test database info when database is empty."""
        agent.vectorstore._collection.count.return_value = 0
        
        info = agent.get_database_info()
        
        assert info['document_count'] == 0

    def test_get_database_info_error(self, agent):
        """Test error handling when retrieving database info."""
        agent.vectorstore._collection.count.side_effect = Exception("Database error")
        
        info = agent.get_database_info()
        
        assert info == {}


class TestMemoryManagement:
    """Test conversation memory management."""

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

    def test_memory_initialization(self, agent):
        """Test that memory is initialized correctly."""
        assert agent.memory is not None
        assert agent.memory.memory_key == "chat_history"
        assert agent.memory.return_messages is True
        assert agent.memory.output_key == "answer"

    def test_memory_clear(self, agent):
        """Test clearing conversation memory."""
        # Test that memory can be cleared
        assert hasattr(agent.memory, 'clear')
        # Call clear without asserting since it's a real object
        agent.memory.clear()
        # Memory should still exist after clear
        assert agent.memory is not None


class TestQueryOptimization:
    """Test query optimization features."""

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
            mock_retriever = Mock()
            mock_vectorstore.as_retriever.return_value = mock_retriever
            mock_chroma.return_value = mock_vectorstore
            
            mock_chain.from_llm.return_value = Mock()
            return QueryAgent()

    def test_retriever_returns_top_k_results(self, agent):
        """Test that retriever is configured to return top 5 results."""
        # The retriever should be configured with k=5
        assert agent.vectorstore.as_retriever.called
        call_kwargs = agent.vectorstore.as_retriever.call_args[1]
        assert call_kwargs['search_kwargs']['k'] == 5

    def test_custom_prompt_template_used(self, agent):
        """Test that custom prompt template is used in the chain."""
        # The QA chain should be using a custom prompt
        assert agent.qa_chain is not None
        # Prompt template should be configured in the chain


class TestErrorHandling:
    """Test comprehensive error handling."""

    def test_missing_api_key_initialization(self):
        """Test initialization fails gracefully with missing API key."""
        with patch('main.OpenAIEmbeddings') as mock_embeddings, \
             patch('main.sys.exit') as mock_exit:
            
            mock_embeddings.side_effect = Exception("OPENAI_API_KEY not found")
            
            QueryAgent()
            
            mock_exit.assert_called()

    @patch('main.ConversationalRetrievalChain')
    @patch('main.Chroma')
    @patch('main.ChatOpenAI')
    @patch('main.OpenAIEmbeddings')
    def test_invalid_model_name(self, mock_embeddings, mock_llm, mock_chroma, mock_chain):
        """Test handling of invalid model name."""
        mock_embeddings.return_value = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 10
        mock_vectorstore = Mock()
        mock_vectorstore._collection = mock_collection
        mock_vectorstore.as_retriever.return_value = Mock()
        mock_chroma.return_value = mock_vectorstore
        mock_chain.from_llm.return_value = Mock()
        
        # Should not raise exception during initialization
        agent = QueryAgent(model_name="invalid-model-999")
        assert agent.model_name == "invalid-model-999"

    @patch('main.ConversationalRetrievalChain')
    @patch('main.Chroma')
    @patch('main.ChatOpenAI')
    @patch('main.OpenAIEmbeddings')
    def test_invalid_temperature(self, mock_embeddings, mock_llm, mock_chroma, mock_chain):
        """Test handling of invalid temperature value."""
        mock_embeddings.return_value = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 10
        mock_vectorstore = Mock()
        mock_vectorstore._collection = mock_collection
        mock_vectorstore.as_retriever.return_value = Mock()
        mock_chroma.return_value = mock_vectorstore
        mock_chain.from_llm.return_value = Mock()
        
        # Should accept temperature value
        agent = QueryAgent(temperature=1.5)  # Higher than recommended
        assert agent.temperature == 1.5

    @patch('main.ConversationalRetrievalChain')
    @patch('main.Chroma')
    @patch('main.ChatOpenAI')
    @patch('main.OpenAIEmbeddings')
    def test_database_connection_error(self, mock_embeddings, mock_llm, mock_chroma, mock_chain):
        """Test handling of database connection errors."""
        mock_embeddings.return_value = Mock()
        mock_chroma.side_effect = Exception("Cannot connect to database")
        
        with patch('main.sys.exit') as mock_exit:
            QueryAgent()
            mock_exit.assert_called()


class TestConversationalRetrieval:
    """Test conversational retrieval functionality."""

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

    def test_follow_up_questions(self, agent):
        """Test that follow-up questions use conversation history."""
        # First query
        agent.qa_chain = Mock()
        agent.qa_chain.return_value = {
            "answer": "The player character has special abilities.",
            "source_documents": []
        }
        
        result1 = agent.process_query("What are the player abilities?")
        
        # Follow-up query
        agent.qa_chain.return_value = {
            "answer": "The quantum shift allows teleportation.",
            "source_documents": []
        }
        
        result2 = agent.process_query("Tell me more about quantum shift")
        
        # Both queries should be processed
        assert result1 is not None
        assert result2 is not None
        assert agent.qa_chain.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
