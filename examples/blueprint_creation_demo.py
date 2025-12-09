#!/usr/bin/env python3
"""
Blueprint Creation Demo

This example demonstrates how to create Blueprints in Unreal Engine
using the Adastrea Director MCP tools.

Usage:
    python examples/blueprint_creation_demo.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server import UnrealMCPServer
import json


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def demo_basic_blueprint_creation():
    """Demonstrate basic blueprint creation."""
    print_section("Demo 1: Create Basic Actor Blueprint")
    
    with UnrealMCPServer() as server:
        if not server.is_connected():
            print("⚠️  Not connected to Unreal Engine.")
            print("Make sure Unreal Editor is running with Python Remote Execution enabled.")
            return
        
        print("✅ Connected to Unreal Engine")
        
        # Create a basic Actor blueprint
        print("\n📝 Creating BP_DemoActor...")
        result = server.handle_tool_call("editor_create_blueprint", {
            "blueprint_name": "BP_DemoActor",
            "parent_class": "Actor",
            "package_path": "/Game/Blueprints/Demo"
        })
        
        if not result.get("isError"):
            print("✅ Blueprint created successfully!")
            print(result["content"][0]["text"])
        else:
            print("❌ Failed to create blueprint:")
            print(result["content"][0]["text"])


def demo_character_blueprint():
    """Demonstrate creating a Character blueprint."""
    print_section("Demo 2: Create Character Blueprint")
    
    with UnrealMCPServer() as server:
        if not server.is_connected():
            print("⚠️  Not connected to Unreal Engine.")
            return
        
        print("✅ Connected to Unreal Engine")
        
        # Create a Character blueprint
        print("\n📝 Creating BP_DemoCharacter...")
        result = server.handle_tool_call("editor_create_blueprint", {
            "blueprint_name": "BP_DemoCharacter",
            "parent_class": "Character",
            "package_path": "/Game/Characters"
        })
        
        if not result.get("isError"):
            print("✅ Character blueprint created successfully!")
            print(result["content"][0]["text"])
        else:
            print("❌ Failed to create blueprint:")
            print(result["content"][0]["text"])


def demo_multiple_blueprints():
    """Demonstrate creating multiple blueprints in one go."""
    print_section("Demo 3: Create Multiple Blueprints")
    
    blueprints = [
        {"name": "BP_GameMode", "parent": "GameModeBase", "path": "/Game/Core"},
        {"name": "BP_PlayerController", "parent": "PlayerController", "path": "/Game/Core"},
        {"name": "BP_Pickup", "parent": "Actor", "path": "/Game/Items"},
    ]
    
    with UnrealMCPServer() as server:
        if not server.is_connected():
            print("⚠️  Not connected to Unreal Engine.")
            return
        
        print("✅ Connected to Unreal Engine")
        
        for bp in blueprints:
            print(f"\n📝 Creating {bp['name']}...")
            result = server.handle_tool_call("editor_create_blueprint", {
                "blueprint_name": bp["name"],
                "parent_class": bp["parent"],
                "package_path": bp["path"]
            })
            
            if not result.get("isError"):
                print(f"✅ {bp['name']} created successfully!")
            else:
                print(f"❌ Failed to create {bp['name']}")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("  Adastrea Director - Blueprint Creation Demo")
    print("=" * 60)
    
    print("\nThis demo shows how to create Blueprints in Unreal Engine")
    print("using the Adastrea Director MCP tools.\n")
    
    print("Prerequisites:")
    print("  - Unreal Engine Editor must be running")
    print("  - Python Plugin must be enabled")
    print("  - Remote Execution must be enabled in Project Settings")
    
    input("\nPress Enter to start the demo...")
    
    try:
        demo_basic_blueprint_creation()
        
        input("\nPress Enter to continue to next demo...")
        demo_character_blueprint()
        
        input("\nPress Enter to continue to next demo...")
        demo_multiple_blueprints()
        
        print_section("Demo Complete!")
        print("All blueprints have been created in your Unreal Engine project.")
        print("You can now open them in the Blueprint Editor to add logic.")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
