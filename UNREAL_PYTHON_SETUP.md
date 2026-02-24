# Unreal Engine Python Remote Execution Setup

## Prerequisites
- Unreal Engine 5.0 or later
- Python Editor Script Plugin (install via Epic Games Launcher)

## Manual Setup

### 1. Enable Python Plugin
1. Launch Unreal Engine Editor
2. Go to **Edit → Plugins**
3. Search for "Python"
4. Enable **"Python Editor Script Plugin"**
5. Restart the editor if prompted

### 2. Enable Remote Execution
1. Go to **Edit → Project Settings**
2. Search for "Python"
3. Check **"Enable Remote Execution"**
4. Set **"Multicast Bind Address"** to `0.0.0.0`
5. Set **"Multicast Endpoint Port"** to `6766`
6. Set **"Remote Execution Command Endpoint"** to `127.0.0.1:6776`

### 3. Verify Connection
```bash
python test_unreal_connection.py
```
Should show: `[SUCCESS] Connected to Unreal Engine`

## Automatic Setup
Run the configuration script:
```bash
python configure_unreal_python.py --create-config
```

## For Adastrea Director MCP Server
After enabling Python Remote Execution:
```bash
python unreal_mcp_cli_enhanced.py
```

## Troubleshooting

### Connection Failed
1. **Ensure Unreal Editor is running**
2. **Check firewall settings** for ports 6766 and 6776
3. **Verify Python plugin is enabled** (Edit → Plugins)
4. **Try restarting Unreal Editor**

### Plugin Not Found
1. Install Python Editor Script Plugin via Epic Games Launcher
2. Under "Engine" plugins, not "Project" plugins

### Port Already in Use
1. Check if another application is using port 6766 or 6776
2. Change ports in Project Settings → Python

## Testing
Use the included test script:
```bash
python test_unreal_connection.py
```

This will diagnose:
- Multicast discovery (239.0.0.1:6766)
- Direct command connection (127.0.0.1:6776)
- Python Remote Execution configuration

## Enhanced Tools

The Adastrea Director repository now includes enhanced tools to make setup easier:

### Configuration Helper
```bash
# Check current configuration
python configure_unreal_python.py --check

# Get setup instructions
python configure_unreal_python.py --instructions

# Create automatic configuration
python configure_unreal_python.py --create-config
```

### Enhanced CLI
```bash
# Interactive mode with better error messages
python unreal_mcp_cli_enhanced.py

# Show diagnostics
python unreal_mcp_cli_enhanced.py --diagnostics

# Get setup help
python unreal_mcp_cli_enhanced.py --setup-help
```

### Enhanced MCP Server
```bash
# Start enhanced server
python -m mcp_server.server_enhanced

# Check configuration
python -m mcp_server.server_enhanced --check
```

## Quick Start Workflow

1. **Check Requirements**:
   ```bash
   python verify_repository.py
   python configure_unreal_python.py --check
   ```

2. **Setup Unreal Engine**:
   ```bash
   python configure_unreal_python.py --create-config
   # Then launch Unreal Engine Editor
   ```

3. **Verify Connection**:
   ```bash
   python test_unreal_connection.py
   ```

4. **Use Adastrea Director**:
   ```bash
   python unreal_mcp_cli_enhanced.py
   ```

## Common Issues & Solutions

### Issue: "Not connected to Unreal Engine"
**Solution**:
1. Ensure Unreal Editor is running (not just the project file)
2. Verify Python plugin is enabled
3. Check firewall settings
4. Run: `python test_unreal_connection.py`

### Issue: Python commands timeout
**Solution**:
1. Check if Unreal Engine is responding
2. Verify the connection is still active
3. Try restarting Unreal Editor
4. Check for blocking operations in Unreal Engine

### Issue: MCP server won't start
**Solution**:
1. Check if port 6766 is available
2. Verify Python dependencies are installed
3. Run with debug mode: `python -m mcp_server.server_enhanced --debug`

## Support Resources

1. **Enhanced Tools Documentation**: `ENHANCED_PLUGIN_TOOLS.md`
2. **Installation Guide**: `UNREAL_PYTHON_INSTALLATION_GUIDE.md`
3. **Work Session Summary**: `WORK_SESSION_SUMMARY_2026-02-24.md`
4. **Quick Start Guide**: `QUICK_START_GUIDE.md`
5. **Repository Verification**: `python verify_repository.py`

## Next Steps After Setup

Once Python Remote Execution is working:

1. **Explore the enhanced CLI**: `python unreal_mcp_cli_enhanced.py`
2. **Test basic commands**: Get project info, list assets, run Python code
3. **Start the MCP server**: `python -m mcp_server.server_enhanced`
4. **Integrate with AI agents**: Use the MCP protocol with AI tools
5. **Explore the plugin features**: Check the plugin documentation

## Notes

- The enhanced tools are backward compatible with the original tools
- Automatic configuration may require Unreal Editor restart
- Firewall settings are often the cause of connection issues
- The configuration helper creates backup files before modifying configurations

---

*Last Updated: 2026-02-24*  
*Created as part of the Adastrea Director plugin enhancement project*