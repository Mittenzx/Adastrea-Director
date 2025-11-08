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

1. Clone the repository:
```bash
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

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
├── README.md              # This file
├── PROJECT_PLAN.md        # Detailed project roadmap
├── AGENTS.md              # Agent system architecture
├── requirements.txt       # Python dependencies
├── ingest.py             # Document ingestion script
├── main.py               # CLI entry point
├── gui_director.py       # GUI application (Windows)
├── GDD_TEMPLATE.md       # Game design document template
└── SAMPLE_GDD.md         # Example game design document
```

## Documentation

- [Project Plan](PROJECT_PLAN.md) - Detailed breakdown of all four phases
- [Agent System](AGENTS.md) - Architecture and design of the agent system
- [GDD Template](GDD_TEMPLATE.md) - Template for creating game design documents

## Contributing

This project is in early development. Contributions, suggestions, and feedback are welcome!

## License

[To be determined]

## Contact

Project maintained by [Mittenzx](https://github.com/Mittenzx)

---

*"Building tomorrow's game development tools, today."*
