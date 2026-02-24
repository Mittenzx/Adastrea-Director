# Unreal Engine Python Remote Execution Installation Guide

## Quick Installation

### Option 1: Automatic Configuration
```bash
python configure_unreal_python.py --create-config
```

### Option 2: Manual Configuration

#### Step 1: Enable Python Plugin
1. Launch Unreal Engine Editor
2. Go to **Edit → Plugins**
3. Search for "Python"
4. Enable **"Python Editor Script Plugin"**
5. Restart the editor if prompted

#### Step 2: Enable Remote Execution
1. Go to **Edit → Project Settings**
2. Search for "Python"
3. Check **"Enable Remote Execution"**
4. Set **"Multicast Bind Address"** to `0.0.0.0`
5. Set **"Multicast Endpoint Port"** to `6766`
6. Set **"Remote Execution Command Endpoint"** to `127.0.0.1:6776`

## Verification

### Test Connection
```bash
python test_unreal_connection.py
```

Expected output:
```
[SUCCESS] Connected to Unreal Engine
```

### Test MCP Server
```bash
python unreal_mcp_cli_enhanced.py
```

## Troubleshooting

### Connection Failed
1. **Check if Unreal Editor is running** (not just the project file)
2. **Verify Python plugin is enabled** (Edit → Plugins)
3. **Check firewall settings** for ports 6766 and 6776
4. **Restart Unreal Editor** after configuration changes

### Plugin Not Found
1. Install via Epic Games Launcher → Unreal Engine → Library → Engine Versions
2. Click the dropdown arrow next to your engine version
3. Select "Options" → "Python Editor Script Plugin"

### Port Conflicts
If ports 6766 or 6776 are already in use:
1. Change ports in Project Settings → Python
2. Update MCP server configuration accordingly

## Advanced Configuration

### Configuration File Location
- **Windows**: `%LOCALAPPDATA%\UnrealEngine\Common\DefaultEngine.ini`
- **macOS**: `~/Library/Application Support/Epic/Unreal Engine/DefaultEngine.ini`
- **Linux**: `~/.config/Epic/Unreal Engine/DefaultEngine.ini`

### Sample Configuration
```ini
[/Script/PythonScriptPlugin.PythonScriptPluginUserSettings]
bEnableRemoteExecution=True
RemoteExecutionBindAddress="0.0.0.0"
RemoteExecutionPort=6766
RemoteExecutionCommandEndpoint="127.0.0.1:6776"
```

## Support
- Run diagnostic: `python configure_unreal_python.py --check`
- Get instructions: `python configure_unreal_python.py --instructions`
- Check repository: `python verify_repository.py`
- Test connection: `python test_unreal_connection.py`

## For Adastrea Director Users

### After Successful Setup
```bash
# Test the enhanced CLI
python unreal_mcp_cli_enhanced.py

# Start the enhanced MCP server
python -m mcp_server.server_enhanced

# Use the original tools (backward compatible)
python unreal_mcp_cli.py
```

### Common Commands
```bash
# Get project information
python unreal_mcp_cli_enhanced.py project-info

# List all assets
python unreal_mcp_cli_enhanced.py list-assets

# Execute Python in Unreal Engine
python unreal_mcp_cli_enhanced.py run-python "import unreal; print(unreal.SystemLibrary.get_engine_version())"
```

## Next Steps

1. **Verify Setup**: Run `python test_unreal_connection.py`
2. **Test Tools**: Run `python unreal_mcp_cli_enhanced.py --diagnostics`
3. **Explore Features**: Use the interactive CLI: `python unreal_mcp_cli_enhanced.py`
4. **Integrate with AI**: Use the MCP server with AI agents

## Need Help?

1. Check the enhanced tools documentation: `ENHANCED_PLUGIN_TOOLS.md`
2. Review the work session summary: `WORK_SESSION_SUMMARY_2026-02-24.md`
3. Use the diagnostic tools included in the repository
4. Check the repository structure: `python verify_repository.py`

---

*Last Updated: 2026-02-24*  
*Part of the Adastrea Director Enhanced Plugin Tools*