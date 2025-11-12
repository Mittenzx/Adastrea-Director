# Document Ingestion System

## Overview

The Adastrea Director document ingestion system is a powerful, flexible component designed to load, process, and store various document types for retrieval-augmented generation (RAG). It supports multiple file formats, intelligent chunking strategies, and automatic metadata enrichment.

## Features

### 🔄 Incremental Ingestion (NEW)

The system now supports intelligent incremental ingestion:

- **Hash-based change detection**: Uses SHA-256 to detect file modifications
- **Skip unchanged files**: Automatically skips files that haven't changed since last ingestion
- **Update modified files**: Detects and re-ingests only changed files
- **Add new files**: Automatically adds newly discovered files
- **Force re-ingestion**: Option to bypass change detection with `--reingest` flag
- **Sequential processing**: Processes files one-by-one to avoid rate limits

This reduces API costs, speeds up ingestion, and minimizes rate limit errors.

### 📄 Supported File Types

#### Documentation Files
- **Markdown** (`.md`) - Game design documents, README files
- **Plain Text** (`.txt`) - Notes, documentation
- **PDF** (`.pdf`) - Design documents, manuals
- **Word Documents** (`.docx`) - Formal documentation

#### Code Files
- **Python** (`.py`) - Game logic, scripts
- **JavaScript** (`.js`, `.jsx`) - Web interfaces, game logic
- **TypeScript** (`.ts`, `.tsx`) - Typed game logic
- **C++** (`.cpp`, `.cc`, `.cxx`, `.h`, `.hpp`) - Engine code, performance-critical systems
- **C#** (`.cs`) - Unity/Unreal scripts

#### Configuration Files
- **JSON** (`.json`) - Configuration, data files
- **YAML** (`.yaml`, `.yml`) - Configuration files

### 🧩 Intelligent Chunking

The system uses language-aware chunking strategies:

- **Language-Specific Splitters**: Automatically detects programming language and uses appropriate chunking strategy
- **Recursive Character Text Splitter**: For documentation and general text
- **Code-Aware Splitters**: Preserve function/class boundaries in code files
- **Configurable Chunk Size**: Adjust chunk size and overlap for optimal embedding

### 📊 Metadata Enrichment

Automatically enriches document metadata with:

- `filename`: Name of the source file
- `extension`: File extension
- `doc_type`: Classification (code, documentation, document, config, other)
- `language`: Programming language for code files
- `file_size`: Size of the source file in bytes
- `file_hash`: SHA-256 hash for change detection (NEW)

### ⚡ Batch Processing

Efficient batch processing for large document sets:

- Automatic batch mode for 200+ chunks
- Configurable batch size
- Progress tracking with visual feedback
- Memory-efficient processing

## Installation

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Ingest documents from a directory (incremental mode - default):

```bash
python ingest.py --docs-dir /path/to/your/docs
```

This will:
- Skip files that haven't changed since last ingestion
- Update files that have been modified
- Add new files that weren't ingested before

Ingest a single file:

```bash
python ingest.py --file /path/to/document.md
```

### Advanced Options

#### Custom Collection Name

```bash
python ingest.py --docs-dir /path/to/docs --collection-name my_game_project
```

#### Custom Chunk Settings

```bash
python ingest.py --docs-dir /path/to/docs --chunk-size 500 --chunk-overlap 100
```

Smaller chunks provide more focused context but require more API calls. Larger chunks provide more context but may be less precise.

#### Incremental Ingestion Options

Force re-ingestion of all files (bypass change detection):

```bash
python ingest.py --docs-dir /path/to/docs --reingest
```

Use legacy mode (load all files at once, no incremental processing):

```bash
python ingest.py --docs-dir /path/to/docs --legacy-mode
```

Adjust delay between files (to avoid rate limits):

```bash
python ingest.py --docs-dir /path/to/docs --delay 3.0
```

#### Batch Processing (Legacy Mode Only)

For large document sets in legacy mode (recommended for 200+ documents):

```bash
python ingest.py --docs-dir /path/to/docs --legacy-mode --use-batch --batch-size 50
```

Note: In incremental mode (default), files are processed sequentially with automatic delays.

#### View Database Statistics

```bash
python ingest.py --stats
```

### Complete Example

```bash
python ingest.py \
  --docs-dir ./game_docs \
  --collection-name space_adventure \
  --chunk-size 1000 \
  --chunk-overlap 200 \
  --batch-size 100 \
  --use-batch
```

## Document Organization Best Practices

### Recommended Directory Structure

```
game_project/
├── design_docs/
│   ├── game_design_document.md
│   ├── technical_design.md
│   └── art_bible.pdf
├── code/
│   ├── python/
│   │   ├── game_logic.py
│   │   └── player_controller.py
│   ├── cpp/
│   │   ├── physics_engine.cpp
│   │   └── physics_engine.h
│   └── scripts/
│       └── level_loader.js
├── config/
│   ├── game_settings.json
│   └── environment.yaml
└── notes/
    └── development_notes.txt
```

### What to Ingest

✅ **DO Ingest:**
- Game design documents
- Technical specifications
- Code files (logic, gameplay systems)
- Configuration files
- Development notes and documentation
- API documentation
- README files

❌ **DON'T Ingest:**
- Binary assets (textures, models, audio)
- Build artifacts
- Temporary files
- Version control directories (`.git`)
- Dependencies (`node_modules`, `venv`)
- Large generated files

### Document Quality Tips

1. **Keep documents well-structured** - Use clear headings and sections
2. **Use descriptive names** - `player_movement_system.md` not `doc1.md`
3. **Add comments to code** - Code comments become searchable context
4. **Update regularly** - Re-run ingestion when documents change (incremental mode only processes changes)
5. **Use consistent formatting** - Helps with chunking and retrieval

## How It Works

### 1. Document Loading

The system scans directories for supported file types and loads them using appropriate loaders:

- **DirectoryLoader**: Recursively scans directories
- **TextLoader**: Plain text files
- **PythonLoader**: Python source code with syntax awareness
- **PyPDFLoader**: PDF documents
- **Docx2txtLoader**: Word documents
- **UnstructuredMarkdownLoader**: Markdown files

### 2. Metadata Enrichment

Each document's metadata is automatically enriched with:

```python
{
    "source": "/path/to/file.py",
    "filename": "file.py",
    "extension": ".py",
    "doc_type": "code",
    "language": "python",
    "file_size": 1234,
    "file_hash": "e5a0e044add66321198f1ad628118960b4b37c804af28ce647fd7aa1f1154b20"
}
```

### 3. Intelligent Chunking

Documents are split into chunks based on type:

- **Code files**: Language-specific splitters preserve code structure
- **Documentation**: Recursive splitter respects paragraphs and sections
- **Configuration**: Text splitter with appropriate separators

### 4. Embedding Generation

Each chunk is converted to a vector embedding using OpenAI's embedding model:

- Model: `text-embedding-ada-002`
- Dimension: 1536
- Cost-effective and high-quality

### 5. Vector Storage

Embeddings are stored in ChromaDB:

- **Persistent storage**: Saved to disk for reuse
- **Fast retrieval**: Optimized for similarity search
- **Metadata filtering**: Query by document type, language, etc.

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
```

### Default Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chunk_size` | 1000 | Characters per chunk |
| `chunk_overlap` | 200 | Overlap between chunks |
| `collection_name` | adastrea_docs | Vector store collection |
| `persist_directory` | ./chroma_db | Storage location |
| `batch_size` | 100 | Documents per batch |

## Error Handling

The system provides clear error messages for common issues:

### Missing API Key
```
Missing or invalid API key for OpenAI
Please set the OPENAI_API_KEY environment variable.
```

### Rate Limiting
```
Rate limit exceeded for OpenAI API
- Wait a few minutes before trying again
- Consider upgrading your API plan
- Reduce chunk size to make fewer API calls
```

### File Encoding Issues
```
Unable to decode file with utf-8 encoding
Try:
- Converting the file to UTF-8 encoding
- Checking if the file is corrupted
```

## Performance Considerations

### Memory Usage

- **Small projects** (<100 docs): ~100-500 MB
- **Medium projects** (100-500 docs): ~500 MB - 2 GB
- **Large projects** (500+ docs): Use batch processing

### API Costs

Approximate costs for OpenAI API (as of 2024):

- **Embeddings**: ~$0.0001 per 1K tokens
- **1000 chunks**: ~$0.10 - $0.50
- **10,000 chunks**: ~$1.00 - $5.00

### Processing Time

- **Small projects**: 1-5 minutes
- **Medium projects**: 5-15 minutes
- **Large projects**: 15-60 minutes

Factors affecting speed:
- Number of documents
- Document size
- API rate limits
- Network speed

## Troubleshooting

### Issue: "No documents loaded"

**Cause**: Directory doesn't exist or contains no supported files

**Solution**:
- Verify the directory path
- Check that files have supported extensions
- Ensure files are readable (check permissions)

### Issue: "Missing dependency for .md files"

**Cause**: `unstructured` package not installed

**Solution**:
```bash
pip install unstructured
```

### Issue: Slow ingestion

**Cause**: Rate limiting or large document set

**Solution**:
- Use batch processing mode
- Reduce chunk size
- Wait between retries if rate limited

### Issue: "Database operation failed"

**Cause**: ChromaDB initialization or persistence error

**Solution**:
- Check disk space
- Verify write permissions for persist directory
- Delete and recreate the database directory

## API Reference

### DocumentIngestionAgent

```python
agent = DocumentIngestionAgent(
    collection_name="my_collection",
    persist_directory="./db",
    chunk_size=1000,
    chunk_overlap=200
)
```

#### Methods

**load_documents_from_directory(directory: str) -> List[Document]**
- Load all supported documents from a directory
- Returns list of loaded documents with metadata

**load_single_file(file_path: str) -> List[Document]**
- Load a single file
- Returns list containing the loaded document

**chunk_documents(documents: List[Document]) -> List[Document]**
- Split documents into chunks using language-aware strategies
- Returns list of document chunks

**ingest_documents(documents: List[Document]) -> bool**
- Ingest documents into vector database
- Returns True if successful

**ingest_documents_batch(documents: List[Document], batch_size: int = 100) -> bool**
- Ingest documents in batches (memory efficient)
- Returns True if successful

**get_database_stats() -> Dict[str, Any]**
- Get statistics about the vector database
- Returns dictionary with collection info

## Future Enhancements

Planned features for future releases:

- [x] Incremental updates (only ingest changed files) - **COMPLETED**
- [ ] Resume interrupted ingestion
- [ ] Support for more file types (HTML, XML, CSV)
- [ ] Custom chunking strategies per project
- [ ] Parallel processing for faster ingestion
- [ ] Automatic document deduplication
- [ ] Web scraping for online documentation
- [ ] Git integration for code repositories

## Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review [Error Handling](#error-handling) messages
3. Open an issue on GitHub
4. Consult the main [README.md](README.md)

---

**Last Updated:** 2024-11-12
**Version:** 1.1.0 - Added incremental ingestion with hash-based change detection
