#!/usr/bin/env python3
"""
Custom exceptions for the Adastrea Director.

This module defines custom exception classes that provide better
error categorization and more descriptive error messages throughout
the application.
"""

from typing import Any


class AdastreaDirectorError(Exception):
    """Base exception class for all Adastrea Director errors."""
    
    def __init__(self, message: str, details: str = None):
        """
        Initialize the exception.
        
        Args:
            message: Main error message
            details: Additional details about the error
        """
        self.message = message
        self.details = details
        super().__init__(self.format_message())
    
    def format_message(self) -> str:
        """Format the complete error message."""
        if self.details:
            return f"{self.message}\nDetails: {self.details}"
        return self.message


class ConfigurationError(AdastreaDirectorError):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(f"Configuration Error: {message}", details)


class APIKeyError(AdastreaDirectorError):
    """Exception raised when API key is missing or invalid."""
    
    def __init__(self, service: str = "OpenAI", details: str = None):
        message = f"Missing or invalid API key for {service}"
        if not details:
            details = (
                f"Please set the {service.upper()}_API_KEY environment variable.\n"
                f"You can add it to a .env file in the project root."
            )
        super().__init__(message, details)


class DocumentLoadError(AdastreaDirectorError):
    """Exception raised when document loading fails."""
    
    def __init__(self, file_path: str, reason: str, details: str = None):
        message = f"Failed to load document: {file_path}"
        if not details:
            details = f"Reason: {reason}"
        super().__init__(message, details)


class DatabaseError(AdastreaDirectorError):
    """Exception raised for database-related errors."""
    
    def __init__(self, operation: str, details: str = None):
        message = f"Database operation failed: {operation}"
        super().__init__(message, details)


class NetworkError(AdastreaDirectorError):
    """Exception raised for network-related errors."""
    
    def __init__(self, operation: str, details: str = None):
        message = f"Network operation failed: {operation}"
        if not details:
            details = (
                "This could be due to:\n"
                "  - No internet connection\n"
                "  - API service temporarily unavailable\n"
                "  - Firewall or proxy blocking the connection\n"
                "Please check your network connection and try again."
            )
        super().__init__(message, details)


class RateLimitError(NetworkError):
    """Exception raised when API rate limit is exceeded."""
    
    def __init__(self, service: str = "OpenAI API", details: str = None):
        if not details:
            details = (
                f"Rate limit exceeded for {service}. You have exceeded the API rate limit. Please:\n"
                "  - Wait a few minutes before trying again\n"
                "  - Consider upgrading your API plan for higher limits\n"
                "  - Reduce the chunk size to make fewer API calls"
            )
        super().__init__("rate limiting", details)


class ChunkingError(AdastreaDirectorError):
    """Exception raised when document chunking fails."""
    
    def __init__(self, reason: str, details: str = None):
        message = f"Failed to chunk documents: {reason}"
        super().__init__(message, details)


class QueryError(AdastreaDirectorError):
    """Exception raised when query processing fails."""
    
    def __init__(self, query: str, reason: str, details: str = None):
        message = f"Failed to process query"
        if not details:
            details = f"Query: {query[:100]}...\nReason: {reason}"
        super().__init__(message, details)


class ValidationError(AdastreaDirectorError):
    """Exception raised when input validation fails."""
    
    def __init__(self, field: str, value: Any, constraint: str):
        message = f"Invalid value for {field}"
        details = f"Value: {value}\nConstraint: {constraint}"
        super().__init__(message, details)


class EmptyDatabaseError(DatabaseError):
    """Exception raised when attempting to query an empty database."""
    
    def __init__(self, collection_name: str):
        details = (
            f"The collection '{collection_name}' contains no documents.\n"
            f"Please ingest documents first using:\n"
            f"  python ingest.py --docs-dir <your_docs_directory>"
        )
        super().__init__("query", details)


class UnsupportedFileTypeError(DocumentLoadError):
    """Exception raised when attempting to load an unsupported file type."""
    
    def __init__(self, file_path: str, extension: str):
        reason = f"Unsupported file extension: {extension}"
        details = (
            f"Supported file types:\n"
            f"  - Markdown (.md)\n"
            f"  - Text (.txt)\n"
            f"  - Python (.py)\n"
            f"  - PDF (.pdf)\n"
            f"  - Word (.docx)\n"
            f"\nThe file will be treated as plain text."
        )
        super().__init__(file_path, reason, details)


class FileEncodingError(DocumentLoadError):
    """Exception raised when file has encoding issues."""
    
    def __init__(self, file_path: str, encoding: str = "utf-8"):
        reason = f"Unable to decode file with {encoding} encoding"
        details = (
            f"The file appears to have encoding issues.\n"
            f"Try:\n"
            f"  - Converting the file to UTF-8 encoding\n"
            f"  - Checking if the file is corrupted\n"
            f"  - Verifying the file is a text-based format"
        )
        super().__init__(file_path, reason, details)


class CorruptedFileError(DocumentLoadError):
    """Exception raised when file appears to be corrupted."""
    
    def __init__(self, file_path: str, file_type: str):
        reason = f"File appears to be corrupted or invalid {file_type}"
        details = (
            f"The file could not be parsed properly.\n"
            f"Try:\n"
            f"  - Opening and re-saving the file in its native application\n"
            f"  - Checking if the file extension matches the actual file type\n"
            f"  - Verifying the file is not truncated or damaged"
        )
        super().__init__(file_path, reason, details)
