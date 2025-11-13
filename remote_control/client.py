"""
Unreal Engine Remote Control API Client.

This module provides the core HTTP client for interacting with the
Unreal Engine Remote Control API.
"""

import requests
import logging
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

from .models import (
    PropertyUpdate,
    FunctionCall,
    ConsoleCommand,
    RemoteControlResponse,
    RemoteControlError,
    ConnectionError,
    RequestError,
    TimeoutError,
    ValidationError,
    PerformanceMetrics,
    AssetInfo,
)

logger = logging.getLogger(__name__)


class UnrealRemoteControlClient:
    """
    Python client for Unreal Engine Remote Control API.
    
    Provides methods to interact with Unreal Engine projects via HTTP/REST API,
    enabling agents to control properties, execute functions, and run console commands.
    
    Example:
        ```python
        client = UnrealRemoteControlClient(host="localhost", port=30010)
        
        # Check connection
        if client.health_check():
            # Execute console command
            result = client.execute_command("stat fps")
            print(result.data)
            
            # Set property
            client.set_property(
                object_path="/Game/MyBlueprint.MyBlueprint_C",
                property_name="Speed",
                value=100.0
            )
        ```
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 30010,
        timeout: int = 30,
        retry_attempts: int = 3,
        retry_delay: int = 5,
        verify_ssl: bool = False,
    ):
        """
        Initialize the Remote Control client.
        
        Args:
            host: Unreal Engine host address
            port: Remote Control API port
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
            retry_delay: Delay between retries in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl
        
        self.base_url = f"http://{host}:{port}/remote/control"
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        
        logger.info(f"Initialized Remote Control client: {self.base_url}")
    
    def health_check(self) -> bool:
        """
        Check if connection to Unreal Engine is healthy.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = self.session.get(
                f"http://{self.host}:{self.port}/remote/control/api",
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            response.raise_for_status()
            logger.info("Health check passed")
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> RemoteControlResponse:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, PUT, POST, etc.)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            
        Returns:
            RemoteControlResponse object
            
        Raises:
            ConnectionError: If connection fails
            RequestError: If request fails
            TimeoutError: If request times out
        """
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.retry_attempts):
            try:
                logger.debug(f"Request {method} {url} (attempt {attempt + 1}/{self.retry_attempts})")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    timeout=self.timeout,
                    verify=self.verify_ssl,
                )
                
                response.raise_for_status()
                
                result_data = response.json() if response.text else None
                
                return RemoteControlResponse(
                    success=True,
                    data=result_data,
                    timestamp=datetime.now(),
                )
                
            except requests.exceptions.Timeout as e:
                if attempt == self.retry_attempts - 1:
                    raise TimeoutError(f"Request timed out after {self.retry_attempts} attempts: {e}")
                logger.warning(f"Request timed out, retrying in {self.retry_delay}s...")
                time.sleep(self.retry_delay)
                
            except requests.exceptions.ConnectionError as e:
                if attempt == self.retry_attempts - 1:
                    raise ConnectionError(f"Failed to connect to Unreal Engine: {e}")
                logger.warning(f"Connection failed, retrying in {self.retry_delay}s...")
                time.sleep(self.retry_delay)
                
            except requests.exceptions.RequestException as e:
                raise RequestError(f"Request failed: {e}")
        
        raise RequestError("Failed to complete request after all retry attempts")
    
    def get_property(self, object_path: str, property_name: str) -> RemoteControlResponse:
        """
        Get a property value from an Unreal Engine object.
        
        Args:
            object_path: Full path to the object (e.g., "/Game/MyBlueprint.MyBlueprint_C")
            property_name: Name of the property to get
            
        Returns:
            RemoteControlResponse containing the property value
            
        Example:
            ```python
            response = client.get_property(
                "/Game/Player.Player_C",
                "Health"
            )
            print(f"Health: {response.data['PropertyValue']}")
            ```
        """
        if not object_path or not property_name:
            raise ValidationError("object_path and property_name are required")
        
        response = self._make_request(
            method="GET",
            endpoint="object/property",
            params={
                "objectPath": object_path,
                "propertyName": property_name,
            },
        )
        
        logger.info(f"Got property {property_name} from {object_path}")
        return response
    
    def set_property(
        self,
        object_path: str,
        property_name: str,
        value: Any,
    ) -> RemoteControlResponse:
        """
        Set a property value on an Unreal Engine object.
        
        Args:
            object_path: Full path to the object
            property_name: Name of the property to set
            value: New value for the property
            
        Returns:
            RemoteControlResponse indicating success
            
        Example:
            ```python
            client.set_property(
                "/Game/Player.Player_C",
                "Health",
                100.0
            )
            ```
        """
        if not object_path or not property_name:
            raise ValidationError("object_path and property_name are required")
        
        update = PropertyUpdate(
            object_path=object_path,
            property_name=property_name,
            property_value=value,
        )
        
        response = self._make_request(
            method="PUT",
            endpoint="object/property",
            data=update.to_dict(),
        )
        
        logger.info(f"Set property {property_name} on {object_path} to {value}")
        return response
    
    def call_function(
        self,
        object_path: str,
        function_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        generate_transaction: bool = False,
    ) -> RemoteControlResponse:
        """
        Call a function on an Unreal Engine object.
        
        Args:
            object_path: Full path to the object
            function_name: Name of the function to call
            parameters: Function parameters as a dictionary
            generate_transaction: Whether to generate an undo transaction
            
        Returns:
            RemoteControlResponse containing function return value
            
        Example:
            ```python
            client.call_function(
                "/Game/MyActor.MyActor_C",
                "TakeDamage",
                parameters={"Amount": 10.0}
            )
            ```
        """
        if not object_path or not function_name:
            raise ValidationError("object_path and function_name are required")
        
        func_call = FunctionCall(
            object_path=object_path,
            function_name=function_name,
            parameters=parameters or {},
            generate_transaction=generate_transaction,
        )
        
        response = self._make_request(
            method="PUT",
            endpoint="function",
            data=func_call.to_dict(),
        )
        
        logger.info(f"Called function {function_name} on {object_path}")
        return response
    
    def execute_command(self, command: str) -> RemoteControlResponse:
        """
        Execute a console command in Unreal Engine.
        
        Args:
            command: Console command to execute (e.g., "stat fps")
            
        Returns:
            RemoteControlResponse containing command output
            
        Example:
            ```python
            result = client.execute_command("stat fps")
            print(result.data)
            ```
        """
        if not command:
            raise ValidationError("command is required")
        
        cmd = ConsoleCommand(command=command)
        
        response = self._make_request(
            method="PUT",
            endpoint="command",
            data=cmd.to_dict(),
        )
        
        logger.info(f"Executed console command: {command}")
        return response
    
    def list_presets(self) -> RemoteControlResponse:
        """
        List all available Remote Control presets.
        
        Returns:
            RemoteControlResponse containing list of presets
        """
        response = self._make_request(
            method="GET",
            endpoint="presets",
        )
        
        logger.info("Retrieved presets list")
        return response
    
    def get_preset(self, preset_name: str) -> RemoteControlResponse:
        """
        Get details of a specific Remote Control preset.
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            RemoteControlResponse containing preset details
        """
        if not preset_name:
            raise ValidationError("preset_name is required")
        
        response = self._make_request(
            method="GET",
            endpoint=f"preset/{preset_name}",
        )
        
        logger.info(f"Retrieved preset: {preset_name}")
        return response
    
    def close(self):
        """Close the client session."""
        self.session.close()
        logger.info("Remote Control client closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
