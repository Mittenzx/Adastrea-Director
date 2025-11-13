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
        from langchain_openai import ChatOpenAI
        
        model = model_name or os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
        return ChatOpenAI(
            model_name=model,
            temperature=temperature
        )
    else:
        # Default to Google Gemini (recommended provider)
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Use gemini-1.5-flash for best value (73% cheaper than GPT-3.5, excellent quality)
        # Use gemini-1.5-pro for complex planning tasks
        model = model_name or os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        
        # GEMINI_KEY is the primary env var, but also support GOOGLE_API_KEY for compatibility
        api_key = os.environ.get("GEMINI_KEY") or os.environ.get("GOOGLE_API_KEY")
        
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=api_key
        )


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
