#!/usr/bin/env python3
"""
Test API key whitespace handling.

This test ensures that API keys with leading/trailing whitespace
are properly stripped before being used for authentication.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys


class TestAPIKeyWhitespaceHandling:
    """Test that API keys with whitespace are handled correctly."""
    
    def test_gemini_key_with_whitespace_llm_config(self):
        """Test that llm_config strips whitespace from Gemini API keys."""
        # Clear environment
        env_backup = {}
        for key in ['LLM_PROVIDER', 'GEMINI_API_KEY', 'GEMINI_KEY', 'GOOGLE_API_KEY', 'OPENAI_API_KEY']:
            env_backup[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]
        
        # Set API key with whitespace
        os.environ['GEMINI_API_KEY'] = '  test-key-with-spaces\n'
        
        try:
            # Mock the langchain module
            mock_langchain = MagicMock()
            sys.modules['langchain_google_genai'] = mock_langchain
            
            # Import after mocking
            import llm_config
            from importlib import reload
            reload(llm_config)
            
            from llm_config import get_llm
            
            get_llm()
            
            # Verify the API key was stripped
            call_kwargs = mock_langchain.ChatGoogleGenerativeAI.call_args[1]
            assert call_kwargs['google_api_key'] == 'test-key-with-spaces'
            assert call_kwargs['google_api_key'] == call_kwargs['google_api_key'].strip()
        finally:
            # Restore environment
            for key, value in env_backup.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]
            # Clean up module mock
            if 'langchain_google_genai' in sys.modules:
                del sys.modules['langchain_google_genai']
    
    def test_openai_key_with_whitespace_llm_config(self):
        """Test that llm_config strips whitespace from OpenAI API keys."""
        # Clear environment
        env_backup = {}
        for key in ['LLM_PROVIDER', 'GEMINI_API_KEY', 'GEMINI_KEY', 'GOOGLE_API_KEY', 'OPENAI_API_KEY']:
            env_backup[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]
        
        # Set OpenAI provider with API key with whitespace
        os.environ['LLM_PROVIDER'] = 'openai'
        os.environ['OPENAI_API_KEY'] = '\ttest-openai-key  \n'
        
        try:
            # Mock the langchain module
            mock_langchain = MagicMock()
            sys.modules['langchain_openai'] = mock_langchain
            
            # Import after mocking
            import llm_config
            from importlib import reload
            reload(llm_config)
            
            from llm_config import get_llm
            
            get_llm()
            
            # Verify the API key was stripped
            call_kwargs = mock_langchain.ChatOpenAI.call_args[1]
            assert call_kwargs['api_key'] == 'test-openai-key'
            assert call_kwargs['api_key'] == call_kwargs['api_key'].strip()
        finally:
            # Restore environment
            for key, value in env_backup.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]
            # Clean up module mock
            if 'langchain_openai' in sys.modules:
                del sys.modules['langchain_openai']
    
    def test_config_manager_strips_whitespace_on_save(self):
        """Test that config_manager strips whitespace when saving API keys."""
        import tempfile
        import shutil
        from pathlib import Path
        
        # Create a temporary config directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Patch the config directory
            with patch('config_manager._get_config_dir') as mock_get_dir:
                mock_get_dir.return_value = Path(temp_dir)
                
                import config_manager
                
                # Save an API key with whitespace
                config_manager.set_api_key("gemini", "  test-key-whitespace  \n")
                
                # Retrieve it
                retrieved_key = config_manager.get_api_key("gemini")
                
                # Verify it was stripped
                assert retrieved_key == "test-key-whitespace"
                assert retrieved_key == retrieved_key.strip()
        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_config_manager_strips_whitespace_on_retrieve(self):
        """Test that config_manager strips whitespace when retrieving API keys."""
        import tempfile
        import shutil
        from pathlib import Path
        
        # Create a temporary config directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Patch the config directory
            with patch('config_manager._get_config_dir') as mock_get_dir:
                mock_get_dir.return_value = Path(temp_dir)
                
                import config_manager
                
                # Save an API key
                config_manager.set_api_key("openai", "test-openai-key")
                
                # Retrieve it
                retrieved_key = config_manager.get_api_key("openai")
                
                # Verify there's no whitespace
                assert retrieved_key == "test-openai-key"
                assert retrieved_key == retrieved_key.strip()
        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_legacy_gemini_key_variable_with_whitespace(self):
        """Test that legacy GEMINI_KEY variable with whitespace is handled."""
        # Clear environment
        env_backup = {}
        for key in ['LLM_PROVIDER', 'GEMINI_API_KEY', 'GEMINI_KEY', 'GOOGLE_API_KEY', 'OPENAI_API_KEY']:
            env_backup[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]
        
        # Set legacy GEMINI_KEY with whitespace
        os.environ['GEMINI_KEY'] = '  legacy-key  '
        
        try:
            # Mock the langchain module
            mock_langchain = MagicMock()
            sys.modules['langchain_google_genai'] = mock_langchain
            
            # Import after mocking
            import llm_config
            from importlib import reload
            reload(llm_config)
            
            from llm_config import get_llm
            
            get_llm()
            
            # Verify the API key was stripped
            call_kwargs = mock_langchain.ChatGoogleGenerativeAI.call_args[1]
            assert call_kwargs['google_api_key'] == 'legacy-key'
        finally:
            # Restore environment
            for key, value in env_backup.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]
            # Clean up module mock
            if 'langchain_google_genai' in sys.modules:
                del sys.modules['langchain_google_genai']
    
    def test_google_api_key_fallback_with_whitespace(self):
        """Test that GOOGLE_API_KEY fallback with whitespace is handled."""
        # Clear environment
        env_backup = {}
        for key in ['LLM_PROVIDER', 'GEMINI_API_KEY', 'GEMINI_KEY', 'GOOGLE_API_KEY', 'OPENAI_API_KEY']:
            env_backup[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]
        
        # Set GOOGLE_API_KEY (fallback) with whitespace
        os.environ['GOOGLE_API_KEY'] = '\n  google-key\t\n'
        
        try:
            # Mock the langchain module
            mock_langchain = MagicMock()
            sys.modules['langchain_google_genai'] = mock_langchain
            
            # Import after mocking
            import llm_config
            from importlib import reload
            reload(llm_config)
            
            from llm_config import get_llm
            
            get_llm()
            
            # Verify the API key was stripped
            call_kwargs = mock_langchain.ChatGoogleGenerativeAI.call_args[1]
            assert call_kwargs['google_api_key'] == 'google-key'
        finally:
            # Restore environment
            for key, value in env_backup.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]
            # Clean up module mock
            if 'langchain_google_genai' in sys.modules:
                del sys.modules['langchain_google_genai']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
