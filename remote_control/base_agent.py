"""
Base agent class for agents that use Remote Control API.

This module provides a base class that combines Phase 3 autonomous agent
functionality with Remote Control API access.
"""

import logging
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

from .client import UnrealRemoteControlClient
from .websocket_client import WebSocketEventClient, EventType
from .models import RemoteControlError

logger = logging.getLogger(__name__)


class RemoteControlAgent(ABC):
    """
    Base class for agents that interact with Unreal Engine via Remote Control API.
    
    This class combines the autonomous agent pattern from Phase 3 with
    Remote Control API functionality, providing a unified interface for
    agents that need to interact with Unreal Engine.
    
    Attributes:
        agent_id: Unique identifier for the agent
        remote_control: HTTP client for Remote Control API
        websocket: WebSocket client for real-time events (optional)
        
    Example:
        ```python
        class MyAgent(RemoteControlAgent):
            def execute_task(self, task):
                # Use remote_control to interact with UE
                response = self.remote_control.execute_command("stat fps")
                return self.process_response(response)
            
            def process_response(self, response):
                # Process the response
                return {"success": True}
        
        agent = MyAgent(
            agent_id="my_agent",
            ue_host="localhost",
            ue_port=30010
        )
        agent.start()
        # ... use agent ...
        agent.stop()
        ```
    """
    
    def __init__(
        self,
        agent_id: str,
        ue_host: str = "localhost",
        ue_port: int = 30010,
        enable_websocket: bool = False,
        timeout: int = 30,
        retry_attempts: int = 3,
    ):
        """
        Initialize the Remote Control agent.
        
        Args:
            agent_id: Unique identifier for this agent
            ue_host: Unreal Engine host address
            ue_port: Remote Control API port
            enable_websocket: Whether to enable WebSocket events
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
        """
        self.agent_id = agent_id
        self.ue_host = ue_host
        self.ue_port = ue_port
        self.enable_websocket = enable_websocket
        
        # Create Remote Control client
        self.remote_control = UnrealRemoteControlClient(
            host=ue_host,
            port=ue_port,
            timeout=timeout,
            retry_attempts=retry_attempts,
        )
        
        # Optionally create WebSocket client
        self.websocket: Optional[WebSocketEventClient] = None
        if enable_websocket:
            self.websocket = WebSocketEventClient(
                host=ue_host,
                port=ue_port,
            )
        
        self.is_running = False
        
        logger.info(f"Initialized {self.__class__.__name__} agent: {agent_id}")
    
    def start(self) -> bool:
        """
        Start the agent and establish connections.
        
        Returns:
            True if agent started successfully
            
        Raises:
            RemoteControlError: If connection fails
        """
        if self.is_running:
            logger.warning(f"Agent {self.agent_id} is already running")
            return True
        
        # Check connection
        logger.info(f"Starting agent {self.agent_id}...")
        if not self.remote_control.health_check():
            raise RemoteControlError(
                f"Failed to connect to Unreal Engine at {self.ue_host}:{self.ue_port}"
            )
        
        logger.info(f"✓ Connected to Unreal Engine")
        
        # Start WebSocket if enabled
        if self.websocket:
            try:
                self._setup_event_handlers()
                self.websocket.connect()
                logger.info(f"✓ WebSocket connected")
            except Exception as e:
                logger.warning(f"WebSocket connection failed: {e}")
                logger.warning("Continuing without WebSocket support")
        
        self.is_running = True
        logger.info(f"✓ Agent {self.agent_id} started successfully")
        
        return True
    
    def stop(self):
        """Stop the agent and close connections."""
        if not self.is_running:
            return
        
        logger.info(f"Stopping agent {self.agent_id}...")
        
        # Disconnect WebSocket
        if self.websocket:
            self.websocket.disconnect()
        
        # Close Remote Control client
        self.remote_control.close()
        
        self.is_running = False
        logger.info(f"✓ Agent {self.agent_id} stopped")
    
    def _setup_event_handlers(self):
        """
        Setup WebSocket event handlers.
        
        Subclasses can override this to add custom event handlers.
        """
        if not self.websocket:
            return
        
        # Default handlers
        self.websocket.add_event_handler(
            EventType.CONNECTION_STATUS,
            self._on_connection_status
        )
        self.websocket.add_event_handler(
            EventType.ERROR,
            self._on_error
        )
    
    def _on_connection_status(self, event):
        """Handle WebSocket connection status changes."""
        status = event.get('status', 'unknown')
        logger.info(f"Agent {self.agent_id} WebSocket status: {status}")
    
    def _on_error(self, event):
        """Handle WebSocket errors."""
        error = event.get('message', 'Unknown error')
        logger.error(f"Agent {self.agent_id} WebSocket error: {error}")
    
    @abstractmethod
    def execute_task(self, task: Any) -> Any:
        """
        Execute a task using Remote Control API.
        
        Subclasses must implement this method to define agent-specific
        task execution logic.
        
        Args:
            task: Task definition (agent-specific format)
            
        Returns:
            Task result (agent-specific format)
        """
        pass
    
    def is_connected(self) -> bool:
        """
        Check if agent is connected to Unreal Engine.
        
        Returns:
            True if connected and healthy
        """
        return self.is_running and self.remote_control.health_check()
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a console command in Unreal Engine.
        
        Args:
            command: Console command to execute
            
        Returns:
            Response data as dictionary
            
        Raises:
            RemoteControlError: If command fails
        """
        response = self.remote_control.execute_command(command)
        if response.is_error:
            raise RemoteControlError(f"Command failed: {response.error}")
        return response.data or {}
    
    def get_property(self, object_path: str, property_name: str) -> Any:
        """
        Get a property value from Unreal Engine object.
        
        Args:
            object_path: Full path to the object
            property_name: Name of the property
            
        Returns:
            Property value
            
        Raises:
            RemoteControlError: If operation fails
        """
        response = self.remote_control.get_property(object_path, property_name)
        if response.is_error:
            raise RemoteControlError(f"Failed to get property: {response.error}")
        return response.data.get('PropertyValue')
    
    def set_property(self, object_path: str, property_name: str, value: Any):
        """
        Set a property value on Unreal Engine object.
        
        Args:
            object_path: Full path to the object
            property_name: Name of the property
            value: New value for the property
            
        Raises:
            RemoteControlError: If operation fails
        """
        response = self.remote_control.set_property(object_path, property_name, value)
        if response.is_error:
            raise RemoteControlError(f"Failed to set property: {response.error}")
    
    def call_function(
        self,
        object_path: str,
        function_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Call a function on Unreal Engine object.
        
        Args:
            object_path: Full path to the object
            function_name: Name of the function
            parameters: Function parameters
            
        Returns:
            Function return value
            
        Raises:
            RemoteControlError: If operation fails
        """
        response = self.remote_control.call_function(
            object_path,
            function_name,
            parameters or {}
        )
        if response.is_error:
            raise RemoteControlError(f"Failed to call function: {response.error}")
        return response.data
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
