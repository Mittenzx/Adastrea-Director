"""
Performance Benchmarks for Phase 3 Integration.

Measures performance of event bus, shared state, and multi-agent
coordination under various load conditions.
"""

import pytest
import time
import statistics
from datetime import datetime

from agents.phase3.event_bus import Event, EventBus, EventType
from agents.phase3.shared_state import SharedContext, Change


# Mark all tests in this module as slow
pytestmark = pytest.mark.slow


class PerformanceBenchmark:
    """Base class for performance benchmarks."""
    
    @staticmethod
    def measure_time(func, iterations: int = 100) -> dict:
        """
        Measure execution time statistics.
        
        Returns:
            Dict with min, max, mean, median, and total time
        """
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            func()
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        
        return {
            "iterations": iterations,
            "min_ms": min(times) * 1000,
            "max_ms": max(times) * 1000,
            "mean_ms": statistics.mean(times) * 1000,
            "median_ms": statistics.median(times) * 1000,
            "stdev_ms": statistics.stdev(times) * 1000 if len(times) > 1 else 0,
            "total_s": sum(times)
        }
    
    @staticmethod
    def print_benchmark_results(name: str, results: dict):
        """Print benchmark results in a formatted way."""
        print(f"\n{'='*60}")
        print(f"Benchmark: {name}")
        print(f"{'='*60}")
        print(f"Iterations:    {results['iterations']}")
        print(f"Mean:          {results['mean_ms']:.3f} ms")
        print(f"Median:        {results['median_ms']:.3f} ms")
        print(f"Min:           {results['min_ms']:.3f} ms")
        print(f"Max:           {results['max_ms']:.3f} ms")
        print(f"Std Dev:       {results['stdev_ms']:.3f} ms")
        print(f"Total Time:    {results['total_s']:.3f} s")
        print(f"{'='*60}\n")


class TestEventBusPerformance(PerformanceBenchmark):
    """Benchmark event bus performance."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus."""
        return EventBus()
    
    def test_event_publishing_throughput(self, event_bus):
        """Benchmark event publishing throughput."""
        counter = [0]
        
        def subscriber(event: Event):
            counter[0] += 1
        
        event_bus.subscribe(EventType.PERFORMANCE_METRICS_COLLECTED, subscriber)
        
        num_events = 1000
        
        def publish_events():
            for i in range(num_events):
                event = Event(
                    event_type=EventType.PERFORMANCE_METRICS_COLLECTED,
                    source="benchmark",
                    payload={"index": i}
                )
                event_bus.publish(event)
        
        start_time = time.perf_counter()
        publish_events()
        elapsed = time.perf_counter() - start_time
        
        throughput = num_events / elapsed
        
        print(f"\n{'='*60}")
        print(f"Event Publishing Throughput")
        print(f"{'='*60}")
        print(f"Events Published: {num_events}")
        print(f"Time Taken:       {elapsed:.3f} s")
        print(f"Throughput:       {throughput:.0f} events/s")
        print(f"Avg Latency:      {(elapsed/num_events)*1000:.3f} ms/event")
        print(f"{'='*60}\n")
        
        # Verify all events were received
        assert counter[0] == num_events
        
        # Performance requirement: at least 500 events/second
        assert throughput > 500, f"Throughput {throughput:.0f} events/s is below target of 500"
    
    def test_subscription_overhead(self, event_bus):
        """Benchmark subscription and unsubscription overhead."""
        handlers = []
        
        # Create handlers
        for i in range(100):
            def make_handler():
                def handler(event: Event):
                    pass
                return handler
            handlers.append(make_handler())
        
        # Benchmark subscription
        def subscribe_all():
            local_event_bus = EventBus()
            for handler in handlers:
                local_event_bus.subscribe(EventType.BUG_DETECTED, handler)
        
        results = self.measure_time(subscribe_all, iterations=10)
        self.print_benchmark_results("Subscribe 100 Handlers", results)
        
        # Benchmark unsubscription
        def unsubscribe_all():
            local_event_bus = EventBus()
            for handler in handlers:
                local_event_bus.subscribe(EventType.BUG_DETECTED, handler)
            for handler in handlers:
                local_event_bus.unsubscribe(EventType.BUG_DETECTED, handler)
        
        results = self.measure_time(unsubscribe_all, iterations=10)
        self.print_benchmark_results("Unsubscribe 100 Handlers", results)
    
    def test_event_delivery_latency(self, event_bus):
        """Benchmark event delivery latency with multiple subscribers."""
        num_subscribers = 50
        delivery_times = []
        
        def make_subscriber():
            def subscriber(event: Event):
                # Record delivery time
                delivery_time = (datetime.now() - event.timestamp).total_seconds() * 1000
                delivery_times.append(delivery_time)
            return subscriber
        
        # Create subscribers
        for _ in range(num_subscribers):
            event_bus.subscribe(EventType.PERFORMANCE_ALERT, make_subscriber())
        
        # Publish events and measure delivery time
        num_events = 100
        for i in range(num_events):
            event = Event(
                event_type=EventType.PERFORMANCE_ALERT,
                source="benchmark",
                payload={"index": i}
            )
            event_bus.publish(event)
        
        # Calculate statistics
        print(f"\n{'='*60}")
        print(f"Event Delivery Latency ({num_subscribers} subscribers)")
        print(f"{'='*60}")
        print(f"Events Published: {num_events}")
        print(f"Subscribers:      {num_subscribers}")
        print(f"Total Deliveries: {len(delivery_times)}")
        print(f"Mean Latency:     {statistics.mean(delivery_times):.3f} ms")
        print(f"Median Latency:   {statistics.median(delivery_times):.3f} ms")
        print(f"Max Latency:      {max(delivery_times):.3f} ms")
        print(f"{'='*60}\n")
        
        # Performance requirement: mean latency < 10ms
        mean_latency = statistics.mean(delivery_times)
        assert mean_latency < 10, f"Mean latency {mean_latency:.3f}ms exceeds 10ms target"
    
    def test_history_query_performance(self, event_bus):
        """Benchmark event history query performance."""
        # Populate history with events
        for i in range(1000):
            event = Event(
                event_type=EventType.CUSTOM if i % 2 == 0 else EventType.BUG_DETECTED,
                source=f"agent_{i % 5}",
                payload={"index": i}
            )
            event_bus.publish(event)
        
        # Benchmark full history query
        def query_full_history():
            return event_bus.get_history(limit=1000)
        
        results = self.measure_time(query_full_history, iterations=100)
        self.print_benchmark_results("Query Full History (1000 events)", results)
        
        # Benchmark filtered query by type
        def query_by_type():
            return event_bus.get_history(event_type=EventType.BUG_DETECTED, limit=1000)
        
        results = self.measure_time(query_by_type, iterations=100)
        self.print_benchmark_results("Query by Type", results)
        
        # Benchmark filtered query by source
        def query_by_source():
            return event_bus.get_history(source="agent_0", limit=1000)
        
        results = self.measure_time(query_by_source, iterations=100)
        self.print_benchmark_results("Query by Source", results)


class TestSharedStatePerformance(PerformanceBenchmark):
    """Benchmark shared state performance."""
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_agent_registration_performance(self, shared_context):
        """Benchmark agent registration performance."""
        def register_agents():
            for i in range(100):
                shared_context.register_agent(f"agent_{i}")
        
        results = self.measure_time(register_agents, iterations=10)
        self.print_benchmark_results("Register 100 Agents", results)
        
        # Cleanup
        shared_context.clear_all()
    
    def test_state_update_performance(self, shared_context):
        """Benchmark state update performance."""
        # Register agents
        num_agents = 50
        for i in range(num_agents):
            shared_context.register_agent(f"agent_{i}")
        
        # Benchmark updates
        update_count = [0]
        
        def update_all_agents():
            for i in range(num_agents):
                shared_context.update_agent_state(
                    f"agent_{i}",
                    current_task=f"Task {update_count[0]}"
                )
            update_count[0] += 1
        
        results = self.measure_time(update_all_agents, iterations=100)
        self.print_benchmark_results(f"Update {num_agents} Agent States", results)
    
    def test_shared_data_access_performance(self, shared_context):
        """Benchmark shared data read/write performance."""
        # Populate with data
        for i in range(100):
            shared_context.set(f"key_{i}", {"index": i, "data": f"value_{i}"})
        
        # Benchmark reads
        def read_all_data():
            for i in range(100):
                shared_context.get(f"key_{i}")
        
        results = self.measure_time(read_all_data, iterations=100)
        self.print_benchmark_results("Read 100 Keys", results)
        
        # Benchmark writes
        write_count = [0]
        
        def write_all_data():
            for i in range(100):
                shared_context.set(f"key_{i}", {
                    "index": i,
                    "data": f"value_{i}",
                    "update": write_count[0]
                })
            write_count[0] += 1
        
        results = self.measure_time(write_all_data, iterations=100)
        self.print_benchmark_results("Write 100 Keys", results)
    
    def test_change_recording_performance(self, shared_context):
        """Benchmark change recording performance."""
        change_count = [0]
        
        def record_changes():
            for i in range(100):
                change = Change(
                    change_id=f"change_{change_count[0]}_{i}",
                    timestamp=datetime.now(),
                    file_path=f"src/file_{i}.cpp",
                    description=f"Change {i}",
                    author="benchmark"
                )
                shared_context.add_change(change)
            change_count[0] += 1
        
        results = self.measure_time(record_changes, iterations=10)
        self.print_benchmark_results("Record 100 Changes", results)
    
    def test_conversation_logging_performance(self, shared_context):
        """Benchmark conversation logging performance."""
        msg_count = [0]
        
        def log_conversations():
            for i in range(100):
                shared_context.add_conversation(
                    role="agent",
                    content=f"Message {msg_count[0]}_{i}",
                    metadata={"index": i}
                )
            msg_count[0] += 1
        
        results = self.measure_time(log_conversations, iterations=10)
        self.print_benchmark_results("Log 100 Conversation Entries", results)


class TestIntegrationPerformance(PerformanceBenchmark):
    """Benchmark integrated event bus and shared state performance."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus."""
        return EventBus()
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_multi_agent_coordination_overhead(self, event_bus, shared_context):
        """Benchmark overhead of multi-agent coordination."""
        num_agents = 10
        events_per_agent = 50
        
        # Register agents
        agent_ids = [f"agent_{i}" for i in range(num_agents)]
        for agent_id in agent_ids:
            shared_context.register_agent(agent_id)
        
        # Subscribe agents to events
        counters = {agent_id: 0 for agent_id in agent_ids}
        
        for agent_id in agent_ids:
            def make_handler(aid):
                def handler(event: Event):
                    counters[aid] += 1
                    # Update state
                    shared_context.update_agent_state(aid, current_task="Processing event")
                return handler
            
            event_bus.subscribe(EventType.PERFORMANCE_ALERT, make_handler(agent_id))
        
        # Benchmark coordinated work
        start_time = time.perf_counter()
        
        for agent_id in agent_ids:
            for i in range(events_per_agent):
                # Publish event
                event = Event(
                    event_type=EventType.PERFORMANCE_ALERT,
                    source=agent_id,
                    payload={"index": i}
                )
                event_bus.publish(event)
                
                # Update agent state
                state = shared_context.get_agent_state(agent_id)
                state.metrics.tasks_completed += 1
        
        elapsed = time.perf_counter() - start_time
        
        total_operations = num_agents * events_per_agent
        ops_per_second = total_operations / elapsed
        
        print(f"\n{'='*60}")
        print(f"Multi-Agent Coordination Overhead")
        print(f"{'='*60}")
        print(f"Agents:           {num_agents}")
        print(f"Events/Agent:     {events_per_agent}")
        print(f"Total Operations: {total_operations}")
        print(f"Time Taken:       {elapsed:.3f} s")
        print(f"Throughput:       {ops_per_second:.0f} ops/s")
        print(f"Avg Latency:      {(elapsed/total_operations)*1000:.3f} ms/op")
        print(f"{'='*60}\n")
        
        # Verify all events were processed
        for agent_id in agent_ids:
            # Each agent receives events from all agents
            assert counters[agent_id] == num_agents * events_per_agent
    
    def test_scalability_benchmark(self, event_bus, shared_context):
        """Benchmark system scalability with increasing load."""
        agent_counts = [5, 10, 20, 50]
        results = []
        
        for num_agents in agent_counts:
            event_bus.clear_history()
            shared_context.clear_all()
            
            # Register agents
            agent_ids = [f"agent_{i}" for i in range(num_agents)]
            for agent_id in agent_ids:
                shared_context.register_agent(agent_id)
            
            # Subscribe to events
            for _ in agent_ids:
                def make_handler():
                    def handler(event: Event):
                        pass
                    return handler
                event_bus.subscribe(EventType.CUSTOM, make_handler())
            
            # Benchmark
            events_per_agent = 100
            start_time = time.perf_counter()
            
            for agent_id in agent_ids:
                for i in range(events_per_agent):
                    event = Event(
                        event_type=EventType.CUSTOM,
                        source=agent_id,
                        payload={"index": i}
                    )
                    event_bus.publish(event)
            
            elapsed = time.perf_counter() - start_time
            total_ops = num_agents * events_per_agent
            throughput = total_ops / elapsed
            
            results.append({
                "agents": num_agents,
                "events": total_ops,
                "time_s": elapsed,
                "throughput": throughput
            })
        
        # Print scalability results
        print(f"\n{'='*60}")
        print(f"Scalability Benchmark")
        print(f"{'='*60}")
        print(f"{'Agents':<10} {'Events':<10} {'Time (s)':<12} {'Throughput (ops/s)':<20}")
        print(f"{'-'*60}")
        for r in results:
            print(f"{r['agents']:<10} {r['events']:<10} {r['time_s']:<12.3f} {r['throughput']:<20.0f}")
        print(f"{'='*60}\n")


class TestMemoryUsage:
    """Test memory usage characteristics."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus."""
        return EventBus()
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_event_history_memory_limit(self, event_bus):
        """Verify event history respects memory limits."""
        # Publish many events
        num_events = 5000
        for i in range(num_events):
            event = Event(
                event_type=EventType.CUSTOM,
                source="test",
                payload={"index": i, "data": "x" * 100}
            )
            event_bus.publish(event)
        
        # History should be limited
        history = event_bus.get_history(limit=10000)
        assert len(history) <= 1000  # Default max history size
        
        print(f"\n{'='*60}")
        print(f"Event History Memory Management")
        print(f"{'='*60}")
        print(f"Events Published: {num_events}")
        print(f"History Size:     {len(history)}")
        print(f"Memory Bounded:   {'✓' if len(history) <= 1000 else '✗'}")
        print(f"{'='*60}\n")
    
    def test_shared_state_memory_management(self, shared_context):
        """Test shared state memory management."""
        # Register many agents
        num_agents = 100
        for i in range(num_agents):
            shared_context.register_agent(f"agent_{i}")
        
        # Add lots of changes
        for i in range(5000):
            change = Change(
                change_id=f"change_{i}",
                timestamp=datetime.now(),
                file_path=f"file_{i}.cpp",
                description="Change description"
            )
            shared_context.add_change(change)
        
        # History should be limited
        changes = shared_context.get_recent_changes(limit=10000)
        assert len(changes) <= 1000
        
        print(f"\n{'='*60}")
        print(f"Shared State Memory Management")
        print(f"{'='*60}")
        print(f"Agents Registered: {num_agents}")
        print(f"Changes Recorded:  5000")
        print(f"Changes in Memory: {len(changes)}")
        print(f"Memory Bounded:    {'✓' if len(changes) <= 1000 else '✗'}")
        print(f"{'='*60}\n")
