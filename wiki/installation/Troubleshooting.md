# Troubleshooting

Common issues and solutions for Adastrea Director.

## 🔧 Common Installation Issues

### Python Version Issues

**Problem:** "Python 3.9 or higher required"

**Solution:**
```bash
# Check your Python version
python --version

# Install Python 3.12 (recommended)
# Visit https://www.python.org/downloads/
```

### Dependency Installation Failures

**Problem:** pip install fails

**Solution:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Use the smart installer
python install_dependencies.py

# Or try with verbose output
pip install -r requirements.txt -v
```

### tkinter Not Found

**Problem:** "No module named 'tkinter'"

**Solution:**

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

**macOS:**
```bash
brew install python-tk
```

**Windows:** Reinstall Python with tkinter option checked

## 🚀 Common Usage Issues

### API Key Issues

**Problem:** "API key not found" or "Invalid API key"

**Solution:**
```bash
# Set API key via CLI
python main.py --set-api-key gemini

# Or via environment variable
export GEMINI_KEY="your-key-here"

# Or via .env file
cp .env.example .env
# Edit .env and add your key
```

### Slow Performance

**Problem:** Queries take too long

**Solution:**
- First query is always slow (5-10s) - this is normal
- Check internet connection for cloud LLMs
- Consider using local Ollama for faster responses
- Use GPU if available

### No/Poor Results

**Problem:** "I don't have enough information" or poor answers

**Solution:**
```bash
# Ensure documents are ingested
python ingest.py --docs-dir /path/to/docs

# Check ingestion was successful
# Use GUI Ingest List tab to verify

# Try rephrasing your question
# Be more specific
```

## 🐛 Common Errors

### Import Errors

**Problem:** "ModuleNotFoundError"

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Errors

**Problem:** "ChromaDB error" or database corruption

**Solution:**
```bash
# Backup existing database
mv chroma_db chroma_db.backup

# Re-ingest documents
python ingest.py --docs-dir /path/to/docs
```

### GUI Won't Start

**Problem:** GUI application fails to start

**Solution:**
1. Check tkinter: `python -m tkinter`
2. Try CLI mode: `python main.py`
3. Check error logs
4. Reinstall dependencies

## 🔍 Debug Mode

Enable verbose logging for troubleshooting:

```bash
# Set debug mode
export DEBUG=1

# Run with verbose output
python main.py --verbose
```

## 📞 Getting More Help

If your issue isn't listed here:

1. **Search Issues:** [GitHub Issues](https://github.com/Mittenzx/Adastrea-Director/issues)
2. **Ask Community:** [Discussions](https://github.com/Mittenzx/Adastrea-Director/discussions)
3. **Report Bug:** [New Issue](https://github.com/Mittenzx/Adastrea-Director/issues/new)

Include in your report:
- OS and version
- Python version
- Error messages
- Steps to reproduce

---

[← Back to FAQ](FAQ.md) | [Installation Guide →](Getting-Started.md)
