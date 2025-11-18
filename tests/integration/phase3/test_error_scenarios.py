"""
Integration tests for Error Scenarios.

Tests error handling, recovery, and failure isolation in multi-agent
environments.
"""

import pytest
import threading

from agents.phase3.base_agent import BaseAutonomousAgent
from agents.phase3.event_bus import Event, EventBus, EventType
from agents.phase3.shared_state import SharedContext, AgentStatus


class FaultyAgent(BaseAutonomousAgent):
    """Agent that simulates various failure modes."""
    
    def __init__(self, agent_id: str, event_bus: EventBus, shared_context: SharedContext,
                 fail_on_start: bool = False, fail_on_event: bool = False):
        super().__init__(agent_id, event_bus, shared_context)
        self.fail_on_start = fail_on_start
        self.fail_on_event = fail_on_event
        self.events_received = []
        self.event_handler = None
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to events (may fail if configured)."""
        def handler(event: Event):
            self.events_received.append(event)
            if self.fail_on_event:
                raise Exception("Handler failure")
        
        self.event_handler = handler
        self.event_bus.subscribe(EventType.PERFORMANCE_ALERT, handler)
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        if self.event_handler:
            try:
                self.event_bus.unsubscribe(EventType.PERFORMANCE_ALERT, self.event_handler)
            except Exception:
                # Ignore errors during unsubscribe (handler may not be subscribed)
                pass
    
    def _on_start(self) -> None:
        """Agent-specific initialization (may fail if configured)."""
        if self.fail_on_start:
            raise Exception("Start failure")
    
    def _on_stop(self) -> None:
        """Agent-specific cleanup."""
        pass


class TestAgentFailureRecovery:
    """Test agent failure recovery scenarios."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus."""
        return EventBus()
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_agent_start_failure(self, event_bus, shared_context):
        """Test handling of agent start failures."""
        # Create an agent that fails on start
        faulty = FaultyAgent("faulty", event_bus, shared_context, fail_on_start=True)
        
        # Starting should handle the error gracefully
        faulty.start()
        
        # Agent should be in error state
        state = shared_context.get_agent_state("faulty")
        assert state.status == AgentStatus.ERROR
        assert state.metrics.tasks_failed == 1
    
    def test_agent_error_limit(self, event_bus, shared_context):
        """Test that agents stop after exceeding error limit."""
        agent = FaultyAgent("test", event_bus, shared_context)
        agent.start()
        
        # Trigger multiple errors
        for i in range(15):  # More than default max_errors (10)
            agent._handle_error(Exception(f"Error {i}"))
        
        # Agent should have stopped itself
        assert not agent.is_running()
        
        state = shared_context.get_agent_state("test")
        # State could be ERROR or STOPPED depending on when we check
        assert state.status in [AgentStatus.ERROR, AgentStatus.STOPPED]
        assert state.metrics.tasks_failed >= 10
    
    def test_partial_agent_failure(self, event_bus, shared_context):
        """Test that partial failures don't bring down the system."""
        # Create mix of working and faulty agents
        working1 = FaultyAgent("working1", event_bus, shared_context)
        faulty = FaultyAgent("faulty", event_bus, shared_context, fail_on_start=True)
        working2 = FaultyAgent("working2", event_bus, shared_context)
        
        # Start all agents
        working1.start()
        faulty.start()
        working2.start()
        
        # Working agents should be operational
        assert working1.is_running()
        assert working2.is_running()
        
        # Faulty agent should be in error state
        assert faulty.get_status() == AgentStatus.ERROR
        
        # System should still function
        event = Event(EventType.PERFORMANCE_ALERT, "test", {})
        event_bus.publish(event)
        
        # Working agents should receive event
        assert len(working1.events_received) == 1
        assert len(working2.events_received) == 1
        
        # Cleanup
        working1.stop()
        working2.stop()
        faulty.stop()


class TestEventBusErrorHandling:
    """Test event bus error handling."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus."""
        return EventBus()
    
    def test_subscriber_exception_isolation(self, event_bus):
        """Test that subscriber exceptions don't affect others."""
        good_count = [0]
        bad_count = [0]
        
        def good_handler(event: Event):
            good_count[0] += 1
        
        def bad_handler(event: Event):
            bad_count[0] += 1
            raise Exception("Subscriber error")
        
        def another_good_handler(event: Event):
            good_count[0] += 1
        
        # Subscribe all handlers
        event_bus.subscribe(EventType.BUG_DETECTED, bad_handler)
        event_bus.subscribe(EventType.BUG_DETECTED, good_handler)
        event_bus.subscribe(EventType.BUG_DETECTED, another_good_handler)
        
        # Publish event
        event = Event(EventType.BUG_DETECTED, "test", {})
        event_bus.publish(event)
        
        # All handlers should have been called despite exception
        assert bad_count[0] == 1
        assert good_count[0] == 2  # Two good handlers
    
    def test_event_publishing_under_load_with_errors(self, event_bus):
        """Test event publishing continues despite subscriber errors."""
        success_count = [0]
        error_count = [0]
        
        def error_handler(event: Event):
            error_count[0] += 1
            if event.payload.get("index", 0) % 5 == 0:
                raise Exception("Periodic error")
        
        def success_handler(event: Event):
            success_count[0] += 1
        
        event_bus.subscribe(EventType.CUSTOM, error_handler)
        event_bus.subscribe(EventType.CUSTOM, success_handler)
        
        # Publish many events
        num_events = 100
        for i in range(num_events):
            event = Event(EventType.CUSTOM, "test", {"index": i})
            event_bus.publish(event)
        
        # Both handlers should have received all events
        assert error_count[0] == num_events
        assert success_count[0] == num_events
        
        # History should have all events
        history = event_bus.get_history()
        assert len(history) >= num_events
    
    def test_concurrent_errors(self, event_bus):
        """Test handling concurrent errors from multiple threads."""
        error_counts = []
        lock = threading.Lock()
        
        def error_handler(event: Event):
            with lock:
                error_counts.append(1)
            raise Exception("Thread error")
        
        event_bus.subscribe(EventType.PERFORMANCE_ALERT, error_handler)
        
        # Publish from multiple threads
        def publisher(thread_id):
            for i in range(50):
                event = Event(
                    EventType.PERFORMANCE_ALERT,
                    f"thread_{thread_id}",
                    {"index": i}
                )
                event_bus.publish(event)
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=publisher, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All events should have been published despite errors
        assert len(error_counts) == 500  # 10 threads * 50 events


class TestSharedStateErrorHandling:
    """Test shared state error handling."""
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_update_nonexistent_agent(self, shared_context):
        """Test updating a non-existent agent doesn't crash."""
        # Should not raise exception
        shared_context.update_agent_state("nonexistent", status=AgentStatus.BUSY)
        
        # Agent still shouldn't exist
        state = shared_context.get_agent_state("nonexistent")
        assert state is None
    
    def test_concurrent_registration_race_condition(self, shared_context):
        """Test handling race condition in concurrent agent registration."""
        agent_id = "contested_agent"
        results = []
        
        def register_agent():
            state = shared_context.register_agent(agent_id)
            results.append(state)
        
        # Try to register same agent from multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=register_agent)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All threads should get a valid state
        assert len(results) == 10
        assert all(r is not None for r in results)
        assert all(r.agent_id == agent_id for r in results)
        
        # But only one agent should be registered
        states = shared_context.get_all_agent_states()
        agent_states = [s for s in states if s.agent_id == agent_id]
        assert len(agent_states) == 1
    
    def test_corrupted_state_recovery(self, shared_context):
        """Test recovery from corrupted state."""
        # Register agent
        agent_id = "test_agent"
        shared_context.register_agent(agent_id)
        
        # Attempt operations that might corrupt state
        for i in range(100):
            try:
                shared_context.update_agent_state(
                    agent_id,
                    status=AgentStatus.BUSY if i % 2 == 0 else AgentStatus.IDLE,
                    current_task=f"Task {i}"
                )
            except Exception:
                # Ignore errors during state corruption testing
                pass
        
        # State should still be retrievable
        state = shared_context.get_agent_state(agent_id)
        assert state is not None
        assert state.agent_id == agent_id


class TestDataConsistency:
    """Test data consistency under error conditions."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus."""
        return EventBus()
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_state_consistency_after_errors(self, event_bus, shared_context):
        """Test state remains consistent after errors."""
        # Create agents
        agents = []
        for i in range(5):
            agent = FaultyAgent(f"agent_{i}", event_bus, shared_context)
            agent.start()
            agents.append(agent)
        
        # Trigger errors in some agents
        agents[1]._handle_error(Exception("Test error"))
        agents[3]._handle_error(Exception("Test error"))
        
        # Verify all agent states are still accessible
        for agent in agents:
            state = shared_context.get_agent_state(agent.agent_id)
            assert state is not None
            assert state.agent_id == agent.agent_id
        
        # Verify error agents are in error state
        assert shared_context.get_agent_state("agent_1").status == AgentStatus.ERROR
        assert shared_context.get_agent_state("agent_3").status == AgentStatus.ERROR
        
        # Verify good agents are still idle
        assert shared_context.get_agent_state("agent_0").status == AgentStatus.IDLE
        assert shared_context.get_agent_state("agent_2").status == AgentStatus.IDLE
        
        # Cleanup
        for agent in agents:
            agent.stop()
    
    def test_event_history_consistency_with_errors(self, event_bus):
        """Test event history remains consistent despite errors."""
        error_handler_count = [0]
        
        def error_handler(event: Event):
            error_handler_count[0] += 1
            if error_handler_count[0] % 3 == 0:
                raise Exception("Periodic error")
        
        event_bus.subscribe(EventType.CUSTOM, error_handler)
        
        # Publish events
        event_ids = []
        for i in range(50):
            event = Event(EventType.CUSTOM, "test", {"index": i})
            event_ids.append(event.event_id)
            event_bus.publish(event)
        
        # All events should be in history despite handler errors
        history = event_bus.get_history()
        history_ids = [e.event_id for e in history]
        
        for event_id in event_ids:
            assert event_id in history_ids


class TestRecoveryMechanisms:
    """Test recovery mechanisms."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus."""
        return EventBus()
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_agent_restart_after_failure(self, event_bus, shared_context):
        """Test restarting an agent after failure."""
        # Create and start agent
        agent = FaultyAgent("test", event_bus, shared_context)
        agent.start()
        assert agent.is_running()
        
        # Trigger error
        agent._handle_error(Exception("Test error"))
        state = shared_context.get_agent_state("test")
        assert state.status == AgentStatus.ERROR
        
        # Stop agent
        agent.stop()
        assert not agent.is_running()
        
        # Create new agent with same ID (simulating restart)
        new_agent = FaultyAgent("test", event_bus, shared_context)
        new_agent.start()
        
        # New agent should be running
        assert new_agent.is_running()
        state = shared_context.get_agent_state("test")
        assert state.status == AgentStatus.IDLE
        
        # Cleanup
        new_agent.stop()
    
    def test_system_wide_error_recovery(self, event_bus, shared_context):
        """Test recovery from system-wide errors."""
        # Create multiple agents
        agents = []
        for i in range(10):
            agent = FaultyAgent(f"agent_{i}", event_bus, shared_context)
            agent.start()
            agents.append(agent)
        
        # Simulate system-wide issue - trigger errors in all agents
        for agent in agents:
            agent._handle_error(Exception("System error"))
        
        # All should be in error state
        for agent in agents:
            state = shared_context.get_agent_state(agent.agent_id)
            assert state.status == AgentStatus.ERROR
        
        # Stop all agents
        for agent in agents:
            agent.stop()
        
        # Clear shared state for recovery
        shared_context.clear_all()
        event_bus.clear_history()
        
        # Restart agents
        new_agents = []
        for i in range(10):
            agent = FaultyAgent(f"agent_{i}", event_bus, shared_context)
            agent.start()
            new_agents.append(agent)
        
        # All should be running and healthy
        for agent in new_agents:
            assert agent.is_running()
            state = shared_context.get_agent_state(agent.agent_id)
            assert state.status == AgentStatus.IDLE
        
        # Cleanup
        for agent in new_agents:
            agent.stop()


class TestErrorEventHandling:
    """Test error event handling and propagation."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus."""
        return EventBus()
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_error_event_propagation(self, event_bus, shared_context):
        """Test that error events are properly propagated."""
        error_events = []
        
        def error_monitor(event: Event):
            error_events.append(event)
        
        event_bus.subscribe(EventType.AGENT_ERROR, error_monitor)
        
        # Create agents and trigger errors
        agents = []
        for i in range(5):
            agent = FaultyAgent(f"agent_{i}", event_bus, shared_context)
            agent.start()
            agents.append(agent)
            
            # Trigger error
            agent._handle_error(Exception(f"Error from agent_{i}"))
        
        # Verify all error events were received
        assert len(error_events) == 5
        
        # Verify error details
        for i, event in enumerate(error_events):
            assert event.source == f"agent_{i}"
            assert f"Error from agent_{i}" in event.payload["error"]
        
        # Cleanup
        for agent in agents:
            agent.stop()
    
    def test_cascading_error_prevention(self, event_bus, shared_context):
        """Test preventing cascading errors."""
        error_count = [0]
        
        def error_reactive_handler(event: Event):
            # This handler reacts to errors but might also fail
            error_count[0] += 1
            if error_count[0] > 10:
                raise Exception("Too many errors")
        
        event_bus.subscribe(EventType.AGENT_ERROR, error_reactive_handler)
        
        # Trigger many errors
        agent = FaultyAgent("test", event_bus, shared_context)
        agent.start()
        
        for i in range(20):
            agent._handle_error(Exception(f"Error {i}"))
        
        # System should still be functional
        # Error in error handler shouldn't crash everything
        state = shared_context.get_agent_state("test")
        assert state is not None
        
        # Cleanup
        agent.stop()
