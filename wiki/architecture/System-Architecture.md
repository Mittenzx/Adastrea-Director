# System Architecture

This document provides a comprehensive overview of Adastrea Director's architecture, covering the core components, data flow, and design decisions.

## 🏗️ High-Level Architecture

Adastrea Director is built on a modular, extensible architecture that supports multiple deployment modes while sharing the same core AI backend.

```
┌─────────────────────────────────────────────────────────────┐
│                    Deployment Layer                          │
│  ┌──────────────────┐              ┌──────────────────┐     │
│  │  Standalone Mode │              │   Plugin Mode    │     │
│  │   (Python GUI)   │              │  (UE C++ + IPC)  │     │
│  └────────┬─────────┘              └────────┬─────────┘     │
└───────────┼──────────────────────────────────┼──────────────┘
            │                                  │
            └──────────┬───────────────────────┘
                       │
            ┌──────────▼───────────────────────────────────┐
            │         Core AI Backend (Python)             │
            │  ┌────────────────────────────────────────┐  │
            │  │    RAG System (Phase 1)                │  │
            │  │  • Document Ingestion                  │  │
            │  │  • Vector Database (ChromaDB)          │  │
            │  │  • Query Processing                    │  │
            │  │  • LLM Integration                     │  │
            │  └────────────────────────────────────────┘  │
            │  ┌────────────────────────────────────────┐  │
            │  │    Planning System (Phase 2)           │  │
            │  │  • Goal Analysis                       │  │
            │  │  • Task Decomposition                  │  │
            │  │  • Dependency Resolution               │  │
            │  │  • Code Generation                     │  │
            │  └────────────────────────────────────────┘  │
            │  ┌────────────────────────────────────────┐  │
            │  │    Agent System (Phase 3)              │  │
            │  │  • Agent Orchestrator                  │  │
            │  │  • Event Bus                           │  │
            │  │  • Shared State                        │  │
            │  │  • Remote Control API                  │  │
            │  └────────────────────────────────────────┘  │
            └──────────────────────────────────────────────┘
                       │
            ┌──────────▼───────────────────────────────────┐
            │         External Services                     │
            │  • LLM APIs (Gemini, OpenAI, Ollama)         │
            │  • Embedding Models (HuggingFace, OpenAI)    │
            │  • GitHub API (for repo ingestion)           │
            └──────────────────────────────────────────────┘
```

## Core Components

### 1. RAG System (Phase 1)

The Retrieval-Augmented Generation system provides context-aware Q&A capabilities.

**Key Components:**
- **Document Ingestion:** `ingest.py`, `ingest_game_repo.py`
- **Vector Database:** ChromaDB for storing embeddings
- **Query Processing:** `main.py` - handles user queries
- **LLM Integration:** `llm_config.py` - manages LLM providers

**Data Flow:**
```
Documents → Chunking → Embedding → Vector DB → Similarity Search → LLM → Answer
```

**Technologies:**
- **ChromaDB:** Vector database for embeddings
- **Sentence Transformers:** Default embedding model
- **LangChain:** Document processing and chunking
- **OpenAI/Gemini:** LLM providers

### 2. Planning System (Phase 2)

Intelligent goal decomposition and task planning.

**Key Components:**
- **Goal Analysis:** `goal_analysis_agent.py` - analyzes and classifies goals
- **Task Decomposition:** `task_decomposition_agent.py` - breaks down goals into tasks
- **Planning CLI:** `planning_cli.py`, `planner.py` - user interfaces
- **Models:** `planning_models.py` - data structures for plans and tasks

**Data Flow:**
```
Goal → Analysis → Classification → Decomposition → Task Graph → Action Plan
```

**Features:**
- Dependency resolution
- Effort estimation
- Priority assignment
- Code generation suggestions
- Multiple export formats (Markdown, JSON, Text)

### 3. Agent System (Phase 3)

Autonomous agents for proactive monitoring and assistance.

**Key Components:**
- **Agent Orchestrator:** `agent_orchestrator_cli.py` - manages agent lifecycle
- **Event Bus:** Pub/sub system for agent communication
- **Shared State:** Thread-safe state management
- **Remote Control API:** `remote_control/` - external integration
- **Dashboard:** `agent_dashboard.py` - real-time monitoring

**Agent Types:**
- **Performance Agent:** Monitors and optimizes performance
- **Bug Detection Agent:** Identifies and analyzes bugs
- **Code Quality Agent:** Reviews code quality and suggests improvements

**Architecture Pattern:**
```
Orchestrator → Event Bus ← Agents
                 ↕
            Shared State
                 ↕
          Remote Control API
```

## Deployment Modes

### Standalone Mode

**Purpose:** Development, testing, and standalone use

**Components:**
- Python CLI (`main.py`, `planner.py`, `agent_orchestrator_cli.py`)
- Python GUI (`gui_director.py`)
- Agent Dashboard (`agent_dashboard.py`)

**Advantages:**
- ✅ Easy to debug and test
- ✅ Rapid iteration
- ✅ Platform-independent
- ✅ Full feature access

**Use Cases:**
- Documentation Q&A
- Planning and task management
- Agent development and testing
- Non-UE game development

### Plugin Mode (Unreal Engine)

**Purpose:** Integrated in-editor workflow

**Components:**
- C++ UE Plugin (`Plugins/AdastreaDirector/`)
- Python Backend (same as standalone)
- IPC Bridge (inter-process communication)
- UE Python API integration

**Advantages:**
- ✅ Integrated editor experience
- ✅ Direct UE Python API access
- ✅ No context switching
- ✅ Editor automation

**Architecture:**
```
UE Editor
    ↕ (IPC/HTTP)
Python Backend → UE Python API
```

**Use Cases:**
- In-editor documentation search
- Asset and actor queries
- Console command execution
- Editor automation

## Data Storage

### Vector Database (ChromaDB)

**Location:** `./chroma_db`

**Structure:**
```
chroma_db/
├── index/          # Vector indices
├── metadata/       # Document metadata
└── storage/        # Persistent storage
```

**Features:**
- Persistent storage
- Fast similarity search
- Metadata filtering
- Incremental updates

### Configuration Storage

**Location:** `~/.adastrea/config.json`

**Contents:**
```json
{
  "api_keys": {
    "gemini": "encrypted_key",
    "openai": "encrypted_key"
  },
  "settings": {
    "llm_provider": "gemini",
    "embedding_provider": "huggingface"
  }
}
```

**Security:**
- Keys are encrypted with machine-specific salt
- Config is stored in user directory (not repository)
- Environment variables override config

### Agent State Storage

**Location:** In-memory + optional persistence

**Structure:**
```python
{
  "agents": {
    "performance": {"status": "running", "metrics": {...}},
    "bug_detection": {"status": "idle", "last_run": ...}
  },
  "events": [...],
  "shared_state": {...}
}
```

## Communication Patterns

### Event-Driven Architecture (Phase 3)

Agents communicate via an event bus:

```python
# Agent publishes event
event_bus.publish("performance.warning", {
  "metric": "fps",
  "value": 30,
  "threshold": 60
})

# Other agents subscribe
event_bus.subscribe("performance.*", callback)
```

**Benefits:**
- Loose coupling between agents
- Scalable architecture
- Easy to add new agents
- Asynchronous processing

### Request-Response (RAG & Planning)

Traditional request-response for user queries:

```python
# User query
query = "How do I implement feature X?"

# System processes
context = vector_db.similarity_search(query)
answer = llm.generate(context, query)

# Return response
return answer
```

### IPC for Plugin Mode

Plugin communicates with backend via HTTP/IPC:

```cpp
// C++ Plugin sends request
FString Response = SendHTTPRequest("http://localhost:8000/query", Query);

// Python backend processes
@app.route('/query', methods=['POST'])
def query():
    result = director.query(request.json['query'])
    return jsonify(result)
```

## Design Patterns

### 1. Strategy Pattern (LLM Providers)

Different LLM providers implement the same interface:

```python
class LLMProvider:
    def generate(self, prompt: str) -> str:
        pass

class GeminiProvider(LLMProvider):
    def generate(self, prompt: str) -> str:
        # Gemini-specific implementation
        pass

class OpenAIProvider(LLMProvider):
    def generate(self, prompt: str) -> str:
        # OpenAI-specific implementation
        pass
```

### 2. Observer Pattern (Event Bus)

Agents observe events without tight coupling:

```python
class Agent:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.event_bus.subscribe("*", self.on_event)
    
    def on_event(self, event):
        # React to event
        pass
```

### 3. Factory Pattern (Agent Creation)

Orchestrator creates agents via factory:

```python
class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str):
        if agent_type == "performance":
            return PerformanceAgent()
        elif agent_type == "bug_detection":
            return BugDetectionAgent()
```

### 4. Singleton Pattern (Shared State)

Single source of truth for agent state:

```python
class SharedState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

## Scalability Considerations

### Current Scale

- **Documents:** Up to 10,000 chunks
- **Agents:** Up to 10 concurrent agents
- **Users:** Single user (local deployment)

### Future Scaling

**Multi-User Support:**
- Add authentication and authorization
- Separate databases per user/project
- Load balancing for LLM requests

**Distributed Agents:**
- Deploy agents as separate microservices
- Use message queue (RabbitMQ, Kafka) instead of in-memory event bus
- Horizontal scaling for agent workers

**Cloud Deployment:**
- Containerize with Docker
- Deploy to Kubernetes
- Use cloud vector databases (Pinecone, Weaviate)

## Security Considerations

### API Key Management

- ✅ Keys encrypted at rest
- ✅ Never committed to repository
- ✅ Machine-specific encryption
- ✅ Environment variables supported

### Data Privacy

- ✅ All data processed locally (except LLM API calls)
- ✅ No telemetry or analytics
- ✅ User controls all data
- ✅ Option for local LLMs (Ollama)

### Code Execution

- ❌ No arbitrary code execution
- ✅ Sandboxed environments for future code gen
- ✅ User review required for generated code

## Performance Characteristics

### RAG System

- **First Query:** 5-10 seconds (model loading)
- **Subsequent Queries:** 1-3 seconds
- **Ingestion:** ~100 documents/minute
- **Database Size:** ~1MB per 1000 chunks

### Planning System

- **Goal Analysis:** 2-5 seconds
- **Task Decomposition:** 5-15 seconds (depends on goal complexity)
- **Plan Export:** <1 second

### Agent System

- **Agent Startup:** <1 second
- **Event Processing:** <100ms
- **Dashboard Update:** 500ms (configurable)

## Technology Stack

### Core Technologies

- **Python 3.9+:** Main language
- **ChromaDB:** Vector database
- **LangChain:** Document processing
- **Sentence Transformers:** Embeddings
- **tkinter:** GUI framework

### LLM Integration

- **Google Gemini:** Recommended (free tier)
- **OpenAI GPT:** Alternative
- **Ollama:** Local deployment

### Unreal Engine Plugin

- **C++:** Plugin implementation
- **UE Python API:** Editor automation
- **Slate UI:** User interface
- **HTTP/IPC:** Backend communication

### Development Tools

- **pytest:** Testing framework (230+ tests)
- **black:** Code formatting
- **mypy:** Type checking
- **GitHub Actions:** CI/CD

## Related Documentation

- [Agent Architecture](Agent-Architecture.md) - Deep dive into P3 agents
- [Deployment Modes](Deployment-Modes.md) - Choosing the right mode
- [Code Reference](../development/Code-Reference.md) - API documentation
- [Testing Guide](../development/Testing.md) - Testing strategy

---

[← Back to Home](../Home.md)
