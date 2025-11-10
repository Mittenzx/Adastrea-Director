# Error Handling Documentation

This document describes the error handling system in Adastrea Director, including common error types, troubleshooting steps, and best practices.

## Table of Contents

1. [Overview](#overview)
2. [Error Categories](#error-categories)
3. [Common Errors and Solutions](#common-errors-and-solutions)
4. [Error Recovery](#error-recovery)
5. [For Developers](#for-developers)

---

## Overview

Adastrea Director implements comprehensive error handling throughout the document loading and query processing workflows. The system is designed to:

- **Categorize errors** into specific types for better debugging
- **Provide descriptive messages** that explain what went wrong and how to fix it
- **Prevent crashes** by catching and handling exceptions gracefully
- **Guide users** toward solutions with actionable recommendations

---

## Error Categories

### 1. Configuration Errors

**Description:** Issues with system configuration or parameters.

**Common Causes:**
- Invalid chunk size or overlap values
- Missing or malformed configuration files
- Invalid collection names or paths

**Example:**
```
Configuration Error: Invalid value for chunk_size
Value: -100
Constraint: Must be greater than 0
```

**Solution:**
- Check your command-line arguments
- Ensure chunk_size > 0
- Ensure chunk_overlap < chunk_size
- Verify collection names are valid strings

---

### 2. API Key Errors

**Description:** Missing or invalid API keys for external services.

**Common Causes:**
- OPENAI_API_KEY not set in environment
- Invalid or expired API key
- API key with insufficient permissions

**Example:**
```
Missing or invalid API key for OpenAI
Details: Please set the OPENAI_API_KEY environment variable.
You can add it to a .env file in the project root.
```

**Solution:**
1. Create a `.env` file in the project root if it doesn't exist
2. Add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```
3. Verify the key is valid at https://platform.openai.com/api-keys
4. Restart the application

---

### 3. Document Loading Errors

**Description:** Problems loading or parsing document files.

#### File Not Found

**Example:**
```
Error: File /path/to/file.txt does not exist
```

**Solution:**
- Verify the file path is correct
- Check for typos in the filename
- Ensure the file hasn't been moved or deleted

#### File Encoding Errors

**Example:**
```
Failed to load document: document.txt
Details: Unable to decode file with utf-8 encoding
The file appears to have encoding issues.
```

**Solution:**
- Convert the file to UTF-8 encoding
- Use a text editor to re-save the file with UTF-8 encoding
- Check if the file is actually a binary file

#### Corrupted File Errors

**Example:**
```
Failed to load document: report.pdf
Details: File appears to be corrupted or invalid PDF
The file could not be parsed properly.
```

**Solution for PDF files:**
- Open the PDF in Adobe Reader or another PDF viewer
- If it opens, try exporting/saving it as a new PDF
- Verify the file extension matches the actual file type
- Check if the file download completed successfully

**Solution for DOCX files:**
- Open the document in Microsoft Word or LibreOffice
- Save it as a new .docx file
- Verify the file is not password-protected
- Check that the file is a valid Office document

#### Permission Errors

**Example:**
```
Error: Permission denied for file: protected_file.txt
Check that you have read permissions for this file
```

**Solution:**
- Check file permissions (on Unix: `ls -l filename`)
- Ensure your user account has read access
- On Windows, check file properties > Security tab
- Try running with appropriate permissions

#### Missing Dependencies

**Example:**
```
Error: Missing required library to load .pdf files
Details: No module named 'pypdf'
Install the required package using: pip install pypdf
```

**Solution:**
- Install the missing package: `pip install pypdf`
- For all dependencies: `pip install -r requirements.txt`
- Verify installation: `pip list | grep pypdf`

---

### 4. Database Errors

**Description:** Issues with the vector database (Chroma).

#### Empty Database

**Example:**
```
Cannot query empty database
Details: The collection 'adastrea_docs' contains no documents.
Please ingest documents first using:
  python ingest.py --docs-dir <your_docs_directory>
```

**Solution:**
1. Ingest documents before querying:
   ```bash
   python ingest.py --docs-dir ./your_documents
   ```
2. Verify documents were ingested successfully
3. Check the database statistics:
   ```bash
   python ingest.py --stats
   ```

#### Database Connection Errors

**Example:**
```
Database operation failed: ingestion
Details: Could not connect to database
```

**Solution:**
- Check if the persist directory exists and is writable
- Verify sufficient disk space
- Ensure no other process is locking the database
- Try deleting and recreating the database:
  ```bash
  rm -rf ./chroma_db
  python ingest.py --docs-dir ./your_documents
  ```

---

### 5. Network Errors

**Description:** Network-related issues when communicating with APIs.

#### Connection Errors

**Example:**
```
Network operation failed: embedding generation
Details: This could be due to:
  - No internet connection
  - API service temporarily unavailable
  - Firewall or proxy blocking the connection
Please check your network connection and try again.
```

**Solution:**
- Verify internet connectivity
- Check if openai.com is accessible
- Verify firewall/proxy settings
- Try again after a few moments
- Check OpenAI status page: https://status.openai.com

#### Timeout Errors

**Example:**
```
Network operation failed: query processing
Details: The request timed out. The API may be experiencing high load.
Try again in a few moments.
```

**Solution:**
- Wait a few minutes and try again
- Check your internet connection speed
- Verify OpenAI API status
- Consider reducing batch sizes for ingestion

#### Rate Limit Errors

**Example:**
```
Rate limit exceeded for OpenAI API
Details: You have exceeded the API rate limit. Please:
  - Wait a few minutes before trying again
  - Consider upgrading your API plan for higher limits
  - Reduce the chunk size to make fewer API calls
```

**Solution:**
- Wait 60 seconds before retrying
- Check your API usage at https://platform.openai.com/usage
- For ingestion, use larger chunk_size to reduce API calls:
  ```bash
  python ingest.py --docs-dir ./docs --chunk-size 2000
  ```
- Consider upgrading your OpenAI plan

---

### 6. Chunking Errors

**Description:** Problems during document chunking/splitting.

#### Invalid Document Format

**Example:**
```
Failed to chunk documents: Invalid document format
Details: One or more documents are not in the expected format.
Ensure all documents have 'page_content' and 'metadata' attributes.
```

**Solution:**
- This is usually an internal error
- Verify you're using supported file types
- Check if files are corrupted
- Report the issue if it persists

#### Memory Errors

**Example:**
```
Failed to chunk documents: Out of memory
Details: The documents are too large to process. Try:
  - Processing fewer documents at once
  - Reducing the chunk_size parameter
  - Increasing available system memory
```

**Solution:**
- Process documents in smaller batches
- Increase chunk_size to reduce chunk count:
  ```bash
  python ingest.py --file large_doc.pdf --chunk-size 2000
  ```
- Close other applications to free memory
- Process documents individually instead of entire directories

---

### 7. Query Errors

**Description:** Issues during query processing.

**Example:**
```
Failed to process query
Query: What is the gameplay loop...
Reason: Network timeout
```

**Solution:**
- Check your internet connection
- Verify OpenAI API status
- Try a shorter or simpler query
- Wait a moment and try again

---

## Error Recovery

### Automatic Recovery

The system automatically handles these scenarios:

1. **Partial File Loading Failures**: If some files in a directory fail to load, others are still processed
2. **Transient Network Issues**: Network timeouts return error messages but don't crash the system
3. **Individual Document Failures**: When loading multiple documents, failures are logged but don't stop processing

### Manual Recovery

For persistent errors:

1. **Check Logs**: Review console output for detailed error messages
2. **Verify Configuration**: Ensure all settings are correct
3. **Test Individually**: Try loading problematic files one at a time
4. **Reset Database**: Delete and recreate if corrupted:
   ```bash
   rm -rf ./chroma_db
   python ingest.py --docs-dir ./docs
   ```

### Retry Strategies

For transient failures:

1. **API Rate Limits**: Wait 60 seconds, then retry
2. **Network Timeouts**: Wait 10-30 seconds, then retry
3. **File Access Errors**: Ensure file isn't open in another program, then retry

---

## Common Error Patterns and Solutions

### Pattern: "Everything was working, now it's not"

**Checklist:**
1. Check API key is still valid
2. Verify OpenAI API status
3. Check internet connection
4. Verify database wasn't deleted or moved
5. Ensure no configuration files were modified

### Pattern: "Some files load, others don't"

**Checklist:**
1. Check file encodings (should be UTF-8)
2. Verify file permissions
3. Check for corrupted files
4. Ensure file extensions match content

### Pattern: "Slow or timing out"

**Checklist:**
1. Check internet connection speed
2. Verify OpenAI API status
3. Reduce batch sizes
4. Increase chunk size to reduce API calls

---

## For Developers

### Using Custom Exceptions

The system provides custom exception classes in `exceptions.py`:

```python
from exceptions import DocumentLoadError, APIKeyError, NetworkError

# Raise specific errors
raise DocumentLoadError("file.txt", "File is corrupted")

# Catch specific errors
try:
    load_document()
except DocumentLoadError as e:
    console.print(f"[red]{e.message}[/red]")
    console.print(f"[yellow]{e.details}[/yellow]")
```

### Exception Hierarchy

```
AdastreaDirectorError (base)
├── ConfigurationError
├── APIKeyError
├── DocumentLoadError
│   ├── UnsupportedFileTypeError
│   ├── FileEncodingError
│   └── CorruptedFileError
├── DatabaseError
│   └── EmptyDatabaseError
├── NetworkError
│   └── RateLimitError
├── ChunkingError
├── QueryError
└── ValidationError
```

### Adding New Error Types

1. Define the exception in `exceptions.py`:
   ```python
   class NewError(AdastreaDirectorError):
       """Description of the error."""
       def __init__(self, message: str, details: str = None):
           super().__init__(message, details)
   ```

2. Import and use in your code:
   ```python
   from exceptions import NewError
   
   raise NewError("Something went wrong", "Additional details")
   ```

3. Document the error in this file

### Error Handling Best Practices

1. **Catch Specific Exceptions**: Don't use bare `except:` clauses
2. **Provide Context**: Include relevant information in error messages
3. **Log Appropriately**: Use appropriate log levels (error, warning, info)
4. **Don't Silence Errors**: Always handle or propagate exceptions
5. **User-Friendly Messages**: Explain what happened and how to fix it

### Testing Error Handling

All error conditions should have corresponding tests in `tests/test_error_handling.py`:

```python
def test_missing_file_error(agent):
    """Test handling of missing files."""
    result = agent.load_single_file("/nonexistent/file.txt")
    assert result == []
```

Run error handling tests:
```bash
pytest tests/test_error_handling.py -v
```

---

## Supported File Types and Common Issues

### Markdown (.md)
- **Loader**: UnstructuredMarkdownLoader
- **Common Issues**: Special characters, invalid UTF-8
- **Dependencies**: markdown, beautifulsoup4

### Text (.txt)
- **Loader**: TextLoader  
- **Common Issues**: Encoding problems, null bytes
- **Dependencies**: None (built-in)

### Python (.py)
- **Loader**: PythonLoader
- **Common Issues**: Syntax errors don't prevent loading
- **Dependencies**: None (built-in)

### PDF (.pdf)
- **Loader**: PyPDFLoader
- **Common Issues**: Corrupted PDFs, password-protected, scanned images
- **Dependencies**: pypdf
- **Note**: Scanned PDFs require OCR (not currently supported)

### Word (.docx)
- **Loader**: Docx2txtLoader
- **Common Issues**: Corrupted files, old .doc format, password-protected
- **Dependencies**: python-docx
- **Note**: Only .docx is supported, not old .doc format

---

## Getting Help

If you encounter an error not covered in this document:

1. Check the full error message and stack trace
2. Review the [GitHub Issues](https://github.com/Mittenzx/Adastrea-Director/issues)
3. Search existing issues for similar problems
4. Create a new issue with:
   - Full error message and stack trace
   - Steps to reproduce
   - System information (OS, Python version)
   - File types being processed

---

**Last Updated**: 2025-11-10
