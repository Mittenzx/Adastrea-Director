"""
Tests for WebSocket event client.

These tests use mocking to avoid requiring a running Unreal Engine instance.
"""

import pytest
from unittest.mock import Mock, patch

from remote_control.websocket_client import WebSocketEventClient, EventType


class TestWebSocketEventClient:
    """Test suite for WebSocketEventClient."""
    
    @pytest.fixture
    def client(self):
        """Create a test WebSocket client."""
        return WebSocketEventClient(
            host="localhost",
            port=30010,
            reconnect_attempts=2,
            reconnect_delay=1,
        )
    
    def test_client_initialization(self, client):
        """Test client is initialized correctly."""
        assert client.host == "localhost"
        assert client.port == 30010
        assert client.ws_url == "ws://localhost:30010/remote/control/ws"
        assert client.reconnect_attempts == 2
        assert client.reconnect_delay == 1
        assert client.is_connected is False
    
    def test_add_event_handler(self, client):
        """Test adding an event handler."""
        handler = Mock()
        
        client.add_event_handler(EventType.PROPERTY_CHANGED, handler)
        
        assert handler in client.event_handlers[EventType.PROPERTY_CHANGED]
    
    def test_remove_event_handler(self, client):
        """Test removing an event handler."""
        handler = Mock()
        
        client.add_event_handler(EventType.PROPERTY_CHANGED, handler)
        client.remove_event_handler(EventType.PROPERTY_CHANGED, handler)
        
        assert handler not in client.event_handlers[EventType.PROPERTY_CHANGED]
    
    def test_trigger_event(self, client):
        """Test event handlers are triggered."""
        handler = Mock()
        event_data = {"property": "Health", "value": 100}
        
        client.add_event_handler(EventType.PROPERTY_CHANGED, handler)
        client._trigger_event(EventType.PROPERTY_CHANGED, event_data)
        
        handler.assert_called_once_with(event_data)
    
    def test_trigger_event_with_exception(self, client):
        """Test event triggering handles exceptions in handlers."""
        handler = Mock(side_effect=Exception("Handler error"))
        event_data = {"property": "Health", "value": 100}
        
        client.add_event_handler(EventType.PROPERTY_CHANGED, handler)
        
        # Should not raise exception
        client._trigger_event(EventType.PROPERTY_CHANGED, event_data)
        
        handler.assert_called_once()
    
    def test_parse_event_type_property(self, client):
        """Test parsing property change events."""
        data = {"type": "property_changed"}
        
        event_type = client._parse_event_type(data)
        
        assert event_type == EventType.PROPERTY_CHANGED
    
    def test_parse_event_type_function(self, client):
        """Test parsing function call events."""
        data = {"type": "function_called"}
        
        event_type = client._parse_event_type(data)
        
        assert event_type == EventType.FUNCTION_CALLED
    
    def test_parse_event_type_error(self, client):
        """Test parsing error events."""
        data = {"type": "error"}
        
        event_type = client._parse_event_type(data)
        
        assert event_type == EventType.ERROR
    
    def test_parse_event_type_unknown(self, client):
        """Test parsing unknown events."""
        data = {"type": "unknown"}
        
        event_type = client._parse_event_type(data)
        
        assert event_type == EventType.CONNECTION_STATUS
    
    @patch('websocket.WebSocketApp')
    def test_on_open(self, mock_ws_app, client):
        """Test WebSocket open handler."""
        handler = Mock()
        client.add_event_handler(EventType.CONNECTION_STATUS, handler)
        
        client._on_open(None)
        
        assert client.is_connected is True
        handler.assert_called_once()
        call_args = handler.call_args[0][0]
        assert call_args["status"] == "connected"
    
    @patch('websocket.WebSocketApp')
    def test_on_message_valid_json(self, mock_ws_app, client):
        """Test WebSocket message handler with valid JSON."""
        handler = Mock()
        client.add_event_handler(EventType.PROPERTY_CHANGED, handler)
        
        message = '{"type": "property_changed", "property": "Health", "value": 100}'
        
        client._on_message(None, message)
        
        handler.assert_called_once()
        call_args = handler.call_args[0][0]
        assert call_args["property"] == "Health"
        assert call_args["value"] == 100
    
    @patch('websocket.WebSocketApp')
    def test_on_message_invalid_json(self, mock_ws_app, client):
        """Test WebSocket message handler with invalid JSON."""
        error_handler = Mock()
        client.add_event_handler(EventType.ERROR, error_handler)
        
        message = 'invalid json{'
        
        client._on_message(None, message)
        
        error_handler.assert_called_once()
        call_args = error_handler.call_args[0][0]
        assert call_args["error"] == "json_decode_error"
    
    @patch('websocket.WebSocketApp')
    def test_on_error(self, mock_ws_app, client):
        """Test WebSocket error handler."""
        handler = Mock()
        client.add_event_handler(EventType.ERROR, handler)
        
        error = Exception("WebSocket error")
        
        client._on_error(None, error)
        
        handler.assert_called_once()
        call_args = handler.call_args[0][0]
        assert call_args["error"] == "websocket_error"
    
    @patch('websocket.WebSocketApp')
    def test_on_close(self, mock_ws_app, client):
        """Test WebSocket close handler."""
        handler = Mock()
        client.add_event_handler(EventType.CONNECTION_STATUS, handler)
        client.is_connected = True
        client.should_reconnect = False  # Disable reconnection for test
        
        client._on_close(None, 1000, "Normal closure")
        
        assert client.is_connected is False
        handler.assert_called_once()
        call_args = handler.call_args[0][0]
        assert call_args["status"] == "disconnected"
    
    @patch('websocket.WebSocketApp')
    @patch('threading.Thread')
    def test_connect_success(self, mock_thread, mock_ws_app, client):
        """Test successful WebSocket connection."""
        # Mock WebSocket connection
        mock_ws_instance = Mock()
        mock_ws_app.return_value = mock_ws_instance
        
        # Mock thread
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        # Simulate connection after thread start
        def set_connected(*args, **kwargs):
            client.is_connected = True
            client.connection_established.set()
        
        mock_thread_instance.start.side_effect = set_connected
        
        client.connect()
        
        mock_ws_app.assert_called_once()
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
    
    def test_connect_already_connected(self, client):
        """Test connecting when already connected."""
        client.is_connected = True
        
        # Should not raise exception
        client.connect()
    
    @patch('websocket.WebSocketApp')
    def test_disconnect(self, mock_ws_app, client):
        """Test disconnecting WebSocket."""
        mock_ws_instance = Mock()
        client.ws = mock_ws_instance
        client.is_connected = True
        
        client.disconnect()
        
        assert client.should_reconnect is False
        mock_ws_instance.close.assert_called_once()
        assert client.is_connected is False
    
    @patch('websocket.WebSocketApp')
    @patch('threading.Thread')
    def test_context_manager(self, mock_thread, mock_ws_app, client):
        """Test client can be used as context manager."""
        mock_ws_instance = Mock()
        mock_ws_app.return_value = mock_ws_instance
        client.ws = mock_ws_instance
        
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        # Simulate connection
        def set_connected(*args, **kwargs):
            client.is_connected = True
            client.connection_established.set()
        
        mock_thread_instance.start.side_effect = set_connected
        
        with client as c:
            assert c is client
        
        mock_ws_instance.close.assert_called_once()


class TestEventType:
    """Test EventType enum."""
    
    def test_event_types_exist(self):
        """Test all event types are defined."""
        assert EventType.PROPERTY_CHANGED is not None
        assert EventType.FUNCTION_CALLED is not None
        assert EventType.PRESET_CHANGED is not None
        assert EventType.CONNECTION_STATUS is not None
        assert EventType.ERROR is not None
    
    def test_event_type_values(self):
        """Test event type values."""
        assert EventType.PROPERTY_CHANGED.value == "property_changed"
        assert EventType.FUNCTION_CALLED.value == "function_called"
        assert EventType.ERROR.value == "error"
