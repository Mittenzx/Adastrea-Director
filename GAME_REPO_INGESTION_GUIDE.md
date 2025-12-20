# Adastrea Game Repository Ingestion Guide

This guide explains how to ingest documentation from the Mittenzx/Adastrea game repository into the RAG system for plugin testing.

## Quick Start

### Method 1: Using the Quick Ingestion Script (Recommended)

```bash
./quick_ingest_game.sh
```

This automated script will:
- Check prerequisites (Python, dependencies)
- Clone the game repository
- Ingest documentation
- Create the ChromaDB database

### Method 2: Manual Ingestion

```bash
# Ingest the game repository
python3 ingest_game_repo.py

# Check ingestion statistics
python3 ingest_game_repo.py --stats

# Force re-ingestion (if docs have changed)
python3 ingest_game_repo.py --force
```

## Prerequisites

### Required
1. **Python 3.9-3.12** (Python 3.13+ is not supported yet due to onnxruntime compatibility)
2. **Dependencies installed**: `pip install -r requirements.txt`
3. **Internet access** (required for first-time HuggingFace model download)

### Optional
- **GitHub token** (only needed if the Adastrea repository becomes private)
  - Set via: `export GITHUB_TOKEN=your_token`
  - Or pass as argument: `--token your_token`

## Understanding the Ingestion Process

### What Gets Ingested

The ingestion script processes documents from these directories in the game repository:

```
Mittenzx/Adastrea/
├── Docs/              # Main documentation
├── Documentation/     # Additional documentation (if exists)
├── Source/            # Source code files (.cpp, .h, .cs, .py)
├── Content/           # Content documentation
└── Config/            # Configuration files
```

### Supported File Types

- **Documentation**: `.md`, `.txt`, `.pdf`, `.docx`
- **Code**: `.py`, `.cpp`, `.cc`, `.h`, `.hpp`, `.cs`

### Processing Steps

1. **Clone Repository** → Clones or updates `/tmp/adastrea_game_repo`
2. **Load Documents** → Reads files from specified directories
3. **Chunk Documents** → Splits into 1000-char chunks with 200-char overlap
4. **Generate Embeddings** → Creates vector embeddings using HuggingFace model
5. **Store in ChromaDB** → Saves to `./chroma_db_adastrea`

### Storage Locations

- **Clone Directory**: `/tmp/adastrea_game_repo` (temporary)
- **Database**: `./chroma_db_adastrea` (persistent)
- **Collection Name**: `adastrea_game_docs`
- **Tracking File**: `.adastrea_ingestion_tracking.json` (tracks last commit)

## Embedding Configuration

### Default: HuggingFace Embeddings (Recommended)

**Advantages:**
- ✅ Free and runs locally
- ✅ No API key required
- ✅ Good quality results
- ✅ Works offline after first download

**First-Time Setup:**
```bash
# Internet required for initial model download (~90MB)
# Model is cached in ~/.cache/huggingface/
python3 ingest_game_repo.py
```

**Customize Model:**
```bash
# Use a different HuggingFace model
export HUGGINGFACE_MODEL_NAME=sentence-transformers/all-mpnet-base-v2
python3 ingest_game_repo.py
```

### Alternative: OpenAI Embeddings

**When to use:**
- If HuggingFace download fails (network restrictions)
- If you prefer OpenAI's embeddings

**Setup:**
```bash
export EMBEDDING_PROVIDER=openai
export OPENAI_API_KEY=your-openai-api-key
python3 ingest_game_repo.py
```

**Cost:** ~$0.0004 per 1000 tokens (very cheap for one-time ingestion)

## Incremental Updates

The ingestion system is smart about updates:

### How It Works

1. **Tracks Last Commit**: Stores the last ingested commit hash
2. **Detects Changes**: Compares current commit to last ingested
3. **Skip If Current**: Won't re-ingest if already up-to-date

### Commands

```bash
# Check if updates are available (without ingesting)
python3 ingest_game_repo.py --check-updates

# Ingest only if there are updates
python3 ingest_game_repo.py

# Force re-ingestion (ignore tracking)
python3 ingest_game_repo.py --force

# View ingestion statistics
python3 ingest_game_repo.py --stats
```

### Statistics Output

```
Ingestion Statistics:
  Last commit: abc123def456...
  Last ingestion: 2025-12-20T10:30:45.123456
  Documents: 247
  Chunks: 1823
```

## Plugin Integration

### Configuring the Plugin

After ingestion, configure your Adastrea Director plugin to use the RAG database:

**In the Plugin UI:**
1. Open Adastrea Director panel in Unreal Editor
2. Set database path: `./chroma_db_adastrea` (relative to project root)
3. Set collection name: `adastrea_game_docs`
4. Click "Test Connection" to verify

**Via IPC (if using programmatic access):**
```json
{
  "type": "query",
  "collection": "adastrea_game_docs",
  "persist_dir": "./chroma_db_adastrea",
  "data": "Your question here"
}
```

### Testing the Plugin

1. **Basic Query Test**
   ```
   Query: "What is the Adastrea game about?"
   Expected: Information from game documentation
   ```

2. **Code Query Test**
   ```
   Query: "How do spaceship controls work?"
   Expected: Code snippets and implementation details
   ```

3. **Follow-up Question Test**
   ```
   Query 1: "What are the main features?"
   Query 2: "Tell me more about the first feature"
   Expected: Context-aware response using conversation history
   ```

## Troubleshooting

### Issue: "Cannot reach huggingface.co"

**Problem**: First-time HuggingFace model download requires internet access

**Solutions:**
1. **Connect to internet** and run again (model will be cached for future offline use)
2. **Use OpenAI instead**:
   ```bash
   export EMBEDDING_PROVIDER=openai
   export OPENAI_API_KEY=your-key
   python3 ingest_game_repo.py
   ```
3. **Copy cached model** from another machine:
   ```bash
   # On machine with internet, after successful first run:
   tar -czf hf_cache.tar.gz ~/.cache/huggingface/
   
   # On target machine:
   tar -xzf hf_cache.tar.gz -C ~/
   ```

### Issue: "Failed to clone repository"

**Problem**: Repository is private or network issue

**Solutions:**
1. **Set GitHub token** (if repository is private):
   ```bash
   export GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
   python3 ingest_game_repo.py
   ```
2. **Check internet connection**
3. **Verify repository exists**: https://github.com/Mittenzx/Adastrea

### Issue: "Plugin can't find database"

**Problem**: Path mismatch between ingestion and plugin configuration

**Solutions:**
1. **Use absolute paths** instead of relative
2. **Verify database exists**:
   ```bash
   ls -la ./chroma_db_adastrea
   ```
3. **Check collection name matches**: `adastrea_game_docs`

### Issue: "Ingestion is very slow"

**Problem**: Large repository or slow network

**Solutions:**
1. **Normal speed**: 1-2 files/second (intentional rate limiting)
2. **Adjust delay**:
   ```python
   # Edit ingest_game_repo.py, line ~296
   delay_between_batches=0.5  # Reduce from 2.0
   ```
3. **Use incremental mode**: Only changed files are re-ingested

### Issue: "Out of disk space"

**Problem**: ChromaDB database is large

**Solutions:**
1. **Check database size**:
   ```bash
   du -sh ./chroma_db_adastrea
   ```
2. **Clean old databases**:
   ```bash
   rm -rf ./chroma_db_adastrea_old
   ```
3. **Typical size**: ~50-200MB depending on documentation size

## Performance

### Ingestion Speed

- **Initial ingestion**: 5-15 minutes (depends on doc size)
- **Update ingestion**: 1-3 minutes (only changed files)
- **Processing rate**: ~1-2 files/second

### Query Performance

- **Cold query**: 1-3 seconds (with LLM processing)
- **Cached query**: <100ms (from cache)
- **Database lookup**: ~50-200ms (vector search)

### Resource Usage

- **RAM**: ~500MB-2GB during ingestion
- **CPU**: ~50-80% during embedding generation
- **Disk**: ~50-200MB for database

## Advanced Usage

### Custom Clone Directory

```bash
python3 ingest_game_repo.py --clone-dir /path/to/custom/dir
```

### Custom Database Location

```bash
python3 ingest_game_repo.py --persist-dir /path/to/custom/db
```

### Custom Collection Name

```bash
python3 ingest_game_repo.py --collection-name my_custom_collection
```

### Automation with Cron

```bash
# Add to crontab for daily updates
0 2 * * * cd /path/to/Adastrea-Director && python3 ingest_game_repo.py
```

### GitHub Actions Workflow

```yaml
name: Update RAG Database
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2am
jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run ingestion
        run: python3 ingest_game_repo.py
        env:
          GITHUB_TOKEN: ${{ secrets.GAME_REPO_TOKEN }}
```

## API Reference

### Command Line Options

```bash
python3 ingest_game_repo.py [OPTIONS]

Options:
  --token TOKEN              GitHub personal access token
  --clone-dir DIR           Directory to clone repository to
  --collection-name NAME    Vector database collection name
  --persist-dir DIR         Vector database storage directory
  --check-updates           Check if updates are available
  --force                   Force re-ingestion
  --stats                   Show ingestion statistics
  -h, --help                Show help message
```

### Environment Variables

```bash
# GitHub Access
GITHUB_TOKEN=ghp_xxxxx              # For private repositories

# Embedding Configuration
EMBEDDING_PROVIDER=hf                # Options: hf, huggingface, openai
HUGGINGFACE_MODEL_NAME=all-MiniLM-L6-v2  # HuggingFace model name
OPENAI_API_KEY=sk-xxxxx             # For OpenAI embeddings

# Database Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db  # Default database location
CHROMA_COLLECTION_NAME=adastrea_docs  # Default collection name
```

## Best Practices

1. **First Run**: Ensure internet access for model download
2. **Regular Updates**: Run weekly to keep documentation current
3. **Disk Space**: Keep at least 1GB free for database
4. **Backup**: Periodically backup `./chroma_db_adastrea` and tracking file
5. **Testing**: Always test plugin after ingestion with sample queries
6. **Logging**: Check console output for warnings or errors

## Support

For issues or questions:
- Check TROUBLESHOOTING.md
- Review plugin logs in `<Project>/Saved/Logs/`
- Check Python backend logs in console output
- Open an issue on GitHub

---

**Last Updated**: 2025-12-20  
**Version**: 1.0  
**Compatibility**: Adastrea Director Plugin Phase 1 (Weeks 5-6+)
