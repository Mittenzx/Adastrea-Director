"""
Unreal Engine Remote Control API client for Adastrea Director.

This module provides a Python client for interacting with Unreal Engine projects
via the Remote Control API, enabling autonomous agents to control, test, and
monitor Unreal Engine in real-time.

Documentation: See https://github.com/Mittenzx/Adastrea-Director/wiki
"""

from .client import UnrealRemoteControlClient
from .models import (
    PropertyUpdate,
    FunctionCall,
    ConsoleCommand,
    RemoteControlResponse,
    RemoteControlError,
)
from .websocket_client import WebSocketEventClient, EventType
from .base_agent import RemoteControlAgent

__all__ = [
    "UnrealRemoteControlClient",
    "PropertyUpdate",
    "FunctionCall",
    "ConsoleCommand",
    "RemoteControlResponse",
    "RemoteControlError",
    "WebSocketEventClient",
    "EventType",
    "RemoteControlAgent",
]

__version__ = "0.1.0"
