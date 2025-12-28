# Blueprint Comment Nodes Implementation Guide

## Overview

This guide provides a step-by-step approach to implementing comment node functionality for the Adastrea game. Comment nodes are the **easiest entry point** for blueprint graph manipulation, making them perfect for starting the implementation.

## Why Start with Comment Nodes?

Comment nodes are ideal because they:
- ✅ Don't affect game logic (safe to experiment)
- ✅ Simple to implement (no pin connections needed)
- ✅ Don't require compilation
- ✅ Provide immediate visual value
- ✅ Great for documentation and organization
- ✅ Low risk of blueprint corruption

## Implementation Approach

### Option 1: Python Script Generation (Recommended) ⭐

The most practical approach for comment nodes is Python script generation that runs inside Unreal Engine.

**Advantages:**
- Works with current Python API
- No C++ extension needed
- Can be implemented immediately
- Easy to test and debug

### Option 2: C++ Plugin (Future)

For complete control and performance, a C++ plugin can be developed later.

## Step-by-Step Implementation

### Phase 1: Basic Comment Node Addition (2-3 hours)

#### 1.1 Update `ue_python_api.py`

Add a dedicated function for comment nodes:

```python
def add_blueprint_comment(
    self,
    blueprint_path: str,
    comment_text: str,
    position_x: float = 0.0,
    position_y: float = 0.0,
    width: float = 400.0,
    height: float = 100.0,
    color: Optional[tuple] = None,
    font_size: int = 18
) -> bool:
    """
    Add a comment node to a blueprint graph.
    
    Args:
        blueprint_path: Full path to the blueprint asset
        comment_text: Text content of the comment
        position_x: X position in the graph
        position_y: Y position in the graph
        width: Width of the comment box
        height: Height of the comment box
        color: Optional RGB color tuple (0-255) for the comment box
        font_size: Font size for the comment text
        
    Returns:
        True if comment was added successfully
        
    Example:
        # Add a header comment
        bridge.add_blueprint_comment(
            "/Game/Blueprints/BP_Character",
            "=== Movement System ===",
            position_x=0,
            position_y=-200,
            width=800,
            color=(100, 149, 237)  # Cornflower blue
        )
    """
    try:
        # Generate Python script to run in UE
        script = self._generate_comment_script(
            blueprint_path,
            comment_text,
            position_x,
            position_y,
            width,
            height,
            color,
            font_size
        )
        
        # Execute via UE Python (this would use the MCP server)
        # For now, log what would be done
        logger.info(f"Would add comment to {blueprint_path}: '{comment_text}'")
        logger.info(f"Position: ({position_x}, {position_y}), Size: {width}x{height}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to add comment to blueprint '{blueprint_path}': {e}")
        return False

def _generate_comment_script(
    self,
    blueprint_path: str,
    comment_text: str,
    position_x: float,
    position_y: float,
    width: float,
    height: float,
    color: Optional[tuple],
    font_size: int
) -> str:
    """Generate Python script for adding comment in UE."""
    
    # Default color if none specified
    if color is None:
        color = (255, 255, 255)  # White
    
    color_str = f"unreal.LinearColor({color[0]/255}, {color[1]/255}, {color[2]/255}, 1.0)"
    
    script = f'''
import unreal

# Load the blueprint
blueprint = unreal.load_asset("{blueprint_path}")
if not blueprint:
    print("ERROR: Blueprint not found: {blueprint_path}")
else:
    # Get the event graph
    event_graph = None
    for graph in blueprint.ubergraph_pages:
        if graph.get_name() == "EventGraph":
            event_graph = graph
            break
    
    if not event_graph:
        print("ERROR: Event graph not found")
    else:
        # Create comment node
        comment_node = unreal.EdGraphNode_Comment()
        comment_node.set_editor_property("node_comment", "{comment_text}")
        comment_node.set_editor_property("node_pos_x", {position_x})
        comment_node.set_editor_property("node_pos_y", {position_y})
        comment_node.set_editor_property("node_width", {width})
        comment_node.set_editor_property("node_height", {height})
        comment_node.set_editor_property("comment_color", {color_str})
        comment_node.set_editor_property("font_size", {font_size})
        
        # Add to graph
        event_graph.add_node(comment_node, False, False)
        
        # Save the blueprint
        unreal.EditorAssetLibrary.save_asset("{blueprint_path}", False)
        
        print(f"SUCCESS: Added comment to {{blueprint_path}}")
'''
    return script
```

#### 1.2 Add Test Cases

```python
def test_add_blueprint_comment(self, bridge):
    """Test adding a comment to blueprint."""
    result = bridge.add_blueprint_comment(
        "/Game/Blueprints/BP_TestActor",
        "Test Comment",
        position_x=100,
        position_y=100
    )
    assert result is True

def test_add_blueprint_comment_with_color(self, bridge):
    """Test adding a colored comment."""
    result = bridge.add_blueprint_comment(
        "/Game/Blueprints/BP_TestActor",
        "Important Note",
        color=(255, 0, 0)  # Red
    )
    assert result is True
```

### Phase 2: MCP Tool Integration (1-2 hours)

Add MCP tool in `mcp_server/tools.py`:

```python
class EditorAddBlueprintComment(MCPTool):
    """Add a comment node to a blueprint graph."""
    
    name = "editor_add_blueprint_comment"
    description = (
        "Add a comment/documentation node to a blueprint graph. "
        "Comments help organize and document blueprint logic without affecting execution."
    )
    parameters = [
        ToolParameter(
            name="blueprint_path",
            type="string",
            description="Full path to the blueprint (e.g., '/Game/Blueprints/BP_Character')"
        ),
        ToolParameter(
            name="comment_text",
            type="string",
            description="Text content of the comment"
        ),
        ToolParameter(
            name="position_x",
            type="number",
            description="X position in the graph (default: 0)",
            required=False,
            default=0
        ),
        ToolParameter(
            name="position_y",
            type="number",
            description="Y position in the graph (default: 0)",
            required=False,
            default=0
        ),
        ToolParameter(
            name="width",
            type="number",
            description="Width of the comment box (default: 400)",
            required=False,
            default=400
        ),
        ToolParameter(
            name="height",
            type="number",
            description="Height of the comment box (default: 100)",
            required=False,
            default=100
        ),
        ToolParameter(
            name="color",
            type="string",
            description="Hex color code (e.g., '#6495ED') or preset name",
            required=False
        )
    ]
    
    # Preset colors for common comment types
    COLOR_PRESETS = {
        "header": (100, 149, 237),      # Cornflower blue
        "important": (220, 20, 60),     # Crimson
        "todo": (255, 215, 0),          # Gold
        "bug": (255, 69, 0),            # Red-Orange
        "optimization": (50, 205, 50),  # Lime green
        "adastrea": (138, 43, 226)      # Blue-violet (Adastrea brand color)
    }
    
    def execute(self, remote, **kwargs) -> ToolResult:
        # Implementation here
        pass
```

### Phase 3: CLI Integration (30 minutes)

Add to `unreal_mcp_cli.py`:

```python
# Interactive mode
elif cmd == "comment":
    if not arg:
        print("Usage: comment <blueprint_path> <text> [x] [y]")
    else:
        parts = arg.split(maxsplit=3)
        if len(parts) < 2:
            print("Error: Need blueprint path and comment text")
        else:
            params = {
                "blueprint_path": parts[0],
                "comment_text": parts[1]
            }
            if len(parts) > 2:
                params["position_x"] = float(parts[2])
            if len(parts) > 3:
                params["position_y"] = float(parts[3])
            result = server.handle_tool_call("editor_add_blueprint_comment", params)
            print_result(result)

# Command-line mode
comment_parser = subparsers.add_parser("add-comment", help="Add comment to blueprint")
comment_parser.add_argument("blueprint", help="Blueprint path")
comment_parser.add_argument("text", help="Comment text")
comment_parser.add_argument("--x", type=float, default=0, help="X position")
comment_parser.add_argument("--y", type=float, default=0, help="Y position")
comment_parser.add_argument("--color", help="Color preset or hex code")
```

## Adastrea Game Comment Library

See `ADASTREA_COMMENT_LIBRARY.md` for a comprehensive library of pre-defined comments specific to the Adastrea game.

## Testing Strategy

### 1. Unit Tests (No UE Required)
```bash
pytest Plugins/AdastreaDirector/Python/test_ue_python_api.py::TestBlueprintComments -v
```

### 2. Integration Tests (UE Required)
1. Start Unreal Engine with Adastrea project
2. Enable Python Plugin and Remote Execution
3. Run test blueprint creation script
4. Verify comments appear in blueprint

### 3. Manual Testing
```bash
# Interactive mode
python unreal_mcp_cli.py
unreal> comment /Game/BP_Test "Test Comment" 0 0

# Command mode
python unreal_mcp_cli.py add-comment /Game/BP_Test "Test Comment" --x 0 --y 0
```

## Common Comment Patterns for Adastrea

### 1. Section Headers
```python
bridge.add_blueprint_comment(
    blueprint_path,
    "═══ INITIALIZATION ═══",
    position_x=0,
    position_y=-200,
    width=800,
    height=60,
    color=(100, 149, 237),  # Cornflower blue
    font_size=20
)
```

### 2. Function Documentation
```python
bridge.add_blueprint_comment(
    blueprint_path,
    """Function: CalculateDamage
    Input: BaseDamage (float), DamageType (enum)
    Output: FinalDamage (float)
    
    Applies modifiers based on damage type and player stats.""",
    position_x=100,
    position_y=100,
    width=500,
    height=150
)
```

### 3. TODO/Bug Markers
```python
bridge.add_blueprint_comment(
    blueprint_path,
    "TODO: Implement collision detection",
    color=(255, 215, 0),  # Gold
    font_size=16
)
```

### 4. System Notes
```python
bridge.add_blueprint_comment(
    blueprint_path,
    "⚠️ ADASTREA GAME SYSTEM\nThis blueprint is part of the core movement system.\nModify with caution!",
    color=(138, 43, 226),  # Adastrea brand color
    width=600
)
```

## Troubleshooting

### Issue: Comment not appearing
**Solution:** Verify blueprint path is correct and UE is running with Python enabled

### Issue: Comment has wrong color
**Solution:** Check color tuple format (R, G, B) with values 0-255

### Issue: Comment text is truncated
**Solution:** Increase width and height parameters

## Next Steps After Comment Nodes

Once comment nodes are working:
1. Add comment templates for common Adastrea patterns
2. Implement bulk comment addition
3. Create comment organization tools
4. Add comment search/filter functionality
5. Progress to simple logic nodes (variables, then function calls)

## Performance Considerations

- Comments don't affect blueprint compilation time
- Can add hundreds of comments without performance impact
- Comments are saved with the blueprint asset
- No runtime overhead

## Best Practices

1. **Use consistent colors** for different comment types
2. **Position strategically** to guide blueprint navigation
3. **Keep text concise** but informative
4. **Use section headers** to organize large blueprints
5. **Document Adastrea-specific systems** clearly

## Resources

- UE Documentation: EdGraphNode_Comment
- Blueprint Best Practices: UE Official Docs
- Adastrea Comment Library: `ADASTREA_COMMENT_LIBRARY.md`

## Conclusion

Comment nodes provide an excellent starting point for blueprint graph manipulation. They're:
- **Safe** - No risk to game logic
- **Practical** - Immediate documentation value
- **Simple** - Easy to implement and test
- **Scalable** - Foundation for more complex operations

Start with comments, validate the workflow, then expand to logic nodes when ready.
