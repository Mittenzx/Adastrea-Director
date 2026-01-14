# Adastrea Director Architecture

## Overview

Adastrea Director provides AI-powered development assistance for Unreal Engine projects through two complementary systems:

1. **Standalone Python System** - Full-featured CLI/GUI application
2. **Unreal Engine C++ Plugin** - Native integration using VibeUE architecture

## 🎯 VibeUE Architecture (Current Focus)

The plugin has been modernized following the **VibeUE architecture pattern**, which eliminates the need for external Python processes and IPC communication.

### Core Principles

- ✅ **Direct LLM Integration** - Native C++ HTTP calls to LLM APIs (Gemini, OpenAI)
- ✅ **Built-in Python** - Uses Unreal's IPythonScriptPlugin for in-process Python execution
- ✅ **Runtime Asset Discovery** - Live queries via Asset Registry (no document ingestion)
- ✅ **Tool System** - Extensible tool registration for AI agent capabilities
- ✅ **MCP Protocol** - Standard protocol for external AI client integration

### New C++ Components (VibeUE)

Located in `Plugins/AdastreaDirector/Source/AdastreaDirector/`:

| Component | Purpose | Status |
|-----------|---------|--------|
| **AdastreaScriptService** | In-process Python execution | ✅ Complete |
| **AdastreaLLMClient** | Direct LLM API calls (Gemini, OpenAI) | ✅ Complete |
| **AdastreaAssetService** | Runtime asset discovery via Asset Registry | ✅ Complete |
| **AdastreaToolSystem** | Tool registration and execution | ✅ Complete |
| **AdastreaMCPServer** | MCP protocol server for external clients | ✅ Complete |

### Legacy Components (Transitional)

These components support the old IPC-based architecture and are maintained for compatibility during the transition:

| Component | Purpose | Status |
|-----------|---------|--------|
| **PythonProcessManager** | External Python process management | ⚠️ Legacy (parallel operation) |
| **IPCClient** | TCP socket communication with Python | ⚠️ Legacy (parallel operation) |
| **PythonBridge** | Wrapper using ProcessManager + IPCClient | ⚠️ Legacy (parallel operation) |

**Note:** According to `VIBEUE_COMPLETION_SUMMARY.md`, legacy components will be removed in Phase 4 cleanup after full migration validation.

## 📊 Architecture Comparison

### Old Architecture (Pre-VibeUE)
```
┌─────────────────┐
│  Unreal Engine  │
│     Plugin      │
└────────┬────────┘
         │ IPC (Port 8765)
         ↓
┌─────────────────┐
│  Python Process │
│   - IPC Server  │
│   - LLM Client  │
│   - RAG System  │
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────┐
│   LLM APIs      │
│ (Gemini/OpenAI) │
└─────────────────┘
```

**Issues:**
- External process can fail to start
- IPC connections can drop
- Python dependency conflicts
- High latency (~200ms IPC overhead)
- Complex debugging (multiple processes)

### New Architecture (VibeUE)
```
┌──────────────────────────────────────┐
│         Unreal Engine Plugin         │
│  ┌────────────────────────────────┐  │
│  │   AdastreaScriptService        │  │
│  │   (IPythonScriptPlugin)        │  │
│  ├────────────────────────────────┤  │
│  │   AdastreaLLMClient            │──┼─→ Gemini API
│  │   (Direct HTTP)                │  │
│  │                                │──┼─→ OpenAI API
│  ├────────────────────────────────┤  │
│  │   AdastreaAssetService         │  │
│  │   (Asset Registry)             │  │
│  ├────────────────────────────────┤  │
│  │   AdastreaToolSystem           │  │
│  │   (Tool Registry)              │  │
│  ├────────────────────────────────┤  │
│  │   AdastreaMCPServer            │  │
│  │   (HTTP Server)                │◄─┼─ VS Code
│  │                                │  │
│  │                                │◄─┼─ Claude Desktop
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

**Benefits:**
- No external process to fail
- 75% lower latency (~50ms vs ~200ms)
- 90% less memory usage
- Direct HTTP streaming support
- Single-process debugging
- Always-current asset data

## 🖥️ Standalone Python System

The standalone system remains fully functional and provides:

### Components

Located in repository root:

| Component | Purpose |
|-----------|---------|
| **main.py** | RAG-based Q&A CLI |
| **gui_director.py** | Full-featured GUI application |
| **planner.py / planning_cli.py** | Goal decomposition and planning |
| **agent_orchestrator_cli.py** | Phase 3 autonomous agents CLI |
| **agent_dashboard.py** | Real-time agent monitoring |
| **ingest.py / ingest_game_repo.py** | Document ingestion |
| **agents/** | Planning and autonomous agents |
| **remote_control/** | UE Remote Control API client |
| **mcp_server/** | MCP server for UE integration |

### Use Cases

The standalone system is ideal for:
- Development and testing without UE running
- RAG-based documentation queries
- Goal planning and task decomposition
- Autonomous agent monitoring
- Non-UE game development
- CI/CD integration

## 🔄 Migration Status

### Current State
- ✅ VibeUE architecture fully implemented (5 major components)
- ✅ Standalone Python system fully functional
- ⚠️ Legacy IPC components maintained for parallel operation
- ⚠️ Full migration to VibeUE pending validation

### Roadmap

**Phase 3.5 (Current):** VibeUE Architecture Implementation ✅
- All core components complete
- Documentation complete
- Manual testing complete
- Unit tests pending

**Phase 4 (Future):** Complete Migration
- Unit and integration tests
- Feature flags for gradual rollout
- Deprecation warnings on legacy components
- Remove PythonProcessManager, IPCClient, PythonBridge
- Update all documentation

## 📚 Documentation

### VibeUE Implementation
- `VIBEUE_EXECUTIVE_SUMMARY.md` - High-level overview and motivation
- `VIBEUE_ARCHITECTURE_SUMMARY.md` - Component details and usage
- `VIBEUE_IMPLEMENTATION_GUIDE.md` - Complete implementation guide (2,929 lines)
- `VIBEUE_COMPLETION_SUMMARY.md` - Implementation results and metrics
- `VIBEUE_RESEARCH_COMPARISON.md` - Comparison with VibeUE reference project

### General Documentation
- `README.md` - Project overview and quick start
- `ROADMAP.md` - Project roadmap and phase tracking
- `CONTRIBUTING.md` - Contribution guidelines
- [Adastrea Director Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki) - Complete documentation

## 🔑 Key Takeaways

1. **Two Systems, One Goal**: Standalone Python + C++ Plugin both provide AI-powered UE development assistance
2. **VibeUE = Modern Plugin**: Direct LLM calls, no external processes, runtime asset queries
3. **Standalone = Full Featured**: CLI/GUI with planning, agents, RAG, and monitoring
4. **Legacy IPC = Transitional**: Old IPC components maintained for compatibility, will be removed
5. **MCP Protocol**: Both systems can integrate with external AI clients (VS Code, Claude, etc.)

For detailed usage instructions, see the [Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki).
