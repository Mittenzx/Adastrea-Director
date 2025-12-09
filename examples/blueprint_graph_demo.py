#!/usr/bin/env python3
"""
Blueprint Graph Manipulation Demo (Experimental)

This example demonstrates the experimental blueprint graph manipulation
capabilities in Adastrea Director. Note that full graph manipulation
requires C++ plugin extensions - this demo shows the API structure.

Usage:
    python examples/blueprint_graph_demo.py
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


def demo_experimental_graph_operations():
    """Demonstrate experimental graph operations."""
    print_section("Blueprint Graph Operations (Experimental)")
    
    print("⚠️  IMPORTANT: Blueprint graph manipulation is experimental")
    print("Full implementation requires C++ plugin extensions.\n")
    print("This demo shows the API structure and approach.\n")
    
    # Example code structure
    example_code = '''
from ue_python_api import UEPythonBridge

bridge = UEPythonBridge()

# Step 1: Create a blueprint
blueprint = bridge.create_blueprint(
    "BP_GraphExample",
    "Actor",
    "/Game/Examples"
)

# Step 2: Add nodes to the graph
begin_play = bridge.add_blueprint_node(
    "/Game/Examples/BP_GraphExample",
    "BeginPlay",
    position_x=100.0,
    position_y=100.0
)

print_node = bridge.add_blueprint_node(
    "/Game/Examples/BP_GraphExample",
    "Print",
    position_x=400.0,
    position_y=100.0
)

# Step 3: Connect the nodes
bridge.connect_blueprint_nodes(
    "/Game/Examples/BP_GraphExample",
    begin_play,
    "execute",
    print_node,
    "execute"
)

# Step 4: Add a variable
bridge.add_blueprint_variable(
    "/Game/Examples/BP_GraphExample",
    "Message",
    "String",
    default_value="Hello from Blueprint!",
    is_exposed=True
)

# Step 5: Compile the blueprint
bridge.compile_blueprint("/Game/Examples/BP_GraphExample")
'''
    
    print("Example API Usage:")
    print(example_code)


def demo_python_script_generation():
    """Demonstrate Python script generation approach."""
    print_section("Alternative: Python Script Generation")
    
    print("A more practical approach is to generate Python scripts")
    print("that run inside Unreal Engine's Python environment.\n")
    
    script_example = '''
def generate_blueprint_setup_script(blueprint_path, variables):
    """Generate a Python script to setup a blueprint."""
    script = f"""
import unreal

# Load the blueprint
blueprint = unreal.load_asset('{blueprint_path}')
if blueprint:
    print(f'Loaded blueprint: {blueprint_path}')
    
    # Variables would be added here
    # (requires blueprint-specific API access)
    
    # Save the blueprint
    unreal.EditorAssetLibrary.save_asset('{blueprint_path}')
    print('Blueprint saved successfully')
else:
    print(f'Failed to load blueprint: {blueprint_path}')
"""
    return script

# Generate script
script = generate_blueprint_setup_script(
    "/Game/Examples/BP_MyActor",
    ["Health", "Speed"]
)

# Execute via MCP
with UnrealMCPServer() as server:
    result = server.handle_tool_call("editor_run_python", {"code": script})
'''
    
    print("Script Generation Approach:")
    print(script_example)


def demo_template_based_approach():
    """Demonstrate template-based blueprint creation."""
    print_section("Alternative: Template-Based Blueprints")
    
    print("The most practical current approach: use blueprint templates\n")
    
    template_example = '''
# Step 1: Create template blueprints in UE with common patterns
# - BP_ActorTemplate (basic actor with common setup)
# - BP_CharacterTemplate (character with movement)
# - BP_InteractableTemplate (object with interaction logic)

# Step 2: Copy and customize programmatically
from ue_python_api import UEPythonBridge

bridge = UEPythonBridge()

# Copy template (would use unreal.EditorAssetLibrary.duplicate_asset)
source_path = "/Game/Templates/BP_ActorTemplate"
dest_path = "/Game/Actors/BP_MyCustomActor"

# Then modify exposed variables
# Variables are accessible without graph manipulation
'''
    
    print("Template-Based Approach:")
    print(template_example)
    print("\nAdvantages:")
    print("✅ Works with current Python API")
    print("✅ No C++ extension needed")
    print("✅ Easy to maintain templates")
    print("✅ Designer-friendly")


def demo_available_operations():
    """Show what operations are currently possible."""
    print_section("Currently Available Operations")
    
    operations = [
        ("✅ Create Blueprint Assets", "Fully implemented"),
        ("✅ Load Blueprint Assets", "Fully implemented"),
        ("✅ Save Blueprint Assets", "Fully implemented"),
        ("⚠️  Add Variables", "API defined, needs implementation"),
        ("⚠️  Add Nodes", "API defined, needs C++ extension"),
        ("⚠️  Connect Nodes", "API defined, needs C++ extension"),
        ("⚠️  Compile Blueprints", "Basic save implemented"),
        ("❌ Add Functions", "Not yet implemented"),
        ("❌ Add Events", "Not yet implemented"),
        ("❌ Modify Graph Layout", "Not yet implemented"),
    ]
    
    for operation, status in operations:
        print(f"{operation:<30} {status}")
    
    print("\nLegend:")
    print("  ✅ = Fully working")
    print("  ⚠️  = Experimental/Limited")
    print("  ❌ = Not yet implemented")


def demo_cpp_extension_approach():
    """Show the C++ plugin extension approach."""
    print_section("Future: C++ Plugin Extension")
    
    print("For full graph control, a C++ plugin extension is needed:\n")
    
    cpp_example = '''
// C++ Module: AdastreaGraphEditor

class UAdastreaGraphLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
    
    UFUNCTION(BlueprintCallable, Category = "Adastrea|Blueprint")
    static UK2Node_Event* AddEventNode(
        UBlueprint* Blueprint,
        FName EventName,
        FVector2D Position
    );
    
    UFUNCTION(BlueprintCallable, Category = "Adastrea|Blueprint")
    static UK2Node_CallFunction* AddFunctionNode(
        UBlueprint* Blueprint,
        UFunction* Function,
        FVector2D Position
    );
    
    UFUNCTION(BlueprintCallable, Category = "Adastrea|Blueprint")
    static bool ConnectNodes(
        UEdGraphPin* SourcePin,
        UEdGraphPin* TargetPin
    );
};
'''
    
    print("C++ Extension Example:")
    print(cpp_example)
    print("\nThis would then be accessible from Python:")
    print("  import unreal")
    print("  unreal.AdastreaGraphLibrary.add_event_node(...)")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("  Blueprint Graph Manipulation Demo (Experimental)")
    print("=" * 60)
    
    print("\nThis demo explores blueprint graph manipulation capabilities.")
    print("Currently, these features are in experimental/planning stage.\n")
    
    try:
        demo_available_operations()
        
        input("\nPress Enter to see experimental API structure...")
        demo_experimental_graph_operations()
        
        input("\nPress Enter to see script generation approach...")
        demo_python_script_generation()
        
        input("\nPress Enter to see template-based approach...")
        demo_template_based_approach()
        
        input("\nPress Enter to see C++ extension approach...")
        demo_cpp_extension_approach()
        
        print_section("Summary")
        print("Blueprint graph manipulation is possible but complex.\n")
        print("Current recommendations:")
        print("1. ✅ Use template-based approach for immediate needs")
        print("2. ⚠️  Use Python script generation for variable setup")
        print("3. 🚀 Develop C++ extension for full control\n")
        print("See BLUEPRINT_GRAPHS_IMPLEMENTATION.md for detailed plan.")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
