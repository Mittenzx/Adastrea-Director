#!/usr/bin/env python3
"""
Test script to verify API validation ImportError handling.
This tests the fix for the issue where missing dependencies cause generic error messages.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the plugin path to sys.path
plugin_path = os.path.join(os.path.dirname(__file__), 'Plugins', 'AdastreaDirector', 'Python')
sys.path.insert(0, plugin_path)

# Import the IPC server
from ipc_server import IPCServer


class TestAPIValidationImportError(unittest.TestCase):
    """Test that API validation handles missing dependencies gracefully."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server = IPCServer(port=0)  # Use port 0 to avoid binding
    
    def test_gemini_missing_dependency(self):
        """Test that missing google-generativeai gives helpful error message."""
        # Mock the import to fail
        with patch.dict('sys.modules', {'google.generativeai': None}):
            # Force ImportError by preventing the import
            original_import = __builtins__.__import__
            
            def mock_import(name, *args, **kwargs):
                if name == 'google.generativeai' or name.startswith('google.generativeai'):
                    raise ImportError("No module named 'google.generativeai'")
                return original_import(name, *args, **kwargs)
            
            with patch('builtins.__import__', side_effect=mock_import):
                result = self.server._validate_gemini_key('fake-api-key')
                
                # Should return success status but with valid=False
                self.assertEqual(result['status'], 'success')
                self.assertEqual(result['valid'], False)
                self.assertEqual(result['provider'], 'gemini')
                
                # Should have helpful error message
                self.assertIn('not installed', result['error'].lower())
                self.assertIn('pip install', result['error'].lower())
                
                # Should NOT be the generic error message
                self.assertNotIn('unexpected error', result['error'].lower())
    
    def test_openai_missing_dependency(self):
        """Test that missing openai library gives helpful error message."""
        # Mock the import to fail
        original_import = __builtins__.__import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'openai' or name.startswith('openai'):
                raise ImportError("No module named 'openai'")
            return original_import(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            result = self.server._validate_openai_key('fake-api-key')
            
            # Should return success status but with valid=False
            self.assertEqual(result['status'], 'success')
            self.assertEqual(result['valid'], False)
            self.assertEqual(result['provider'], 'openai')
            
            # Should have helpful error message
            self.assertIn('not installed', result['error'].lower())
            self.assertIn('pip install', result['error'].lower())
            
            # Should NOT be the generic error message
            self.assertNotIn('unexpected error', result['error'].lower())
    
    def test_openrouter_missing_dependency(self):
        """Test that missing openai library for OpenRouter gives helpful error message."""
        # Mock the import to fail
        original_import = __builtins__.__import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'openai' or name.startswith('openai'):
                raise ImportError("No module named 'openai'")
            return original_import(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            result = self.server._validate_openrouter_key('fake-api-key')
            
            # Should return success status but with valid=False
            self.assertEqual(result['status'], 'success')
            self.assertEqual(result['valid'], False)
            self.assertEqual(result['provider'], 'openrouter')
            
            # Should have helpful error message
            self.assertIn('not installed', result['error'].lower())
            # OpenRouter uses OpenAI library so message should mention that
            self.assertTrue(
                'openai' in result['error'].lower() or 
                'required for openrouter' in result['error'].lower()
            )


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
