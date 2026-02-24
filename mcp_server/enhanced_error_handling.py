#!/usr/bin/env python3
"""
Enhanced error handling for Adastrea Director MCP Server.

This module provides better error messages and troubleshooting guidance
for Unreal Engine Python Remote Execution issues.
"""

import sys
import os
from typing import Dict, Any

def get_enhanced_connection_error() -> Dict[str, Any]:
    """
    Get enhanced error message for connection issues.
    
    Returns:
        Dictionary with detailed error information and troubleshooting steps.
    """
    error_message = """🚫 Not connected to Unreal Engine

The Adastrea Director MCP server cannot connect to Unreal Engine's Python Remote Execution.

REQUIREMENTS:
1. Unreal Engine 5.0+ must be running
2. Python Editor Script Plugin must be enabled
3. Remote Execution must be enabled in Project Settings

QUICK SETUP:
1. In Unreal Editor: Edit → Plugins → Enable "Python Editor Script Plugin"
2. Edit → Project Settings → Python → Check "Enable Remote Execution"
3. Set "Multicast Bind Address" to "0.0.0.0"
4. Restart Unreal Editor

DIAGNOSE THE ISSUE:
Run the diagnostic tool:
  python test_unreal_connection.py

Or use the configuration helper:
  python configure_unreal_python.py --check
  python configure_unreal_python.py --instructions

COMMON SOLUTIONS:
• Ensure Unreal Editor is running (not just the project file)
• Check firewall settings for ports 6766 and 6776
• Verify Python plugin is installed (via Epic Games Launcher)
• Try the automatic configuration:
  python configure_unreal_python.py --create-config

For detailed instructions, see: UNREAL_PYTHON_SETUP.md
"""
    
    return {
        "isError": True,
        "content": [{
            "type": "text",
            "text": error_message
        }]
    }

def get_tool_execution_error(tool_name: str, error: Exception) -> Dict[str, Any]:
    """
    Get enhanced error message for tool execution failures.
    
    Args:
        tool_name: Name of the tool that failed
        error: Exception that occurred
        
    Returns:
        Dictionary with error information.
    """
    error_message = f"""🔧 Tool execution failed: {tool_name}

Error: {error}

TROUBLESHOOTING:
1. Ensure Unreal Engine is still running
2. Check if the Python connection is still active
3. Verify the tool parameters are correct
4. Try reconnecting to Unreal Engine

RECONNECTION STEPS:
1. Stop the MCP server (if running)
2. Ensure Unreal Editor is running with Python Remote Execution
3. Restart the MCP server
4. Test connection: python test_unreal_connection.py
"""
    
    return {
        "isError": True,
        "content": [{
            "type": "text",
            "text": error_message
        }]
    }

def get_installation_guide() -> str:
    """
    Get installation guide for Python Remote Execution.
    
    Returns:
        Markdown-formatted installation guide.
    """
    return """# Unreal Engine Python Remote Execution Installation Guide

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
python unreal_mcp_cli.py
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
"""

def create_installation_guide_file():
    """Create installation guide markdown file."""
    guide = get_installation_guide()
    
    try:
        with open("UNREAL_PYTHON_INSTALLATION_GUIDE.md", "w", encoding="utf-8") as f:
            f.write(guide)
        print("✅ Created installation guide: UNREAL_PYTHON_INSTALLATION_GUIDE.md")
    except Exception as e:
        print(f"❌ Error creating installation guide: {e}")

if __name__ == "__main__":
    # Create installation guide when run directly
    create_installation_guide_file()
    print("\nEnhanced error handling module ready.")
    print("Import this module to get better error messages for MCP server.")