"""
Base Autonomous Agent

Provides the foundation for all Phase 3 autonomous agents with
common functionality for monitoring, event handling, and state management.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
import logging

from .event_bus import Event, EventBus, EventType
from .shared_state import AgentState, AgentStatus, SharedContext

logger = logging.getLogger(__name__)


class BaseAutonomousAgent(ABC):
    """
    Base class for all autonomous agents in Phase 3.
    
    Provides common functionality:
    - Event bus integration
    - State management
    - Lifecycle management
    - Error handling
    """
    
    def __init__(self, 
                 agent_id: str,
                 event_bus: EventBus,
                 shared_context: SharedContext):
        """
        Initialize the base autonomous agent.
        
        Args:
            agent_id: Unique identifier for this agent
            event_bus: Event bus for communication
            shared_context: Shared context for coordination
        """
        self.agent_id = agent_id
        self.event_bus = event_bus
        self.shared_context = shared_context
        self._is_running = False
        self._error_count = 0
        self._max_errors = 10
        
        # Register with shared context
        self.state = shared_context.register_agent(agent_id)
        
        logger.info(f"Agent initialized: {agent_id}")
    
    def start(self) -> None:
        """
        Start the agent.
        
        This method handles:
        - State updates
        - Event subscriptions
        - Agent initialization
        """
        if self._is_running:
            logger.warning(f"Agent {self.agent_id} is already running")
            return
        
        try:
            logger.info(f"Starting agent: {self.agent_id}")
            
            # Update state
            self.shared_context.update_agent_state(
                self.agent_id,
                status=AgentStatus.IDLE
            )
            
            # Subscribe to events
            self._subscribe_to_events()
            
            # Perform agent-specific initialization
            self._on_start()
            
            self._is_running = True
            
            # Publish start event
            self.event_bus.publish(Event(
                event_type=EventType.AGENT_STARTED,
                source=self.agent_id,
                payload={'agent_id': self.agent_id}
            ))
            
            logger.info(f"Agent started successfully: {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Error starting agent {self.agent_id}: {e}", exc_info=True)
            self._handle_error(e)
    
    def stop(self) -> None:
        """
        Stop the agent.
        
        This method handles:
        - Cleanup
        - Event unsubscriptions
        - State updates
        """
        if not self._is_running:
            logger.warning(f"Agent {self.agent_id} is not running")
            return
        
        try:
            logger.info(f"Stopping agent: {self.agent_id}")
            
            # Perform agent-specific cleanup
            self._on_stop()
            
            # Unsubscribe from events
            self._unsubscribe_from_events()
            
            # Update state
            self.shared_context.update_agent_state(
                self.agent_id,
                status=AgentStatus.STOPPED,
                current_task=None
            )
            
            self._is_running = False
            
            # Publish stop event
            self.event_bus.publish(Event(
                event_type=EventType.AGENT_STOPPED,
                source=self.agent_id,
                payload={'agent_id': self.agent_id}
            ))
            
            logger.info(f"Agent stopped successfully: {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Error stopping agent {self.agent_id}: {e}", exc_info=True)
    
    def is_running(self) -> bool:
        """Check if the agent is currently running."""
        return self._is_running
    
    def get_status(self) -> AgentStatus:
        """
        Get the current status of the agent.
        
        Returns:
            Current agent status
        """
        state = self.shared_context.get_agent_state(self.agent_id)
        return state.status if state else AgentStatus.STOPPED
    
    def _handle_error(self, error: Exception) -> None:
        """
        Handle an error that occurred in the agent.
        
        Args:
            error: The exception that occurred
        """
        self._error_count += 1
        
        # Update state
        self.shared_context.update_agent_state(
            self.agent_id,
            status=AgentStatus.ERROR
        )
        
        # Update metrics
        state = self.shared_context.get_agent_state(self.agent_id)
        if state:
            state.metrics.tasks_failed += 1
        
        # Publish error event
        self.event_bus.publish(Event(
            event_type=EventType.AGENT_ERROR,
            source=self.agent_id,
            payload={
                'agent_id': self.agent_id,
                'error': str(error),
                'error_count': self._error_count
            }
        ))
        
        # Stop if too many errors
        if self._error_count >= self._max_errors:
            logger.error(f"Agent {self.agent_id} exceeded max errors ({self._max_errors}), stopping")
            self.stop()
    
    def _update_metrics(self, 
                       task_completed: bool = False,
                       completion_time: Optional[float] = None,
                       api_calls: int = 0,
                       tokens: int = 0) -> None:
        """
        Update agent metrics.
        
        Args:
            task_completed: Whether a task was completed
            completion_time: Time taken to complete task (seconds)
            api_calls: Number of API calls made
            tokens: Number of tokens used
        """
        state = self.shared_context.get_agent_state(self.agent_id)
        if not state:
            return
        
        if task_completed:
            state.metrics.tasks_completed += 1
            
            if completion_time is not None:
                # Update average completion time
                total_tasks = state.metrics.tasks_completed
                current_avg = state.metrics.average_completion_time
                state.metrics.average_completion_time = (
                    (current_avg * (total_tasks - 1) + completion_time) / total_tasks
                )
        
        state.metrics.api_calls_made += api_calls
        state.metrics.tokens_used += tokens
        state.metrics.last_activity = datetime.now()
    
    def _set_current_task(self, task: Optional[str]) -> None:
        """
        Set the current task being worked on.
        
        Args:
            task: Description of the current task, or None to clear
        """
        status = AgentStatus.BUSY if task else AgentStatus.IDLE
        self.shared_context.update_agent_state(
            self.agent_id,
            current_task=task,
            status=status
        )
    
    # Abstract methods that subclasses must implement
    
    @abstractmethod
    def _subscribe_to_events(self) -> None:
        """
        Subscribe to relevant events.
        
        Subclasses should override this to subscribe to events they care about.
        """
        pass
    
    @abstractmethod
    def _unsubscribe_from_events(self) -> None:
        """
        Unsubscribe from events.
        
        Subclasses should override this to clean up event subscriptions.
        """
        pass
    
    @abstractmethod
    def _on_start(self) -> None:
        """
        Agent-specific initialization logic.
        
        Called when the agent starts. Subclasses should override
        to perform any necessary setup.
        """
        pass
    
    @abstractmethod
    def _on_stop(self) -> None:
        """
        Agent-specific cleanup logic.
        
        Called when the agent stops. Subclasses should override
        to perform any necessary cleanup.
        """
        pass
