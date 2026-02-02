# Adastrea Director - Troubleshooting Guide

> Comprehensive guide to diagnose and fix common issues

## 🎯 Quick Diagnostics

### First Steps (Do This First!)

1. **Test API Keys and Dependencies**
   ```bash
   # ⚠️  IMPORTANT: Run this from a system terminal/command prompt,
   # NOT from Unreal Engine's Python console!
   
   # Run the comprehensive diagnostic script
   python test_api_keys.py
   
   # Test specific provider
   python test_api_keys.py --provider gemini
   
   # Check configuration only (no API calls)
   python test_api_keys.py --skip-api-test
   ```
   
   **Note**: If you accidentally run this from UE's Python console, you'll see
   "Dependencies NOT INSTALLED" errors. This is expected! The plugin doesn't
   require these dependencies in UE's Python environment. Run the script from
   your system terminal instead.
   
   This script will check:
   - All required dependencies are installed
   - API keys are properly configured
   - API keys can authenticate with their services
   - Which configuration source is being used (.env, environment, config file)

2. **Check the Dashboard**
   - Open the Dashboard tab in the plugin panel
   - Review all 6 status indicators
   - Note which ones are red or yellow

3. **Verify Installation**
   ```bash
   # Check Python version
   python --version  # Should be 3.9+
   
   # Check dependencies
   pip list | grep -E "(chromadb|langchain|openai)"
   
   # Check plugin loaded
   # In UE: Edit → Plugins → Search "Adastrea"
   ```

4. **Check Logs**
   ```bash
   # Plugin logs
   tail -f Plugins/AdastreaDirector/Python/logs/ipc_server.log
   
   # Standalone logs
   tail -f logs/adastrea_director.log
   
   # UE Editor logs
   tail -f Saved/Logs/MyProject.log
   ```

## 🔴 Critical Issues

### "Dependencies NOT INSTALLED" Error in UE Python Console

**Symptoms:**
- Running `test_api_keys.py` from Unreal Engine's Python console shows:
  ```
  LogPython:   ✗ python-dotenv NOT INSTALLED
  LogPython:   ✗ langchain NOT INSTALLED
  LogPython:   ✗ chromadb NOT INSTALLED
  ```
- Path shows UE installation directory (e.g., `C:\Program Files\Epic Games\UE_5.6\`)

**Cause:**
You're running the test script from inside Unreal Engine's Python environment instead
of your system Python environment.

**Solution:**
This is **expected behavior** and **not an error**! The Adastrea Director plugin does NOT
require LangChain dependencies to be installed in UE's Python environment.

1. **Close UE's Python console**
2. **Open a system terminal/command prompt** (Windows: cmd.exe or PowerShell, Mac/Linux: Terminal)
3. **Navigate to your repository:**
   ```bash
   cd path/to/Adastrea-Director
   ```
4. **Run the test from there:**
   ```bash
   python test_api_keys.py
   ```

**Why this happens:**
- The plugin uses UE's built-in Python for in-editor operations only
- LLM functionality runs through a separate IPC server using your system Python
- Only the system Python needs the LangChain dependencies installed
- If you run `test_api_keys.py` from UE Python, it will now detect this and show
  helpful guidance instead of failing

**Updated behavior (v1.x+):**
The script now detects when running in UE's Python and displays:
- ⚠️  WARNING at the top
- ✅ "This is EXPECTED behavior" message  
- Clear instructions on proper usage
- Returns success (exit code 0) instead of failure

### API Key Not Working

**Symptoms:**
- "API key not configured" errors
- Authentication failures
- System asking to install dependencies even though they're installed

**Diagnosis:**
```bash
# ⚠️  Run from system terminal, NOT UE Python console
# Run comprehensive API key test
python test_api_keys.py --verbose

# This will show:
# - Which API key sources are checked
# - Which key is actually being used
# - Whether the key authenticates successfully
```

**Solutions:**

1. **Check API key configuration:**
   ```bash
   # View current configuration
   python test_api_keys.py --skip-api-test
   ```

2. **Set API key via environment variable:**
   ```bash
   export GEMINI_API_KEY="your-key-here"
   # or
   export OPENAI_API_KEY="your-key-here"
   ```

3. **Set API key via .env file:**
   ```bash
   cp .env.example .env
   # Edit .env and add your key
   nano .env  # or use your preferred editor
   ```

4. **Set API key via config file:**
   ```bash
   python main.py --set-api-key gemini
   ```

5. **Check for whitespace:**
   API keys should not have leading or trailing spaces. The test script will detect this.

6. **Verify key is valid:**
   - Gemini: https://makersuite.google.com/app/apikey
   - OpenAI: https://platform.openai.com/api-keys
   - OpenRouter: https://openrouter.ai/keys

### Plugin Panel Empty or Not Loading

**Symptoms:**
- Panel opens but shows nothing
- Panel immediately closes
- "Failed to load" error message

**Diagnosis:**
```bash
# Check if Python backend started
ps aux | grep python | grep ipc_server

# Check port availability
netstat -an | grep 5555

# Check plugin files exist
ls -la Plugins/AdastreaDirector/Python/
```

**Solutions:**

1. **Python Backend Not Starting**
   ```bash
   # Try manual start
   cd Plugins/AdastreaDirector/Python
   python ipc_server.py
   
   # Check for errors in output
   # If errors, install dependencies:
   pip install -r requirements.txt
   ```

2. **Port Already in Use**
   ```bash
   # Find process using port
   lsof -i :5555  # Mac/Linux
   netstat -ano | findstr :5555  # Windows
   
   # Kill process or change port in settings
   ```

3. **Missing Dependencies**
   ```bash
   # Reinstall dependencies
   cd Plugins/AdastreaDirector/Python
   pip install -r requirements.txt --force-reinstall
   ```

4. **Permissions Issue**
   ```bash
   # Fix permissions (Linux/Mac)
   chmod +x Plugins/AdastreaDirector/Python/ipc_server.py
   
   # Check write permissions for logs
   ls -la Plugins/AdastreaDirector/Python/logs/
   ```

### Connection Failed / Cannot Connect to Backend

**Symptoms:**
- 🔴 IPC Connection indicator red
- "Connection failed" errors
- Queries timeout

**Diagnosis:**
```bash
# Test IPC server manually
curl http://localhost:5555/health

# Check firewall
# Windows: Check Windows Defender Firewall
# Mac: System Preferences → Security & Privacy → Firewall
# Linux: sudo ufw status
```

**Solutions:**

1. **Firewall Blocking**
   - **Windows**: Add exception for Python.exe
   - **Mac**: System Preferences → Security → Allow Python
   - **Linux**: `sudo ufw allow 5555`

2. **Python Process Crashed**
   ```bash
   # Check if process exists
   ps aux | grep ipc_server
   
   # Restart Unreal Engine Editor
   # Backend will auto-start on next panel open
   ```

3. **Port Configuration Mismatch**
   - Check Settings dialog → Advanced → IPC Port
   - Ensure it matches backend configuration
   - Default should be 5555

4. **Network Interface Issue**
   ```bash
   # Test localhost connectivity
   ping localhost
   
   # Try alternative loopback
   # Edit ipc_server.py: change 'localhost' to '127.0.0.1'
   ```

### API Key Issues

**Symptoms:**
- 🔴 LLM Provider indicator red
- "Invalid API key" errors
- "Authentication failed" messages

**Diagnosis:**
```bash
# Check if key is set
python -c "from config_manager import ConfigManager; cm = ConfigManager(); print(cm.get_api_key('gemini'))"

# Test key manually (Gemini)
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
  "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=YOUR_KEY"
```

**Solutions:**

1. **Key Not Set**
   ```bash
   # Via CLI
   python main.py --set-api-key gemini
   
   # Via GUI
   # Settings → API Key Management → Enter key
   ```

2. **Key Invalid or Expired**
   - Get new key from Google AI Studio or OpenAI
   - Delete old key from config
   - Set new key via Settings

3. **Key Quota Exceeded**
   - Check your API usage dashboard
   - Gemini: https://makersuite.google.com/
   - OpenAI: https://platform.openai.com/usage
   - Wait for quota reset or upgrade plan

4. **Wrong Provider Selected**
   - Check Settings → LLM Provider matches your key type
   - Gemini key won't work with OpenAI provider setting

### Missing LLM Dependencies

**Symptoms:**
- "LLM fails each time" errors in UE logs
- "ModuleNotFoundError: No module named 'langchain_google_genai'" errors
- "Missing required dependencies for Gemini/OpenAI LLM provider" messages
- LLM queries fail immediately without processing

**Diagnosis:**
```bash
# Check if dependencies are installed
python -c "from llm_config import check_dependencies_available; available, msg = check_dependencies_available(); print('Available:', available); print(msg if not available else 'All dependencies OK')"

# Check specific packages
pip list | grep -E "(langchain|google-genai|openai)"
```

**Solutions:**

1. **Install All Dependencies (Recommended)**
   ```bash
   # Navigate to repository root
   cd /path/to/Adastrea-Director
   
   # Install all requirements
   pip install -r requirements.txt
   
   # Restart Unreal Engine Editor
   ```

2. **Install Specific LLM Provider Package**
   ```bash
   # For Gemini (default)
   pip install langchain-google-genai>=2.0.5
   
   # For OpenAI (if using LLM_PROVIDER=openai)
   pip install langchain-openai>=0.3.0
   ```

3. **Virtual Environment Issues**
   ```bash
   # If using a virtual environment, ensure it's activated
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   
   # Then install dependencies
   pip install -r requirements.txt
   ```

4. **Python Environment Mismatch**
   - Ensure UE is using the same Python environment where dependencies are installed
   - Check Python path in plugin settings
   - If using system Python, install dependencies system-wide
   - If using a virtual environment, configure UE to use that environment's Python

**Note:** After installing dependencies, always restart Unreal Engine Editor for changes to take effect.

## 🟡 Warning Issues

### Knowledge Base Empty or Not Loading

**Symptoms:**
- 🟡 Knowledge Base indicator yellow/red
- "No documents found" message
- Poor quality responses

**Diagnosis:**
```bash
# Check database exists
ls -la ./chroma_db/

# Check document count
python -c "from rag_agent import RAGAgent; agent = RAGAgent(); print(agent.get_stats())"

# Check ingestion logs
tail -f logs/ingestion.log
```

**Solutions:**

1. **No Documents Ingested Yet**
   ```bash
   # Ingest documentation
   python ingest.py --docs-dir /path/to/docs
   
   # Or use Ingestion tab in plugin
   ```

2. **Database Corrupted**
   ```bash
   # Backup and recreate
   mv chroma_db chroma_db.backup
   python ingest.py --docs-dir /path/to/docs
   ```

3. **Permissions Issue**
   ```bash
   # Check permissions
   ls -la chroma_db/
   
   # Fix if needed
   chmod -R u+rw chroma_db/
   ```

4. **Documents Not in Supported Format**
   - Supported: .md, .txt, .rst, .py, .cpp, .h, .json
   - Check file extensions
   - Convert unsupported formats to Markdown

### Slow Performance / Long Query Times

**Symptoms:**
- Queries take > 10 seconds
- UI feels sluggish
- High CPU/RAM usage

**Diagnosis:**
```bash
# Check system resources
top  # Linux/Mac
# Task Manager → Performance tab (Windows)

# Check database size
du -sh chroma_db/

# Check document count
# Should be < 10,000 for optimal performance
```

**Solutions:**

1. **Too Many Documents**
   ```bash
   # Clear and re-ingest selectively
   rm -rf chroma_db/
   python ingest.py --docs-dir /path/to/essential/docs/only
   ```

2. **Large Documents**
   - Break large files into smaller chunks
   - Remove unnecessary sections
   - Focus on relevant documentation

3. **Resource Constraints**
   - Close unnecessary applications
   - Increase system RAM if possible
   - Use more powerful LLM provider (e.g., OpenAI GPT-4)

4. **Network Issues**
   - Check internet speed
   - Test API latency: `ping generativelanguage.googleapis.com`
   - Consider local LLM solutions for offline use

### Director Only Shows "Thinking..." Then Stops

**Symptoms:**
- Query is sent successfully
- UI shows "Thinking..." status
- Response never appears or is empty
- No error messages shown
- Particularly occurs with Gemini 2.0 models

**Cause:**
This issue was caused by incomplete parsing of Gemini API responses. When using Gemini models with extended thinking capabilities (like gemini-2.0-flash-thinking), the API returns response parts with a "thought" field containing the reasoning process, in addition to or instead of the regular "text" field. Previous versions only extracted "text" fields, causing thinking-only responses to be ignored.

**Fixed In:** v1.1+ (January 2026)

**Solution:**

1. **Update to Latest Version**
   - The fix is included in v1.1 and later
   - Update your plugin to the latest version
   - The LLM client now properly extracts both "text" and "thought" fields from responses

2. **Check Logs for Detailed Information**
   ```bash
   # Check UE Editor logs for response parsing details
   tail -f Saved/Logs/MyProject.log | grep AdastreaDirector
   
   # Look for messages like:
   # "Processing N parts in Gemini response"
   # "Total content extracted: X chars, Y tool calls"
   ```
   
   **For verbose per-part diagnostics**, enable verbose logging:
   ```bash
   # Add to your project's DefaultEngine.ini or ConsoleVariables.ini:
   [Core.Log]
   LogAdastreaDirector=Verbose
   
   # Then look for detailed part-level messages:
   # "Part N: Found text field (X chars)"
   # "Part N: Found thought field (X chars)"
   ```

3. **Verify API Configuration**
   - Ensure your Gemini API key is valid
   - Check that the model name is correct in settings
   - Supported models: gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash, gemini-2.0-flash-thinking

4. **Enable Verbose Logging** (if issue persists)
   - The updated LLM client includes detailed logging
   - Check logs for warnings about unrecognized response fields
   - Report any unrecognized field names as they may indicate new API features

**Technical Details:**
The fix modifies `AdastreaLLMClient.cpp` to:
- Check for both "text" and "thought" fields in Gemini response parts
- Use thinking content as a fallback when no text is available
- Log detailed information about each part being processed
- Warn when parts contain unrecognized fields (fields beyond text/thought/functionCall)

### Ingestion Fails or Hangs

**Symptoms:**
- Progress bar stuck at X%
- "Ingestion failed" error
- Specific files causing errors

**Diagnosis:**
```bash
# Check logs for specific errors
tail -f logs/ingestion.log

# Test file manually
python -c "
from langchain_community.document_loaders import TextLoader
loader = TextLoader('/path/to/problem/file.md')
docs = loader.load()
print(f'Loaded {len(docs)} docs')
"
```

**Solutions:**

1. **File Encoding Issues**
   ```bash
   # Check file encoding
   file /path/to/file.md
   
   # Convert to UTF-8 if needed
   iconv -f ISO-8859-1 -t UTF-8 file.md > file_utf8.md
   ```

2. **File Permission Issues**
   ```bash
   # Check permissions
   ls -la /path/to/docs/
   
   # Fix if needed
   chmod -R a+r /path/to/docs/
   ```

3. **File Too Large**
   - Split large files (> 10 MB) into smaller parts
   - Remove binary content if accidentally included
   - Focus ingestion on text documentation only

4. **Specific File Format Issue**
   - Skip problematic files temporarily
   - Convert to plain text or Markdown
   - Report issue on GitHub with file example

## ⚙️ Configuration Issues

### Settings Not Saving

**Symptoms:**
- Settings revert after restart
- API key needs to be re-entered
- Configuration changes lost

**Diagnosis:**
```bash
# Check config file location
ls -la ~/.adastrea/config.json

# Check file permissions
ls -la ~/.adastrea/

# Check file contents
cat ~/.adastrea/config.json
```

**Solutions:**

1. **Permission Denied**
   ```bash
   # Create directory if missing
   mkdir -p ~/.adastrea
   
   # Fix permissions
   chmod u+rw ~/.adastrea/config.json
   ```

2. **Config File Corrupted**
   ```bash
   # Backup and reset
   mv ~/.adastrea/config.json ~/.adastrea/config.json.backup
   
   # Reconfigure via Settings dialog
   ```

3. **Using Environment Variables Instead**
   - If `GEMINI_KEY` or `OPENAI_API_KEY` env var is set
   - It overrides saved config
   - Either unset env var or uncheck "Use environment variable"

### Python Path Issues

**Symptoms:**
- "Python not found" errors
- "Module not found" errors
- Backend fails to start

**Diagnosis:**
```bash
# Find Python
which python3  # Linux/Mac
where python  # Windows

# Check version
python3 --version

# Check sys.path
python3 -c "import sys; print('\n'.join(sys.path))"
```

**Solutions:**

1. **Python Not in PATH**
   ```bash
   # Add to PATH (Linux/Mac)
   export PATH="/usr/local/bin:$PATH"
   
   # Or specify full path in Settings
   # Settings → Advanced → Python Path → /full/path/to/python3
   ```

2. **Multiple Python Versions**
   ```bash
   # Use specific version
   python3.12 --version
   
   # Update Settings to use specific version
   # Settings → Advanced → Python Path → python3.12
   ```

3. **Virtual Environment Issues**
   ```bash
   # Activate venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   
   # Install dependencies in venv
   pip install -r requirements.txt
   
   # Update Settings to use venv Python
   ```

## 🔧 Platform-Specific Issues

### Windows

**Issue: Python Scripts Not Executable**
```bash
# Solution: Use 'python' instead of 'python3'
python main.py

# Or add .py to PATHEXT
set PATHEXT=%PATHEXT%;.PY
```

**Issue: Antivirus Blocking Python**
- Add Python.exe to antivirus exceptions
- Add Plugins folder to exceptions
- Temporarily disable to test

**Issue: Long Path Names**
- Enable long path support in Windows
- Or move project closer to drive root

### macOS

**Issue: Gatekeeper Blocking**
```bash
# Allow Python to run
xattr -d com.apple.quarantine Plugins/AdastreaDirector/Python/ipc_server.py

# Or in System Preferences
# Security & Privacy → Allow apps downloaded from: App Store and identified developers
```

**Issue: SSL Certificate Errors**
```bash
# Install certificates
/Applications/Python\ 3.x/Install\ Certificates.command
```

**Issue: Apple Silicon (M1/M2) Compatibility**
```bash
# Use Python 3.9+ with ARM support
arch -arm64 python3 --version

# Install ARM-compatible dependencies
arch -arm64 pip install -r requirements.txt
```

### Linux

**Issue: tkinter Not Installed**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

**Issue: Permission Denied**
```bash
# Don't use sudo with pip
pip install --user -r requirements.txt

# Fix ownership if needed
sudo chown -R $USER:$USER ~/.adastrea
```

**Issue: Missing System Libraries**
```bash
# Install build tools
sudo apt-get install build-essential python3-dev

# Install system dependencies
sudo apt-get install libssl-dev libffi-dev
```

## 🐛 Bug Reporting

### Information to Include

When reporting bugs, please provide:

1. **System Information**
   ```bash
   # Run this and include output
   python --version
   uname -a  # Linux/Mac
   systeminfo | findstr /B /C:"OS"  # Windows
   ```

2. **Plugin Version**
   - Check Plugins/AdastreaDirector/AdastreaDirector.uplugin
   - Look for "VersionName"

3. **Error Messages**
   - Full error text from logs
   - Screenshot of error dialog
   - Stack trace if available

4. **Steps to Reproduce**
   - What you did before the error
   - What you expected to happen
   - What actually happened

5. **Logs**
   ```bash
   # Collect relevant logs
   # Plugin log
   cat Plugins/AdastreaDirector/Python/logs/ipc_server.log
   
   # Standalone log
   cat logs/adastrea_director.log
   
   # UE log (last 100 lines)
   tail -100 Saved/Logs/MyProject.log
   ```

### Where to Report

- **GitHub Issues**: https://github.com/Mittenzx/Adastrea-Director/issues
- **Search existing issues first** before creating new one
- **Use issue template** if available
- **Add appropriate labels** (bug, enhancement, question)

## 🔍 Advanced Diagnostics

### Enable Debug Logging

```bash
# Standalone
python main.py --debug

# Plugin: Edit ipc_server.py
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

```bash
# Test RAG system
python -c "
from rag_agent import RAGAgent
agent = RAGAgent()
result = agent.query('test question')
print(result)
"

# Test LLM connection
python -c "
from llm_config import get_llm
llm = get_llm()
response = llm.invoke('Hello')
print(response)
"

# Test database
python -c "
import chromadb
client = chromadb.PersistentClient(path='./chroma_db')
collections = client.list_collections()
print(f'Collections: {len(collections)}')
"
```

### Performance Profiling

```bash
# Profile Python backend
python -m cProfile -o profile.stats ipc_server.py

# Analyze results
python -m pstats profile.stats
# Then: sort cumulative, stats 20

# Monitor resource usage
# Linux: htop
# Mac: Activity Monitor
# Windows: Task Manager → Performance
```

### Network Diagnostics

```bash
# Test API connectivity
curl -I https://generativelanguage.googleapis.com

# Test local IPC
curl -X POST http://localhost:5555/query \
  -H "Content-Type: application/json" \
  -d '{"type":"ping","data":"{}"}'

# Check DNS
nslookup generativelanguage.googleapis.com

# Check latency
ping -c 5 generativelanguage.googleapis.com
```

## 📞 Getting Help

### Self-Help Resources

1. **Documentation**
   - README.md - Overview and quick start
   - FAQ.md - Common questions
   - SETUP_GUIDE.md - Detailed setup
   - Wiki - Comprehensive guides

2. **Logs**
   - Always check logs first
   - Look for ERROR or WARNING messages
   - Note timestamps for correlation

3. **Dashboard**
   - Use status indicators for quick diagnosis
   - All green = system healthy
   - Yellow/Red = check that specific component

### Community Help

1. **GitHub Discussions**
   - Ask questions
   - Share experiences
   - Get community support

2. **GitHub Issues**
   - Report bugs
   - Request features
   - Track known issues

3. **Stack Overflow**
   - Tag: unreal-engine, ai-assistant
   - Search existing questions first

### Emergency Recovery

**If all else fails:**

```bash
# Complete reset (CAUTION: Deletes all data!)

# Backup first
cp -r chroma_db chroma_db.backup
cp ~/.adastrea/config.json config.backup

# Clean everything
rm -rf chroma_db/
rm -rf logs/
rm -rf ~/.adastrea/
rm -rf __pycache__/
rm -rf Plugins/AdastreaDirector/Python/__pycache__/

# Reinstall dependencies
pip uninstall -y chromadb langchain openai google-generativeai
pip install -r requirements.txt

# Reconfigure
python main.py --set-api-key gemini

# Re-ingest documentation
python ingest.py --docs-dir /path/to/docs

# Restart UE Editor
```

## ✅ Verification Checklist

After fixing issues, verify everything works:

- [ ] All 6 Dashboard indicators green
- [ ] Test query returns valid response
- [ ] Ingestion completes successfully
- [ ] Settings save and persist
- [ ] Python backend auto-starts
- [ ] IPC connection stable (< 2ms latency)
- [ ] API key valid and has quota
- [ ] Knowledge base accessible
- [ ] Recent activity shows successes
- [ ] No errors in logs

## 📚 Additional Resources

- **Official Documentation**: GitHub Wiki
- **Video Tutorials**: (Coming soon)
- **Community Forum**: GitHub Discussions
- **Bug Tracker**: GitHub Issues
- **Email Support**: Via GitHub profile

---

**Remember**: Most issues are configuration or environment related. Check the basics first (Python version, dependencies, API key) before diving into complex diagnostics.

If you solve an issue not covered here, please share your solution on GitHub Discussions to help others!
