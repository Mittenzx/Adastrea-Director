# Blueprint Graphs Implementation Plan

## Overview

This document outlines the implementation approach for manipulating Blueprint graphs (visual scripting) in Unreal Engine via Adastrea Director. This is in response to the request to add graph manipulation capabilities beyond just blueprint asset creation.

## What Are Blueprint Graphs?

Blueprint graphs are the visual scripting environment in Unreal Engine where developers create game logic by:
- Adding **nodes** (events, functions, operations)
- Connecting **pins** (inputs/outputs) between nodes
- Setting **properties** and **default values**
- Creating **variables** and **functions**
- Adding **comments** and organizing the graph

## Challenges

Manipulating Blueprint graphs programmatically is significantly more complex than creating blueprint assets because:

1. **Limited Python API**: Unreal Engine's Python API has limited direct access to blueprint graph internals
2. **Graph Complexity**: Blueprint graphs involve multiple interconnected systems (nodes, pins, connections, compilation)
3. **Compilation Requirements**: Changes must be validated and compiled to work correctly
4. **Version Differences**: Graph APIs vary between UE versions
5. **No Direct Graph API**: Unlike C++, Python doesn't have full `UK2Node` access

## Implementation Strategy

### Phase 1: Foundation (Current - Experimental) ✅

Added placeholder functions to `ue_python_api.py`:

1. **`add_blueprint_node()`** - Add nodes to blueprint graphs
   - Parameters: blueprint_path, node_type, position_x, position_y
   - Node types: BeginPlay, Print, Delay, Branch, etc.
   - Currently returns placeholder (requires graph API access)

2. **`connect_blueprint_nodes()`** - Connect nodes via pins
   - Parameters: blueprint_path, source_node, source_pin, target_node, target_pin
   - Currently returns success flag (requires graph API access)

3. **`compile_blueprint()`** - Compile blueprints after changes
   - Validates and finalizes graph modifications
   - Currently saves the blueprint asset

4. **`add_blueprint_variable()`** - Add variables to blueprints
   - Parameters: variable_name, variable_type, default_value, is_exposed
   - Supports common types: Boolean, Integer, Float, String, Vector, etc.
   - Currently returns placeholder (requires variable API access)

### Phase 2: Python Script Generation (Recommended Approach) 🎯

Instead of direct graph manipulation, generate Python scripts that run inside UE:

**Advantages:**
- Works within UE's Python environment constraints
- More stable across UE versions
- Easier to debug and test
- Can leverage UE's existing blueprint utilities

**Implementation:**
```python
def generate_blueprint_graph_script(
    blueprint_path: str,
    nodes: List[Dict],
    connections: List[Dict],
    variables: List[Dict]
) -> str:
    """
    Generate a Python script that creates blueprint graphs.
    
    Args:
        blueprint_path: Path to blueprint
        nodes: List of node definitions
        connections: List of pin connections
        variables: List of variable definitions
    
    Returns:
        Python script to execute in UE
    """
    script = f'''
import unreal

# Load blueprint
blueprint = unreal.load_asset("{blueprint_path}")
if not blueprint:
    print("Blueprint not found")
else:
    # Access blueprint's generated class
    blueprint_class = blueprint.generated_class()
    
    # Add variables
    {generate_variable_code(variables)}
    
    # Note: Graph manipulation requires C++ level access
    # This is a limitation of UE Python API
    
    # Save blueprint
    unreal.EditorAssetLibrary.save_asset("{blueprint_path}")
    print("Blueprint updated successfully")
'''
    return script
```

### Phase 3: C++ Plugin Extension (Full Solution) 🚀

For complete graph manipulation, create a C++ plugin that exposes graph operations to Python:

**Required Components:**

1. **C++ Module** (`AdastreaGraphEditor`)
   ```cpp
   class ADASTREAGRAPHEDITOR_API UAdastreaGraphLibrary : public UBlueprintFunctionLibrary
   {
       UFUNCTION(BlueprintCallable, Category = "Adastrea|Blueprint")
       static UK2Node* AddBlueprintNode(UBlueprint* Blueprint, FString NodeType, FVector2D Position);
       
       UFUNCTION(BlueprintCallable, Category = "Adastrea|Blueprint")
       static bool ConnectNodes(UK2Node* SourceNode, FName SourcePin, UK2Node* TargetNode, FName TargetPin);
   };
   ```

2. **Python Bindings**
   ```python
   import unreal
   
   def add_blueprint_node_cpp(blueprint_path, node_type, x, y):
       blueprint = unreal.load_asset(blueprint_path)
       node = unreal.AdastreaGraphLibrary.add_blueprint_node(
           blueprint, node_type, unreal.Vector2D(x, y)
       )
       return node
   ```

3. **MCP Tool Integration**
   ```python
   class EditorAddBlueprintNode(MCPTool):
       name = "editor_add_blueprint_node"
       description = "Add a node to a blueprint graph"
       # Implementation using C++ bridge
   ```

## Current Implementation Status

### ✅ Completed (Phase 1)

1. **API Structure**: Added 4 new methods to `UEPythonBridge`:
   - `add_blueprint_node()` - 70 lines with documentation
   - `connect_blueprint_nodes()` - 40 lines with documentation
   - `compile_blueprint()` - 45 lines with documentation
   - `add_blueprint_variable()` - 60 lines with documentation

2. **Documentation**: Each function includes:
   - Comprehensive docstrings
   - Parameter descriptions
   - Usage examples
   - Important notes about limitations

3. **Logging**: All functions include appropriate logging for debugging

### ⚠️ Current Limitations

1. **Placeholder Implementation**: Functions currently return placeholders
2. **No Direct Graph Access**: Python API doesn't expose graph internals
3. **Requires C++ Extension**: Full implementation needs C++ plugin
4. **Testing Required**: Need UE running to test actual graph operations

## Recommended Next Steps

### Option A: Python Script Approach (Easier, Limited)

1. Implement script generation in `ue_python_api.py`
2. Create helper scripts for common patterns
3. Test with simple blueprints
4. Document what's possible and limitations

**Estimated Effort**: 2-3 days
**Capabilities**: Variable creation, basic graph inspection
**Limitations**: No direct node manipulation

### Option B: C++ Plugin (Complete, Complex)

1. Create new C++ module in plugin
2. Implement graph manipulation functions
3. Expose to Python via bindings
4. Update MCP tools to use new functions
5. Comprehensive testing

**Estimated Effort**: 1-2 weeks
**Capabilities**: Full graph control
**Limitations**: Requires C++ compilation, UE version-specific

### Option C: Hybrid Approach (Recommended) ⭐

1. Keep current placeholder functions as interface
2. Implement what's possible with Python (variables, compilation)
3. Document C++ extension points
4. Provide examples using UE's built-in tools
5. Add MCP tool that executes custom Python in UE context

**Estimated Effort**: 3-5 days
**Capabilities**: Best of both worlds
**Limitations**: Some operations require manual UE interaction

## Example Usage (Future)

```python
# Create a simple blueprint with BeginPlay and Print
from ue_python_api import UEPythonBridge

bridge = UEPythonBridge()

# Create blueprint
blueprint = bridge.create_blueprint("BP_HelloWorld", "Actor", "/Game/Test")

# Add BeginPlay event
begin_play = bridge.add_blueprint_node(
    "/Game/Test/BP_HelloWorld",
    "BeginPlay",
    position_x=100,
    position_y=100
)

# Add Print String node
print_node = bridge.add_blueprint_node(
    "/Game/Test/BP_HelloWorld",
    "Print",
    position_x=400,
    position_y=100
)

# Connect them
bridge.connect_blueprint_nodes(
    "/Game/Test/BP_HelloWorld",
    begin_play,
    "execute",
    print_node,
    "execute"
)

# Add a variable
bridge.add_blueprint_variable(
    "/Game/Test/BP_HelloWorld",
    "Message",
    "String",
    default_value="Hello World!",
    is_exposed=True
)

# Compile
bridge.compile_blueprint("/Game/Test/BP_HelloWorld")
```

## Alternative: Template-Based Approach

Instead of programmatic graph creation, use blueprint templates:

1. Create template blueprints with common patterns
2. Copy and modify templates programmatically
3. Expose template parameters as variables
4. Much simpler than graph manipulation

```python
def create_blueprint_from_template(
    blueprint_name: str,
    template_path: str,
    parameters: Dict[str, Any]
) -> Optional[Any]:
    """Create blueprint from template and set parameters."""
    # Copy template
    # Set exposed variables
    # Rename and save
```

## Testing Strategy

1. **Unit Tests**: Mock UE APIs, test logic
2. **Integration Tests**: Run in UE, verify results
3. **Manual Testing**: Use test blueprints in UE Editor
4. **Documentation**: Example blueprints for each operation

## Resources

- [UE Python API Docs](https://docs.unrealengine.com/en-US/PythonAPI/)
- [Blueprint Technical Guide](https://docs.unrealengine.com/en-US/ProgrammingAndScripting/Blueprints/TechnicalGuide/)
- [UK2Node API (C++)](https://docs.unrealengine.com/en-US/API/Runtime/BlueprintGraph/UK2Node/)

## Conclusion

Blueprint graph manipulation is complex but achievable. The current implementation provides:
- ✅ API structure and interfaces
- ✅ Comprehensive documentation
- ✅ Clear implementation path forward
- ⚠️ Placeholder implementations (requires C++ or script generation)

**Recommendation**: Proceed with Hybrid Approach (Option C) to provide maximum value with reasonable effort.
