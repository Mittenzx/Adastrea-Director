"""
Data models for Unreal Engine Remote Control API.

This module defines the data structures used for communicating with
the Unreal Engine Remote Control API.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum


class PropertyType(Enum):
    """Supported property types in Unreal Engine."""
    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    VECTOR = "vector"
    ROTATOR = "rotator"
    COLOR = "color"
    OBJECT = "object"
    ARRAY = "array"


class CommandCategory(Enum):
    """Categories of console commands."""
    PROFILING = "profiling"
    DEBUG = "debug"
    RENDERING = "rendering"
    GAMEPLAY = "gameplay"
    CUSTOM = "custom"


@dataclass
class PropertyUpdate:
    """Represents a property update request."""
    object_path: str
    property_name: str
    property_value: Any
    property_type: Optional[PropertyType] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        return {
            "objectPath": self.object_path,
            "propertyName": self.property_name,
            "propertyValue": self.property_value,
        }


@dataclass
class FunctionCall:
    """Represents a function call request."""
    object_path: str
    function_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    generate_transaction: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        return {
            "objectPath": self.object_path,
            "functionName": self.function_name,
            "parameters": self.parameters,
            "generateTransaction": self.generate_transaction,
        }


@dataclass
class ConsoleCommand:
    """Represents a console command execution request."""
    command: str
    category: CommandCategory = CommandCategory.CUSTOM
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        return {
            "command": self.command,
        }


@dataclass
class RemoteControlResponse:
    """Response from Remote Control API."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def is_error(self) -> bool:
        """Check if response contains an error."""
        return not self.success or self.error is not None


@dataclass
class AssetInfo:
    """Information about a Unreal Engine asset."""
    asset_path: str
    asset_name: str
    asset_type: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance metrics from Unreal Engine."""
    timestamp: datetime
    frame_rate: float
    frame_time_ms: float
    game_thread_ms: float
    render_thread_ms: float
    gpu_time_ms: float
    memory_mb: float
    draw_calls: int
    triangles: int
    
    def is_below_threshold(self, target_fps: float = 60.0) -> bool:
        """Check if performance is below target threshold."""
        return self.frame_rate < target_fps


class RemoteControlError(Exception):
    """Base exception for Remote Control API errors."""
    pass


class ConnectionError(RemoteControlError):
    """Raised when connection to Unreal Engine fails."""
    pass


class RequestError(RemoteControlError):
    """Raised when a request to the API fails."""
    pass


class TimeoutError(RemoteControlError):
    """Raised when a request times out."""
    pass


class ValidationError(RemoteControlError):
    """Raised when input validation fails."""
    pass
