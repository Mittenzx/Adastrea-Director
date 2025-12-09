# GitHub Copilot Quick Reference for Adastrea Director

Quick reference guide for GitHub Copilot agents working with Adastrea Director from VS Code.

📖 **For comprehensive documentation, see:** [COPILOT_INSTRUCTIONS.md](../COPILOT_INSTRUCTIONS.md)

## 🚀 Quick Setup

### 1. Add MCP Server to VS Code Settings

Create/edit `.vscode/settings.json` in your workspace:

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

Replace `/path/to/Adastrea-Director` with your actual installation path.

### 2. Verify Prerequisites

Ensure these are enabled in Unreal Engine:
- ✅ **Python Editor Script Plugin** (Edit → Plugins)
- ✅ **Remote Execution** (Edit → Project Settings → Python)
- ✅ **Unreal Engine Editor is running**

### 3. Test Connection

In Copilot Chat, try:
```
"Get project information from Unreal Engine"
```

If you receive project details, you're connected! 🎉

---

## 📝 Common Commands

Use these natural language prompts in Copilot Chat:

### Project Information
```
"Get project information from Unreal Engine"
"What version of Unreal Engine is running?"
"Get information about the current map"
```

### Asset Operations
```
"List all assets in the project"
"Search for assets containing 'player'"
"Get information about asset '/Game/Characters/Hero'"
```

### Actor Management
```
"List all actors in the current level"
"Create a StaticMeshActor at position (0, 0, 100)"
"Delete the actor named 'TestCube'"
"Move the actor 'PlayerStart' to (100, 200, 50)"
```

### Python Execution
```
"Execute this Python code in Unreal Engine: import unreal; print(unreal.SystemLibrary.get_engine_version())"
"Run Python code to spawn a particle effect"
```

### Console Commands
```
"Execute console command 'stat fps'"
"Run the console command 'stat unit'"
```

### Viewport Control
```
"Take a screenshot of the viewport"
"Move the viewport camera to position (1000, 0, 500)"
```

---

## 🔌 Available Connection Methods

| Method | Port | Best For | Latency |
|--------|------|----------|---------|
| **MCP Server** | 6766 | Copilot integration | < 1ms |
| **HTTP Remote Control** | 30010 | Property/function calls | 10-50ms |
| **WebSocket Events** | 30010 | Real-time monitoring | 1-5ms |
| **Python IPC** | 5555 | RAG queries, planning | < 1ms |
| **UE Python API** | N/A | Direct editor automation | < 0.1ms |

**Recommendation:** Use MCP Server for Copilot - it's pre-configured and optimized for AI agents.

---

## 🛠️ Available MCP Tools

The MCP server provides these tools (automatically used by Copilot):

### Editor Tools
1. **editor_run_python** - Execute Python code in Unreal Editor
2. **editor_console_command** - Run console commands
3. **editor_project_info** - Get project information
4. **editor_get_map_info** - Get current map details

### Asset Tools
5. **editor_list_assets** - List all project assets
6. **editor_search_assets** - Search for specific assets
7. **editor_get_asset_info** - Get detailed asset information

### World Tools
8. **editor_get_world_outliner** - List all actors in world
9. **editor_create_object** - Create new actors
10. **editor_update_object** - Modify actor properties
11. **editor_delete_object** - Remove actors

### Viewport Tools
12. **editor_take_screenshot** - Capture viewport screenshot
13. **editor_move_camera** - Position viewport camera

---

## 🔍 How to Verify Operations

### Check if UE is Connected
```
"Is Unreal Engine connected?"
"Get project information"
```

### Verify Actor Creation
```
"List all actors in the world"
"Does an actor named 'TestCube' exist?"
```

### Verify Property Changes
```
# Ask Copilot to run this in UE:
"Execute Python code to check player health:
import unreal
player = unreal.GameplayStatics.get_player_character(
    unreal.EditorLevelLibrary.get_editor_world(), 0
)
print(player.get_editor_property('Health'))"
```

### Verify Asset Operations
```
"Search for assets containing 'character'"
"How many SkeletalMesh assets are in the project?"
```

---

## 💡 Example Workflows

### Create and Configure Actor

```
1. "Create a StaticMeshActor named 'HealthPickup' at (100, 200, 50)"
2. "List all actors to verify 'HealthPickup' exists"
3. "Execute Python to set its scale:
   import unreal
   actors = unreal.EditorLevelLibrary.get_all_level_actors()
   for actor in actors:
       if actor.get_actor_label() == 'HealthPickup':
           actor.set_actor_scale3d(unreal.Vector(2, 2, 2))
           print('Scale updated')"
4. "Take a screenshot to verify the changes"
```

### Query Documentation and Execute

```
1. "How do I spawn a particle effect in Unreal Engine?"
   (Uses IPC RAG system automatically)
2. "Execute the following Python code in Unreal to spawn particles:
   [generated code from step 1]"
3. "Verify the particle system exists in the world"
```

### Monitor and React

```
1. "List all actors with 'Player' in the name"
2. "Get the current location of the PlayerStart actor"
3. "Take a screenshot showing the player start location"
```

---

## 🚨 Troubleshooting

### "Not connected to Unreal Engine"

**Check:**
1. Is Unreal Engine Editor running?
2. Is Python Editor Script Plugin enabled?
3. Is Remote Execution enabled in Project Settings?

**Fix:**
```
1. Edit → Plugins → Enable "Python Editor Script Plugin"
2. Edit → Project Settings → Python → Enable "Remote Execution"
3. Restart Unreal Engine
```

### "Connection refused" on port 5555

**Fix:**
```bash
# Start IPC server manually
cd /path/to/Adastrea-Director/Plugins/AdastreaDirector/Python
python ipc_server.py --port 5555
```

### HTTP API not responding (port 30010)

**Fix:**
1. Enable in Project Settings:
   - Edit → Project Settings → Plugins → Remote Control API
   - Check "Enable Remote Control API"

2. Or launch UE with flags:
   ```bash
   UnrealEditor.exe <Project> -RCWebControlEnable -RCWebInterfaceEnable
   ```

### MCP tools not available

**Fix:**
1. Verify MCP server is configured in VS Code settings
2. Restart VS Code after adding MCP configuration
3. Check the path in settings points to your Adastrea installation

---

## 📚 Additional Resources

### Documentation Files
- **[COPILOT_INSTRUCTIONS.md](../COPILOT_INSTRUCTIONS.md)** - Complete guide for Copilot agents
- **[mcp_server/MCP_SERVER_GUIDE.md](../mcp_server/MCP_SERVER_GUIDE.md)** - MCP server documentation
- **[wiki/Remote-Connection-Types-and-Actions.md](../wiki/Remote-Connection-Types-and-Actions.md)** - All connection types
- **[README.md](../README.md)** - Main project documentation

### VS Code Extension
- **[vscode-extension/README.md](../vscode-extension/README.md)** - VS Code extension guide
- **[vscode-extension/PHASE2_GUIDE.md](../vscode-extension/PHASE2_GUIDE.md)** - Advanced features

### Unreal Plugin
- **[Plugins/AdastreaDirector/README.md](../Plugins/AdastreaDirector/README.md)** - Plugin documentation
- **[Plugins/AdastreaDirector/SETUP_GUIDE.md](../Plugins/AdastreaDirector/SETUP_GUIDE.md)** - Plugin setup

---

## 🎯 Best Practices for Copilot Agents

1. **Always verify connections first** before attempting operations
2. **Use natural language** - MCP tools are designed for conversational requests
3. **Verify critical operations** by checking results
4. **Check multiple sources** - combine MCP tools for comprehensive verification
5. **Handle errors gracefully** - ask for connection status if operations fail
6. **Use context from RAG** - query documentation before attempting complex tasks
7. **Take screenshots** to visually verify changes
8. **Log operations** for audit trail and debugging

---

## 🔗 Quick Links

- [GitHub Repository](https://github.com/Mittenzx/Adastrea-Director)
- [Project Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki)
- [Issue Tracker](https://github.com/Mittenzx/Adastrea-Director/issues)

---

**Version:** 1.0.0  
**Last Updated:** December 2025  
**For comprehensive documentation, see:** [COPILOT_INSTRUCTIONS.md](../COPILOT_INSTRUCTIONS.md)
