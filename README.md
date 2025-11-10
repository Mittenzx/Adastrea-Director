# Adastrea Director - AI Game Director

An intelligent assistant system designed to understand natural language commands and assist with the game development lifecycle in Unreal Engine.

## Overview

Adastrea Director is an AI-powered tool that aims to revolutionize game development by providing context-aware assistance, automated planning, and eventually autonomous development capabilities. The project is being developed in four distinct phases, with each phase building upon the previous one.

## Current Phase: Phase 1 - The Foundation

Phase 1 focuses on creating a context-aware assistant using Retrieval-Augmented Generation (RAG) to answer questions about project documents. This foundation enables the AI to understand your game design documents, code structure, and development context.

### Features (Phase 1)

- **Document Ingestion**: Load and process game design documents, code files, and other project documentation
- **RAG-Based Q&A**: Ask questions about your project and receive context-aware answers
- **Command-Line Interface**: Simple CLI for interacting with the AI assistant
- **Vector Database**: Efficient storage and retrieval of document embeddings

## Project Phases

1. **Phase 1: The Foundation (Context-Aware Assistant)** - *Current Phase*
   - RAG-based document understanding
   - Natural language query interface
   
2. **Phase 2: The Planner (Goal-Oriented Tasking)**
   - Break down high-level goals into actionable tasks
   - Generate reviewable action plans
   
3. **Phase 3: The Proactive Agent System**
   - Autonomous performance profiling
   - Automated bug detection and reporting
   
4. **Phase 4: The Creative Partner**
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

### Usage

#### Command-Line Interface (CLI)

1. **Ingest your project documents:**
```bash
python ingest.py --docs-dir /path/to/your/docs
```

**📚 New to ingestion?** See [DOCS_TO_INGEST.md](DOCS_TO_INGEST.md) for a comprehensive list of documents to ingest and detailed instructions.

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
├── main.py                        # CLI entry point
├── gui_director.py                # GUI application (enhanced)
├── GDD_TEMPLATE.md                # Game design document template
├── SAMPLE_GDD.md                  # Example game design document
└── GUI Documentation/
    ├── GUI_IMPROVEMENTS.md        # Detailed feature documentation
    ├── GUI_VISUAL_COMPARISON.md   # Before/after comparison
    ├── GUI_SCREENSHOT_DESCRIPTION.md  # Visual description
    ├── GUI_QUICK_START.md         # User quick start guide
    └── GUI_CHANGES_SUMMARY.md     # Complete changes summary
```

## Documentation

### Installation & Setup
- [Installation Guide](INSTALLATION.md) - Platform-specific installation instructions
- [Troubleshooting](TROUBLESHOOTING.md) - Quick reference for common issues
- **[Documents to Ingest](DOCS_TO_INGEST.md)** - Comprehensive guide to documents for the knowledge base

### Project Documentation
- [Project Plan](PROJECT_PLAN.md) - Detailed breakdown of all four phases
- [Agent System](AGENTS.md) - Architecture and design of the agent system
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
