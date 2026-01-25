# Changelog

All notable changes to the Adastrea Director project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Plugin UI Enhancements (Phase 2):**
  - Collapsible sections using SExpandableArea for better space management
  - Toast notification system using FSlateNotificationManager
  - Agent Performance Monitoring dashboard with 4 metric cards (FPS, Memory, CPU, GPU)
  - Enhanced visual hierarchy with emoji icons throughout
  - Modern header styling with dark border background
  - Color-coded metric cards for quick visual recognition
  - PLUGIN_UI_UPGRADES.md documentation for all UI improvements
- **VibeUE Architecture Migration Features:**
  - Feature flag system for gradual VibeUE rollout (UseBuiltInPython, UseDirectLLM, UseRuntimeDiscovery, EnableMCPServer)
  - Comprehensive testing framework with 20 unit tests for VibeUE components
  - VIBEUE_MIGRATION_GUIDE.md for step-by-step migration instructions
  - VIBEUE_TESTING_FRAMEWORK.md documenting all test coverage
  - AdastreaDirectorTests module for automated testing
  - 6 tests for AdastreaScriptService (Python execution)
  - 7 tests for AdastreaAssetService (Asset discovery)
  - 7 tests for AdastreaToolSystem (Tool registration and execution)
- Professional 128x128 plugin icon with AI/Director theme
- Comprehensive CHANGELOG.md for version tracking
- Updated Unreal Engine compatibility range to 4.27–5.6 with explicit EngineVersion specification (UE5.7 no longer supported)
- **Phase 3 Complete:** Three fully functional autonomous agents (Performance, Bug Detection, Code Quality)
- Agent Orchestrator CLI and Real-time Dashboard for agent management
- 120+ comprehensive tests for Phase 3 agents and infrastructure

### Changed
- **Plugin UI Improvements:**
  - Dashboard sections now use expandable/collapsible design
  - All section headers enhanced with emoji icons (🔌 🎮 💾 🖥️ 🎨 📊 📝)
  - Tab buttons enhanced with larger fonts and emoji icons (💬 📊 🧪)
  - Action buttons now use emoji icons for better recognition (🔄 ⚙️ 🗑️ 💾)
  - Header title increased from 16pt to 18pt for better prominence
  - Settings button uses flat button style for consistency
  - User actions now trigger toast notifications for immediate feedback
- **VibeUE Architecture Updates:**
  - Updated manual testing checklist in VIBEUE_ARCHITECTURE_SUMMARY.md (all items now checked)
  - Migration status updated to show Phase 1 complete, Phase 2 in progress
  - Next Steps section reorganized into Completed/In Progress/Pending
  - AdastreaSettings now includes feature flags for VibeUE migration control
- Adjusted supported Unreal Engine versions to 4.27–5.6 (dropped UE5.7 from previously supported range)
- Removed deprecated EditorStyle module dependency
- Plugin now explicitly targets UE5.6.0 in .uplugin file to align with the new 4.27–5.6 support range (excluding UE5.7)
- **Updated documentation to reflect Phase 3 completion status**

## [1.0.0] - 2025-12-16

### Added

#### Core System (P1-P2)
- RAG-based document understanding and Q&A system
- Context-aware documentation search across project guides
- Intelligent planning and task decomposition for development goals
- Goal analysis and classification system
- Task decomposition with dependency management
- Code generation with multiple implementation approaches
- Interactive planning CLI interface
- Effort estimation and priority assignment
- Plan export in Markdown, JSON, or Text formats

#### Autonomous Agent System (P3)
- Agent Orchestrator CLI for managing autonomous agents
- Real-time Dashboard UI for monitoring agent activity
- Remote Control API integration (67 tests)
- Event bus implementation (16 tests)
- Shared state management (20 tests)
- MCP Server integration for AI agent access (84 tests)
- Performance profiling capabilities
- Automated bug detection and crash analysis
- Code quality monitoring framework

#### Unreal Engine Plugin
- Basic plugin structure with Runtime and Editor modules
- Python subprocess management (`FPythonProcessManager`)
- IPC socket communication (`FIPCClient`)
- High-level bridge interface (`FPythonBridge`)
- Main Slate panel (`SAdastreaDirectorPanel`)
- Tabbed interface with Query, Ingestion, and Dashboard tabs
- Settings dialog with API key management
- Real-time system health monitoring with 6 status indicators
- Direct UE Python API access (`import unreal`)
- Comprehensive API wrapper (`ue_python_api.py`)
- Asset operations (query, load, save)
- Actor operations (spawn, query, delete)
- Console command execution
- Content generation utilities
- Content validation framework
- Batch processing for mass operations
- UE log capture and analysis

#### GUI Application
- Modern dark theme with professional appearance
- Comprehensive settings dialog
- Secure API key management for multiple providers
- Knowledge base update functionality
- Ingest list tab with visual checklist
- Unreal MCP tab for direct UE integration
- Conversation history with timestamps
- Keyboard shortcuts for fast workflow
- Copy and export functionality
- Adjustable font sizes for accessibility
- Full menu bar with File, Edit, and Help menus
- Automatic UE log capture to dated log files

#### Documentation
- Comprehensive Wiki with all detailed documentation
- Platform-specific installation guides
- Usage guides for all features (P1-P3)
- Architecture documentation
- API reference documentation
- Testing guides and checklists
- Troubleshooting guides
- GitHub Copilot integration guides

#### Testing & Quality
- 230+ comprehensive tests (100% passing)
- 27 GUI tests with 88% coverage
- Unit, integration, and UI test categories
- Production-ready stability
- Comprehensive test suite for all major components

### Changed
- Documentation migrated to Wiki for better organization
- Improved error handling with user-friendly messages
- Enhanced UI with color-coded status indicators
- Optimized request routing (< 1ms latency)

### Technical Details
- Python 3.9+ support (Python 3.12+ recommended)
- HuggingFace embeddings (no API key required, works offline)
- Support for Gemini and OpenAI LLM providers
- Cross-platform support (Windows, Mac, Linux)
- Hybrid architecture (External Python + UE Python)

### Known Issues
- Plugin is in beta version
- Some P3 features still in development
- Planning agent integration pending for plugin

## Release Notes

### Version 1.0.0 - Production Ready

Adastrea Director 1.0.0 marks the completion of Phase 2 (The Planner) and includes the foundation for Phase 3 (Autonomous Agents). The system provides:

- **7/10 Current Value**: Production-ready RAG and planning capabilities with 230+ passing tests
- **10/10 Future Potential**: Autonomous performance profiling, bug detection, and AI-assisted content generation
- **ROI**: 300%+ return in 6 months (P1-P3 complete with autonomous agents), scaling to 400%+ with full UE plugin integration (P4)

The plugin integrates seamlessly with Unreal Engine 4.27-5.6, providing developers with powerful AI assistance without leaving the editor.

### System Requirements

- **Python**: 3.9 or higher (3.12+ recommended)
- **Unreal Engine**: 4.27 - 5.6 (for plugin)
- **Operating Systems**: Windows, macOS, Linux
- **Optional**: GitHub Personal Access Token for repository ingestion

### Breaking Changes

None - Initial 1.0.0 release

---

[Unreleased]: https://github.com/Mittenzx/Adastrea-Director/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Mittenzx/Adastrea-Director/releases/tag/v1.0.0
