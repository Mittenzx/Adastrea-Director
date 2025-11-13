"""
Tests for Remote Control API client.

These tests use mocking to avoid requiring a running Unreal Engine instance.
"""

import pytest
from unittest.mock import Mock, patch

from remote_control.client import UnrealRemoteControlClient
from remote_control.models import (
    PropertyUpdate,
    FunctionCall,
    ConsoleCommand,
    RemoteControlResponse,
    ValidationError,
    TimeoutError,
)


class TestUnrealRemoteControlClient:
    """Test suite for UnrealRemoteControlClient."""
    
    @pytest.fixture
    def client(self):
        """Create a test client instance."""
        return UnrealRemoteControlClient(
            host="localhost",
            port=30010,
            timeout=10,
            retry_attempts=2,
        )
    
    @pytest.fixture
    def mock_response(self):
        """Create a mock HTTP response."""
        mock = Mock()
        mock.status_code = 200
        mock.text = '{"success": true, "data": {"value": 100}}'
        mock.json.return_value = {"success": True, "data": {"value": 100}}
        mock.raise_for_status = Mock()
        return mock
    
    def test_client_initialization(self, client):
        """Test client is initialized correctly."""
        assert client.host == "localhost"
        assert client.port == 30010
        assert client.base_url == "http://localhost:30010/remote/control"
        assert client.timeout == 10
        assert client.retry_attempts == 2
    
    @patch('requests.Session.get')
    def test_health_check_success(self, mock_get, client, mock_response):
        """Test successful health check."""
        mock_get.return_value = mock_response
        
        result = client.health_check()
        
        assert result is True
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_health_check_failure(self, mock_get, client):
        """Test failed health check."""
        mock_get.side_effect = Exception("Connection failed")
        
        result = client.health_check()
        
        assert result is False
    
    @patch('requests.Session.request')
    def test_get_property_success(self, mock_request, client, mock_response):
        """Test getting a property value."""
        mock_response.json.return_value = {"PropertyValue": 100.0}
        mock_request.return_value = mock_response
        
        response = client.get_property(
            object_path="/Game/MyActor.MyActor_C",
            property_name="Health"
        )
        
        assert response.success is True
        assert response.data["PropertyValue"] == 100.0
        mock_request.assert_called_once()
    
    def test_get_property_validation(self, client):
        """Test get_property validates inputs."""
        with pytest.raises(ValidationError):
            client.get_property("", "Health")
        
        with pytest.raises(ValidationError):
            client.get_property("/Game/MyActor", "")
    
    @patch('requests.Session.request')
    def test_set_property_success(self, mock_request, client, mock_response):
        """Test setting a property value."""
        mock_request.return_value = mock_response
        
        response = client.set_property(
            object_path="/Game/MyActor.MyActor_C",
            property_name="Health",
            value=75.0
        )
        
        assert response.success is True
        mock_request.assert_called_once()
        
        # Verify request payload
        call_args = mock_request.call_args
        payload = call_args.kwargs['json']
        assert payload['objectPath'] == "/Game/MyActor.MyActor_C"
        assert payload['propertyName'] == "Health"
        assert payload['propertyValue'] == 75.0
    
    def test_set_property_validation(self, client):
        """Test set_property validates inputs."""
        with pytest.raises(ValidationError):
            client.set_property("", "Health", 100)
        
        with pytest.raises(ValidationError):
            client.set_property("/Game/MyActor", "", 100)
    
    @patch('requests.Session.request')
    def test_call_function_success(self, mock_request, client, mock_response):
        """Test calling a function."""
        mock_response.json.return_value = {"ReturnValue": True}
        mock_request.return_value = mock_response
        
        response = client.call_function(
            object_path="/Game/MyActor.MyActor_C",
            function_name="TakeDamage",
            parameters={"Amount": 10.0}
        )
        
        assert response.success is True
        assert response.data["ReturnValue"] is True
        
        # Verify request payload
        call_args = mock_request.call_args
        payload = call_args.kwargs['json']
        assert payload['objectPath'] == "/Game/MyActor.MyActor_C"
        assert payload['functionName'] == "TakeDamage"
        assert payload['parameters'] == {"Amount": 10.0}
    
    def test_call_function_validation(self, client):
        """Test call_function validates inputs."""
        with pytest.raises(ValidationError):
            client.call_function("", "MyFunction")
        
        with pytest.raises(ValidationError):
            client.call_function("/Game/MyActor", "")
    
    @patch('requests.Session.request')
    def test_execute_command_success(self, mock_request, client, mock_response):
        """Test executing a console command."""
        mock_response.json.return_value = {"output": "FPS: 60"}
        mock_request.return_value = mock_response
        
        response = client.execute_command("stat fps")
        
        assert response.success is True
        assert "FPS" in response.data["output"]
        
        # Verify request payload
        call_args = mock_request.call_args
        payload = call_args.kwargs['json']
        assert payload['command'] == "stat fps"
    
    def test_execute_command_validation(self, client):
        """Test execute_command validates inputs."""
        with pytest.raises(ValidationError):
            client.execute_command("")
    
    @patch('requests.Session.request')
    def test_request_retry_on_timeout(self, mock_request, client):
        """Test that requests are retried on timeout."""
        import requests as req
        mock_request.side_effect = [
            req.exceptions.Timeout("Timeout"),
            Mock(status_code=200, json=lambda: {}, text="", raise_for_status=Mock())
        ]
        
        # Should succeed on second attempt
        with patch('time.sleep'):  # Mock sleep to speed up test
            response = client._make_request("GET", "test")
            assert response.success is True
    
    @patch('requests.Session.request')
    def test_request_failure_after_retries(self, mock_request, client):
        """Test that RequestError is raised after all retries fail."""
        import requests
        mock_request.side_effect = requests.exceptions.Timeout("Timeout")
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            with pytest.raises(TimeoutError):
                client._make_request("GET", "test")
    
    @patch('requests.Session.request')
    def test_list_presets(self, mock_request, client, mock_response):
        """Test listing presets."""
        mock_response.json.return_value = {"presets": ["Preset1", "Preset2"]}
        mock_request.return_value = mock_response
        
        response = client.list_presets()
        
        assert response.success is True
        assert len(response.data["presets"]) == 2
    
    @patch('requests.Session.request')
    def test_get_preset(self, mock_request, client, mock_response):
        """Test getting a specific preset."""
        mock_response.json.return_value = {"name": "MyPreset", "properties": []}
        mock_request.return_value = mock_response
        
        response = client.get_preset("MyPreset")
        
        assert response.success is True
        assert response.data["name"] == "MyPreset"
    
    def test_context_manager(self, client):
        """Test client can be used as context manager."""
        with patch.object(client, 'close') as mock_close:
            with client as c:
                assert c is client
            mock_close.assert_called_once()
    
    def test_close(self, client):
        """Test closing the client."""
        client.close()
        # Session should be closed (no exception means success)


class TestPropertyUpdate:
    """Test PropertyUpdate model."""
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        update = PropertyUpdate(
            object_path="/Game/MyActor",
            property_name="Health",
            property_value=100.0
        )
        
        result = update.to_dict()
        
        assert result["objectPath"] == "/Game/MyActor"
        assert result["propertyName"] == "Health"
        assert result["propertyValue"] == 100.0


class TestFunctionCall:
    """Test FunctionCall model."""
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        call = FunctionCall(
            object_path="/Game/MyActor",
            function_name="MyFunction",
            parameters={"param1": 10},
            generate_transaction=True
        )
        
        result = call.to_dict()
        
        assert result["objectPath"] == "/Game/MyActor"
        assert result["functionName"] == "MyFunction"
        assert result["parameters"] == {"param1": 10}
        assert result["generateTransaction"] is True
    
    def test_default_parameters(self):
        """Test default parameters."""
        call = FunctionCall(
            object_path="/Game/MyActor",
            function_name="MyFunction"
        )
        
        result = call.to_dict()
        assert result["parameters"] == {}
        assert result["generateTransaction"] is False


class TestConsoleCommand:
    """Test ConsoleCommand model."""
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        cmd = ConsoleCommand(command="stat fps")
        
        result = cmd.to_dict()
        
        assert result["command"] == "stat fps"


class TestRemoteControlResponse:
    """Test RemoteControlResponse model."""
    
    def test_is_error_with_error_message(self):
        """Test is_error when error is present."""
        response = RemoteControlResponse(
            success=True,
            error="Something went wrong"
        )
        
        assert response.is_error is True
    
    def test_is_error_when_not_successful(self):
        """Test is_error when success is False."""
        response = RemoteControlResponse(success=False)
        
        assert response.is_error is True
    
    def test_is_not_error_on_success(self):
        """Test is_error when successful."""
        response = RemoteControlResponse(
            success=True,
            data={"value": 100}
        )
        
        assert response.is_error is False
