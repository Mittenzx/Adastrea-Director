"""
Tests for the MCP Server tools module.
"""

import pytest
import json
from unittest.mock import Mock, MagicMock

from mcp_server.tools import (
    ToolParameter,
    ToolResult,
    MCPTool,
    EditorRunPython,
    EditorListAssets,
    EditorGetAssetInfo,
    EditorSearchAssets,
    EditorConsoleCommand,
    EditorGetProjectInfo,
    EditorGetMapInfo,
    EditorGetWorldOutliner,
    EditorCreateObject,
    EditorUpdateObject,
    EditorDeleteObject,
    EditorTakeScreenshot,
    EditorMoveCamera,
    TOOLS,
    get_tool,
    get_all_tools,
)
from mcp_server.remote_execution import CommandResult


class TestToolParameter:
    """Tests for ToolParameter dataclass."""
    
    def test_required_parameter(self):
        """Test creating a required parameter."""
        param = ToolParameter(
            name="code",
            type="string",
            description="Python code to execute"
        )
        
        assert param.name == "code"
        assert param.type == "string"
        assert param.description == "Python code to execute"
        assert param.required is True
        assert param.default is None
    
    def test_optional_parameter(self):
        """Test creating an optional parameter."""
        param = ToolParameter(
            name="filter",
            type="string",
            description="Optional filter",
            required=False,
            default=""
        )
        
        assert param.name == "filter"
        assert param.required is False
        assert param.default == ""


class TestToolResult:
    """Tests for ToolResult dataclass."""
    
    def test_text_result(self):
        """Test creating a text result."""
        result = ToolResult.text("Hello, World!")
        
        assert result.success is True
        assert len(result.content) == 1
        assert result.content[0]["type"] == "text"
        assert result.content[0]["text"] == "Hello, World!"
        assert result.error_message is None
    
    def test_image_result(self):
        """Test creating an image result."""
        result = ToolResult.image("base64data", "image/png")
        
        assert result.success is True
        assert len(result.content) == 1
        assert result.content[0]["type"] == "image"
        assert result.content[0]["data"] == "base64data"
        assert result.content[0]["mimeType"] == "image/png"
    
    def test_error_result(self):
        """Test creating an error result."""
        result = ToolResult.error("Something went wrong")
        
        assert result.success is False
        assert result.error_message == "Something went wrong"
        assert len(result.content) == 1
        assert "Error:" in result.content[0]["text"]


class TestEditorRunPython:
    """Tests for EditorRunPython tool."""
    
    def test_tool_metadata(self):
        """Test tool name and description."""
        tool = EditorRunPython()
        
        assert tool.name == "editor_run_python"
        assert "Python" in tool.description
        assert len(tool.parameters) == 1
        assert tool.parameters[0].name == "code"
    
    def test_execute_success(self):
        """Test successful execution."""
        tool = EditorRunPython()
        mock_remote = Mock()
        mock_remote.run_command.return_value = CommandResult(
            success=True,
            output="Hello from Python!"
        )
        
        result = tool.execute(mock_remote, code="print('Hello from Python!')")
        
        assert result.success is True
        assert "Hello from Python!" in result.content[0]["text"]
        mock_remote.run_command.assert_called_once()
    
    def test_execute_no_code(self):
        """Test execution with no code."""
        tool = EditorRunPython()
        mock_remote = Mock()
        
        result = tool.execute(mock_remote)
        
        assert result.success is False
        assert "No code provided" in result.error_message
    
    def test_execute_failure(self):
        """Test failed execution."""
        tool = EditorRunPython()
        mock_remote = Mock()
        mock_remote.run_command.return_value = CommandResult(
            success=False,
            error="Syntax error"
        )
        
        result = tool.execute(mock_remote, code="invalid python")
        
        assert result.success is False
        assert "Syntax error" in result.error_message
    
    def test_get_schema(self):
        """Test schema generation."""
        tool = EditorRunPython()
        schema = tool.get_schema()
        
        assert schema["type"] == "object"
        assert "code" in schema["properties"]
        assert "code" in schema["required"]


class TestEditorListAssets:
    """Tests for EditorListAssets tool."""
    
    def test_tool_metadata(self):
        """Test tool name and description."""
        tool = EditorListAssets()
        
        assert tool.name == "editor_list_assets"
        assert "assets" in tool.description.lower()
        assert len(tool.parameters) == 0
    
    def test_execute_success(self):
        """Test successful execution."""
        tool = EditorListAssets()
        mock_remote = Mock()
        mock_remote.run_command.return_value = CommandResult(
            success=True,
            output='["/Game/Maps/TestMap", "/Game/Blueprints/BP_Player"]'
        )
        
        result = tool.execute(mock_remote)
        
        assert result.success is True
        mock_remote.run_command.assert_called_once()


class TestEditorGetAssetInfo:
    """Tests for EditorGetAssetInfo tool."""
    
    def test_tool_metadata(self):
        """Test tool name and description."""
        tool = EditorGetAssetInfo()
        
        assert tool.name == "editor_get_asset_info"
        assert len(tool.parameters) == 1
        assert tool.parameters[0].name == "asset_path"
    
    def test_execute_success(self):
        """Test successful execution."""
        tool = EditorGetAssetInfo()
        mock_remote = Mock()
        mock_remote.run_command.return_value = CommandResult(
            success=True,
            output='{"name": "SM_Cube", "class": "StaticMesh"}'
        )
        
        result = tool.execute(mock_remote, asset_path="/Game/Meshes/SM_Cube")
        
        assert result.success is True
        mock_remote.run_command.assert_called_once()
    
    def test_execute_no_path(self):
        """Test execution with no asset path."""
        tool = EditorGetAssetInfo()
        mock_remote = Mock()
        
        result = tool.execute(mock_remote)
        
        assert result.success is False
        assert "No asset_path provided" in result.error_message


class TestEditorSearchAssets:
    """Tests for EditorSearchAssets tool."""
    
    def test_tool_metadata(self):
        """Test tool name and description."""
        tool = EditorSearchAssets()
        
        assert tool.name == "editor_search_assets"
        assert len(tool.parameters) == 2
    
    def test_execute_success(self):
        """Test successful execution."""
        tool = EditorSearchAssets()
        mock_remote = Mock()
        mock_remote.run_command.return_value = CommandResult(
            success=True,
            output='{"total_matches": 5, "assets": []}'
        )
        
        result = tool.execute(mock_remote, search_term="character")
        
        assert result.success is True
    
    def test_execute_no_search_term(self):
        """Test execution with no search term."""
        tool = EditorSearchAssets()
        mock_remote = Mock()
        
        result = tool.execute(mock_remote)
        
        assert result.success is False
        assert "No search_term provided" in result.error_message


class TestEditorConsoleCommand:
    """Tests for EditorConsoleCommand tool."""
    
    def test_tool_metadata(self):
        """Test tool name and description."""
        tool = EditorConsoleCommand()
        
        assert tool.name == "editor_console_command"
        assert len(tool.parameters) == 1
    
    def test_execute_success(self):
        """Test successful execution."""
        tool = EditorConsoleCommand()
        mock_remote = Mock()
        mock_remote.run_command.return_value = CommandResult(
            success=True,
            output="Command executed: stat fps"
        )
        
        result = tool.execute(mock_remote, command="stat fps")
        
        assert result.success is True
    
    def test_execute_no_command(self):
        """Test execution with no command."""
        tool = EditorConsoleCommand()
        mock_remote = Mock()
        
        result = tool.execute(mock_remote)
        
        assert result.success is False


class TestEditorGetProjectInfo:
    """Tests for EditorGetProjectInfo tool."""
    
    def test_tool_metadata(self):
        """Test tool name and description."""
        tool = EditorGetProjectInfo()
        
        assert tool.name == "editor_project_info"
        assert len(tool.parameters) == 0
    
    def test_execute_success(self):
        """Test successful execution."""
        tool = EditorGetProjectInfo()
        mock_remote = Mock()
        mock_remote.run_command.return_value = CommandResult(
            success=True,
            output='{"project_name": "TestProject", "engine_version": "5.4"}'
        )
        
        result = tool.execute(mock_remote)
        
        assert result.success is True


class TestEditorGetMapInfo:
    """Tests for EditorGetMapInfo tool."""
    
    def test_tool_metadata(self):
        """Test tool name and description."""
        tool = EditorGetMapInfo()
        
        assert tool.name == "editor_get_map_info"
        assert len(tool.parameters) == 0


class TestEditorGetWorldOutliner:
    """Tests for EditorGetWorldOutliner tool."""
    
    def test_tool_metadata(self):
        """Test tool name and description."""
        tool = EditorGetWorldOutliner()
        
        assert tool.name == "editor_get_world_outliner"
        assert len(tool.parameters) == 0


class TestEditorCreateObject:
    """Tests for EditorCreateObject tool."""
    
    def test_tool_metadata(self):
        """Test tool name and description."""
        tool = EditorCreateObject()
        
        assert tool.name == "editor_create_object"
        # Required params: object_class, object_name
        required_params = [p for p in tool.parameters if p.required]
        assert len(required_params) >= 2
    
    def test_execute_success(self):
        """Test successful execution."""
        tool = EditorCreateObject()
        mock_remote = Mock()
        mock_remote.run_command.return_value = CommandResult(
            success=True,
            output='{"success": true, "actor_name": "StaticMeshActor_1"}'
        )
        
        result = tool.execute(
            mock_remote,
            object_class="StaticMeshActor",
            object_name="MyCube",
            location={"x": 0, "y": 0, "z": 0}
        )
        
        assert result.success is True
    
    def test_execute_missing_required(self):
        """Test execution with missing required parameters."""
        tool = EditorCreateObject()
        mock_remote = Mock()
        
        result = tool.execute(mock_remote, object_class="StaticMeshActor")
        
        assert result.success is False


class TestEditorUpdateObject:
    """Tests for EditorUpdateObject tool."""
    
    def test_tool_metadata(self):
        """Test tool name and description."""
        tool = EditorUpdateObject()
        
        assert tool.name == "editor_update_object"
    
    def test_execute_missing_required(self):
        """Test execution with missing required parameters."""
        tool = EditorUpdateObject()
        mock_remote = Mock()
        
        result = tool.execute(mock_remote)
        
        assert result.success is False


class TestEditorDeleteObject:
    """Tests for EditorDeleteObject tool."""
    
    def test_tool_metadata(self):
        """Test tool name and description."""
        tool = EditorDeleteObject()
        
        assert tool.name == "editor_delete_object"
    
    def test_execute_missing_required(self):
        """Test execution with missing required parameters."""
        tool = EditorDeleteObject()
        mock_remote = Mock()
        
        result = tool.execute(mock_remote)
        
        assert result.success is False


class TestEditorTakeScreenshot:
    """Tests for EditorTakeScreenshot tool."""
    
    def test_tool_metadata(self):
        """Test tool name and description."""
        tool = EditorTakeScreenshot()
        
        assert tool.name == "editor_take_screenshot"
        assert len(tool.parameters) == 0


class TestEditorMoveCamera:
    """Tests for EditorMoveCamera tool."""
    
    def test_tool_metadata(self):
        """Test tool name and description."""
        tool = EditorMoveCamera()
        
        assert tool.name == "editor_move_camera"
        assert len(tool.parameters) == 2
    
    def test_execute_missing_required(self):
        """Test execution with missing required parameters."""
        tool = EditorMoveCamera()
        mock_remote = Mock()
        
        result = tool.execute(mock_remote, location={"x": 0, "y": 0, "z": 0})
        
        assert result.success is False


class TestToolRegistry:
    """Tests for tool registry functions."""
    
    def test_tools_registry(self):
        """Test TOOLS registry contains all tools."""
        expected_tools = [
            "editor_run_python",
            "editor_list_assets",
            "editor_get_asset_info",
            "editor_search_assets",
            "editor_console_command",
            "editor_project_info",
            "editor_get_map_info",
            "editor_get_world_outliner",
            "editor_create_object",
            "editor_update_object",
            "editor_delete_object",
            "editor_take_screenshot",
            "editor_move_camera",
        ]
        
        for tool_name in expected_tools:
            assert tool_name in TOOLS
    
    def test_get_tool_exists(self):
        """Test getting an existing tool."""
        tool = get_tool("editor_run_python")
        
        assert tool is not None
        assert isinstance(tool, EditorRunPython)
    
    def test_get_tool_not_exists(self):
        """Test getting a non-existent tool."""
        tool = get_tool("nonexistent_tool")
        
        assert tool is None
    
    def test_get_all_tools(self):
        """Test getting all tools."""
        tools = get_all_tools()
        
        assert len(tools) == len(TOOLS)
        for tool in tools:
            assert isinstance(tool, MCPTool)
