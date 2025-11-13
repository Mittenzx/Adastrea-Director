# How to Trigger Database Population (Quick Guide)

This guide shows you how to populate the Adastrea Director database **right now** using the workflow that was just created.

## ⚡ Quick Steps (5 minutes)

### Step 1: Add the GitHub Token Secret

The workflow needs a GitHub token to access the private mittenzx/adastrea repository.

1. **Create a Personal Access Token** (if you don't have one):
   - Go to: https://github.com/settings/tokens
   - Click **"Generate new token"** → **"Generate new token (classic)"**
   - Name: `Adastrea Director Database`
   - Expiration: `90 days` (or your preference)
   - Scopes: ✅ **repo** (Full control of private repositories)
   - Click **"Generate token"**
   - **Copy the token immediately** (starts with `ghp_`)

2. **Add it as a repository secret**:
   - Go to: https://github.com/Mittenzx/Adastrea-Director/settings/secrets/actions
   - Click **"New repository secret"**
   - Name: `GAME_REPO_TOKEN`
   - Value: Paste your token (e.g., `ghp_xxxxxxxxxxxx`)
   - Click **"Add secret"**

### Step 2: Trigger the Workflow

1. Go to the **Actions** tab: https://github.com/Mittenzx/Adastrea-Director/actions
2. In the left sidebar, click **"Populate Database with Adastrea Game Repository"**
3. Click the **"Run workflow"** button (top right)
4. Select:
   - **Branch**: `copilot/populate-db-with-adastrea-info` (or `main` after merging)
   - **Force re-ingestion**: `false` (for first run, doesn't matter)
5. Click **"Run workflow"**

### Step 3: Monitor the Workflow

1. The workflow will start running (you'll see a yellow dot)
2. Click on the workflow run to see progress
3. Wait for it to complete (typically 5-15 minutes depending on repo size)
4. Look for ✅ green checkmark when complete

### Step 4: Download the Database (Optional)

After the workflow completes successfully:

1. Scroll down to the **"Artifacts"** section
2. Click **"adastrea-database"** to download
3. Extract the files:
   - `chroma_db_adastrea/` - The vector database
   - `.adastrea_ingestion_tracking.json` - Tracking file
4. Place them in your local repository root

### Step 5: Verify Success

Check the workflow output for statistics like:

```
✅ Database population complete!
📊 Database is ready for use by Adastrea Director agents

Ingestion Statistics:
  Last commit: abc123def456...
  Last ingestion: 2025-11-13T10:00:00
  Documents: 150
  Chunks: 1342
```

## What Happens During Population

The workflow will:
1. ✅ Clone the mittenzx/adastrea repository
2. ✅ Scan for documentation, code, and config files
3. ✅ Create embeddings using HuggingFace (local, free)
4. ✅ Store in ChromaDB vector database
5. ✅ Upload as artifact for download
6. ✅ Track the commit for future updates

## Troubleshooting

### "GAME_REPO_TOKEN is NOT configured"

**Problem**: The workflow shows this message and exits

**Solution**: 
- Make sure you added the secret with the exact name `GAME_REPO_TOKEN`
- Verify the token has `repo` scope
- Check the token hasn't expired

### "Authentication failed"

**Problem**: Can't clone the repository

**Solution**:
- Regenerate the token
- Ensure you have access to mittenzx/adastrea repository
- Update the `GAME_REPO_TOKEN` secret

### Workflow doesn't appear

**Problem**: Can't find the workflow in Actions tab

**Solution**:
- Make sure this branch is pushed to GitHub
- Check that the workflow file exists at `.github/workflows/populate-database.yml`
- Try refreshing the page

## Next Steps After Population

Once the database is populated:

1. **Use the assistant**:
   ```bash
   python main.py
   ```

2. **Try the GUI**:
   ```bash
   python gui_director.py
   ```

3. **Test with a question**:
   - "What are the main gameplay systems in Adastrea?"
   - "Describe the character controller implementation"
   - "What's the structure of the combat system?"

4. **Use planning features**:
   ```bash
   python planning_cli.py --interactive
   ```

## Automatic Updates

The workflow is configured to run automatically:
- **Daily at 3 AM UTC** - Checks for updates and re-ingests if needed
- **Manual trigger** - Run anytime via Actions tab

To disable automatic updates, remove the `schedule:` section from the workflow file.

## Alternative: Local Population

If you prefer to run locally instead of using GitHub Actions:

```bash
# Set your GitHub token
export GITHUB_TOKEN="ghp_your_token_here"

# Run the ingestion
python ingest_game_repo.py

# Check statistics
python ingest_game_repo.py --stats
```

See [POPULATE_DATABASE.md](POPULATE_DATABASE.md) for complete local setup instructions.

---

**Need more help?** See:
- [POPULATE_DATABASE.md](POPULATE_DATABASE.md) - Complete guide
- [SETUP_GITHUB_SECRETS.md](SETUP_GITHUB_SECRETS.md) - Detailed token setup
- [QUICK_START_GAME_REPO.md](QUICK_START_GAME_REPO.md) - 5-minute local setup

**Ready to go!** The workflow is set up and ready to populate your database. Just add the token and click "Run workflow"! 🚀
