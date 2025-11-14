#!/usr/bin/env python3
"""
Configuration Manager for Adastrea Director

Manages persistent configuration storage for API keys and other settings.
Configuration is stored in the user's home directory to persist across
repository clones and updates.

Storage location:
- Unix/Linux/macOS: ~/.adastrea/config.json
- Windows: %USERPROFILE%/.adastrea/config.json

Security:
- Config file has restricted permissions (600 on Unix-like systems)
- API keys are encrypted using a machine-specific key
- Config directory is created with secure permissions
"""

import os
import json
import stat
from pathlib import Path
from typing import Optional, Dict, Any
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def _get_config_dir() -> Path:
    """
    Get the configuration directory path.

    Returns:
        Path to the configuration directory (~/.adastrea/)
    """
    return Path.home() / ".adastrea"


def _get_config_file() -> Path:
    """
    Get the configuration file path.

    Returns:
        Path to the configuration file (~/.adastrea/config.json)
    """
    return _get_config_dir() / "config.json"


def _get_machine_key() -> bytes:
    """
    Generate a machine-specific encryption key.

    Uses a combination of username and machine name to create a unique key
    for encrypting API keys. This provides basic encryption that ties the
    config to the specific machine.

    Returns:
        32-byte encryption key
    """
    import socket
    import getpass

    # Create a machine-specific salt from username and hostname
    username = getpass.getuser()
    hostname = socket.gethostname()
    salt = f"{username}@{hostname}".encode()

    # Derive a key using PBKDF2HMAC
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(b"adastrea-director-config"))
    return key


def _encrypt_value(value: str) -> str:
    """
    Encrypt a configuration value.

    Args:
        value: The value to encrypt

    Returns:
        Base64-encoded encrypted value
    """
    if not value:
        return ""

    key = _get_machine_key()
    f = Fernet(key)
    encrypted = f.encrypt(value.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def _decrypt_value(encrypted_value: str) -> str:
    """
    Decrypt a configuration value.

    Args:
        encrypted_value: The base64-encoded encrypted value

    Returns:
        Decrypted value
    """
    if not encrypted_value:
        return ""

    try:
        key = _get_machine_key()
        f = Fernet(key)
        encrypted = base64.urlsafe_b64decode(encrypted_value.encode())
        decrypted = f.decrypt(encrypted)
        return decrypted.decode()
    except Exception:
        # If decryption fails, return empty string
        return ""


def _ensure_config_dir() -> None:
    """
    Ensure the configuration directory exists with secure permissions.

    Creates the directory if it doesn't exist and sets permissions to 700
    (owner read/write/execute only) on Unix-like systems.
    """
    config_dir = _get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    # Set secure permissions on Unix-like systems
    if os.name != 'nt':  # Not Windows
        try:
            os.chmod(config_dir, stat.S_IRWXU)  # 700
        except Exception:
            pass  # Ignore permission errors


def _ensure_config_file_permissions() -> None:
    """
    Ensure the configuration file has secure permissions.

    Sets permissions to 600 (owner read/write only) on Unix-like systems.
    """
    config_file = _get_config_file()
    if config_file.exists() and os.name != 'nt':  # Not Windows
        try:
            os.chmod(config_file, stat.S_IRUSR | stat.S_IWUSR)  # 600
        except Exception:
            pass  # Ignore permission errors


def load_config() -> Dict[str, Any]:
    """
    Load configuration from the config file.

    Returns:
        Dictionary containing configuration values
    """
    config_file = _get_config_file()

    if not config_file.exists():
        return {}

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except Exception:
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """
    Save configuration to the config file.

    Args:
        config: Dictionary containing configuration values
    """
    _ensure_config_dir()
    config_file = _get_config_file()

    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        _ensure_config_file_permissions()
    except Exception as e:
        raise RuntimeError(f"Failed to save configuration: {e}")


def get_api_key(provider: str = "gemini") -> Optional[str]:
    """
    Get API key for the specified provider from local config.

    Args:
        provider: The LLM provider ("gemini" or "openai")

    Returns:
        Decrypted API key or None if not found
    """
    config = load_config()
    encrypted_keys = config.get("api_keys", {})

    provider = provider.lower()
    encrypted_key = encrypted_keys.get(provider)

    if encrypted_key:
        return _decrypt_value(encrypted_key)

    return None


def set_api_key(provider: str, api_key: str) -> None:
    """
    Save API key for the specified provider to local config.

    Args:
        provider: The LLM provider ("gemini" or "openai")
        api_key: The API key to save
    """
    provider = provider.lower()
    config = load_config()

    if "api_keys" not in config:
        config["api_keys"] = {}

    # Encrypt the API key before storing
    config["api_keys"][provider] = _encrypt_value(api_key)
    save_config(config)


def clear_api_key(provider: str) -> None:
    """
    Remove API key for the specified provider from local config.

    Args:
        provider: The LLM provider ("gemini" or "openai")
    """
    provider = provider.lower()
    config = load_config()

    if "api_keys" in config and provider in config["api_keys"]:
        del config["api_keys"][provider]
        save_config(config)


def clear_all_config() -> None:
    """
    Clear all configuration data.

    Removes the entire config file.
    """
    config_file = _get_config_file()
    if config_file.exists():
        try:
            config_file.unlink()
        except Exception as e:
            raise RuntimeError(f"Failed to clear configuration: {e}")


def get_config_location() -> str:
    """
    Get the path to the configuration file.

    Returns:
        String path to the config file
    """
    return str(_get_config_file())


def config_exists() -> bool:
    """
    Check if configuration file exists.

    Returns:
        True if config file exists, False otherwise
    """
    return _get_config_file().exists()
