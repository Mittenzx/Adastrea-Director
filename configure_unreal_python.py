#!/usr/bin/env python3
"""
Adastrea Director - Unreal Engine Python Configuration Helper

This script helps configure Unreal Engine for Python Remote Execution,
which is required for the Adastrea Director MCP server to work.

Usage:
    python configure_unreal_python.py --check
    python configure_unreal_python.py --enable
    python configure_unreal_python.py --create-config
"""

import os
import sys
import json
import argparse
import subprocess
import platform
from pathlib import Path
from typing import Optional, Dict, Any

def get_platform() -> str:
    """Get current platform."""
    return platform.system()

def get_unreal_engine_paths() -> list:
    """Get possible Unreal Engine installation paths."""
    system = get_platform()
    paths = []
    
    if system == "Windows":
        # Common Windows installation paths
        epic_games = Path("C:/Program Files/Epic Games")
        if epic_games.exists():
            for version_dir in epic_games.iterdir():
                if version_dir.name.startswith("UE_"):
                    paths.append(version_dir)
        
        # Also check without underscore
        for version in ["5.6", "5.5", "5.4", "5.3", "5.2", "5.1", "5.0"]:
            path = epic_games / f"UE{version}"
            if path.exists():
                paths.append(path)
    
    elif system == "Darwin":  # macOS
        applications = Path("/Applications")
        epic_games = applications / "Epic Games"
        if epic_games.exists():
            for version_dir in epic_games.iterdir():
                if "Unreal Engine" in version_dir.name:
                    paths.append(version_dir)
    
    elif system == "Linux":
        home = Path.home()
        # Common Linux installation paths
        paths.extend([
            home / "UnrealEngine",
            home / "UE5",
            home / "UE4",
        ])
    
    return paths

def check_python_remote_execution() -> Dict[str, Any]:
    """
    Check if Python Remote Execution is properly configured.
    
    Returns:
        Dictionary with check results and recommendations.
    """
    print("=" * 60)
    print("Checking Unreal Engine Python Remote Execution Configuration")
    print("=" * 60)
    
    results = {
        "unreal_engine_found": False,
        "python_plugin_available": False,
        "config_files_exist": False,
        "remote_execution_enabled": False,
        "recommendations": []
    }
    
    # Check if Unreal Engine is installed
    unreal_paths = get_unreal_engine_paths()
    if unreal_paths:
        results["unreal_engine_found"] = True
        print(f"✅ Found Unreal Engine at: {unreal_paths[0]}")
    else:
        results["recommendations"].append("Install Unreal Engine 5.6 or later")
        print("❌ Unreal Engine not found in standard locations")
    
    # Check for Python plugin
    for unreal_path in unreal_paths:
        python_plugin_path = unreal_path / "Engine" / "Plugins" / "Experimental" / "PythonScriptPlugin"
        if python_plugin_path.exists():
            results["python_plugin_available"] = True
            print("✅ Python Editor Script Plugin is available")
            break
    else:
        results["recommendations"].append("Install Python Editor Script Plugin via Epic Games Launcher")
        print("❌ Python Editor Script Plugin not found")
    
    # Check for common config files
    config_locations = []
    if system == "Windows":
        config_locations.append(Path(os.environ.get("LOCALAPPDATA", "")) / "UnrealEngine" / "Common")
        config_locations.append(Path.home() / "AppData" / "Local" / "UnrealEngine" / "Common")
    
    for config_loc in config_locations:
        if config_loc.exists():
            results["config_files_exist"] = True
            print(f"✅ Found Unreal Engine config directory: {config_loc}")
            break
    
    print("\n" + "=" * 60)
    print("Configuration Status:")
    print("=" * 60)
    
    status_items = [
        ("Unreal Engine installed", results["unreal_engine_found"]),
        ("Python plugin available", results["python_plugin_available"]),
        ("Config directory exists", results["config_files_exist"]),
    ]
    
    for item, status in status_items:
        symbol = "✅" if status else "❌"
        print(f"{symbol} {item}")
    
    if results["recommendations"]:
        print("\n" + "=" * 60)
        print("Recommendations:")
        print("=" * 60)
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"{i}. {rec}")
    
    return results

def create_python_config() -> bool:
    """
    Create a Python configuration file for Unreal Engine.
    
    Returns:
        True if successful, False otherwise.
    """
    print("\n" + "=" * 60)
    print("Creating Python Configuration for Unreal Engine")
    print("=" * 60)
    
    # Create a sample DefaultEngine.ini configuration
    config_content = """[/Script/PythonScriptPlugin.PythonScriptPluginSettings]
+bindings=(commandlet_class="/Script/UnrealEd.PythonCommandlet")
+bindings=(commandlet_class="/Script/UnrealEd.AutomationTestCommandlet")
+bindings=(commandlet_class="/Script/UnrealEd.AutomationResavePackagesCommandlet")
+bindings=(commandlet_class="/Script/UnrealEd.AutomationFileSystemCommandlet")
+bindings=(commandlet_class="/Script/UnrealEd.AutomationAssetCheckCommandlet")
+bindings=(commandlet_class="/Script/UnrealEd.AutomationPerformaceCommandlet")
+bindings=(commandlet_class="/Script/UnrealEd.AutomationScreenshotCommandlet")
+bindings=(commandlet_class="/Script/UnrealEd.AutomationTestCommandlet")
+bindings=(commandlet_class="/Script/UnrealEd.AutomationResavePackagesCommandlet")
+bindings=(commandlet_class="/Script/UnrealEd.AutomationFileSystemCommandlet")
+bindings=(commandlet_class="/Script/UnrealEd.AutomationAssetCheckCommandlet")
+bindings=(commandlet_class="/Script/UnrealEd.AutomationPerformaceCommandlet")
+bindings=(commandlet_class="/Script/UnrealEd.AutomationScreenshotCommandlet")

[/Script/PythonScriptPlugin.PythonScriptPluginUserSettings]
bDeveloperMode=True
bEnableRemoteExecution=True
RemoteExecutionBindAddress="0.0.0.0"
RemoteExecutionPort=6766
RemoteExecutionCommandEndpoint="127.0.0.1:6776"
bShowPythonLoadErrors=True
bAllowUnverifiedPythonPackages=True

[/Script/UnrealEd.EditorEngine]
+ActivePythonInterpreters=(InterpreterType=Internal, bAutoInitialize=True)
+ActivePythonInterpreters=(InterpreterType=External, bAutoInitialize=True)
"""
    
    # Determine where to save the config
    config_path = None
    system = get_platform()
    
    if system == "Windows":
        config_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "UnrealEngine" / "Common"
        if not config_dir.exists():
            config_dir = Path.home() / "AppData" / "Local" / "UnrealEngine" / "Common"
            config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "DefaultEngine.ini"
    
    elif system == "Darwin":  # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "Epic" / "Unreal Engine"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "DefaultEngine.ini"
    
    elif system == "Linux":
        config_dir = Path.home() / ".config" / "Epic" / "Unreal Engine"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "DefaultEngine.ini"
    
    if config_path:
        try:
            # Check if file already exists
            if config_path.exists():
                print(f"⚠️  Config file already exists: {config_path}")
                print("   Backing up existing file...")
                backup_path = config_path.with_suffix(".ini.backup")
                config_path.rename(backup_path)
                print(f"   Backup created: {backup_path}")
            
            # Write new config
            config_path.write_text(config_content, encoding="utf-8")
            print(f"✅ Created Python configuration at: {config_path}")
            print("\nConfiguration includes:")
            print("  • Python Remote Execution enabled")
            print("  • Bind address: 0.0.0.0 (all interfaces)")
            print("  • Multicast port: 6766")
            print("  • Command endpoint: 127.0.0.1:6776")
            print("  • Developer mode enabled")
            return True
            
        except Exception as e:
            print(f"❌ Error creating config file: {e}")
            return False
    else:
        print("❌ Could not determine config directory for your platform")
        return False

def generate_setup_instructions() -> None:
    """Generate setup instructions for Python Remote Execution."""
    print("\n" + "=" * 60)
    print("Unreal Engine Python Remote Execution Setup Instructions")
    print("=" * 60)
    
    instructions = """
MANUAL SETUP (Recommended):

1. Launch Unreal Engine Editor
2. Enable Python Plugin:
   • Go to Edit → Plugins
   • Search for "Python"
   • Enable "Python Editor Script Plugin"
   • Restart the editor if prompted

3. Enable Remote Execution:
   • Go to Edit → Project Settings
   • Search for "Python"
   • Check "Enable Remote Execution"
   • Set "Multicast Bind Address" to "0.0.0.0"
   • Set "Multicast Endpoint Port" to 6766
   • Set "Remote Execution Command Endpoint" to "127.0.0.1:6776"

4. Verify Configuration:
   • Run: python test_unreal_connection.py
   • Should show: [SUCCESS] Connected to Unreal Engine

AUTOMATIC SETUP:

1. Run this script with --create-config flag
2. Launch Unreal Engine Editor
3. The settings should be automatically applied

TROUBLESHOOTING:

If connection fails:
1. Ensure Unreal Editor is running
2. Check firewall settings for ports 6766 and 6776
3. Verify Python plugin is enabled
4. Try restarting Unreal Editor

For Adastrea Director MCP Server:
1. After enabling Python Remote Execution
2. Run: python unreal_mcp_cli.py
3. Should connect and show interactive prompt
"""
    
    print(instructions)
    
    # Also create a markdown file with instructions
    md_content = """# Unreal Engine Python Remote Execution Setup

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
python unreal_mcp_cli.py
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
"""
    
    try:
        with open("UNREAL_PYTHON_SETUP.md", "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"✅ Created documentation: UNREAL_PYTHON_SETUP.md")
    except Exception as e:
        print(f"⚠️  Could not create documentation file: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Configure Unreal Engine for Python Remote Execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python configure_unreal_python.py --check
  python configure_unreal_python.py --create-config
  python configure_unreal_python.py --instructions
        """
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check current Python Remote Execution configuration"
    )
    
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create Python configuration file for Unreal Engine"
    )
    
    parser.add_argument(
        "--instructions",
        action="store_true",
        help="Generate setup instructions"
    )
    
    args = parser.parse_args()
    
    if not any([args.check, args.create_config, args.instructions]):
        parser.print_help()
        return
    
    if args.check:
        check_python_remote_execution()
    
    if args.create_config:
        if create_python_config():
            print("\n✅ Configuration created successfully!")
            print("   Launch Unreal Engine Editor to apply the settings.")
        else:
            print("\n❌ Failed to create configuration.")
            print("   Please use manual setup instructions.")
    
    if args.instructions:
        generate_setup_instructions()
    
    print("\n" + "=" * 60)
    print("Next steps for Adastrea Director:")
    print("=" * 60)
    print("1. Enable Python Remote Execution in Unreal Engine")
    print("2. Test connection: python test_unreal_connection.py")
    print("3. Run MCP server: python unreal_mcp_cli.py")
    print("4. Use Adastrea Director tools to control Unreal Engine!")

if __name__ == "__main__":
    main()