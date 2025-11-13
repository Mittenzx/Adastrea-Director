# How to Populate the Database with Adastrea Game Repository

This guide explains how to populate the Adastrea Director database with information from the mittenzx/adastrea game repository.

## Why Populate the Database?

Populating the database allows Adastrea Director to:
- Answer questions about your game's codebase
- Provide context-aware suggestions based on your game's design
- Help with development tasks by understanding your game's architecture
- Assist all agents (Goal Analysis, Task Decomposition, etc.) with game-specific knowledge

## Quick Start

### Prerequisites

1. **Python 3.9+** installed (3.12 recommended)
2. **Dependencies installed**: Run `pip install -r requirements.txt`
3. **GitHub Token** (for private repository access)

### Option 1: Using GitHub Actions (Recommended for CI/CD)

This is the easiest method if you want automated, scheduled updates.

#### Step 1: Configure GitHub Token

1. Create a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name: `Adastrea Director - Game Repo Access`
   - Expiration: 90 days (or your preference)
   - Scopes: ✅ **repo** (Full control of private repositories)
   - Click "Generate token" and **copy it immediately**

2. Add token as repository secret:
   - Go to https://github.com/Mittenzx/Adastrea-Director/settings/secrets/actions
   - Click "New repository secret"
   - Name: `GAME_REPO_TOKEN`
   - Value: [paste your token here]
   - Click "Add secret"

For detailed instructions, see [SETUP_GITHUB_SECRETS.md](SETUP_GITHUB_SECRETS.md).

#### Step 2: Run the Workflow

1. Go to the **Actions** tab in GitHub
2. Select "Populate Database with Adastrea Game Repository"
3. Click "Run workflow"
4. Choose your options:
   - **Branch**: Select the branch (usually `main`)
   - **Force re-ingestion**: Select `false` for incremental update or `true` to re-ingest everything
5. Click "Run workflow"

The workflow will:
- Clone the mittenzx/adastrea repository
- Extract and process all documents
- Create embeddings using HuggingFace (local, no API key needed)
- Store in ChromaDB
- Upload the database as an artifact

#### Step 3: Download the Database (Optional)

After the workflow completes:
1. Go to the workflow run
2. Scroll down to "Artifacts"
3. Download "adastrea-database"
4. Extract to your local repository root

### Option 2: Local Command Line

If you prefer to run locally or need immediate updates.

#### Step 1: Set Environment Variable

**Linux/Mac:**
```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

**Windows (PowerShell):**
```powershell
$env:GITHUB_TOKEN="ghp_your_token_here"
```

**Windows (Command Prompt):**
```cmd
set GITHUB_TOKEN=ghp_your_token_here
```

#### Step 2: Run the Ingestion Script

```bash
# Basic ingestion (recommended)
python ingest_game_repo.py

# Check if updates are available first
python ingest_game_repo.py --check-updates

# Force re-ingestion of all files
python ingest_game_repo.py --force

# View statistics
python ingest_game_repo.py --stats
```

### Option 3: Using the GUI

The GUI provides a user-friendly interface for database population.

1. Start the GUI:
   ```bash
   python gui_director.py
   ```

2. Click "Update Knowledge Base" or use the menu: **Edit → Update Knowledge Base** (Ctrl+U)

3. The GUI will use environment variables (GITHUB_TOKEN) if available

## Configuration Options

### Embedding Provider

By default, the script uses **HuggingFace embeddings** (local, no API key required).

To use OpenAI embeddings instead:

**Set environment variable:**
```bash
export EMBEDDING_PROVIDER=openai
export OPENAI_API_KEY="sk-your-key-here"
```

**Or in the workflow:**
Uncomment these lines in `.github/workflows/populate-database.yml`:
```yaml
EMBEDDING_PROVIDER: openai
OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Custom Directories

By default, the script ingests from these directories:
- `docs/`
- `Documentation/`
- `Source/`
- `Content/`
- `Config/`

To customize, edit `INGEST_DIRS` in `ingest_game_repo.py`.

### Database Location

Default: `./chroma_db_adastrea/`

To change:
```bash
python ingest_game_repo.py --persist-dir /path/to/custom/location
```

## Automated Updates

### GitHub Actions (Daily Checks)

The workflow includes a scheduled run every day at 3 AM UTC:
- Automatically checks for updates
- Only re-ingests if changes detected
- Minimal API usage

### Local Automation

**Linux/Mac (cron):**
```bash
crontab -e
# Add this line for daily updates at 3 AM:
0 3 * * * cd /path/to/Adastrea-Director && python ingest_game_repo.py
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Update Adastrea Database"
4. Trigger: Daily, 3:00 AM
5. Action: Start Program
   - Program: `python`
   - Arguments: `ingest_game_repo.py`
   - Start in: `C:\path\to\Adastrea-Director`

## Verification

### Check Database Statistics

```bash
python ingest_game_repo.py --stats
```

Output example:
```
Ingestion Statistics:
  Last commit: abc123def456...
  Last ingestion: 2025-11-13T08:00:00
  Documents: 142
  Chunks: 1250
```

### Test the Knowledge Base

```bash
python main.py
```

Then ask questions like:
- "What are the main gameplay systems?"
- "Describe the character controller"
- "What's in the combat system?"

## Troubleshooting

### Authentication Failed

**Problem:** `fatal: Authentication failed for 'https://github.com/Mittenzx/Adastrea.git/'`

**Solutions:**
1. Verify GITHUB_TOKEN is set correctly
2. Check token has `repo` scope
3. Ensure token hasn't expired
4. Regenerate token if needed

### No Documents Found

**Problem:** `No documents found to ingest`

**Solutions:**
1. Check the repository structure matches expected directories
2. Customize `INGEST_DIRS` in `ingest_game_repo.py`
3. Verify the repository was cloned successfully

### Rate Limit Exceeded

**Problem:** `Rate limit exceeded` or `429 Too Many Requests`

**Solutions:**
1. Wait 5-10 minutes before retrying
2. Use smaller batch size (edit `batch_size` in the script)
3. Increase delay between batches (edit `delay_between_batches`)
4. Consider using HuggingFace embeddings (no rate limits)

### Out of Memory

**Problem:** System runs out of memory during ingestion

**Solutions:**
1. Use smaller batch size
2. Process fewer files at once
3. Increase system swap space
4. Close other applications

## Best Practices

### 1. Regular Updates

- Run ingestion weekly or after major game changes
- Use the scheduled workflow for automatic updates
- Monitor the Actions tab for failures

### 2. Token Security

- Never commit tokens to code
- Use repository secrets for GitHub Actions
- Rotate tokens every 90 days
- Delete tokens when no longer needed

### 3. Verification

- Always check statistics after ingestion
- Test with a few questions to verify knowledge
- Monitor database size (should grow with game content)

### 4. Performance

- Use HuggingFace embeddings for faster, free processing
- Enable incremental updates (default) to skip unchanged files
- Schedule ingestion during off-hours

## What Gets Ingested?

The script processes these file types:

**Documentation:**
- Markdown (`.md`)
- Text files (`.txt`)
- PDFs (`.pdf`)
- Word documents (`.docx`)

**Code:**
- Python (`.py`)
- JavaScript/TypeScript (`.js`, `.jsx`, `.ts`, `.tsx`)
- C++ (`.cpp`, `.cc`, `.cxx`, `.h`, `.hpp`)
- C# (`.cs`)

**Configuration:**
- JSON (`.json`)
- YAML (`.yaml`, `.yml`)

## Database Structure

After population, you'll have:

```
Adastrea-Director/
├── chroma_db_adastrea/          # Vector database
│   ├── chroma.sqlite3           # SQLite database
│   └── [other chroma files]
└── .adastrea_ingestion_tracking.json  # Tracking file
```

The tracking file records:
- Last commit hash processed
- Timestamp of last ingestion
- Document and chunk counts

## Integration with Agents

Once populated, all agents can access this knowledge:

- **Query Agent** (Phase 1): Answers questions about your game
- **Goal Analysis Agent** (Phase 2): Understands game context when analyzing goals
- **Task Decomposition Agent** (Phase 2): Creates tasks based on game architecture
- **Code Generation Agent** (Phase 2): Generates code consistent with your game
- **Future Agents** (Phase 3+): Will have full game context

## Monitoring and Maintenance

### Check Workflow Status

1. Go to Actions tab
2. View recent workflow runs
3. Check for failures or warnings

### Database Health

```bash
# View statistics
python ingest_game_repo.py --stats

# Check for updates
python ingest_game_repo.py --check-updates

# Test queries
python main.py
```

### Cleanup

To start fresh:
```bash
# Remove database
rm -rf chroma_db_adastrea/

# Remove tracking
rm .adastrea_ingestion_tracking.json

# Re-ingest
python ingest_game_repo.py
```

## Cost Considerations

### HuggingFace Embeddings (Default)
- **Cost:** Free
- **Processing:** Local (uses CPU/GPU)
- **Speed:** Fast
- **Quality:** Good for most use cases

### OpenAI Embeddings (Optional)
- **Cost:** ~$0.00013 per 1K tokens
- **Processing:** Cloud API
- **Speed:** Depends on API rate limits
- **Quality:** Excellent

**Estimated costs for typical game project:**
- 500 files, average 2KB each: ~$0.13
- Monthly updates (small changes): <$0.01 per update

## Next Steps

After populating the database:

1. **Test the assistant:**
   ```bash
   python main.py
   ```

2. **Try the GUI:**
   ```bash
   python gui_director.py
   ```

3. **Use planning features:**
   ```bash
   python planning_cli.py --interactive
   ```

4. **Set up automated updates** (see Automated Updates section above)

5. **Explore Phase 2 features** - Now that agents have game context, they can provide better planning assistance

## Support

Need help? Check these resources:

1. [SETUP_GITHUB_SECRETS.md](SETUP_GITHUB_SECRETS.md) - Token setup
2. [QUICK_START_GAME_REPO.md](QUICK_START_GAME_REPO.md) - Quick reference
3. [GAME_REPO_INGESTION.md](GAME_REPO_INGESTION.md) - Complete guide
4. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
5. Open an issue on GitHub with:
   - Error message (without exposing tokens!)
   - Steps to reproduce
   - Environment details (OS, Python version)

---

**Quick Command Reference:**

| Task | Command |
|------|---------|
| Initial population | `python ingest_game_repo.py` |
| Check for updates | `python ingest_game_repo.py --check-updates` |
| Force re-ingestion | `python ingest_game_repo.py --force` |
| View statistics | `python ingest_game_repo.py --stats` |
| Test knowledge | `python main.py` |
| Use GUI | `python gui_director.py` |

---

**Estimated Time:**
- Initial setup: 10-15 minutes
- First ingestion: 5-30 minutes (depends on repo size)
- Incremental updates: 1-5 minutes

**Status:** ✅ Ready to use
