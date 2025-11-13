# How to Run Integration Tests with Your Secrets

You've added the secrets to the repository, which is great! However, there are a few ways to actually run the integration tests with those secrets.

## Understanding the Environment

The secret you added (`GAME_REPO_TOKEN`) and optional secret (`OPENAI_API_KEY`) are stored securely in GitHub and are only available to:
1. GitHub Actions workflows that you configure
2. Not available in this Copilot interactive environment for security reasons

**Note:** Only `GAME_REPO_TOKEN` is required. The system uses HuggingFace embeddings by default (no API key needed). `OPENAI_API_KEY` is optional and only used if you set `EMBEDDING_PROVIDER=openai`.

## Option 1: Trigger the GitHub Actions Workflow (Recommended)

The workflow I created (`.github/workflows/test-game-repo-integration.yml`) will automatically use your secrets.

### Method A: Push a Commit
The workflow is configured to run automatically on push. Any new commit will trigger it:

```bash
# Make a small change (like updating this file) and push
git commit --allow-empty -m "Trigger integration tests with secrets"
git push
```

Then:
1. Go to https://github.com/Mittenzx/Adastrea-Director/actions
2. Find the latest workflow run
3. Click on it to see the results
4. The "Integration Tests" job should run and pass ✅

### Method B: Manual Trigger (Easiest)
1. Go to https://github.com/Mittenzx/Adastrea-Director/actions
2. Click on "Test Game Repository Integration" workflow
3. Click "Run workflow" button (top right)
4. Select branch: the branch you want to test (e.g., `main` or your feature branch)
5. Click green "Run workflow" button
6. Wait for it to complete (2-3 minutes)
7. Check the results

### Method C: Wait for PR Update
When I push my next commit, it will automatically trigger the workflow.

## Option 2: Run Locally on Your Machine

If you want to run the integration tests on your local machine:

```bash
# Clone the repository
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director
git checkout <your-branch-name>  # e.g., main or your feature branch

# Install dependencies
pip install -r requirements.txt

# Set your required secret as environment variable
export GITHUB_TOKEN="your_ghp_token_here"

# Optional: Set OpenAI API key only if you want to use OpenAI embeddings
# export OPENAI_API_KEY="your_sk_key_here"
# export EMBEDDING_PROVIDER="openai"

# Run integration tests (uses HuggingFace embeddings by default)
pytest tests/test_game_repo_ingestion.py -v -m integration
```

## What the Integration Test Does

Once it runs successfully, it will:

1. ✅ Clone the Mittenzx/Adastrea repository using your GitHub token
2. ✅ Load all documents from the repository:
   - Documentation files (markdown, text)
   - Source code (C++, headers)
   - Configuration files
   - Blueprint documentation
3. ✅ Create embeddings using HuggingFace (default) or OpenAI (if configured)
4. ✅ Store in ChromaDB vector database
5. ✅ Verify document count > 0
6. ✅ Check database statistics

Expected output:
```
test_ingest_real_game_repo PASSED [100%]
✅ Integration test passed!
✅ Successfully cloned and ingested Mittenzx/Adastrea repository
✅ Documents loaded: X documents
✅ Chunks created: Y chunks
```

## Verifying the Secrets Are Set Up Correctly

The workflow includes a check that will tell you if secrets are configured:

```yaml
- name: Check for secrets
  run: |
    if [ -n "${{ secrets.GAME_REPO_TOKEN }}" ]; then
      echo "✅ Required secret (GAME_REPO_TOKEN) is configured"
      echo "ℹ️  Using HuggingFace embeddings (default)"
      if [ -n "${{ secrets.OPENAI_API_KEY }}" ]; then
        echo "ℹ️  OpenAI API key is also available (optional)"
      fi
    else
      echo "⚠️  GAME_REPO_TOKEN not configured"
    fi
```

## Expected Timeline

- **Manual trigger**: Results in 2-3 minutes
- **Push commit**: Results in 2-3 minutes after push
- **Next PR update**: Automatic when I push next commit

## Troubleshooting

### Workflow doesn't run
- Check that workflow file exists in `.github/workflows/`
- Verify you're triggering from correct branch
- Check Actions tab is not disabled in repository settings

### "Secrets not configured" message
- Verify secret names are exactly: `GAME_REPO_TOKEN` and `OPENAI_API_KEY`
- Check they were added to the correct repository (Adastrea-Director)
- Ensure you have admin access to the repository

### Integration test fails
- Check GitHub token has `repo` scope and access to Mittenzx/Adastrea
- Verify OpenAI API key is valid and has credits
- Check error message in workflow logs

## Recommendation

**The easiest way right now is:**

1. Go to https://github.com/Mittenzx/Adastrea-Director/actions
2. Click "Test Game Repository Integration"
3. Click "Run workflow"
4. Select your branch
5. Click "Run workflow"
6. Wait 2-3 minutes
7. Check results ✅

This will immediately test with your secrets and show you the results!

---

**Alternative:** I can push an empty commit to trigger the workflow automatically. Would you like me to do that?
