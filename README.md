# Adastrea Director - AI Game Director

An intelligent assistant system designed to understand natural language commands and assist with the game development lifecycle in Unreal Engine.

## Overview

Adastrea Director is an AI-powered tool that aims to revolutionize game development by providing context-aware assistance, automated planning, and eventually autonomous development capabilities. The project is being developed in four distinct phases, with each phase building upon the previous one.

## Current Phase: Phase 2 - The Planner

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

### Installation

#### Quick Setup (All Platforms)

```bash
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director
./setup.sh  # Linux/Mac
```

The setup script will:
- Check your system compatibility
- Create a virtual environment
- Install all dependencies with platform-specific handling
- Verify the installation

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

**📝 Note**: If you encounter issues (especially on Apple Silicon Macs or ARM systems), use the smart installer or see [INSTALLATION.md](INSTALLATION.md) for platform-specific instructions and troubleshooting.

3. Set up your OpenAI API key (or other LLM provider):
```bash
export OPENAI_API_KEY="your-api-key-here"
```

4. **(Optional)** Set up GitHub token for game repository ingestion:
```bash
export GITHUB_TOKEN="your-github-token-here"
```
This is only needed if you want to ingest documents from the private Mittenzx/Adastrea game repository. See [GAME_REPO_INGESTION.md](GAME_REPO_INGESTION.md) for details.

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

**📚 New to ingestion?** See [DOCS_TO_INGEST.md](DOCS_TO_INGEST.md) for a comprehensive list of documents to ingest and detailed instructions.

**🎮 Working on the Mittenzx/Adastrea game?** Use the dedicated game repository ingestion:
```bash
python ingest_game_repo.py
```
See [GAME_REPO_INGESTION.md](GAME_REPO_INGESTION.md) for setup and automatic update features.

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

**📋 Want to learn more?** See [PHASE2_GUIDE.md](PHASE2_GUIDE.md) for comprehensive Phase 2 documentation with examples.

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

See [GUI_IMPROVEMENTS.md](GUI_IMPROVEMENTS.md) for detailed documentation of all enhancements.

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
├── GDD_TEMPLATE.md                # Game design document template
├── SAMPLE_GDD.md                  # Example game design document
├── PHASE1_COMPLETION.md           # Phase 1 completion report
├── PHASE2_COMPLETION.md           # Phase 2 completion report (NEW!)
└── GUI Documentation/
    ├── GUI_IMPROVEMENTS.md        # Detailed feature documentation
    ├── GUI_VISUAL_COMPARISON.md   # Before/after comparison
    └── GUI_QUICK_START.md         # User quick start guide
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

### Installation & Setup
- [Installation Guide](INSTALLATION.md) - Platform-specific installation instructions
- [Troubleshooting](TROUBLESHOOTING.md) - Quick reference for common issues
- [Error Handling Guide](ERROR_HANDLING.md) - Comprehensive error handling documentation
- **[Documents to Ingest](DOCS_TO_INGEST.md)** - Comprehensive guide to documents for the knowledge base
- **[Game Repository Ingestion](GAME_REPO_INGESTION.md)** - Guide for ingesting from Mittenzx/Adastrea game repo

### Project Documentation
- [Project Plan](PROJECT_PLAN.md) - Detailed breakdown of all four phases
- [Phase 1 Completion](PHASE1_COMPLETION.md) - Phase 1 completion report
- [Phase 2 Completion](PHASE2_COMPLETION.md) - Phase 2 completion report (NEW!)
- [Agent System](AGENTS.md) - Architecture and design of the agent system
- [Agent System Assessment](AGENTS_UTILITY_ASSESSMENT.md) - Comprehensive evaluation of agent architecture utility
- [Unreal MCP Assessment](UNREAL_MCP_ASSESSMENT.md) - Evaluation of Unreal Engine MCP Server integration potential
- **[Phase 2 Guide](PHASE2_GUIDE.md)** - ✨ Complete guide to goal decomposition and planning (NEW!)
- [GDD Template](GDD_TEMPLATE.md) - Template for creating game design documents

### UI/UX Design Documentation
- **[Design Documentation Index](DESIGN_INDEX.md)** - Start here! Complete guide to all design documentation
- [UI/UX Design System](UI_UX_DESIGN_SYSTEM.md) - Complete design system with principles, colors, typography, and components
- [Visual Design Guide](DESIGN_GUIDE.md) - Visual specifications, mockups, and implementation examples
- [Component Library](COMPONENT_LIBRARY.md) - Reusable UI components with code examples

### GUI Documentation
- [GUI Improvements](GUI_IMPROVEMENTS.md) - Comprehensive feature documentation
- [Ingest List Feature](INGEST_LIST_FEATURE.md) - Document ingestion tracking and visualization
- [Visual Comparison](GUI_VISUAL_COMPARISON.md) - Before/after comparison with visuals
- [Visual Description](GUI_SCREENSHOT_DESCRIPTION.md) - Detailed interface description
- [Quick Start Guide](GUI_QUICK_START.md) - User quick start and tips
- [Changes Summary](GUI_CHANGES_SUMMARY.md) - Complete summary of all changes

## Contributing

This project is in early development. Contributions, suggestions, and feedback are welcome!

## License

[To be determined]

## Contact

Project maintained by [Mittenzx](https://github.com/Mittenzx)

---

*"Building tomorrow's game development tools, today."*
