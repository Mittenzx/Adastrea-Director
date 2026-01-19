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

### Legacy Components (Phase 2: Deprecation in Progress)

These components support the old IPC-based architecture. They are marked as **DEPRECATED** and will be removed in Phase 3.

⚠️ **MIGRATION REQUIRED** - See `MIGRATION_GUIDE.md` for migration instructions.

| Component | Purpose | Status |
|-----------|---------|--------|
| **PythonProcessManager** | External Python process management | ⚠️ **DEPRECATED** (Phase 2) |
| **IPCClient** | TCP socket communication with Python | ⚠️ **DEPRECATED** (Phase 2) |
| **PythonBridge** | Wrapper using ProcessManager + IPCClient | ⚠️ **DEPRECATED** (Phase 2) |
| **ipc_server.py** | Python IPC server process | ⚠️ **DEPRECATED** (Phase 2) |

**Deprecation Notices:**
- All legacy components now emit deprecation warnings when used
- New features MUST use VibeUE components
- Existing code should be migrated to VibeUE components
- Legacy components will be removed in Phase 3 (Q2 2026)

**Migration Path:**
- `PythonProcessManager` → `AdastreaScriptService`
- `IPCClient` → `AdastreaLLMClient`
- `PythonBridge` → Multiple VibeUE components (see MIGRATION_GUIDE.md)
- `ipc_server.py` → Not needed (eliminated entirely)

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

## 🚀 Migration Phases

The transition from legacy IPC architecture to VibeUE is happening in phases:

### Phase 1: VibeUE Implementation ✅ Complete (January 2026)
- All VibeUE components implemented and tested
- New architecture working alongside legacy system
- Documentation and examples created
- **Status:** Complete

### Phase 2: Gradual Cutover 🚧 In Progress (Q1 2026)
**Goal:** Deprecate legacy components while maintaining backwards compatibility

**Current Status:**
- ✅ Deprecation warnings added to all legacy components:
  - `FPythonProcessManager` - Warns on construction and key methods
  - `FIPCClient` - Warns on construction and connection
  - `FPythonBridge` - Warns on construction and initialization
  - `ipc_server.py` - Warns on startup
- ✅ `MIGRATION_GUIDE.md` created with complete migration instructions
- ✅ Architecture documentation updated
- 🚧 Route new features through C++ services (ongoing)
- 🚧 Migration of existing code (ongoing)
- 📅 Maintain backwards compatibility until Phase 3

**Guidelines for Phase 2:**
- **All new features** MUST use VibeUE components
- **Existing code** SHOULD be migrated when touched
- **Legacy components** remain functional but emit warnings
- **Tests** should be updated to use VibeUE components
- **Documentation** should reference VibeUE components

### Phase 3: Complete Migration 📅 Planned (Q2 2026)
**Goal:** Remove all legacy components and IPC infrastructure

**Planned Changes:**
- ❌ Remove `FPythonProcessManager` class and source files
- ❌ Remove `FIPCClient` class and source files
- ❌ Remove `FPythonBridge` class and source files
- ❌ Remove `ipc_server.py` and related Python IPC infrastructure
- 🔄 Update all documentation to remove legacy references
- 🔄 Remove legacy component tests
- 🔄 Clean up build dependencies (Sockets, Networking modules if unused)
- ✅ Update `ROADMAP.md` to reflect completion

**Prerequisites for Phase 3:**
- All internal code migrated to VibeUE
- External users notified of deprecation (1+ release cycle)
- Migration guide validated with real-world use cases
- No outstanding migration blockers

## 🖥️ Standalone Python System

The standalone system remains fully functional and provides:

### Components

Located in repository root:

| Component | Purpose |
|-----------|---------|
| **main.py** | RAG-based Q&A CLI |
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

### Current State: Phase 2 (Gradual Cutover) 🚧
- ✅ VibeUE architecture fully implemented (5 major components)
- ✅ Deprecation warnings added to all legacy components
- ✅ Migration guide created and comprehensive
- ✅ Standalone Python system fully functional
- 🚧 Legacy IPC components deprecated but functional
- 🚧 Active migration of existing code to VibeUE
- 📅 Phase 3 removal planned for Q2 2026

### Next Steps
1. Continue migrating existing code to VibeUE components
2. Update all examples to use VibeUE components
3. Validate migration guide with real-world scenarios
4. Monitor for migration blockers or issues
5. Prepare for Phase 3 removal (Q2 2026)

See `MIGRATION_GUIDE.md` for detailed migration instructions.

### Roadmap

**Phase 2 (Current):** Gradual Cutover 🚧
- ✅ Deprecation warnings added to legacy components
- ✅ Migration guide created
- 🚧 New features using VibeUE components
- 🚧 Existing code migration
- 📅 Backwards compatibility maintained

**Phase 3 (Planned Q2 2026):** Complete Migration
- Remove PythonProcessManager, IPCClient, PythonBridge
- Remove ipc_server.py Python IPC infrastructure
- Update all documentation
- Clean up build dependencies
- Final validation and testing

## 📚 Documentation

### Migration
- `MIGRATION_GUIDE.md` - Complete guide for migrating from legacy IPC to VibeUE
- `VIBEUE_ARCHITECTURE_SUMMARY.md` - Technical implementation details
- `ARCHITECTURE.md` - This file - overall system architecture

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
