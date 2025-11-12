"""
Phase 3: Autonomous Agents

This module contains the autonomous agent system for proactive monitoring,
bug detection, and code quality analysis.
"""

from .event_bus import EventBus, Event, EventType
from .shared_state import SharedContext, AgentState, AgentStatus
from .base_agent import BaseAutonomousAgent
from .performance_profiling_agent import PerformanceProfilingAgent
from .bug_detection_agent import BugDetectionAgent
from .code_quality_agent import CodeQualityAgent

__all__ = [
    'EventBus',
    'Event',
    'EventType',
    'SharedContext',
    'AgentState',
    'AgentStatus',
    'BaseAutonomousAgent',
    'PerformanceProfilingAgent',
    'BugDetectionAgent',
    'CodeQualityAgent',
]
