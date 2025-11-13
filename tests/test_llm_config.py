#!/usr/bin/env python3
"""
Unit tests for LLM provider configuration in the Adastrea Director.

Tests cover:
- Default Gemini LLM provider
- OpenAI LLM provider via environment variable
- Provider name and API key environment variable retrieval
- Model name defaults for each provider
"""

import os
import sys
from unittest.mock import Mock, patch
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLLMConfiguration:
    """Test LLM provider configuration logic."""

    def test_default_uses_gemini(self):
        """Test that Gemini is used by default."""
        # Clear any existing environment variables
        env_backup = {}
        for key in ['LLM_PROVIDER', 'GEMINI_KEY', 'GOOGLE_API_KEY', 'OPENAI_API_KEY']:
            env_backup[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]
        
        # Set a dummy API key
        os.environ['GEMINI_KEY'] = 'test-key'
        
        try:
            with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock_gemini:
                mock_gemini.return_value = Mock()
                from llm_config import get_llm, get_provider_name, get_api_key_env_var
                
                llm = get_llm()
                
                # Verify ChatGoogleGenerativeAI was called with default model
                mock_gemini.assert_called_once()
                call_kwargs = mock_gemini.call_args[1]
                assert call_kwargs['model'] == 'gemini-1.5-flash'
                assert call_kwargs['temperature'] == 0.7
                assert call_kwargs['google_api_key'] == 'test-key'
                
                # Verify provider name
                assert get_provider_name() == "Gemini"
                assert get_api_key_env_var() == "GEMINI_KEY"
        finally:
            # Restore environment
            for key, value in env_backup.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]

    def test_gemini_with_google_api_key(self):
        """Test that GOOGLE_API_KEY works as fallback for GEMINI_KEY."""
        env_backup = {}
        for key in ['LLM_PROVIDER', 'GEMINI_KEY', 'GOOGLE_API_KEY']:
            env_backup[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]
        
        # Set GOOGLE_API_KEY but not GEMINI_KEY
        os.environ['GOOGLE_API_KEY'] = 'test-google-key'
        
        try:
            with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock_gemini:
                mock_gemini.return_value = Mock()
                from llm_config import get_llm
                
                llm = get_llm()
                
                # Verify ChatGoogleGenerativeAI was called with GOOGLE_API_KEY
                call_kwargs = mock_gemini.call_args[1]
                assert call_kwargs['google_api_key'] == 'test-google-key'
        finally:
            for key, value in env_backup.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]

    def test_custom_gemini_model(self):
        """Test using a custom Gemini model via environment variable."""
        env_backup = {
            'GEMINI_MODEL': os.environ.get('GEMINI_MODEL'),
            'GEMINI_KEY': os.environ.get('GEMINI_KEY'),
        }
        
        os.environ['GEMINI_MODEL'] = 'gemini-1.5-pro'
        os.environ['GEMINI_KEY'] = 'test-key'
        
        try:
            with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock_gemini:
                mock_gemini.return_value = Mock()
                from llm_config import get_llm
                
                llm = get_llm()
                
                # Verify ChatGoogleGenerativeAI was called with custom model
                call_kwargs = mock_gemini.call_args[1]
                assert call_kwargs['model'] == 'gemini-1.5-pro'
        finally:
            for key, value in env_backup.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]

    def test_openai_provider_selection(self):
        """Test selecting OpenAI via environment variable."""
        env_backup = {
            'LLM_PROVIDER': os.environ.get('LLM_PROVIDER'),
            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
        }
        
        os.environ['LLM_PROVIDER'] = 'openai'
        os.environ['OPENAI_API_KEY'] = 'test-key'
        
        try:
            with patch('langchain_openai.ChatOpenAI') as mock_openai:
                mock_openai.return_value = Mock()
                from llm_config import get_llm, get_provider_name, get_api_key_env_var
                
                llm = get_llm()
                
                # Verify ChatOpenAI was called with default model
                mock_openai.assert_called_once()
                call_kwargs = mock_openai.call_args[1]
                assert call_kwargs['model_name'] == 'gpt-3.5-turbo'
                assert call_kwargs['temperature'] == 0.7
                
                # Verify provider name
                assert get_provider_name() == "OpenAI"
                assert get_api_key_env_var() == "OPENAI_API_KEY"
        finally:
            for key, value in env_backup.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]

    def test_custom_openai_model(self):
        """Test using a custom OpenAI model via environment variable."""
        env_backup = {
            'LLM_PROVIDER': os.environ.get('LLM_PROVIDER'),
            'OPENAI_MODEL': os.environ.get('OPENAI_MODEL'),
            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
        }
        
        os.environ['LLM_PROVIDER'] = 'openai'
        os.environ['OPENAI_MODEL'] = 'gpt-4'
        os.environ['OPENAI_API_KEY'] = 'test-key'
        
        try:
            with patch('langchain_openai.ChatOpenAI') as mock_openai:
                mock_openai.return_value = Mock()
                from llm_config import get_llm
                
                llm = get_llm()
                
                # Verify ChatOpenAI was called with custom model
                call_kwargs = mock_openai.call_args[1]
                assert call_kwargs['model_name'] == 'gpt-4'
        finally:
            for key, value in env_backup.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]

    def test_explicit_model_overrides_env(self):
        """Test that explicit model parameter overrides environment variable."""
        env_backup = {
            'GEMINI_MODEL': os.environ.get('GEMINI_MODEL'),
            'GEMINI_KEY': os.environ.get('GEMINI_KEY'),
        }
        
        os.environ['GEMINI_MODEL'] = 'gemini-1.5-flash'
        os.environ['GEMINI_KEY'] = 'test-key'
        
        try:
            with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock_gemini:
                mock_gemini.return_value = Mock()
                from llm_config import get_llm
                
                llm = get_llm(model_name='gemini-1.5-pro')
                
                # Verify the explicit model name was used, not the env var
                call_kwargs = mock_gemini.call_args[1]
                assert call_kwargs['model'] == 'gemini-1.5-pro'
        finally:
            for key, value in env_backup.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]

    def test_custom_temperature(self):
        """Test using a custom temperature parameter."""
        env_backup = {
            'GEMINI_KEY': os.environ.get('GEMINI_KEY'),
        }
        
        os.environ['GEMINI_KEY'] = 'test-key'
        
        try:
            with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock_gemini:
                mock_gemini.return_value = Mock()
                from llm_config import get_llm
                
                llm = get_llm(temperature=0.3)
                
                # Verify the custom temperature was used
                call_kwargs = mock_gemini.call_args[1]
                assert call_kwargs['temperature'] == 0.3
        finally:
            for key, value in env_backup.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
