# Adastrea Director - Unreal Engine Plugin

An AI-powered development assistant plugin for Unreal Engine that provides intelligent code assistance, automated planning, performance profiling, and bug detection capabilities.

## Overview

This plugin integrates the Adastrea Director AI system directly into Unreal Engine, enabling developers to leverage advanced AI capabilities without leaving the editor. The plugin uses a hybrid architecture with a lightweight C++ shell in UE and a powerful Python backend for AI processing.

## Current Status

**Phase 1: Plugin Shell (Week 1) - In Progress**

This is the foundational plugin structure. The plugin currently provides:
- ✅ Basic plugin structure and module organization
- ✅ Runtime module for core functionality
- ✅ Editor module for Unreal Editor integration
- ✅ Build system configuration (.uplugin and .Build.cs files)

**Coming Soon (Week 2-4):**
- Python bridge for subprocess management
- IPC socket communication between C++ and Python
- Basic Slate UI panel for queries
- Integration with existing RAG system

## Installation

### For Development

1. Copy the entire `Plugins/AdastreaDirector` folder into your Unreal Engine project's `Plugins` directory
2. Regenerate project files (right-click .uproject → Generate Visual Studio project files)
3. Build your project
4. Launch Unreal Engine Editor
5. The plugin will be loaded automatically

### Verifying Installation

1. Open your project in Unreal Engine Editor
2. Go to Edit → Plugins
3. Search for "Adastrea Director"
4. The plugin should appear in the "Developer Tools" category
5. Check the console log for "AdastreaDirector Module: StartupModule" messages

## Architecture

### Hybrid Approach

The plugin uses a hybrid architecture as specified in `PLUGIN_DEVELOPMENT_FEASIBILITY.md`:

```
┌─────────────────────────────────────┐
│  Unreal Engine Editor (C++)        │
│  - Slate UI                         │
│  - Python Bridge                    │
│  - Plugin Module                    │
└──────────────┬──────────────────────┘
               │ Local Socket IPC
               ▼
┌─────────────────────────────────────┐
│  Python Backend (Subprocess)        │
│  - RAG Documentation System         │
│  - Planning Agents                  │
│  - LLM Integration                  │
└─────────────────────────────────────┘
```

### Module Structure

- **AdastreaDirector** (Runtime Module)
  - Core functionality accessible at runtime
  - Python subprocess management (future)
  - IPC communication layer (future)
  
- **AdastreaDirectorEditor** (Editor Module)
  - Editor-only functionality
  - Slate UI panels and widgets (future)
  - Menu and toolbar integration (future)
  - Asset actions (future)

## File Structure

```
Plugins/AdastreaDirector/
├── AdastreaDirector.uplugin          # Plugin descriptor
├── README.md                         # This file
├── Resources/
│   └── Icon128.txt                   # Plugin icon (placeholder)
├── Source/
│   ├── AdastreaDirector/             # Runtime module
│   │   ├── AdastreaDirector.Build.cs
│   │   ├── Public/
│   │   │   └── AdastreaDirectorModule.h
│   │   └── Private/
│   │       └── AdastreaDirectorModule.cpp
│   └── AdastreaDirectorEditor/       # Editor module
│       ├── AdastreaDirectorEditor.Build.cs
│       ├── Public/
│       │   └── AdastreaDirectorEditorModule.h
│       └── Private/
│           └── AdastreaDirectorEditorModule.cpp
└── Content/
    └── UI/
        └── EditorWidgets/            # Future: UI assets
```

## Development Roadmap

### Phase 1: Plugin Shell (Weeks 1-4)

**Week 1: Project Setup** ✅ (Current)
- [x] Create plugin folder structure
- [x] Write .uplugin descriptor
- [x] Create build scripts (.Build.cs)
- [x] Set up version control
- [ ] Test plugin loads in UE

**Week 2: Python Bridge**
- [ ] Implement subprocess management
- [ ] Create IPC socket communication
- [ ] Handle Python process lifecycle
- [ ] Error handling and recovery

**Week 3: Python Backend IPC**
- [ ] Create Python IPC server
- [ ] Implement request router
- [ ] Test communication with plugin
- [ ] Performance optimization

**Week 4: Basic UI**
- [ ] Create main Slate panel
- [ ] Add to Editor menu
- [ ] Query input widget
- [ ] Results display widget

### Phase 2: RAG Integration (Weeks 5-8)
- Document ingestion UI
- Query system integration
- Settings dialog

### Phase 3: Planning Features (Weeks 9-12)
- Goal analysis UI
- Task decomposition display
- Code generation interface

### Phase 4: Polish & Release (Weeks 13-16)
- Cross-platform testing
- Documentation
- Fab marketplace submission

## Requirements

### Unreal Engine
- Unreal Engine 5.0 or higher
- Supported platforms: Windows, Mac, Linux

### Dependencies
- Python 3.9+ (for backend)
- PythonScriptPlugin (optional, enabled in .uplugin)

### Python Backend
The plugin requires the Adastrea Director Python backend to be available. See the main repository README for setup instructions:
- ChromaDB for vector storage
- LangChain for LLM orchestration
- OpenAI API (or compatible alternative)

## Configuration

### Plugin Settings (Future)

Settings will be configurable through:
- Editor Preferences → Plugins → Adastrea Director
- Project Settings → Plugins → Adastrea Director

Planned settings include:
- Python backend path
- IPC port configuration
- API keys (encrypted)
- Model selection
- Performance options

## Building the Plugin

### From Unreal Engine Editor
1. File → Generate Visual Studio Project Files
2. Build → Rebuild Solution (or Build → Build Solution)

### From Command Line (Windows)
```cmd
"C:\Program Files\Epic Games\UE_5.3\Engine\Build\BatchFiles\RunUAT.bat" BuildPlugin ^
  -Plugin="C:\Path\To\Project\Plugins\AdastreaDirector\AdastreaDirector.uplugin" ^
  -Package="C:\Output\Path"
```

### From Command Line (Mac/Linux)
```bash
/Path/To/UnrealEngine/Engine/Build/BatchFiles/RunUAT.sh BuildPlugin \
  -Plugin="/Path/To/Project/Plugins/AdastreaDirector/AdastreaDirector.uplugin" \
  -Package="/Output/Path"
```

## Testing

### Manual Testing
1. Load the plugin in UE Editor
2. Check console log for startup messages
3. Verify plugin appears in Edit → Plugins

### Automated Testing (Future)
- Unit tests for C++ components
- Integration tests for Python bridge
- UI tests for Slate panels

## Troubleshooting

### Plugin Doesn't Load
- Check the Output Log for error messages
- Verify all .uplugin and .Build.cs files are correct
- Regenerate project files
- Rebuild the project

### Build Errors
- Ensure Unreal Engine version meets requirements
- Check that all module dependencies are available
- Verify file paths are correct

### Runtime Errors
- Check that Python backend is accessible
- Verify API keys are configured (future)
- Review console logs for specific errors

## Contributing

This plugin is part of the Adastrea Director project. For contribution guidelines, see the main repository:
- [CONTRIBUTING.md](../../CONTRIBUTING.md)
- [ROADMAP.md](../../ROADMAP.md)

## Support

- **Issues**: [GitHub Issues](https://github.com/Mittenzx/Adastrea-Director/issues)
- **Documentation**: [Main README](../../README.md)
- **Feasibility Study**: [PLUGIN_DEVELOPMENT_FEASIBILITY.md](../../PLUGIN_DEVELOPMENT_FEASIBILITY.md)

## License

[To be determined]

## Credits

- **Project Lead**: Mittenzx
- **Architecture**: Based on PLUGIN_DEVELOPMENT_FEASIBILITY.md
- **Development**: GitHub Copilot Workspace

---

*"Building tomorrow's game development tools, today."*
