"""
Tests for RemoteControlAgent base class.
"""

import pytest
from unittest.mock import Mock, patch

from remote_control.base_agent import RemoteControlAgent
from remote_control.models import RemoteControlError, RemoteControlResponse


class TestAgent(RemoteControlAgent):
    """Concrete test implementation of RemoteControlAgent."""
    
    def execute_task(self, task):
        """Execute a test task."""
        return {"result": "success", "task": task}


class TestRemoteControlAgent:
    """Test suite for RemoteControlAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        with patch('remote_control.base_agent.UnrealRemoteControlClient'):
            agent = TestAgent(
                agent_id="test_agent",
                ue_host="localhost",
                ue_port=30010,
                enable_websocket=False,
            )
            return agent
    
    def test_agent_initialization(self, agent):
        """Test agent is initialized correctly."""
        assert agent.agent_id == "test_agent"
        assert agent.ue_host == "localhost"
        assert agent.ue_port == 30010
        assert agent.is_running is False
        assert agent.remote_control is not None
    
    def test_agent_initialization_with_websocket(self):
        """Test agent initialization with WebSocket enabled."""
        with patch('remote_control.base_agent.UnrealRemoteControlClient'):
            with patch('remote_control.base_agent.WebSocketEventClient'):
                agent = TestAgent(
                    agent_id="test_agent",
                    enable_websocket=True
                )
                assert agent.websocket is not None
    
    @patch('remote_control.base_agent.UnrealRemoteControlClient')
    def test_start_success(self, mock_client_class, agent):
        """Test successful agent start."""
        # Mock health check
        agent.remote_control.health_check = Mock(return_value=True)
        
        result = agent.start()
        
        assert result is True
        assert agent.is_running is True
        agent.remote_control.health_check.assert_called_once()
    
    @patch('remote_control.base_agent.UnrealRemoteControlClient')
    def test_start_failure_connection(self, mock_client_class, agent):
        """Test agent start fails when connection fails."""
        # Mock health check failure
        agent.remote_control.health_check = Mock(return_value=False)
        
        with pytest.raises(RemoteControlError):
            agent.start()
        
        assert agent.is_running is False
    
    @patch('remote_control.base_agent.UnrealRemoteControlClient')
    def test_start_already_running(self, mock_client_class, agent):
        """Test starting agent that is already running."""
        agent.is_running = True
        
        result = agent.start()
        
        assert result is True
        assert agent.is_running is True
    
    @patch('remote_control.base_agent.UnrealRemoteControlClient')
    def test_start_with_websocket(self, mock_client_class):
        """Test agent start with WebSocket enabled."""
        with patch('remote_control.base_agent.WebSocketEventClient') as mock_ws_class:
            agent = TestAgent(
                agent_id="test_agent",
                enable_websocket=True
            )
            
            # Mock health check and WebSocket connect
            agent.remote_control.health_check = Mock(return_value=True)
            mock_ws_instance = Mock()
            agent.websocket = mock_ws_instance
            
            agent.start()
            
            assert agent.is_running is True
            mock_ws_instance.connect.assert_called_once()
    
    def test_stop(self, agent):
        """Test stopping the agent."""
        agent.is_running = True
        agent.remote_control.close = Mock()
        
        agent.stop()
        
        assert agent.is_running is False
        agent.remote_control.close.assert_called_once()
    
    def test_stop_with_websocket(self):
        """Test stopping agent with WebSocket."""
        with patch('remote_control.base_agent.UnrealRemoteControlClient'):
            with patch('remote_control.base_agent.WebSocketEventClient'):
                agent = TestAgent(
                    agent_id="test_agent",
                    enable_websocket=True
                )
                agent.is_running = True
                agent.websocket = Mock()
                agent.remote_control.close = Mock()
                
                agent.stop()
                
                agent.websocket.disconnect.assert_called_once()
                agent.remote_control.close.assert_called_once()
    
    def test_execute_task(self, agent):
        """Test executing a task."""
        result = agent.execute_task("test_task")
        
        assert result["result"] == "success"
        assert result["task"] == "test_task"
    
    def test_is_connected(self, agent):
        """Test connection status check."""
        agent.is_running = True
        agent.remote_control.health_check = Mock(return_value=True)
        
        assert agent.is_connected() is True
        
        agent.remote_control.health_check = Mock(return_value=False)
        assert agent.is_connected() is False
        
        agent.is_running = False
        assert agent.is_connected() is False
    
    def test_execute_command_success(self, agent):
        """Test executing a console command."""
        mock_response = RemoteControlResponse(
            success=True,
            data={"output": "FPS: 60"}
        )
        agent.remote_control.execute_command = Mock(return_value=mock_response)
        
        result = agent.execute_command("stat fps")
        
        assert result == {"output": "FPS: 60"}
    
    def test_execute_command_failure(self, agent):
        """Test executing a console command that fails."""
        mock_response = RemoteControlResponse(
            success=False,
            error="Command failed"
        )
        agent.remote_control.execute_command = Mock(return_value=mock_response)
        
        with pytest.raises(RemoteControlError):
            agent.execute_command("invalid command")
    
    def test_get_property_success(self, agent):
        """Test getting a property value."""
        mock_response = RemoteControlResponse(
            success=True,
            data={"PropertyValue": 100.0}
        )
        agent.remote_control.get_property = Mock(return_value=mock_response)
        
        value = agent.get_property("/Game/MyActor", "Health")
        
        assert value == 100.0
    
    def test_get_property_failure(self, agent):
        """Test getting a property value that fails."""
        mock_response = RemoteControlResponse(
            success=False,
            error="Property not found"
        )
        agent.remote_control.get_property = Mock(return_value=mock_response)
        
        with pytest.raises(RemoteControlError):
            agent.get_property("/Game/MyActor", "InvalidProperty")
    
    def test_set_property_success(self, agent):
        """Test setting a property value."""
        mock_response = RemoteControlResponse(success=True)
        agent.remote_control.set_property = Mock(return_value=mock_response)
        
        # Should not raise exception
        agent.set_property("/Game/MyActor", "Health", 75.0)
        
        agent.remote_control.set_property.assert_called_once_with(
            "/Game/MyActor", "Health", 75.0
        )
    
    def test_set_property_failure(self, agent):
        """Test setting a property value that fails."""
        mock_response = RemoteControlResponse(
            success=False,
            error="Property is read-only"
        )
        agent.remote_control.set_property = Mock(return_value=mock_response)
        
        with pytest.raises(RemoteControlError):
            agent.set_property("/Game/MyActor", "ReadOnlyProperty", 100)
    
    def test_call_function_success(self, agent):
        """Test calling a function."""
        mock_response = RemoteControlResponse(
            success=True,
            data={"ReturnValue": True}
        )
        agent.remote_control.call_function = Mock(return_value=mock_response)
        
        result = agent.call_function(
            "/Game/MyActor",
            "TakeDamage",
            {"Amount": 10.0}
        )
        
        assert result == {"ReturnValue": True}
    
    def test_call_function_failure(self, agent):
        """Test calling a function that fails."""
        mock_response = RemoteControlResponse(
            success=False,
            error="Function not found"
        )
        agent.remote_control.call_function = Mock(return_value=mock_response)
        
        with pytest.raises(RemoteControlError):
            agent.call_function("/Game/MyActor", "InvalidFunction")
    
    def test_context_manager(self):
        """Test agent can be used as context manager."""
        with patch('remote_control.base_agent.UnrealRemoteControlClient'):
            agent = TestAgent(agent_id="test_agent")
            agent.remote_control.health_check = Mock(return_value=True)
            agent.remote_control.close = Mock()
            
            with agent as a:
                assert a is agent
                assert a.is_running is True
            
            assert agent.is_running is False
            agent.remote_control.close.assert_called_once()
    
    def test_event_handlers_setup(self):
        """Test WebSocket event handlers are set up correctly."""
        with patch('remote_control.base_agent.UnrealRemoteControlClient'):
            with patch('remote_control.base_agent.WebSocketEventClient'):
                agent = TestAgent(
                    agent_id="test_agent",
                    enable_websocket=True
                )
                
                agent.websocket = Mock()
                agent._setup_event_handlers()
                
                # Verify handlers were added
                assert agent.websocket.add_event_handler.call_count == 2
    
    def test_on_connection_status(self, agent):
        """Test connection status event handler."""
        event = {"status": "connected"}
        
        # Should not raise exception
        agent._on_connection_status(event)
    
    def test_on_error(self, agent):
        """Test error event handler."""
        event = {"message": "Test error"}
        
        # Should not raise exception
        agent._on_error(event)


class TestAbstractMethods:
    """Test that abstract methods are enforced."""
    
    def test_cannot_instantiate_base_class(self):
        """Test that RemoteControlAgent cannot be instantiated directly."""
        with pytest.raises(TypeError):
            RemoteControlAgent(agent_id="test")
