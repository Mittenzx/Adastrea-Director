# Plugin Testing Quick Reference

**Quick access guide for testing the Adastrea Director plugin**

---

## 📋 Main Testing Document

**[TESTING_CHECKLIST_WEEKS_1_6.md](TESTING_CHECKLIST_WEEKS_1_6.md)** - Comprehensive testing checklist (1594 lines)

---

## 🚀 Quick Start Testing

### Prerequisites Check
```bash
# Verify you have everything installed
python --version          # Should be 3.9+
which python             # Should show Python path
pip list | grep chroma   # Verify ChromaDB installed
```

### Run All Quick Tests
```bash
cd Plugins/AdastreaDirector/Python

# Test 1: IPC Server functionality
python test_ipc.py 5555

# Test 2: RAG modules structure
python test_rag_modules.py

# Test 3: IPC performance
python test_ipc_performance.py

# Test 4: UI integration (requires server running)
python ipc_server.py --port 5555 &
SERVER_PID=$!
python test_ui_integration.py
kill $SERVER_PID
```

---

## 📊 Testing by Week

| Week | Focus | Quick Test Command | Full Docs |
|------|-------|-------------------|-----------|
| **Week 1** | Project Setup | Manual: Load plugin in UE | [Week 1 Tests](#week-1-quick-tests) |
| **Week 2** | Python Bridge | `python test_ipc.py 5555` | [Week 2 Tests](#week-2-quick-tests) |
| **Week 3** | Backend IPC | `python test_ipc_performance.py` | [Week 3 Tests](#week-3-quick-tests) |
| **Week 4** | Basic UI | Manual: Open panel in UE | [Week 4 Tests](#week-4-quick-tests) |
| **Week 5** | Ingestion | `python test_rag_modules.py` | [Week 5 Tests](#week-5-quick-tests) |
| **Week 6** | Query System | `python test_ui_integration.py` | [Week 6 Tests](#week-6-quick-tests) |

---

## Week 1 Quick Tests

**Goal:** Verify plugin structure and loading

### Essential Checks
- [ ] Plugin folder structure complete
- [ ] `.uplugin` file is valid JSON
- [ ] Plugin appears in UE plugin list
- [ ] Plugin loads without errors

### Quick Verification
```bash
# Check structure
ls -la Plugins/AdastreaDirector/Source/
ls -la Plugins/AdastreaDirector/Resources/

# Validate JSON
python -m json.tool AdastreaDirector.uplugin
```

**Full Details:** [TESTING_CHECKLIST_WEEKS_1_6.md#week-1-project-setup-testing](TESTING_CHECKLIST_WEEKS_1_6.md#week-1-project-setup-testing)

---

## Week 2 Quick Tests

**Goal:** Verify Python Bridge and IPC work

### Essential Checks
- [ ] Python server starts
- [ ] IPC connection succeeds
- [ ] Request/response works
- [ ] Subprocess managed correctly

### Quick Test
```bash
cd Python
python test_ipc.py 5555
```

**Expected:** All tests pass ✅

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
| Memory Usage | < 1GB | Monitor during ingestion |

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
