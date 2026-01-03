# RAG Ingestion Simulation Tests

## Overview

The RAG ingestion simulation test suite (`tests/test_simulate_rag_ingestion.py`) provides comprehensive testing of the RAG (Retrieval-Augmented Generation) document ingestion functionality without requiring external API keys or live databases.

## Purpose

These tests simulate the complete RAG ingestion workflow to verify that:
1. Document ingestion works correctly
2. Incremental ingestion detects changes properly
3. Progress tracking functions correctly
4. Hash-based change detection works
5. Different file types are handled correctly
6. Error handling is robust

## Test Coverage

### 22 Test Cases Across Multiple Categories:

#### 1. Progress Writer Tests (2 tests)
- `test_progress_writer_basic` - Verifies progress updates are written correctly
- `test_progress_writer_multiple_updates` - Tests that multiple updates overwrite properly

#### 2. File Hash Tests (2 tests)
- `test_file_hash_calculation` - Validates consistent hash calculation
- `test_file_hash_changes_with_content` - Ensures hash changes when file content changes

#### 3. File Discovery Tests (1 test)
- `test_get_file_list` - Verifies supported file types are found

#### 4. File Loading Tests (2 tests)
- `test_load_single_file_markdown` - Tests loading markdown files
- `test_load_single_file_python` - Tests loading Python files

#### 5. Metadata Tests (1 test)
- `test_metadata_enrichment` - Validates metadata enrichment with hash and file info

#### 6. Chunking Tests (2 tests)
- `test_chunk_documents` - Tests document chunking
- `test_language_detection` - Validates programming language detection

#### 7. Full Workflow Tests (1 test)
- `test_ingestion_simulation_full_workflow` - End-to-end ingestion simulation

#### 8. Incremental Ingestion Tests (3 tests)
- `test_incremental_ingestion_skip_unchanged` - Tests skipping unchanged files
- `test_incremental_ingestion_update_changed` - Tests updating changed files
- `test_force_reingest` - Tests force re-ingestion flag

#### 9. Error Handling Tests (2 tests)
- `test_error_handling_invalid_file` - Tests handling of invalid files
- `test_error_handling_during_ingestion` - Tests error tracking during ingestion

#### 10. Integration Tests (1 test)
- `test_main_ingest_documents_function` - Tests the main ingest function

#### 11. Progress Utils Tests (3 tests)
- `test_write_progress_file_function` - Tests progress file writing
- `test_write_progress_file_creates_directories` - Tests directory creation
- `test_write_progress_file_clamps_percent` - Tests percent clamping to 0-100

#### 12. Module Import Tests (2 tests)
- `test_rag_ingestion_module_imports` - Validates module can be imported
- `test_progress_utils_module_imports` - Validates progress utils can be imported

## Running the Tests

### Run All Simulation Tests
```bash
pytest tests/test_simulate_rag_ingestion.py -v
```

### Run Specific Test Category
```bash
# Progress writer tests
pytest tests/test_simulate_rag_ingestion.py::TestRAGIngestionSimulation::test_progress_writer_basic -v

# Full workflow test
pytest tests/test_simulate_rag_ingestion.py::TestRAGIngestionSimulation::test_ingestion_simulation_full_workflow -v
```

### Run with Detailed Output
```bash
pytest tests/test_simulate_rag_ingestion.py -v -s
```

## Key Features

### Mock Embeddings
The tests use mock embeddings to avoid requiring API keys:
```python
@pytest.fixture
def mock_embeddings(self):
    """Create mock embeddings to avoid requiring API keys."""
    mock_embed = Mock()
    mock_embed.embed_documents.return_value = [[0.1] * 384] * 10
    mock_embed.embed_query.return_value = [0.1] * 384
    return mock_embed
```

### Temporary Test Data
Tests create temporary directories with sample documents:
- Markdown files (`.md`)
- Python files (`.py`)
- Text files (`.txt`)
- C++ files (`.cpp`)

### Realistic Simulation
The tests simulate real-world scenarios including:
- First-time ingestion (all new files)
- Incremental ingestion (some files unchanged)
- File updates (content changed)
- Error conditions
- Progress tracking

## Benefits

1. **No External Dependencies**: Tests run without API keys or live databases
2. **Fast Execution**: Complete test suite runs in ~4 seconds
3. **Comprehensive Coverage**: 22 tests covering all major functionality
4. **CI/CD Ready**: Can run in automated pipelines
5. **Documentation**: Tests serve as usage examples

## Test Structure

Each test follows best practices:
- Clear docstrings explaining what is being tested
- Proper setup and teardown with fixtures
- Isolated test data (temporary directories)
- Mocked external dependencies
- Assertions that verify expected behavior

## Integration with CI/CD

These tests are suitable for continuous integration:
- No manual setup required
- No API keys needed
- Fast execution time
- Clear pass/fail indicators
- Compatible with pytest-cov for coverage reports

## Maintenance

When updating the RAG ingestion functionality:
1. Run these tests to ensure backward compatibility
2. Add new tests for new features
3. Update existing tests if behavior changes
4. Maintain high test coverage (currently 100% of simulation scenarios)

## Related Documentation

- [Plugin RAG Integration](../../Plugins/AdastreaDirector/Documentation/features/RAG_INTEGRATION.md)
- [Main Ingestion Module](../../Plugins/AdastreaDirector/Python/rag_ingestion.py)
- [Progress Utils](../../Plugins/AdastreaDirector/Python/progress_utils.py)

## Troubleshooting

### ImportError: No module named 'pytest'
```bash
pip install pytest pytest-mock
```

### ImportError: No module named 'dotenv'
```bash
pip install -r requirements.txt
```

### Test failures after code changes
Review the specific test that failed and ensure the RAG ingestion code still follows the expected behavior pattern.

## Future Enhancements

Potential additions to the test suite:
- Performance benchmarks for large document sets
- Memory usage profiling
- Concurrent ingestion testing
- Database corruption recovery tests
- Network failure simulation
