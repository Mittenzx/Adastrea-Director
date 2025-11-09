# Troubleshooting Guide

Quick reference for common installation and runtime issues with Adastrea Director.

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

### ❌ Error: Python 3.13+ Compatibility Issues

**Symptoms**:
- GUI shows warning: "Python 3.13+ is not yet fully supported"
- `onnxruntime` installation fails on Python 3.13+
- GUI fails to start with errors at line 964

**Cause**: Python 3.13+ introduces changes that make it incompatible with `onnxruntime`, which is required by ChromaDB (the vector database).

**Solution**: Use Python 3.9 through 3.12 (Python 3.12 recommended)

**Option 1: Install Python 3.12 (Recommended)**
1. Download Python 3.12 from [python.org](https://www.python.org/downloads/)
2. Install it (you can have multiple Python versions)
3. Create a new virtual environment with Python 3.12:
   ```bash
   # Windows
   py -3.12 -m venv venv
   venv\Scripts\activate
   
   # Linux/macOS
   python3.12 -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

**Option 2: Use pyenv (Linux/macOS)**
```bash
# Install pyenv (if not already installed)
curl https://pyenv.run | bash

# Install Python 3.12
pyenv install 3.12.7
pyenv local 3.12.7

# Create virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Option 3: Use Docker**
If you prefer to keep Python 3.13+, you can run ChromaDB in Docker:
```bash
docker pull chromadb/chroma
docker run -p 8000:8000 chromadb/chroma
# Then modify code to use remote ChromaDB (see INSTALLATION.md)
```

**Verify Your Python Version**:
```bash
python --version
# Should show 3.9.x through 3.12.x
```

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

### ❌ Error: `tkinter is not available` (GUI only)

**Symptoms**:
- Error message: "ERROR: tkinter is not available"
- Cannot start `gui_director.py`
- Import error: "No module named 'tkinter'"

**Cause**: tkinter (Python's built-in GUI library) is not installed.

**Solutions by Platform**:

**Windows**:
- tkinter should be included with Python from python.org
- If missing, reinstall Python and ensure "tcl/tk and IDLE" is checked in the installer
- Download from: https://www.python.org/downloads/

**Ubuntu/Debian Linux**:
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

**Fedora/RHEL Linux**:
```bash
sudo dnf install python3-tkinter
```

**macOS**:
- tkinter is included with Python from python.org
- If using Homebrew Python:
  ```bash
  brew install python-tk@3.12  # Replace 3.12 with your Python version
  ```

**Verify tkinter installation**:
```bash
python -c "import tkinter; print('✅ tkinter is available')"
```

**Alternative**: If you can't install tkinter, use the command-line interface instead:
```bash
python main.py
```

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
