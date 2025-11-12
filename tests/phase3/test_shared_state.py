"""
Tests for the Shared State Management system.
"""

import pytest
from datetime import datetime
from agents.phase3.shared_state import (
    AgentState,
    AgentStatus,
    AgentMetrics,
    SharedContext,
    ProjectInfo,
    CodeStructure,
    Change
)


class TestAgentMetrics:
    """Tests for AgentMetrics class."""
    
    def test_metrics_initialization(self):
        """Test metrics initialization with defaults."""
        metrics = AgentMetrics()
        
        assert metrics.tasks_completed == 0
        assert metrics.tasks_failed == 0
        assert metrics.average_completion_time == 0.0
        assert metrics.api_calls_made == 0
        assert metrics.tokens_used == 0
        assert metrics.last_activity is None
    
    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        metrics = AgentMetrics(tasks_completed=8, tasks_failed=2)
        assert metrics.success_rate() == 80.0
        
        # Test with no tasks
        empty_metrics = AgentMetrics()
        assert empty_metrics.success_rate() == 0.0
        
        # Test with 100% success
        perfect_metrics = AgentMetrics(tasks_completed=10, tasks_failed=0)
        assert perfect_metrics.success_rate() == 100.0


class TestAgentState:
    """Tests for AgentState class."""
    
    def test_state_creation(self):
        """Test creating agent state."""
        state = AgentState(agent_id="test_agent")
        
        assert state.agent_id == "test_agent"
        assert state.status == AgentStatus.IDLE
        assert state.current_task is None
        assert isinstance(state.memory, dict)
        assert isinstance(state.metrics, AgentMetrics)
        assert isinstance(state.started_at, datetime)
    
    def test_state_update(self):
        """Test updating agent state."""
        state = AgentState(agent_id="test_agent")
        original_update_time = state.updated_at
        
        # Update state
        state.update(status=AgentStatus.BUSY, current_task="Processing")
        
        assert state.status == AgentStatus.BUSY
        assert state.current_task == "Processing"
        assert state.updated_at > original_update_time


class TestSharedContext:
    """Tests for SharedContext class."""
    
    @pytest.fixture
    def context(self):
        """Create a fresh shared context for each test."""
        return SharedContext()
    
    def test_initialization(self, context):
        """Test shared context initialization."""
        assert context is not None
        assert len(context.get_all_agent_states()) == 0
    
    def test_register_agent(self, context):
        """Test registering an agent."""
        state = context.register_agent("agent1")
        
        assert state.agent_id == "agent1"
        assert state.status == AgentStatus.IDLE
        
        # Verify it's stored
        stored_state = context.get_agent_state("agent1")
        assert stored_state == state
    
    def test_register_duplicate_agent(self, context):
        """Test registering the same agent twice."""
        state1 = context.register_agent("agent1")
        state2 = context.register_agent("agent1")
        
        # Should return the same state
        assert state1 == state2
    
    def test_get_agent_state(self, context):
        """Test retrieving agent state."""
        context.register_agent("agent1")
        
        state = context.get_agent_state("agent1")
        assert state is not None
        assert state.agent_id == "agent1"
        
        # Non-existent agent
        missing_state = context.get_agent_state("nonexistent")
        assert missing_state is None
    
    def test_update_agent_state(self, context):
        """Test updating agent state."""
        context.register_agent("agent1")
        
        context.update_agent_state(
            "agent1",
            status=AgentStatus.BUSY,
            current_task="Working on task"
        )
        
        state = context.get_agent_state("agent1")
        assert state.status == AgentStatus.BUSY
        assert state.current_task == "Working on task"
    
    def test_update_nonexistent_agent(self, context):
        """Test updating a non-existent agent (should not crash)."""
        # Should not raise exception
        context.update_agent_state("nonexistent", status=AgentStatus.BUSY)
    
    def test_get_all_agent_states(self, context):
        """Test getting all agent states."""
        context.register_agent("agent1")
        context.register_agent("agent2")
        context.register_agent("agent3")
        
        states = context.get_all_agent_states()
        assert len(states) == 3
        agent_ids = [s.agent_id for s in states]
        assert "agent1" in agent_ids
        assert "agent2" in agent_ids
        assert "agent3" in agent_ids
    
    def test_project_info(self, context):
        """Test setting and getting project info."""
        project_info = ProjectInfo(
            name="Test Project",
            root_path="/path/to/project",
            language="Python",
            framework="Unreal Engine 5.3"
        )
        
        context.set_project_info(project_info)
        retrieved = context.get_project_info()
        
        assert retrieved == project_info
        assert retrieved.name == "Test Project"
    
    def test_code_structure(self, context):
        """Test setting and getting code structure."""
        code_structure = CodeStructure(
            total_files=100,
            total_lines=10000,
            languages=["Python", "C++"],
            file_tree={"src": ["main.py", "utils.py"]}
        )
        
        context.set_code_structure(code_structure)
        retrieved = context.get_code_structure()
        
        assert retrieved == code_structure
        assert retrieved.total_files == 100
    
    def test_change_tracking(self, context):
        """Test adding and retrieving changes."""
        change1 = Change(
            change_id="change1",
            timestamp=datetime.now(),
            file_path="src/main.py",
            description="Fixed bug",
            author="developer"
        )
        
        change2 = Change(
            change_id="change2",
            timestamp=datetime.now(),
            file_path="src/utils.py",
            description="Added feature",
            author="developer"
        )
        
        context.add_change(change1)
        context.add_change(change2)
        
        changes = context.get_recent_changes()
        assert len(changes) == 2
        assert changes[0] == change1
        assert changes[1] == change2
    
    def test_change_limit(self, context):
        """Test change history limit."""
        for i in range(10):
            change = Change(
                change_id=f"change{i}",
                timestamp=datetime.now(),
                file_path=f"file{i}.py",
                description=f"Change {i}"
            )
            context.add_change(change)
        
        # Get with limit
        recent = context.get_recent_changes(limit=5)
        assert len(recent) == 5
        # Should be most recent
        assert recent[0].change_id == "change5"
    
    def test_conversation_history(self, context):
        """Test conversation history tracking."""
        context.add_conversation("user", "Hello", {"source": "cli"})
        context.add_conversation("agent", "Hi there!", {"source": "agent_system"})
        
        history = context.get_conversation_history()
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "agent"
    
    def test_conversation_limit(self, context):
        """Test conversation history limit."""
        for i in range(10):
            context.add_conversation("user", f"Message {i}")
        
        limited = context.get_conversation_history(limit=5)
        assert len(limited) == 5
        assert limited[0]["content"] == "Message 5"
    
    def test_shared_data(self, context):
        """Test shared data storage."""
        context.set("key1", "value1")
        context.set("key2", {"nested": "data"})
        
        assert context.get("key1") == "value1"
        assert context.get("key2") == {"nested": "data"}
        assert context.get("nonexistent") is None
        assert context.get("nonexistent", "default") == "default"
    
    def test_delete_shared_data(self, context):
        """Test deleting shared data."""
        context.set("key1", "value1")
        assert context.get("key1") == "value1"
        
        context.delete("key1")
        assert context.get("key1") is None
        
        # Deleting non-existent key should not crash
        context.delete("nonexistent")
    
    def test_clear_all(self, context):
        """Test clearing all context."""
        # Add various data
        context.register_agent("agent1")
        context.set("key", "value")
        context.add_conversation("user", "test")
        context.add_change(Change(
            change_id="change1",
            timestamp=datetime.now(),
            file_path="test.py",
            description="test"
        ))
        
        # Clear everything
        context.clear_all()
        
        assert len(context.get_all_agent_states()) == 0
        assert context.get("key") is None
        assert len(context.get_conversation_history()) == 0
        assert len(context.get_recent_changes()) == 0
