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

from logging_config import get_logger

logger = get_logger(__name__)


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
        Base64-urlsafe-encoded bytes representing a 32-byte key (44 bytes when encoded)
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
        Fernet token (base64-encoded encrypted value)
    """
    if not value:
        return ""

    key = _get_machine_key()
    f = Fernet(key)
    encrypted = f.encrypt(value.encode())
    return encrypted.decode()  # Fernet tokens are already base64-encoded


def _decrypt_value(encrypted_value: str) -> str:
    """
    Decrypt a configuration value.
    
    Automatically strips leading/trailing whitespace from decrypted values
    to handle copy-paste errors. This is a non-breaking enhancement since
    API keys should never contain meaningful leading/trailing whitespace.

    Args:
        encrypted_value: The Fernet token (base64-encoded encrypted value)

    Returns:
        Decrypted value with leading/trailing whitespace stripped
    """
    if not encrypted_value:
        return ""

    try:
        key = _get_machine_key()
        f = Fernet(key)
        encrypted = encrypted_value.encode()
        decrypted = f.decrypt(encrypted)
        # Strip whitespace to handle copy-paste errors
        return decrypted.decode().strip()
    except Exception as e:
        # If decryption fails, log the error and return empty string
        logger.error(f"Failed to decrypt configuration value: {e}")
        return ""


def _ensure_config_dir() -> None:
    """
    Ensure the configuration directory exists with secure permissions.

    Creates the directory if it doesn't exist and sets permissions to 700
    (owner read/write/execute only) on Unix-like systems.
    """
    config_dir = _get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Configuration directory ensured: {config_dir}")

    # Set secure permissions on Unix-like systems
    if os.name != 'nt':  # Not Windows
        try:
            os.chmod(config_dir, stat.S_IRWXU)  # 700
            logger.debug(f"Set secure permissions (700) on: {config_dir}")
        except Exception as e:
            logger.warning(f"Failed to set secure permissions on {config_dir}: {e}")


def _ensure_config_file_permissions() -> None:
    """
    Ensure the configuration file has secure permissions.

    Sets permissions to 600 (owner read/write only) on Unix-like systems.
    """
    config_file = _get_config_file()
    if config_file.exists() and os.name != 'nt':  # Not Windows
        try:
            os.chmod(config_file, stat.S_IRUSR | stat.S_IWUSR)  # 600
            logger.debug(f"Set secure permissions (600) on: {config_file}")
        except Exception as e:
            logger.warning(f"Failed to set secure permissions on {config_file}: {e}")


def load_config() -> Dict[str, Any]:
    """
    Load configuration from the config file.

    Returns:
        Dictionary containing configuration values
    """
    config_file = _get_config_file()

    if not config_file.exists():
        logger.debug(f"Configuration file not found: {config_file}")
        return {}

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        logger.debug(f"Configuration loaded successfully from: {config_file}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration from {config_file}: {e}")
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
        logger.info(f"Configuration saved successfully to: {config_file}")
    except Exception as e:
        logger.error(f"Failed to save configuration to {config_file}: {e}")
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
        logger.debug(f"Retrieved API key for provider: {provider}")
        return _decrypt_value(encrypted_key)

    logger.debug(f"No API key found for provider: {provider}")
    return None


def set_api_key(provider: str, api_key: str) -> None:
    """
    Save API key for the specified provider to local config.

    Automatically strips leading/trailing whitespace from API keys
    to prevent authentication issues from copy-paste operations.

    Args:
        provider: The LLM provider ("gemini" or "openai")
        api_key: The API key to save (whitespace will be automatically stripped)
    """
    provider = provider.lower()
    config = load_config()

    if "api_keys" not in config:
        config["api_keys"] = {}

    # Strip whitespace before encrypting to prevent copy-paste issues
    api_key = api_key.strip() if api_key else ""
    
    # Encrypt the API key before storing
    config["api_keys"][provider] = _encrypt_value(api_key)
    save_config(config)
    logger.info(f"API key set successfully for provider: {provider}")


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
        logger.info(f"API key cleared for provider: {provider}")
    else:
        logger.debug(f"No API key to clear for provider: {provider}")


def clear_all_config() -> None:
    """
    Clear all configuration data.

    Removes the entire config file.
    """
    config_file = _get_config_file()
    if config_file.exists():
        try:
            config_file.unlink()
            logger.info(f"Configuration cleared: {config_file}")
        except Exception as e:
            logger.error(f"Failed to clear configuration {config_file}: {e}")
            raise RuntimeError(f"Failed to clear configuration: {e}")
    else:
        logger.debug(f"No configuration file to clear: {config_file}")


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
