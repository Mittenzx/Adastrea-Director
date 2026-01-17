# Context-Aware Assistant (Phase 1)

The Context-Aware Assistant is the foundation of Adastrea Director, providing intelligent Q&A capabilities powered by Retrieval-Augmented Generation (RAG).

## 🎯 Overview

The Context-Aware Assistant allows you to:
- 📚 Ask questions about your project documentation
- 🔍 Get answers with source citations
- 💡 Discover relevant information across all documents
- 🎮 Access Unreal Engine and game development knowledge

**Status:** ✅ Complete and Production-Ready

## How It Works

### RAG Architecture

The Context-Aware Assistant uses a sophisticated RAG (Retrieval-Augmented Generation) pipeline:

1. **Document Ingestion**
   - Documents are split into manageable chunks
   - Each chunk is converted to a vector embedding
   - Embeddings are stored in a vector database (ChromaDB)

2. **Query Processing**
   - Your question is converted to a vector embedding
   - Similar chunks are retrieved from the database
   - Context is assembled from relevant chunks

3. **Answer Generation**
   - Context + question are sent to the LLM
   - LLM generates a comprehensive answer
   - Sources are cited for verification

```
User Query → Embedding → Similarity Search → Context Assembly → LLM → Answer
```

## Getting Started

### Prerequisites

✅ Adastrea Director installed ([Installation Guide](../installation/Getting-Started.md))
✅ LLM API key configured (Gemini or OpenAI)

### Basic Usage

#### CLI Mode

```bash
# Start the interactive assistant
python main.py

# Ask your questions
> What is the main gameplay loop?
> How do I implement player movement?
> What are the performance requirements?

# Exit when done
> quit
```

#### Single Query Mode

```bash
# Ask a single question
python main.py --query "What is the main character's backstory?"

# Useful for scripts and automation
```

## Document Ingestion

Before asking questions, you need to populate the knowledge base.

### Ingest Project Documentation

```bash
# Basic ingestion
python ingest.py --docs-dir /path/to/your/docs

# Specify file types
python ingest.py --docs-dir /path/to/docs --file-types .md .txt .rst

# Recursive ingestion (default)
python ingest.py --docs-dir /path/to/docs --recursive

# Update existing database
python ingest.py --docs-dir /path/to/docs --update
```

### Ingest Game Repository

For Mittenzx/Adastrea game developers:

```bash
# Set your GitHub token
export GITHUB_TOKEN="ghp_your_token_here"

# Ingest the game repository
python ingest_game_repo.py
```

**Alternative: Use GitHub Actions** (Recommended for team)
1. Add `GAME_REPO_TOKEN` secret in repository settings
2. Go to Actions → "Populate Database with Adastrea Game Repository"
3. Click "Run workflow"

See the [Document Ingestion Guide](Document-Ingestion.md) for more details.

## Advanced Features

### Context Window Management

The assistant intelligently manages context:

- **Default:** Top 5 most relevant chunks
- **Configurable:** Adjust in `config.json`
- **Smart Ranking:** Uses similarity scores to prioritize content

### Source Citations

Every answer includes source citations:

```
Answer: The player character has three main abilities...

Sources:
- PlayerCharacter.md (lines 45-67)
- GameplayMechanics.md (lines 122-145)
```

This allows you to:
- ✅ Verify information
- ✅ Dive deeper into specific topics
- ✅ Track down outdated documentation

### Query Optimization

Tips for better results:

**❌ Too Vague:**
```
> How do I code?
```

**✅ Specific and Clear:**
```
> How do I implement a singleton pattern for the GameManager in C++?
```

**❌ Multiple Questions:**
```
> What is the player character and what are their abilities and how do I implement them?
```

**✅ One Question at a Time:**
```
> What are the player character's abilities?
> How do I implement ability X in C++?
```

## Configuration

### LLM Provider Selection

You can choose from multiple LLM providers:

**Gemini (Recommended):**
```bash
export GEMINI_KEY="your-api-key-here"
# or use --set-api-key flag
python main.py --set-api-key gemini
```

**OpenAI:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Ollama (Local):**
```bash
# Install and run Ollama locally
ollama serve

# Configure to use Ollama
# (Set in config or via GUI settings)
```

### Embedding Provider Selection

**Default - HuggingFace (No API Key Required):**
```python
# Uses 'sentence-transformers/all-MiniLM-L6-v2'
# Works offline after initial model download
```

**Optional - OpenAI Embeddings:**
```bash
export OPENAI_API_KEY="your-api-key-here"
# Configure in settings to use OpenAI embeddings
```

### Database Location

By default, the database is stored in `./chroma_db`. You can customize this:

```python
# In config.json
{
  "database": {
    "path": "/custom/path/to/chroma_db"
  }
}
```

## Use Cases

### 1. Onboarding New Team Members

Help new developers quickly understand the project:

```
> What is the overall architecture of the game?
> Where is the player movement implemented?
> What are the coding standards for this project?
> How is the save system implemented?
```

### 2. Debugging and Problem-Solving

Get quick answers while debugging:

```
> How is the inventory system supposed to work?
> What are the error handling patterns in this codebase?
> Where are network events processed?
```

### 3. Documentation Discovery

Find relevant documentation without manual searching:

```
> What documentation exists about the AI system?
> Show me information about performance optimization
> Where is the build process documented?
```

### 4. Code Review Assistance

Understand code context during reviews:

```
> What design patterns are used in the combat system?
> How should new abilities be structured?
> What are the testing requirements for new features?
```

## Limitations and Best Practices

### Current Limitations

- **Document Quality:** Answers are only as good as ingested documents
- **Context Window:** Limited to top relevant chunks (not entire codebase)
- **Hallucination:** LLMs may occasionally generate incorrect information
- **Real-time Data:** Database must be updated manually (not live)

### Best Practices

**✅ Do:**
- Keep documentation up-to-date and re-ingest regularly
- Ask specific, focused questions
- Verify important information from sources
- Use natural language (write as you would ask a colleague)

**❌ Don't:**
- Assume all answers are 100% accurate without verification
- Ask questions about code not in the ingested documents
- Expect real-time updates to code changes
- Use for security-sensitive information without validation

## Performance Tips

### First Query Optimization

The first query is always slower due to model loading:

```bash
# Pre-load models by running a test query
python main.py --query "test" > /dev/null
```

### GPU Acceleration

If you have a CUDA-capable GPU:

```bash
# HuggingFace embeddings will automatically use GPU
# Check GPU usage:
nvidia-smi
```

### Database Optimization

For large document collections:

```python
# Adjust chunk size in ingestion
python ingest.py --docs-dir /path/to/docs --chunk-size 1500

# Increase overlap for better context
python ingest.py --docs-dir /path/to/docs --chunk-overlap 200
```

## Troubleshooting

### No Results Returned

**Problem:** Query returns "I don't have enough information..."

**Solutions:**
- ✅ Ensure relevant documents are ingested
- ✅ Try rephrasing your question
- ✅ Check database path is correct
- ✅ Verify documents were processed successfully

### Slow Performance

**Problem:** Queries take too long

**Solutions:**
- ✅ First query is always slow (model loading) - this is normal
- ✅ Reduce number of retrieved chunks in config
- ✅ Use GPU acceleration if available
- ✅ Consider using lighter embedding models

### Incorrect Answers

**Problem:** Assistant provides wrong information

**Solutions:**
- ✅ Check source citations - is source document correct?
- ✅ Re-ingest documents if they were recently updated
- ✅ Rephrase question to be more specific
- ✅ Verify LLM API key and configuration

## API Reference

For programmatic usage:

```python
from main import AdastreaDirector

# Initialize
director = AdastreaDirector()

# Query
response = director.query("What is the main character?")

# Get sources
sources = director.get_sources(response)
```

See [Code Reference](../development/Code-Reference.md) for complete API documentation.

## Next Steps

- **📋 [Planning System](Planning-System.md)** - Create implementation plans (P2)
- **🤖 [Autonomous Agents](Autonomous-Agents.md)** - Set up proactive monitoring (P3)
- **🎮 [Unreal Plugin](../installation/Plugin-Setup.md)** - Use in Unreal Engine

## Related Pages

- [Document Ingestion Guide](Document-Ingestion.md) - Detailed ingestion instructions
- [System Architecture](../architecture/System-Architecture.md) - How RAG works
- [Troubleshooting](../installation/Troubleshooting.md) - Common issues

---

[← Back to Home](../Home.md) | [Next: Planning System →](Planning-System.md)
