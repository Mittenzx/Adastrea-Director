# MCP Readiness Plan - Adastrea Director & Adastrea-MCP Integration

**Date**: December 31, 2025  
**Status**: Assessment Complete - Action Plan Defined  
**Related Repositories**: 
- Adastrea-Director: https://github.com/Mittenzx/Adastrea-Director
- Adastrea-MCP: https://github.com/Mittenzx/Adastrea-MCP

---

## Executive Summary

The Adastrea ecosystem currently has **two complementary MCP (Model Context Protocol) implementations**:

1. **Adastrea-Director MCP** (Python) - Runtime integration with Unreal Engine Editor
2. **Adastrea-MCP** (Node.js/TypeScript) - Static analysis, code generation, and UE knowledge

This document outlines the readiness assessment and integration strategy to bring these systems together into a cohesive development experience.

### Current Status

✅ **Adastrea-Director MCP** (Python - this repository):
- 13 MCP tools implemented (`mcp_server/server.py`)
- Python Remote Execution protocol for UE Editor
- Works with VS Code + GitHub Copilot via stdio
- 84 tests (per ROADMAP.md)
- Tools: `editor_run_python`, `editor_list_assets`, `editor_console_command`, etc.

✅ **Adastrea-MCP** (Node.js - separate repository):
- 37 MCP tools, 13 MCP resources
- Phases 1, 2.1, 2.2, 2.3, and 3.1 complete
- Static project analysis, Blueprint interaction, actor management
- Code generation (8 tools for UE-compliant code)
- UE5.6+ knowledge database
- **Phase 2.1 complete**: Infrastructure to call Adastrea-Director REST API

### The Gap

**Adastrea-MCP needs REST API endpoints from Adastrea-Director to fully integrate.**

Currently:
- Adastrea-MCP has infrastructure ready (DirectorClient, EditorBridge)
- Adastrea-Director has MCP tools but no REST API
- Both can work independently but not together yet

---

## Architecture Overview

### Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent (Claude, VS Code Copilot)       │
└───────────────┬──────────────────────┬──────────────────────┘
                │                      │
                │ stdio MCP            │ stdio MCP
                │                      │
        ┌───────▼───────┐      ┌──────▼──────────┐
        │ Adastrea-     │      │ Adastrea-MCP    │
        │ Director MCP  │      │ (Node.js)       │
        │ (Python)      │      │ 37 tools        │
        │ 13 tools      │      │ Static analysis │
        └───────┬───────┘      └─────────────────┘
                │
                │ Python Remote Execution
                │
        ┌───────▼────────────────────┐
        │ Unreal Engine Editor       │
        │ (with Python plugin)       │
        └────────────────────────────┘
```

**Problem**: Two separate MCP servers cannot communicate with each other.

### Target Architecture (Option 1: REST API Integration)

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent (Claude, VS Code Copilot)       │
└─────────────────────────────┬───────────────────────────────┘
                              │ stdio MCP
                      ┌───────▼──────────┐
                      │ Adastrea-MCP     │
                      │ (Node.js)        │
                      │ 37 tools         │
                      │ Static analysis  │
                      └──────┬───────────┘
                             │
                             │ REST API (HTTP)
                             │
                      ┌──────▼───────────────┐
                      │ Adastrea-Director    │
                      │ REST API Server      │
                      │ (Python)             │
                      └──────┬───────────────┘
                             │
                             │ Python Remote Execution
                             │
                      ┌──────▼──────────────────┐
                      │ Unreal Engine Editor    │
                      │ (with Python plugin)    │
                      └─────────────────────────┘
```

**Benefits**:
- Single MCP endpoint for AI agents
- Adastrea-MCP handles static analysis (works offline)
- Adastrea-Director handles runtime operations (requires UE running)
- Clear separation of concerns
- Both repos remain independent

### Target Architecture (Option 2: Merged Repository)

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent (Claude, VS Code Copilot)       │
└─────────────────────────────┬───────────────────────────────┘
                              │ stdio MCP
                      ┌───────▼──────────────────┐
                      │ Adastrea-Director        │
                      │ Unified MCP Server       │
                      │                          │
                      │ ┌──────────────────────┐ │
                      │ │ Node.js MCP (37 tools)│ │
                      │ │ Static analysis      │ │
                      │ └──────────────────────┘ │
                      │                          │
                      │ ┌──────────────────────┐ │
                      │ │ Python MCP (13 tools)│ │
                      │ │ Runtime integration  │ │
                      │ └───────┬──────────────┘ │
                      └─────────┼────────────────┘
                                │
                                │ Python Remote Execution
                                │
                      ┌─────────▼──────────────────┐
                      │ Unreal Engine Editor       │
                      │ (with Python plugin)       │
                      └────────────────────────────┘
```

**Benefits**:
- Single repository to maintain
- Unified documentation
- Consistent versioning
- Easier deployment

**Drawbacks**:
- Adds Node.js dependency to Python project
- More complex build process
- Larger repository

---

## Feasibility Analysis Summary

Based on the comprehensive **MCP_DIRECTOR_MERGE_FEASIBILITY.md** analysis:

| Aspect | Score | Assessment |
|--------|-------|------------|
| Technical Feasibility | 95% | Very High |
| Strategic Value | Excellent | Strong fit for unified architecture |
| Risk Level | Low-Medium | Manageable with proper planning |
| Timeline | 2-4 weeks | For core integration |
| Complexity | Moderate | Primarily architectural refactoring |

**Recommendation from Feasibility Study**: **MERGE IS HIGHLY FEASIBLE**

---

## Integration Strategy

### Recommended Approach: **Hybrid Strategy**

1. **Phase 1 (Immediate)**: Keep separate, implement REST API
   - Implement REST API in Adastrea-Director (Python)
   - Enable Adastrea-MCP to call Director via HTTP
   - Validate full integration works
   - Timeline: 1-2 weeks

2. **Phase 2 (Later)**: Evaluate merge
   - After proving integration works
   - Based on maintenance burden
   - User feedback on deployment complexity
   - Timeline: TBD (Q1 2026)

### Why This Approach?

- ✅ **Lower risk**: Validate integration before committing to merge
- ✅ **Faster deployment**: REST API is simpler than full merge
- ✅ **Reversible**: Can still merge later if desired
- ✅ **Learn from usage**: Real-world feedback informs merge decision

---

## Phase 1: REST API Implementation

### Required Endpoints in Adastrea-Director

Based on `INTEGRATION_NOTES.md` from Adastrea-MCP:

#### 1. Health Check
```http
GET /health
Response: {
  "editorConnected": true,
  "version": "1.0.0",
  "capabilities": ["console", "python", "assets"]
}
```

#### 2. Editor State
```http
GET /api/editor/state
Response: {
  "isRunning": true,
  "currentLevel": "/Game/Maps/MainLevel",
  "selectedActors": ["..."],
  "editingContext": { "mode": "LevelEditor" }
}
```

#### 3. Project Info
```http
GET /api/project/info
Response: {
  "projectName": "MyGame",
  "projectPath": "C:/Projects/MyGame",
  "engineVersion": "5.6",
  "isLoaded": true
}
```

#### 4. List Assets
```http
POST /api/assets/list
Request: { "filter": "Material" }
Response: [
  {
    "assetName": "M_Base",
    "assetPath": "/Game/Materials/M_Base",
    "assetClass": "Material"
  }
]
```

#### 5. Console Command
```http
POST /api/console/execute
Request: { "command": "stat fps" }
Response: {
  "command": "stat fps",
  "output": "FPS display enabled",
  "success": true
}
```

#### 6. Python Execution
```http
POST /api/python/execute
Request: { "code": "import unreal\nprint('Hello')" }
Response: {
  "code": "...",
  "output": "Hello",
  "error": null,
  "success": true
}
```

### Implementation Plan

1. **Create REST API Module** (`rest_api/`)
   - `server.py` - Flask/FastAPI server
   - `routes.py` - Endpoint handlers
   - `models.py` - Request/response models
   - `bridge.py` - Bridge to existing MCP tools

2. **Reuse Existing MCP Tools**
   - REST endpoints delegate to existing MCP tool implementations
   - Minimal code duplication
   - Maintain single source of truth

3. **Add Configuration**
   - Port configuration (default: 3001)
   - CORS settings for web clients
   - Authentication (optional)

4. **Testing**
   - Unit tests for each endpoint
   - Integration tests with Adastrea-MCP
   - Load testing for performance

---

## Tool Delegation Strategy

### Adastrea-MCP (Static Analysis) - Handles:
- `.uproject` file parsing
- C++ code analysis (UCLASS, USTRUCT, etc.)
- Blueprint metadata extraction (offline)
- Asset registry scanning (offline)
- Code generation
- UE5.6+ knowledge queries
- Project structure analysis

### Adastrea-Director (Runtime) - Handles:
- Python execution in UE Editor
- Console command execution
- Live asset queries
- Actor spawning/modification
- Blueprint runtime inspection
- Editor state queries
- Live level information

### Shared Capabilities (Both Can Handle):
- Asset listing (MCP: offline cache, Director: live query)
- Blueprint inspection (MCP: static structure, Director: runtime state)
- Project info (MCP: .uproject data, Director: live editor info)

**Decision Rule**: Adastrea-MCP tries static analysis first, calls Director if runtime data needed.

---

## Deployment Scenarios

### Scenario 1: AI Agent with Both MCP Servers

**Use Case**: Claude Desktop or VS Code Copilot with full capabilities

**Setup**:
```json
{
  "mcpServers": {
    "adastrea-mcp": {
      "command": "node",
      "args": ["/path/to/Adastrea-MCP/build/index.js"],
      "env": {
        "DIRECTOR_URL": "http://localhost:3001"
      }
    }
  }
}
```

**What happens**:
1. AI agent connects to Adastrea-MCP
2. Adastrea-MCP provides 37 tools
3. When AI uses runtime tools, Adastrea-MCP calls Director REST API
4. Graceful fallback if Director not running

### Scenario 2: VS Code Copilot with Director Only

**Use Case**: Lightweight setup, only runtime features

**Setup**:
```json
{
  "github.copilot.chat.experimental.mcpServers": {
    "adastrea-unreal": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/Adastrea-Director"
    }
  }
}
```

**What happens**:
1. VS Code Copilot connects to Adastrea-Director MCP
2. 13 runtime tools available
3. No static analysis features

### Scenario 3: Full Stack (Recommended)

**Use Case**: Maximum capabilities for production use

**Components**:
1. **Adastrea-MCP server** (Node.js) - stdio MCP
2. **Adastrea-Director REST API** (Python) - HTTP server
3. **Unreal Engine** with Python plugin

**Setup Steps**:
1. Start Adastrea-Director REST API: `python -m rest_api.server`
2. Start Unreal Engine with project
3. Configure AI agent to use Adastrea-MCP
4. Adastrea-MCP automatically connects to Director REST API

---

## Testing & Validation

### Test Checklist

#### Integration Testing
- [ ] Adastrea-MCP can reach Director REST API
- [ ] Health check endpoint returns correct status
- [ ] Console commands execute successfully
- [ ] Python execution works
- [ ] Asset listing returns live data
- [ ] Graceful fallback when Director unavailable

#### Performance Testing
- [ ] Response time < 100ms for simple queries
- [ ] Response time < 2s for complex operations
- [ ] No memory leaks during long sessions
- [ ] Handles 10+ concurrent requests

#### Compatibility Testing
- [ ] Works with VS Code Copilot
- [ ] Works with Claude Desktop
- [ ] Works with Cline
- [ ] Works with Zed editor

#### Error Handling
- [ ] Graceful degradation when UE not running
- [ ] Clear error messages
- [ ] Automatic reconnection after connection loss
- [ ] Timeout handling

---

## Documentation Requirements

### New Documents Needed

1. **MCP Integration Guide**
   - How both systems work together
   - Architecture diagrams
   - Deployment scenarios
   - Troubleshooting

2. **REST API Documentation**
   - Endpoint specifications
   - Request/response examples
   - Authentication (if added)
   - Rate limiting

3. **Developer Guide**
   - How to extend MCP tools
   - Adding new endpoints
   - Testing strategies
   - Debugging tips

4. **User Quick Start**
   - Installation steps
   - Configuration examples
   - Common use cases
   - FAQ

### Documents to Update

- [ ] README.md - Add Adastrea-MCP relationship
- [ ] ROADMAP.md - Update with REST API milestone
- [ ] mcp_server/MCP_SERVER_GUIDE.md - Add REST API section
- [ ] CONTRIBUTING.md - Add REST API development guidelines

---

## Timeline & Milestones

### Week 1: REST API Foundation
- [ ] Day 1-2: Design REST API architecture
- [ ] Day 3-4: Implement core endpoints (health, project info)
- [ ] Day 5: Testing and documentation

### Week 2: Full Integration
- [ ] Day 1-2: Implement remaining endpoints (console, python, assets)
- [ ] Day 3: Integration testing with Adastrea-MCP
- [ ] Day 4: Performance optimization
- [ ] Day 5: Documentation completion

### Week 3-4: Polish & Deployment
- [ ] Week 3: User acceptance testing, bug fixes
- [ ] Week 4: Deployment guide, video tutorials, release

---

## Success Metrics

How we'll know the integration is successful:

| Metric | Target | Measurement |
|--------|--------|-------------|
| REST API uptime | 99%+ | Monitoring |
| Response time (simple queries) | < 100ms | Performance tests |
| Response time (complex ops) | < 2s | Performance tests |
| Test coverage | 80%+ | Coverage report |
| Documentation completeness | 100% | Manual review |
| User satisfaction | 4.5/5+ | User feedback |
| GitHub issues (integration bugs) | < 5 | Issue tracker |

---

## Risk Analysis & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| REST API adds latency | Medium | High | Optimize, use HTTP keep-alive, local connections |
| Port conflicts | Low | Medium | Configurable ports, auto-detect |
| Two repos hard to maintain | High | Medium | Automate cross-repo testing, shared CI |
| Breaking changes in Director | Medium | Medium | Versioning, deprecation policy |
| Authentication complexity | Low | Low | Start without auth, add later if needed |

---

## Decision Matrix: Merge vs. Separate

| Factor | Separate Repos | Merged Repo |
|--------|---------------|-------------|
| Maintenance effort | Higher (2 repos) | Lower (1 repo) |
| Deployment complexity | Higher | Lower |
| Technology stack | Node.js + Python | Node.js + Python |
| Build complexity | Lower | Higher |
| Versioning | Independent | Unified |
| Community contributions | May split focus | Concentrated |
| **Recommendation** | **Phase 1: Start here** | **Phase 2: Consider later** |

---

## Next Actions

### Immediate (This Week)
1. [ ] Create REST API module structure in Adastrea-Director
2. [ ] Implement health check endpoint
3. [ ] Test basic connectivity from Adastrea-MCP
4. [ ] Document REST API design decisions

### Short Term (Next 2 Weeks)
1. [ ] Implement all 6 core endpoints
2. [ ] Integration testing suite
3. [ ] Update documentation
4. [ ] Create deployment guide

### Medium Term (Next Month)
1. [ ] User acceptance testing
2. [ ] Performance optimization
3. [ ] Video tutorials
4. [ ] Community feedback

### Long Term (Q1 2026)
1. [ ] Evaluate merge decision
2. [ ] Advanced features (WebSocket, events)
3. [ ] Scale testing
4. [ ] Production deployment guide

---

## Resources & References

### Documentation
- Adastrea-MCP: `MCP_DIRECTOR_MERGE_FEASIBILITY.md`
- Adastrea-MCP: `INTEGRATION_NOTES.md`
- Adastrea-MCP: `NEXT_STEPS.md`
- Adastrea-MCP: `ROADMAP.md`
- Adastrea-Director: `mcp_server/MCP_SERVER_GUIDE.md`
- Adastrea-Director: `Documentation/guides/IPC_MCP_INTEGRATION_GUIDE.md`

### Tools & Libraries
- Flask/FastAPI for REST API
- Requests library for testing
- pytest for integration tests
- Swagger/OpenAPI for API docs

### Community
- GitHub Issues for both repos
- Discord (if available)
- Unreal Slackers Discord

---

## Conclusion

The Adastrea ecosystem has built two powerful MCP implementations that complement each other perfectly:

- **Adastrea-MCP**: Static analysis powerhouse (37 tools, UE knowledge, code generation)
- **Adastrea-Director**: Runtime integration master (13 tools, live editor control)

**The path forward is clear**:

1. ✅ Phase 1: Implement REST API (2 weeks)
2. ✅ Validate integration works seamlessly
3. ✅ Gather user feedback
4. ⏳ Phase 2: Evaluate merge based on real-world usage

This hybrid approach minimizes risk while maximizing value delivery to users.

---

**Status**: Ready to proceed with Phase 1  
**Next Milestone**: REST API implementation  
**Target Date**: January 14, 2026  
**Success Criteria**: Full integration working, documented, tested

Let's build something amazing! 🚀
