"""
Phase 3: Autonomous Agents

This module contains the autonomous agent system for proactive monitoring,
bug detection, and code quality analysis.
"""

from .event_bus import EventBus, Event, EventType
from .shared_state import (
    SharedContext,
    AgentState,
    AgentStatus,
    AgentMetrics,
    ProjectInfo,
    CodeStructure,
    Change
)
from .base_agent import BaseAutonomousAgent
from .performance_profiling_agent import (
    PerformanceProfilingAgent,
    PerformanceMetrics,
    Bottleneck,
    Recommendation,
    PerformanceAnalysis
)
from .bug_detection_agent import (
    BugDetectionAgent,
    Anomaly,
    Crash,
    TestResults,
    Regression,
    BugReport
)
from .code_quality_agent import (
    CodeQualityAgent,
    CodeSmell,
    Violation,
    Refactoring,
    QualityReport,
    TechnicalDebtScore
)

__all__ = [
    # Event Bus
    'EventBus',
    'Event',
    'EventType',
    # Shared State
    'SharedContext',
    'AgentState',
    'AgentStatus',
    'AgentMetrics',
    'ProjectInfo',
    'CodeStructure',
    'Change',
    # Base Agent
    'BaseAutonomousAgent',
    # Performance Profiling
    'PerformanceProfilingAgent',
    'PerformanceMetrics',
    'Bottleneck',
    'Recommendation',
    'PerformanceAnalysis',
    # Bug Detection
    'BugDetectionAgent',
    'Anomaly',
    'Crash',
    'TestResults',
    'Regression',
    'BugReport',
    # Code Quality
    'CodeQualityAgent',
    'CodeSmell',
    'Violation',
    'Refactoring',
    'QualityReport',
    'TechnicalDebtScore',
]
