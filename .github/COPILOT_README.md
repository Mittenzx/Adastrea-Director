# GitHub Copilot Integration with Adastrea Director

Welcome! This directory contains documentation for GitHub Copilot agents and AI assistants working with the Adastrea Director plugin.

## 📚 Documentation Overview

### For Copilot Agents & AI Assistants

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **[COPILOT_INSTRUCTIONS.md](../COPILOT_INSTRUCTIONS.md)** | Comprehensive guide (1,750+ lines) | When you need detailed information about any aspect of the system |
| **[COPILOT_QUICK_REFERENCE.md](COPILOT_QUICK_REFERENCE.md)** | Quick reference card (290 lines) | When you need a quick lookup for common operations |

### What's Covered

Both documents cover:

✅ **All Connection Methods** (5 different ways to connect)
- MCP Server (recommended for Copilot)
- HTTP Remote Control API
- WebSocket Event Client
- Python IPC Server
- UE Python API

✅ **What You Can Do**
- Query documentation and project context
- Execute Python code in Unreal Engine
- Control actors and properties
- Search and manage assets
- Generate development plans
- Monitor real-time events
- Take screenshots and control viewport

✅ **How to Verify Operations**
- 8 different verification methods
- Connection health checks
- Property change verification
- Actor creation confirmation
- Command execution results

✅ **Example Workflows**
- 5 complete end-to-end workflows
- From simple queries to complex automation
- Real code examples with verification

✅ **Troubleshooting**
- Common issues and solutions
- Diagnostic procedures
- Step-by-step fixes

## 🚀 Quick Start

### 1. Add MCP Server to VS Code

Edit `.vscode/settings.json`:

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

### 2. Verify Prerequisites

- ✅ Unreal Engine Editor is running
- ✅ Python Editor Script Plugin enabled
- ✅ Remote Execution enabled in Project Settings

### 3. Test Connection

In Copilot Chat:
```
"Get project information from Unreal Engine"
```

If successful, you're ready to go! 🎉

## 📖 Choosing the Right Document

### Use COPILOT_INSTRUCTIONS.md when:
- You need detailed explanations
- Setting up for the first time
- Troubleshooting issues
- Learning about all capabilities
- Building complex workflows

### Use COPILOT_QUICK_REFERENCE.md when:
- You need a quick command reference
- Looking up common operations
- Checking connection ports
- Finding example commands
- Quick troubleshooting

## 🔗 Related Documentation

### For Developers
- [Main README](../README.md) - Project overview
- [MCP Server Guide](../mcp_server/MCP_SERVER_GUIDE.md) - MCP server details
- [Remote Connection Types](../wiki/Remote-Connection-Types-and-Actions.md) - All connection types

### For Plugin Users
- [Plugin README](../Plugins/AdastreaDirector/README.md) - Plugin documentation
- [Plugin Setup Guide](../Plugins/AdastreaDirector/SETUP_GUIDE.md) - Installation guide

### For VS Code Users
- [VS Code Extension README](../vscode-extension/README.md) - Extension documentation
- [Phase 2 Guide](../vscode-extension/PHASE2_GUIDE.md) - Advanced features

## 💡 Tips for Effective Use

1. **Start with the Quick Reference** - Get familiar with common commands
2. **Read the Full Instructions** - Understand all capabilities
3. **Test your connection first** - Always verify prerequisites
4. **Use natural language** - MCP tools understand conversational requests
5. **Verify critical operations** - Check that changes were applied
6. **Refer to examples** - Follow the workflow patterns
7. **Check troubleshooting** - Common issues have known solutions

## 🆘 Getting Help

If you encounter issues:

1. Check the **Troubleshooting** section in either document
2. Verify your **Prerequisites** are met
3. Test **Connection Health** using the provided checks
4. Consult the [Project Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki)
5. Open an [Issue](https://github.com/Mittenzx/Adastrea-Director/issues) if needed

## 🤝 Contributing

Found an issue or have suggestions for improving the Copilot documentation?

1. Open an issue describing the problem or improvement
2. Submit a PR with your proposed changes
3. See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines

## 📝 Feedback

We want to make these instructions as helpful as possible for AI agents. If you have feedback:

- What worked well?
- What was confusing?
- What's missing?

Please let us know through GitHub Issues!

---

**Quick Links:**
- [COPILOT_INSTRUCTIONS.md](../COPILOT_INSTRUCTIONS.md) - Full guide
- [COPILOT_QUICK_REFERENCE.md](COPILOT_QUICK_REFERENCE.md) - Quick reference
- [GitHub Repository](https://github.com/Mittenzx/Adastrea-Director)
- [Project Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki)

---

**Version:** 1.0.0  
**Last Updated:** December 2024  
**Adastrea Director** - AI Game Development Assistant
