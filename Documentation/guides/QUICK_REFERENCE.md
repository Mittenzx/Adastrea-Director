# Adastrea Director - Quick Reference Card

> Your cheat sheet for using Adastrea Director effectively

## 🚀 Quick Start (5 Minutes)

### For Plugin Users (Unreal Engine)

```
1. Window → Developer Tools → Adastrea Director
2. Click Settings icon → Add API key
3. (Optional) Ingestion tab → Add docs
4. Query tab → Ask questions!
```

### For Standalone Users (Python)

```bash
# Setup
python install_dependencies.py
export GEMINI_KEY="your-key-here"

# Query
python main.py

# Plan
python planner.py --interactive
```

## 🎯 Essential Features

### Query Tab
- **Ask questions** about your project
- **Generate code** snippets
- **Get documentation** answers
- **Review history** of past queries

**Keyboard Shortcuts:**
- `Enter` or `Ctrl+Enter` - Submit query
- `Ctrl+,` - Open settings
- `Ctrl+L` - Clear conversation

### Ingestion Tab
- **Add documentation** to knowledge base
- **Track progress** with visual indicators
- **View ingested files** count
- **Update knowledge base** anytime

### Dashboard Tab
- **Monitor system health** (6 indicators)
- **Check connectivity** status
- **View recent activity** success rate
- **Debug issues** with color-coded status

**Status Colors:**
- 🟢 **Green** - All good
- 🟡 **Yellow** - Warning
- 🔴 **Red** - Issue detected

## 💡 Common Use Cases

### Get API Documentation
```
Query: "How do I spawn an actor in C++?"
Query: "Show me Blueprint replication setup"
Query: "What's the best way to optimize draw calls?"
```

### Plan New Features
```bash
# Via CLI
python planner.py "Add inventory system with weight limits"

# Via GUI (standalone)
python gui_director.py
# Then use planning features
```

### Generate Code
```
Query: "Generate a dash ability for a third-person character"
Query: "Create a Blueprint that plays a sound on overlap"
Query: "Write C++ code for a health component"
```

### Debug Issues
```
Query: "Why is my actor not replicating?"
Query: "Explain this crash: [paste crash log]"
Query: "How do I fix memory leaks in UE?"
```

## 🔧 Configuration Quick Tips

### API Keys

**Priority:**
1. Saved config (`~/.adastrea/config.json`)
2. Environment variable
3. `.env` file

**Set via CLI:**
```bash
python main.py --set-api-key gemini
```

**Set via GUI:**
Settings icon → API Key Management

### File Paths

**Default Locations:**
- Database: `./chroma_db/`
- Logs: `./logs/`
- Config: `~/.adastrea/`

**Custom Paths:**
```bash
python ingest.py --docs-dir /custom/path --db-path /custom/db
```

## 📊 Status Indicators Explained

### Python Backend (🟢🟡🔴)
- **Green**: Process running, healthy
- **Yellow**: Starting up
- **Red**: Not running or crashed

### IPC Connection (🟢🟡🔴)
- **Green**: Connected, < 1ms latency
- **Yellow**: Connecting
- **Red**: Connection failed

### LLM Provider (🟢🟡🔴)
- **Green**: API key valid, connected
- **Yellow**: Not configured
- **Red**: Invalid key or connection failed

### Vector Database (🟢🟡🔴)
- **Green**: ChromaDB accessible
- **Yellow**: Initializing
- **Red**: Database error

### Knowledge Base (🟢🟡🔴)
- **Green**: Documents loaded (shows count)
- **Yellow**: Empty or loading
- **Red**: Error accessing documents

### Recent Activity (🟢🟡🔴)
- **Green**: Queries succeeding
- **Yellow**: Some failures
- **Red**: All queries failing

## 🐛 Quick Troubleshooting

### Plugin Panel Empty
```
1. Check Dashboard tab - all indicators green?
2. Restart UE Editor
3. Check Python installed: python --version
4. Check logs in Plugins/AdastreaDirector/Python/logs/
```

### Connection Failed
```
1. Port 5555 available? netstat -an | grep 5555
2. Python dependencies installed? pip list
3. Firewall blocking localhost? Check settings
4. Try manual start: python ipc_server.py
```

### Poor Query Results
```
1. Add more documentation (Ingestion tab)
2. Make query more specific
3. Include code context
4. Try different LLM provider
```

### Slow Performance
```
1. Check system resources (RAM, CPU)
2. Reduce document count if excessive
3. Clear old logs: rm -rf logs/*
4. Restart Python backend
```

## 📚 Documentation Quick Links

### Plugin
- Setup: `Plugins/AdastreaDirector/SETUP_GUIDE.md`
- Features: `Plugins/AdastreaDirector/FEATURES.md`
- Python API: `Plugins/AdastreaDirector/UE_PYTHON_API.md`
- Examples: `Plugins/AdastreaDirector/Content/Examples/`

### Main Project
- README: `README.md`
- FAQ: `FAQ.md`
- Changelog: `CHANGELOG.md`
- Wiki: https://github.com/Mittenzx/Adastrea-Director/wiki

## 🎓 Best Practices

### Query Writing
✅ **Good:**
- "Show me how to implement a dash ability in C++ with input binding"
- "What's causing this replication issue: [specific symptoms]"
- "Generate Blueprint code for a damage system with armor calculation"

❌ **Avoid:**
- "Help"
- "Fix my code" (without context)
- "Make it work"

### Documentation Ingestion
✅ **Include:**
- Project design documents
- API references
- Code comments and READMEs
- Team wikis and guides

❌ **Skip:**
- Binary files
- Large media files
- Generated code
- Third-party SDKs (unless needed)

### Performance
✅ **Do:**
- Ingest docs once, query many times
- Use specific queries for faster results
- Keep knowledge base updated
- Monitor Dashboard for issues

❌ **Don't:**
- Re-ingest same docs repeatedly
- Query while ingesting
- Ignore red status indicators
- Let logs accumulate indefinitely

## 🔑 Keyboard Shortcuts Reference

### Plugin (Unreal Engine)
| Shortcut | Action |
|----------|--------|
| `Ctrl+,` | Open Settings |
| `Ctrl+Enter` | Submit Query |
| `Ctrl+L` | Clear Conversation |

### Standalone GUI
| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Send Question |
| `Ctrl+K` | Set API Key |
| `Ctrl+,` | Settings Dialog |
| `Ctrl+U` | Update Knowledge Base |
| `Ctrl+L` | Clear Conversation |
| `Ctrl+C` | Copy Response |
| `Ctrl+E` | Export Conversation |

## 💻 Command-Line Reference

### Main Applications
```bash
# Interactive assistant
python main.py

# GUI application
python gui_director.py

# Planning system
python planner.py --interactive

# Agent dashboard
python agent_dashboard.py

# Document ingestion
python ingest.py --docs-dir /path/to/docs
```

### Common Arguments
```bash
# Set API key
--set-api-key gemini

# Use specific LLM
--llm-provider openai

# Custom database path
--db-path /custom/path

# Enable debug logging
--debug

# Show version
--version
```

## 🆘 Get Help

### Self-Service
1. Check Dashboard status indicators
2. Read FAQ.md
3. Check logs: `logs/` folder
4. Review SETUP_GUIDE.md

### Community Support
- 🐛 **GitHub Issues**: Bug reports
- 💬 **Discussions**: Questions and ideas
- 📖 **Wiki**: Comprehensive docs
- 📧 **Contact**: Via GitHub profile

### Useful Commands for Debugging
```bash
# Check Python version
python --version

# List installed packages
pip list | grep -E "(chromadb|langchain|openai)"

# Test IPC connection
curl http://localhost:5555/health

# View recent logs
tail -f logs/adastrea_director.log

# Check process status
ps aux | grep python | grep ipc_server
```

## 📈 Performance Tips

### For Best Results
- **Ingest selectively**: Quality over quantity
- **Clear queries**: Be specific about what you need
- **Use context**: Include relevant code/errors
- **Monitor status**: Check Dashboard regularly
- **Update regularly**: Keep knowledge base current

### Resource Usage
- **RAM**: ~500 MB - 1 GB typical
- **CPU**: Minimal (spikes during queries)
- **Disk**: 50-500 MB for knowledge base
- **Network**: Only for LLM API calls

## 🎯 Success Checklist

Before first use:
- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] API key configured (Gemini or OpenAI)
- [ ] Plugin loaded in UE (for plugin users)
- [ ] Documentation ingested (optional but recommended)

For optimal experience:
- [ ] All status indicators green
- [ ] Knowledge base has 10+ documents
- [ ] API key is valid and has quota
- [ ] Latest version installed
- [ ] Familiarized with basic queries

## 🚀 Pro Tips

1. **Use the Dashboard**: Check it first when something seems wrong
2. **Ingest Early**: Add docs before you need them
3. **Be Specific**: Detailed queries get better answers
4. **Save Responses**: Export valuable conversations
5. **Update Often**: Keep knowledge base current
6. **Try Examples**: Learn from included examples
7. **Check Changelog**: Stay updated on new features
8. **Join Community**: Share experiences on GitHub

---

**Adastrea Director** - Your AI development partner

*Need more details? See README.md, FAQ.md, or the Wiki*
