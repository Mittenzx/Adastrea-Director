# Troubleshooting Guide

Quick reference for common installation and runtime issues with Adastrea Director.

## Installation Issues

### ❌ Error: `Could not find a version that satisfies the requirement onnxruntime`

**Cause**: Your platform doesn't have pre-built onnxruntime wheels available.

**Affected Platforms**:
- Apple Silicon Macs (M1/M2/M3/M4)
- Linux ARM (Raspberry Pi, ARM servers)
- Windows ARM (Surface ARM devices)

**Quick Solutions**:

1. **Use the smart installer** (detects platform automatically):
   ```bash
   python install_dependencies.py
   ```

2. **Apple Silicon Macs - Use onnxruntime-silicon**:
   ```bash
   pip install numpy pandas langchain langchain-openai langchain-community openai
   pip install onnxruntime-silicon>=1.14.0
   pip install chromadb>=0.5.23
   pip install -r requirements.txt  # Install remaining packages
   ```

3. **Linux/Windows ARM - Build from source**:
   ```bash
   sudo apt-get install python3-dev build-essential cmake  # Linux only
   pip install --no-binary onnxruntime onnxruntime>=1.14.1
   pip install -r requirements.txt
   ```

4. **Any Platform - Use Docker**:
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
