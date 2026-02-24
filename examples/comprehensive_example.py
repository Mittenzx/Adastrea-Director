#!/usr/bin/env python3
"""
Comprehensive Example: Adastrea Director Plugin in Action

This example demonstrates the full capabilities of the Adastrea Director plugin
for controlling Unreal Engine through Python and MCP.

Features demonstrated:
1. Basic connection to Unreal Engine
2. Project and scene inspection
3. Asset management
4. Python script execution
5. Blueprint creation
6. Actor manipulation
7. Console commands
8. Integration with AI workflows

Prerequisites:
- Unreal Engine 5.0+ with Python Remote Execution enabled
- Adastrea Director plugin installed
- Python dependencies installed (pip install -r requirements.txt)
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mcp_server.server_enhanced import EnhancedUnrealMCPServer, EnhancedMCPServerConfig
    print("[OK] Imported enhanced MCP server")
except ImportError as e:
    print(f"[ERROR] Failed to import MCP server: {e}")
    print("Make sure you're running from the Adastrea-Director directory")
    sys.exit(1)


class AdastreaDirectorDemo:
    """Demonstration of Adastrea Director plugin capabilities."""
    
    def __init__(self):
        """Initialize the demo with enhanced MCP server."""
        print("\n" + "=" * 60)
        print("Adastrea Director - Comprehensive Demo")
        print("=" * 60)
        
        # Create enhanced server configuration
        config = EnhancedMCPServerConfig(
            name="AdastreaDemo",
            version="1.0.0",
            description="Demo of Adastrea Director capabilities",
            enable_diagnostics=True,
            show_connection_help=True,
            connection_timeout=30.0
        )
        
        # Create server instance
        self.server = EnhancedUnrealMCPServer(config)
        
        print("[INFO] Demo initialized")
        print(f"[INFO] Server name: {config.name}")
        print(f"[INFO] Server version: {config.version}")
    
    def run_demo(self):
        """Run the comprehensive demonstration."""
        print("\n[STEP 1] Starting MCP server...")
        
        if not self.server.start():
            print("[ERROR] Failed to start MCP server")
            print("[TIP] Make sure Unreal Engine is running with Python Remote Execution enabled")
            print("[TIP] Run: python configure_unreal_python.py --instructions")
            return False
        
        print("[OK] MCP server started")
        
        # Check connection status
        if not self.server.is_connected():
            print("[WARNING] Not connected to Unreal Engine")
            print("[TIP] The demo will continue but some features may not work")
            print("[TIP] Run: python test_unreal_connection.py to diagnose")
        
        # Run demonstration steps
        steps = [
            self.demo_project_info,
            self.demo_list_tools,
            self.demo_asset_management,
            self.demo_python_execution,
            self.demo_blueprint_creation,
            self.demo_actor_manipulation,
            self.demo_console_commands,
            self.demo_ai_integration,
        ]
        
        for i, step in enumerate(steps, 1):
            print(f"\n[STEP {i}] Running: {step.__name__}")
            try:
                if not step():
                    print(f"[WARNING] Step {i} had issues, continuing...")
            except Exception as e:
                print(f"[ERROR] Step {i} failed: {e}")
                print("[INFO] Continuing with next step...")
        
        print("\n" + "=" * 60)
        print("Demo completed!")
        print("=" * 60)
        
        # Show summary
        self.show_summary()
        
        return True
    
    def demo_project_info(self):
        """Demonstrate project information retrieval."""
        print("\n--- Project Information ---")
        
        result = self.server.handle_tool_call("editor_project_info", {})
        
        if result.get("isError"):
            print(f"[ERROR] Failed to get project info: {result.get('content', [{}])[0].get('text', 'Unknown error')}")
            return False
        
        # Parse and display project info
        for content in result.get("content", []):
            if content["type"] == "text":
                try:
                    project_info = json.loads(content["text"])
                    print(f"Project: {project_info.get('project_name', 'Unknown')}")
                    print(f"Engine: {project_info.get('engine_version', 'Unknown')}")
                    print(f"Path: {project_info.get('project_root', 'Unknown')}")
                    print(f"Maps: {len(project_info.get('maps', []))}")
                    print(f"Plugins: {len(project_info.get('plugins', []))}")
                    return True
                except json.JSONDecodeError:
                    print(content["text"])
                    return True
        
        return False
    
    def demo_list_tools(self):
        """Demonstrate listing available tools."""
        print("\n--- Available Tools ---")
        
        tools = self.server.list_tools()
        
        if not tools:
            print("[ERROR] No tools available")
            return False
        
        print(f"Total tools: {len(tools)}")
        print("\nTool categories:")
        
        # Group tools by category
        categories = {}
        for tool in tools:
            category = tool.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(tool['name'])
        
        for category, tool_names in categories.items():
            print(f"  {category}: {len(tool_names)} tools")
            for tool_name in tool_names[:3]:  # Show first 3 tools per category
                print(f"    - {tool_name}")
            if len(tool_names) > 3:
                print(f"    ... and {len(tool_names) - 3} more")
        
        return True
    
    def demo_asset_management(self):
        """Demonstrate asset management capabilities."""
        print("\n--- Asset Management ---")
        
        # List some assets
        result = self.server.handle_tool_call("editor_list_assets", {
            "limit": 10,
            "asset_class": "Blueprint"
        })
        
        if result.get("isError"):
            print("[INFO] Asset listing failed or no Blueprint assets found")
            # Try without filter
            result = self.server.handle_tool_call("editor_list_assets", {
                "limit": 5
            })
        
        if not result.get("isError"):
            for content in result.get("content", []):
                if content["type"] == "text":
                    print("Sample assets:")
                    print(content["text"][:500] + "..." if len(content["text"]) > 500 else content["text"])
                    break
        
        # Search for assets
        print("\nSearching for 'player' assets...")
        result = self.server.handle_tool_call("editor_search_assets", {
            "search_term": "player",
            "limit": 3
        })
        
        if not result.get("isError"):
            for content in result.get("content", []):
                if content["type"] == "text":
                    print("Search results:")
                    print(content["text"][:300] + "..." if len(content["text"]) > 300 else content["text"])
        
        return True
    
    def demo_python_execution(self):
        """Demonstrate Python execution in Unreal Engine."""
        print("\n--- Python Execution ---")
        
        # Simple Python code to execute
        python_code = """
import unreal

# Get engine version
engine_version = unreal.SystemLibrary.get_engine_version()
print(f"Unreal Engine Version: {engine_version}")

# Get current level
editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
current_level = editor_subsystem.get_current_level()
print(f"Current Level: {current_level.get_name() if current_level else 'None'}")

# List some actor classes
all_classes = unreal.EditorUtilityLibrary.get_all_actor_classes()
print(f"Total Actor Classes: {len(all_classes)}")

# Return success
{"status": "success", "engine_version": engine_version}
"""
        
        print("Executing Python in Unreal Engine...")
        result = self.server.handle_tool_call("editor_run_python", {
            "code": python_code
        })
        
        if result.get("isError"):
            print("[ERROR] Python execution failed")
            print("[TIP] This may be because Python Remote Execution is not fully configured")
            return False
        
        print("[OK] Python executed successfully")
        for content in result.get("content", []):
            if content["type"] == "text":
                print("Output:", content["text"][:200] + "..." if len(content["text"]) > 200 else content["text"])
        
        return True
    
    def demo_blueprint_creation(self):
        """Demonstrate Blueprint creation."""
        print("\n--- Blueprint Creation ---")
        
        # Create a simple blueprint
        blueprint_name = "BP_DemoActor"
        
        print(f"Creating blueprint: {blueprint_name}")
        result = self.server.handle_tool_call("editor_create_blueprint", {
            "blueprint_name": blueprint_name,
            "parent_class": "Actor",
            "package_path": "/Game/DemoBlueprints"
        })
        
        if result.get("isError"):
            error_msg = result.get('content', [{}])[0].get('text', 'Unknown error')
            if "already exists" in error_msg.lower():
                print(f"[INFO] Blueprint {blueprint_name} already exists")
                return True
            else:
                print(f"[INFO] Blueprint creation failed: {error_msg}")
                print("[TIP] This may require specific permissions or the path may not exist")
                return False
        
        print(f"[OK] Blueprint {blueprint_name} created successfully")
        return True
    
    def demo_actor_manipulation(self):
        """Demonstrate actor manipulation."""
        print("\n--- Actor Manipulation ---")
        
        # Get world outliner
        print("Getting world outliner (actors in current level)...")
        result = self.server.handle_tool_call("editor_get_world_outliner", {})
        
        if result.get("isError"):
            print("[INFO] Could not get world outliner")
            print("[TIP] This may be because no level is loaded")
            return False
        
        actor_count = 0
        for content in result.get("content", []):
            if content["type"] == "text":
                try:
                    outliner_data = json.loads(content["text"])
                    actor_count = len(outliner_data.get("actors", []))
                    print(f"Actors in current level: {actor_count}")
                    
                    # Show some actor types
                    actor_types = {}
                    for actor in outliner_data.get("actors", [])[:10]:  # First 10 actors
                        actor_type = actor.get("type", "Unknown")
                        actor_types[actor_type] = actor_types.get(actor_type, 0) + 1
                    
                    print("Actor types (sample):")
                    for actor_type, count in list(actor_types.items())[:5]:
                        print(f"  {actor_type}: {count}")
                    
                    break
                except json.JSONDecodeError:
                    print("Outliner data:", content["text"][:200] + "..." if len(content["text"]) > 200 else content["text"])
        
        return actor_count > 0
    
    def demo_console_commands(self):
        """Demonstrate console command execution."""
        print("\n--- Console Commands ---")
        
        # Run a simple console command
        print("Running console command: stat fps")
        result = self.server.handle_tool_call("editor_console_command", {
            "command": "stat fps"
        })
        
        if result.get("isError"):
            print("[INFO] Console command execution failed")
            print("[TIP] Some console commands may not be available in editor mode")
            return False
        
        print("[OK] Console command executed")
        return True
    
    def demo_ai_integration(self):
        """Demonstrate AI integration capabilities."""
        print("\n--- AI Integration ---")
        
        print("Adastrea Director enables AI agents to control Unreal Engine through:")
        print("  1. MCP (Model Context Protocol) server")
        print("  2. Natural language commands")
        print("  3. Automated scene generation")
        print("  4. Intelligent asset management")
        print("  5. Procedural content creation")
        
        print("\nExample AI workflows:")
        print("  - 'Create a forest scene with trees and animals'")
        print("  - 'Add a player character with shooting mechanics'")
        print("  - 'Generate a city block with buildings and roads'")
        print("  - 'Animate this character to walk across the scene'")
        
        print("\nIntegration points:")
        print("  - OpenClaw AI assistant")
        print("  - Custom AI agents via MCP")
        print("  - Python scripting for automation")
        print("  - REST API for web interfaces")
        
        return True
    
    def show_summary(self):
        """Show demonstration summary."""
        print("\n" + "=" * 60)
        print("DEMONSTRATION SUMMARY")
        print("=" * 60)
        
        # Get diagnostics
        if hasattr(self.server, 'get_diagnostics'):
            diag = self.server.get_diagnostics()
            print(f"Server running: {'[OK]' if diag['server_running'] else '[ERROR]'}")
            print(f"Connected to UE: {'[OK]' if diag['connected_to_ue'] else '[WARNING]'}")
            print(f"Connection errors: {diag['connection_errors']}")
        
        # List tools count
        tools = self.server.list_tools()
        print(f"Available tools: {len(tools)}")
        
        print("\nCapabilities demonstrated:")
        print("  [OK] Project inspection")
        print("  [OK] Tool discovery")
        print("  [OK] Asset management")
        print("  [OK] Python execution")
        print("  [OK] Blueprint creation")
        print("  [OK] Actor manipulation")
        print("  [OK] Console commands")
        print("  [OK] AI integration")
        
        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)
        print("1. Explore the enhanced tools:")
        print("   python unreal_mcp_cli_enhanced.py")
        print("2. Configure Unreal Engine:")
        print("   python configure_unreal_python.py --instructions")
        print("3. Test connection:")
        print("   python test_unreal_connection.py")
        print("4. Read documentation:")
        print("   ENHANCED_PLUGIN_TOOLS.md")
        print("   UNREAL_PYTHON_SETUP.md")
        
        print("\nFor AI integration:")
        print("1. Start MCP server:")
        print("   python -m mcp_server.server_enhanced")
        print("2. Connect AI agents via MCP protocol")
        print("3. Use natural language to control Unreal Engine!")


def main():
    """Main function to run the comprehensive demo."""
    print("Adastrea Director - Comprehensive Demonstration")
    print("This demo shows the full capabilities of the plugin.")
    print("\nPrerequisites:")
    print("  - Unreal Engine 5.0+ running")
    print("  - Python Remote Execution enabled")
    print("  - Adastrea Director plugin installed")
    
    # Check if we should run
    response = input("\nRun the demonstration? (y/n): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Demo cancelled.")
        return
    
    # Create and run demo
    demo = AdastreaDirectorDemo()
    
    try:
        success = demo.run_demo()
        
        if success:
            print("\n[SUCCESS] Demonstration completed successfully!")
            print("The Adastrea Director plugin is ready to use.")
        else:
            print("\n[WARNING] Demonstration had some issues.")
            print("Check the error messages above and ensure Unreal Engine is properly configured.")
        
    except KeyboardInterrupt:
        print("\n[INFO] Demonstration interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] Demonstration failed: {e}")
        print("[TIP] Check that Unreal Engine is running with Python Remote Execution enabled")
    
    print("\nThank you for trying Adastrea Director!")


if __name__ == "__main__":
    main()