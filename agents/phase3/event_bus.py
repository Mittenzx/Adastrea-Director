"""
Event Bus for Agent Communication

Provides a central message bus for agents to publish and subscribe to events.
Enables decoupled, asynchronous communication between autonomous agents.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events that can be published on the bus."""
    # Performance events
    PERFORMANCE_ALERT = "performance_alert"
    PERFORMANCE_METRICS_COLLECTED = "performance_metrics_collected"
    
    # Bug detection events
    BUG_DETECTED = "bug_detected"
    CRASH_DETECTED = "crash_detected"
    
    # Code quality events
    CODE_QUALITY_ISSUE = "code_quality_issue"
    REFACTORING_OPPORTUNITY = "refactoring_opportunity"
    
    # Testing events
    TEST_COMPLETED = "test_completed"
    TEST_FAILED = "test_failed"
    
    # System events
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    AGENT_ERROR = "agent_error"
    
    # Generic events
    CUSTOM = "custom"


@dataclass
class Event:
    """
    An event that can be published and subscribed to on the event bus.
    
    Attributes:
        event_type: The type of event
        source: The agent or component that published the event
        payload: Event-specific data
        timestamp: When the event was created
        event_id: Unique identifier for this event
        correlation_id: Optional ID to correlate related events
    """
    event_type: EventType
    source: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    correlation_id: Optional[str] = None
    
    def __str__(self) -> str:
        return f"Event({self.event_type.value}, source={self.source}, id={self.event_id[:8]})"


class EventBus:
    """
    Central event bus for agent communication.
    
    Provides publish/subscribe functionality for agents to communicate
    asynchronously without tight coupling.
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._event_history: List[Event] = []
        self._max_history_size: int = 1000
        logger.info("EventBus initialized")
    
    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: The event to publish
        """
        logger.debug(f"Publishing event: {event}")
        
        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)
        
        # Notify subscribers
        subscribers = self._subscribers.get(event.event_type, [])
        for handler in subscribers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event.event_type}: {e}", exc_info=True)
    
    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: The type of event to subscribe to
            handler: Callback function to handle the event
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
        logger.debug(f"Handler subscribed to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """
        Unsubscribe from events of a specific type.
        
        Args:
            event_type: The type of event to unsubscribe from
            handler: The callback function to remove
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
                logger.debug(f"Handler unsubscribed from {event_type.value}")
            except ValueError:
                logger.warning(f"Handler not found for {event_type.value}")
    
    def get_history(self, 
                    event_type: Optional[EventType] = None,
                    source: Optional[str] = None,
                    limit: int = 100) -> List[Event]:
        """
        Retrieve event history with optional filtering.
        
        Args:
            event_type: Filter by event type
            source: Filter by event source
            limit: Maximum number of events to return
            
        Returns:
            List of events matching the filters
        """
        events = self._event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if source:
            events = [e for e in events if e.source == source]
        
        return events[-limit:]
    
    def clear_history(self) -> None:
        """Clear the event history."""
        self._event_history.clear()
        logger.info("Event history cleared")
    
    def get_subscriber_count(self, event_type: EventType) -> int:
        """
        Get the number of subscribers for an event type.
        
        Args:
            event_type: The event type to check
            
        Returns:
            Number of subscribers
        """
        return len(self._subscribers.get(event_type, []))
    
    def get_all_event_types(self) -> List[EventType]:
        """
        Get all event types that have subscribers.
        
        Returns:
            List of event types with active subscribers
        """
        return list(self._subscribers.keys())
