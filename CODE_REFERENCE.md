# 💻 Adastrea Director - Code Reference

**Complete Python Module and Code Structure Reference**

This document provides a comprehensive guide to the Python codebase, helping developers understand the architecture, find specific functionality, and contribute effectively.

---

## 📋 Table of Contents

- [Core Application Modules](#core-application-modules)
- [Agent System](#agent-system)
- [Supporting Modules](#supporting-modules)
- [Remote Control System](#remote-control-system)
- [Utilities & Tools](#utilities--tools)
- [Test Suite](#test-suite)
- [Examples](#examples)
- [Module Dependencies](#module-dependencies)
- [Development Workflow](#development-workflow)

---

## 🎯 Core Application Modules

### Entry Points

#### `main.py`
**Phase 1 CLI - Context-Aware Q&A Interface**

Primary entry point for the RAG-based question-answering system.

**Key Functions:**
- `main()` - Main application loop
- `process_query(query: str)` - Process user queries
- `load_knowledge_base()` - Load documents from ChromaDB

**Usage:**
```bash
python main.py
python main.py --set-api-key gemini
```

**Related:**
- Uses: `llm_config.py`, `config_manager.py`
- Tests: `tests/test_query_system.py`

---

#### `gui_director.py`
**Graphical User Interface Application**

Enhanced GUI with modern dark theme and comprehensive features.

**Key Classes:**
- `AdastreaDirectorGUI` - Main GUI class
- `IngestListDialog` - Document tracking dialog

**Key Features:**
- API key management with secure storage
- Knowledge base updates
- Conversation history with export
- Keyboard shortcuts (Ctrl+K, Ctrl+U, Ctrl+L, etc.)

**Usage:**
```bash
python gui_director.py
```

**Documentation:**
- [GUI Quick Start](docs/gui/GUI_QUICK_START.md)
- [GUI Improvements](docs/gui/GUI_IMPROVEMENTS.md)

---

#### `planner.py`
**Phase 2 - Planning CLI Entry Point**

Interactive planning system for goal decomposition and task planning.

**Key Functions:**
- `create_plan(goal: str)` - Create implementation plan
- `export_plan(plan: Plan, format: str)` - Export plan to file
- `interactive_mode()` - Interactive planning session

**Usage:**
```bash
python planner.py --interactive
python planner.py "Add inventory system" --export markdown
```

**Related:**
- Uses: `goal_analysis_agent.py`, `task_decomposition_agent.py`
- Tests: `tests/test_phase2_planning.py`

---

#### `planning_cli.py`
**Phase 2 - Alternative Planning Interface**

Alternative CLI for planning with different interaction patterns.

**Key Functions:**
- `run_interactive()` - Interactive planning mode
- `process_single_goal()` - Process one goal
- `export_plan_to_file()` - Save plan to file

**Usage:**
```bash
python planning_cli.py --interactive
python planning_cli.py --goal "Implement auth system"
```

---

#### `agent_orchestrator_cli.py`
**Phase 3 - Agent Management CLI**

Command-line interface for managing autonomous agents.

**Key Functions:**
- `start_agents(agent_names: List[str])` - Start agents
- `stop_agents(agent_names: List[str])` - Stop agents
- `get_status()` - Get agent status
- `view_events(limit: int)` - View recent events

**Usage:**
```bash
python agent_orchestrator_cli.py start --all
python agent_orchestrator_cli.py status --verbose
python agent_orchestrator_cli.py events --limit 20
```

**Documentation:**
- [PHASE3_GUIDE.md](PHASE3_GUIDE.md)
- [Agent Orchestration](docs/phases/AGENT_ORCHESTRATION.md)

---

#### `agent_dashboard.py`
**Phase 3 - Real-time Monitoring Dashboard**

Terminal-based dashboard for real-time agent monitoring.

**Key Classes:**
- `AgentDashboard` - Main dashboard class
- `DashboardUI` - Terminal UI component

**Usage:**
```bash
python agent_dashboard.py --auto-start
python agent_dashboard.py --interval 2.0
```

---

### Document Ingestion

#### `ingest.py`
**General Document Ingestion System**

Ingests documents from local filesystem into ChromaDB vector database.

**Key Functions:**
- `ingest_documents(docs_dir: str)` - Ingest documents
- `chunk_document(content: str, doc_type: str)` - Chunk documents
- `generate_embeddings(chunks: List[str])` - Generate embeddings
- `store_in_database(chunks, embeddings, metadata)` - Store in ChromaDB

**Usage:**
```bash
python ingest.py --docs-dir /path/to/docs
python ingest.py --docs-dir /path/to/docs --batch-size 50
```

**Supported File Types:**
- Markdown (.md)
- Python (.py)
- C++ (.cpp, .h)
- Blueprint (.uasset)
- Text (.txt)
- JSON (.json)
- YAML (.yaml, .yml)

**Related:**
- Tests: `tests/test_document_loaders.py`, `tests/test_chunking_strategies.py`

---

#### `ingest_game_repo.py`
**Game Repository Ingestion**

Specialized ingestion for the Mittenzx/Adastrea game repository.

**Key Functions:**
- `clone_or_update_repo()` - Clone or update game repo
- `ingest_game_files()` - Ingest game-specific files
- `filter_relevant_files()` - Filter by relevance

**Usage:**
```bash
export GITHUB_TOKEN="ghp_your_token"
python ingest_game_repo.py
```

**Documentation:**
- [Game Repo Ingestion Guide](docs/guides/GAME_REPO_INGESTION.md)
- [Quick Start](docs/guides/QUICK_START_GAME_REPO.md)

---

## 🤖 Agent System

### Phase 2 Agents (Planning)

#### `agents/goal_analysis_agent.py`
**Goal Analysis Agent**

Analyzes and classifies development goals.

**Key Classes:**
- `GoalAnalysisAgent` - Main agent class

**Key Methods:**
- `parse_goal(goal_description: str) -> Goal`
- `identify_constraints(goal: Goal) -> List[Constraint]`
- `classify_goal(goal: Goal) -> GoalType`
- `determine_scope(goal: Goal) -> ProjectScope`

**Goal Types:**
- FEATURE, BUG_FIX, OPTIMIZATION, REFACTORING, DOCUMENTATION

**Related:**
- Model: `agents/models.py`
- Tests: `tests/test_planning_agents.py`

---

#### `agents/task_decomposition_agent.py`
**Task Decomposition Agent**

Breaks down goals into actionable tasks with dependencies.

**Key Classes:**
- `TaskDecompositionAgent` - Main agent class

**Key Methods:**
- `decompose_goal(goal: Goal) -> TaskTree`
- `estimate_effort(task: Task) -> Duration`
- `identify_dependencies(tasks: List[Task]) -> DependencyGraph`
- `prioritize_tasks(tasks: List[Task]) -> List[Task]`

**Related:**
- Model: `agents/models.py`
- Tests: `tests/test_planning_agents.py`

---

#### `agents/code_generation_agent.py`
**Code Generation Agent**

Generates code suggestions and implementation approaches.

**Key Classes:**
- `CodeGenerationAgent` - Main agent class

**Key Methods:**
- `generate_boilerplate(task: Task) -> str`
- `suggest_implementation(task: Task) -> List[Implementation]`
- `create_example(task: Task) -> str`
- `propose_modifications(task: Task) -> List[FileModification]`

**Related:**
- Tests: `tests/test_planning_agents.py`

---

#### `agents/models.py`
**Agent Data Models**

Core data models for the agent system.

**Key Classes:**
- `Goal` - Development goal
- `Task` - Actionable task
- `TaskTree` - Hierarchical task structure
- `DependencyGraph` - Task dependencies
- `Implementation` - Code implementation approach
- `Constraint` - Goal constraint
- `ProjectScope` - Affected project areas

**Related:**
- Tests: `tests/test_planning_models.py`

---

### Phase 3 Agents (Autonomous)

#### `agents/phase3/base_agent.py`
**Base Agent Class**

Abstract base class for all autonomous agents.

**Key Classes:**
- `BaseAgent` - Abstract base class

**Key Methods:**
- `start()` - Start agent
- `stop()` - Stop agent
- `get_status() -> AgentStatus`
- `process_event(event: Event)` - Handle events
- `publish_event(event: Event)` - Publish to event bus

**Agent States:**
- IDLE, BUSY, ERROR, STOPPED

---

#### `agents/phase3/performance_profiling_agent.py`
**Performance Profiling Agent**

Monitors and analyzes game performance metrics.

**Key Classes:**
- `PerformanceProfilingAgent` - Main agent class

**Key Methods:**
- `start_monitoring()` - Start performance monitoring
- `collect_metrics() -> PerformanceMetrics`
- `analyze_performance(metrics) -> Analysis`
- `detect_bottlenecks(analysis) -> List[Bottleneck]`
- `generate_recommendations(bottlenecks) -> List[Recommendation]`

**Metrics Tracked:**
- Frame rate (FPS)
- Memory usage (RAM, VRAM)
- CPU/GPU utilization
- Load times
- Asset streaming

**Related:**
- Tests: `tests/phase3/test_performance_profiling_agent.py`

---

#### `agents/phase3/bug_detection_agent.py`
**Bug Detection Agent**

Automated bug detection and playtesting.

**Key Classes:**
- `BugDetectionAgent` - Main agent class

**Key Methods:**
- `run_automated_tests() -> TestResults`
- `analyze_logs(log_file: str) -> List[Anomaly]`
- `detect_crashes() -> List[Crash]`
- `verify_regressions(commit: str) -> List[Regression]`
- `create_bug_report(issue: Issue) -> BugReport`

**Detection Types:**
- Crash detection
- Log anomaly detection
- Regression testing
- Automated playtesting

**Related:**
- Tests: `tests/phase3/test_bug_detection_agent.py`

---

#### `agents/phase3/code_quality_agent.py`
**Code Quality Agent**

Monitors code quality and suggests refactoring.

**Key Classes:**
- `CodeQualityAgent` - Main agent class

**Key Methods:**
- `analyze_code(file_path: str) -> QualityReport`
- `detect_code_smells(code: str) -> List[CodeSmell]`
- `suggest_refactoring(code_smell) -> Refactoring`
- `check_standards(file_path) -> List[Violation]`
- `calculate_technical_debt() -> TechnicalDebtScore`

**Quality Checks:**
- Static code analysis
- Code smell detection
- Coding standards compliance
- Technical debt tracking
- Complexity metrics

**Related:**
- Tests: `tests/phase3/test_code_quality_agent.py`

---

#### `agents/phase3/event_bus.py`
**Event Bus System**

Central event communication system for agents.

**Key Classes:**
- `EventBus` - Singleton event bus
- `Event` - Event data class

**Key Methods:**
- `publish(event: Event)` - Publish event
- `subscribe(event_type, handler)` - Subscribe to events
- `unsubscribe(event_type, handler)` - Unsubscribe

**Event Types:**
- AGENT_STARTED, AGENT_STOPPED
- METRIC_COLLECTED, ALERT_TRIGGERED
- BUG_DETECTED, ISSUE_CREATED
- RECOMMENDATION_GENERATED

**Related:**
- Tests: `tests/phase3/test_event_bus.py`

---

#### `agents/phase3/shared_state.py`
**Shared State Management**

Manages shared context and state across agents.

**Key Classes:**
- `SharedState` - Singleton state manager

**Key Methods:**
- `get_project_info() -> ProjectInfo`
- `get_code_structure() -> CodeStructure`
- `get_recent_changes() -> List[Change]`
- `update_context(key, value)`

**Related:**
- Tests: `tests/phase3/test_shared_state.py`

---

## 🔧 Supporting Modules

### `config_manager.py`
**Configuration Management**

Manages application configuration with secure storage.

**Key Classes:**
- `ConfigManager` - Configuration manager

**Key Methods:**
- `get_config(key: str)` - Get config value
- `set_config(key: str, value: Any)` - Set config value
- `save_api_key(provider: str, key: str)` - Save encrypted API key
- `load_api_key(provider: str) -> str` - Load decrypted API key

**Config Storage:**
- Location: `~/.adastrea/config.json`
- Encryption: Machine-specific key
- Supports: API keys, user preferences, project settings

**Related:**
- Tests: `tests/test_config_manager.py`

---

### `llm_config.py`
**LLM Configuration**

Configures and manages LLM provider connections.

**Key Functions:**
- `get_llm_client(provider: str)` - Get LLM client
- `configure_openai()` - Configure OpenAI
- `configure_gemini()` - Configure Google Gemini
- `configure_anthropic()` - Configure Anthropic Claude

**Supported Providers:**
- OpenAI (GPT-3.5, GPT-4)
- Google Gemini (Gemini Pro)
- Anthropic (Claude)
- Ollama (Local, free)
- Groq (Fast inference)

**Documentation:**
- [LLM Alternatives](LLM_ALTERNATIVES.md)
- [API Cost Analysis](API_COST_ANALYSIS.md)

**Related:**
- Tests: `tests/test_llm_config.py`

---

### `cost_tracker.py`
**API Cost Tracking**

Tracks and reports API usage costs.

**Key Classes:**
- `CostTracker` - Cost tracking manager

**Key Methods:**
- `track_request(provider, tokens, operation)` - Track API call
- `get_session_cost() -> float` - Get session cost
- `get_total_cost() -> float` - Get total cost
- `export_report(format: str)` - Export cost report

**Tracking:**
- Token usage per operation
- Cost per provider
- Session and total costs
- Cost projections

**Related:**
- Example: `examples/cost_tracking_example.py`
- Documentation: [API Cost Analysis](API_COST_ANALYSIS.md)

---

### `planning_models.py`
**Planning Data Models**

Data models for planning system (older, being deprecated in favor of `agents/models.py`).

**Key Classes:**
- `Goal` - Development goal
- `Task` - Task definition
- `Plan` - Implementation plan

**Note:** Consider using `agents/models.py` for new code.

**Related:**
- Tests: `tests/test_planning_models.py`

---

### `exceptions.py`
**Custom Exceptions**

Custom exception classes for error handling.

**Key Classes:**
- `AdastreaException` - Base exception
- `ConfigurationError` - Configuration errors
- `IngestionError` - Document ingestion errors
- `QueryError` - Query processing errors
- `AgentError` - Agent system errors

**Documentation:**
- [Error Handling Guide](docs/guides/ERROR_HANDLING.md)

**Related:**
- Tests: `tests/test_error_handling.py`

---

## 🎮 Remote Control System

### `remote_control/client.py`
**Remote Control Client**

HTTP client for Unreal Engine Remote Control API.

**Key Classes:**
- `RemoteControlClient` - HTTP client

**Key Methods:**
- `call_function(object_path, function_name, parameters)`
- `get_property(object_path, property_name)`
- `set_property(object_path, property_name, value)`
- `batch_operations(operations: List[Operation])`

**Usage:**
```python
from remote_control.client import RemoteControlClient

client = RemoteControlClient("http://localhost:30010")
result = client.call_function("/Game/MyActor", "MyFunction", {"param": "value"})
```

**Documentation:**
- [Remote Control API](docs/remote-control/REMOTE_CONTROL_API.md)
- [Quickstart](docs/remote-control/REMOTE_CONTROL_QUICKSTART.md)

**Related:**
- Tests: `tests/remote_control/test_client.py`

---

### `remote_control/websocket_client.py`
**WebSocket Client**

WebSocket client for real-time Unreal Engine communication.

**Key Classes:**
- `WebSocketClient` - WebSocket client

**Key Methods:**
- `connect()` - Establish connection
- `subscribe(event_type)` - Subscribe to events
- `send_message(message)` - Send message
- `receive_message() -> Message` - Receive message

**Related:**
- Tests: `tests/remote_control/test_websocket_client.py`

---

### `remote_control/base_agent.py`
**Base Remote Control Agent**

Base class for agents that interact with Unreal Engine.

**Key Classes:**
- `RemoteControlBaseAgent` - Base agent

**Key Methods:**
- `initialize()` - Initialize connection
- `execute_action(action: Action)` - Execute action
- `get_editor_state() -> EditorState` - Get editor state

**Related:**
- Tests: `tests/remote_control/test_base_agent.py`

---

### `remote_control/models.py`
**Remote Control Data Models**

Data models for remote control operations.

**Key Classes:**
- `RemoteOperation` - Remote operation
- `PropertyChange` - Property change
- `FunctionCall` - Function call
- `BatchRequest` - Batch operation request

---

## 🛠️ Utilities & Tools

### `check_compatibility.py`
**System Compatibility Check**

Checks system compatibility before installation.

**Checks:**
- Python version (3.9+)
- Operating system
- Required libraries availability
- Platform-specific requirements

**Usage:**
```bash
python check_compatibility.py
```

---

### `install_dependencies.py`
**Smart Dependency Installer**

Platform-aware dependency installation with retry logic.

**Features:**
- Detects platform (Windows, macOS, Linux)
- Handles ARM architecture (Apple Silicon)
- Retry logic for failed installations
- Detailed progress reporting

**Usage:**
```bash
python install_dependencies.py
```

**Documentation:**
- [Installation Guide](docs/guides/INSTALLATION.md)

---

### `validate_requirements.py`
**Requirements Validation**

Validates that all required packages are installed correctly.

**Checks:**
- Package versions
- Import tests
- Dependency conflicts

**Usage:**
```bash
python validate_requirements.py
```

---

### `verify_encoding_fix.py`
**Encoding Verification**

Verifies Unicode and encoding fixes.

**Tests:**
- UTF-8 encoding handling
- Unicode character support
- Cross-platform encoding

**Usage:**
```bash
python verify_encoding_fix.py
```

**Related:**
- Documentation: [Unicode Encoding Fix](docs/summaries/UNICODE_ENCODING_FIX.md)

---

### `test_unicode_support.py`
**Unicode Support Test**

Tests Unicode character handling across the system.

**Usage:**
```bash
python test_unicode_support.py
```

---

### `test_ingest_list.py`
**Ingestion List Test**

Tests document tracking and ingestion list functionality.

**Usage:**
```bash
python test_ingest_list.py
```

---

### `demo_incremental.py`
**Incremental Ingestion Demo**

Demonstrates incremental document ingestion.

**Usage:**
```bash
python demo_incremental.py
```

---

### `phase3_demo.py`
**Phase 3 Demo**

Demonstrates Phase 3 autonomous agent capabilities.

**Usage:**
```bash
python phase3_demo.py
```

---

## 🧪 Test Suite

### Test Organization

```
tests/
├── test_planning_models.py          # Planning model tests
├── test_planning_agents.py          # Planning agent tests
├── test_phase2_planning.py          # Phase 2 integration tests
├── test_game_repo_ingestion.py      # Game repo tests
├── test_config_manager.py           # Config manager tests
├── test_llm_config.py               # LLM config tests
├── test_query_system.py             # Query system tests
├── test_document_loaders.py         # Document loader tests
├── test_chunking_strategies.py      # Chunking strategy tests
├── test_embedding_providers.py      # Embedding provider tests
├── test_error_handling.py           # Error handling tests
├── test_error_integration.py        # Error integration tests
├── phase3/                          # Phase 3 agent tests
│   ├── test_performance_profiling_agent.py
│   ├── test_bug_detection_agent.py
│   ├── test_code_quality_agent.py
│   ├── test_event_bus.py
│   └── test_shared_state.py
└── remote_control/                  # Remote control tests
    ├── test_client.py
    ├── test_websocket_client.py
    └── test_base_agent.py
```

### Running Tests

**Run all tests:**
```bash
pytest
```

**Run specific test file:**
```bash
pytest tests/test_planning_agents.py
```

**Run with coverage:**
```bash
pytest --cov=. --cov-report=html
```

**Run Phase 3 tests only:**
```bash
pytest tests/phase3/
```

**Documentation:**
- [Testing Guide](docs/testing/TESTING.md)
- [Test Summary](docs/testing/TEST_SUMMARY.md)

### Test Statistics

- **Total Tests:** 230+ (100% passing)
- **Phase 1 Tests:** 50+
- **Phase 2 Tests:** 60+
- **Phase 3 Tests:** 120+
- **Coverage:** ~85%

---

## 📦 Examples

### `examples/phase2_example.py`
**Phase 2 Demonstration**

Complete example of Phase 2 planning capabilities.

**Demonstrates:**
- Goal analysis
- Task decomposition
- Dependency management
- Code generation

**Usage:**
```bash
python examples/phase2_example.py
```

---

### `examples/phase3_orchestrator_demo.py`
**Phase 3 Orchestrator Demo**

Demonstrates agent orchestration and monitoring.

**Demonstrates:**
- Starting/stopping agents
- Agent status monitoring
- Event handling
- Dashboard UI

**Usage:**
```bash
python examples/phase3_orchestrator_demo.py
```

---

### `examples/remote_control_demo.py`
**Remote Control Demo**

Demonstrates Unreal Engine remote control integration.

**Demonstrates:**
- Connecting to Unreal Engine
- Calling functions
- Getting/setting properties
- Batch operations

**Usage:**
```bash
python examples/remote_control_demo.py
```

---

### `examples/cost_tracking_example.py`
**Cost Tracking Example**

Demonstrates API cost tracking.

**Demonstrates:**
- Tracking API calls
- Calculating costs
- Generating reports
- Cost projections

**Usage:**
```bash
python examples/cost_tracking_example.py
```

---

## 📊 Module Dependencies

### Core Dependencies

```
main.py
├── llm_config.py
├── config_manager.py
└── chromadb

gui_director.py
├── llm_config.py
├── config_manager.py
├── ingest.py
└── tkinter

planner.py
├── goal_analysis_agent.py
├── task_decomposition_agent.py
├── agents/models.py
└── llm_config.py

agent_orchestrator_cli.py
├── agents/phase3/base_agent.py
├── agents/phase3/performance_profiling_agent.py
├── agents/phase3/bug_detection_agent.py
├── agents/phase3/code_quality_agent.py
└── agents/phase3/event_bus.py
```

### Agent Dependencies

```
agents/phase3/base_agent.py
├── agents/phase3/event_bus.py
└── agents/phase3/shared_state.py

agents/phase3/performance_profiling_agent.py
├── agents/phase3/base_agent.py
└── remote_control/client.py

agents/phase3/bug_detection_agent.py
├── agents/phase3/base_agent.py
└── remote_control/client.py

agents/phase3/code_quality_agent.py
└── agents/phase3/base_agent.py
```

---

## 🔄 Development Workflow

### Setup Development Environment

1. **Clone repository:**
```bash
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director
```

2. **Run setup:**
```bash
./setup.sh  # Linux/Mac
# or
python install_dependencies.py  # All platforms
```

3. **Activate virtual environment:**
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows
```

### Making Changes

1. **Check existing tests:**
```bash
pytest tests/
```

2. **Make your changes**

3. **Write tests:**
```bash
# Add tests in appropriate test file
pytest tests/test_your_feature.py
```

4. **Run all tests:**
```bash
pytest
```

5. **Check code style:**
```bash
# If using linter
pylint your_module.py
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Code Style

- Follow PEP 8
- Use type hints where possible
- Write docstrings for public APIs
- Keep functions focused and small
- Add tests for new features

---

## 📚 Additional Resources

### Documentation
- **[Master Index](INDEX.md)** - Complete documentation index
- **[docs/INDEX.md](docs/INDEX.md)** - Organized documentation hub
- **[AGENTS.md](AGENTS.md)** - Agent system architecture

### Guides
- **[Installation](docs/guides/INSTALLATION.md)** - Setup guide
- **[Troubleshooting](docs/guides/TROUBLESHOOTING.md)** - Common issues
- **[Error Handling](docs/guides/ERROR_HANDLING.md)** - Error handling patterns

### Project Info
- **[ROADMAP.md](ROADMAP.md)** - Development roadmap
- **[README.md](README.md)** - Project overview
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute

---

## 🆘 Need Help?

- **Code Questions:** Check this reference first
- **Module Usage:** See examples/ directory
- **Testing:** [Testing Guide](docs/testing/TESTING.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Issues:** GitHub Issues

---

## 📅 Last Updated

**Date:** 2025-11-14  
**Version:** 1.0  

---

*"Your complete guide to the Adastrea Director codebase - Building tomorrow's game development tools, today."*
