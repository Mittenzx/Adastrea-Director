# Test Skip Analysis: test_ingest_real_game_repo

## Problem
The test `tests/test_game_repo_ingestion.py::TestGameRepositoryIngestion::test_ingest_real_game_repo` is being **SKIPPED** during GitHub Actions runs.

## Root Cause
The test attempts to clone the private repository `https://github.com/Mittenzx/Adastrea.git` (the game repository). The clone operation is failing, causing the test to skip with the error message from git clone.

## Why It Skips

The test has the following flow:
1. ✅ Check for `GITHUB_TOKEN` and `OPENAI_API_KEY` environment variables
2. ❌ Attempt to clone `Mittenzx/Adastrea` repository using the GITHUB_TOKEN
3. ❌ Clone fails (returncode != 0)
4. ✅ Test gracefully skips with error message

## Possible Causes

### 1. Repository Doesn't Exist
The repository `Mittenzx/Adastrea` may not exist yet, or the name may be incorrect.

**How to check:**
- Navigate to https://github.com/Mittenzx/Adastrea
- If you get a 404 error, the repository doesn't exist or is incorrectly named

**Solution:**
- Create the repository at `Mittenzx/Adastrea`
- OR update line 30 in `tests/test_game_repo_ingestion.py` to point to the correct repository URL

### 2. Token Doesn't Have Access
The `GAME_REPO_TOKEN` GitHub secret may not have access to the `Mittenzx/Adastrea` repository.

**How to check:**
- The token needs the `repo` scope for private repositories
- The token's owner needs to be a collaborator on `Mittenzx/Adastrea`

**Solution:**
- Generate a new Personal Access Token (PAT) with `repo` scope
- Make sure the PAT is from a GitHub user who has access to `Mittenzx/Adastrea`
- Update the `GAME_REPO_TOKEN` secret in GitHub repository settings

### 3. Wrong Token Being Used
The workflow uses `secrets.GAME_REPO_TOKEN`, but the test uses `os.environ.get("GITHUB_TOKEN")`.

**Current setup:**
```yaml
# In workflow:
env:
  GITHUB_TOKEN: ${{ secrets.GAME_REPO_TOKEN }}
```

This is correct - the workflow maps `GAME_REPO_TOKEN` to the `GITHUB_TOKEN` environment variable that the test reads.

### 4. Token Has Wrong Scope
The token may have been created with insufficient permissions.

**Required scopes:**
- `repo` (full control of private repositories)

**Solution:**
- Go to GitHub Settings → Developer Settings → Personal Access Tokens
- Generate a new token with the `repo` scope checked
- Update the `GAME_REPO_TOKEN` secret

## How to Fix

### Option 1: Create the Game Repository (Recommended)
If you plan to use this test with a real game repository:

1. Create a private repository at `https://github.com/Mittenzx/Adastrea`
2. Add some game documentation files to it
3. Generate a PAT with `repo` scope from a GitHub account that has access
4. Update the `GAME_REPO_TOKEN` secret in this repository's settings

### Option 2: Update the Test to Point to a Different Repository
If the game repository has a different name or location:

1. Edit `tests/test_game_repo_ingestion.py` line 30:
   ```python
   GAME_REPO_URL = "https://github.com/YOUR_ORG/YOUR_REPO.git"
   ```
2. Update line 31 as well:
   ```python
   GAME_REPO_NAME = "YOUR_REPO"
   ```

### Option 3: Skip the Integration Test (Temporary)
If you don't need the integration test yet:

1. The test already skips gracefully when it can't clone
2. This is the current behavior - the test skips but doesn't fail
3. Unit tests will still run and pass

## Verification

After making changes, you can verify the fix by:

1. Manually running the workflow:
   - Go to Actions → Test Game Repository Integration
   - Click "Run workflow"
   - Select "run_integration: true"

2. Check the logs for:
   - The detailed skip message (now visible with improved diagnostics)
   - Or success if the repository can be cloned

## Changes Made

This PR includes improved diagnostics:
- ✅ Detailed skip reasons are now printed to console
- ✅ Skip summaries are shown in pytest output (`-rs` flag)
- ✅ Actionable error messages explain what's needed

## Next Steps

1. Review this analysis
2. Determine which fix option applies to your situation
3. Implement the appropriate solution
4. Re-run the workflow to verify

## Questions?

If you need help:
- Check if `Mittenzx/Adastrea` exists and is accessible
- Verify the `GAME_REPO_TOKEN` secret has the correct permissions
- Review the workflow logs for the detailed error message
