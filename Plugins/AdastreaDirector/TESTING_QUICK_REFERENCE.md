# Plugin Testing Quick Reference

**Quick access guide for testing the Adastrea Director plugin**

---

## 👋 First Time Here?

**Welcome!** This is a condensed guide for testing the Adastrea Director plugin.

### What is This Document?

This is the **quick reference** version of our testing documentation. Think of it as a "cheat sheet" that gives you the most important commands and checks without all the detailed explanations.

**Use this if:**
- ✅ You've tested before and need a quick reminder
- ✅ You want to run specific tests quickly
- ✅ You need to find a command fast
- ✅ You're debugging a specific issue

**Use the [full testing checklist](TESTING_CHECKLIST_WEEKS_1_6.md) if:**
- 📚 This is your first time testing the plugin
- 📚 You want detailed explanations of what each test does
- 📚 You need troubleshooting help
- 📚 You're learning about the plugin architecture

### How Testing Works

Testing the plugin involves:
1. **Automated tests** - Scripts you run that check things automatically
2. **Manual tests** - Things you do yourself in Unreal Engine (clicking, typing, observing)
3. **Verification** - Confirming the results match what's expected

Don't worry - we tell you exactly what commands to run and what to look for!

### What You're Testing

The Adastrea Director plugin has several components that need testing:
- **Plugin structure** (Week 1): Files are organized correctly
- **Python connection** (Week 2-3): C++ and Python parts can communicate
- **User interface** (Week 4): UI displays and works properly
- **AI features** (Week 5-6): Document ingestion and question answering work

---

## 📋 Main Testing Document

**[TESTING_CHECKLIST_WEEKS_1_6.md](TESTING_CHECKLIST_WEEKS_1_6.md)** - Comprehensive testing checklist (1594 lines)
- ⭐ **Start here if you're new to testing this plugin**
- Contains detailed explanations, step-by-step procedures, and troubleshooting
- Includes beginner-friendly context and terminology

---

## 🚀 Quick Start Testing

**Before you start:** Make sure you've completed the setup in the [full testing checklist](TESTING_CHECKLIST_WEEKS_1_6.md#testing-prerequisites).

### Prerequisites Check

**What this does:** Verifies you have the required software installed.

```bash
# Check Python version (should show 3.9 or higher)
python --version

# Check where Python is installed (optional, for troubleshooting)
which python             # Mac/Linux
where python             # Windows

# Check if ChromaDB is installed (needed for AI features in Week 5+)
pip list | grep chroma   # Mac/Linux
pip list | findstr chroma  # Windows
```

**What the output means:**
- `python --version` shows something like "Python 3.9.7" or higher → ✅ Good
- `python --version` shows "command not found" or lower version → ❌ Need to install Python
- `pip list` shows chromadb → ✅ Ready for Week 5+ tests
- `pip list` shows nothing → ⚠️ Install later before Week 5 tests

### Run All Quick Tests

**What this does:** Runs the main automated test suite to verify the plugin's Python backend works correctly.

**Time needed:** 2-3 minutes

**Skill level:** Basic (just copy and paste)

**When to use:** After setting up the plugin or making changes to verify everything still works.

```bash
# Step 1: Navigate to the Python backend folder
cd Plugins/AdastreaDirector/Python

# Test 1: IPC Server functionality
# What it tests: Communication between C++ and Python works
python test_ipc.py 5555
# Expected: Should see "All IPC tests passed!" at the end

# Test 2: RAG modules structure  
# What it tests: AI document processing modules are set up correctly
python test_rag_modules.py
# Expected: Should see checkmarks (✅) for each module check

# Test 3: IPC performance
# What it tests: Communication is fast enough (should be under 50ms)
python test_ipc_performance.py
# Expected: Should show latency times all under 50ms

# Test 4: UI integration (requires server running)
# What it tests: UI can connect to and use the Python backend
python ipc_server.py --port 5555 &  # Start server in background
SERVER_PID=$!                        # Save process ID for cleanup
python test_ui_integration.py        # Run integration tests
kill $SERVER_PID                     # Stop the server when done
# Expected: Should see "All integration tests passed!"
```

**If tests fail:**
1. Check the error message - it usually tells you what's wrong
2. Verify prerequisites are installed (see above)
3. See the [Troubleshooting section](#common-issues--quick-fixes) below
4. Check the [full testing checklist](TESTING_CHECKLIST_WEEKS_1_6.md#troubleshooting-guide) for detailed help

**Windows users note:**
The last test (Test 4) uses Unix commands. On Windows, use this instead:
```cmd
:: Start server
start /B python ipc_server.py --port 5555
:: Run tests (wait a moment for server to start)
timeout /t 2
python test_ui_integration.py
:: Stop server (manually close the window or use Task Manager)
```

---

## 📊 Testing by Week

**How the weeks are organized:**

The plugin was built over 6 weeks, with each week adding new features. Testing follows the same structure:
- **Weeks 1-2**: Foundation (plugin setup and Python connection)
- **Weeks 3-4**: Communication and UI (data flow and user interface)
- **Weeks 5-6**: AI Features (document processing and question answering)

**Test in order if:**
- This is your first time testing
- You want to understand how everything builds up
- Something isn't working and you need to isolate the problem

**Jump to specific weeks if:**
- You've tested before and need to verify specific features
- You only changed code for a specific week's features
- You're debugging a known issue

| Week | Focus | What Gets Tested | Quick Test Command | Full Docs |
|------|-------|------------------|-------------------|-----------|
| **Week 1** | Project Setup | Files exist, plugin loads | Manual: Load plugin in UE | [Week 1 Tests](#week-1-quick-tests) |
| **Week 2** | Python Bridge | C++ ↔ Python connection | `python test_ipc.py 5555` | [Week 2 Tests](#week-2-quick-tests) |
| **Week 3** | Backend IPC | Communication speed/reliability | `python test_ipc_performance.py` | [Week 3 Tests](#week-3-quick-tests) |
| **Week 4** | Basic UI | Interface displays correctly | Manual: Open panel in UE | [Week 4 Tests](#week-4-quick-tests) |
| **Week 5** | Ingestion | Document processing | `python test_rag_modules.py` | [Week 5 Tests](#week-5-quick-tests) |
| **Week 6** | Query System | Question answering | `python test_ui_integration.py` | [Week 6 Tests](#week-6-quick-tests) |

---

## Week 1 Quick Tests

**Goal:** Verify plugin structure and loading

**What you're checking:** The plugin files are organized correctly and Unreal Engine can recognize and load the plugin.

**Why this matters:** If the basic structure isn't right, nothing else will work. Think of it like checking the foundation before building a house.

**Skill level:** Basic - checking files and opening Unreal Engine

**Time needed:** 5-10 minutes

### Essential Checks
- [ ] Plugin folder structure complete (all expected files and folders exist)
- [ ] `.uplugin` file is valid JSON (configuration file is properly formatted)
- [ ] Plugin appears in UE plugin list (Unreal Engine can see it)
- [ ] Plugin loads without errors (starts up successfully)

### Quick Verification

**Check 1: Verify Folder Structure**

```bash
# Navigate to plugin directory
cd Plugins/AdastreaDirector

# Check source code folders exist
ls -la Source/
# Expected: Should see AdastreaDirector/ and AdastreaDirectorEditor/ folders

# Check resources folder exists
ls -la Resources/
# Expected: Should see Icon files

# Windows equivalent:
dir Source\
dir Resources\
```

**Check 2: Validate Configuration File**

```bash
# Check that the .uplugin file is valid JSON format
python -m json.tool AdastreaDirector.uplugin
# Expected: Should display formatted JSON without errors
# If you see an error, the file format is invalid

# What this file does: Tells Unreal Engine about the plugin 
# (name, version, what modules it has, etc.)
```

**Check 3: Test in Unreal Engine (Manual)**

1. Open Unreal Engine Editor
2. Open your test project
3. Go to **Edit → Plugins**
4. Search for "Adastrea Director"
5. ✅ Plugin should appear in the list under "Developer Tools"
6. ✅ Status should show as "Enabled"
7. Check **Window → Developer Tools → Output Log**
8. ✅ Should see: "AdastreaDirector Module: StartupModule"

**If plugin doesn't appear:**
- Check that plugin is copied to YourProject/Plugins/
- Right-click .uproject → Generate Visual Studio Project Files
- Rebuild the project

**Full Details:** [TESTING_CHECKLIST_WEEKS_1_6.md#week-1-project-setup-testing](TESTING_CHECKLIST_WEEKS_1_6.md#week-1-project-setup-testing)

---

## Week 2 Quick Tests

**Goal:** Verify Python Bridge and IPC work

**What you're checking:** The C++ plugin can successfully start and communicate with the Python backend. This is the connection that makes the AI features possible.

**Why this matters:** The plugin's AI capabilities run in Python, so the C++ and Python parts must be able to talk to each other reliably.

**Key concept - IPC (Inter-Process Communication):** 
Think of it like a phone call between two programs. The C++ plugin (in Unreal Engine) needs to "call" the Python backend to request AI processing, and Python needs to "answer" with results.

**Skill level:** Basic - running test scripts

**Time needed:** 2-3 minutes

### Essential Checks
- [ ] Python server starts (the Python backend launches successfully)
- [ ] IPC connection succeeds (C++ can connect to Python)
- [ ] Request/response works (can send data and get responses)
- [ ] Subprocess managed correctly (Python process starts/stops cleanly)

### Quick Test

```bash
# Navigate to Python backend folder
cd Plugins/AdastreaDirector/Python

# Run the IPC test script
python test_ipc.py 5555
# This script:
# 1. Starts a test Python server on port 5555
# 2. Sends various test messages
# 3. Verifies responses are correct
# 4. Cleans up when done
```

**Expected Output:**
```
✅ Server connection successful
✅ Ping test passed
✅ Query test passed
✅ Plan test passed
✅ Analyze test passed
✅ Invalid request handled correctly
✅ Multi-threaded test passed

All IPC tests passed!
```

**What each test means:**
- **Server connection**: Python backend is reachable
- **Ping test**: Basic communication works (like "hello, are you there?")
- **Query/Plan/Analyze**: Different types of AI requests work
- **Invalid request**: Error handling works properly
- **Multi-threaded**: Multiple requests at once work (important for performance)

**If tests fail:**
- Check Python is installed: `python --version`
- Check port 5555 isn't already in use: `netstat -an | grep 5555` (Mac/Linux) or `netstat -an | findstr 5555` (Windows)
- Make sure you're in the correct directory
- Check firewall isn't blocking localhost connections

**Full Details:** [TESTING_CHECKLIST_WEEKS_1_6.md#week-2-python-bridge-testing](TESTING_CHECKLIST_WEEKS_1_6.md#week-2-python-bridge-testing)

---

## Week 3 Quick Tests

**Goal:** Verify backend performance and reliability

### Essential Checks
- [ ] Performance metrics working
- [ ] All handlers implemented
- [ ] Latency < 1ms for ping
- [ ] Concurrent requests handled

### Quick Test
```bash
cd Python
python test_ipc_performance.py
```

**Expected:** Average latency < 1ms ✅

**Full Details:** [TESTING_CHECKLIST_WEEKS_1_6.md#week-3-python-backend-ipc-testing](TESTING_CHECKLIST_WEEKS_1_6.md#week-3-python-backend-ipc-testing)

---

## Week 4 Quick Tests

**Goal:** Verify UI loads and communicates

### Essential Checks
- [ ] Panel opens in UE
- [ ] Query input works
- [ ] Send button functional
- [ ] Results display updates

### Quick Test
**Manual in Unreal Editor:**
1. Window → Developer Tools → Adastrea Director
2. Type "test query"
3. Click "Send Query"
4. Verify response appears

**Full Details:** [TESTING_CHECKLIST_WEEKS_1_6.md#week-4-basic-ui-testing](TESTING_CHECKLIST_WEEKS_1_6.md#week-4-basic-ui-testing)

---

## Week 5 Quick Tests

**Goal:** Verify document ingestion works

### Essential Checks
- [ ] Ingestion UI functional
- [ ] Progress bar updates
- [ ] Documents ingested
- [ ] ChromaDB created

### Quick Test
```bash
cd Python
python test_rag_modules.py
```

**Manual in UE:**
1. Open Ingestion tab
2. Select test docs folder
3. Click "Start Ingestion"
4. Verify progress reaches 100%

**Full Details:** [TESTING_CHECKLIST_WEEKS_1_6.md#week-5-document-ingestion-testing](TESTING_CHECKLIST_WEEKS_1_6.md#week-5-document-ingestion-testing)

---

## Week 6 Quick Tests

**Goal:** Verify query system works end-to-end

### Essential Checks
- [ ] Queries return responses
- [ ] Responses are contextual
- [ ] Conversation history works
- [ ] Cache improves performance

### Quick Test
```bash
cd Python
# Start server first
python ipc_server.py --port 5555 &
sleep 2

# Run UI integration tests
python test_ui_integration.py

# Cleanup
pkill -f ipc_server.py
```

**Manual in UE:**
1. Open Query tab
2. Send: "What is Unreal Engine?"
3. Verify contextual response
4. Send follow-up question
5. Verify context maintained

**Full Details:** [TESTING_CHECKLIST_WEEKS_1_6.md#week-6-query-system-testing](TESTING_CHECKLIST_WEEKS_1_6.md#week-6-query-system-testing)

---

## 🔧 Common Issues & Quick Fixes

### Plugin Won't Load
```bash
# Regenerate project files
cd /path/to/UEProject
# Windows: Right-click .uproject → Generate VS files
# Linux/Mac: ./GenerateProjectFiles.sh
```

### Python Won't Connect
```bash
# Check Python is installed
python --version

# Check dependencies
cd Plugins/AdastreaDirector/Python
pip install -r requirements.txt

# Test server manually
python ipc_server.py --port 5555
```

### Ingestion Fails
```bash
# Check ChromaDB
pip install chromadb langchain

# Verify folder permissions
ls -la /path/to/docs/folder

# Test standalone
cd Python
python -c "from rag_ingestion import RAGIngestionAgent; print('OK')"
```

### Queries Return Nothing
```bash
# Check database exists
ls -la /path/to/chroma_db/

# Test RAG modules
cd Python
python test_rag_modules.py

# Check LLM API key
echo $GEMINI_KEY
echo $OPENAI_API_KEY
```

**Full Troubleshooting:** [TESTING_CHECKLIST_WEEKS_1_6.md#troubleshooting-guide](TESTING_CHECKLIST_WEEKS_1_6.md#troubleshooting-guide)

---

## 📈 Performance Targets

| Metric | Target | How to Test |
|--------|--------|-------------|
| IPC Latency | < 50ms | `python test_ipc_performance.py` |
| Query Response | < 3s | Send query in UI |
| Cached Query | < 100ms | Repeat same query |
| Ingestion Rate | 1-2 files/s | Ingest 10 files, time it |
| Memory Usage | < 1GB total (peak), avg 500MB | Monitor during ingestion |

---

## 🧪 Test Scripts Reference

Located in: `Plugins/AdastreaDirector/Python/`

| Script | Purpose | Usage |
|--------|---------|-------|
| `test_ipc.py` | IPC functionality | `python test_ipc.py 5555` |
| `test_rag_modules.py` | RAG module structure | `python test_rag_modules.py` |
| `test_ipc_performance.py` | Performance benchmarks | `python test_ipc_performance.py` |
| `test_ui_integration.py` | UI integration | `python test_ui_integration.py` |

---

## 📚 Related Documentation

- **[TESTING_CHECKLIST_WEEKS_1_6.md](TESTING_CHECKLIST_WEEKS_1_6.md)** - Complete testing guide
- **[README.md](README.md)** - Plugin overview
- **[INSTALLATION.md](INSTALLATION.md)** - Installation guide
- **[RAG_INTEGRATION.md](RAG_INTEGRATION.md)** - RAG system details
- **[WEEK1_COMPLETION.md](WEEK1_COMPLETION.md)** - Week 1 report
- **[WEEK2_COMPLETION.md](WEEK2_COMPLETION.md)** - Week 2 report
- **[WEEK3_COMPLETION.md](WEEK3_COMPLETION.md)** - Week 3 report
- **[WEEK4_COMPLETION.md](WEEK4_COMPLETION.md)** - Week 4 report
- **[WEEK5_6_COMPLETION.md](WEEK5_6_COMPLETION.md)** - Weeks 5-6 report

---

## ✅ Full Test Checklist Summary

### Week 1: Project Setup ✅
- [x] Plugin structure valid
- [x] Plugin loads in UE
- [x] Modules initialize
- [x] Cross-platform verified

### Week 2: Python Bridge ✅
- [x] Python subprocess launches
- [x] IPC connection works
- [x] Requests/responses correct
- [x] Error recovery functional

### Week 3: Backend IPC ✅
- [x] Performance metrics working
- [x] All handlers implemented
- [x] Concurrent requests handled
- [x] Optimization targets met

### Week 4: Basic UI ✅
- [x] Panel loads and displays
- [x] Query input functional
- [x] Results display works
- [x] End-to-end communication verified

### Week 5: Document Ingestion ✅
- [x] Ingestion UI functional
- [x] Progress tracking works
- [x] Documents ingested correctly
- [x] Incremental updates work

### Week 6: Query System ✅
- [x] Basic queries work
- [x] Context-aware responses
- [x] Conversation history maintained
- [x] Performance acceptable

### Integration ✅
- [x] End-to-end workflow smooth
- [x] Cross-module integration verified
- [x] Platform compatibility confirmed
- [x] Performance benchmarks met

---

## 🎯 Next Steps

After completing testing for weeks 1-6:

1. **Week 7-8:** Polish & Testing
   - Settings dialog
   - Error handling improvements
   - Additional UI polish
   - Documentation refinement

2. **Week 9-12:** Planning Features (Phase 3)
   - Goal analysis integration
   - Task decomposition
   - Code generation

3. **Week 13-16:** Polish & Release (Phase 4)
   - Fab marketplace preparation
   - Final testing
   - Documentation complete
   - Launch!

---

**Document Version:** 1.0  
**Last Updated:** November 14, 2025  
**Status:** Ready for Use

*For detailed testing procedures, see [TESTING_CHECKLIST_WEEKS_1_6.md](TESTING_CHECKLIST_WEEKS_1_6.md)*
