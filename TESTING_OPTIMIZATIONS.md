# Testing Query System Optimizations

This document outlines how to test the query system optimizations implemented in this PR.

## Prerequisites

Before testing, ensure you have:
1. Python 3.9+ installed
2. All dependencies installed: `pip install -r requirements.txt`
3. OpenAI API key configured: `export OPENAI_API_KEY="your-key"`
4. Test documents ingested into the database

## Syntax and Logic Validation

The core optimization logic has been validated independently:

### ✓ Query Hashing
- Case-insensitive query matching
- Whitespace trimming
- Consistent hash generation

### ✓ Cache LRU Eviction
- Maximum size enforcement (50 entries)
- Oldest entry eviction when full
- Proper cache hit/miss behavior

### ✓ Search Configuration
- MMR search with fetch_k parameter
- Similarity search without fetch_k
- Configurable retrieval_k parameter

### ✓ Document Type Detection
- Python files detected for code-aware chunking
- Text/Markdown files use prose-optimized chunking
- Correct splitting based on file extension

## Manual Testing

### 1. Test Default Configuration (MMR)

```bash
# Ingest some test documents
python ingest.py --docs-dir ./test_docs

# Run with default optimized settings
python main.py
```

**Expected behavior:**
- System starts with MMR search enabled
- Shows "Response time: X.XXs" for each query
- Displays "(cached)" indicator for repeated queries

**Test queries:**
```
What is the main gameplay loop?
# Note the response time, then ask again:
What is the main gameplay loop?
# Should show "(cached)" and much faster response
```

### 2. Test Similarity Search

```bash
python main.py --search-type similarity
```

**Expected behavior:**
- Faster retrieval but potentially less diverse results
- Still shows caching and performance metrics

### 3. Test Custom Retrieval Parameters

```bash
# More documents for comprehensive answers
python main.py --retrieval-k 10 --fetch-k 30

# Fewer documents for faster responses
python main.py --retrieval-k 4
```

**Expected behavior:**
- Higher k values = more source documents
- Response quality should scale with k value

### 4. Test Code vs Text Document Chunking

Ingest a mix of Python files and Markdown documents:

```bash
python ingest.py --docs-dir ./test_docs_mixed
python main.py
```

**Test with code query:**
```
Show me the implementation of the QueryAgent class
```

**Test with text query:**
```
What are the main features described in the documentation?
```

**Expected behavior:**
- Code queries should return well-structured code snippets
- Text queries should return coherent paragraphs
- Both should preserve context appropriately

### 5. Test Performance Metrics

```bash
python main.py
```

**Test queries:**
```
# First query - should take ~1-3 seconds
What is the main gameplay loop?

# Cached query - should take < 0.01 seconds
What is the main gameplay loop?

# Different query - should take ~1-3 seconds again
What are the system requirements?
```

**Expected behavior:**
- First query: Normal response time displayed
- Cached query: Very fast response with "(cached)" indicator
- All queries: Response time always displayed

## Integration Testing

### Test with Various Document Types

1. **Markdown documents:**
   ```bash
   python ingest.py --file README.md
   python main.py
   # Ask: "What is this project about?"
   ```

2. **Python code:**
   ```bash
   python ingest.py --file main.py
   python main.py
   # Ask: "Explain the QueryAgent class"
   ```

3. **Mixed collection:**
   ```bash
   python ingest.py --docs-dir .
   python main.py
   # Ask various questions about code and documentation
   ```

### Test Cache Behavior

```python
# Test script to verify cache
python main.py

# In the CLI:
What is X?          # First query
What is X?          # Should be cached
what is x?          # Should be cached (case insensitive)
  What is X?        # Should be cached (whitespace trimmed)
What is Y?          # Not cached (different query)
```

## Performance Benchmarking

Create a benchmark script to measure improvements:

```python
#!/usr/bin/env python3
import time
import subprocess

queries = [
    "What is the main gameplay loop?",
    "Describe the player character",
    "What are the system requirements?",
]

# Test each query twice (first and cached)
for query in queries:
    # First query
    start = time.time()
    # Run query...
    first_time = time.time() - start
    
    # Cached query
    start = time.time()
    # Run same query...
    cached_time = time.time() - start
    
    print(f"Query: {query}")
    print(f"  First: {first_time:.2f}s")
    print(f"  Cached: {cached_time:.2f}s")
    print(f"  Speedup: {first_time/cached_time:.1f}x")
```

## Expected Performance Results

### Response Time
- **First query**: 1.0-3.0 seconds (API dependent)
- **Cached query**: < 0.01 seconds (100-300x faster)
- **MMR vs Similarity**: Similar (< 5% difference)

### Relevance
- **MMR search**: More diverse results, better for broad queries
- **Similarity search**: More similar results, better for specific queries
- **Code chunking**: Better preservation of function/class boundaries

### Resource Usage
- **Memory**: +1-2 MB for cache (negligible)
- **API calls**: Same for new queries, 0 for cached
- **Token usage**: +20% for k=6 vs k=5 (better value)

## Troubleshooting

### Tests fail to import modules
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.9+)

### Cache doesn't work
- Cache is in-memory only (clears on restart)
- Query must be identical (case-insensitive, whitespace-trimmed)
- Check for "(cached)" indicator in output

### Poor performance
- Check network connection to OpenAI API
- Try `--search-type similarity` for faster retrieval
- Reduce `--retrieval-k` for fewer documents

### Poor relevance
- Increase `--retrieval-k` for more context
- Ensure `--search-type mmr` for diversity
- Verify documents are properly ingested

## Automated Testing

The test suite has been updated to cover new features:

```bash
# Run all tests
pytest tests/test_query_system.py -v

# Run specific test classes
pytest tests/test_query_system.py::TestQueryOptimization -v
```

### Test Coverage

- ✓ Default initialization with optimization parameters
- ✓ Custom search configuration
- ✓ MMR retriever configuration
- ✓ Query caching behavior
- ✓ Cache disable functionality
- ✓ Performance timing
- ✓ Document type detection
- ✓ Search kwargs configuration

## Validation Checklist

Before considering the optimizations complete, verify:

- [ ] All optimization parameters are configurable via CLI
- [ ] MMR search works correctly
- [ ] Query caching improves performance
- [ ] Performance metrics are displayed
- [ ] Code-aware chunking preserves structure
- [ ] Backward compatibility maintained (default behavior improved)
- [ ] Documentation is comprehensive
- [ ] Tests pass for new features
- [ ] No regressions in existing functionality

## Known Limitations

1. **Cache persistence**: Cache is in-memory only (cleared on restart)
2. **Semantic similarity**: Cache requires exact query match (after normalization)
3. **Cache size**: Fixed at 50 entries (not configurable)
4. **Document types**: Only Python code has special handling

These limitations are intentional to keep changes minimal and focused on high-impact optimizations. Future enhancements can address these if needed.

---

**Last Updated**: 2025-11-10
