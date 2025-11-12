"""
Tests for the Performance Profiling Agent.
"""

import pytest
from datetime import datetime
from agents.phase3.event_bus import EventBus, EventType
from agents.phase3.shared_state import SharedContext, AgentStatus
from agents.phase3.performance_profiling_agent import (
    PerformanceProfilingAgent,
    PerformanceMetrics,
    Bottleneck,
    Recommendation
)


class TestPerformanceMetrics:
    """Tests for PerformanceMetrics class."""
    
    def test_metrics_creation(self):
        """Test creating performance metrics."""
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            frame_rate=60.0,
            memory_usage_mb=2048.0,
            cpu_usage_percent=50.0,
            gpu_usage_percent=75.0,
            draw_calls=1500,
            triangles=500000
        )
        
        assert metrics.frame_rate == 60.0
        assert metrics.memory_usage_mb == 2048.0
        assert not metrics.is_below_target(60.0)
        assert metrics.is_below_target(70.0)


class TestPerformanceProfilingAgent:
    """Tests for PerformanceProfilingAgent class."""
    
    @pytest.fixture
    def setup(self):
        """Set up test fixtures."""
        event_bus = EventBus()
        shared_context = SharedContext()
        agent = PerformanceProfilingAgent(
            event_bus=event_bus,
            shared_context=shared_context,
            target_fps=60.0,
            memory_threshold_mb=4096.0
        )
        return agent, event_bus, shared_context
    
    def test_agent_initialization(self, setup):
        """Test agent initialization."""
        agent, event_bus, shared_context = setup
        
        assert agent.agent_id == "performance_profiling_agent"
        assert agent.target_fps == 60.0
        assert agent.memory_threshold_mb == 4096.0
        assert not agent.is_running()
    
    def test_agent_start_stop(self, setup):
        """Test starting and stopping the agent."""
        agent, event_bus, shared_context = setup
        
        # Start agent
        agent.start()
        assert agent.is_running()
        assert agent.get_status() == AgentStatus.BUSY  # Should be monitoring
        
        # Stop agent
        agent.stop()
        assert not agent.is_running()
        assert agent.get_status() == AgentStatus.STOPPED
    
    def test_collect_metrics(self, setup):
        """Test collecting performance metrics."""
        agent, event_bus, shared_context = setup
        
        # Collect events
        collected_events = []
        event_bus.subscribe(EventType.PERFORMANCE_METRICS_COLLECTED, 
                          lambda e: collected_events.append(e))
        
        # Collect metrics
        metrics = agent.collect_metrics(
            frame_rate=55.0,
            memory_usage_mb=3000.0,
            cpu_usage_percent=60.0,
            gpu_usage_percent=80.0,
            draw_calls=2000,
            triangles=800000
        )
        
        assert metrics.frame_rate == 55.0
        assert metrics.memory_usage_mb == 3000.0
        
        # Event should be published
        assert len(collected_events) == 1
        assert collected_events[0].event_type == EventType.PERFORMANCE_METRICS_COLLECTED
    
    def test_detect_bottlenecks_low_fps(self, setup):
        """Test detecting low frame rate bottleneck."""
        agent, event_bus, shared_context = setup
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            frame_rate=30.0,  # Below 60 FPS target
            memory_usage_mb=2000.0,
            cpu_usage_percent=50.0,
            gpu_usage_percent=50.0
        )
        
        bottlenecks = agent.detect_bottlenecks(metrics)
        
        assert len(bottlenecks) > 0
        assert any(b.bottleneck_type == "frame_rate" for b in bottlenecks)
    
    def test_detect_bottlenecks_high_memory(self, setup):
        """Test detecting high memory usage bottleneck."""
        agent, event_bus, shared_context = setup
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            frame_rate=60.0,
            memory_usage_mb=5000.0,  # Above 4096 MB threshold
            cpu_usage_percent=50.0,
            gpu_usage_percent=50.0
        )
        
        bottlenecks = agent.detect_bottlenecks(metrics)
        
        assert len(bottlenecks) > 0
        assert any(b.bottleneck_type == "memory" for b in bottlenecks)
    
    def test_detect_bottlenecks_high_cpu(self, setup):
        """Test detecting high CPU usage bottleneck."""
        agent, event_bus, shared_context = setup
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            frame_rate=60.0,
            memory_usage_mb=2000.0,
            cpu_usage_percent=95.0,  # Very high CPU
            gpu_usage_percent=50.0
        )
        
        bottlenecks = agent.detect_bottlenecks(metrics)
        
        assert len(bottlenecks) > 0
        assert any(b.bottleneck_type == "cpu" for b in bottlenecks)
    
    def test_detect_bottlenecks_high_draw_calls(self, setup):
        """Test detecting high draw call bottleneck."""
        agent, event_bus, shared_context = setup
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            frame_rate=60.0,
            memory_usage_mb=2000.0,
            cpu_usage_percent=50.0,
            gpu_usage_percent=50.0,
            draw_calls=4000  # High draw calls
        )
        
        bottlenecks = agent.detect_bottlenecks(metrics)
        
        assert len(bottlenecks) > 0
        assert any(b.bottleneck_type == "draw_calls" for b in bottlenecks)
    
    def test_generate_recommendations(self, setup):
        """Test generating recommendations from bottlenecks."""
        agent, event_bus, shared_context = setup
        
        bottleneck = Bottleneck(
            bottleneck_type="frame_rate",
            severity="high",
            description="Low FPS"
        )
        
        recommendations = agent.generate_recommendations([bottleneck])
        
        assert len(recommendations) > 0
        assert isinstance(recommendations[0], Recommendation)
        assert recommendations[0].bottleneck == bottleneck
    
    def test_analyze_performance(self, setup):
        """Test full performance analysis."""
        agent, event_bus, shared_context = setup
        
        # Collect alert events
        alerts = []
        event_bus.subscribe(EventType.PERFORMANCE_ALERT,
                          lambda e: alerts.append(e))
        
        # Create metrics with issues
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            frame_rate=40.0,  # Below target
            memory_usage_mb=5000.0,  # Above threshold
            cpu_usage_percent=50.0,
            gpu_usage_percent=50.0
        )
        
        analysis = agent.analyze_performance(metrics)
        
        assert analysis is not None
        assert len(analysis.bottlenecks) > 0
        assert len(analysis.recommendations) > 0
        assert "below target" in analysis.summary.lower()
        
        # Alert should be triggered
        assert len(alerts) > 0
    
    def test_analyze_performance_no_issues(self, setup):
        """Test analysis with good performance."""
        agent, event_bus, shared_context = setup
        
        alerts = []
        event_bus.subscribe(EventType.PERFORMANCE_ALERT,
                          lambda e: alerts.append(e))
        
        # Good metrics
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            frame_rate=60.0,
            memory_usage_mb=2000.0,
            cpu_usage_percent=50.0,
            gpu_usage_percent=50.0
        )
        
        analysis = agent.analyze_performance(metrics)
        
        assert len(analysis.bottlenecks) == 0
        assert len(analysis.recommendations) == 0
        assert "acceptable" in analysis.summary.lower()
        
        # No alert should be triggered
        assert len(alerts) == 0
    
    def test_metrics_history(self, setup):
        """Test metrics history tracking."""
        agent, event_bus, shared_context = setup
        
        # Collect multiple metrics
        for i in range(5):
            agent.collect_metrics(
                frame_rate=60.0 - i,
                memory_usage_mb=2000.0 + (i * 100),
                cpu_usage_percent=50.0,
                gpu_usage_percent=50.0
            )
        
        history = agent.get_metrics_history()
        assert len(history) == 5
        assert history[0].frame_rate == 60.0
        assert history[4].frame_rate == 56.0
    
    def test_average_fps_calculation(self, setup):
        """Test average FPS calculation."""
        agent, event_bus, shared_context = setup
        
        # Collect metrics with known FPS values
        agent.collect_metrics(60.0, 2000.0, 50.0, 50.0)
        agent.collect_metrics(50.0, 2000.0, 50.0, 50.0)
        agent.collect_metrics(40.0, 2000.0, 50.0, 50.0)
        
        avg_fps = agent.get_average_fps(duration_seconds=60)
        
        # Average should be 50.0
        assert avg_fps == 50.0
    
    def test_average_fps_no_data(self, setup):
        """Test average FPS with no data."""
        agent, event_bus, shared_context = setup
        
        avg_fps = agent.get_average_fps()
        assert avg_fps is None
