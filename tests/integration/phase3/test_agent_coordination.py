"""
Integration tests for Agent Coordination.

Tests how multiple Phase 3 agents work together through the event bus
and shared state system.
"""

import pytest
import time
from datetime import datetime
from typing import List

from agents.phase3.base_agent import BaseAutonomousAgent
from agents.phase3.event_bus import Event, EventBus, EventType
from agents.phase3.shared_state import SharedContext, AgentStatus


class SimpleTestAgent(BaseAutonomousAgent):
    """Simple test agent for integration testing."""
    
    def __init__(self, agent_id: str, event_bus: EventBus, shared_context: SharedContext):
        super().__init__(agent_id, event_bus, shared_context)
        self.events_received: List[Event] = []
        self.event_handlers = []
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to test events."""
        def handler(event: Event):
            self.events_received.append(event)
        
        self.event_handlers.append(handler)
        self.event_bus.subscribe(EventType.PERFORMANCE_ALERT, handler)
        self.event_bus.subscribe(EventType.BUG_DETECTED, handler)
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        for handler in self.event_handlers:
            try:
                self.event_bus.unsubscribe(EventType.PERFORMANCE_ALERT, handler)
                self.event_bus.unsubscribe(EventType.BUG_DETECTED, handler)
            except:
                pass
        self.event_handlers.clear()
    
    def _on_start(self) -> None:
        """Agent-specific initialization."""
        pass
    
    def _on_stop(self) -> None:
        """Agent-specific cleanup."""
        pass
    
    def perform_work(self, task_description: str):
        """Simulate performing work."""
        self._set_current_task(task_description)
        time.sleep(0.1)  # Simulate work
        self._update_metrics(task_completed=True, completion_time=0.1)
        self._set_current_task(None)


class ReactiveTestAgent(BaseAutonomousAgent):
    """Test agent that reacts to other agents' events."""
    
    def __init__(self, agent_id: str, event_bus: EventBus, shared_context: SharedContext):
        super().__init__(agent_id, event_bus, shared_context)
        self.reactions: List[str] = []
        self.event_handlers = []
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to all agent events."""
        def on_agent_started(event: Event):
            self.reactions.append(f"Detected agent start: {event.source}")
        
        def on_performance_alert(event: Event):
            self.reactions.append(f"Responding to performance alert from {event.source}")
            # React by publishing our own event
            self.event_bus.publish(Event(
                event_type=EventType.CODE_QUALITY_ISSUE,
                source=self.agent_id,
                payload={"reacting_to": event.event_id}
            ))
        
        self.event_handlers.extend([on_agent_started, on_performance_alert])
        self.event_bus.subscribe(EventType.AGENT_STARTED, on_agent_started)
        self.event_bus.subscribe(EventType.PERFORMANCE_ALERT, on_performance_alert)
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        for handler in self.event_handlers:
            try:
                self.event_bus.unsubscribe(EventType.AGENT_STARTED, handler)
                self.event_bus.unsubscribe(EventType.PERFORMANCE_ALERT, handler)
            except:
                pass
        self.event_handlers.clear()
    
    def _on_start(self) -> None:
        """Agent-specific initialization."""
        pass
    
    def _on_stop(self) -> None:
        """Agent-specific cleanup."""
        pass


@pytest.fixture
def event_bus():
    """Create a fresh event bus."""
    return EventBus()


@pytest.fixture
def shared_context():
    """Create a fresh shared context."""
    return SharedContext()


class TestMultiAgentLifecycle:
    """Test agent lifecycle coordination."""
    
    def test_multiple_agents_start_stop(self, event_bus, shared_context):
        """Test starting and stopping multiple agents."""
        # Create agents
        agent1 = SimpleTestAgent("agent1", event_bus, shared_context)
        agent2 = SimpleTestAgent("agent2", event_bus, shared_context)
        agent3 = SimpleTestAgent("agent3", event_bus, shared_context)
        
        # Start all agents
        agent1.start()
        agent2.start()
        agent3.start()
        
        # Verify all are running
        assert agent1.is_running()
        assert agent2.is_running()
        assert agent3.is_running()
        
        # Verify all are registered in shared context
        states = shared_context.get_all_agent_states()
        assert len(states) == 3
        agent_ids = [s.agent_id for s in states]
        assert "agent1" in agent_ids
        assert "agent2" in agent_ids
        assert "agent3" in agent_ids
        
        # Verify all have IDLE status
        for agent_id in ["agent1", "agent2", "agent3"]:
            state = shared_context.get_agent_state(agent_id)
            assert state.status == AgentStatus.IDLE
        
        # Stop all agents
        agent1.stop()
        agent2.stop()
        agent3.stop()
        
        # Verify all are stopped
        assert not agent1.is_running()
        assert not agent2.is_running()
        assert not agent3.is_running()
    
    def test_agent_start_events(self, event_bus, shared_context):
        """Test that agents receive start events from other agents."""
        # Create a reactive agent
        reactive = ReactiveTestAgent("reactive", event_bus, shared_context)
        reactive.start()
        
        # Clear reactions from reactive agent's own start
        reactive.reactions.clear()
        
        # Start other agents
        agent1 = SimpleTestAgent("agent1", event_bus, shared_context)
        agent2 = SimpleTestAgent("agent2", event_bus, shared_context)
        
        agent1.start()
        agent2.start()
        
        # Verify reactive agent detected the starts
        assert len(reactive.reactions) == 2
        assert "Detected agent start: agent1" in reactive.reactions
        assert "Detected agent start: agent2" in reactive.reactions
        
        # Cleanup
        agent1.stop()
        agent2.stop()
        reactive.stop()


class TestEventCoordination:
    """Test coordination through events."""
    
    def test_event_propagation(self, event_bus, shared_context):
        """Test that events propagate to all subscribed agents."""
        # Create multiple agents
        agents = [
            SimpleTestAgent(f"agent{i}", event_bus, shared_context)
            for i in range(5)
        ]
        
        # Start all agents
        for agent in agents:
            agent.start()
        
        # Publish a performance alert
        event = Event(
            event_type=EventType.PERFORMANCE_ALERT,
            source="external",
            payload={"fps": 30}
        )
        event_bus.publish(event)
        
        # Verify all agents received the event
        for agent in agents:
            assert len(agent.events_received) == 1
            assert agent.events_received[0] == event
        
        # Cleanup
        for agent in agents:
            agent.stop()
    
    def test_reactive_event_chain(self, event_bus, shared_context):
        """Test that agents can react to events from other agents."""
        # Create agents
        simple = SimpleTestAgent("simple", event_bus, shared_context)
        reactive = ReactiveTestAgent("reactive", event_bus, shared_context)
        
        # Subscribe simple agent to code quality issues
        code_quality_events = []
        def track_code_quality(event: Event):
            code_quality_events.append(event)
        
        event_bus.subscribe(EventType.CODE_QUALITY_ISSUE, track_code_quality)
        
        # Start agents
        simple.start()
        reactive.start()
        
        # Clear initial reactions
        reactive.reactions.clear()
        
        # Publish performance alert from simple agent
        event = Event(
            event_type=EventType.PERFORMANCE_ALERT,
            source="simple",
            payload={"fps": 25}
        )
        event_bus.publish(event)
        
        # Verify reactive agent responded
        assert len(reactive.reactions) == 1
        assert "Responding to performance alert" in reactive.reactions[0]
        
        # Verify reactive agent published a code quality issue
        assert len(code_quality_events) == 1
        assert code_quality_events[0].source == "reactive"
        
        # Cleanup
        event_bus.unsubscribe(EventType.CODE_QUALITY_ISSUE, track_code_quality)
        simple.stop()
        reactive.stop()
    
    def test_concurrent_event_publishing(self, event_bus, shared_context):
        """Test that multiple agents can publish events concurrently."""
        # Create agents
        agents = [
            SimpleTestAgent(f"agent{i}", event_bus, shared_context)
            for i in range(10)
        ]
        
        # Start all agents
        for agent in agents:
            agent.start()
        
        # Each agent publishes an event
        for i, agent in enumerate(agents):
            event = Event(
                event_type=EventType.PERFORMANCE_ALERT,
                source=agent.agent_id,
                payload={"agent_index": i}
            )
            event_bus.publish(event)
        
        # Verify all agents received all events (10 events each)
        for agent in agents:
            assert len(agent.events_received) == 10
        
        # Verify event history has all events
        history = event_bus.get_history()
        performance_alerts = [e for e in history if e.event_type == EventType.PERFORMANCE_ALERT]
        assert len(performance_alerts) == 10
        
        # Cleanup
        for agent in agents:
            agent.stop()


class TestStateCoordination:
    """Test coordination through shared state."""
    
    def test_state_synchronization(self, event_bus, shared_context):
        """Test that agents can see each other's state."""
        # Create agents
        agent1 = SimpleTestAgent("agent1", event_bus, shared_context)
        agent2 = SimpleTestAgent("agent2", event_bus, shared_context)
        
        agent1.start()
        agent2.start()
        
        # Agent1 starts working
        agent1.perform_work("Processing data")
        
        # Agent2 can see agent1's completion metrics
        agent1_state = shared_context.get_agent_state("agent1")
        assert agent1_state.metrics.tasks_completed == 1
        
        # Agent2 also does work
        agent2.perform_work("Analyzing results")
        
        # Both states are visible
        agent2_state = shared_context.get_agent_state("agent2")
        assert agent2_state.metrics.tasks_completed == 1
        
        # Cleanup
        agent1.stop()
        agent2.stop()
    
    def test_shared_data_coordination(self, event_bus, shared_context):
        """Test agents coordinating through shared data."""
        # Create agents
        agent1 = SimpleTestAgent("agent1", event_bus, shared_context)
        agent2 = SimpleTestAgent("agent2", event_bus, shared_context)
        
        agent1.start()
        agent2.start()
        
        # Agent1 stores some data
        shared_context.set("analysis_results", {
            "agent": "agent1",
            "findings": ["issue1", "issue2"],
            "timestamp": datetime.now()
        })
        
        # Agent2 can retrieve it
        results = shared_context.get("analysis_results")
        assert results is not None
        assert results["agent"] == "agent1"
        assert len(results["findings"]) == 2
        
        # Agent2 adds its own data
        shared_context.set("agent2_status", "completed")
        
        # Both pieces of data are available
        assert shared_context.get("analysis_results") is not None
        assert shared_context.get("agent2_status") == "completed"
        
        # Cleanup
        agent1.stop()
        agent2.stop()
    
    def test_concurrent_state_updates(self, event_bus, shared_context):
        """Test concurrent state updates from multiple agents."""
        # Create multiple agents
        agents = [
            SimpleTestAgent(f"agent{i}", event_bus, shared_context)
            for i in range(5)
        ]
        
        # Start all agents
        for agent in agents:
            agent.start()
        
        # All agents perform work
        for agent in agents:
            agent.perform_work("Concurrent task")
        
        # Verify all state updates succeeded
        for agent in agents:
            state = shared_context.get_agent_state(agent.agent_id)
            assert state.metrics.tasks_completed == 1
            assert state.status == AgentStatus.IDLE
        
        # Cleanup
        for agent in agents:
            agent.stop()


class TestErrorCoordination:
    """Test error handling in multi-agent scenarios."""
    
    def test_agent_failure_isolation(self, event_bus, shared_context):
        """Test that one agent's failure doesn't affect others."""
        # Create agents
        agent1 = SimpleTestAgent("agent1", event_bus, shared_context)
        agent2 = SimpleTestAgent("agent2", event_bus, shared_context)
        
        agent1.start()
        agent2.start()
        
        # Simulate agent1 error
        agent1._handle_error(Exception("Test error"))
        
        # Verify agent1 is in error state
        agent1_state = shared_context.get_agent_state("agent1")
        assert agent1_state.status == AgentStatus.ERROR
        assert agent1_state.metrics.tasks_failed == 1
        
        # Verify agent2 is still operational
        agent2_state = shared_context.get_agent_state("agent2")
        assert agent2_state.status == AgentStatus.IDLE
        assert agent2.is_running()
        
        # Agent2 can still do work
        agent2.perform_work("Continuing despite agent1 error")
        agent2_state = shared_context.get_agent_state("agent2")
        assert agent2_state.metrics.tasks_completed == 1
        
        # Cleanup
        agent1.stop()
        agent2.stop()
    
    def test_error_event_propagation(self, event_bus, shared_context):
        """Test that error events are properly propagated."""
        # Track error events
        error_events = []
        
        def error_handler(event: Event):
            error_events.append(event)
        
        event_bus.subscribe(EventType.AGENT_ERROR, error_handler)
        
        # Create agent
        agent = SimpleTestAgent("test_agent", event_bus, shared_context)
        agent.start()
        
        # Trigger error
        agent._handle_error(Exception("Test error"))
        
        # Verify error event was published
        assert len(error_events) == 1
        assert error_events[0].source == "test_agent"
        assert "Test error" in error_events[0].payload["error"]
        
        # Cleanup
        event_bus.unsubscribe(EventType.AGENT_ERROR, error_handler)
        agent.stop()
