"""
MCP Tools for Unreal Engine integration.

This module defines the tools available through the MCP server for
interacting with Unreal Engine. Each tool corresponds to a specific
operation that can be performed in the Unreal Editor.
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

logger = logging.getLogger(__name__)

# Maximum number of results to return from asset/actor queries
MAX_RESULTS = 100
MAX_SEARCH_RESULTS = 50
MAX_ASSET_TYPE_SAMPLE = 1000


@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    content: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    
    @classmethod
    def text(cls, text: str) -> "ToolResult":
        """Create a text result."""
        return cls(success=True, content=[{"type": "text", "text": text}], error_message=None)
    
    @classmethod
    def image(cls, data: str, mime_type: str = "image/png") -> "ToolResult":
        """Create an image result."""
        return cls(success=True, content=[{
            "type": "image",
            "data": data,
            "mimeType": mime_type
        }], error_message=None)
    
    @classmethod
    def error(cls, message: str) -> "ToolResult":
        """Create an error result."""
        return cls(success=False, error_message=message, content=[{
            "type": "text",
            "text": f"Error: {message}"
        }])


class MCPTool(ABC):
    """Base class for MCP tools."""
    
    name: str = ""
    description: str = ""
    parameters: List[ToolParameter] = []
    
    @abstractmethod
    def execute(self, remote, **kwargs) -> ToolResult:
        """
        Execute the tool.
        
        Args:
            remote: UnrealRemoteExecution instance for running commands.
            **kwargs: Tool-specific parameters.
            
        Returns:
            ToolResult with the execution result.
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool's parameters."""
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            if param.default is not None:
                properties[param.name]["default"] = param.default
            if param.required:
                required.append(param.name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }


class EditorRunPython(MCPTool):
    """Execute arbitrary Python code in the Unreal Editor."""
    
    name = "editor_run_python"
    description = (
        "Execute any Python code within the Unreal Editor. "
        "It is recommended to include `import unreal` at the top. "
        "Check the Unreal Python documentation before using this tool."
    )
    parameters = [
        ToolParameter(
            name="code",
            type="string",
            description="Python code to execute in the Unreal Editor"
        )
    ]
    
    def execute(self, remote, **kwargs) -> ToolResult:
        code = kwargs.get("code", "")
        if not code:
            return ToolResult.error("No code provided")
        
        result = remote.run_command(code)
        if result.success:
            return ToolResult.text(result.output)
        else:
            return ToolResult.error(result.error)


class EditorListAssets(MCPTool):
    """List all Unreal assets in the project."""
    
    name = "editor_list_assets"
    description = (
        "List all Unreal assets in the project. "
        "Returns a Python list of asset paths."
    )
    parameters = []
    
    _script = """
import unreal
import json

asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
assets = asset_registry.get_all_assets()
asset_paths = [str(asset.package_name) for asset in assets]
print(json.dumps(asset_paths[:100]))  # Limit to first MAX_RESULTS for performance
"""
    
    def execute(self, remote, **kwargs) -> ToolResult:
        result = remote.run_command(self._script)
        if result.success:
            return ToolResult.text(result.output)
        else:
            return ToolResult.error(result.error)


class EditorGetAssetInfo(MCPTool):
    """Get information about a specific asset."""
    
    name = "editor_get_asset_info"
    description = (
        "Get information about an asset, including LOD levels for "
        "StaticMesh and SkeletalMesh assets."
    )
    parameters = [
        ToolParameter(
            name="asset_path",
            type="string",
            description="Path to the asset (e.g., '/Game/Meshes/SM_Cube')"
        )
    ]
    
    _script_template = """
import unreal
import json

asset_path = {asset_path_json}
asset_data = unreal.EditorAssetLibrary.find_asset_data(asset_path)

if not asset_data.is_valid():
    print(json.dumps({{"error": "Asset not found"}}))
else:
    info = {{
        "name": str(asset_data.asset_name),
        "class": str(asset_data.asset_class_path.asset_name),
        "path": str(asset_data.package_name),
        "is_valid": asset_data.is_valid(),
    }}
    
    # Try to get additional info for mesh assets
    asset = asset_data.get_asset()
    if asset:
        if hasattr(asset, 'get_num_lods'):
            lods = []
            for i in range(asset.get_num_lods()):
                lods.append({{"lod_index": i}})
            info["lod_levels"] = lods
    
    print(json.dumps(info))
"""
    
    def execute(self, remote, **kwargs) -> ToolResult:
        asset_path = kwargs.get("asset_path", "")
        if not asset_path:
            return ToolResult.error("No asset_path provided")
        
        script = self._script_template.format(asset_path_json=json.dumps(asset_path))
        result = remote.run_command(script)
        if result.success:
            return ToolResult.text(result.output)
        else:
            return ToolResult.error(result.error)


class EditorSearchAssets(MCPTool):
    """Search for assets by name or path."""
    
    name = "editor_search_assets"
    description = (
        "Search for assets by name or path with optional class filter. "
        "Returns matching assets with details."
    )
    parameters = [
        ToolParameter(
            name="search_term",
            type="string",
            description="Search term to find assets"
        ),
        ToolParameter(
            name="asset_class",
            type="string",
            description="Optional class filter (e.g., 'Blueprint', 'StaticMesh')",
            required=False,
            default=""
        )
    ]
    
    _script_template = """
import unreal
import json

search_term = {search_term_json}
asset_class = {asset_class_json}

asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
assets = asset_registry.get_all_assets()

results = []
for asset in assets:
    name = str(asset.asset_name).lower()
    path = str(asset.package_name).lower()
    
    if search_term.lower() in name or search_term.lower() in path:
        if not asset_class or asset_class.lower() in str(asset.asset_class_path.asset_name).lower():
            results.append({{
                "name": str(asset.asset_name),
                "path": str(asset.package_name),
                "class": str(asset.asset_class_path.asset_name)
            }})
    
    if len(results) >= 50:  # Limit results
        break

output = {{
    "search_term": search_term,
    "asset_class_filter": asset_class,
    "total_matches": len(results),
    "assets": results
}}
print(json.dumps(output))
"""
    
    def execute(self, remote, **kwargs) -> ToolResult:
        search_term = kwargs.get("search_term", "")
        asset_class = kwargs.get("asset_class", "")
        
        if not search_term:
            return ToolResult.error("No search_term provided")
        
        script = self._script_template.format(
            search_term_json=json.dumps(search_term),
            asset_class_json=json.dumps(asset_class)
        )
        result = remote.run_command(script)
        if result.success:
            return ToolResult.text(result.output)
        else:
            return ToolResult.error(result.error)


class EditorConsoleCommand(MCPTool):
    """Execute a console command in Unreal Engine."""
    
    name = "editor_console_command"
    description = "Run a console command in Unreal Engine."
    parameters = [
        ToolParameter(
            name="command",
            type="string",
            description="Console command to execute (e.g., 'stat fps')"
        )
    ]
    
    _script_template = """
import unreal
command = {command_json}
unreal.SystemLibrary.execute_console_command(None, command)
print("Command executed: " + command)
"""
    
    def execute(self, remote, **kwargs) -> ToolResult:
        command = kwargs.get("command", "")
        if not command:
            return ToolResult.error("No command provided")
        
        script = self._script_template.format(command_json=json.dumps(command))
        result = remote.run_command(script)
        if result.success:
            return ToolResult.text(result.output)
        else:
            return ToolResult.error(result.error)


class EditorGetProjectInfo(MCPTool):
    """Get detailed information about the current project."""
    
    name = "editor_project_info"
    description = (
        "Get detailed information about the current project including "
        "project name, engine version, and asset counts."
    )
    parameters = []
    
    _script = """
import unreal
import json

# Get project info
project_dir = unreal.Paths.project_dir()
project_name = unreal.Paths.get_base_filename(unreal.Paths.get_project_file_path())
engine_version = unreal.SystemLibrary.get_engine_version()

# Count assets
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
all_assets = asset_registry.get_all_assets()
total_assets = len(all_assets)

# Categorize assets by type
asset_types = {}
for asset in all_assets[:1000]:  # Sample for performance
    asset_class = str(asset.asset_class_path.asset_name)
    asset_types[asset_class] = asset_types.get(asset_class, 0) + 1

info = {
    "project_name": project_name,
    "project_directory": project_dir,
    "engine_version": engine_version,
    "total_assets": total_assets,
    "asset_types_sample": dict(sorted(asset_types.items(), key=lambda x: -x[1])[:10])
}

print(json.dumps(info, indent=2))
"""
    
    def execute(self, remote, **kwargs) -> ToolResult:
        result = remote.run_command(self._script)
        if result.success:
            return ToolResult.text(result.output)
        else:
            return ToolResult.error(result.error)


class EditorGetMapInfo(MCPTool):
    """Get detailed information about the current map/level."""
    
    name = "editor_get_map_info"
    description = (
        "Get detailed information about the current map/level including "
        "actor counts and lighting details."
    )
    parameters = []
    
    _script = """
import unreal
import json

world = unreal.EditorLevelLibrary.get_editor_world()
if not world:
    print(json.dumps({"error": "No world loaded"}))
else:
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    
    # Count actors by type
    actor_types = {}
    for actor in actors:
        actor_class = actor.get_class().get_name()
        actor_types[actor_class] = actor_types.get(actor_class, 0) + 1
    
    info = {
        "map_name": world.get_name(),
        "total_actors": len(actors),
        "actor_types": dict(sorted(actor_types.items(), key=lambda x: -x[1])[:20])
    }
    
    print(json.dumps(info, indent=2))
"""
    
    def execute(self, remote, **kwargs) -> ToolResult:
        result = remote.run_command(self._script)
        if result.success:
            return ToolResult.text(result.output)
        else:
            return ToolResult.error(result.error)


class EditorGetWorldOutliner(MCPTool):
    """Get all actors in the current world with their properties."""
    
    name = "editor_get_world_outliner"
    description = (
        "Get all actors in the current world with their properties including "
        "location, rotation, and scale."
    )
    parameters = []
    
    _script = """
import unreal
import json

world = unreal.EditorLevelLibrary.get_editor_world()
if not world:
    print(json.dumps({"error": "No world loaded"}))
else:
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    
    actor_list = []
    for actor in actors[:100]:  # Limit for performance
        location = actor.get_actor_location()
        rotation = actor.get_actor_rotation()
        scale = actor.get_actor_scale3d()
        
        actor_info = {
            "name": actor.get_name(),
            "label": actor.get_actor_label(),
            "class": actor.get_class().get_name(),
            "location": {"x": location.x, "y": location.y, "z": location.z},
            "rotation": {"pitch": rotation.pitch, "yaw": rotation.yaw, "roll": rotation.roll},
            "scale": {"x": scale.x, "y": scale.y, "z": scale.z},
            "is_hidden": actor.is_hidden()
        }
        actor_list.append(actor_info)
    
    output = {
        "world_name": world.get_name(),
        "total_actors": len(actors),
        "actors": actor_list
    }
    
    print(json.dumps(output, indent=2))
"""
    
    def execute(self, remote, **kwargs) -> ToolResult:
        result = remote.run_command(self._script)
        if result.success:
            return ToolResult.text(result.output)
        else:
            return ToolResult.error(result.error)


class EditorCreateObject(MCPTool):
    """Create a new actor in the world."""
    
    name = "editor_create_object"
    description = (
        "Create a new object/actor in the world with specified properties."
    )
    parameters = [
        ToolParameter(
            name="object_class",
            type="string",
            description="Unreal class name (e.g., 'StaticMeshActor', 'DirectionalLight')"
        ),
        ToolParameter(
            name="object_name",
            type="string",
            description="Name/label for the created object"
        ),
        ToolParameter(
            name="location",
            type="object",
            description="World position {x, y, z}",
            required=False
        ),
        ToolParameter(
            name="rotation",
            type="object",
            description="Rotation in degrees {pitch, yaw, roll}",
            required=False
        ),
        ToolParameter(
            name="scale",
            type="object",
            description="Scale multipliers {x, y, z}",
            required=False
        )
    ]
    
    _script_template = """
import unreal
import json

object_class = {object_class_json}
object_name = {object_name_json}
location = {location}
rotation = {rotation}
scale = {scale}

# Create spawn location
spawn_location = unreal.Vector(
    location.get('x', 0) if location else 0,
    location.get('y', 0) if location else 0,
    location.get('z', 0) if location else 0
)

spawn_rotation = unreal.Rotator(
    rotation.get('pitch', 0) if rotation else 0,
    rotation.get('yaw', 0) if rotation else 0,
    rotation.get('roll', 0) if rotation else 0
)

# Spawn the actor
actor_class = getattr(unreal, object_class, None)
if not actor_class:
    print(json.dumps({{"error": f"Class {{object_class}} not found"}}))
else:
    world = unreal.EditorLevelLibrary.get_editor_world()
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(actor_class, spawn_location, spawn_rotation)
    
    if actor:
        actor.set_actor_label(object_name)
        
        if scale:
            actor.set_actor_scale3d(unreal.Vector(
                scale.get('x', 1),
                scale.get('y', 1),
                scale.get('z', 1)
            ))
        
        result = {{
            "success": True,
            "actor_name": actor.get_name(),
            "actor_label": object_name,
            "class": object_class,
            "location": {{"x": spawn_location.x, "y": spawn_location.y, "z": spawn_location.z}},
            "rotation": {{"pitch": spawn_rotation.pitch, "yaw": spawn_rotation.yaw, "roll": spawn_rotation.roll}}
        }}
        print(json.dumps(result))
    else:
        print(json.dumps({{"error": "Failed to spawn actor"}}))
"""
    
    def execute(self, remote, **kwargs) -> ToolResult:
        object_class = kwargs.get("object_class", "")
        object_name = kwargs.get("object_name", "")
        
        if not object_class or not object_name:
            return ToolResult.error("object_class and object_name are required")
        
        location = kwargs.get("location", None)
        rotation = kwargs.get("rotation", None)
        scale = kwargs.get("scale", None)
        
        script = self._script_template.format(
            object_class_json=json.dumps(object_class),
            object_name_json=json.dumps(object_name),
            location=json.dumps(location) if location else "None",
            rotation=json.dumps(rotation) if rotation else "None",
            scale=json.dumps(scale) if scale else "None"
        )
        
        result = remote.run_command(script)
        if result.success:
            return ToolResult.text(result.output)
        else:
            return ToolResult.error(result.error)


class EditorUpdateObject(MCPTool):
    """Update an existing actor in the world."""
    
    name = "editor_update_object"
    description = "Update an existing object/actor in the world."
    parameters = [
        ToolParameter(
            name="actor_name",
            type="string",
            description="Name or label of the actor to update"
        ),
        ToolParameter(
            name="location",
            type="object",
            description="New world position {x, y, z}",
            required=False
        ),
        ToolParameter(
            name="rotation",
            type="object",
            description="New rotation in degrees {pitch, yaw, roll}",
            required=False
        ),
        ToolParameter(
            name="scale",
            type="object",
            description="New scale multipliers {x, y, z}",
            required=False
        ),
        ToolParameter(
            name="new_name",
            type="string",
            description="New name/label for the actor",
            required=False
        )
    ]
    
    _script_template = """
import unreal
import json

actor_name = {actor_name_json}
location = {location}
rotation = {rotation}
scale = {scale}
new_name = {new_name}

# Find the actor
actors = unreal.EditorLevelLibrary.get_all_level_actors()
target_actor = None
for actor in actors:
    if actor.get_name() == actor_name or actor.get_actor_label() == actor_name:
        target_actor = actor
        break

if not target_actor:
    print(json.dumps({{"error": f"Actor '{{actor_name}}' not found"}}))
else:
    if location:
        target_actor.set_actor_location(unreal.Vector(
            location.get('x', 0),
            location.get('y', 0),
            location.get('z', 0)
        ), False, False)
    
    if rotation:
        target_actor.set_actor_rotation(unreal.Rotator(
            rotation.get('pitch', 0),
            rotation.get('yaw', 0),
            rotation.get('roll', 0)
        ), False)
    
    if scale:
        target_actor.set_actor_scale3d(unreal.Vector(
            scale.get('x', 1),
            scale.get('y', 1),
            scale.get('z', 1)
        ))
    
    if new_name is not None:
        target_actor.set_actor_label(new_name)
    
    loc = target_actor.get_actor_location()
    rot = target_actor.get_actor_rotation()
    sc = target_actor.get_actor_scale3d()
    
    result = {{
        "success": True,
        "actor_name": target_actor.get_name(),
        "actor_label": target_actor.get_actor_label(),
        "location": {{"x": loc.x, "y": loc.y, "z": loc.z}},
        "rotation": {{"pitch": rot.pitch, "yaw": rot.yaw, "roll": rot.roll}},
        "scale": {{"x": sc.x, "y": sc.y, "z": sc.z}}
    }}
    print(json.dumps(result))
"""
    
    def execute(self, remote, **kwargs) -> ToolResult:
        actor_name = kwargs.get("actor_name", "")
        
        if not actor_name:
            return ToolResult.error("actor_name is required")
        
        location = kwargs.get("location", None)
        rotation = kwargs.get("rotation", None)
        scale = kwargs.get("scale", None)
        new_name = kwargs.get("new_name", None)
        
        script = self._script_template.format(
            actor_name_json=json.dumps(actor_name),
            location=json.dumps(location) if location else "None",
            rotation=json.dumps(rotation) if rotation else "None",
            scale=json.dumps(scale) if scale else "None",
            new_name=json.dumps(new_name) if new_name is not None else "None"
        )
        
        result = remote.run_command(script)
        if result.success:
            return ToolResult.text(result.output)
        else:
            return ToolResult.error(result.error)


class EditorDeleteObject(MCPTool):
    """Delete an actor from the world."""
    
    name = "editor_delete_object"
    description = "Delete an object/actor from the world."
    parameters = [
        ToolParameter(
            name="actor_name",
            type="string",
            description="Name or label of the actor to delete"
        )
    ]
    
    _script_template = """
import unreal
import json

actor_name = {actor_name_json}

# Find the actor
actors = unreal.EditorLevelLibrary.get_all_level_actors()
target_actor = None
for actor in actors:
    if actor.get_name() == actor_name or actor.get_actor_label() == actor_name:
        target_actor = actor
        break

if not target_actor:
    print(json.dumps({{"error": f"Actor '{{actor_name}}' not found"}}))
else:
    actor_info = {{
        "actor_name": target_actor.get_name(),
        "actor_label": target_actor.get_actor_label(),
        "class": target_actor.get_class().get_name()
    }}
    
    success = unreal.EditorLevelLibrary.destroy_actor(target_actor)
    
    if success:
        result = {{
            "success": True,
            "message": f"Successfully deleted actor: {{actor_name}}",
            "deleted_actor": actor_info
        }}
    else:
        result = {{"error": "Failed to delete actor"}}
    
    print(json.dumps(result))
"""
    
    def execute(self, remote, **kwargs) -> ToolResult:
        actor_name = kwargs.get("actor_name", "")
        
        if not actor_name:
            return ToolResult.error("actor_name is required")
        
        script = self._script_template.format(actor_name_json=json.dumps(actor_name))
        result = remote.run_command(script)
        if result.success:
            return ToolResult.text(result.output)
        else:
            return ToolResult.error(result.error)


class EditorTakeScreenshot(MCPTool):
    """Take a screenshot of the Unreal Editor."""
    
    name = "editor_take_screenshot"
    description = (
        "Take a screenshot of the Unreal Editor viewport. "
        "Make sure the Unreal Engine window is focused."
    )
    parameters = []
    
    _script = """
import unreal
import os
import tempfile

# Generate unique filename
temp_dir = tempfile.gettempdir()
filename = os.path.join(temp_dir, "unreal_screenshot.png")

# Take screenshot
unreal.AutomationLibrary.take_high_res_screenshot(
    1920, 1080,  # Resolution
    filename
)

print(filename)
"""
    
    def execute(self, remote, **kwargs) -> ToolResult:
        result = remote.run_command(self._script)
        if result.success:
            # The script returns the file path
            # In a full implementation, we'd read the file and return as base64
            return ToolResult.text(f"Screenshot saved to: {result.output.strip()}")
        else:
            return ToolResult.error(result.error)


class EditorMoveCamera(MCPTool):
    """Move the viewport camera to a specific location."""
    
    name = "editor_move_camera"
    description = (
        "Move the viewport camera to a specific location and rotation "
        "for positioning screenshots."
    )
    parameters = [
        ToolParameter(
            name="location",
            type="object",
            description="Camera world position {x, y, z}"
        ),
        ToolParameter(
            name="rotation",
            type="object",
            description="Camera rotation in degrees {pitch, yaw, roll}"
        )
    ]
    
    _script_template = """
import unreal
import json

location = {location}
rotation = {rotation}

# Get the level editor viewport
editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if editor_subsystem:
    editor_subsystem.set_level_viewport_camera_info(
        unreal.Vector(location['x'], location['y'], location['z']),
        unreal.Rotator(rotation['pitch'], rotation['yaw'], rotation['roll'])
    )
    
    result = {{
        "success": True,
        "location": location,
        "rotation": rotation
    }}
    print(json.dumps(result))
else:
    print(json.dumps({{"error": "Could not access level editor subsystem"}}))
"""
    
    def execute(self, remote, **kwargs) -> ToolResult:
        location = kwargs.get("location", {})
        rotation = kwargs.get("rotation", {})
        
        if not location or not rotation:
            return ToolResult.error("Both location and rotation are required")
        
        script = self._script_template.format(
            location=json.dumps(location),
            rotation=json.dumps(rotation)
        )
        
        result = remote.run_command(script)
        if result.success:
            return ToolResult.text(result.output)
        else:
            return ToolResult.error(result.error)


# Registry of all available tools
TOOLS: Dict[str, Type[MCPTool]] = {
    "editor_run_python": EditorRunPython,
    "editor_list_assets": EditorListAssets,
    "editor_get_asset_info": EditorGetAssetInfo,
    "editor_search_assets": EditorSearchAssets,
    "editor_console_command": EditorConsoleCommand,
    "editor_project_info": EditorGetProjectInfo,
    "editor_get_map_info": EditorGetMapInfo,
    "editor_get_world_outliner": EditorGetWorldOutliner,
    "editor_create_object": EditorCreateObject,
    "editor_update_object": EditorUpdateObject,
    "editor_delete_object": EditorDeleteObject,
    "editor_take_screenshot": EditorTakeScreenshot,
    "editor_move_camera": EditorMoveCamera,
}


def get_tool(name: str) -> Optional[MCPTool]:
    """Get a tool instance by name."""
    tool_class = TOOLS.get(name)
    if tool_class:
        return tool_class()
    return None


def get_all_tools() -> List[MCPTool]:
    """Get instances of all available tools."""
    return [tool_class() for tool_class in TOOLS.values()]
