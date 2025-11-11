# Setup Guide: GitHub Secrets for Game Repository Testing

This guide walks you through setting up GitHub secrets to enable full integration testing with the Mittenzx/Adastrea game repository.

## Prerequisites

You need:
1. Admin access to the Mittenzx/Adastrea-Director repository
2. Access to the Mittenzx/Adastrea repository (to generate token with correct permissions)
3. An OpenAI API account

---

## Step 1: Create GitHub Personal Access Token

### 1.1 Navigate to GitHub Token Settings

1. Go to your GitHub profile (top-right corner)
2. Click **Settings**
3. Scroll down and click **Developer settings** (left sidebar, near bottom)
4. Click **Personal access tokens**
5. Click **Tokens (classic)**

### 1.2 Generate New Token

1. Click **Generate new token** → **Generate new token (classic)**
2. Fill in the details:
   - **Note:** `Adastrea Director - Game Repo Access`
   - **Expiration:** Choose duration (90 days recommended, or No expiration)
   - **Select scopes:**
     - ✅ **repo** (Full control of private repositories)
       - This grants access to code, commit status, etc.

3. Scroll down and click **Generate token**
4. **IMPORTANT:** Copy the token immediately (starts with `ghp_`)
   - You won't be able to see it again!
   - Store it temporarily in a secure location

Example token format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## Step 2: Get OpenAI API Key

### 2.1 If You Already Have One

1. Go to https://platform.openai.com/api-keys
2. Find your existing key or create a new one
3. Copy the key (starts with `sk-`)

### 2.2 If You Need to Create One

1. Go to https://platform.openai.com/api-keys
2. Click **+ Create new secret key**
3. Name it: `Adastrea Director Testing`
4. Click **Create secret key**
5. **IMPORTANT:** Copy the key immediately
   - You won't be able to see it again!

Example key format: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## Step 3: Add Secrets to Repository

### 3.1 Navigate to Repository Secrets

1. Go to https://github.com/Mittenzx/Adastrea-Director
2. Click **Settings** tab (top navigation)
3. In the left sidebar, expand **Secrets and variables**
4. Click **Actions**

### 3.2 Add GAME_REPO_TOKEN Secret

1. Click **New repository secret**
2. Fill in:
   - **Name:** `GAME_REPO_TOKEN`
   - **Secret:** Paste the GitHub token you created (starts with `ghp_`)
3. Click **Add secret**

### 3.3 Add OPENAI_API_KEY Secret

1. Click **New repository secret** again
2. Fill in:
   - **Name:** `OPENAI_API_KEY`
   - **Secret:** Paste your OpenAI API key (starts with `sk-`)
3. Click **Add secret**

### 3.4 Verify Secrets Are Added

You should now see two secrets listed:
- ✅ GAME_REPO_TOKEN
- ✅ OPENAI_API_KEY

The values will be hidden (shown as `***`)

---

## Step 4: Update GitHub Actions Workflow (Optional)

If you want to run integration tests automatically in CI/CD, create or update `.github/workflows/test.yml`:

```yaml
name: Test Game Repository Integration

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:  # Allow manual trigger

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          
      - name: Run unit tests
        run: |
          pytest tests/test_game_repo_ingestion.py -v -m unit
          
      - name: Run integration tests
        if: github.event_name != 'pull_request'  # Only on main branch
        run: |
          pytest tests/test_game_repo_ingestion.py -v -m integration
        env:
          GITHUB_TOKEN: ${{ secrets.GAME_REPO_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

Save this file and commit it to enable automated testing.

---

## Step 5: Test the Setup

### 5.1 Test Locally (Optional)

Before running in GitHub Actions, you can test locally:

```bash
# Set the secrets as environment variables
export GITHUB_TOKEN="ghp_your_token_here"
export OPENAI_API_KEY="sk_your_key_here"

# Run integration tests
pytest tests/test_game_repo_ingestion.py -v -m integration
```

### 5.2 Test in GitHub Actions

**Option A: Via Pull Request**
1. The current PR should trigger tests automatically
2. Check the "Actions" tab to see test results

**Option B: Manual Trigger** (if workflow_dispatch is enabled)
1. Go to **Actions** tab
2. Select the workflow
3. Click **Run workflow**
4. Select branch: the branch you want to test (e.g., `main` or your feature branch)
5. Click **Run workflow**

### 5.3 Verify Test Results

1. Go to **Actions** tab
2. Click on the latest workflow run
3. Expand the test job
4. Look for:
   ```
   ✅ test_ingest_real_game_repo PASSED
   ```

---

## Step 6: Run Manual Integration Test

Once secrets are set up, you can also run the actual ingestion script:

```bash
# The script will automatically use GITHUB_TOKEN from environment
python ingest_game_repo.py
```

Or trigger it manually in a workflow:

```yaml
- name: Ingest Game Repository
  run: python ingest_game_repo.py
  env:
    GITHUB_TOKEN: ${{ secrets.GAME_REPO_TOKEN }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## Troubleshooting

### "Authentication failed" Error

**Problem:** Token doesn't have correct permissions

**Solution:**
1. Check token has `repo` scope
2. Regenerate token if expired
3. Update the GAME_REPO_TOKEN secret with new token

### "API key not found" Error

**Problem:** OpenAI key not set or invalid

**Solution:**
1. Verify key is active at https://platform.openai.com/api-keys
2. Update the OPENAI_API_KEY secret
3. Ensure you have billing set up on OpenAI account

### Secrets Not Available in Workflow

**Problem:** Secrets not accessible in pull requests from forks

**Solution:**
- Secrets are only available for pull requests from the same repository
- For security, GitHub doesn't expose secrets to forked PRs
- Run tests on branches in the main repository

### "Rate limit exceeded"

**Problem:** Too many API requests to OpenAI

**Solution:**
1. Use smaller batch sizes in `ingest_game_repo.py`
2. Add longer delays between batches
3. Wait a few minutes before retrying

---

## Security Best Practices

### ✅ DO

- ✅ Use repository secrets for sensitive data
- ✅ Set token expiration dates (90 days recommended)
- ✅ Use specific scopes (only `repo` needed)
- ✅ Rotate tokens periodically
- ✅ Delete tokens when no longer needed

### ❌ DON'T

- ❌ Never commit tokens to code
- ❌ Never share tokens in issues or comments
- ❌ Never use personal tokens with excessive permissions
- ❌ Never store tokens in environment files tracked by git

---

## Token Rotation Schedule

Recommended rotation schedule:

| Token Type | Rotation Frequency |
|-----------|-------------------|
| GitHub Personal Access Token | Every 90 days |
| OpenAI API Key | Annually or when compromised |

### How to Rotate

1. Generate new token/key
2. Update repository secret
3. Test that everything still works
4. Delete old token/key

---

## Quick Reference

### Secret Names
- `GAME_REPO_TOKEN` - GitHub Personal Access Token
- `OPENAI_API_KEY` - OpenAI API Key

### Required Scopes
- GitHub Token: `repo` (full control of private repositories)
- OpenAI Key: No special scopes, just valid API key

### Where to Add Secrets
Repository → Settings → Secrets and variables → Actions

### How to Use in Workflow
```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GAME_REPO_TOKEN }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## Next Steps After Setup

1. ✅ Secrets are configured
2. Run integration tests
3. Review test results in Actions tab
4. Set up automated daily ingestion (optional)
5. Configure monitoring and alerts (optional)

See [GAME_REPO_INGESTION.md](GAME_REPO_INGESTION.md) for details on automated ingestion setup.

---

## Support

If you encounter issues:

1. Check this troubleshooting guide
2. Review [GAME_REPO_TEST_RESULTS.md](GAME_REPO_TEST_RESULTS.md)
3. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. Open an issue with:
   - Error message (without exposing tokens!)
   - Steps to reproduce
   - Environment details

---

**Estimated Setup Time:** 10-15 minutes  
**Difficulty:** Easy  
**Prerequisites:** Admin access to repository

**Status:** Ready to implement Option 1
