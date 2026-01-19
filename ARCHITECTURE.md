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

### Legacy Components - REMOVED ✅ (Phase 3 Complete - January 2026)

**All legacy IPC components have been removed as of Phase 3 migration (January 2026):**

| Component | Status |
|-----------|--------|
| **PythonProcessManager** | ❌ **REMOVED** (Phase 3) |
| **IPCClient** | ❌ **REMOVED** (Phase 3) |
| **PythonBridge** | ❌ **REMOVED** (Phase 3) |
| **ipc_server.py** | ❌ **REMOVED** (Phase 3) |
| **Sockets/Networking modules** | ❌ **REMOVED** from build (Phase 3) |

**Migration Complete:**
- All IPC-based architecture removed
- Plugin operates entirely on VibeUE components
- Zero IPC latency, simplified architecture, better reliability
- See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for historical reference

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

### Phase 3: Complete Migration ✅ Complete (January 2026)
**Goal:** Remove all legacy components and IPC infrastructure

**Status: COMPLETE** ✅

All legacy IPC components have been successfully removed:
- ✅ Removed `FPythonProcessManager` class and source files
- ✅ Removed `FIPCClient` class and source files
- ✅ Removed `FPythonBridge` class and source files
- ✅ Removed `ipc_server.py` and related Python IPC infrastructure
- ✅ Removed IPC-related tests (test_ipc.py, test_ipc_performance.py, etc.)
- ✅ Removed `Sockets` and `Networking` modules from build configuration
- ✅ Updated module initialization to use VibeUE components only
- ✅ Updated startup validator to check VibeUE component availability

**Results:**
- ~5000+ lines of legacy code removed
- Zero IPC latency overhead eliminated
- Simplified single-process architecture
- Better reliability (no socket connection failures)
- Native C++ integration throughout

**Completion Date:** January 19, 2026

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

### Current State: ✅ Phase 3 Complete (January 2026)
- ✅ VibeUE architecture fully implemented (5 major components)
- ✅ Deprecation warnings added to all legacy components (Phase 2)
- ✅ Migration guide created and comprehensive (Phase 2)
- ✅ Legacy IPC components fully removed (Phase 3)
- ✅ Plugin operates entirely on VibeUE architecture
- ✅ ~5000+ lines of legacy code eliminated
- ✅ Zero IPC overhead, better reliability, simplified architecture

### Migration Complete

The migration from legacy IPC architecture to VibeUE is **100% complete**. All three phases finished:

1. **Phase 1:** VibeUE Implementation ✅ (January 2026)
2. **Phase 2:** Gradual Cutover ✅ (January 2026)
3. **Phase 3:** Complete Migration ✅ (January 2026)

The plugin now uses exclusively native C++ VibeUE components with no external process dependencies.

See `MIGRATION_GUIDE.md` for historical migration reference.

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
