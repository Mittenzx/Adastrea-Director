# Adastrea Director MCP Server Guide

This guide explains how to set up and use the Adastrea Director MCP (Model Context Protocol) server to enable AI agents and tools to interact with Unreal Engine.

## Overview

The Adastrea Director MCP Server provides a bridge between AI assistants and Unreal Engine, allowing natural language commands to be translated into actions within the Unreal Editor. This is similar to the [runreal/unreal-mcp](https://github.com/runreal/unreal-mcp) project, but integrated with Adastrea Director's Python infrastructure.

### Key Features

- **Direct Python Execution**: Execute Python code directly in the Unreal Editor
- **Asset Management**: List, search, and get information about assets
- **Level Editing**: Create, update, and delete actors in the world
- **Project Information**: Get detailed project and map information
- **Screenshots**: Capture editor viewport screenshots
- **Camera Control**: Position the viewport camera

## Supported MCP Clients

The Adastrea MCP Server works with many MCP-compatible clients. Here are options that **don't require VS Code**:

### Desktop Applications

| Client | Platform | Description |
|--------|----------|-------------|
| **[5ire](https://github.com/5ire-tech/5ire)** | Windows, Mac, Linux | Cross-platform AI assistant with full MCP support |
| **[Cline](https://github.com/cline/cline)** | Windows, Mac, Linux | Open-source desktop client, multi-server support |
| **[Cherry Studio](https://github.com/anthropics/anthropic-tools)** | Windows, Mac | Desktop chat application with MCP |

### Code Editors (Non-VS Code)

| Client | Type | Description |
|--------|------|-------------|
| **[Zed](https://zed.dev)** | Native Editor | High-performance editor with built-in MCP |
| **[JetBrains + Continue](https://continue.dev)** | Plugin | Works with IntelliJ, PyCharm, WebStorm, etc. |

### Web-Based

| Client | Type | Description |
|--------|------|-------------|
| **[LibreChat](https://github.com/danny-avila/LibreChat)** | Self-hosted Web | Web-based chat with MCP tool support |
| **[AIaW](https://github.com/anthropics/anthropic-tools)** | Web App | Lightweight web client |

### Standalone / Programmatic

You can also use the MCP server **directly from Python** without any external client - see [Standalone Usage](#standalone-usage-recommended) below.

## Prerequisites

### Unreal Engine Setup

1. **Enable Python Plugin**:
   - Open your Unreal Engine project
   - Go to `Edit` → `Plugins`
   - Search for "Python Editor Script Plugin" and enable it
   - Restart the editor if prompted

2. **Enable Remote Execution**:
   - Go to `Edit` → `Project Settings`
   - Search for "Python"
   - Check "Enable Remote Execution"

### Python Setup

Ensure you have the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Installation

### Interactive CLI (Easiest - No External Client Needed)

The easiest way to use the MCP tools is with the built-in CLI:

```bash
cd /path/to/Adastrea-Director

# Interactive mode
python unreal_mcp_cli.py

# Or run specific commands directly
python unreal_mcp_cli.py project-info
python unreal_mcp_cli.py list-assets
python unreal_mcp_cli.py search-assets "character"
python unreal_mcp_cli.py run-python "import unreal; print(unreal.SystemLibrary.get_engine_version())"
python unreal_mcp_cli.py console "stat fps"
```

**Interactive mode commands:**
```
unreal> help              # Show available commands
unreal> project           # Get project info
unreal> map               # Get current map info
unreal> assets            # List project assets
unreal> search player     # Search for assets
unreal> outliner          # Get all actors in world
unreal> python <code>     # Execute Python in Unreal
unreal> console stat fps  # Run console command
unreal> quit              # Exit
```

### Programmatic Usage (Best for Integration)

For integrating into your own tools or scripts:

```python
from mcp_server import UnrealMCPServer

# Create and start server
with UnrealMCPServer() as server:
    if server.is_connected():
        # List available tools
        tools = server.list_tools()
        print(f"Available tools: {len(tools)}")
        
        # Call a tool directly
        result = server.handle_tool_call("editor_project_info", {})
        print(result)
        
        # Execute Python in Unreal
        result = server.handle_tool_call("editor_run_python", {
            "code": "import unreal; print(unreal.SystemLibrary.get_engine_version())"
        })
        print(result)
        
        # List all assets
        result = server.handle_tool_call("editor_list_assets", {})
        print(result)
```

### MCP Server Mode (For External Clients)

If you want to use an external MCP client, run the server in MCP mode:

```bash
python -m mcp_server.server
```

With debug logging:

```bash
python -m mcp_server.server --debug
```

### Using with 5ire (Desktop App)

[5ire](https://github.com/5ire-tech/5ire) is a cross-platform desktop AI assistant.

1. **Download 5ire** for your platform (Windows, Mac, or Linux).

2. **Open Settings** → **MCP Servers**

3. **Add server configuration**:

```json
{
  "adastrea-unreal": {
    "command": "python",
    "args": ["-m", "mcp_server.server"],
    "cwd": "/path/to/Adastrea-Director"
  }
}
```

### Using with Cline (Desktop App)

[Cline](https://github.com/cline/cline) is an open-source desktop MCP client.

1. **Install Cline** from the releases page.

2. **Add the server** in Cline's settings:

```json
{
  "mcpServers": {
    "adastrea-unreal": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/Adastrea-Director"
    }
  }
}
```

### Using with Zed Editor

[Zed](https://zed.dev) is a high-performance code editor with built-in MCP support.

1. **Open Zed settings** (`~/.config/zed/settings.json`):

```json
{
  "language_models": {
    "mcp_servers": {
      "adastrea-unreal": {
        "command": "python",
        "args": ["-m", "mcp_server.server"],
        "cwd": "/path/to/Adastrea-Director"
      }
    }
  }
}
```

### Using with JetBrains IDEs (via Continue)

If you use IntelliJ, PyCharm, WebStorm, or other JetBrains IDEs:

1. **Install Continue plugin** from the JetBrains marketplace.

2. **Edit Continue config** (`~/.continue/config.json`):

```json
{
  "mcpServers": {
    "adastrea-unreal": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/Adastrea-Director"
    }
  }
}
```

### Using with LibreChat (Self-Hosted Web)

[LibreChat](https://github.com/danny-avila/LibreChat) is a self-hosted web chat interface.

1. **Deploy LibreChat** following their installation guide.

2. **Configure MCP** in the LibreChat settings to point to the Adastrea MCP server.

## Available Tools

### `editor_run_python`

Execute arbitrary Python code within the Unreal Editor.

**Parameters:**
- `code` (string, required): Python code to execute

**Example:**
```python
import unreal
print(unreal.SystemLibrary.get_engine_version())
```

### `editor_list_assets`

List all assets in the project.

**Parameters:** None

**Returns:** List of asset paths

### `editor_get_asset_info`

Get detailed information about a specific asset.

**Parameters:**
- `asset_path` (string, required): Path to the asset (e.g., '/Game/Meshes/SM_Cube')

**Returns:** Asset metadata including class, path, and LOD information for meshes

### `editor_search_assets`

Search for assets by name or path.

**Parameters:**
- `search_term` (string, required): Search term
- `asset_class` (string, optional): Filter by asset class

**Returns:** List of matching assets (max 50)

### `editor_console_command`

Execute a console command in Unreal Engine.

**Parameters:**
- `command` (string, required): Console command (e.g., 'stat fps')

### `editor_project_info`

Get detailed information about the current project.

**Parameters:** None

**Returns:** Project name, directory, engine version, asset counts

### `editor_get_map_info`

Get information about the current map/level.

**Parameters:** None

**Returns:** Map name, actor counts, actor types

### `editor_get_world_outliner`

Get all actors in the current world with their properties.

**Parameters:** None

**Returns:** List of actors with location, rotation, scale

### `editor_create_object`

Create a new actor in the world.

**Parameters:**
- `object_class` (string, required): Unreal class name (e.g., 'StaticMeshActor')
- `object_name` (string, required): Label for the actor
- `location` (object, optional): Position {x, y, z}
- `rotation` (object, optional): Rotation {pitch, yaw, roll}
- `scale` (object, optional): Scale {x, y, z}

### `editor_update_object`

Update an existing actor's properties.

**Parameters:**
- `actor_name` (string, required): Name or label of the actor
- `location` (object, optional): New position
- `rotation` (object, optional): New rotation
- `scale` (object, optional): New scale
- `new_name` (string, optional): New label

### `editor_delete_object`

Delete an actor from the world.

**Parameters:**
- `actor_name` (string, required): Name or label of the actor to delete

### `editor_take_screenshot`

Take a screenshot of the editor viewport.

**Parameters:** None

**Returns:** Path to the saved screenshot

### `editor_move_camera`

Move the viewport camera to a specific position.

**Parameters:**
- `location` (object, required): Camera position {x, y, z}
- `rotation` (object, required): Camera rotation {pitch, yaw, roll}

## Configuration

The MCP server can be configured with custom settings:

```python
from mcp_server import UnrealMCPServer, MCPServerConfig

config = MCPServerConfig(
    name="MyMCPServer",
    multicast_group="239.0.0.1",
    multicast_port=6766,
    connection_timeout=30.0,
    max_retries=3,
    retry_delay=2.0
)

server = UnrealMCPServer(config)
server.start()
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `name` | "AdastreaMCP" | Server name |
| `version` | "0.1.0" | Server version |
| `multicast_group` | "239.0.0.1" | Multicast group for discovery |
| `multicast_port` | 6766 | Multicast port |
| `connection_timeout` | 30.0 | Connection timeout in seconds |
| `max_retries` | 3 | Maximum connection retries |
| `retry_delay` | 2.0 | Delay between retries in seconds |

## Programmatic Usage

You can also use the MCP server programmatically:

```python
from mcp_server import UnrealMCPServer

# Create and start server
with UnrealMCPServer() as server:
    if server.is_connected():
        # List available tools
        tools = server.list_tools()
        print(f"Available tools: {len(tools)}")
        
        # Call a tool
        result = server.handle_tool_call(
            "editor_project_info",
            {}
        )
        print(result)
```

## Troubleshooting

### Connection Failed

**Problem:** `Not connected to Unreal Engine`

**Solutions:**
1. Ensure Unreal Engine is running
2. Verify Python Editor Script Plugin is enabled
3. Verify Remote Execution is enabled in Project Settings
4. Check if another application is using port 6766
5. Try changing the bind address:
   - In Project Settings → Python → Remote Execution
   - Change "Multicast Bind Address" to `0.0.0.0`

### Plugin Not Enabled

**Problem:** Python commands fail

**Solutions:**
1. Go to Edit → Plugins
2. Search for "Python Editor Script Plugin"
3. Enable and restart the editor

### Command Timeout

**Problem:** Commands timeout

**Solutions:**
1. Increase `connection_timeout` in config
2. Ensure Unreal Editor is responding
3. Check for blocking operations in the editor

### No Nodes Discovered

**Problem:** `No remote nodes discovered`

**Solutions:**
1. Verify Remote Execution is enabled
2. Check firewall settings for multicast traffic
3. Ensure same network interface for both applications
4. Try restarting Unreal Editor

## Architecture

```
┌─────────────────────────────────────┐
│   MCP Client                        │
│   (5ire/Cline/Zed/Continue/etc.)    │
│   - Sends tool requests             │
│   - Receives results                │
└──────────────┬──────────────────────┘
               │ stdio (JSON-RPC)
               ▼
┌─────────────────────────────────────┐
│   Adastrea MCP Server               │
│   - Parses MCP messages             │
│   - Routes to tools                 │
│   - Manages UE connection           │
└──────────────┬──────────────────────┘
               │ Python Remote Execution
               ▼
┌─────────────────────────────────────┐
│   Unreal Engine Editor              │
│   - Executes Python scripts         │
│   - Returns results                 │
└─────────────────────────────────────┘
```

## Integration with Adastrea Director

The MCP server integrates with Adastrea Director's existing infrastructure:

- **Remote Control API**: Uses the same Remote Control configuration
- **Event Bus**: Can publish events to Adastrea's event system
- **Shared State**: Access to shared state for multi-agent coordination
- **Agents**: Can work alongside autonomous agents

## Security Considerations

1. **Local Only**: By default, the server only accepts local connections
2. **No Authentication**: The MCP protocol doesn't include authentication
3. **Full Access**: Tools have full access to the Unreal Editor
4. **Review Changes**: Always review AI-suggested changes before approving

## Contributing

Contributions are welcome! To add new tools:

1. Create a new class extending `MCPTool` in `mcp_server/tools.py`
2. Define `name`, `description`, and `parameters`
3. Implement the `execute` method
4. Add to the `TOOLS` registry
5. Add tests in `tests/mcp_server/`

## Version History

### v0.1.0 (Current)
- Initial implementation
- 13 editor tools
- Python Remote Execution protocol
- stdio transport for MCP
- Support for multiple MCP clients (GitHub Copilot, Continue, Cline, 5ire, Zed, etc.)

## Finding More MCP Clients

The MCP ecosystem is growing rapidly. Here are resources to find more compatible clients:

- **[Awesome MCP Clients](https://github.com/punkpeye/awesome-mcp-clients)** - Community-maintained list of MCP clients
- **[Best MCP Clients Directory](https://www.bestmcpclients.com/)** - Feature comparisons between clients
- **[Model Context Protocol Documentation](https://modelcontextprotocol.info/docs/clients/)** - Official client documentation
- **[MCP Server List](https://mcp-server-list.com/)** - Directory of MCP servers and compatible clients

## License

See project LICENSE file.

## Credits

- Inspired by [runreal/unreal-mcp](https://github.com/runreal/unreal-mcp)
- Built for the Adastrea Director project
- Uses Unreal Engine Python Remote Execution protocol
