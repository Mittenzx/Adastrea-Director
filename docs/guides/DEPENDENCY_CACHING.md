# Dependency Caching Guide

This guide explains how dependency caching works in Adastrea Director to speed up development and CI/CD workflows.

## Problem

Installing Python dependencies from `requirements.txt` can take 2-3 minutes, which slows down:
- Running quick tests during development
- GitHub Actions CI/CD pipelines
- Agent work that requires frequent environment setup

## Solution

We use caching at two levels:

### 1. GitHub Actions Caching (CI/CD)

The GitHub Actions workflow now caches pip's download cache, significantly speeding up subsequent runs.

#### How It Works

```yaml
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

- **Cache Key**: Based on OS and `requirements.txt` hash
- **Cache Path**: `~/.cache/pip` (pip's download cache)
- **Restore Keys**: Allow partial matches when requirements change slightly

#### Performance Impact

- **First run** (cache miss): ~3 minutes
- **Subsequent runs** (cache hit): ~10-30 seconds
- **Speedup**: ~10x faster

#### Cache Behavior

- Cache is **automatically created** after first successful install
- Cache is **invalidated** when `requirements.txt` changes
- Cache is **shared** across workflow runs on the same branch
- Cache **expires** after 7 days of inactivity (GitHub default)

### 2. Local Development (Virtual Environments)

For local development, the most effective caching strategy is to **reuse your virtual environment**.

#### Best Practices

1. **Create a virtual environment once:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies once:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Reuse the environment for all work:**
   ```bash
   # Every time you start work:
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   
   # Now run your commands:
   python main.py
   pytest
   ```

4. **Only reinstall when requirements change:**
   ```bash
   # After git pull, if requirements.txt changed:
   pip install -r requirements.txt
   ```

#### Why Virtual Environments?

- **Fast**: No installation needed after initial setup
- **Isolated**: Project dependencies don't affect other projects
- **Persistent**: Environment survives between sessions
- **Standard**: Recommended Python practice

#### Setup Script

The `setup.sh` script creates and activates a virtual environment:

```bash
./setup.sh
```

This script:
1. Creates `venv/` directory
2. Installs all dependencies
3. Verifies installation
4. Provides next steps

#### Quickstart (Recommended Workflow)

```bash
# Initial setup (once):
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director
./setup.sh

# Daily workflow:
cd Adastrea-Director
source venv/bin/activate
# ... do your work ...
deactivate  # when done
```

## Checking Cache Status

### GitHub Actions

View cache status in GitHub:
1. Go to repository → Actions → Caches
2. Or check workflow logs for "Cache restored" messages

### Local Development

Check if you're in a virtual environment:
```bash
which python
# Should show: /path/to/Adastrea-Director/venv/bin/python
```

Check installed packages:
```bash
pip list
```

## Troubleshooting

### GitHub Actions: Cache Not Working

**Symptom**: Every run takes 3 minutes

**Solutions**:
1. Check if cache key changed (e.g., requirements.txt modified)
2. Cache may have been evicted (7-day expiry)
3. Check workflow logs for "Cache not found" vs "Cache restored"
4. Clear old caches: Settings → Actions → Caches → Delete

### Local: "Module not found" Errors

**Symptom**: `ImportError: No module named 'X'`

**Solutions**:
1. Verify virtual environment is activated:
   ```bash
   which python  # Should show venv path
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Check Python version:
   ```bash
   python --version  # Should be 3.9+
   ```

### Platform-Specific Issues

See [INSTALLATION.md](INSTALLATION.md) for:
- Apple Silicon (M1/M2/M3/M4) specific instructions
- ARM Linux/Windows workarounds
- Python 3.13+ compatibility notes

## Advanced: pip Cache Location

pip caches downloaded packages to avoid re-downloading:

**Default locations:**
- Linux: `~/.cache/pip`
- macOS: `~/Library/Caches/pip`
- Windows: `%LocalAppData%\pip\Cache`

You can clear pip's cache if needed:
```bash
pip cache purge
```

## Cost-Benefit Analysis

### Without Caching (Original)
- **Setup time**: 3 minutes every run
- **Developer experience**: Slow iteration
- **CI/CD time**: ~10 minutes for 3 jobs

### With Caching (New)
- **First run**: 3 minutes (same)
- **Cached runs**: ~30 seconds
- **CI/CD time**: ~2-3 minutes for 3 jobs
- **Speedup**: 3-4x faster overall

## Additional Resources

- [GitHub Actions Cache Documentation](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [pip Caching Documentation](https://pip.pypa.io/en/stable/topics/caching/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

## Summary

| Method | Setup Time | Best For |
|--------|------------|----------|
| **Virtual environment** (local) | 3 min once, then instant | Development |
| **pip cache** (GitHub Actions) | 3 min first, 30s after | CI/CD |
| **No caching** (old way) | 3 min every time | Not recommended |

**Recommendation**: Use virtual environments for local development and rely on GitHub Actions caching for CI/CD. This provides the best developer experience with minimal setup overhead.

---

**Last Updated**: 2025-11-12
