# Adastrea Director - AI Game Director

An intelligent assistant system designed to understand natural language commands and assist with the game development lifecycle in Unreal Engine.

> 📚 **Documentation Update:** All detailed documentation has been moved to the [Adastrea Director Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki) for better organization and accessibility. See [WIKI_MIGRATION.md](WIKI_MIGRATION.md) for details.

## Overview

Adastrea Director is an AI-powered tool that aims to revolutionize game development by providing context-aware assistance, automated planning, and eventually autonomous development capabilities. The project is being developed in four distinct phases, with each phase building upon the previous one.

## Value Proposition

**Current Value (P1-P2):** ⭐⭐⭐⭐⭐⭐⭐ 7/10
- Context-aware documentation search across all project guides
- Intelligent planning and task decomposition for development goals
- Code generation assistance with multiple implementation approaches
- 230 comprehensive tests (100% passing), production-ready stability
- **ROI: 210% return in 6 months** with 2-month payback period

**Future Potential (P3-P4):** ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ 10/10
- Autonomous performance profiling and optimization in Unreal Engine
- Automated bug detection and playtesting with reproduction steps
- Real-time code quality monitoring and refactoring suggestions
- AI-assisted content generation (quests, dialogue, assets)
- **ROI: 63% return in 12 months**, then $40k+ annually

*For detailed analysis, see the [Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki)*

## Architecture: One System, Two Deployment Options

Adastrea Director is **one AI system** with **two deployment modes**:

### 🖥️ Standalone Mode (Python GUI/CLI)
- **Purpose:** Development, testing, and standalone use
- **Technology:** Python + tkinter/CLI
- **Best for:** Rapid prototyping, testing, non-UE users
- **Status:** ✅ Fully functional (P1-P3)

### 🎮 Plugin Mode (Unreal Engine)
- **Purpose:** Integrated in-editor workflow
- **Technology:** C++ (UE Plugin) + same Python backend
- **Best for:** Game developers working in Unreal Engine
- **Status:** 🚀 In development (Weeks 1-6 complete: basic UI + RAG)

**Key Point:** Both modes use the **same Python backend** (RAG, Planning, Agents). The plugin is not a separate implementation—it's a wrapper that integrates the standalone system into Unreal Engine via IPC.

📖 **See:** [Architecture Documentation](https://github.com/Mittenzx/Adastrea-Director/wiki) in the Wiki for complete details

## Current Phase: P2 Complete - Ready for P3

P2 has been **completed successfully** with intelligent goal decomposition, task planning, and code generation capabilities. The system can now break down high-level development goals into concrete, actionable tasks with dependencies, priorities, and effort estimates.

**🎯 Status:** P2 complete (PR #45) - Ready to begin P3 (Autonomous Agents)

P2 introduces intelligent planning capabilities that transform high-level development goals into actionable implementation plans with code suggestions, building on P1's foundation by adding **intelligent goal decomposition** - the ability to break down high-level development goals into concrete, actionable tasks with dependencies, priorities, and effort estimates.

### Features

- ✅ **P1: Foundation** - RAG-based document understanding and Q&A
- ✨ **P2: The Planner** (Complete):
  - **Goal Analysis**: Parse natural language development goals and classify them
  - **Task Decomposition**: Automatically break down goals into prioritized tasks
  - **Dependency Management**: Identify task dependencies and optimal execution order
  - **Code Generation**: Generate implementation approaches with code examples
  - **Feasibility Analysis**: Assess complexity and provide recommendations
  - **Plan Export**: Export plans in Markdown, JSON, or Text formats
  - **Interactive Planning CLI**: New dedicated planning interface
  - **Effort Estimation**: Estimate time and complexity for tasks
  - **Priority Assignment**: Intelligent task prioritization

## 📋 Project Status

**Active Development:** P3 Remote Control Integration + Plugin P2.4.1

For detailed project roadmap, sprint planning, and task tracking, see the [Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki).

---

## Project Phases

1. **P1: Foundation (Context-Aware Assistant)** - ✅ *Complete*
   - RAG-based document understanding
   - Natural language query interface
   - Document ingestion and vector database
   
2. **P2: The Planner (Goal-Oriented Tasking)** - ✅ *Complete*
   - Goal analysis and classification
   - Task decomposition with dependencies
   - Action plan generation
   - Effort estimation and prioritization
   
3. **Phase 3: The Proactive Agent System** - 🚀 *Prerequisites Complete - Ready for Agents*
   - Autonomous performance profiling and optimization
   - Automated bug detection and crash analysis
   - Code quality monitoring and refactoring suggestions
   - **NEW:** Agent Orchestrator CLI for managing agents
   - **NEW:** Real-time Dashboard UI for monitoring
   - **NEW:** 120 comprehensive tests (100% passing)
   - **COMPLETE:** Remote Control API integration (67 tests)
   - **COMPLETE:** Event bus implementation (16 tests)
   - **COMPLETE:** Shared state management (20 tests)
   - **NEW:** MCP Server integration for AI agent access (84 tests)
   
4. **P4: Creative Partner** - 🌟 *Vision*
   - AI-assisted content generation
   - Creative design suggestions

## Getting Started

### Prerequisites

- Python 3.9 or higher (Python 3.12+ recommended for best compatibility)
- pip package manager
- (Optional) GitHub Personal Access Token for game repository ingestion

### Quick Start: Populate the Database

**⚡ Want to start using Adastrea Director immediately with full game context?**

**🎉 NEW: HuggingFace access is now enabled! Game repository ingestion is ready to use.**

Populate the database with your game repository so all agents have access to your codebase:

**Method 1: Quick Ingestion Script (Easiest)**
```bash
./quick_ingest_game.sh
```

**Method 2: Manual Ingestion**
```bash
# Set your GitHub token (for private repository access, if needed)
export GITHUB_TOKEN="ghp_your_token_here"

# Populate the database (uses HuggingFace embeddings - no API key required!)
python3 ingest_game_repo.py
```

**Method 3: Use GitHub Actions (Automated) ⭐**
1. Add `GAME_REPO_TOKEN` secret in [repository settings](https://github.com/Mittenzx/Adastrea-Director/settings/secrets/actions)
2. Go to [Actions](https://github.com/Mittenzx/Adastrea-Director/actions) → "Populate Database with Adastrea Game Repository"
3. Click "Run workflow"

📖 **Documentation:**
- **Quick Status**: [INGESTION_STATUS.md](INGESTION_STATUS.md) - Current status and quick reference
- **Complete Guide**: [GAME_REPO_INGESTION_GUIDE.md](GAME_REPO_INGESTION_GUIDE.md) - Detailed instructions and troubleshooting
- **Quick Start**: [START_HERE_INGESTION.md](START_HERE_INGESTION.md) - 60-second setup guide

Once populated, all agents will have full context about your Adastrea game when providing assistance!

### Installation

#### Quick Setup (All Platforms)

```bash
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director
./setup.sh  # Linux/Mac
```

The setup script will:
- Check your system compatibility
- Create a virtual environment (reusable for fast subsequent runs)
- Install all dependencies with platform-specific handling
- Verify the installation

**💡 Tip**: The virtual environment can be reused - just activate it with `source venv/bin/activate` for instant access without reinstalling dependencies.

#### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director
```

2. Install dependencies:

**Option A: Smart Installer (Recommended)**
```bash
python install_dependencies.py
```
This script will detect your platform and guide you through any platform-specific setup needed.

**Option B: Direct Installation**
```bash
pip install -r requirements.txt
```

**📝 Note**: If you encounter issues (especially on Apple Silicon Macs or ARM systems), use the smart installer or see the [Installation Guide](https://github.com/Mittenzx/Adastrea-Director/wiki) in the Wiki for platform-specific instructions and troubleshooting.

3. Set up your LLM API key:

**For document embeddings:** The system uses **HuggingFace embeddings by default** (no API key required, works offline).
- See the [Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki) for OpenAI embeddings setup if needed

**For LLM queries:** Set up your preferred LLM provider. You have three options:

**Option A: Save to local config (Recommended - persists across repository clones)**
```bash
# Via CLI
python main.py --set-api-key gemini

# Via GUI
# When prompted, check "Save API key for future sessions"
```
Keys are securely stored in `~/.adastrea/config.json` and encrypted with a machine-specific key.

**Option B: Use environment variable**
```bash
export GEMINI_KEY="your-api-key-here"
# or for OpenAI
export OPENAI_API_KEY="your-api-key-here"
```

**Option C: Use .env file**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_KEY
```

**Priority:** Local config → Environment variables (including .env file)

4. **(Optional)** Set up GitHub token for game repository ingestion:
```bash
export GITHUB_TOKEN="your-github-token-here"
```
This is only needed if you want to ingest documents from the private Mittenzx/Adastrea game repository. 

**📖 For detailed setup guides**, see the [Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki)

### Usage

**💡 Which mode should I use?**

| Use Case | Recommended Mode | Why |
|----------|------------------|-----|
| Working in Unreal Engine | 🎮 **Plugin** | Integrated workflow, no context switching |
| Testing/prototyping new features | 🖥️ **Standalone** | Faster iteration, easier debugging |
| Non-UE game development | 🖥️ **Standalone** | Works with any project type |
| Plugin is not yet feature-complete | 🖥️ **Standalone** | All features available immediately |

Both modes share the same AI backend, so you get the same quality of results!

#### Planning System (P2 - Complete!)

Create implementation plans for your development goals:

```bash
# Interactive planning mode
python planner.py --interactive

# Plan a specific goal
python planner.py "Add a new inventory system"

# Export plan to file
python planner.py "Optimize rendering pipeline" --export markdown --output plan.md

# Enable debug logging for troubleshooting
python planner.py --debug "Optimize rendering pipeline"
```

The planning system will:
- Analyze your goal and identify requirements
- Break it down into prioritized tasks with dependencies
- Estimate effort and assess feasibility
- Suggest implementation approaches with code examples
- Export a complete plan for review

**Debugging & Logging:**
All commands support `--debug` flag for detailed logging output. Logs are saved to `logs/adastrea_YYYYMMDD.log` and can be viewed in the GUI's Debug Logs tab

#### Context-Aware Assistant (P1)

1. **Ingest your project documents:**
```bash
python ingest.py --docs-dir /path/to/your/docs
```

**📚 For detailed ingestion guides**, see the [Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki)

**🎮 Working on the Mittenzx/Adastrea game?** Use the dedicated game repository ingestion:
```bash
python ingest_game_repo.py
```

2. **Start the interactive assistant:**
```bash
python main.py
```

3. **Ask questions about your project:**
```
> What is the main gameplay loop?
> Describe the player character abilities
> What are the performance requirements?
```

#### P2: Goal Decomposition

1. **Interactive goal planning:**
```bash
python planning_cli.py --interactive
```

2. **Single goal with markdown export:**
```bash
python planning_cli.py --goal "Implement user authentication system" --output action_plan.md
```

3. **Run the P2 example:**
```bash
python examples/phase2_example.py
```

**📋 Want to learn more?** See the [Phase 2 Guide](https://github.com/Mittenzx/Adastrea-Director/wiki) in the Wiki for comprehensive documentation with examples.

#### P3: Autonomous Agents (In Progress!)

Manage and monitor autonomous agents for performance profiling, bug detection, and code quality:

1. **Agent Orchestrator CLI - Control agents from command line:**
```bash
# Start all agents
python agent_orchestrator_cli.py start --all

# Check agent status
python agent_orchestrator_cli.py status

# View recent events
python agent_orchestrator_cli.py events --limit 20

# Stop specific agent
python agent_orchestrator_cli.py stop --agent performance
```

2. **Agent Dashboard - Real-time monitoring:**
```bash
# Start dashboard with auto-start
python agent_dashboard.py --auto-start

# Custom update interval
python agent_dashboard.py --interval 2.0
```

3. **Run the P3 demo:**
```bash
python examples/phase3_orchestrator_demo.py
```

**📋 Documentation:** See the [Phase 3 Guide](https://github.com/Mittenzx/Adastrea-Director/wiki) in the Wiki for complete documentation

#### Unreal Engine Plugin

For game developers working in Unreal Engine, the plugin provides an integrated in-editor experience:

**Current Status:** Weeks 1-6 Complete (Basic UI + RAG Integration) + **NEW: UE Python API Integration** ✨

**🚀 Quick Start:**

👉 **[Plugin Setup Guide](Plugins/AdastreaDirector/SETUP_GUIDE.md)** - Get started in 5 minutes!

**Installation (Quick):**
1. Copy `Plugins/AdastreaDirector` to your UE project's `Plugins` folder
2. Regenerate project files (right-click .uproject → Generate Visual Studio project files)
3. Build your project
4. Launch Unreal Engine Editor

**Usage:**
1. Open **Window → Developer Tools → Adastrea Director**
2. The AI assistant panel opens as a dockable tab
3. Use the Ingestion tab to add your documentation
4. Use the Query tab to ask questions
5. Python backend starts automatically!

**NEW: UE Python API Features** ✨
- ✅ Direct access to Unreal Engine's Python API (`import unreal`)
- ✅ Asset operations (query, load, save)
- ✅ Actor operations (spawn, query, delete)
- ✅ Console command execution
- ✅ Editor automation (notifications, logging)
- ✅ Hybrid architecture (External Python + UE Python)
- ✅ **Content generation utilities** - Procedural layouts, material libraries, Blueprint creation
- ✅ **Content validation framework** - Automated asset validation and standards compliance
- ✅ **Batch processing** - Mass operations on assets and actors
- ✅ 25+ comprehensive tests (100% passing)

**📖 Complete Plugin Documentation:**
- **[Setup Guide](Plugins/AdastreaDirector/SETUP_GUIDE.md)** - 🌟 **Start here!** Quick setup and testing
- [Plugin README](Plugins/AdastreaDirector/README.md) - Full plugin guide
- [UE Python API Guide](Plugins/AdastreaDirector/UE_PYTHON_API.md) - **NEW!** UE Python integration
- **[Python Research Document](PYTHON_RESEARCH_UE427.md)** - 📚 **NEW!** Complete UE Python API capabilities (UE 4.27-5.7)
- [Installation Guide](Plugins/AdastreaDirector/INSTALLATION.md) - Detailed setup
- [RAG Integration](Plugins/AdastreaDirector/RAG_INTEGRATION.md) - Using the RAG system
- [Testing Quick Reference](Plugins/AdastreaDirector/TESTING_QUICK_REFERENCE.md) - Verify installation

**Coming Soon (Weeks 7-16):**
- Planning agent integration (task breakdown in UE)
- Performance profiling UI
- Bug detection integration
- Code quality monitoring

#### Unreal Engine MCP Integration (NEW!)

Control Unreal Engine directly from the command line using the MCP server integration:

```bash
# Interactive mode - no external client needed
python unreal_mcp_cli.py

# Direct commands
python unreal_mcp_cli.py project-info      # Get project info
python unreal_mcp_cli.py list-assets       # List all assets
python unreal_mcp_cli.py search-assets "player"
python unreal_mcp_cli.py run-python "import unreal; print(unreal.SystemLibrary.get_engine_version())"
```

**Features:**
- ✅ Execute Python directly in Unreal Editor
- ✅ List, search, and inspect assets
- ✅ Create, update, and delete actors
- ✅ Run console commands
- ✅ Get project and level information
- ✅ Works with any MCP-compatible client (5ire, Cline, Zed, etc.)
- ✅ 84 comprehensive tests

**📖 Documentation:** [MCP Server Guide](mcp_server/MCP_SERVER_GUIDE.md)

#### Graphical User Interface (GUI - Standalone)

For a more user-friendly experience, you can use the enhanced GUI application:

```bash
python gui_director.py
```

The improved GUI provides:
- **Modern Dark Theme**: Professional appearance with reduced eye strain
- **Comprehensive Settings Dialog**: Configure API keys, LLM providers, embedding providers, and display options
- **API Key Management**: Secure storage for multiple providers (Gemini, OpenAI)
- **Knowledge Base Updates**: One-click knowledge base updates
- **Ingest List Tab**: Visual checklist of ingested documents with statistics
- **🎮 Unreal MCP Tab**: Direct integration with Unreal Engine via MCP
- **🐛 Debug Logs Tab**: Real-time log viewer with auto-refresh and colorized output
- **Conversation History**: Full conversation display with timestamps and color-coding
- **Keyboard Shortcuts**: Fast workflow with comprehensive keyboard support
- **Copy & Export**: One-click copy to clipboard and export conversations to file
- **Font Size Controls**: Adjustable text size for better accessibility
- **Menu Bar**: File, Edit, and Help menus with full functionality
- **Tooltips**: Helpful hints on all interactive elements
- **Status Feedback**: Real-time status updates with visual indicators
- **Comprehensive Logging**: All operations logged with structured output for debugging

**🎮 Unreal MCP Tab Features:**
- Connect/disconnect to Unreal Engine via MCP server
- Quick access to common tools (Project Info, Map Info, Assets, World Outliner)
- Python code execution directly in Unreal Editor
- Console command execution
- Real-time output display with JSON formatting
- **✨ Automatic UE log capture** - All UE output is saved to dated log files for agent processing

**Keyboard Shortcuts:**
- `Enter` or `Ctrl+Enter` - Send question
- `Ctrl+K` - Set API Key (quick access)
- `Ctrl+,` - Open Settings dialog (comprehensive configuration)
- `Ctrl+U` - Update knowledge base
- `Ctrl+L` - Clear conversation
- `Ctrl+C` - Copy last response (from menu)
- `Ctrl+E` - Export conversation

**Documentation:** See the [GUI Guide](https://github.com/Mittenzx/Adastrea-Director/wiki) in the Wiki for complete feature documentation

**Note**: The GUI application requires tkinter, which is included with most Python installations on Windows and can be installed on Linux/Mac.

## Project Structure

```
Adastrea-Director/
├── README.md                      # This file - Quick start guide
├── CONTRIBUTING.md                # Contribution guidelines
├── WIKI_MIGRATION.md              # Documentation migration manifest
├── UE_LOG_USAGE_GUIDE.md          # Guide for UE log capture and analysis
├── requirements.txt               # Python dependencies
├── ingest.py                      # Document ingestion script
├── ingest_game_repo.py            # Game repository ingestion
├── main.py                        # P1 CLI entry point
├── planner.py                     # P2 planning CLI
├── gui_director.py                # GUI application
├── ue_log_capture.py              # UE log capture module
├── agent_orchestrator_cli.py      # P3 agent CLI
├── agent_dashboard.py             # P3 dashboard
├── agents/                        # Agent system
│   ├── phase3/                    # P3 autonomous agents
│   └── ...                        # P2 planning agents
├── logs/                          # UE output logs (dated files)
├── tests/                         # Comprehensive test suite (230+ tests)
├── examples/                      # Example scripts
├── remote_control/                # Remote control API
└── Plugins/                       # Unreal Engine plugin
    └── AdastreaDirector/          # Plugin implementation

📚 All documentation is now in the Wiki: https://github.com/Mittenzx/Adastrea-Director/wiki
```

## Documentation

📚 **Complete documentation is available in the [Adastrea Director Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki)**

The wiki includes:
- **Installation & Setup** - Platform-specific instructions and troubleshooting
- **Usage Guides** - How to use all features (P1-P3)
- **Architecture** - System design and agent architecture
- **Phase Documentation** - Detailed guides for each project phase
- **Development** - Contributing, testing, and code reference
- **Design System** - UI/UX guidelines
- **API Reference** - Remote control API and integrations
- **[Remote Connection Types & Actions](wiki/Remote-Connection-Types-and-Actions.md)** - Comprehensive directory of all connection types (HTTP, WebSocket, Python IPC, UE Python API, Director Plugin)

### 🤖 For GitHub Copilot and AI Agents

If you're a GitHub Copilot agent or AI assistant working with Adastrea Director:
- **[COPILOT_INSTRUCTIONS.md](COPILOT_INSTRUCTIONS.md)** - 📖 Complete guide for Copilot agents with connection methods, capabilities, and verification procedures
- **[.github/COPILOT_QUICK_REFERENCE.md](.github/COPILOT_QUICK_REFERENCE.md)** - 🚀 Quick reference card for common operations
### 🤖 GitHub Copilot Integration

Want GitHub Copilot to help debug UE crashes and errors? See **[COPILOT_UE_LOGS_GUIDE.md](COPILOT_UE_LOGS_GUIDE.md)** for details on how Copilot can access Unreal Engine output logs for better assistance.



## Testing

Adastrea Director includes a comprehensive test suite to ensure reliability and quality:

### Test Coverage

- **230+ Total Tests**: Covering all major components
- **27 GUI Tests**: Complete UI testing suite (20 functional, 7 integration tests marked for future)
- **88% GUI Coverage**: Thorough testing of UI components
- **100% Pass Rate**: Production-ready stability

### Running Tests

```bash
# Run all tests
pytest

# Run GUI tests specifically
pytest tests/test_gui_director.py -v

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **UI Tests**: User interface behavior testing
- **Error Handling Tests**: Error condition validation
- **Workflow Tests**: Complete user workflow testing

### Manual Testing

For manual testing and QA procedures, see the [Testing Guide](https://github.com/Mittenzx/Adastrea-Director/wiki) in the Wiki.

## Contributing

This project is in early development. Contributions, suggestions, and feedback are welcome!

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

[To be determined]

## Contact

Project maintained by [Mittenzx](https://github.com/Mittenzx)

---

*"Building tomorrow's game development tools, today."*
