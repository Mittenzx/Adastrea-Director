"""
Tests for the Event Bus system.
"""

import pytest
from datetime import datetime
from agents.phase3.event_bus import Event, EventBus, EventType


class TestEvent:
    """Tests for the Event class."""
    
    def test_event_creation(self):
        """Test creating a basic event."""
        event = Event(
            event_type=EventType.PERFORMANCE_ALERT,
            source="test_agent",
            payload={"test": "data"}
        )
        
        assert event.event_type == EventType.PERFORMANCE_ALERT
        assert event.source == "test_agent"
        assert event.payload == {"test": "data"}
        assert event.event_id is not None
        assert isinstance(event.timestamp, datetime)
    
    def test_event_with_correlation_id(self):
        """Test creating an event with correlation ID."""
        event = Event(
            event_type=EventType.BUG_DETECTED,
            source="bug_agent",
            payload={},
            correlation_id="test-correlation-123"
        )
        
        assert event.correlation_id == "test-correlation-123"
    
    def test_event_string_representation(self):
        """Test event string representation."""
        event = Event(
            event_type=EventType.AGENT_STARTED,
            source="test_agent",
            payload={}
        )
        
        event_str = str(event)
        assert "agent_started" in event_str
        assert "test_agent" in event_str


class TestEventBus:
    """Tests for the EventBus class."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus for each test."""
        return EventBus()
    
    def test_initialization(self, event_bus):
        """Test event bus initialization."""
        assert event_bus is not None
        assert len(event_bus.get_all_event_types()) == 0
    
    def test_publish_event(self, event_bus):
        """Test publishing an event."""
        event = Event(
            event_type=EventType.TEST_COMPLETED,
            source="test",
            payload={"result": "pass"}
        )
        
        # Should not raise exception
        event_bus.publish(event)
        
        # Event should be in history
        history = event_bus.get_history()
        assert len(history) == 1
        assert history[0] == event
    
    def test_subscribe_and_receive(self, event_bus):
        """Test subscribing to and receiving events."""
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        # Subscribe to events
        event_bus.subscribe(EventType.PERFORMANCE_ALERT, handler)
        
        # Publish an event
        event = Event(
            event_type=EventType.PERFORMANCE_ALERT,
            source="perf_agent",
            payload={"fps": 30}
        )
        event_bus.publish(event)
        
        # Handler should have received the event
        assert len(received_events) == 1
        assert received_events[0] == event
    
    def test_multiple_subscribers(self, event_bus):
        """Test multiple subscribers receiving the same event."""
        received_1 = []
        received_2 = []
        
        def handler1(event):
            received_1.append(event)
        
        def handler2(event):
            received_2.append(event)
        
        # Subscribe both handlers
        event_bus.subscribe(EventType.BUG_DETECTED, handler1)
        event_bus.subscribe(EventType.BUG_DETECTED, handler2)
        
        # Publish event
        event = Event(
            event_type=EventType.BUG_DETECTED,
            source="bug_agent",
            payload={}
        )
        event_bus.publish(event)
        
        # Both should receive
        assert len(received_1) == 1
        assert len(received_2) == 1
        assert received_1[0] == event
        assert received_2[0] == event
    
    def test_unsubscribe(self, event_bus):
        """Test unsubscribing from events."""
        received = []
        
        def handler(event):
            received.append(event)
        
        # Subscribe
        event_bus.subscribe(EventType.AGENT_STARTED, handler)
        
        # Publish first event
        event1 = Event(
            event_type=EventType.AGENT_STARTED,
            source="agent1",
            payload={}
        )
        event_bus.publish(event1)
        assert len(received) == 1
        
        # Unsubscribe
        event_bus.unsubscribe(EventType.AGENT_STARTED, handler)
        
        # Publish second event
        event2 = Event(
            event_type=EventType.AGENT_STARTED,
            source="agent2",
            payload={}
        )
        event_bus.publish(event2)
        
        # Should still only have one event
        assert len(received) == 1
    
    def test_subscriber_error_handling(self, event_bus):
        """Test that errors in subscribers don't break the bus."""
        received = []
        
        def bad_handler(event):
            raise ValueError("Handler error")
        
        def good_handler(event):
            received.append(event)
        
        # Subscribe both handlers
        event_bus.subscribe(EventType.TEST_FAILED, bad_handler)
        event_bus.subscribe(EventType.TEST_FAILED, good_handler)
        
        # Publish event - should not raise exception
        event = Event(
            event_type=EventType.TEST_FAILED,
            source="test",
            payload={}
        )
        event_bus.publish(event)
        
        # Good handler should still receive event
        assert len(received) == 1
    
    def test_event_history(self, event_bus):
        """Test event history tracking."""
        # Publish multiple events
        for i in range(5):
            event = Event(
                event_type=EventType.PERFORMANCE_METRICS_COLLECTED,
                source="perf_agent",
                payload={"index": i}
            )
            event_bus.publish(event)
        
        # Get full history
        history = event_bus.get_history()
        assert len(history) == 5
        assert history[0].payload["index"] == 0
        assert history[4].payload["index"] == 4
    
    def test_event_history_limit(self, event_bus):
        """Test event history size limit."""
        # Get history with limit
        for i in range(10):
            event = Event(
                event_type=EventType.CUSTOM,
                source="test",
                payload={"index": i}
            )
            event_bus.publish(event)
        
        history = event_bus.get_history(limit=5)
        assert len(history) == 5
        # Should be the most recent 5
        assert history[0].payload["index"] == 5
        assert history[4].payload["index"] == 9
    
    def test_event_history_filtering_by_type(self, event_bus):
        """Test filtering event history by type."""
        # Publish different event types
        event1 = Event(
            event_type=EventType.BUG_DETECTED,
            source="bug_agent",
            payload={}
        )
        event2 = Event(
            event_type=EventType.PERFORMANCE_ALERT,
            source="perf_agent",
            payload={}
        )
        event3 = Event(
            event_type=EventType.BUG_DETECTED,
            source="bug_agent",
            payload={}
        )
        
        event_bus.publish(event1)
        event_bus.publish(event2)
        event_bus.publish(event3)
        
        # Filter by type
        bug_events = event_bus.get_history(event_type=EventType.BUG_DETECTED)
        assert len(bug_events) == 2
        
        perf_events = event_bus.get_history(event_type=EventType.PERFORMANCE_ALERT)
        assert len(perf_events) == 1
    
    def test_event_history_filtering_by_source(self, event_bus):
        """Test filtering event history by source."""
        # Publish events from different sources
        event1 = Event(
            event_type=EventType.AGENT_STARTED,
            source="agent1",
            payload={}
        )
        event2 = Event(
            event_type=EventType.AGENT_STARTED,
            source="agent2",
            payload={}
        )
        event3 = Event(
            event_type=EventType.AGENT_STOPPED,
            source="agent1",
            payload={}
        )
        
        event_bus.publish(event1)
        event_bus.publish(event2)
        event_bus.publish(event3)
        
        # Filter by source
        agent1_events = event_bus.get_history(source="agent1")
        assert len(agent1_events) == 2
        
        agent2_events = event_bus.get_history(source="agent2")
        assert len(agent2_events) == 1
    
    def test_clear_history(self, event_bus):
        """Test clearing event history."""
        # Add some events
        for i in range(5):
            event = Event(
                event_type=EventType.CUSTOM,
                source="test",
                payload={}
            )
            event_bus.publish(event)
        
        assert len(event_bus.get_history()) == 5
        
        # Clear history
        event_bus.clear_history()
        
        assert len(event_bus.get_history()) == 0
    
    def test_subscriber_count(self, event_bus):
        """Test getting subscriber count."""
        def handler1(event):
            pass
        
        def handler2(event):
            pass
        
        assert event_bus.get_subscriber_count(EventType.CRASH_DETECTED) == 0
        
        event_bus.subscribe(EventType.CRASH_DETECTED, handler1)
        assert event_bus.get_subscriber_count(EventType.CRASH_DETECTED) == 1
        
        event_bus.subscribe(EventType.CRASH_DETECTED, handler2)
        assert event_bus.get_subscriber_count(EventType.CRASH_DETECTED) == 2
        
        event_bus.unsubscribe(EventType.CRASH_DETECTED, handler1)
        assert event_bus.get_subscriber_count(EventType.CRASH_DETECTED) == 1
    
    def test_get_all_event_types(self, event_bus):
        """Test getting all subscribed event types."""
        def handler(event):
            pass
        
        event_bus.subscribe(EventType.BUG_DETECTED, handler)
        event_bus.subscribe(EventType.PERFORMANCE_ALERT, handler)
        
        event_types = event_bus.get_all_event_types()
        assert EventType.BUG_DETECTED in event_types
        assert EventType.PERFORMANCE_ALERT in event_types
        assert len(event_types) == 2
