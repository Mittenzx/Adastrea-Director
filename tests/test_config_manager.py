#!/usr/bin/env python3
"""
Unit tests for the configuration manager.

Tests cover:
- Configuration directory creation
- Reading and writing configuration
- API key encryption and decryption
- File permissions (on Unix-like systems)
- Config file cleanup
"""

import os
import sys
import json
import stat
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config_manager


class TestConfigManager:
    """Test configuration manager functionality."""

    @pytest.fixture(autouse=True)
    def setup_temp_config(self, tmp_path):
        """Set up a temporary config directory for each test."""
        self.original_get_config_dir = config_manager._get_config_dir
        
        # Create a temp directory for config
        self.temp_config_dir = tmp_path / ".adastrea"
        
        # Mock the config directory to use temp location
        config_manager._get_config_dir = lambda: self.temp_config_dir
        
        yield
        
        # Restore original function
        config_manager._get_config_dir = self.original_get_config_dir
        
        # Clean up temp directory
        if self.temp_config_dir.exists():
            shutil.rmtree(self.temp_config_dir)

    def test_config_dir_creation(self):
        """Test that configuration directory is created with correct permissions."""
        config_manager._ensure_config_dir()
        
        assert self.temp_config_dir.exists()
        assert self.temp_config_dir.is_dir()
        
        # Check permissions on Unix-like systems
        if os.name != 'nt':
            mode = os.stat(self.temp_config_dir).st_mode
            # Directory should be 700 (rwx for owner only)
            assert stat.S_IMODE(mode) == stat.S_IRWXU

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        test_config = {
            "test_key": "test_value",
            "nested": {
                "key": "value"
            }
        }
        
        config_manager.save_config(test_config)
        loaded_config = config_manager.load_config()
        
        assert loaded_config == test_config

    def test_load_nonexistent_config(self):
        """Test loading config when file doesn't exist."""
        loaded_config = config_manager.load_config()
        assert loaded_config == {}

    def test_config_file_permissions(self):
        """Test that config file has secure permissions."""
        test_config = {"test": "data"}
        config_manager.save_config(test_config)
        
        config_file = config_manager._get_config_file()
        assert config_file.exists()
        
        # Check permissions on Unix-like systems
        if os.name != 'nt':
            mode = os.stat(config_file).st_mode
            # File should be 600 (rw for owner only)
            expected_mode = stat.S_IRUSR | stat.S_IWUSR
            assert stat.S_IMODE(mode) == expected_mode

    def test_encrypt_decrypt_value(self):
        """Test encryption and decryption of values."""
        original_value = "my-secret-api-key-12345"
        
        encrypted = config_manager._encrypt_value(original_value)
        assert encrypted != original_value  # Should be encrypted
        assert len(encrypted) > 0
        
        decrypted = config_manager._decrypt_value(encrypted)
        assert decrypted == original_value

    def test_encrypt_empty_string(self):
        """Test encrypting empty string."""
        encrypted = config_manager._encrypt_value("")
        assert encrypted == ""
        
        decrypted = config_manager._decrypt_value("")
        assert decrypted == ""

    def test_decrypt_invalid_value(self):
        """Test decrypting invalid encrypted value."""
        # Should return empty string on decryption failure
        decrypted = config_manager._decrypt_value("invalid-encrypted-data")
        assert decrypted == ""

    def test_set_and_get_api_key(self):
        """Test setting and getting API key."""
        test_key = "test-gemini-api-key-xyz"
        
        config_manager.set_api_key("gemini", test_key)
        retrieved_key = config_manager.get_api_key("gemini")
        
        assert retrieved_key == test_key

    def test_get_nonexistent_api_key(self):
        """Test getting API key that doesn't exist."""
        retrieved_key = config_manager.get_api_key("nonexistent")
        assert retrieved_key is None

    def test_set_multiple_api_keys(self):
        """Test setting multiple API keys for different providers."""
        gemini_key = "gemini-key-123"
        openai_key = "openai-key-456"
        
        config_manager.set_api_key("gemini", gemini_key)
        config_manager.set_api_key("openai", openai_key)
        
        assert config_manager.get_api_key("gemini") == gemini_key
        assert config_manager.get_api_key("openai") == openai_key

    def test_clear_api_key(self):
        """Test clearing a specific API key."""
        test_key = "test-api-key"
        
        config_manager.set_api_key("gemini", test_key)
        assert config_manager.get_api_key("gemini") == test_key
        
        config_manager.clear_api_key("gemini")
        assert config_manager.get_api_key("gemini") is None

    def test_clear_nonexistent_api_key(self):
        """Test clearing API key that doesn't exist (should not raise error)."""
        config_manager.clear_api_key("nonexistent")
        # Should complete without error

    def test_clear_all_config(self):
        """Test clearing all configuration."""
        config_manager.set_api_key("gemini", "test-key-1")
        config_manager.set_api_key("openai", "test-key-2")
        
        assert config_manager.config_exists()
        
        config_manager.clear_all_config()
        
        assert not config_manager.config_exists()
        assert config_manager.get_api_key("gemini") is None
        assert config_manager.get_api_key("openai") is None

    def test_config_exists(self):
        """Test checking if config file exists."""
        assert not config_manager.config_exists()
        
        config_manager.set_api_key("gemini", "test-key")
        assert config_manager.config_exists()

    def test_get_config_location(self):
        """Test getting config file location."""
        location = config_manager.get_config_location()
        assert isinstance(location, str)
        assert location.endswith("config.json")
        assert ".adastrea" in location

    def test_api_key_case_insensitive(self):
        """Test that provider names are case-insensitive."""
        test_key = "test-key-123"
        
        config_manager.set_api_key("GEMINI", test_key)
        assert config_manager.get_api_key("gemini") == test_key
        assert config_manager.get_api_key("Gemini") == test_key
        assert config_manager.get_api_key("GEMINI") == test_key

    def test_machine_key_consistency(self):
        """Test that machine key is consistent across calls."""
        key1 = config_manager._get_machine_key()
        key2 = config_manager._get_machine_key()
        
        assert key1 == key2
        assert len(key1) == 44  # Base64 encoded 32 bytes

    def test_config_json_format(self):
        """Test that config file is valid JSON."""
        config_manager.set_api_key("gemini", "test-key")
        
        config_file = config_manager._get_config_file()
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, dict)
        assert "api_keys" in data
        assert isinstance(data["api_keys"], dict)

    def test_update_existing_api_key(self):
        """Test updating an existing API key."""
        old_key = "old-api-key"
        new_key = "new-api-key"
        
        config_manager.set_api_key("gemini", old_key)
        assert config_manager.get_api_key("gemini") == old_key
        
        config_manager.set_api_key("gemini", new_key)
        assert config_manager.get_api_key("gemini") == new_key

    def test_load_corrupted_config(self):
        """Test loading corrupted config file."""
        config_file = config_manager._get_config_file()
        config_manager._ensure_config_dir()
        
        # Write invalid JSON
        with open(config_file, 'w') as f:
            f.write("invalid json {{{")
        
        # Should return empty dict instead of raising error
        loaded_config = config_manager.load_config()
        assert loaded_config == {}

    def test_save_config_creates_directory(self):
        """Test that save_config creates directory if it doesn't exist."""
        # Ensure directory doesn't exist
        if self.temp_config_dir.exists():
            shutil.rmtree(self.temp_config_dir)
        
        config_manager.save_config({"test": "data"})
        
        assert self.temp_config_dir.exists()
        assert config_manager._get_config_file().exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
