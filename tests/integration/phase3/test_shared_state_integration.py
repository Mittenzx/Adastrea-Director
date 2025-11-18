"""
Integration tests for Shared State Management with Multiple Agents.

Tests shared state behavior under concurrent access, consistency,
and coordination scenarios.
"""

import pytest
import threading
import time
from datetime import datetime
from typing import List

from agents.phase3.shared_state import (
    SharedContext,
    AgentState,
    AgentStatus,
    ProjectInfo,
    CodeStructure,
    Change
)


class TestSharedStateConsistency:
    """Test state consistency with multiple agents."""
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_concurrent_agent_registration(self, shared_context):
        """Test concurrent agent registration."""
        num_threads = 20
        agents_per_thread = 10
        
        def register_agents(thread_id):
            for i in range(agents_per_thread):
                agent_id = f"thread_{thread_id}_agent_{i}"
                shared_context.register_agent(agent_id)
        
        # Start threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=register_agents, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify all agents were registered
        states = shared_context.get_all_agent_states()
        assert len(states) == num_threads * agents_per_thread
    
    def test_concurrent_state_updates(self, shared_context):
        """Test concurrent state updates to the same agent."""
        agent_id = "test_agent"
        shared_context.register_agent(agent_id)
        
        num_threads = 10
        updates_per_thread = 50
        
        def update_worker():
            for i in range(updates_per_thread):
                shared_context.update_agent_state(
                    agent_id,
                    status=AgentStatus.BUSY,
                    current_task=f"Task {i}"
                )
                time.sleep(0.001)
        
        # Start concurrent updates
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=update_worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Agent should still be in valid state
        state = shared_context.get_agent_state(agent_id)
        assert state is not None
        assert state.agent_id == agent_id
        # Status should be one of the updated values
        assert state.status in [AgentStatus.BUSY, AgentStatus.IDLE]
    
    def test_concurrent_shared_data_access(self, shared_context):
        """Test concurrent access to shared data."""
        num_threads = 10
        operations_per_thread = 100
        
        def data_worker(thread_id):
            for i in range(operations_per_thread):
                # Set data
                shared_context.set(f"thread_{thread_id}_key_{i}", {
                    "thread": thread_id,
                    "value": i,
                    "timestamp": datetime.now()
                })
                
                # Get data
                data = shared_context.get(f"thread_{thread_id}_key_{i}")
                assert data is not None
                assert data["thread"] == thread_id
                assert data["value"] == i
        
        # Run concurrent operations
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=data_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify all data was stored
        for thread_id in range(num_threads):
            for i in range(operations_per_thread):
                key = f"thread_{thread_id}_key_{i}"
                data = shared_context.get(key)
                assert data is not None
                assert data["thread"] == thread_id


class TestProjectInfoManagement:
    """Test project information management."""
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_project_info_sharing(self, shared_context):
        """Test multiple agents accessing project info."""
        # Set project info
        project_info = ProjectInfo(
            name="Test Game",
            root_path="/path/to/game",
            language="C++",
            framework="Unreal Engine 5.3"
        )
        shared_context.set_project_info(project_info)
        
        # Simulate multiple agents reading it
        num_readers = 20
        read_results = []
        lock = threading.Lock()
        
        def reader():
            info = shared_context.get_project_info()
            with lock:
                read_results.append(info)
        
        threads = []
        for _ in range(num_readers):
            thread = threading.Thread(target=reader)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All readers should get the same info
        assert len(read_results) == num_readers
        for info in read_results:
            assert info.name == "Test Game"
            assert info.framework == "Unreal Engine 5.3"
    
    def test_code_structure_updates(self, shared_context):
        """Test code structure updates."""
        # Initial structure
        structure = CodeStructure(
            total_files=100,
            total_lines=10000,
            languages=["C++", "Python"],
            file_tree={"Source": ["Main.cpp", "Utils.cpp"]}
        )
        shared_context.set_code_structure(structure)
        
        # Verify retrieval
        retrieved = shared_context.get_code_structure()
        assert retrieved.total_files == 100
        assert "C++" in retrieved.languages
        
        # Update structure
        new_structure = CodeStructure(
            total_files=150,
            total_lines=15000,
            languages=["C++", "Python", "Blueprint"],
            file_tree={"Source": ["Main.cpp", "Utils.cpp", "New.cpp"]}
        )
        shared_context.set_code_structure(new_structure)
        
        # Verify update
        retrieved = shared_context.get_code_structure()
        assert retrieved.total_files == 150
        assert "Blueprint" in retrieved.languages


class TestChangeTracking:
    """Test change tracking functionality."""
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_concurrent_change_recording(self, shared_context):
        """Test recording changes from multiple agents concurrently."""
        num_agents = 10
        changes_per_agent = 50
        
        def record_changes(agent_id):
            for i in range(changes_per_agent):
                change = Change(
                    change_id=f"{agent_id}_change_{i}",
                    timestamp=datetime.now(),
                    file_path=f"src/file_{i}.cpp",
                    description=f"Change {i} by {agent_id}",
                    author=agent_id
                )
                shared_context.add_change(change)
        
        # Start recording threads
        threads = []
        for i in range(num_agents):
            agent_id = f"agent_{i}"
            thread = threading.Thread(target=record_changes, args=(agent_id,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Get recent changes
        changes = shared_context.get_recent_changes(limit=1000)
        
        # Should have changes from all agents (limited by history size)
        assert len(changes) > 0
        
        # Verify changes from different agents are present
        authors = set(c.author for c in changes)
        assert len(authors) > 1  # Multiple agents contributed
    
    def test_change_history_limit(self, shared_context):
        """Test that change history respects limit."""
        # Add many changes
        for i in range(200):
            change = Change(
                change_id=f"change_{i}",
                timestamp=datetime.now(),
                file_path=f"file_{i}.cpp",
                description=f"Change {i}"
            )
            shared_context.add_change(change)
        
        # Get limited history
        recent_10 = shared_context.get_recent_changes(limit=10)
        recent_50 = shared_context.get_recent_changes(limit=50)
        
        assert len(recent_10) == 10
        assert len(recent_50) == 50
        
        # Most recent changes should be at the end
        assert recent_10[-1].change_id == "change_199"
        assert recent_50[-1].change_id == "change_199"


class TestConversationHistory:
    """Test conversation history functionality."""
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_conversation_recording(self, shared_context):
        """Test recording conversation history."""
        # Add conversation entries
        shared_context.add_conversation("user", "What's the frame rate?")
        shared_context.add_conversation("agent", "Current FPS is 60", {"agent": "perf_agent"})
        shared_context.add_conversation("user", "Any bugs detected?")
        shared_context.add_conversation("agent", "Found 3 issues", {"agent": "bug_agent"})
        
        # Get history
        history = shared_context.get_conversation_history()
        
        assert len(history) == 4
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "agent"
        assert history[1]["metadata"]["agent"] == "perf_agent"
    
    def test_concurrent_conversation_logging(self, shared_context):
        """Test concurrent conversation logging."""
        num_threads = 10
        messages_per_thread = 20
        
        def logger(thread_id):
            for i in range(messages_per_thread):
                shared_context.add_conversation(
                    role=f"agent_{thread_id}",
                    content=f"Message {i}",
                    metadata={"thread": thread_id, "index": i}
                )
        
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=logger, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Get history
        history = shared_context.get_conversation_history(limit=500)
        
        # Should have messages from all threads
        roles = set(entry["role"] for entry in history)
        assert len(roles) == num_threads


class TestAgentMetricsAggregation:
    """Test agent metrics aggregation."""
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_aggregate_metrics_across_agents(self, shared_context):
        """Test collecting metrics from multiple agents."""
        # Register multiple agents
        num_agents = 5
        for i in range(num_agents):
            agent_id = f"agent_{i}"
            shared_context.register_agent(agent_id)
            
            # Simulate work
            state = shared_context.get_agent_state(agent_id)
            state.metrics.tasks_completed = 10 + i
            state.metrics.tasks_failed = i
            state.metrics.api_calls_made = 100 * (i + 1)
            state.metrics.tokens_used = 1000 * (i + 1)
        
        # Aggregate metrics
        all_states = shared_context.get_all_agent_states()
        
        total_completed = sum(s.metrics.tasks_completed for s in all_states)
        total_failed = sum(s.metrics.tasks_failed for s in all_states)
        total_api_calls = sum(s.metrics.api_calls_made for s in all_states)
        total_tokens = sum(s.metrics.tokens_used for s in all_states)
        
        assert total_completed == 60  # 10+11+12+13+14
        assert total_failed == 10  # 0+1+2+3+4
        assert total_api_calls == 1500  # 100+200+300+400+500
        assert total_tokens == 15000  # 1000+2000+3000+4000+5000
        
        # Calculate average success rate
        success_rates = [s.metrics.success_rate() for s in all_states]
        avg_success_rate = sum(success_rates) / len(success_rates)
        assert avg_success_rate > 0


class TestStateCleaning:
    """Test state cleanup and management."""
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_clear_all(self, shared_context):
        """Test clearing all state."""
        # Populate with data
        shared_context.register_agent("agent1")
        shared_context.register_agent("agent2")
        shared_context.set("key1", "value1")
        shared_context.add_conversation("user", "test")
        shared_context.add_change(Change(
            change_id="change1",
            timestamp=datetime.now(),
            file_path="test.cpp",
            description="test"
        ))
        
        # Verify data exists
        assert len(shared_context.get_all_agent_states()) == 2
        assert shared_context.get("key1") is not None
        assert len(shared_context.get_conversation_history()) == 1
        assert len(shared_context.get_recent_changes()) == 1
        
        # Clear all
        shared_context.clear_all()
        
        # Verify everything is cleared
        assert len(shared_context.get_all_agent_states()) == 0
        assert shared_context.get("key1") is None
        assert len(shared_context.get_conversation_history()) == 0
        assert len(shared_context.get_recent_changes()) == 0
    
    def test_delete_shared_data(self, shared_context):
        """Test deleting specific shared data."""
        # Set multiple keys
        for i in range(10):
            shared_context.set(f"key_{i}", f"value_{i}")
        
        # Delete some keys
        shared_context.delete("key_0")
        shared_context.delete("key_5")
        shared_context.delete("key_9")
        
        # Verify deletions
        assert shared_context.get("key_0") is None
        assert shared_context.get("key_5") is None
        assert shared_context.get("key_9") is None
        
        # Verify others still exist
        assert shared_context.get("key_1") == "value_1"
        assert shared_context.get("key_4") == "value_4"


class TestStateSnapshots:
    """Test taking snapshots of shared state."""
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_agent_state_snapshot(self, shared_context):
        """Test capturing agent state at a point in time."""
        # Register agents and do work
        agent1 = shared_context.register_agent("agent1")
        agent2 = shared_context.register_agent("agent2")
        
        agent1.metrics.tasks_completed = 10
        agent1.status = AgentStatus.BUSY
        
        agent2.metrics.tasks_completed = 5
        agent2.status = AgentStatus.IDLE
        
        # Capture snapshot
        snapshot_time = datetime.now()
        snapshot = {
            "timestamp": snapshot_time,
            "agents": [
                {
                    "agent_id": state.agent_id,
                    "status": state.status.value,
                    "tasks_completed": state.metrics.tasks_completed
                }
                for state in shared_context.get_all_agent_states()
            ]
        }
        
        # Continue work
        agent1.metrics.tasks_completed = 20
        agent2.metrics.tasks_completed = 15
        
        # Verify snapshot preserved old state
        assert snapshot["agents"][0]["tasks_completed"] == 10
        assert snapshot["agents"][1]["tasks_completed"] == 5
        
        # Verify current state is different
        current_agent1 = shared_context.get_agent_state("agent1")
        assert current_agent1.metrics.tasks_completed == 20
