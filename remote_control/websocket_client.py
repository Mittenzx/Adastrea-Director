"""
WebSocket client for real-time events from Unreal Engine Remote Control API.

This module provides WebSocket connectivity for receiving real-time updates
from Unreal Engine.
"""

import json
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from enum import Enum

import websocket

from .models import RemoteControlError

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events from Remote Control API."""
    PROPERTY_CHANGED = "property_changed"
    FUNCTION_CALLED = "function_called"
    PRESET_CHANGED = "preset_changed"
    CONNECTION_STATUS = "connection_status"
    ERROR = "error"


class WebSocketEventClient:
    """
    WebSocket client for real-time events from Unreal Engine.
    
    Provides asynchronous event handling for property changes, function calls,
    and other real-time updates from the Remote Control API.
    
    Example:
        ```python
        def on_property_changed(event):
            print(f"Property changed: {event}")
        
        client = WebSocketEventClient(host="localhost", port=30010)
        client.add_event_handler(EventType.PROPERTY_CHANGED, on_property_changed)
        client.connect()
        
        # ... do work ...
        
        client.disconnect()
        ```
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 30010,
        reconnect_attempts: int = 10,
        reconnect_delay: int = 2,
        ping_interval: int = 30,
    ):
        """
        Initialize WebSocket event client.
        
        Args:
            host: Unreal Engine host address
            port: Remote Control API port
            reconnect_attempts: Number of reconnection attempts
            reconnect_delay: Delay between reconnection attempts (seconds)
            ping_interval: Interval for ping messages (seconds)
        """
        self.host = host
        self.port = port
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay
        self.ping_interval = ping_interval
        
        self.ws_url = f"ws://{host}:{port}/remote/control/ws"
        self.ws: Optional[websocket.WebSocketApp] = None
        self.ws_thread: Optional[threading.Thread] = None
        
        self.event_handlers: Dict[EventType, List[Callable]] = {
            event_type: [] for event_type in EventType
        }
        
        self.is_connected = False
        self.should_reconnect = True
        self.connection_established = threading.Event()
        
        logger.info(f"Initialized WebSocket client: {self.ws_url}")
    
    def add_event_handler(self, event_type: EventType, handler: Callable):
        """
        Add an event handler for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler: Callback function that takes event data as parameter
        """
        if handler not in self.event_handlers[event_type]:
            self.event_handlers[event_type].append(handler)
            logger.debug(f"Added handler for {event_type.value}")
    
    def remove_event_handler(self, event_type: EventType, handler: Callable):
        """
        Remove an event handler.
        
        Args:
            event_type: Type of event
            handler: Handler to remove
        """
        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            logger.debug(f"Removed handler for {event_type.value}")
    
    def _trigger_event(self, event_type: EventType, data: Dict[str, Any]):
        """
        Trigger all handlers for an event type.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type.value}: {e}")
    
    def _on_open(self, ws):
        """WebSocket connection opened."""
        self.is_connected = True
        self.connection_established.set()
        logger.info("WebSocket connection established")
        self._trigger_event(EventType.CONNECTION_STATUS, {
            "status": "connected",
            "timestamp": datetime.now().isoformat(),
        })
    
    def _on_message(self, ws, message: str):
        """WebSocket message received."""
        try:
            data = json.loads(message)
            
            # Determine event type from message
            event_type = self._parse_event_type(data)
            
            # Trigger appropriate handlers
            self._trigger_event(event_type, data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse WebSocket message: {e}")
            self._trigger_event(EventType.ERROR, {
                "error": "json_decode_error",
                "message": str(e),
            })
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            self._trigger_event(EventType.ERROR, {
                "error": "message_handler_error",
                "message": str(e),
            })
    
    def _on_error(self, ws, error):
        """WebSocket error occurred."""
        logger.error(f"WebSocket error: {error}")
        self._trigger_event(EventType.ERROR, {
            "error": "websocket_error",
            "message": str(error),
            "timestamp": datetime.now().isoformat(),
        })
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket connection closed."""
        self.is_connected = False
        logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")
        
        self._trigger_event(EventType.CONNECTION_STATUS, {
            "status": "disconnected",
            "code": close_status_code,
            "message": close_msg,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Attempt reconnection if enabled
        if self.should_reconnect:
            self._reconnect()
    
    def _parse_event_type(self, data: Dict[str, Any]) -> EventType:
        """
        Parse event type from message data.
        
        Args:
            data: Message data
            
        Returns:
            EventType enum value
        """
        # This is a simplified version - actual implementation depends on
        # the specific message format from Unreal Engine
        event_name = data.get("type", "").lower()
        
        if "property" in event_name:
            return EventType.PROPERTY_CHANGED
        elif "function" in event_name:
            return EventType.FUNCTION_CALLED
        elif "preset" in event_name:
            return EventType.PRESET_CHANGED
        elif "error" in event_name:
            return EventType.ERROR
        else:
            return EventType.CONNECTION_STATUS
    
    def _reconnect(self):
        """Attempt to reconnect with exponential backoff."""
        for attempt in range(self.reconnect_attempts):
            if not self.should_reconnect:
                break
            
            delay = self.reconnect_delay * (2 ** attempt)
            logger.info(f"Reconnection attempt {attempt + 1}/{self.reconnect_attempts} in {delay}s")
            time.sleep(delay)
            
            try:
                self.connect()
                logger.info("Reconnection successful")
                return
            except Exception as e:
                logger.error(f"Reconnection attempt {attempt + 1} failed: {e}")
        
        logger.error("All reconnection attempts failed")
    
    def connect(self):
        """
        Establish WebSocket connection to Unreal Engine.
        
        Raises:
            RemoteControlError: If connection fails
        """
        if self.is_connected:
            logger.warning("Already connected")
            return
        
        try:
            # Create WebSocket application
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
            )
            
            # Run WebSocket in separate thread
            self.ws_thread = threading.Thread(
                target=self.ws.run_forever,
                kwargs={"ping_interval": self.ping_interval},
                daemon=True,
            )
            self.ws_thread.start()
            
            # Wait for connection with timeout
            if not self.connection_established.wait(timeout=5):
                raise RemoteControlError("Failed to establish WebSocket connection")
            
            logger.info("WebSocket connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect WebSocket: {e}")
            raise RemoteControlError(f"WebSocket connection failed: {e}")
    
    def disconnect(self):
        """Disconnect WebSocket connection."""
        self.should_reconnect = False
        
        if self.ws:
            self.ws.close()
            logger.info("WebSocket disconnected")
        
        if self.ws_thread and self.ws_thread.is_alive():
            self.ws_thread.join(timeout=5)
        
        self.is_connected = False
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
