#!/usr/bin/env python3
"""
LLM Configuration Module

This module provides a unified interface for different LLM providers.
Currently supports:
- Google Gemini (default)
- OpenAI (legacy support)

Environment Variables:
- GEMINI_KEY: API key for Google Gemini (default provider)
- GEMINI_MODEL: Model to use (default: gemini-1.5-flash)
- OPENAI_API_KEY: API key for OpenAI (legacy, if LLM_PROVIDER=openai)
- LLM_PROVIDER: Provider to use (gemini or openai, default: gemini)
"""

import os
from typing import Optional
try:
    from config_manager import get_api_key as get_stored_api_key
    CONFIG_MANAGER_AVAILABLE = True
except ImportError:
    CONFIG_MANAGER_AVAILABLE = False


def get_llm(model_name: Optional[str] = None, temperature: float = 0.7):
    """
    Get LLM instance based on configuration.
    
    Args:
        model_name: Optional model name to use. If not provided, uses defaults:
                   - Gemini: gemini-1.5-flash
                   - OpenAI: gpt-3.5-turbo
        temperature: Temperature for response generation (0-1)
    
    Returns:
        LLM instance (ChatGoogleGenerativeAI or ChatOpenAI)
    
    Raises:
        ImportError: If required LangChain dependencies are not installed
    
    Environment Variables:
        LLM_PROVIDER: Which provider to use (gemini or openai). Default: gemini
        GEMINI_KEY: API key for Google Gemini
        GEMINI_MODEL: Default Gemini model (default: gemini-1.5-flash)
        OPENAI_API_KEY: API key for OpenAI (only if using openai provider)
        OPENAI_MODEL: Default OpenAI model (default: gpt-3.5-turbo)
    
    Example:
        >>> llm = get_llm()  # Uses Gemini by default
        >>> llm = get_llm(model_name="gemini-1.5-pro", temperature=0.3)
        >>> llm = get_llm(model_name="gpt-4", temperature=0.7)  # If LLM_PROVIDER=openai
    """
    provider = os.environ.get("LLM_PROVIDER", "gemini").lower()
    
    if provider == "openai":
        # Legacy OpenAI support
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as e:
            raise ImportError(
                f"Missing required dependencies for OpenAI LLM provider.\n"
                f"Error: {e}\n\n"
                f"To fix this, please install the required dependencies:\n"
                f"  pip install -r requirements.txt\n\n"
                f"Or install the specific package:\n"
                f"  pip install langchain-openai>=0.3.0\n\n"
                f"If you're running from Unreal Engine, ensure dependencies are installed "
                f"in the Python environment used by the plugin."
            ) from e
        
        model = model_name or os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
        
        # Priority: stored config -> OPENAI_API_KEY env var
        api_key = None
        if CONFIG_MANAGER_AVAILABLE:
            api_key = get_stored_api_key("openai")
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY")
        
        kwargs = {
            "model_name": model,
            "temperature": temperature
        }
        if api_key:
            kwargs["api_key"] = api_key
        
        return ChatOpenAI(**kwargs)
    else:
        # Default to Google Gemini (recommended provider)
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError as e:
            raise ImportError(
                f"Missing required dependencies for Gemini LLM provider.\n"
                f"Error: {e}\n\n"
                f"To fix this, please install the required dependencies:\n"
                f"  pip install -r requirements.txt\n\n"
                f"Or install the specific package:\n"
                f"  pip install langchain-google-genai>=2.0.5\n\n"
                f"If you're running from Unreal Engine, ensure dependencies are installed "
                f"in the Python environment used by the plugin.\n\n"
                f"Quick setup:\n"
                f"  1. Navigate to the repository root directory\n"
                f"  2. Run: pip install -r requirements.txt\n"
                f"  3. Restart Unreal Engine Editor"
            ) from e
        
        # Use gemini-1.5-flash for best value (73% cheaper than GPT-3.5, excellent quality)
        # Use gemini-1.5-pro for complex planning tasks
        model = model_name or os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        
        # Priority: stored config -> GEMINI_KEY env var -> GOOGLE_API_KEY env var
        api_key = None
        if CONFIG_MANAGER_AVAILABLE:
            api_key = get_stored_api_key("gemini")
        if not api_key:
            api_key = os.environ.get("GEMINI_KEY") or os.environ.get("GOOGLE_API_KEY")
        
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=api_key
        )


def check_dependencies_available() -> tuple[bool, Optional[str]]:
    """
    Check if required LLM dependencies are available.
    
    Returns:
        Tuple of (available: bool, error_message: Optional[str])
        If available is True, error_message is None.
        If available is False, error_message contains helpful installation instructions.
    """
    provider = os.environ.get("LLM_PROVIDER", "gemini").lower()
    
    try:
        if provider == "openai":
            import langchain_openai
            return (True, None)
        else:
            import langchain_google_genai
            return (True, None)
    except ImportError as e:
        error_msg = (
            f"Missing required dependencies for {provider.upper()} LLM provider.\n"
            f"Error: {e}\n\n"
            f"To fix this, please install the required dependencies:\n"
            f"  pip install -r requirements.txt\n\n"
        )
        
        if provider == "openai":
            error_msg += (
                f"Or install the specific package:\n"
                f"  pip install langchain-openai>=0.3.0\n"
            )
        else:
            error_msg += (
                f"Or install the specific package:\n"
                f"  pip install langchain-google-genai>=2.0.5\n"
            )
        
        error_msg += (
            f"\nIf you're running from Unreal Engine, ensure dependencies are installed "
            f"in the Python environment used by the plugin.\n\n"
            f"Quick setup:\n"
            f"  1. Navigate to the repository root directory\n"
            f"  2. Run: pip install -r requirements.txt\n"
            f"  3. Restart Unreal Engine Editor"
        )
        
        return (False, error_msg)


def get_provider_name() -> str:
    """
    Get the name of the current LLM provider.
    
    Returns:
        String: "Gemini" or "OpenAI"
    """
    provider = os.environ.get("LLM_PROVIDER", "gemini").lower()
    return "OpenAI" if provider == "openai" else "Gemini"


def get_api_key_env_var() -> str:
    """
    Get the environment variable name for the current provider's API key.
    
    Returns:
        String: "GEMINI_KEY" or "OPENAI_API_KEY"
    """
    provider = os.environ.get("LLM_PROVIDER", "gemini").lower()
    return "OPENAI_API_KEY" if provider == "openai" else "GEMINI_KEY"
