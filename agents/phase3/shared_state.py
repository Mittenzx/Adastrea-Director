"""
Shared State Management for Agent Coordination

Provides a centralized state management system for agents to share
project context, metrics, and coordination information.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Status of an autonomous agent."""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class AgentMetrics:
    """
    Metrics tracked for each agent.
    
    Attributes:
        tasks_completed: Number of tasks completed
        tasks_failed: Number of tasks that failed
        average_completion_time: Average time to complete tasks (seconds)
        api_calls_made: Number of API calls made
        tokens_used: Total tokens consumed
        last_activity: Timestamp of last activity
    """
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_completion_time: float = 0.0
    api_calls_made: int = 0
    tokens_used: int = 0
    last_activity: Optional[datetime] = None
    
    def success_rate(self) -> float:
        """Calculate the success rate as a percentage."""
        total = self.tasks_completed + self.tasks_failed
        if total == 0:
            return 0.0
        return (self.tasks_completed / total) * 100.0


@dataclass
class AgentState:
    """
    State information for an autonomous agent.
    
    Attributes:
        agent_id: Unique identifier for the agent
        status: Current status of the agent
        current_task: Description of current task (if any)
        memory: Agent-specific memory/context
        metrics: Performance metrics
        started_at: When the agent was started
        updated_at: When the state was last updated
    """
    agent_id: str
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    memory: Dict[str, Any] = field(default_factory=dict)
    metrics: AgentMetrics = field(default_factory=AgentMetrics)
    started_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def update(self, **kwargs) -> None:
        """Update agent state fields and timestamp."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()


@dataclass
class ProjectInfo:
    """
    Information about the current project.
    
    Attributes:
        name: Project name
        root_path: Path to project root
        language: Primary programming language
        framework: Framework or engine (e.g., "Unreal Engine 5.3")
        metadata: Additional project metadata
    """
    name: str
    root_path: str
    language: str = "Unknown"
    framework: str = "Unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeStructure:
    """
    Information about code structure.
    
    Attributes:
        total_files: Number of code files
        total_lines: Total lines of code
        languages: Languages used in the project
        file_tree: Simplified file tree structure
    """
    total_files: int = 0
    total_lines: int = 0
    languages: List[str] = field(default_factory=list)
    file_tree: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Change:
    """
    Represents a code change.
    
    Attributes:
        change_id: Unique identifier
        timestamp: When the change was made
        file_path: Path to changed file
        description: Description of the change
        author: Who made the change
    """
    change_id: str
    timestamp: datetime
    file_path: str
    description: str
    author: str = "system"


class SharedContext:
    """
    Centralized state management for agent coordination.
    
    Provides access to project information, agent states, and shared context
    that agents need to coordinate their activities.
    """
    
    def __init__(self):
        """Initialize the shared context."""
        self._agent_states: Dict[str, AgentState] = {}
        self._project_info: Optional[ProjectInfo] = None
        self._code_structure: Optional[CodeStructure] = None
        self._recent_changes: List[Change] = []
        self._conversation_history: List[Dict[str, Any]] = []
        self._shared_data: Dict[str, Any] = {}
        self._max_history_size: int = 1000
        logger.info("SharedContext initialized")
    
    # Agent State Management
    
    def register_agent(self, agent_id: str) -> AgentState:
        """
        Register a new agent.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            The created agent state
        """
        if agent_id in self._agent_states:
            logger.warning(f"Agent {agent_id} already registered, returning existing state")
            return self._agent_states[agent_id]
        
        state = AgentState(agent_id=agent_id)
        self._agent_states[agent_id] = state
        logger.info(f"Agent registered: {agent_id}")
        return state
    
    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """
        Get the state of a specific agent.
        
        Args:
            agent_id: The agent identifier
            
        Returns:
            Agent state or None if not found
        """
        return self._agent_states.get(agent_id)
    
    def update_agent_state(self, agent_id: str, **kwargs) -> None:
        """
        Update an agent's state.
        
        Args:
            agent_id: The agent identifier
            **kwargs: Fields to update
        """
        if agent_id not in self._agent_states:
            logger.warning(f"Agent {agent_id} not registered, cannot update state")
            return
        
        self._agent_states[agent_id].update(**kwargs)
        logger.debug(f"Agent state updated: {agent_id}")
    
    def get_all_agent_states(self) -> List[AgentState]:
        """
        Get states of all registered agents.
        
        Returns:
            List of all agent states
        """
        return list(self._agent_states.values())
    
    # Project Information
    
    def set_project_info(self, project_info: ProjectInfo) -> None:
        """
        Set the project information.
        
        Args:
            project_info: Project information to store
        """
        self._project_info = project_info
        logger.info(f"Project info set: {project_info.name}")
    
    def get_project_info(self) -> Optional[ProjectInfo]:
        """
        Get the project information.
        
        Returns:
            Project information or None
        """
        return self._project_info
    
    # Code Structure
    
    def set_code_structure(self, code_structure: CodeStructure) -> None:
        """
        Set the code structure information.
        
        Args:
            code_structure: Code structure to store
        """
        self._code_structure = code_structure
        logger.info("Code structure updated")
    
    def get_code_structure(self) -> Optional[CodeStructure]:
        """
        Get the code structure information.
        
        Returns:
            Code structure or None
        """
        return self._code_structure
    
    # Change Tracking
    
    def add_change(self, change: Change) -> None:
        """
        Record a code change.
        
        Args:
            change: The change to record
        """
        self._recent_changes.append(change)
        if len(self._recent_changes) > self._max_history_size:
            self._recent_changes.pop(0)
        logger.debug(f"Change recorded: {change.file_path}")
    
    def get_recent_changes(self, limit: int = 100) -> List[Change]:
        """
        Get recent code changes.
        
        Args:
            limit: Maximum number of changes to return
            
        Returns:
            List of recent changes
        """
        return self._recent_changes[-limit:]
    
    # Conversation History
    
    def add_conversation(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a conversation entry.
        
        Args:
            role: Role (e.g., "user", "agent", "system")
            content: Conversation content
            metadata: Additional metadata
        """
        entry = {
            'timestamp': datetime.now(),
            'role': role,
            'content': content,
            'metadata': metadata or {}
        }
        self._conversation_history.append(entry)
        if len(self._conversation_history) > self._max_history_size:
            self._conversation_history.pop(0)
    
    def get_conversation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of conversation entries
        """
        return self._conversation_history[-limit:]
    
    # Shared Data
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in shared context.
        
        Args:
            key: The key to set
            value: The value to store
        """
        self._shared_data[key] = value
        logger.debug(f"Shared data set: {key}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from shared context.
        
        Args:
            key: The key to retrieve
            default: Default value if key not found
            
        Returns:
            The stored value or default
        """
        return self._shared_data.get(key, default)
    
    def delete(self, key: str) -> None:
        """
        Delete a value from shared context.
        
        Args:
            key: The key to delete
        """
        if key in self._shared_data:
            del self._shared_data[key]
            logger.debug(f"Shared data deleted: {key}")
    
    def clear_all(self) -> None:
        """Clear all shared data (for testing)."""
        self._agent_states.clear()
        self._recent_changes.clear()
        self._conversation_history.clear()
        self._shared_data.clear()
        logger.info("SharedContext cleared")
