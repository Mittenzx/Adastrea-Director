# Document Ingestion Guide

Learn how to populate Adastrea Director's knowledge base with your project documentation.

## Overview

Document ingestion is the process of loading your project documentation into the vector database so Adastrea Director can provide context-aware answers about your project.

## Quick Start

```bash
# Basic ingestion
python ingest.py --docs-dir /path/to/your/docs

# For Adastrea game developers
python ingest_game_repo.py
```

## Supported File Types

By default, these file types are ingested:

### Documentation Files
- `.md` - Markdown
- `.txt` - Plain text
- `.rst` - reStructuredText

### Code Files
- `.py` - Python
- `.cpp`, `.h`, `.hpp` - C++
- `.cs` - C#
- `.js`, `.ts` - JavaScript/TypeScript

### Custom File Types

Specify custom types with `--file-types`:

```bash
python ingest.py --docs-dir /path/to/docs --file-types .md .txt .pdf .docx
```

## Ingestion Options

### Basic Ingestion

```bash
# Ingest from a directory
python ingest.py --docs-dir /path/to/docs

# Ingest recursively (default)
python ingest.py --docs-dir /path/to/docs --recursive

# Non-recursive ingestion
python ingest.py --docs-dir /path/to/docs --no-recursive
```

### Update Existing Database

```bash
# Update database (only process new/changed files)
python ingest.py --docs-dir /path/to/docs --update
```

### Advanced Options

```bash
# Custom chunk size
python ingest.py --docs-dir /path/to/docs --chunk-size 1500

# Custom chunk overlap
python ingest.py --docs-dir /path/to/docs --chunk-overlap 200

# Specify embedding model
python ingest.py --docs-dir /path/to/docs --embedding-model sentence-transformers/all-mpnet-base-v2
```

## Game Repository Ingestion

For Mittenzx/Adastrea game developers:

### Command Line

```bash
# Set GitHub token
export GITHUB_TOKEN="ghp_your_token_here"

# Ingest game repository
python ingest_game_repo.py
```

### GitHub Actions (Recommended)

1. Go to [Repository Settings → Secrets](https://github.com/Mittenzx/Adastrea-Director/settings/secrets/actions)
2. Add `GAME_REPO_TOKEN` secret with your GitHub token
3. Go to [Actions](https://github.com/Mittenzx/Adastrea-Director/actions)
4. Select "Populate Database with Adastrea Game Repository"
5. Click "Run workflow"

### What Gets Ingested

The game repository ingestion includes:
- Game design documents
- C++ source files
- Blueprint documentation
- Architecture documents
- System documentation
- Configuration files

## Best Practices

### 1. Organize Your Documentation

Structure your docs for optimal ingestion:

```
docs/
├── README.md
├── architecture/
│   ├── overview.md
│   └── components.md
├── guides/
│   ├── getting-started.md
│   └── api-reference.md
└── design/
    ├── gameplay.md
    └── systems.md
```

### 2. Keep Documentation Current

Re-ingest regularly to keep knowledge base updated:

```bash
# Weekly or after major documentation changes
python ingest.py --docs-dir /path/to/docs --update
```

### 3. Include Code Comments

Well-commented code provides valuable context:

```cpp
/**
 * PlayerCharacter handles all player-related functionality.
 * 
 * Key responsibilities:
 * - Movement and physics
 * - Input handling
 * - Ability management
 */
class APlayerCharacter : public ACharacter {
    // Implementation
};
```

### 4. Use Clear File Names

Descriptive file names help with retrieval:

✅ Good:
- `player-movement-system.md`
- `inventory-design-doc.md`
- `combat-mechanics.md`

❌ Avoid:
- `doc1.md`
- `temp.md`
- `notes.txt`

### 5. Add Metadata

Include metadata in your documents:

```markdown
---
title: Player Movement System
author: John Doe
date: 2025-01-15
tags: gameplay, movement, physics
---

# Player Movement System

Content here...
```

## Monitoring Ingestion

### Check What's Ingested

**Via GUI:**
1. Open `python gui_director.py`
2. Go to "Ingest List" tab
3. View all ingested documents with statistics

**Via CLI:**
```bash
# Query the database
python main.py --query "What documents are in the database?"
```

### Ingestion Statistics

After ingestion, you'll see:

```
Ingesting documents...
✓ Processed 45 documents
✓ Created 1,234 chunks
✓ Generated embeddings
✓ Stored in vector database

Ingestion complete!
Time elapsed: 2m 34s
```

## Troubleshooting

### Issue: "No documents found"

**Solution:**
- Check directory path is correct
- Verify file types match (default: .md, .txt, .py, .cpp, .h)
- Use `--file-types` to specify custom types

### Issue: "Out of memory during ingestion"

**Solution:**
- Reduce chunk size: `--chunk-size 500`
- Process fewer files at once
- Close other applications
- Increase system RAM

### Issue: "Embeddings model fails to load"

**Solution:**
- Ensure internet connection (first-time download)
- Check available disk space (models need ~500MB)
- Try alternative model: `--embedding-model all-MiniLM-L6-v2`

### Issue: "GitHub token invalid"

**Solution:**
```bash
# Create new token at https://github.com/settings/tokens
# Required scopes: repo (for private repos)
export GITHUB_TOKEN="ghp_new_token_here"
```

## Advanced Topics

### Custom Document Loaders

For unsupported file types, create custom loaders:

```python
from langchain.document_loaders import BaseLoader

class CustomLoader(BaseLoader):
    def load(self, file_path):
        # Your custom loading logic
        return documents

# Use in ingestion
loader = CustomLoader()
documents = loader.load("custom_file.ext")
```

### Chunking Strategy

Understand chunking parameters:

- **chunk_size:** Maximum tokens per chunk (default: 1000)
- **chunk_overlap:** Overlapping tokens between chunks (default: 200)

**Guidelines:**
- Larger chunks: More context, fewer chunks
- Smaller chunks: More precise retrieval, more chunks
- Overlap: Preserves context across boundaries

### Embedding Models

Choose based on your needs:

**Default - all-MiniLM-L6-v2:**
- Dimensions: 384
- Speed: Fast
- Quality: Good
- Size: ~90MB

**High Quality - all-mpnet-base-v2:**
- Dimensions: 768
- Speed: Moderate
- Quality: Excellent
- Size: ~420MB

**OpenAI Embeddings:**
- Dimensions: 1536
- Speed: API-dependent
- Quality: Excellent
- Cost: Pay-per-use

## Integration with Other Features

### With Context-Aware Assistant

Ingested documents power the Q&A system:
```bash
python ingest.py --docs-dir /path/to/docs
python main.py
> What is the main gameplay loop?
```

### With Planning System

Planning uses documentation for context:
```bash
python ingest.py --docs-dir /path/to/docs
python planner.py "Add new inventory system"
# Planner references your ingested docs
```

### With Agent System

Agents query documentation for insights:
```bash
python ingest.py --docs-dir /path/to/docs
python agent_orchestrator_cli.py start --all
# Agents use docs for context-aware monitoring
```

## Related Documentation

- [Context-Aware Assistant](Context-Aware-Assistant.md)
- [Quick Start Tutorial](../installation/Quick-Start.md)
- [System Architecture](../architecture/System-Architecture.md)

---

[← Back to Usage](Context-Aware-Assistant.md)
