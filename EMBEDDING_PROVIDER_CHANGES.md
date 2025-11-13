# Embedding Provider Changes

## Overview

This document describes the changes made to support multiple embedding providers, with HuggingFace embeddings as the default instead of requiring OpenAI API keys.

## What Changed

### Before
- **Required** OPENAI_API_KEY environment variable
- Hard dependency on OpenAI API for embeddings
- Would exit with error if API key was missing

### After
- **Default**: Uses HuggingFace embeddings locally (no API key required)
- **Optional**: Can still use OpenAI by setting environment variable
- Falls back gracefully with helpful error messages

## Configuration

### Using HuggingFace (Default)

No configuration needed! Just run the ingestion:

```bash
python ingest.py --docs-dir /path/to/docs
```

To customize the model:

```bash
export HUGGINGFACE_MODEL_NAME=sentence-transformers/all-mpnet-base-v2
python ingest.py --docs-dir /path/to/docs
```

### Using OpenAI

**For complete OpenAI setup instructions, see [OpenAI Embeddings Setup Guide](docs/guides/OPENAI_EMBEDDINGS_SETUP.md).**

Quick setup:

```bash
export EMBEDDING_PROVIDER=openai
export OPENAI_API_KEY=your-api-key-here
python ingest.py --docs-dir /path/to/docs
```

### Using Custom Embeddings

You can also pass custom embeddings programmatically:

```python
from ingest import DocumentIngestionAgent
from langchain_openai import OpenAIEmbeddings

custom_embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
agent = DocumentIngestionAgent(embeddings=custom_embeddings)
```

## Environment Variables

### EMBEDDING_PROVIDER
- **Options**: `hf`, `huggingface`, or `openai`
- **Default**: `hf` (HuggingFace)
- **Description**: Selects which embedding provider to use

### HUGGINGFACE_MODEL_NAME
- **Default**: `all-MiniLM-L6-v2`
- **Description**: Which HuggingFace model to use for embeddings
- **Popular Options**:
  - `all-MiniLM-L6-v2` - Fast, lightweight, good quality (default)
  - `sentence-transformers/all-mpnet-base-v2` - Slower but better quality
  - `sentence-transformers/all-MiniLM-L12-v2` - Balance of speed and quality

### OPENAI_API_KEY
- **Required**: Only when `EMBEDDING_PROVIDER=openai`
- **Description**: Your OpenAI API key for embeddings

## Installation

### For HuggingFace (Default)

The required `sentence-transformers` package is already in `requirements.txt`:

```bash
pip install -r requirements.txt
```

If you get an error about missing `sentence-transformers`:

```bash
pip install sentence-transformers
```

### For OpenAI

The required packages are already in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Benefits

1. **No API Keys Required**: Can run completely offline with local embeddings
2. **Free to Use**: No API costs for embeddings
3. **Privacy**: Data doesn't leave your machine
4. **Backward Compatible**: Existing code with OpenAI still works
5. **Flexible**: Easy to switch between providers or use custom embeddings

## Migration Guide

### Existing Users

If you're currently using OpenAI embeddings and want to continue:

```bash
# Add to your .env file or environment
export EMBEDDING_PROVIDER=openai
export OPENAI_API_KEY=your-existing-key
```

Your existing workflow will continue to work without changes.

### New Users

Just run the ingestion commands - no API key setup required!

```bash
python ingest.py --docs-dir docs/
```

## Error Messages

The system provides helpful error messages to guide you:

### When HuggingFace packages are missing:

```
Error: HuggingFace embeddings require 'sentence-transformers' package
Install it with: pip install sentence-transformers
Or to use OpenAI instead, set: EMBEDDING_PROVIDER=openai
```

### When OpenAI is selected but key is missing:

```
Error initializing OpenAI embeddings: API key not found
Make sure OPENAI_API_KEY is set in your environment
```

## Testing

Comprehensive tests verify:
- Default HuggingFace embeddings work
- Custom HuggingFace models work
- OpenAI provider selection works
- Custom embeddings parameter works
- Error handling works correctly
- Backward compatibility is maintained

Run tests:

```bash
pytest tests/test_embedding_providers.py -v
```

## Files Modified

1. **ingest.py** - Added embedding provider selection logic
2. **ingest_game_repo.py** - Updated documentation
3. **.env.example** - Added new environment variables
4. **tests/test_embedding_providers.py** - New comprehensive test suite
5. **tests/test_ingestion_improvements.py** - Updated to use new default

## Performance

HuggingFace embeddings run locally and:
- First run: Downloads model (~90MB for all-MiniLM-L6-v2)
- Subsequent runs: Uses cached model
- No network calls after initial download
- Generally faster than API calls for small batches
- May be slower than OpenAI for very large batches

## Support

If you encounter issues:

1. Check that `sentence-transformers` is installed
2. Verify environment variables are set correctly
3. Check error messages for specific guidance
4. Ensure you have internet access for first-time model download
5. After initial download, can work completely offline

## Future Enhancements

Possible future improvements:
- Support for more embedding providers (Cohere, Anthropic, etc.)
- Automatic provider selection based on available credentials
- Performance benchmarking between providers
- Model recommendation based on use case
