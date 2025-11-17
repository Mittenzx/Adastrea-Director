# Adastrea Director - AI Game Director

An intelligent assistant system designed to understand natural language commands and assist with the game development lifecycle in Unreal Engine.

## Overview

Adastrea Director is an AI-powered tool that aims to revolutionize game development by providing context-aware assistance, automated planning, and eventually autonomous development capabilities. The project is being developed in four distinct phases, with each phase building upon the previous one.

## Value Proposition

**Current Value (Phases 1-2):** ⭐⭐⭐⭐⭐⭐⭐ 7/10
- Context-aware documentation search across all project guides
- Intelligent planning and task decomposition for development goals
- Code generation assistance with multiple implementation approaches
- 230 comprehensive tests (100% passing), production-ready stability
- **ROI: 210% return in 6 months** with 2-month payback period

**Future Potential (Phases 3-4):** ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ 10/10
- Autonomous performance profiling and optimization in Unreal Engine
- Automated bug detection and playtesting with reproduction steps
- Real-time code quality monitoring and refactoring suggestions
- AI-assisted content generation (quests, dialogue, assets)
- **ROI: 63% return in 12 months**, then $40k+ annually

*Based on comprehensive analysis: [ADASTREA_DIRECTOR_ANALYSIS.md](ADASTREA_DIRECTOR_ANALYSIS.md)*

## Architecture: One System, Two Deployment Options

Adastrea Director is **one AI system** with **two deployment modes**:

### 🖥️ Standalone Mode (Python GUI/CLI)
- **Purpose:** Development, testing, and standalone use
- **Technology:** Python + tkinter/CLI
- **Best for:** Rapid prototyping, testing, non-UE users
- **Status:** ✅ Fully functional (Phases 1-3)

### 🎮 Plugin Mode (Unreal Engine)
- **Purpose:** Integrated in-editor workflow
- **Technology:** C++ (UE Plugin) + same Python backend
- **Best for:** Game developers working in Unreal Engine
- **Status:** 🚀 In development (Weeks 1-6 complete: basic UI + RAG)

**Key Point:** Both modes use the **same Python backend** (RAG, Planning, Agents). The plugin is not a separate implementation—it's a wrapper that integrates the standalone system into Unreal Engine via IPC.

📖 **See:** [ARCHITECTURE_ANALYSIS.md](ARCHITECTURE_ANALYSIS.md) for complete architecture details

## Current Phase: Phase 2 Complete - Ready for Phase 3

Phase 2 has been **completed successfully** with intelligent goal decomposition, task planning, and code generation capabilities. The system can now break down high-level development goals into concrete, actionable tasks with dependencies, priorities, and effort estimates.

**🎯 Status:** Phase 2 complete (PR #45) - Ready to begin Phase 3 (Autonomous Agents)
Phase 2 introduces intelligent planning capabilities that transform high-level development goals into actionable implementation plans with code suggestions.

### Features (Phase 2 - NEW!)

- **Goal Analysis**: Parse natural language development goals and classify them
- **Task Decomposition**: Automatically break down goals into prioritized tasks
- **Dependency Management**: Identify task dependencies and optimal execution order
- **Code Generation**: Generate implementation approaches with code examples
- **Feasibility Analysis**: Assess complexity and provide recommendations
- **Plan Export**: Export plans in Markdown, JSON, or Text formats
- **Interactive Planning CLI**: New dedicated planning interface
Phase 2 builds on Phase 1's foundation by adding **intelligent goal decomposition** - the ability to break down high-level development goals into concrete, actionable tasks with dependencies, priorities, and effort estimates.

### Features (Phase 2)

- ✅ **Phase 1 - Foundation**: RAG-based document understanding and Q&A
- ✨ **Phase 2 - Planning** (NEW):
  - **Goal Analysis**: Parse and understand development goals
  - **Task Decomposition**: Break goals into actionable tasks
  - **Dependency Management**: Identify task dependencies and create execution graphs
  - **Effort Estimation**: Estimate time and complexity for tasks
  - **Priority Assignment**: Intelligent task prioritization
  - **Action Plans**: Generate comprehensive action plans with markdown export

## 📋 Current Sprint: 2-Week Task List (Nov 17-30, 2025)

**Active Development:** Phase 3 Remote Control Integration + Plugin Week 7-8

**Quick Access:**
- 📖 **[Full Task List](TASKS_2_WEEKS.md)** - Detailed descriptions of all 14 tasks
- 📊 **[Task Board](TASK_BOARD.md)** - Quick status overview and burndown chart
- ✅ **[Sprint Checklist](SPRINT_CHECKLIST.md)** - Daily tracking checklist
- 📝 **[Task List Summary](TASK_LIST_SUMMARY.md)** - High-level summary of all tasks and progress
- 🚀 **[Start Sprint Guide](START_SPRINT.md)** - Step-by-step instructions to kick off the sprint

**This Sprint Focus:**
1. 🎯 Agent Orchestration CLI & Dashboard
2. 🎮 Plugin Week 7-8 Feature Integration (Settings, Shortcuts)
3. 🔌 Remote Control API Foundation for UE Integration
4. 🌐 WebSocket Integration for Real-time Monitoring
5. ⚡ Performance Agent Enhancement with Remote Control
6. 📋 Plugin Planning Agent Integration

**Team:** @Copilot (Remote Control, Agent Enhancement) + @Mittenzx (Plugin Development, UI/UX)

---

## Project Phases

1. **Phase 1: The Foundation (Context-Aware Assistant)** - ✅ *Complete*
   - RAG-based document understanding
   - Natural language query interface
   - Document ingestion and vector database
   
2. **Phase 2: The Planner (Goal-Oriented Tasking)** - ✅ *Complete*
   - Goal analysis and classification
   - Task decomposition with dependencies
   - Action plan generation
   - Effort estimation and prioritization
   
3. **Phase 3: The Proactive Agent System** - 🚀 *In Progress*
   - Autonomous performance profiling and optimization
   - Automated bug detection and crash analysis
   - Code quality monitoring and refactoring suggestions
   - **NEW:** Agent Orchestrator CLI for managing agents
   - **NEW:** Real-time Dashboard UI for monitoring
   - **NEW:** 120 comprehensive tests (100% passing)
   - **IN PROGRESS:** Remote Control API integration for Unreal Engine
   
4. **Phase 4: The Creative Partner** - 🌟 *Vision*
   - AI-assisted content generation
   - Creative design suggestions

## Getting Started

### Prerequisites

- Python 3.9 or higher (Python 3.12+ recommended for best compatibility)
- pip package manager
- (Optional) GitHub Personal Access Token for game repository ingestion

### Quick Start: Populate the Database

**⚡ Want to start using Adastrea Director immediately with full game context?**

Populate the database with your game repository so all agents have access to your codebase:

```bash
# Set your GitHub token (for private repository access)
export GITHUB_TOKEN="ghp_your_token_here"

# Populate the database (uses HuggingFace embeddings - no API key required!)
python ingest_game_repo.py
```

**Alternative: Use GitHub Actions (Recommended) ⭐**
1. Add `GAME_REPO_TOKEN` secret in [repository settings](https://github.com/Mittenzx/Adastrea-Director/settings/secrets/actions)
2. Go to [Actions](https://github.com/Mittenzx/Adastrea-Director/actions) → "Populate Database with Adastrea Game Repository"
3. Click "Run workflow"

📖 **Quick Setup**: [TRIGGER_DATABASE_POPULATION.md](docs/guides/TRIGGER_DATABASE_POPULATION.md)  
📖 **Complete Guide**: [POPULATE_DATABASE.md](docs/guides/POPULATE_DATABASE.md)

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

**💡 Tip**: The virtual environment can be reused - just activate it with `source venv/bin/activate` for instant access without reinstalling dependencies. See [DEPENDENCY_CACHING.md](docs/guides/DEPENDENCY_CACHING.md) for details.

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

**📝 Note**: If you encounter issues (especially on Apple Silicon Macs or ARM systems), use the smart installer or see [INSTALLATION.md](docs/guides/INSTALLATION.md) for platform-specific instructions and troubleshooting.

3. Set up your LLM API key:

**For document embeddings:** The system uses **HuggingFace embeddings by default** (no API key required, works offline).
- See [OpenAI Embeddings Setup Guide](docs/guides/OPENAI_EMBEDDINGS_SETUP.md) if you want to use OpenAI instead

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

**📖 Setup Guides:**
- [Quick Start](docs/guides/QUICK_START_GAME_REPO.md) - 5-minute setup
- [GitHub Secrets Setup](docs/guides/SETUP_GITHUB_SECRETS.md) - CI/CD integration
- [Complete Guide](docs/guides/GAME_REPO_INGESTION.md) - Full documentation
- [OpenAI Embeddings Setup](docs/guides/OPENAI_EMBEDDINGS_SETUP.md) - Optional OpenAI configuration

### Usage

**💡 Which mode should I use?**

| Use Case | Recommended Mode | Why |
|----------|------------------|-----|
| Working in Unreal Engine | 🎮 **Plugin** | Integrated workflow, no context switching |
| Testing/prototyping new features | 🖥️ **Standalone** | Faster iteration, easier debugging |
| Non-UE game development | 🖥️ **Standalone** | Works with any project type |
| Plugin is not yet feature-complete | 🖥️ **Standalone** | All features available immediately |

Both modes share the same AI backend, so you get the same quality of results!

#### Planning System (Phase 2 - NEW!)

Create implementation plans for your development goals:

```bash
# Interactive planning mode
python planner.py --interactive

# Plan a specific goal
python planner.py "Add a new inventory system"

# Export plan to file
python planner.py "Optimize rendering pipeline" --export markdown --output plan.md
```

The planning system will:
- Analyze your goal and identify requirements
- Break it down into prioritized tasks with dependencies
- Estimate effort and assess feasibility
- Suggest implementation approaches with code examples
- Export a complete plan for review

#### Context-Aware Assistant (Phase 1)
#### Phase 1: Context-Aware Assistant

1. **Ingest your project documents:**
```bash
python ingest.py --docs-dir /path/to/your/docs
```

**📚 New to ingestion?** See [DOCS_TO_INGEST.md](docs/guides/DOCS_TO_INGEST.md) for a comprehensive list of documents to ingest and detailed instructions.

**🎮 Working on the Mittenzx/Adastrea game?** Use the dedicated game repository ingestion:
```bash
python ingest_game_repo.py
```
See [Quick Start Guide](docs/guides/QUICK_START_GAME_REPO.md) for 5-minute setup or [GAME_REPO_INGESTION.md](docs/guides/GAME_REPO_INGESTION.md) for complete documentation.

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

#### Phase 2: Goal Decomposition (NEW!)

1. **Interactive goal planning:**
```bash
python planning_cli.py --interactive
```

2. **Single goal with markdown export:**
```bash
python planning_cli.py --goal "Implement user authentication system" --output action_plan.md
```

3. **Run the Phase 2 example:**
```bash
python examples/phase2_example.py
```

**📋 Want to learn more?** See [PHASE2_GUIDE.md](docs/phases/PHASE2_GUIDE.md) for comprehensive Phase 2 documentation with examples.

#### Phase 3: Autonomous Agents (NEW!)

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

3. **Run the Phase 3 demo:**
```bash
python examples/phase3_orchestrator_demo.py
```

**📋 Documentation:** 
- [Agent Orchestration Guide](docs/phases/AGENT_ORCHESTRATION.md) - Complete CLI and Dashboard documentation
- [PHASE3_GUIDE.md](PHASE3_GUIDE.md) - Autonomous agents user guide

#### Unreal Engine Plugin

For game developers working in Unreal Engine, the plugin provides an integrated in-editor experience:

**Current Status:** Weeks 1-6 Complete (Basic UI + RAG Integration) + **NEW: UE Python API Integration** ✨

**Installation:**
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
- ✅ 25 comprehensive tests (100% passing)

**📖 Complete Plugin Documentation:**
- [Plugin README](Plugins/AdastreaDirector/README.md) - Full plugin guide
- [UE Python API Guide](Plugins/AdastreaDirector/UE_PYTHON_API.md) - **NEW!** UE Python integration
- [Installation Guide](Plugins/AdastreaDirector/INSTALLATION.md) - Detailed setup
- [RAG Integration](Plugins/AdastreaDirector/RAG_INTEGRATION.md) - Using the RAG system
- [Testing Quick Reference](Plugins/AdastreaDirector/TESTING_QUICK_REFERENCE.md) - Verify installation

**Coming Soon (Weeks 7-16):**
- Planning agent integration (task breakdown in UE)
- Performance profiling UI
- Bug detection integration
- Code quality monitoring

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
- **Conversation History**: Full conversation display with timestamps and color-coding
- **Keyboard Shortcuts**: Fast workflow with comprehensive keyboard support
- **Copy & Export**: One-click copy to clipboard and export conversations to file
- **Font Size Controls**: Adjustable text size for better accessibility
- **Menu Bar**: File, Edit, and Help menus with full functionality
- **Tooltips**: Helpful hints on all interactive elements
- **Status Feedback**: Real-time status updates with visual indicators

**Keyboard Shortcuts:**
- `Enter` or `Ctrl+Enter` - Send question
- `Ctrl+K` - Set API Key (quick access)
- `Ctrl+,` - Open Settings dialog (comprehensive configuration)
- `Ctrl+U` - Update knowledge base
- `Ctrl+L` - Clear conversation
- `Ctrl+C` - Copy last response (from menu)
- `Ctrl+E` - Export conversation

**Documentation:**
- [GUI Improvements](docs/gui/GUI_IMPROVEMENTS.md) - Complete feature guide
- [GUI Settings](docs/gui/GUI_SETTINGS.md) - Settings configuration guide
- [GUI Testing](docs/testing/GUI_TESTING_GUIDE.md) - Testing procedures

**Note**: The GUI application requires tkinter, which is included with most Python installations on Windows and can be installed on Linux/Mac.

## Project Structure

```
Adastrea-Director/
├── README.md                      # This file
├── PROJECT_PLAN.md                # Detailed project roadmap
├── AGENTS.md                      # Agent system architecture
├── requirements.txt               # Python dependencies
├── ingest.py                      # Document ingestion script
├── ingest_game_repo.py            # Game repository ingestion (NEW!)
├── main.py                        # Phase 1 CLI entry point
├── planner.py                     # Phase 2 planning CLI (NEW!)
├── gui_director.py                # GUI application (enhanced)
├── agents/                        # Phase 2 agent system (NEW!)
│   ├── models.py                  # Data models for planning
│   ├── goal_analysis_agent.py     # Goal analysis agent
│   ├── task_decomposition_agent.py # Task decomposition agent
│   └── code_generation_agent.py   # Code generation agent
├── tests/                         # Comprehensive test suite
│   ├── test_planning_models.py    # Phase 2 model tests (NEW!)
│   ├── test_planning_agents.py    # Phase 2 agent tests (NEW!)
│   └── test_game_repo_ingestion.py # Game repo ingestion tests (NEW!)
├── docs/                          # Documentation (organized)
│   ├── INDEX.md                   # Documentation index
│   ├── phases/                    # Phase-specific documentation
│   ├── gui/                       # GUI documentation
│   ├── design/                    # Design system documentation
│   ├── guides/                    # Installation and usage guides
│   ├── remote-control/            # Remote control API documentation
│   ├── testing/                   # Testing documentation
│   └── summaries/                 # Implementation summaries
│
├── Phase 1 - Foundation
│   ├── ingest.py                  # Document ingestion script
│   ├── main.py                    # CLI Q&A interface
│   └── gui_director.py            # GUI application
│
├── Phase 2 - Planning (NEW!)
│   ├── planning_models.py         # Data models for goals and tasks
│   ├── goal_analysis_agent.py     # Goal analysis and classification
│   ├── task_decomposition_agent.py # Task decomposition and planning
│   ├── planning_cli.py            # Planning CLI interface
│   └── PHASE2_GUIDE.md            # Phase 2 user guide
│
├── examples/
│   └── phase2_example.py          # Phase 2 demonstration code
│
├── Templates
│   ├── GDD_TEMPLATE.md            # Game design document template
│   └── SAMPLE_GDD.md              # Example game design document
│
└── tests/
    ├── test_phase2_planning.py    # Tests for Phase 2 features
    └── ...                        # Additional tests

Note: "Phase 1" and "Phase 2" labels above indicate logical groupings, 
not actual directory names. All files are in the root directory.
```

## Documentation

### 📚 Documentation Indices

**Three ways to navigate the documentation:**
1. **[INDEX.md](INDEX.md)** - 🌟 **Master Index** - Complete project overview, code structure, and all documentation
2. **[docs/INDEX.md](docs/INDEX.md)** - 📖 **Documentation Hub** - Organized guides, tutorials, and references
3. **[CODE_REFERENCE.md](CODE_REFERENCE.md)** - 💻 **Code Reference** - Python modules, APIs, and development guide

### Quick Links

**Installation & Setup:**
- [Installation Guide](docs/guides/INSTALLATION.md) - Platform-specific installation instructions
- [Troubleshooting](docs/guides/TROUBLESHOOTING.md) - Quick reference for common issues
- [Error Handling Guide](docs/guides/ERROR_HANDLING.md) - Comprehensive error handling documentation

**Project Documentation:**
- [Project Plan](docs/guides/PROJECT_PLAN.md) - Detailed breakdown of all four phases
- [Project Roadmap](ROADMAP.md) - Timeline, milestones, and phase details
- [Agent System](AGENTS.md) - Architecture and design of the agent system
- [Phase 2 Guide](docs/phases/PHASE2_GUIDE.md) - Complete guide to goal decomposition and planning
- [Phase 2 Completion](docs/phases/PHASE2_COMPLETION.md) - Phase 2 completion report
- [Phase 3 Guide](PHASE3_GUIDE.md) - Autonomous agents user guide

**Integration & Analysis:**
- [Integration Guide](INTEGRATION_GUIDE.md) - Step-by-step integration into your workflow
- [API Cost Analysis](API_COST_ANALYSIS.md) - Comprehensive API cost analysis and optimization strategies
- [LLM Alternatives](LLM_ALTERNATIVES.md) - Compare providers: OpenAI, Anthropic, Ollama (free), Groq, and more
- [Improvements Roadmap](IMPROVEMENTS.md) - Planned enhancements and priorities
- [Project Analysis](ADASTREA_DIRECTOR_ANALYSIS.md) - Comprehensive value analysis and ROI

**GUI Documentation:**
- [GUI Quick Start](docs/gui/GUI_QUICK_START.md) - User quick start and tips
- [GUI Improvements](docs/gui/GUI_IMPROVEMENTS.md) - Comprehensive feature documentation
- [GUI Settings Guide](docs/gui/GUI_SETTINGS.md) - Settings configuration guide

**Testing Documentation:**
- [GUI Testing Guide](docs/testing/GUI_TESTING_GUIDE.md) - Testing procedures and manual checklist
- [Testing](docs/testing/TESTING.md) - General testing guide
- [Test Summary](docs/testing/TEST_SUMMARY.md) - Test results and coverage

**Design System:**
- [Design Index](docs/design/DESIGN_INDEX.md) - Complete guide to all design documentation
- [UI/UX Design System](docs/design/UI_UX_DESIGN_SYSTEM.md) - Complete design system
- [Visual Mockups](docs/design/UE_INTERFACE_MOCKUPS.md) ✨ **NEW** - Interface mockups and design specs
- [Mockups Summary](VISUAL_MOCKUPS_SUMMARY.md) ✨ **NEW** - Visual mockups overview

**For complete documentation:**
- 🌟 **[INDEX.md](INDEX.md)** - Start here for complete overview
- 📖 **[docs/INDEX.md](docs/INDEX.md)** - Organized documentation hub
- 💻 **[CODE_REFERENCE.md](CODE_REFERENCE.md)** - Developer code guide

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

For manual testing and QA procedures, see:
- [GUI Testing Guide](docs/testing/GUI_TESTING_GUIDE.md) - Complete manual testing checklist
- [Testing Documentation](docs/testing/TESTING.md) - General testing guidelines

## Contributing

This project is in early development. Contributions, suggestions, and feedback are welcome!

## License

[To be determined]

## Contact

Project maintained by [Mittenzx](https://github.com/Mittenzx)

---

*"Building tomorrow's game development tools, today."*
