# Quick Start: Game Repository Integration

This guide gets you up and running with Mittenzx/Adastrea game repository integration in under 5 minutes.

## Prerequisites

1. **OpenAI API Key** - Required
2. **GitHub Token** - Only if Mittenzx/Adastrea is private

## Setup (One Time)

### Step 1: Set Environment Variables

**Linux/Mac:**
```bash
export OPENAI_API_KEY="sk-..."
export GITHUB_TOKEN="ghp_..."  # If repo is private
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-..."
$env:GITHUB_TOKEN="ghp_..."  # If repo is private
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-...
set GITHUB_TOKEN=ghp_...
```

### Step 2: Ingest the Game Repository

```bash
python ingest_game_repo.py
```

That's it! The script will:
- Clone Mittenzx/Adastrea
- Load all documents (docs, source, blueprints)
- Create embeddings
- Store in vector database
- Track the commit for future updates

## Daily Use

### Option 1: GUI (Easiest)

```bash
python gui_director.py
```

1. Click "🔗 Ingest Repo"
2. Enter: `https://github.com/Mittenzx/Adastrea`
3. Click "Clone & Ingest"

### Option 2: Command Line

**Ask questions about the game:**
```bash
python main.py
```

Then type questions like:
- "What are the main character abilities?"
- "Explain the combat system"
- "What's the player movement code?"

**Update knowledge base:**
```bash
python ingest_game_repo.py --check-updates  # Check for changes
python ingest_game_repo.py                   # Update if needed
```

## Automatic Updates

### Linux/Mac (cron)

```bash
crontab -e
# Add: Daily at 3 AM
0 3 * * * cd /path/to/Adastrea-Director && python ingest_game_repo.py
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, 3:00 AM
4. Action: Start Program
   - Program: `python`
   - Arguments: `ingest_game_repo.py`
   - Start in: `C:\path\to\Adastrea-Director`

## Common Commands

```bash
# Basic ingestion
python ingest_game_repo.py

# Check if updates available
python ingest_game_repo.py --check-updates

# Force re-ingestion
python ingest_game_repo.py --force

# View statistics
python ingest_game_repo.py --stats

# Run tests
pytest tests/test_game_repo_ingestion.py -v -m unit
```

## Troubleshooting

### "Authentication failed"
- Check GITHUB_TOKEN is set correctly
- Verify token has `repo` scope
- Try: `echo $GITHUB_TOKEN` (Linux/Mac) or `echo %GITHUB_TOKEN%` (Windows)

### "No documents found"
- Repository structure might be different than expected
- Check console output for which directories were found
- Customize `INGEST_DIRS` in `ingest_game_repo.py` if needed

### "Rate limit exceeded"
- Wait 5-10 minutes
- Use smaller batch size: Edit `batch_size` in script
- Increase delay: Edit `delay_between_batches` in script

## Next Steps

For more details, see:
- [GAME_REPO_INGESTION.md](GAME_REPO_INGESTION.md) - Complete guide
- [TESTING.md](TESTING.md) - Running tests
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

## Getting Help

1. Check [GAME_REPO_INGESTION.md](GAME_REPO_INGESTION.md)
2. Review error messages carefully
3. Open an issue with:
   - Error message
   - Steps to reproduce
   - OS and Python version

---

**Quick Commands Cheatsheet:**

| Task | Command |
|------|---------|
| Initial setup | `python ingest_game_repo.py` |
| Check updates | `python ingest_game_repo.py --check-updates` |
| View stats | `python ingest_game_repo.py --stats` |
| Ask questions | `python main.py` |
| Use GUI | `python gui_director.py` |
| Run tests | `pytest tests/test_game_repo_ingestion.py -v` |
