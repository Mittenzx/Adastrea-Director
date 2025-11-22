"""
Unreal Engine Remote Control API client for Adastrea Director.

This module provides a Python client for interacting with Unreal Engine projects
via the Remote Control API, enabling autonomous agents to control, test, and
monitor Unreal Engine in real-time.

Documentation: See docs/remote-control/REMOTE_CONTROL_API.md
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
from .test_agent import TestAgent, TestResult, TestStatus

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
    "TestAgent",
    "TestResult",
    "TestStatus",
]

__version__ = "0.1.0"
