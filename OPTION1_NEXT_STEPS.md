# Option 1: Next Steps - GitHub Secrets Setup

You've chosen **Option 1: Add GitHub Secrets** for enabling full integration testing.

## Quick Summary

I've created everything you need to set this up. Follow these steps:

---

## Step 1: Create GitHub Personal Access Token (5 minutes)

1. Go to https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Settings:
   - **Note:** `Adastrea Director - Game Repo Access`
   - **Expiration:** 90 days (or your preference)
   - **Scopes:** ✅ Check **repo** (Full control of private repositories)
4. Click **Generate token**
5. **Copy the token** (starts with `ghp_`)
   - ⚠️ You won't be able to see it again!

---

## Step 2: Get OpenAI API Key (2 minutes)

1. Go to https://platform.openai.com/api-keys
2. Find your existing key OR click **+ Create new secret key**
3. **Copy the key** (starts with `sk-` or `sk-proj-`)
   - ⚠️ You won't be able to see it again if creating new!

---

## Step 3: Add Secrets to Repository (3 minutes)

1. Go to https://github.com/Mittenzx/Adastrea-Director/settings/secrets/actions
2. Click **New repository secret**
3. Add first secret:
   - **Name:** `GAME_REPO_TOKEN`
   - **Secret:** Paste your GitHub token (the `ghp_` one)
   - Click **Add secret**
4. Click **New repository secret** again
5. Add second secret:
   - **Name:** `OPENAI_API_KEY`
   - **Secret:** Paste your OpenAI key (the `sk-` one)
   - Click **Add secret**

✅ You should now see two secrets listed (values will be hidden as `***`)

---

## Step 4: Run the Tests (Automatic!)

Once secrets are added, the tests will automatically run:

### Automatic Trigger
- The GitHub Actions workflow will run automatically on your next push
- Check the **Actions** tab to see results

### Manual Trigger
1. Go to https://github.com/Mittenzx/Adastrea-Director/actions
2. Click **Test Game Repository Integration** workflow
3. Click **Run workflow**
4. Select branch: the branch you want to test (e.g., `main` or your feature branch)
5. Click **Run workflow**

---

## What Will Happen

Once secrets are configured, the workflow will:

1. ✅ Run 11 unit tests (already passing)
2. ✅ Run integration test with real Mittenzx/Adastrea repository
   - Clone the repository
   - Load all documents
   - Create embeddings
   - Store in database
   - Verify everything works
3. ✅ Test script functionality
4. ✅ Display comprehensive results

Expected output:
```
✅ Unit Tests: 11/11 passed
✅ Integration Tests: 1/1 passed
✅ Script Tests: 2/2 passed
```

---

## Verification

After running, you can verify:

1. **Check Actions Tab:**
   - Go to https://github.com/Mittenzx/Adastrea-Director/actions
   - Latest run should show all green checkmarks ✅

2. **Check Test Output:**
   - Click on the workflow run
   - Expand "Integration Tests" job
   - Look for `test_ingest_real_game_repo PASSED`

3. **Local Testing (Optional):**
   ```bash
   export GITHUB_TOKEN="ghp_your_token"
   export OPENAI_API_KEY="sk_your_key"
   pytest tests/test_game_repo_ingestion.py -v -m integration
   ```

---

## Troubleshooting

### "Secrets not configured" message
- Double-check secret names are exactly: `GAME_REPO_TOKEN` and `OPENAI_API_KEY`
- Verify you added them to the correct repository (Adastrea-Director)
- Try re-running the workflow

### "Authentication failed" error
- Token might not have `repo` scope
- Token might be expired
- Regenerate token and update the secret

### "API key not found" error
- Verify OpenAI key is active at https://platform.openai.com/api-keys
- Check billing is set up on OpenAI account
- Update the secret with correct key

---

## Files to Reference

- **SETUP_GITHUB_SECRETS.md** - Detailed step-by-step guide with screenshots guidance
- **GAME_REPO_TEST_RESULTS.md** - Current test results and what will be tested
- **.github/workflows/test-game-repo-integration.yml** - The workflow that runs tests

---

## Security Notes

✅ **Safe:**
- Secrets are encrypted by GitHub
- Only accessible to workflows in this repository
- Not exposed in logs or to external PRs

❌ **Never:**
- Commit tokens to code
- Share tokens in comments
- Use tokens with excessive permissions

---

## Time Estimate

- **Step 1:** 5 minutes (Create GitHub token)
- **Step 2:** 2 minutes (Get OpenAI key)
- **Step 3:** 3 minutes (Add secrets)
- **Step 4:** Automatic (workflow runs on its own)

**Total:** ~10 minutes of your time

---

## What Happens Next

1. You add the secrets (10 minutes)
2. Workflow runs automatically
3. Integration tests pass ✅
4. You can review results in Actions tab
5. Future changes will automatically run full test suite
6. You can set up automated daily ingestion (optional)

---

## Need Help?

If you encounter issues:

1. Check **Troubleshooting** section above
2. Review **SETUP_GITHUB_SECRETS.md** for detailed guidance
3. Check **GAME_REPO_TEST_RESULTS.md** for expected behavior
4. Comment on the PR with specific error messages

---

## Ready to Start?

📖 **Detailed Guide:** [SETUP_GITHUB_SECRETS.md](SETUP_GITHUB_SECRETS.md)

🚀 **Quick Start:**
1. Create token: https://github.com/settings/tokens
2. Get API key: https://platform.openai.com/api-keys
3. Add secrets: https://github.com/Mittenzx/Adastrea-Director/settings/secrets/actions
4. Watch tests run: https://github.com/Mittenzx/Adastrea-Director/actions

**Current Status:** ⏳ Waiting for secrets to be added  
**Once Complete:** ✅ Full integration testing enabled
