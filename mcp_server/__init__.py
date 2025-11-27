"""
Adastrea Director MCP Server.

This module provides a Model Context Protocol (MCP) server that enables
AI agents and tools (like Claude, Cursor, etc.) to interact with Unreal Engine
through the Adastrea Director infrastructure.

The MCP server bridges external AI assistants to Unreal Engine using the
Python Remote Execution protocol, similar to the runreal/unreal-mcp project
but integrated with Adastrea Director's existing capabilities.

Documentation: See MCP_SERVER_GUIDE.md for setup and usage.
"""

from .server import UnrealMCPServer
from .tools import (
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
)
from .remote_execution import UnrealRemoteExecution

__all__ = [
    "UnrealMCPServer",
    "UnrealRemoteExecution",
    "MCPTool",
    "EditorRunPython",
    "EditorListAssets",
    "EditorGetAssetInfo",
    "EditorSearchAssets",
    "EditorConsoleCommand",
    "EditorGetProjectInfo",
    "EditorGetMapInfo",
    "EditorGetWorldOutliner",
    "EditorCreateObject",
    "EditorUpdateObject",
    "EditorDeleteObject",
    "EditorTakeScreenshot",
    "EditorMoveCamera",
]

__version__ = "0.1.0"
