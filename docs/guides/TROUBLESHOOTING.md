# Troubleshooting Guide

Quick reference for common installation and runtime issues with Adastrea Director.

**For comprehensive error handling documentation, see [ERROR_HANDLING.md](ERROR_HANDLING.md).**

## Installation Issues

### ❌ Error: `Could not find a version that satisfies the requirement onnxruntime`

**Common Causes**:
1. **Python version incompatibility** - Most common on Windows 11 x86_64
2. **Platform lacks pre-built wheels** - ARM systems (Apple Silicon, Linux ARM, Windows ARM)
3. **Network/proxy issues**

**Affected Platforms**:
- **Windows 11 (x86_64)** - Usually Python version issue (3.13+ not supported)
- Apple Silicon Macs (M1/M2/M3/M4)
- Linux ARM (Raspberry Pi, ARM servers)
- Windows ARM (Surface ARM devices)

**Quick Solutions**:

1. **Windows 11 x86_64 - Check Python version**:
   ```bash
   python --version
   # If 3.13+: Install Python 3.12 from python.org
   # If 3.12 or lower:
   python -m pip install --upgrade pip setuptools wheel
   pip install --verbose onnxruntime  # See detailed error
   ```

2. **Use the smart installer** (detects platform automatically):
   ```bash
   python install_dependencies.py
   ```

3. **Apple Silicon Macs - Use onnxruntime-silicon**:
   ```bash
   pip install numpy pandas langchain langchain-openai langchain-community openai
   pip install onnxruntime-silicon>=1.14.0
   pip install chromadb>=0.5.23
   pip install -r requirements.txt  # Install remaining packages
   ```

4. **Linux/Windows ARM - Build from source**:
   ```bash
   sudo apt-get install python3-dev build-essential cmake  # Linux only
   pip install --no-binary onnxruntime onnxruntime>=1.14.1
   pip install -r requirements.txt
   ```

5. **Any Platform - Use Docker**:
   ```bash
   docker pull chromadb/chroma
   docker run -p 8000:8000 chromadb/chroma
   # Then modify code to use remote ChromaDB (see INSTALLATION.md)
   ```

**For complete instructions**: See [INSTALLATION.md](INSTALLATION.md)

---

### ❌ Error: `numpy` version conflicts

**Cause**: Version incompatibility between numpy 2.0 and older packages.

**Solution**:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If using Python < 3.12, you may need to adjust numpy version constraints.

---

### ❌ Error: Import errors after successful installation

**Cause**: Virtual environment corruption or incomplete installation.

**Solution**:
```bash
deactivate  # If in a venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Runtime Issues

### ❌ Error: `OpenAI API key not found`

**Cause**: API key not configured.

**Solution**:

1. **Using environment variable**:
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```

2. **Using .env file**:
   ```bash
   echo "OPENAI_API_KEY=sk-your-key-here" > .env
   ```

3. **Using GUI**: The GUI will prompt you to enter your API key on first launch.

---

### ❌ Error: `No such collection` or `Database not found`

**Cause**: Vector database not initialized.

**Solution**: Ingest documents first:
```bash
python ingest.py --docs-dir /path/to/your/docs
```

---

## Document Ingestion Issues

### ❌ Error: `No module named 'unstructured'` when loading Markdown files

**Cause**: The `unstructured` package is an optional dependency for better Markdown parsing.

**Impact**: Markdown files will be loaded as plain text instead of parsed Markdown.

**Solutions**:

1. **Install the package** (recommended for better parsing):
   ```bash
   pip install unstructured
   ```

2. **Continue without it** - The system will automatically fall back to plain text loading.

**Note**: The fallback to TextLoader works well for most use cases. Only install `unstructured` if you need advanced Markdown parsing features.

---

### ❌ Error: `Error loading file` for specific .txt or .json files

**Cause**: Individual files may fail to load due to:
- Encoding issues (non-UTF-8 characters)
- File corruption
- Permission problems
- Malformed content

**Solution**: The ingestion system now continues loading other files even when some fail. Check the warning messages for specific file issues.

**To fix individual files**:

1. **Encoding issues**:
   ```bash
   # Convert to UTF-8
   iconv -f ISO-8859-1 -t UTF-8 problem_file.txt -o problem_file_utf8.txt
   ```

2. **Check file permissions**:
   ```bash
   chmod 644 problem_file.txt
   ```

3. **Validate JSON files**:
   ```bash
   python -m json.tool problem_file.json
   ```

---

### ❌ Error: `Error code: 429 - insufficient_quota` or `You exceeded your current quota`

**Cause**: OpenAI API rate limiting or quota exceeded. When ingesting large document sets (e.g., 6000+ files), you're making too many API calls too quickly, hitting OpenAI's rate limits (requests per minute).

**Built-in Solutions (Automatic)**:
- ✅ Rate limiting with delays between batches
- ✅ Automatic retry with exponential backoff
- ✅ Configurable delays and batch sizes

**Recommended Solutions**:

1. **Use delays between batches** (RECOMMENDED for large document sets):
   ```bash
   # For 1000-5000 chunks
   python ingest.py --docs-dir /path/to/docs --delay 2.0
   
   # For 5000+ chunks
   python ingest.py --docs-dir /path/to/docs --delay 3.0 --batch-size 50
   ```

2. **Use smaller batches with longer delays**:
   ```bash
   python ingest.py --docs-dir /path/to/docs --batch-size 50 --delay 2.0
   ```

3. **Check your billing** at [OpenAI Platform](https://platform.openai.com/account/billing):
   - Verify payment method is valid
   - Check current usage and limits
   - Add credits if needed

4. **Upgrade your plan**:
   - Free tier has very limited rate limits
   - Paid plans have higher requests-per-minute limits

5. **Process documents in smaller groups**:
   ```bash
   # Instead of entire directory, process subdirectories
   python ingest.py --docs-dir /path/to/docs/subset1 --delay 2.0
   python ingest.py --docs-dir /path/to/docs/subset2 --delay 2.0
   ```

**Understanding Rate Limits**:
- Rate limits are measured in **requests per minute (RPM)**, not total quota
- Each batch of documents makes 1 API call for embeddings
- Default: 100 chunks per batch = ~62 batches for 6000 chunks
- Without delays: hits rate limit quickly
- With delays: spreads requests over time, avoiding limits

**Example for 6000 chunks**:
```bash
# Good: 2 second delay between batches = ~2 minutes total
python ingest.py --docs-dir /path/to/docs --batch-size 100 --delay 2.0

# Better: Smaller batches with delays = more stable
python ingest.py --docs-dir /path/to/docs --batch-size 50 --delay 1.5
```

**Tip**: Start with a small test set to verify everything works before processing large collections.

---

### ❌ Error: `capture() takes 1 positional argument but 3 were given`

**Cause**: ChromaDB telemetry signature mismatch.

**Solution**: This is now automatically fixed - the ingestion system disables ChromaDB telemetry. If you still see this error, update to the latest version.

**Manual workaround** (if needed):
```bash
export ANONYMIZED_TELEMETRY=False
python ingest.py --docs-dir /path/to/docs
```

---

### ❌ Error: `sentence-transformers` download fails or is slow

**Cause**: Large model downloads on first run.

**Solutions**:

1. **Wait patiently** - models are ~400MB and download once
2. **Use a specific model**:
   ```bash
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```
3. **Pre-download models** before running the application

---

### ❌ Performance: Queries are slow

**Possible Causes & Solutions**:

1. **Large document collection**: Reduce chunk size or use more specific queries
2. **CPU-only inference**: Consider using GPU if available
3. **API rate limits**: Implement caching or use local models

---

## Platform-Specific Issues

### 🍎 macOS Issues

**Python not found or wrong version**:
```bash
# Install Python via Homebrew
brew install python@3.12

# For Apple Silicon with compatibility:
arch -x86_64 brew install python@3.12
```

**tkinter not found (for GUI)**:
```bash
brew install python-tk@3.12
```

---

### 🐧 Linux Issues

**tkinter not found (for GUI)**:
```bash
# Debian/Ubuntu
sudo apt-get install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter
```

**Build tools not found**:
```bash
sudo apt-get install python3-dev build-essential cmake
```

---

### 🪟 Windows Issues

**`python` command not found**:
- Use `python` or `python3` depending on your installation
- Ensure Python is in your PATH (check during installation)

**Virtual environment activation**:
```powershell
# PowerShell
venv\Scripts\Activate.ps1

# Command Prompt
venv\Scripts\activate.bat
```

**Long path names**: Enable long path support in Windows settings.

**Unicode/Emoji encoding errors** (cp1252 encoding issue):
- **Symptom**: `UnicodeEncodeError: 'charmap' codec can't encode character`
- **Cause**: Windows console using cp1252 encoding instead of UTF-8
- **Solution**: This is now fixed in the code (v1.1+). If you still encounter this:
  ```powershell
  # Set environment variable before running
  $env:PYTHONIOENCODING="utf-8"
  python ingest.py
  ```
- **Alternative**: Use Windows Terminal (instead of cmd.exe) which has better Unicode support

---

## Verification Commands

After installation, verify everything works:

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Run compatibility check
python check_compatibility.py

# Run validation
python validate_requirements.py

# Test imports
python -c "import numpy, pandas, langchain, chromadb; print('✅ All imports successful')"
```

---

## Getting More Help

1. **Check existing issues**: [GitHub Issues](https://github.com/Mittenzx/Adastrea-Director/issues)
2. **Review documentation**:
   - [README.md](README.md) - Quick start guide
   - [INSTALLATION.md](INSTALLATION.md) - Detailed installation instructions
   - [CONTRIBUTING.md](CONTRIBUTING.md) - Development setup
3. **Open a new issue**: Include:
   - Platform and Python version (`python --version`, `uname -m`)
   - Full error message
   - Output of `pip list`
   - What you've already tried

---

## Quick Reference

| Problem | Quick Fix | Details |
|---------|-----------|---------|
| onnxruntime not found | `python install_dependencies.py` | INSTALLATION.md |
| Apple Silicon issues | Use onnxruntime-silicon | INSTALLATION.md §2.1 |
| Import errors | Recreate virtual environment | See above |
| No API key | Set OPENAI_API_KEY | See above |
| No database | Run ingest.py first | See above |
| Slow queries | Optimize chunk size | See above |

---

**Last Updated**: 2025-11-09
