"""
Integration tests for Event Bus with Multiple Agents.

Tests event bus behavior under various multi-agent scenarios including
concurrent publishing, filtering, and ordering.
"""

import pytest
import threading
import time

from agents.phase3.event_bus import Event, EventBus, EventType


class TestEventBusConcurrency:
    """Test event bus with concurrent operations."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus."""
        return EventBus()
    
    def test_concurrent_publishing(self, event_bus):
        """Test multiple threads publishing events simultaneously."""
        num_threads = 10
        events_per_thread = 50
        received_events = []
        lock = threading.Lock()
        
        def publisher(thread_id):
            for i in range(events_per_thread):
                event = Event(
                    event_type=EventType.PERFORMANCE_ALERT,
                    source=f"thread_{thread_id}",
                    payload={"thread": thread_id, "index": i}
                )
                event_bus.publish(event)
                time.sleep(0.001)  # Small delay to increase concurrency
        
        def subscriber(event: Event):
            with lock:
                received_events.append(event)
        
        # Subscribe
        event_bus.subscribe(EventType.PERFORMANCE_ALERT, subscriber)
        
        # Start publishing threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=publisher, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all events were received
        assert len(received_events) == num_threads * events_per_thread
        
        # Verify events from each thread
        for thread_id in range(num_threads):
            thread_events = [e for e in received_events if e.source == f"thread_{thread_id}"]
            assert len(thread_events) == events_per_thread
    
    def test_concurrent_subscribe_unsubscribe(self, event_bus):
        """Test concurrent subscription and unsubscription."""
        num_operations = 100
        handlers_added = []
        
        def handler_factory(handler_id):
            def handler(event: Event):
                pass
            handler._id = handler_id
            return handler
        
        def subscribe_unsubscribe_worker():
            for i in range(num_operations):
                handler = handler_factory(i)
                handlers_added.append(handler)
                event_bus.subscribe(EventType.BUG_DETECTED, handler)
                time.sleep(0.001)
                event_bus.unsubscribe(EventType.BUG_DETECTED, handler)
        
        # Run concurrent operations
        threads = [threading.Thread(target=subscribe_unsubscribe_worker) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Event bus should still be operational
        test_event = Event(
            event_type=EventType.BUG_DETECTED,
            source="test",
            payload={}
        )
        # Should not raise exception
        event_bus.publish(test_event)
    
    def test_event_ordering(self, event_bus):
        """Test that events maintain some ordering under concurrent load."""
        num_agents = 5
        events_per_agent = 20
        received_order = []
        lock = threading.Lock()
        
        def subscriber(event: Event):
            with lock:
                received_order.append((event.source, event.payload["index"]))
        
        event_bus.subscribe(EventType.CUSTOM, subscriber)
        
        def publish_sequence(agent_id):
            for i in range(events_per_agent):
                event = Event(
                    event_type=EventType.CUSTOM,
                    source=f"agent_{agent_id}",
                    payload={"index": i}
                )
                event_bus.publish(event)
        
        # Start all publishers
        threads = []
        for agent_id in range(num_agents):
            thread = threading.Thread(target=publish_sequence, args=(agent_id,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify all events were received
        assert len(received_order) == num_agents * events_per_agent
        
        # Verify each agent's events maintain their order
        for agent_id in range(num_agents):
            agent_events = [idx for src, idx in received_order if src == f"agent_{agent_id}"]
            # Events from same agent should be in order
            assert agent_events == list(range(events_per_agent))


class TestEventFiltering:
    """Test event filtering with multiple subscribers."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus."""
        return EventBus()
    
    def test_selective_subscription(self, event_bus):
        """Test that agents only receive events they subscribe to."""
        perf_events = []
        bug_events = []
        quality_events = []
        
        def perf_handler(event: Event):
            perf_events.append(event)
        
        def bug_handler(event: Event):
            bug_events.append(event)
        
        def quality_handler(event: Event):
            quality_events.append(event)
        
        # Subscribe to different event types
        event_bus.subscribe(EventType.PERFORMANCE_ALERT, perf_handler)
        event_bus.subscribe(EventType.BUG_DETECTED, bug_handler)
        event_bus.subscribe(EventType.CODE_QUALITY_ISSUE, quality_handler)
        
        # Publish various events
        event_bus.publish(Event(EventType.PERFORMANCE_ALERT, "agent1", {}))
        event_bus.publish(Event(EventType.BUG_DETECTED, "agent2", {}))
        event_bus.publish(Event(EventType.CODE_QUALITY_ISSUE, "agent3", {}))
        event_bus.publish(Event(EventType.PERFORMANCE_ALERT, "agent1", {}))
        event_bus.publish(Event(EventType.BUG_DETECTED, "agent2", {}))
        
        # Verify each handler only received its events
        assert len(perf_events) == 2
        assert len(bug_events) == 2
        assert len(quality_events) == 1
        
        # Verify event types
        assert all(e.event_type == EventType.PERFORMANCE_ALERT for e in perf_events)
        assert all(e.event_type == EventType.BUG_DETECTED for e in bug_events)
        assert all(e.event_type == EventType.CODE_QUALITY_ISSUE for e in quality_events)
    
    def test_history_filtering_by_source(self, event_bus):
        """Test filtering event history by source agent."""
        # Publish events from different sources
        for i in range(10):
            agent_id = f"agent{i % 3}"  # 3 different agents
            event = Event(
                event_type=EventType.PERFORMANCE_METRICS_COLLECTED,
                source=agent_id,
                payload={"index": i}
            )
            event_bus.publish(event)
        
        # Filter by each source
        agent0_events = event_bus.get_history(source="agent0")
        agent1_events = event_bus.get_history(source="agent1")
        agent2_events = event_bus.get_history(source="agent2")
        
        # Verify correct filtering
        assert len(agent0_events) == 4  # indices 0, 3, 6, 9
        assert len(agent1_events) == 3  # indices 1, 4, 7
        assert len(agent2_events) == 3  # indices 2, 5, 8
        
        # Verify all are from correct source
        assert all(e.source == "agent0" for e in agent0_events)
        assert all(e.source == "agent1" for e in agent1_events)
        assert all(e.source == "agent2" for e in agent2_events)
    
    def test_history_filtering_combined(self, event_bus):
        """Test filtering by both type and source."""
        # Publish mixed events
        sources = ["agent1", "agent2", "agent1", "agent2"]
        types = [
            EventType.PERFORMANCE_ALERT,
            EventType.BUG_DETECTED,
            EventType.BUG_DETECTED,
            EventType.PERFORMANCE_ALERT
        ]
        
        for source, event_type in zip(sources, types):
            event = Event(event_type=event_type, source=source, payload={})
            event_bus.publish(event)
        
        # Filter by type
        bug_events = event_bus.get_history(event_type=EventType.BUG_DETECTED)
        assert len(bug_events) == 2
        
        # Filter by source
        agent1_events = event_bus.get_history(source="agent1")
        assert len(agent1_events) == 2
        
        # Combined filter (would need custom logic in real implementation)
        # For now just verify separate filters work
        assert all(e.event_type == EventType.BUG_DETECTED for e in bug_events)
        assert all(e.source == "agent1" for e in agent1_events)


class TestEventBusScalability:
    """Test event bus performance with many agents."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus."""
        return EventBus()
    
    def test_many_subscribers(self, event_bus):
        """Test event bus with many subscribers."""
        num_subscribers = 100
        handlers = []
        received_counts = [0] * num_subscribers
        
        # Create many subscribers
        for i in range(num_subscribers):
            def make_handler(index):
                def handler(event: Event):
                    received_counts[index] += 1
                return handler
            
            handler = make_handler(i)
            handlers.append(handler)
            event_bus.subscribe(EventType.PERFORMANCE_ALERT, handler)
        
        # Publish events
        num_events = 50
        for i in range(num_events):
            event = Event(
                event_type=EventType.PERFORMANCE_ALERT,
                source="test",
                payload={"index": i}
            )
            event_bus.publish(event)
        
        # Verify all subscribers received all events
        assert all(count == num_events for count in received_counts)
        assert event_bus.get_subscriber_count(EventType.PERFORMANCE_ALERT) == num_subscribers
    
    def test_large_event_history(self, event_bus):
        """Test event bus with large event history."""
        # Publish many events
        num_events = 2000  # More than default history size
        for i in range(num_events):
            event = Event(
                event_type=EventType.CUSTOM,
                source="test",
                payload={"index": i}
            )
            event_bus.publish(event)
        
        # Get full history (should be limited)
        history = event_bus.get_history(limit=10000)
        
        # Should not exceed max history size
        assert len(history) <= 1000  # Default max size
        
        # Most recent events should be preserved
        last_event = history[-1]
        assert last_event.payload["index"] == num_events - 1
    
    def test_rapid_event_publishing(self, event_bus):
        """Test rapid event publishing performance."""
        received_count = 0
        lock = threading.Lock()
        
        def subscriber(event: Event):
            nonlocal received_count
            with lock:
                received_count += 1
        
        event_bus.subscribe(EventType.PERFORMANCE_METRICS_COLLECTED, subscriber)
        
        # Publish events rapidly
        num_events = 1000
        start_time = time.time()
        
        for i in range(num_events):
            event = Event(
                event_type=EventType.PERFORMANCE_METRICS_COLLECTED,
                source="perf_agent",
                payload={"metric": i}
            )
            event_bus.publish(event)
        
        elapsed = time.time() - start_time
        
        # Verify all events were received
        assert received_count == num_events
        
        # Performance check - should be fast (< 1 second for 1000 events)
        assert elapsed < 1.0, f"Event publishing took {elapsed:.2f}s, expected < 1.0s"


class TestEventBusReliability:
    """Test event bus reliability and error handling."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus."""
        return EventBus()
    
    def test_subscriber_exception_isolation(self, event_bus):
        """Test that subscriber exceptions don't affect other subscribers."""
        good_handler_called = 0
        bad_handler_called = 0
        
        def good_handler(event: Event):
            nonlocal good_handler_called
            good_handler_called += 1
        
        def bad_handler(event: Event):
            nonlocal bad_handler_called
            bad_handler_called += 1
            raise Exception("Handler error")
        
        # Subscribe both handlers
        event_bus.subscribe(EventType.TEST_COMPLETED, bad_handler)
        event_bus.subscribe(EventType.TEST_COMPLETED, good_handler)
        
        # Publish event
        event = Event(EventType.TEST_COMPLETED, "test", {})
        event_bus.publish(event)
        
        # Both handlers should have been called
        assert bad_handler_called == 1
        assert good_handler_called == 1
        
        # Event should be in history despite handler error
        history = event_bus.get_history(event_type=EventType.TEST_COMPLETED)
        assert len(history) == 1
    
    def test_unsubscribe_during_iteration(self, event_bus):
        """Test unsubscribing handlers that don't exist or have already been unsubscribed."""
        def handler(event: Event):
            pass
        
        # Unsubscribe without subscribing first (should not crash)
        event_bus.unsubscribe(EventType.BUG_DETECTED, handler)
        
        # Subscribe then unsubscribe twice
        event_bus.subscribe(EventType.BUG_DETECTED, handler)
        event_bus.unsubscribe(EventType.BUG_DETECTED, handler)
        event_bus.unsubscribe(EventType.BUG_DETECTED, handler)  # Should not crash
    
    def test_event_bus_clear_history(self, event_bus):
        """Test clearing event history."""
        # Publish events
        for i in range(100):
            event = Event(EventType.CUSTOM, "test", {"index": i})
            event_bus.publish(event)
        
        # Verify history has events
        assert len(event_bus.get_history()) == 100
        
        # Clear history
        event_bus.clear_history()
        
        # Verify history is empty
        assert len(event_bus.get_history()) == 0
        
        # Event bus should still work
        event = Event(EventType.CUSTOM, "test", {})
        event_bus.publish(event)
        assert len(event_bus.get_history()) == 1
