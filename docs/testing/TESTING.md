# Testing Guide for Adastrea Director

This document provides information about the test suite for the Adastrea Director project.

## Overview

The test suite provides comprehensive coverage for the document loading, chunking, and query systems. All tests are located in the `tests/` directory and use `pytest` as the testing framework.

## Test Structure

### Test Files

- **`test_document_loaders.py`**: Tests for document ingestion functionality
  - Document loader initialization
  - Loading from directories and single files
  - PDF, DOCX, Markdown, Text, and Python file support
  - Error handling for missing files and invalid inputs
  - Database statistics retrieval

- **`test_chunking_strategies.py`**: Tests for document chunking
  - Chunking strategies and configurations
  - Chunk size and overlap settings
  - Separator handling
  - Metadata preservation
  - Edge cases (empty documents, special characters, etc.)

- **`test_query_system.py`**: Tests for the query agent
  - QueryAgent initialization
  - Query processing
  - Database information retrieval
  - Memory and conversation management
  - Query optimization features

- **`test_error_handling.py`**: Tests for error handling mechanisms
  - Missing API keys
  - Invalid file paths
  - Network errors
  - Database errors
  - Invalid configurations
  - Document loading errors

- **`test_game_repo_ingestion.py`**: Tests for game repository ingestion (NEW!)
  - Mock game repository structure
  - Document ingestion from game projects
  - C++ and Blueprint file handling
  - Configuration parsing
  - Auto-update detection
  - Integration with real Mittenzx/Adastrea repo (when credentials provided)

## Running Tests

### Run All Tests

```bash
pytest tests/
```

### Run Tests with Verbose Output

```bash
pytest tests/ -v
```

### Run Tests with Coverage Report

```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
```

This generates:
- HTML coverage report in `htmlcov/` directory
- Terminal coverage summary with missing lines

### Run Specific Test File

```bash
pytest tests/test_document_loaders.py
```

### Run Specific Test Class

```bash
pytest tests/test_document_loaders.py::TestDocumentIngestionAgentInitialization
```

### Run Specific Test Method

```bash
pytest tests/test_document_loaders.py::TestDocumentIngestionAgentInitialization::test_default_initialization
```

### Run Game Repository Ingestion Tests

```bash
# Run all game repo tests (unit tests with mock data)
pytest tests/test_game_repo_ingestion.py -v -m unit

# Run with real repository (requires GITHUB_TOKEN, uses HuggingFace embeddings by default)
# Optional: Set EMBEDDING_PROVIDER=openai and OPENAI_API_KEY to use OpenAI embeddings
pytest tests/test_game_repo_ingestion.py -v -m integration --requires-api-key

# View game repo test categories
pytest tests/test_game_repo_ingestion.py -v --collect-only
```

## Test Coverage

Current test coverage metrics:

- **Document Loaders (ingest.py)**: 64% coverage
  - Core functionality is well tested
  - CLI and main functions are excluded (tested via integration)

- **Query System (main.py)**: 48% coverage
  - Core query processing is well tested
  - CLI interface is excluded (tested via integration)

- **Test Files**: 98-99% coverage
  - Comprehensive test coverage for all test modules

### Coverage Goals

- Maintain >70% overall coverage for core modules
- 100% coverage for critical paths (loading, chunking, querying)
- Test all error handling paths

## Test Configuration

Tests are configured via `pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### Coverage Configuration

Coverage exclusions are defined in `pytest.ini`:
- GUI components (`gui_director.py`)
- Setup and validation scripts
- Test files themselves
- External dependencies

## Test Best Practices

### 1. Test Isolation

Each test is independent and doesn't rely on other tests:

```python
@pytest.fixture
def agent(self):
    """Create a fresh agent for each test."""
    with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
        mock_embeddings.return_value = Mock()
        return DocumentIngestionAgent()
```

### 2. Mocking External Dependencies

All external dependencies (OpenAI API, file system, database) are mocked:

```python
@patch('ingest.OpenAIEmbeddings')
def test_initialization(self, mock_embeddings):
    mock_embeddings.return_value = Mock()
    agent = DocumentIngestionAgent()
    assert agent is not None
```

### 3. Testing Edge Cases

Tests cover edge cases and error conditions:

```python
def test_empty_document(self, agent):
    """Test chunking an empty document."""
    mock_doc = Mock()
    mock_doc.page_content = ""
    chunks = agent.chunk_documents([mock_doc])
    assert isinstance(chunks, list)
```

### 4. Clear Test Names

Test names clearly describe what is being tested:

```python
def test_load_from_nonexistent_directory(self, agent):
    """Test loading from a directory that doesn't exist."""
    documents = agent.load_documents_from_directory("/nonexistent/path")
    assert documents == []
```

## Adding New Tests

When adding new functionality:

1. **Create corresponding test file** in `tests/` directory
2. **Follow naming convention**: `test_<feature>.py`
3. **Organize tests in classes** by functionality
4. **Use fixtures** for common setup
5. **Mock external dependencies** to ensure test isolation
6. **Test both success and failure paths**
7. **Run tests locally** before committing

### Example Test Template

```python
#!/usr/bin/env python3
"""
Unit tests for <feature> in the Adastrea Director.

Tests cover:
- <functionality 1>
- <functionality 2>
- Error handling
"""

import os
import sys
from unittest.mock import Mock, patch
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module import FeatureClass


class TestFeatureInitialization:
    """Test initialization of Feature."""

    @pytest.fixture
    def feature(self):
        """Create a test feature instance."""
        with patch('module.Dependency') as mock_dep:
            mock_dep.return_value = Mock()
            return FeatureClass()

    def test_default_initialization(self, feature):
        """Test feature initializes with defaults."""
        assert feature.some_attribute == "expected_value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Release builds

### CI Requirements

- All tests must pass
- Coverage must not decrease
- No new linting errors

## Troubleshooting

### Common Issues

#### Import Errors

```python
# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

#### Mock Issues

Ensure all external dependencies are mocked:

```python
@patch('module.ExternalDependency')
def test_feature(self, mock_dep):
    mock_dep.return_value = Mock()
    # test code
```

#### Coverage Not Updating

Clear coverage cache:

```bash
rm -rf .coverage htmlcov/
pytest tests/ --cov=.
```

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-cov plugin](https://pytest-cov.readthedocs.io/)

## Test Metrics Summary

| Test File | Tests | Coverage |
|-----------|-------|----------|
| test_document_loaders.py | 31 | 99% |
| test_chunking_strategies.py | 22 | 98% |
| test_query_system.py | 27 | 99% |
| test_error_handling.py | 25 | 99% |
| **Total** | **105** | **98%** |

## Maintenance

- Review and update tests when adding new features
- Keep tests DRY (Don't Repeat Yourself) using fixtures
- Update documentation when test structure changes
- Monitor coverage trends over time

---

**Last Updated**: 2025-11-10
