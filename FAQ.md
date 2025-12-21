# Adastrea Director - Frequently Asked Questions (FAQ)

## General Questions

### What is Adastrea Director?

Adastrea Director is an AI-powered development assistant for Unreal Engine that provides intelligent code assistance, automated planning, performance profiling, and bug detection capabilities. It's available as both a standalone Python application and an integrated Unreal Engine plugin.

### Who is this tool for?

- **Game Developers**: Working in Unreal Engine who need AI assistance
- **Technical Artists**: Looking for automated content generation and validation
- **Indie Developers**: Needing comprehensive development assistance without a large team
- **Studios**: Seeking to improve development efficiency and code quality

### Is this free or paid?

Adastrea Director is open-source and free to use under the MIT License. There are no licensing fees or subscription costs for the tool itself. However, you'll need API keys for LLM providers (Gemini, OpenAI) which have their own pricing.

### What Unreal Engine versions are supported?

The plugin supports Unreal Engine 4.27 through 5.6. The standalone Python version works with any project type.

## Installation & Setup

### Do I need to install anything besides the plugin?

Yes, for full functionality you need:
- **Python 3.9+** (Python 3.12+ recommended)
- **LLM API Key**: Gemini (recommended, free tier available) or OpenAI
- **Python Dependencies**: Installed via `pip install -r requirements.txt`

The plugin handles the Python backend automatically, but initial setup requires these components.

### Why do I need Python if this is an Unreal Engine plugin?

The plugin uses a hybrid architecture:
- **C++ Shell**: Provides the UI and UE integration
- **Python Backend**: Handles AI processing, RAG, and complex operations

This design allows us to leverage powerful Python AI libraries while maintaining tight UE integration.

### Can I use this without an LLM API key?

For embedding documents, yes! The system uses **HuggingFace embeddings by default**, which work offline without any API key. However, to query the AI assistant and get responses, you'll need an LLM API key (Gemini or OpenAI).

### Which LLM provider should I use?

**Recommended: Google Gemini**
- Free tier available with generous limits
- Good performance for code and documentation tasks
- Easy setup with single API key

**Alternative: OpenAI**
- Excellent quality but paid service
- Higher costs but potentially better for complex queries
- Well-established and reliable

### How do I get a Gemini API key?

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to Adastrea Director settings

Free tier includes substantial monthly quota for personal projects.

## Usage Questions

### How do I use the plugin in Unreal Engine?

1. **Open the Panel**: Window → Developer Tools → Adastrea Director
2. **Configure API Key**: Click Settings icon, add your LLM API key
3. **Ingest Docs** (optional): Use Ingestion tab to add your project documentation
4. **Start Querying**: Use the Query tab to ask questions

See `Plugins/AdastreaDirector/SETUP_GUIDE.md` for detailed instructions.

### What can I ask the AI assistant?

You can ask about:
- Unreal Engine API usage and best practices
- Your project's documentation and code structure
- Implementation approaches for features
- Debugging assistance
- Performance optimization strategies
- Blueprint and C++ coding questions

### How do I add my project documentation?

**Option 1: Via Plugin UI**
1. Open the Adastrea Director panel
2. Switch to the "Ingestion" tab
3. Enter documentation paths or URLs
4. Click "Start Ingestion"

**Option 2: Via Standalone CLI**
```bash
python ingest.py --docs-dir /path/to/your/docs
```

### What file formats are supported for ingestion?

- **Markdown** (.md)
- **Text** (.txt)
- **reStructuredText** (.rst)
- **Python** (.py) - extracts docstrings
- **C++** (.cpp, .h) - extracts comments
- **JSON** (.json) - structured data

### How does the planning feature work?

The Planner (Phase 2) breaks down development goals:

1. **Input**: Natural language goal (e.g., "Add an inventory system")
2. **Analysis**: AI analyzes requirements and complexity
3. **Decomposition**: Breaks into prioritized tasks with dependencies
4. **Output**: Actionable plan with code suggestions and effort estimates

Use via CLI: `python planner.py --interactive`

## Technical Questions

### What's the difference between Standalone and Plugin modes?

**Standalone (Python GUI/CLI)**
- Runs independently of Unreal Engine
- Faster for quick queries and testing
- Full feature set available
- Better for non-UE projects

**Plugin (Unreal Engine)**
- Integrated into UE editor workflow
- No context switching required
- Direct access to UE Python API
- Better for active UE development

Both use the **same Python backend** - it's the same AI system with different interfaces.

### How fast is the system?

- **IPC Latency**: < 1ms for communication
- **Query Response**: 1-5 seconds (depends on LLM provider)
- **Document Ingestion**: ~10-100 docs per minute
- **Status Updates**: Real-time (0.5s refresh)

Performance is optimized for development workflows with minimal interruption.

### Does this work offline?

**Partially:**
- ✅ **Document embedding**: Yes (HuggingFace embeddings work offline)
- ✅ **Local operations**: File operations, status monitoring
- ❌ **AI queries**: No (requires LLM API connection)
- ❌ **Code generation**: No (requires LLM)

Once documents are ingested, the vector database is local, but AI responses need internet connectivity.

### How secure is my code/data?

- **Local Storage**: All ingested documents are stored locally in ChromaDB
- **API Calls**: Only queries and context are sent to LLM provider
- **No Cloud Storage**: We don't store or transmit your code to any servers
- **API Key Encryption**: Keys are encrypted with machine-specific encryption

See `SECURITY_SUMMARY.md` for detailed security analysis.

### Can I use this with private/proprietary code?

Yes, but be aware:
- Documents are stored locally
- Queries may include code snippets sent to the LLM provider
- Review your company's policies on AI tool usage
- Consider using self-hosted LLM solutions for maximum security

## Feature Questions

### What is Phase 3 (Autonomous Agents)?

Phase 3 adds autonomous capabilities:
- **Performance Profiling**: Automatic performance monitoring and optimization
- **Bug Detection**: Automated crash analysis and error detection
- **Code Quality**: Continuous monitoring and refactoring suggestions
- **Agent Orchestration**: Multiple AI agents working together

Status: Prerequisites complete, agents in development.

### Can this generate code for me?

Yes! The system can:
- Generate code snippets based on your queries
- Suggest multiple implementation approaches
- Provide complete function/class implementations
- Generate Blueprint graphs (descriptions, not actual .uasset files)

However, always review and test generated code - it's an assistant, not a replacement for developer judgment.

### Does it support languages other than English?

Currently, the system is optimized for English. The underlying LLMs (Gemini, OpenAI) support multiple languages, so basic functionality may work in other languages, but documentation and UI are English-only at this time.

### Can it help with multiplayer/networking code?

Yes! If you've ingested relevant documentation about your multiplayer system, the AI can:
- Answer questions about replication
- Suggest networking best practices
- Help debug multiplayer issues
- Generate network-aware code

It has general knowledge of UE multiplayer systems from its training.

## Troubleshooting

### The plugin panel is empty or not responding

**Solutions:**
1. Check Dashboard tab - ensure all status lights are green
2. Verify Python backend is running (should auto-start)
3. Check your API key is configured correctly
4. Restart Unreal Engine Editor
5. See `SETUP_GUIDE.md` troubleshooting section

### I get "Connection Failed" errors

**Common causes:**
- Python backend failed to start
- Port already in use (default: 5000)
- Python dependencies not installed
- Firewall blocking local connections

**Solutions:**
```bash
# Verify Python dependencies
cd Plugins/AdastreaDirector/Python
pip install -r requirements.txt

# Check port availability
netstat -an | grep 5000

# Check firewall settings (allow localhost connections)
```

### Ingestion is slow or failing

**Tips:**
- Large file ingestion takes time (be patient)
- Check disk space for ChromaDB
- Some file formats may not be supported
- Try smaller batches of files
- Check logs for specific errors

### AI responses are poor quality

**Improvement strategies:**
- Ingest more relevant documentation
- Make queries more specific and detailed
- Provide code context in your questions
- Try different LLM providers (Gemini vs OpenAI)
- Update knowledge base with recent changes

### The plugin won't compile

**Common issues:**
- Ensure you have Unreal Engine build tools installed
- Check Python version compatibility (3.9+)
- Regenerate project files
- Clean and rebuild
- Check `INSTALLATION.md` for platform-specific guidance

## Performance & Optimization

### How much RAM does this use?

**Typical usage:**
- **Plugin**: ~100-200 MB
- **Python Backend**: ~300-500 MB
- **ChromaDB**: Varies with document count (typically 50-500 MB)
- **Total**: ~500 MB - 1 GB

These are reasonable for modern development machines.

### Does this impact UE Editor performance?

Minimal impact:
- Python backend runs in separate process
- IPC is optimized for < 1ms latency
- UI updates are asynchronous
- No blocking operations on game thread

You can work normally while the AI processes in the background.

### Can I limit resource usage?

Currently, resource usage is optimized but not directly configurable. Future versions may add:
- Memory limits for ChromaDB
- Query rate limiting
- Background processing throttling

## Development & Contributing

### Can I contribute to this project?

Yes! We welcome contributions:
- Bug reports and fixes
- Feature requests and implementations
- Documentation improvements
- Test coverage expansion

See `CONTRIBUTING.md` for guidelines.

### Is there a roadmap?

Yes! See the project Wiki for:
- Current phase status
- Planned features
- Development timeline
- Sprint planning

We're currently in P3 (Autonomous Agents) development.

### How can I report bugs?

1. Check existing issues: https://github.com/Mittenzx/Adastrea-Director/issues
2. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, UE version, Python version)
   - Relevant logs

### Where can I get help?

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and community help
- **Wiki**: Comprehensive documentation
- **README**: Quick start and overview

## Licensing & Commercial Use

### Can I use this in commercial projects?

Yes! MIT License allows:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

Just include the license and copyright notice.

### Do I need to credit Adastrea Director?

Not required by the license, but appreciated! If you find it useful, consider:
- Mentioning it in your credits
- Starring the GitHub repo
- Sharing your experience with others

### Can I sell plugins/tools built with this?

Yes! You can create and sell commercial tools that use or integrate with Adastrea Director, as long as you comply with the MIT License terms.

## Future Plans

### What's coming next?

**Short-term (Current):**
- Complete Phase 3 autonomous agents
- Enhanced plugin UI features
- More integration examples

**Medium-term:**
- Phase 4: Creative Partner features
- AI-assisted content generation
- Advanced Blueprint integration
- Runtime gameplay integration

**Long-term:**
- Multi-project support
- Team collaboration features
- Cloud-based knowledge sharing
- Visual scripting for AI workflows

### Will there be a paid version?

No plans for a paid version of the tool itself. The project will remain open-source and free. Possible future premium options might include:
- Hosted knowledge base services
- Team collaboration features
- Premium support plans

But the core tool will always be free.

## Still Have Questions?

- 📖 **Read the Wiki**: https://github.com/Mittenzx/Adastrea-Director/wiki
- 🐛 **Report Issues**: https://github.com/Mittenzx/Adastrea-Director/issues
- 💬 **Join Discussions**: GitHub Discussions tab
- 📧 **Contact**: Via GitHub profile

---

*Last Updated: December 2025*
