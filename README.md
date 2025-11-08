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

- Python 3.8 or higher
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

## Project Structure

```
Adastrea-Director/
├── README.md              # This file
├── PROJECT_PLAN.md        # Detailed project roadmap
├── AGENTS.md              # Agent system architecture
├── requirements.txt       # Python dependencies
├── ingest.py             # Document ingestion script
├── main.py               # CLI entry point
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
