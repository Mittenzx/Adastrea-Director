# Frequently Asked Questions (FAQ)

Common questions and answers about Adastrea Director.

## General Questions

### What is Adastrea Director?

Adastrea Director is an AI-powered game development assistant that provides context-aware documentation search, intelligent planning, and autonomous monitoring capabilities. It's designed to help game developers work more efficiently by providing intelligent assistance throughout the development lifecycle.

### Is it free to use?

Yes, Adastrea Director is open source (see the [LICENSE](https://github.com/Mittenzx/Adastrea-Director/blob/main/LICENSE) file for details). However, you'll need API keys for LLM providers (Gemini or OpenAI). Google Gemini offers a generous free tier, making it possible to use Adastrea Director at no cost for API usage.

### What makes it different from other AI assistants?

Adastrea Director is specifically designed for game development and offers:
- **Context-aware:** Understands your project documentation
- **Planning capabilities:** Breaks down goals into actionable tasks
- **Autonomous agents:** Proactive monitoring and optimization
- **Game dev focused:** Tailored for Unreal Engine and game development

### Can I use it with any game engine?

Yes! The standalone mode works with any project. However, the Unreal Engine plugin provides the best experience for UE developers with integrated in-editor features.

## Installation & Setup

### What are the system requirements?

- **Python:** 3.9+ (3.12+ recommended)
- **RAM:** 4GB minimum, 8GB+ recommended
- **Storage:** 2GB free space
- **OS:** Windows 10+, macOS 10.14+, Ubuntu 20.04+

See [System Requirements](System-Requirements.md) for details.

### Do I need an API key?

Yes, you need an API key for one of these LLM providers:
- **Google Gemini** (Recommended - free tier available)
- **OpenAI** (Pay-per-use)
- **Ollama** (Completely local, no API key needed)

For embeddings, HuggingFace is used by default (no API key required).

### How do I get a Gemini API key?

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Get API Key" or "Create API Key"
4. Copy your API key
5. Configure in Adastrea Director:
   ```bash
   python main.py --set-api-key gemini
   ```

### Can I use it without an internet connection?

Partially. You can:
- ✅ Use Ollama for local LLM (completely offline)
- ✅ Use HuggingFace embeddings (offline after first download)
- ❌ Cannot use cloud LLM providers (Gemini, OpenAI)

### Installation fails on Apple Silicon Mac. What should I do?

Use the smart installer which handles Apple Silicon dependencies:
```bash
python install_dependencies.py
```

It will guide you through any platform-specific steps needed.

### "No module named 'tkinter'" error. How do I fix it?

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**macOS:**
```bash
brew install python-tk
```

**Windows:** tkinter is included with Python on Windows. Reinstall Python if missing.

## Usage Questions

### How do I start using Adastrea Director?

1. Install: `./setup.sh`
2. Configure API key: `python main.py --set-api-key gemini`
3. Ingest docs: `python ingest.py --docs-dir /path/to/docs`
4. Start using: `python main.py`

See [Quick Start Tutorial](Quick-Start.md) for details.

### Why is my first query so slow?

The first query loads the embedding model and LLM, which can take 5-10 seconds. Subsequent queries are much faster (1-3 seconds). This is normal behavior.

### How do I populate the knowledge base?

Use the ingestion script:
```bash
# Ingest your documentation
python ingest.py --docs-dir /path/to/your/docs

# For Adastrea game developers
python ingest_game_repo.py
```

See [Document Ingestion Guide](../usage/Document-Ingestion.md) for details.

### Can I ingest code files?

Yes! Supported file types include:
- `.md`, `.txt`, `.rst` - Documentation
- `.py`, `.cpp`, `.h`, `.cs` - Code files
- Custom types via `--file-types` flag

### How do I update the knowledge base?

Re-run ingestion with the `--update` flag:
```bash
python ingest.py --docs-dir /path/to/docs --update
```

This will process new/changed files without re-processing everything.

### What kind of questions can I ask?

Ask natural language questions about your project:
- "What is the main gameplay loop?"
- "How do I implement feature X?"
- "Where is the player movement code?"
- "What are the requirements for Y?"
- "Explain the architecture of Z"

Be specific for best results!

### Why am I getting "I don't have enough information" responses?

Possible reasons:
1. **Not enough documents ingested:** Ingest relevant documentation
2. **Question too vague:** Be more specific
3. **Information not in documents:** Add relevant docs
4. **Wrong context:** Rephrase your question

### Can I export conversations?

Yes! In the GUI:
- Press `Ctrl+E` or use File → Export Conversation
- Choose format (text, markdown, JSON)

## Planning System (P2)

### What is the Planning System?

The Planning System (Phase 2) breaks down high-level development goals into actionable tasks with dependencies, priorities, and code suggestions.

### How do I use the planner?

```bash
# Interactive mode
python planner.py --interactive

# Single goal
python planner.py "Your goal here"

# Export plan
python planner.py "Your goal" --export markdown --output plan.md
```

See [Planning System Guide](../usage/Planning-System.md) for details.

### What format can I export plans in?

- **Markdown** - For documentation and sharing
- **JSON** - For programmatic use
- **Text** - Simple text format

### Can the planner generate code?

Yes! The planner suggests implementation approaches with code examples. However, you should review and adapt the code for your specific needs.

## Autonomous Agents (P3)

### What are autonomous agents?

Autonomous agents (Phase 3) are proactive AI assistants that monitor your project for performance issues, bugs, and code quality problems without requiring manual queries.

### How do I start agents?

```bash
# Start all agents
python agent_orchestrator_cli.py start --all

# Check status
python agent_orchestrator_cli.py status

# View dashboard
python agent_dashboard.py --auto-start
```

See [Autonomous Agents Guide](../usage/Autonomous-Agents.md) for details.

### What agents are available?

Currently available agents:
- **Performance Agent:** Monitors performance metrics
- **Bug Detection Agent:** Identifies potential bugs
- **Code Quality Agent:** Reviews code quality

More agents coming in future phases!

### Can I create custom agents?

Not yet, but this is planned for a future release. Check the [main README](https://github.com/Mittenzx/Adastrea-Director#readme) for the current roadmap.

## Unreal Engine Plugin

### How do I install the Unreal Engine plugin?

1. Copy `Plugins/AdastreaDirector` to your UE project's `Plugins` folder
2. Regenerate project files
3. Build your project
4. Launch UE Editor
5. Open **Window → Developer Tools → Adastrea Director**

See [Plugin Setup Guide](Plugin-Setup.md) for details.

### What UE versions are supported?

Unreal Engine 5.0 and later are supported.

### Do I need the standalone version if I use the plugin?

No, the plugin includes the Python backend. However, the standalone version is useful for:
- Testing and development
- Features not yet in the plugin
- Non-UE projects

### Can I use the plugin and standalone together?

Yes! They can run simultaneously and even share the same knowledge base.

## Technical Questions

### Where is data stored?

- **Vector Database:** `./chroma_db` (configurable)
- **Configuration:** `~/.adastrea/config.json`
- **Logs:** `./logs` (if enabled)

### Is my data private?

Yes! Data is stored locally except for:
- LLM API calls (sent to provider)
- Optional telemetry (disabled by default)

Use Ollama for completely local, private operation.

### Can I use a different LLM provider?

Yes! Supported providers:
- Google Gemini
- OpenAI (GPT-3.5, GPT-4)
- Ollama (local)

Configure via settings or command line.

### Can I use GPU acceleration?

Yes! If you have a CUDA-compatible GPU:
- HuggingFace embeddings automatically use GPU
- Some LLM providers support GPU
- Check with `nvidia-smi` to verify GPU usage

### How much does it cost to run?

**Free Option:**
- Google Gemini free tier (generous limits)
- HuggingFace embeddings (free, offline)
- **Total cost: $0/month**

**Paid Option:**
- OpenAI API (pay-per-use, typically $0.01-$0.10 per query)
- OpenAI embeddings (optional)

### How do I backup my data?

Backup these directories:
- `./chroma_db` - Vector database
- `~/.adastrea/config.json` - Configuration

```bash
# Backup command
tar -czf adastrea-backup.tar.gz chroma_db ~/.adastrea/config.json
```

## Troubleshooting

### The GUI won't start

1. Check tkinter is installed: `python -m tkinter`
2. Try CLI mode: `python main.py`
3. Check error logs
4. See [Troubleshooting Guide](Troubleshooting.md)

### Queries are very slow

1. First query is always slow (model loading) - normal
2. Check internet connection (for cloud LLMs)
3. Check GPU usage: `nvidia-smi`
4. Consider using lighter models

### "API key not found" error

Configure your API key:
```bash
# Via CLI
python main.py --set-api-key gemini
```

### More troubleshooting help?

See the comprehensive [Troubleshooting Guide](Troubleshooting.md).

## Contributing

### How can I contribute?

See [Contributing Guide](../development/Contributing.md) for details on:
- Code contributions
- Documentation improvements
- Bug reports
- Feature requests

### I found a bug. What should I do?

1. Check [existing issues](https://github.com/Mittenzx/Adastrea-Director/issues)
2. If not reported, [create a new issue](https://github.com/Mittenzx/Adastrea-Director/issues/new)
3. Include:
   - Description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Error logs (if any)

### Can I suggest new features?

Yes! We welcome feature suggestions:
1. Check [discussions](https://github.com/Mittenzx/Adastrea-Director/discussions)
2. Create a new discussion with your idea
3. Explain the use case and benefits

## Getting More Help

### Where can I get help?

- **📖 Wiki:** [Comprehensive documentation](../Home.md)
- **🐛 Issues:** [Report bugs](https://github.com/Mittenzx/Adastrea-Director/issues)
- **💬 Discussions:** [Ask questions](https://github.com/Mittenzx/Adastrea-Director/discussions)
- **📧 Contact:** [@Mittenzx](https://github.com/Mittenzx)

### Is there a community?

Join the discussions on GitHub:
- [GitHub Discussions](https://github.com/Mittenzx/Adastrea-Director/discussions)

### Where can I find examples?

Check the `examples/` directory in the repository:
- Phase 1 examples (RAG usage)
- Phase 2 examples (Planning)
- Phase 3 examples (Agents)

---

**Didn't find your answer?** [Ask in Discussions](https://github.com/Mittenzx/Adastrea-Director/discussions) or [create an issue](https://github.com/Mittenzx/Adastrea-Director/issues/new).

[← Back to Installation](Getting-Started.md) | [Troubleshooting →](Troubleshooting.md)
