# Using OpenAI Embeddings (Optional)

This guide explains how to configure Adastrea Director to use OpenAI embeddings instead of the default HuggingFace embeddings.

## When to Use OpenAI Embeddings

**Default (Recommended):** The system uses HuggingFace embeddings by default, which:
- Work completely offline after initial model download
- Are free to use
- Provide good quality for most use cases
- Run locally on your machine

**Optional (OpenAI):** You may want to use OpenAI embeddings if you:
- Need potentially higher quality embeddings
- Are already paying for OpenAI and want consistent embeddings
- Have specific requirements for embedding quality
- Don't mind the API costs

## Cost Consideration

OpenAI embeddings have associated costs:
- **text-embedding-ada-002**: ~$0.0001 per 1K tokens
- **text-embedding-3-small**: ~$0.00002 per 1K tokens
- **text-embedding-3-large**: ~$0.00013 per 1K tokens

A typical documentation repository might cost $0.50-$5.00 to embed, depending on size.

## Prerequisites

1. **OpenAI Account**: Sign up at https://platform.openai.com
2. **API Key**: Create an API key with billing enabled
3. **Billing Setup**: Ensure you have payment method configured

## Configuration

### Step 1: Get Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Click **+ Create new secret key**
3. Name it: `Adastrea Director Embeddings`
4. Click **Create secret key**
5. **IMPORTANT:** Copy the key immediately (starts with `sk-`)
   - You won't be able to see it again!
   - Store it securely

Example key format: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2: Configure Environment Variables

#### Option A: Environment Variables (Recommended)

```bash
# Set the embedding provider to OpenAI
export EMBEDDING_PROVIDER=openai

# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"

# Optional: Specify OpenAI model (default: text-embedding-ada-002)
export OPENAI_EMBEDDING_MODEL="text-embedding-3-small"
```

#### Option B: .env File

Create or update `.env` file in the project root:

```bash
# Embedding Provider Configuration
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# Optional: Custom embedding model
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### Step 3: Verify Configuration

Test that OpenAI embeddings are working:

```bash
# Test with document ingestion
python ingest.py --docs-dir docs/ --verbose

# You should see messages indicating OpenAI embeddings are being used
```

## Available OpenAI Embedding Models

| Model | Dimensions | Cost per 1K tokens | Use Case |
|-------|-----------|-------------------|----------|
| `text-embedding-ada-002` | 1536 | $0.0001 | Default, good balance |
| `text-embedding-3-small` | 1536 | $0.00002 | Most cost-effective |
| `text-embedding-3-large` | 3072 | $0.00013 | Highest quality |

### Choosing a Model

```bash
# Use the most cost-effective model
export OPENAI_EMBEDDING_MODEL="text-embedding-3-small"

# Use the highest quality model
export OPENAI_EMBEDDING_MODEL="text-embedding-3-large"
```

## Usage Examples

### Basic Document Ingestion

```bash
# Set OpenAI as provider
export EMBEDDING_PROVIDER=openai
export OPENAI_API_KEY="sk-your-key"

# Ingest documents
python ingest.py --docs-dir /path/to/docs
```

### Game Repository Ingestion

```bash
# Configure OpenAI embeddings
export EMBEDDING_PROVIDER=openai
export OPENAI_API_KEY="sk-your-key"
export GITHUB_TOKEN="ghp-your-token"

# Ingest game repository
python ingest_game_repo.py
```

### In Python Code

```python
from ingest import DocumentIngestionAgent
from langchain_openai import OpenAIEmbeddings

# Create custom OpenAI embeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key="sk-your-key"
)

# Use with ingestion agent
agent = DocumentIngestionAgent(embeddings=embeddings)
```

## GitHub Actions / CI/CD Setup

### Adding OpenAI API Key as Secret

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `OPENAI_API_KEY`
5. Value: Your OpenAI API key (starts with `sk-`)
6. Click **Add secret**

### Using in Workflow

```yaml
- name: Ingest documents with OpenAI embeddings
  run: python ingest.py --docs-dir docs/
  env:
    EMBEDDING_PROVIDER: openai
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Example Workflow

```yaml
name: Ingest Documentation

on:
  push:
    branches: [main]

jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Ingest with OpenAI embeddings
        run: python ingest.py --docs-dir docs/
        env:
          EMBEDDING_PROVIDER: openai
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## Switching Between Providers

### Switch to OpenAI

```bash
export EMBEDDING_PROVIDER=openai
export OPENAI_API_KEY="sk-your-key"
```

### Switch Back to HuggingFace

```bash
# Remove or unset the provider variable
unset EMBEDDING_PROVIDER

# Or explicitly set to HuggingFace
export EMBEDDING_PROVIDER=hf
```

**Note:** When switching providers, you may need to re-ingest documents as the embeddings are different.

## Troubleshooting

### "API key not found" Error

**Problem:** OpenAI key not set or invalid

**Solution:**
1. Verify key is active at https://platform.openai.com/api-keys
2. Check that `EMBEDDING_PROVIDER=openai` is set
3. Ensure `OPENAI_API_KEY` environment variable is set correctly
4. Verify you have billing enabled on your OpenAI account

### "Rate limit exceeded"

**Problem:** Too many API requests to OpenAI

**Solution:**
1. Wait a few minutes before retrying
2. Upgrade your OpenAI plan for higher rate limits
3. Use smaller batch sizes in ingestion
4. Consider switching to HuggingFace embeddings (no rate limits)

### "Insufficient quota"

**Problem:** OpenAI account has no credits or billing not set up

**Solution:**
1. Go to https://platform.openai.com/account/billing
2. Add a payment method
3. Add credits to your account
4. Wait a few minutes for the system to update

### High Costs

**Problem:** Unexpectedly high API costs

**Solution:**
1. Use `text-embedding-3-small` instead of `text-embedding-3-large`
2. Consider switching to HuggingFace for development/testing
3. Only use OpenAI embeddings for production
4. Set up cost alerts in your OpenAI account

## Cost Optimization Tips

1. **Use the smallest model that meets your needs**
   - Start with `text-embedding-3-small`
   - Only upgrade if quality is insufficient

2. **Cache embeddings**
   - The system already stores embeddings in the vector database
   - Avoid re-ingesting documents unless necessary

3. **Incremental ingestion**
   - Use `--check-updates` to only ingest new/changed documents
   - Saves costs by not re-embedding unchanged content

4. **Development vs Production**
   - Use HuggingFace for development and testing (free)
   - Use OpenAI only for production deployments

5. **Set up cost alerts**
   - Configure alerts at https://platform.openai.com/account/billing/limits
   - Get notified when you exceed a certain spending threshold

## Performance Comparison

| Aspect | HuggingFace | OpenAI |
|--------|-------------|---------|
| **Cost** | Free | ~$0.00002-$0.00013 per 1K tokens |
| **Speed (first run)** | Slower (model download) | Fast |
| **Speed (subsequent)** | Fast (cached model) | Depends on network |
| **Quality** | Good | Potentially higher |
| **Privacy** | Complete (local) | Data sent to OpenAI |
| **Offline capability** | Yes (after download) | No (requires internet) |
| **Rate limits** | None | Yes (depends on plan) |

## Security Best Practices

### ✅ DO

- ✅ Store API keys in environment variables or secrets
- ✅ Use repository secrets for CI/CD
- ✅ Rotate API keys periodically (every 90 days)
- ✅ Set up cost alerts to prevent unexpected charges
- ✅ Use minimum required permissions

### ❌ DON'T

- ❌ Never commit API keys to source code
- ❌ Never share API keys in issues or comments
- ❌ Never use API keys with broader permissions than needed
- ❌ Never store API keys in files tracked by git

## Reverting to HuggingFace

If you want to switch back to HuggingFace embeddings:

```bash
# Method 1: Remove the environment variable
unset EMBEDDING_PROVIDER

# Method 2: Explicitly set to HuggingFace
export EMBEDDING_PROVIDER=hf

# Verify HuggingFace is being used
python ingest.py --docs-dir docs/ --verbose
```

**Important:** You'll need to re-ingest your documents with the new embedding provider, as embeddings from different providers are not compatible.

## Support

If you encounter issues:

1. Check that API key is valid and billing is enabled
2. Verify environment variables are set correctly
3. Check OpenAI status page: https://status.openai.com
4. Review error messages for specific guidance
5. Consider switching to HuggingFace if issues persist

## Related Documentation

- [Embedding Provider Changes](../../EMBEDDING_PROVIDER_CHANGES.md) - Overview of embedding provider system
- [Installation Guide](INSTALLATION.md) - General installation instructions
- [Document Ingestion Guide](DOCUMENT_INGESTION.md) - How to ingest documents

---

**Last Updated:** 2025-11-13  
**For Default Setup:** See main README.md (HuggingFace is default and requires no API key)
