# Adastrea Director - AI Game Director

An intelligent assistant system designed to understand natural language commands and assist with the game development lifecycle in Unreal Engine.

> 📚 **Documentation:** See [Adastrea Director Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki) for complete documentation.
> 
> 🏗️ **Architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md) for system architecture, VibeUE modernization, and component overview.

## Overview

Adastrea Director is an AI-powered tool that aims to revolutionize game development by providing context-aware assistance, automated planning, and eventually autonomous development capabilities. The project is being developed in four distinct phases, with each phase building upon the previous one.

## Value Proposition

**Current Value (P1-P3):** ⭐⭐⭐⭐⭐⭐⭐⭐⭐ 9/10
- Context-aware documentation search across all project guides
- Intelligent planning and task decomposition for development goals
- Code generation assistance with multiple implementation approaches
- **✨ Autonomous agents for performance profiling, bug detection, and code quality**
- Real-time monitoring and proactive issue detection
- 230+ comprehensive tests across Phases P1–P3 (including 120+ Phase 3 autonomous-agent tests, all 100% passing) for production-ready stability
- **ROI: 300%+ return in 6 months** with automated profiling and bug detection

**Future Potential (P4 + Plugin):** ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ 10/10
- Integrated UE Editor experience with all P1-P3 capabilities
- AI-assisted content generation (quests, dialogue, assets)
- Real-time in-editor performance profiling and optimization
- Automated playtesting with reproduction steps
- **ROI: 400%+ return** with full autonomous development assistance

*For detailed analysis, see the [Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki)*

## Architecture: One System, Two Deployment Options

Adastrea Director is **one AI system** with **two deployment modes**:

### 🖥️ Standalone Mode (Python GUI/CLI)
- **Purpose:** Development, testing, and standalone use
- **Technology:** Python + tkinter/CLI
- **Best for:** Rapid prototyping, testing, non-UE users
- **Status:** ✅ Fully functional (P1-P3)

### 🎮 Plugin Mode (Unreal Engine - VibeUE Architecture)
- **Purpose:** Native C++ integration in Unreal Editor
- **Technology:** Modern C++ with direct LLM integration (no external processes)
- **Architecture:** VibeUE pattern - IPythonScriptPlugin, direct HTTP, runtime queries
- **Best for:** Production UE development with integrated AI assistance
- **Status:** ✅ Core VibeUE components complete (AdastreaScriptService, LLMClient, AssetService, ToolSystem, MCPServer)
- **Legacy:** Old IPC components maintained for transition, will be removed in Phase 4

**Key Point:** The plugin now uses the **VibeUE architecture** with native C++ components (no external Python process needed). The standalone system remains fully functional for development, testing, and non-UE use cases.

📖 **See:** [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system architecture and [Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki) for complete documentation.

## Current Phase: P3 Complete - Plugin Integration Focus

Phase 3 has been **completed successfully** with fully implemented autonomous agents for performance profiling, bug detection, and code quality monitoring. The system now includes:
- ✅ Three fully functional autonomous agents (Performance, Bug Detection, Code Quality)
- ✅ Agent Orchestrator CLI for managing agents
- ✅ Real-time Dashboard UI for monitoring agent activity
- ✅ Complete infrastructure (Event Bus, Shared State, Remote Control API)

**🎯 Current Focus:** VibeUE Architecture Complete - Testing & Migration Planning

The C++ plugin has been successfully modernized with the VibeUE architecture:
- ✅ Direct LLM integration (AdastreaLLMClient) - no Python process needed
- ✅ Built-in Python execution (AdastreaScriptService) via IPythonScriptPlugin
- ✅ Runtime asset discovery (AdastreaAssetService) - no document ingestion
- ✅ Tool system (AdastreaToolSystem) for extensible AI capabilities
- ✅ MCP server (AdastreaMCPServer) for external AI clients

See [VIBEUE_COMPLETION_SUMMARY.md](VIBEUE_COMPLETION_SUMMARY.md) for implementation details.

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

**Current Focus:** Unreal Engine Plugin Integration (P1-P3 features in UE Editor)

**Completed:**
- ✅ Phase 1: Foundation (RAG-based Q&A)
- ✅ Phase 2: The Planner (Goal decomposition and task planning)
- ✅ Phase 3: Autonomous Agents (Performance, Bug Detection, Code Quality)
- ✅ Standalone Python application (CLI + GUI)

**In Progress:**
- 🚀 UE Plugin Weeks 7-16: Planning agent integration and UI/UX improvements

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
   
3. **Phase 3: The Proactive Agent System** - ✅ *Complete*
   - ✅ Autonomous performance profiling and optimization
   - ✅ Automated bug detection and crash analysis
   - ✅ Code quality monitoring and refactoring suggestions
   - ✅ Agent Orchestrator CLI for managing agents
   - ✅ Real-time Dashboard UI for monitoring
   - ✅ 120+ comprehensive tests (100% passing)
   - ✅ Remote Control API client module (67 tests, ready for integration)
     - 📝 **[Integration Status](REMOTE_CONTROL_INTEGRATION_STATUS.md)** - Not yet integrated with GUI/VSCode
     - 🚀 **[Quick Integration Guide](REMOTE_CONTROL_QUICK_INTEGRATION.md)** - 5-minute setup
   - ✅ Event bus implementation (16 tests)
   - ✅ Shared state management (20 tests)
   - ✅ MCP Server integration for AI agent access (84 tests)
   
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
- **Quick Status**: [INGESTION_STATUS.md](Documentation/development/INGESTION_STATUS.md) - Current status and quick reference
- **Complete Guide**: [GAME_REPO_INGESTION_GUIDE.md](Documentation/guides/GAME_REPO_INGESTION_GUIDE.md) - Detailed instructions and troubleshooting
- **Quick Start**: [START_HERE_INGESTION.md](Documentation/guides/START_HERE_INGESTION.md) - 60-second setup guide

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

3. **Verify your installation and test API keys:**

**⚠️ Run from system terminal, NOT UE Python console!**

```bash
# Test that all dependencies are installed and API keys work
python test_api_keys.py

# Test specific provider
python test_api_keys.py --provider gemini

# Check configuration without making API calls
python test_api_keys.py --skip-api-test
```

This script will help you diagnose any issues with dependencies or API key configuration.

**Note:** If run from Unreal Engine's Python console, you'll see "Dependencies NOT INSTALLED" 
messages. This is expected - the script should be run from your system terminal. See 
TROUBLESHOOTING.md for details.

4. Set up your LLM API key:

**For document embeddings:** The system uses **HuggingFace embeddings by default** (no API key required, works offline).
- See the [Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki) for OpenAI embeddings setup if needed

**For LLM queries:** Set up your preferred LLM provider. You have four options:

**Option A: Save to local config (Recommended - persists across repository clones)**
```bash
# Via CLI
python main.py --set-api-key gemini  # or openai, or openrouter

# Via GUI
# When prompted, check "Save API key for future sessions"
```
Keys are securely stored in `~/.adastrea/config.json` and encrypted with a machine-specific key.

**Option B: Use environment variable**
```bash
export GEMINI_KEY="your-api-key-here"
# or for OpenAI
export OPENAI_API_KEY="your-api-key-here"
# or for OpenRouter
export OPENROUTER_API_KEY="your-api-key-here"
```

**Option C: Use .env file**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY
```

**Option D: Select provider in GUI Settings**
Open the Settings dialog (⚙️) and configure your preferred provider and API key.

**Priority:** Local config → Environment variables (including .env file)

**🔍 Test your configuration:**
After setting up your API key, verify it works:
```bash
python test_api_keys.py
```

5. **(Optional)** Set up GitHub token for game repository ingestion:
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

3. **Run the planning example:**
```bash
python examples/planning_example.py
```

**📋 Want to learn more?** See the [Planning Guide](https://github.com/Mittenzx/Adastrea-Director/wiki) in the Wiki for comprehensive documentation with examples.

#### P3: Autonomous Agents (Complete! ✅)

The autonomous agent system is fully implemented and operational. Manage and monitor agents for performance profiling, bug detection, and code quality:

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

👉 **[Plugin Setup Guide](Plugins/AdastreaDirector/Documentation/guides/SETUP_GUIDE.md)** - Get started in 5 minutes!

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
- **[Setup Guide](Plugins/AdastreaDirector/Documentation/guides/SETUP_GUIDE.md)** - 🌟 **Start here!** Quick setup and testing
- [Plugin README](Plugins/AdastreaDirector/README.md) - Full plugin guide
- [UE Python API Guide](Plugins/AdastreaDirector/Documentation/features/UE_PYTHON_API.md) - **NEW!** UE Python integration
- **[Python Research Document](Documentation/research/PYTHON_RESEARCH_UE427.md)** - 📚 **NEW!** Complete UE Python API capabilities (UE 4.27-5.7)
- [Installation Guide](Plugins/AdastreaDirector/Documentation/guides/INSTALLATION.md) - Detailed setup
- [RAG Integration](Plugins/AdastreaDirector/Documentation/features/RAG_INTEGRATION.md) - Using the RAG system
- [Testing Quick Reference](Plugins/AdastreaDirector/Documentation/guides/TESTING_QUICK_REFERENCE.md) - Verify installation

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

**🔗 Related Project:** [Adastrea-MCP](https://github.com/Mittenzx/Adastrea-MCP) - Complementary MCP server providing static analysis, code generation, and UE5.6+ knowledge (37 tools). Can integrate with Adastrea-Director for comprehensive UE development assistance. See [MCP Integration Architecture](Documentation/architecture/MCP_INTEGRATION_ARCHITECTURE.md) for details.


## Project Structure

```
Adastrea-Director/
├── README.md                      # This file - Quick start guide
├── CONTRIBUTING.md                # Contribution guidelines
├── Documentation/                 # Organized documentation (UE standards)
│   ├── guides/                    # User guides and tutorials
│   ├── implementation/            # Implementation summaries
│   ├── architecture/              # Architecture and design docs
│   ├── research/                  # Research and exploration
│   └── development/               # Development status docs
├── requirements.txt               # Python dependencies
├── ingest.py                      # Document ingestion script
├── ingest_game_repo.py            # Game repository ingestion
├── main.py                        # P1 CLI entry point
├── planner.py                     # P2 planning CLI

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
- **[COPILOT_INSTRUCTIONS.md](Documentation/development/COPILOT_INSTRUCTIONS.md)** - 📖 Complete guide for Copilot agents with connection methods, capabilities, and verification procedures
- **[.github/COPILOT_QUICK_REFERENCE.md](.github/COPILOT_QUICK_REFERENCE.md)** - 🚀 Quick reference card for common operations

### 🤖 GitHub Copilot Integration

**NEW: MCP Server Integration** ✨

GitHub Copilot in VS Code can now directly use Adastrea Director's MCP (Model Context Protocol) server to interact with Unreal Engine! The repository includes pre-configured VS Code settings in `.vscode/settings.json` that enable Copilot to:

- Execute Python code directly in Unreal Engine Editor
- Query project information and list assets
- Create and manipulate actors in the level
- Access Director's RAG knowledge base
- Get context-aware assistance for UE development

**Quick Setup:**
1. Open this repository in VS Code
2. Ensure GitHub Copilot extension is installed
3. Start Unreal Engine with Python Editor Script Plugin enabled
4. Ask Copilot: `Use the adastrea-unreal server to get project information`

See **[.vscode/README.md](.vscode/README.md)** for complete setup instructions and troubleshooting.

**Debugging UE Logs:**
Want GitHub Copilot to help debug UE crashes and errors? See **[COPILOT_UE_LOGS_GUIDE.md](Documentation/guides/COPILOT_UE_LOGS_GUIDE.md)** for details on how Copilot can access Unreal Engine output logs for better assistance.



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
