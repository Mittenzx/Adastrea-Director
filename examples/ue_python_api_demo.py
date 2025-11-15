"""
Unreal Engine Python API Demo

This example demonstrates how to use the Adastrea Director UE Python API
for direct interaction with Unreal Engine.

IMPORTANT: This script must be run from within Unreal Engine's Python
environment, not as a standalone script.

How to run in Unreal Engine:
1. Enable the Python Editor Script Plugin in UE
2. Copy this file to your project's Content/Python folder
3. In UE Editor, go to: Window > Developer Tools > Python Console
4. Run: execfile("Content/Python/ue_python_api_demo.py")

Or use the Adastrea Director plugin which automatically loads this.
"""

import sys
import os

# Add plugin Python directory to path
plugin_python_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'Plugins', 'AdastreaDirector', 'Python'
)
if os.path.exists(plugin_python_dir):
    sys.path.insert(0, plugin_python_dir)

try:
    from ue_python_api import (
        UEPythonBridge,
        is_running_in_ue,
        get_bridge,
        LogLevel
    )
except ImportError as e:
    print(f"Error: Failed to import UE Python API: {e}")
    print("Make sure the Adastrea Director plugin is installed")
    sys.exit(1)


def demo_basic_info():
    """Demo: Get basic Unreal Engine information."""
    print("\n" + "="*60)
    print("Demo 1: Basic Engine Information")
    print("="*60)
    
    bridge = get_bridge()
    if not bridge:
        print("✗ Failed to create UE Python bridge")
        return
    
    print(f"Engine Version: {bridge.get_engine_version()}")
    print(f"Project Directory: {bridge.get_project_directory()}")
    print(f"Current Level: {bridge.get_current_level_name()}")


def demo_console_commands():
    """Demo: Execute console commands."""
    print("\n" + "="*60)
    print("Demo 2: Console Commands")
    print("="*60)
    
    bridge = get_bridge()
    if not bridge:
        print("✗ Failed to create UE Python bridge")
        return
    
    commands = [
        "stat fps",
        "stat unit",
        "stat game",
    ]
    
    for cmd in commands:
        print(f"Executing: {cmd}")
        success = bridge.execute_console_command(cmd)
        if success:
            print(f"  ✓ Command executed successfully")
        else:
            print(f"  ✗ Command failed")


def demo_asset_operations():
    """Demo: Asset operations."""
    print("\n" + "="*60)
    print("Demo 3: Asset Operations")
    print("="*60)
    
    bridge = get_bridge()
    if not bridge:
        print("✗ Failed to create UE Python bridge")
        return
    
    # Get selected assets
    print("\nSelected Assets:")
    selected_assets = bridge.get_selected_assets()
    if selected_assets:
        for asset in selected_assets:
            print(f"  - {asset.asset_name} ({asset.asset_class})")
            print(f"    Path: {asset.asset_path}")
    else:
        print("  No assets selected")
    
    # Find materials
    print("\nSearching for Materials in /Game...")
    materials = bridge.find_assets_by_class("Material", "/Game")
    print(f"Found {len(materials)} materials")
    if materials:
        print("First 5 materials:")
        for material in materials[:5]:
            print(f"  - {material.asset_name}")
    
    # Find static meshes
    print("\nSearching for Static Meshes in /Game...")
    meshes = bridge.find_assets_by_class("StaticMesh", "/Game")
    print(f"Found {len(meshes)} static meshes")
    if meshes:
        print("First 5 meshes:")
        for mesh in meshes[:5]:
            print(f"  - {mesh.asset_name}")


def demo_actor_operations():
    """Demo: Actor operations."""
    print("\n" + "="*60)
    print("Demo 4: Actor Operations")
    print("="*60)
    
    bridge = get_bridge()
    if not bridge:
        print("✗ Failed to create UE Python bridge")
        return
    
    # Get selected actors
    print("\nSelected Actors:")
    selected_actors = bridge.get_selected_actors()
    if selected_actors:
        for actor in selected_actors:
            print(f"  - {actor.actor_name} ({actor.actor_class})")
            print(f"    Location: {actor.location}")
            print(f"    Rotation: {actor.rotation}")
            print(f"    Scale: {actor.scale}")
    else:
        print("  No actors selected")
    
    # Get all static mesh actors
    print("\nAll Static Mesh Actors in level:")
    mesh_actors = bridge.get_all_actors_of_class("StaticMeshActor")
    print(f"Found {len(mesh_actors)} static mesh actors")
    if mesh_actors:
        print("First 3 actors:")
        for actor in mesh_actors[:3]:
            print(f"  - {actor.actor_name}")
            print(f"    Location: {actor.location}")
    
    # Get all lights
    print("\nAll Lights in level:")
    lights = bridge.get_all_actors_of_class("Light")
    print(f"Found {len(lights)} lights")


def demo_spawn_actor():
    """Demo: Spawn a new actor."""
    print("\n" + "="*60)
    print("Demo 5: Spawn Actor")
    print("="*60)
    
    bridge = get_bridge()
    if not bridge:
        print("✗ Failed to create UE Python bridge")
        return
    
    print("\nSpawning a test actor...")
    actor = bridge.spawn_actor(
        "StaticMeshActor",
        location=(100.0, 200.0, 50.0),
        rotation=(0.0, 0.0, 0.0),
        actor_name="AdastreaTest_Actor"
    )
    
    if actor:
        print(f"✓ Successfully spawned: {actor.get_name()}")
        print(f"  Location: (100.0, 200.0, 50.0)")
        
        # Show notification
        bridge.show_notification(
            "Test actor spawned successfully!",
            duration=3.0,
            severity="Success"
        )
    else:
        print("✗ Failed to spawn actor")


def demo_logging():
    """Demo: Logging to UE output log."""
    print("\n" + "="*60)
    print("Demo 6: Logging")
    print("="*60)
    
    bridge = get_bridge()
    if not bridge:
        print("✗ Failed to create UE Python bridge")
        return
    
    print("\nWriting messages to UE output log...")
    bridge.log_message("This is a regular log message", LogLevel.LOG)
    bridge.log_message("This is a display message", LogLevel.DISPLAY)
    bridge.log_message("This is a warning message", LogLevel.WARNING)
    bridge.log_message("This is an error message", LogLevel.ERROR)
    
    print("✓ Check the Output Log in UE Editor for these messages")


def demo_notifications():
    """Demo: Show notifications in UE editor."""
    print("\n" + "="*60)
    print("Demo 7: Editor Notifications")
    print("="*60)
    
    bridge = get_bridge()
    if not bridge:
        print("✗ Failed to create UE Python bridge")
        return
    
    print("\nShowing various notifications...")
    
    bridge.show_notification(
        "This is an info notification",
        duration=2.0,
        severity="Info"
    )
    
    import time
    time.sleep(2.5)
    
    bridge.show_notification(
        "This is a success notification",
        duration=2.0,
        severity="Success"
    )
    
    time.sleep(2.5)
    
    bridge.show_notification(
        "This is a warning notification",
        duration=2.0,
        severity="Warning"
    )
    
    print("✓ Notifications shown (check UE Editor)")


def run_all_demos():
    """Run all demonstration functions."""
    print("="*60)
    print("Adastrea Director - UE Python API Demonstration")
    print("="*60)
    
    # Check if running in UE
    if not is_running_in_ue():
        print("\n✗ ERROR: Not running inside Unreal Engine!")
        print("This script must be run from UE's Python environment.")
        print("\nTo run this demo:")
        print("1. Enable Python Editor Script Plugin in UE")
        print("2. Run from UE Python Console: execfile('path/to/this/file.py')")
        return
    
    print("\n✓ Running inside Unreal Engine")
    
    # Run all demos
    try:
        demo_basic_info()
        demo_console_commands()
        demo_asset_operations()
        demo_actor_operations()
        
        # Ask before spawning/modifying
        print("\n" + "="*60)
        print("The following demos will modify your level:")
        print("  - Demo 5: Spawn Actor")
        print("  - Demo 6: Logging")
        print("  - Demo 7: Notifications")
        print("="*60)
        
        response = input("\nContinue with modification demos? (y/n): ")
        if response.lower() == 'y':
            demo_spawn_actor()
            demo_logging()
            demo_notifications()
        else:
            print("\nSkipping modification demos")
        
        print("\n" + "="*60)
        print("Demo Complete!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_demos()
