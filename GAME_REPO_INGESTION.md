# Game Repository Ingestion Guide

This guide explains how to ingest documents from the Mittenzx/Adastrea game repository into the Adastrea Director knowledge base, and how to set up automatic updates.

## Overview

Adastrea Director is designed to help build the Mittenzx/Adastrea game. To provide the most relevant assistance, it needs to understand the game's codebase, documentation, and design documents. This guide shows you how to:

1. Ingest documents from the game repository
2. Test the ingestion process
3. Set up automatic updates
4. Troubleshoot common issues

## Quick Start

### Prerequisites

1. **OpenAI API Key**: Set your API key
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. **GitHub Token** (for private repositories): Create a personal access token with `repo` scope
   ```bash
   export GITHUB_TOKEN="ghp_your_token_here"
   ```
   
   To create a token:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Click "Generate new token" (classic)
   - Give it a name like "Adastrea Director Ingestion"
   - Check the `repo` scope
   - Generate and copy the token

### Basic Usage

Ingest the game repository with one command:

```bash
python ingest_game_repo.py
```

This will:
1. Clone the Mittenzx/Adastrea repository
2. Load all relevant documents (docs, source code, config files)
3. Chunk and embed the documents
4. Store them in a vector database
5. Track the ingestion for future updates

## Advanced Usage

### Check for Updates

Before ingesting, check if there are new commits:

```bash
python ingest_game_repo.py --check-updates
```

Exit codes:
- `0`: No updates available (up to date)
- `1`: Updates available

### Force Re-ingestion

To re-ingest even if there are no updates:

```bash
python ingest_game_repo.py --force
```

### View Statistics

See information about the last ingestion:

```bash
python ingest_game_repo.py --stats
```

Output:
```
Ingestion Statistics:
  Last commit: abc123def456...
  Last ingestion: 2025-11-11T10:30:00
  Documents: 150
  Chunks: 450
```

### Custom Configuration

Specify custom directories and collection names:

```bash
python ingest_game_repo.py \
  --collection-name my_custom_collection \
  --persist-dir ./my_custom_db \
  --clone-dir /tmp/my_game_clone
```

## Testing

### Running Tests

The test suite includes comprehensive tests for game repository ingestion:

```bash
# Run all game repo ingestion tests
python -m pytest tests/test_game_repo_ingestion.py -v

# Run only unit tests (uses mock data)
python -m pytest tests/test_game_repo_ingestion.py -v -m unit

# Run integration tests (requires credentials)
python -m pytest tests/test_game_repo_ingestion.py -v -m integration
```

### Test Categories

1. **Unit Tests** (no credentials required)
   - Use mock game repository structure
   - Test document loading and chunking
   - Test metadata enrichment
   - Fast and safe for CI/CD

2. **Integration Tests** (requires credentials)
   - Clone and ingest real repository
   - Validate end-to-end flow
   - Marked with `@pytest.mark.requires_api_key`

### Mock Testing

The test suite includes a mock game repository structure that simulates a typical Unreal Engine game project:

```
mock_adastrea/
├── README.md
├── docs/
│   ├── GameDesignDocument.md
│   ├── TechnicalSpecification.md
│   └── Characters.md
├── Source/Adastrea/
│   ├── PlayerCharacter.h
│   └── PlayerCharacter.cpp
└── Content/Blueprints/
    └── README.md
```

This allows testing without access to the actual repository.

## Automatic Updates

### Setup with Cron (Linux/Mac)

Update the knowledge base daily at 3 AM:

```bash
# Edit crontab
crontab -e

# Add this line:
0 3 * * * cd /path/to/Adastrea-Director && /usr/bin/python ingest_game_repo.py >> logs/ingestion.log 2>&1
```

### Setup with Task Scheduler (Windows)

1. Open Task Scheduler
2. Create a new task
3. Set trigger: Daily at 3:00 AM
4. Set action: 
   - Program: `python`
   - Arguments: `ingest_game_repo.py`
   - Start in: `C:\path\to\Adastrea-Director`

### Setup with GitHub Actions

Create `.github/workflows/ingest-game-repo.yml`:

```yaml
name: Update Game Repository Knowledge Base

on:
  schedule:
    # Run daily at 3 AM UTC
    - cron: '0 3 * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  ingest:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout Adastrea-Director
        uses: actions/checkout@v3
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          
      - name: Check for updates
        id: check
        run: |
          python ingest_game_repo.py --check-updates
        env:
          GITHUB_TOKEN: ${{ secrets.GAME_REPO_TOKEN }}
        continue-on-error: true
        
      - name: Ingest if updates available
        if: steps.check.outcome == 'failure'
        run: |
          python ingest_game_repo.py
        env:
          GITHUB_TOKEN: ${{ secrets.GAME_REPO_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          
      - name: Upload database artifact
        if: success()
        uses: actions/upload-artifact@v3
        with:
          name: game-knowledge-base
          path: chroma_db_adastrea/
```

### Pre-commit Hook

Update knowledge base before committing (useful for developers):

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Update game repository knowledge base before committing

cd "$(git rev-parse --show-toplevel)"

echo "Checking for game repository updates..."
python ingest_game_repo.py --check-updates

if [ $? -eq 1 ]; then
    echo "Updates available. Ingesting..."
    python ingest_game_repo.py
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Directory Structure

The ingestion script looks for these directories in the game repository:

- `docs/` or `Documentation/` - Game design documents, technical specs
- `Source/` - C++ source code
- `Content/` - Blueprint documentation, asset info
- `Config/` - Configuration files

You can customize which directories to ingest by editing `INGEST_DIRS` in `ingest_game_repo.py`.

## Troubleshooting

### Authentication Failed

**Problem:** `fatal: Authentication failed`

**Solutions:**
1. Verify your GitHub token is valid
2. Check the token has `repo` scope
3. For private repos, ensure you have access
4. Token might be expired - generate a new one

### No Documents Found

**Problem:** `No documents found to ingest`

**Solutions:**
1. Check that the repository structure matches expected directories
2. Verify the repository cloned successfully
3. Check that target directories exist in the repository
4. Look at console output for which directories were found/skipped

### Rate Limiting

**Problem:** `Rate limit exceeded` or `429 Too Many Requests`

**Solutions:**
1. Use smaller batch sizes: Edit `batch_size` in `ingest_game_repo.py`
2. Increase delay between batches: Edit `delay_between_batches`
3. Wait a few minutes before retrying
4. Check OpenAI API usage limits

### Out of Memory

**Problem:** Process crashes with memory errors

**Solutions:**
1. Ingest directories one at a time
2. Reduce `chunk_size` in agent initialization
3. Process fewer files per batch
4. Increase system memory

## Integration with GUI

The GUI application (`gui_director.py`) has built-in support for ingesting GitHub repositories:

1. Click the "🔗 Ingest Repo" button
2. Enter the repository URL: `https://github.com/Mittenzx/Adastrea`
3. Click "Clone & Ingest"

The GUI will:
- Clone the repository to `/tmp/`
- Ingest all documents
- Update the knowledge base
- Show progress in the conversation area

## Best Practices

### 1. Regular Updates

Set up automated ingestion to run daily or after each commit to the game repository. This keeps the AI assistant's knowledge current.

### 2. Selective Ingestion

Only ingest directories that contain useful information:
- ✅ Documentation
- ✅ Source code
- ✅ Configuration files
- ❌ Binary assets
- ❌ Build artifacts
- ❌ Temporary files

### 3. Version Tracking

The ingestion script automatically tracks:
- Last ingested commit hash
- Ingestion timestamp
- Document and chunk counts

This enables incremental updates and prevents redundant ingestion.

### 4. Collection Management

Use separate collections for different purposes:
- `adastrea_game_docs` - Game repository
- `adastrea_docs` - Adastrea Director documentation
- `design_docs` - Design-specific documents

### 5. Backup

Periodically backup your vector database:

```bash
# Backup
tar -czf chroma_db_backup_$(date +%Y%m%d).tar.gz chroma_db_adastrea/

# Restore
tar -xzf chroma_db_backup_20251111.tar.gz
```

## File Reference

### `ingest_game_repo.py`

Main script for ingesting the game repository.

**Key Features:**
- Automatic cloning with GitHub token support
- Selective directory ingestion
- Update tracking
- Progress reporting
- Error handling

### `tests/test_game_repo_ingestion.py`

Comprehensive test suite.

**Test Categories:**
- Mock repository testing (no credentials)
- Real repository testing (with credentials)
- Configuration parsing
- Auto-update detection
- Metadata enrichment

### `.adastrea_ingestion_tracking.json`

Tracking file (auto-generated).

**Contains:**
```json
{
  "last_commit": "abc123...",
  "last_ingestion_time": "2025-11-11T10:30:00",
  "document_count": 150,
  "chunk_count": 450
}
```

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes | OpenAI API authentication |
| `GITHUB_TOKEN` | No* | GitHub authentication for private repos |

\* Required only if the Mittenzx/Adastrea repository is private

## Command Reference

```bash
# Basic ingestion
python ingest_game_repo.py

# Check for updates only
python ingest_game_repo.py --check-updates

# Force re-ingestion
python ingest_game_repo.py --force

# Show statistics
python ingest_game_repo.py --stats

# Custom configuration
python ingest_game_repo.py \
  --token ghp_xxx \
  --collection-name custom_name \
  --persist-dir ./custom_dir \
  --clone-dir /tmp/custom_clone

# Run tests
python -m pytest tests/test_game_repo_ingestion.py -v

# Manual ingestion via test helper
python tests/test_game_repo_ingestion.py --ingest
```

## Support

If you encounter issues:

1. Check this troubleshooting guide
2. Review error messages carefully
3. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for general issues
4. Open an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Python version)

## Future Enhancements

Planned improvements:

- [ ] Incremental ingestion (only new/changed files)
- [ ] Web dashboard for monitoring ingestion status
- [ ] Automatic rollback on failed ingestion
- [ ] Multi-repository support
- [ ] Integration with GitHub Desktop
- [ ] Webhook support for real-time updates

## Contributing

To improve game repository ingestion:

1. Fork the repository
2. Add tests for new features
3. Update this documentation
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

---

**Last Updated:** 2025-11-11  
**Version:** 1.0
