# VS Code Configuration for Adastrea Director

This directory contains VS Code configuration to enable GitHub Copilot to use Adastrea Director's MCP (Model Context Protocol) server.

## GitHub Copilot Integration

The `settings.json` file configures GitHub Copilot to connect to the Adastrea Director MCP server, allowing Copilot to:

- Execute Python code directly in Unreal Engine Editor
- Query project information and assets
- Create and manipulate actors in the level
- Access Director's RAG (Retrieval-Augmented Generation) system for context-aware Unreal Engine assistance based on ingested documentation

### Prerequisites

Before using this integration:

1. **Install GitHub Copilot** in VS Code
2. **Start Unreal Engine** with the Python Editor Script Plugin enabled
3. **Enable Remote Execution** in Project Settings → Python
4. **Install Adastrea Director dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

Once configured, you can use Copilot Chat with the Adastrea Director tools:

```
Ask Copilot: "Use the adastrea-unreal server to get project information"
Ask Copilot: "List all assets in the current Unreal project"
Ask Copilot: "Execute Python code to spawn an actor at location (0,0,100)"
```

### Configuration

The `settings.json` file uses `${workspaceFolder}` which VS Code automatically resolves to the workspace root directory. If you need to use a different path, you can modify the `cwd` field.

**Example for different path:**
```json
{
  "github.copilot.chat.experimental.mcpServers": {
    "adastrea-unreal": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/your/custom/path/to/Adastrea-Director"
    }
  }
}
```

### Troubleshooting

If Copilot cannot connect to the MCP server:

1. **Check Python is available**: Run `python --version` in terminal
2. **Verify dependencies**: Run `pip list | grep mcp`
3. **Check Unreal Engine is running**: The editor must be running with Python enabled
4. **View MCP logs**: Check the VS Code Output panel for "MCP" logs
5. **Test MCP server manually**:
   ```bash
   cd /path/to/Adastrea-Director
   python -m mcp_server.server
   ```
   Or use the interactive CLI:
   ```bash
   python unreal_mcp_cli.py
   ```

### Documentation

For complete documentation, see:

- [MCP Server Guide](../mcp_server/MCP_SERVER_GUIDE.md) - Complete MCP server documentation
- [Copilot Instructions](../Documentation/development/COPILOT_INSTRUCTIONS.md) - Full guide for Copilot agents
- [Copilot Quick Reference](../.github/COPILOT_QUICK_REFERENCE.md) - Quick reference for common operations

### Related Files

- `settings.json` - Active configuration (tracked in git)
- `settings.json.example` - Example configuration template
