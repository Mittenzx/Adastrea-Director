# Deployment Modes

Adastrea Director offers two deployment modes: **Standalone** and **Unreal Engine Plugin**. Both use the same Python backend, providing consistent functionality across different workflows.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              Deployment Layer                            │
│   ┌─────────────────┐        ┌─────────────────┐       │
│   │  Standalone     │        │  Plugin Mode    │       │
│   │  (Python)       │        │  (UE + Python)  │       │
│   └────────┬────────┘        └────────┬────────┘       │
└────────────┼──────────────────────────┼─────────────────┘
             │                          │
             └─────────┬────────────────┘
                       │
            ┌──────────▼──────────────────────┐
            │   Shared Python Backend         │
            │  • RAG System (P1)              │
            │  • Planning System (P2)         │
            │  • Agent System (P3)            │
            └─────────────────────────────────┘
```

## Standalone Mode

### Overview

Standalone mode provides a Python-based interface (CLI and GUI) for using Adastrea Director without Unreal Engine.

### When to Use

✅ **Use Standalone Mode when:**
- Working on non-Unreal Engine projects
- Testing and prototyping features
- Developing agents or backend components
- Needing quick access without loading UE
- Working on documentation or planning
- Running on systems without Unreal Engine

### Components

**CLI Applications:**
- `main.py` - Context-aware assistant
- `planner.py` - Planning system
- `agent_orchestrator_cli.py` - Agent management
- `agent_dashboard.py` - Real-time monitoring

### Features

✅ **All Core Features:**
- RAG-based Q&A system
- Document ingestion
- Planning and task decomposition
- Agent orchestration
- Real-time dashboard

### Installation

```bash
# Clone repository
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director

# Run setup script
./setup.sh

# Or install manually
pip install -r requirements.txt
```

See [Installation Guide](../installation/Getting-Started.md) for details.

### Usage

**CLI:**
```bash
# Context-aware assistant
python main.py

# Planning system
python planner.py --interactive

# Agent orchestrator
python agent_orchestrator_cli.py start --all
```

### Advantages

- ✅ **Fast Startup:** No need to load Unreal Engine
- ✅ **Lightweight:** Minimal system requirements
- ✅ **Easy Debugging:** Direct Python debugging
- ✅ **Platform Independent:** Works on any OS with Python
- ✅ **All Features:** Full access to all capabilities

### Limitations

- ❌ Not integrated into Unreal Engine workflow
- ❌ Requires context switching between tools
- ❌ No direct UE API access
- ❌ Manual asset/actor queries via CLI

## Plugin Mode

### Overview

Plugin mode integrates Adastrea Director directly into Unreal Engine Editor as a C++ plugin with Python backend communication.

### When to Use

✅ **Use Plugin Mode when:**
- Working primarily in Unreal Engine
- Need integrated in-editor experience
- Want to query UE assets and actors directly
- Performing editor automation tasks
- Avoiding context switching
- Working on UE-specific features

### Components

**C++ Plugin:**
- `Plugins/AdastreaDirector/` - UE plugin
- Slate UI for in-editor interface
- HTTP/IPC bridge to Python backend

**Python Backend:**
- Same backend as standalone mode
- Additional UE Python API integration
- HTTP server for plugin communication

### Features

✅ **Integrated Experience:**
- In-editor UI panel (dockable)
- Asset and actor queries
- Console command execution
- Editor automation
- Same RAG, Planning, and Agent features

✅ **UE Python API Access:**
- Query assets and actors
- Modify scene objects
- Execute console commands
- Editor notifications

### Installation

```bash
# 1. Copy plugin to UE project
cp -r Plugins/AdastreaDirector /path/to/UEProject/Plugins/

# 2. Regenerate project files
# Right-click .uproject → Generate Visual Studio project files

# 3. Build project
# Build in Visual Studio/Xcode

# 4. Launch Unreal Engine
# Window → Developer Tools → Adastrea Director
```

See [Plugin Setup Guide](../installation/Plugin-Setup.md) for details.

### Usage

**In-Editor:**
1. Open Unreal Engine Editor
2. Window → Developer Tools → Adastrea Director
3. Use Ingestion tab to add documentation
4. Use Query tab to ask questions
5. Python backend starts automatically!

**With UE Python API:**
```python
# Query assets
> List all StaticMesh assets in the project

# Spawn actors
> Spawn a PointLight at location (0, 0, 100)

# Execute commands
> Run command stat fps
```

### Advantages

- ✅ **Integrated Workflow:** No context switching
- ✅ **Direct UE Access:** Query assets, actors, and execute commands
- ✅ **Editor Automation:** Automate repetitive tasks
- ✅ **Natural Integration:** Part of UE editor
- ✅ **Same Backend:** All standalone features available

### Limitations

- ❌ UE startup time overhead
- ❌ More complex setup
- ❌ Platform-specific builds required
- ❌ Some features still in development (Weeks 1-6 complete)

### Current Status

**✅ Complete (Weeks 1-6):**
- Basic UI with tabbed interface
- RAG integration
- Document ingestion in-editor
- Query interface
- UE Python API integration

**🚧 In Progress (Weeks 7-16):**
- Planning system integration
- Agent orchestration UI
- Performance profiling panel
- Bug detection integration

## Comparison Table

| Feature | Standalone | Plugin |
|---------|-----------|--------|
| **Setup Complexity** | Easy | Moderate |
| **Startup Time** | Fast (seconds) | Slow (UE startup) |
| **Context Switching** | Required | Not required |
| **RAG System** | ✅ | ✅ |
| **Planning System** | ✅ | 🚧 |
| **Agent System** | ✅ | 🚧 |
| **UE Integration** | ❌ | ✅ |
| **Asset Queries** | Manual | Direct |
| **Editor Automation** | ❌ | ✅ |
| **Platform** | Any | UE-supported |
| **Development** | Easy | Moderate |
| **Non-UE Projects** | ✅ | ❌ |

## Hybrid Workflow

You can use both modes together!

**Example Workflow:**
1. **Planning** - Use standalone GUI for quick planning
2. **Implementation** - Use plugin in UE for implementation
3. **Monitoring** - Use standalone dashboard for agent monitoring
4. **Documentation** - Use standalone for doc queries

**Shared Resources:**
- Same knowledge base (chroma_db)
- Same configuration
- Same Python backend

## Choosing Your Mode

### Decision Flow

```
Are you using Unreal Engine?
  ├─ No → Use Standalone Mode
  └─ Yes
      └─ Do you need in-editor integration?
          ├─ Yes → Use Plugin Mode
          └─ No → Use Standalone Mode
              (faster, easier debugging)
```

### Recommendations

**For Individual Developers:**
- Start with **Standalone Mode** for learning
- Switch to **Plugin Mode** once comfortable
- Use both for different tasks

**For Teams:**
- **Standalone Mode** for designers/writers/planners
- **Plugin Mode** for UE developers
- **Both** for technical directors

**For Non-UE Projects:**
- **Standalone Mode** only

## Migration Between Modes

Switching between modes is seamless:

**Standalone → Plugin:**
1. Install plugin
2. Point to same `chroma_db` directory
3. Use same configuration
4. All data preserved

**Plugin → Standalone:**
1. Exit Unreal Engine
2. Use standalone CLI/GUI
3. Same database and config
4. No data loss

## Technical Details

### Communication Architecture

**Standalone:**
```
CLI/GUI → Python Backend → LLM/Vector DB
```

**Plugin:**
```
UE Plugin (C++) → HTTP/IPC → Python Backend → LLM/Vector DB
                                    ↕
                              UE Python API
```

### Backend Startup

**Standalone:**
- Backend runs directly in Python process
- Immediate availability

**Plugin:**
- Backend starts on plugin initialization
- HTTP server on localhost:8000 (configurable)
- Automatic startup/shutdown with UE

### Data Storage

Both modes share:
- **Vector DB:** `./chroma_db` or configured path
- **Config:** `~/.adastrea/config.json`
- **Logs:** Same logging directory

## Future Enhancements

### Planned Improvements

**Standalone:**
- Web-based UI (browser interface)
- VS Code extension
- CLI autocomplete

**Plugin:**
- Blueprint integration
- Visual scripting support
- In-game runtime queries

**Both:**
- Cloud synchronization
- Team collaboration features
- Multi-project support

## Getting Started

### For Standalone Mode
→ [Installation Guide](../installation/Getting-Started.md)

### For Plugin Mode
→ [Plugin Setup Guide](../installation/Plugin-Setup.md)

### For Both
→ [Quick Start Tutorial](../installation/Quick-Start.md)

## Related Documentation

- [System Architecture](System-Architecture.md)
- [Installation Guide](../installation/Getting-Started.md)
- [Plugin Setup](../installation/Plugin-Setup.md)
- [Usage Guides](../usage/Context-Aware-Assistant.md)

---

[← Back to Architecture](System-Architecture.md) | [Agent Architecture →](Agent-Architecture.md)
