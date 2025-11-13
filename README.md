# Adastrea Director - AI Game Director

An intelligent assistant system designed to understand natural language commands and assist with the game development lifecycle in Unreal Engine.

## Overview

Adastrea Director is an AI-powered tool that aims to revolutionize game development by providing context-aware assistance, automated planning, and eventually autonomous development capabilities. The project is being developed in four distinct phases, with each phase building upon the previous one.

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

## Project Phases

1. **Phase 1: The Foundation (Context-Aware Assistant)** - ✅ Complete
1. **Phase 1: The Foundation (Context-Aware Assistant)** - ✅ *Complete*
   - RAG-based document understanding
   - Natural language query interface
   - Document ingestion and vector database
   
2. **Phase 2: The Planner (Goal-Oriented Tasking)** - ✅ Complete
   - Break down high-level goals into actionable tasks
   - Generate reviewable action plans
   - Code generation and suggestions
2. **Phase 2: The Planner (Goal-Oriented Tasking)** - ✨ *Current Phase*
   - Goal analysis and classification
   - Task decomposition with dependencies
   - Action plan generation
   - Effort estimation and prioritization
   
3. **Phase 3: The Proactive Agent System** - 🔮 *Planned*
   - Autonomous performance profiling
   - Automated bug detection and reporting
   
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

**For LLM queries:** Set up your preferred LLM provider:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

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

#### Graphical User Interface (GUI)

For a more user-friendly experience, you can use the enhanced GUI application:

```bash
python gui_director.py
```

The improved GUI provides:
- **Modern Dark Theme**: Professional appearance with reduced eye strain
- **Easy API Key Management**: Styled dialog for OpenAI API key configuration
- **Knowledge Base Updates**: One-click knowledge base updates
- **Ingest List Tab**: Visual checklist of ingested documents with statistics
- **Conversation History**: Full conversation display with timestamps and color-coding
- **Keyboard Shortcuts**: Fast workflow with comprehensive keyboard support (Ctrl+K, Ctrl+U, Ctrl+L, etc.)
- **Copy & Export**: One-click copy to clipboard and export conversations to file
- **Font Size Controls**: Adjustable text size for better accessibility
- **Menu Bar**: File, Edit, and Help menus with full functionality
- **Tooltips**: Helpful hints on all interactive elements
- **Status Feedback**: Real-time status updates with visual indicators

**Keyboard Shortcuts:**
- `Enter` or `Ctrl+Enter` - Send question
- `Ctrl+K` - Set API Key
- `Ctrl+U` - Update knowledge base
- `Ctrl+L` - Clear conversation
- `Ctrl+C` - Copy last response (from menu)
- `Ctrl+E` - Export conversation

See [GUI_IMPROVEMENTS.md](docs/gui/GUI_IMPROVEMENTS.md) for detailed documentation of all enhancements.

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

📚 **[Complete Documentation Index](docs/INDEX.md)** - Comprehensive, organized documentation hub

### Quick Links

**Installation & Setup:**
- [Installation Guide](docs/guides/INSTALLATION.md) - Platform-specific installation instructions
- [Troubleshooting](docs/guides/TROUBLESHOOTING.md) - Quick reference for common issues
- [Error Handling Guide](docs/guides/ERROR_HANDLING.md) - Comprehensive error handling documentation

**Project Documentation:**
- [Project Plan](docs/guides/PROJECT_PLAN.md) - Detailed breakdown of all four phases
- [Agent System](AGENTS.md) - Architecture and design of the agent system
- [Phase 2 Guide](docs/phases/PHASE2_GUIDE.md) - Complete guide to goal decomposition and planning
- [Phase 2 Completion](docs/phases/PHASE2_COMPLETION.md) - Phase 2 completion report

**GUI Documentation:**
- [GUI Quick Start](docs/gui/GUI_QUICK_START.md) - User quick start and tips
- [GUI Improvements](docs/gui/GUI_IMPROVEMENTS.md) - Comprehensive feature documentation

**Design System:**
- [Design Index](docs/design/DESIGN_INDEX.md) - Complete guide to all design documentation
- [UI/UX Design System](docs/design/UI_UX_DESIGN_SYSTEM.md) - Complete design system

**For complete documentation, see [docs/INDEX.md](docs/INDEX.md)**

## Contributing

This project is in early development. Contributions, suggestions, and feedback are welcome!

## License

[To be determined]

## Contact

Project maintained by [Mittenzx](https://github.com/Mittenzx)

---

*"Building tomorrow's game development tools, today."*
