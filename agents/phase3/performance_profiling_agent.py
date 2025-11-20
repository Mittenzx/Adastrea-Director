"""
Performance Profiling Agent

Continuously monitors game performance, identifies bottlenecks,
and generates optimization recommendations.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import logging
import re

from .base_agent import BaseAutonomousAgent
from .event_bus import Event, EventBus, EventType
from .shared_state import SharedContext

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """
    Performance metrics collected during monitoring.
    
    Attributes:
        timestamp: When metrics were collected
        frame_rate: Current frame rate (FPS)
        memory_usage_mb: Memory usage in megabytes
        cpu_usage_percent: CPU usage percentage
        gpu_usage_percent: GPU usage percentage
        draw_calls: Number of draw calls per frame
        triangles: Number of triangles rendered
    """
    timestamp: datetime
    frame_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    gpu_usage_percent: float
    draw_calls: int = 0
    triangles: int = 0
    
    def is_below_target(self, target_fps: float = 60.0) -> bool:
        """Check if performance is below target."""
        return self.frame_rate < target_fps


@dataclass
class Bottleneck:
    """
    A performance bottleneck identified by analysis.
    
    Attributes:
        bottleneck_type: Type of bottleneck (CPU, GPU, memory, etc.)
        severity: Severity level (low, medium, high, critical)
        description: Human-readable description
        location: Where the bottleneck occurs (if known)
        metrics: Related performance metrics
    """
    bottleneck_type: str
    severity: str
    description: str
    location: Optional[str] = None
    metrics: Optional[PerformanceMetrics] = None


@dataclass
class Recommendation:
    """
    An optimization recommendation.
    
    Attributes:
        title: Short title of the recommendation
        description: Detailed description
        bottleneck: The bottleneck this addresses
        priority: Priority level (low, medium, high)
        estimated_impact: Estimated performance improvement
        implementation_difficulty: How difficult to implement (easy, medium, hard)
    """
    title: str
    description: str
    bottleneck: Bottleneck
    priority: str = "medium"
    estimated_impact: str = "moderate"
    implementation_difficulty: str = "medium"


@dataclass
class PerformanceAnalysis:
    """
    Analysis results from performance profiling.
    
    Attributes:
        timestamp: When analysis was performed
        metrics: The metrics analyzed
        bottlenecks: Identified bottlenecks
        recommendations: Optimization recommendations
        summary: Overall summary of findings
    """
    timestamp: datetime
    metrics: PerformanceMetrics
    bottlenecks: List[Bottleneck]
    recommendations: List[Recommendation]
    summary: str


class PerformanceProfilingAgent(BaseAutonomousAgent):
    """
    Agent that monitors and analyzes game performance.
    
    Capabilities:
    - Monitor frame rate, memory, CPU/GPU utilization
    - Identify performance hotspots
    - Track performance trends over time
    - Generate optimization recommendations
    - Trigger alerts for performance regressions
    - Collect metrics from Unreal Engine via Remote Control API
    """
    
    def __init__(self,
                 event_bus: EventBus,
                 shared_context: SharedContext,
                 target_fps: float = 60.0,
                 memory_threshold_mb: float = 4096.0,
                 remote_control_client = None):
        """
        Initialize the Performance Profiling Agent.
        
        Args:
            event_bus: Event bus for communication
            shared_context: Shared context for coordination
            target_fps: Target frame rate to maintain
            memory_threshold_mb: Memory usage threshold for alerts
            remote_control_client: Optional UnrealRemoteControlClient for UE integration
        """
        super().__init__(
            agent_id="performance_profiling_agent",
            event_bus=event_bus,
            shared_context=shared_context
        )
        
        self.target_fps = target_fps
        self.memory_threshold_mb = memory_threshold_mb
        self._metrics_history: List[PerformanceMetrics] = []
        self._max_history_size = 1000
        self.remote_control_client = remote_control_client
        
        logger.info(f"PerformanceProfilingAgent created (target: {target_fps} FPS, UE integration: {remote_control_client is not None})")
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events."""
        # Subscribe to any performance-related events
        # In a real implementation, this would subscribe to metrics collection events
        pass
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        # Clean up subscriptions
        pass
    
    def _on_start(self) -> None:
        """Initialize profiling on start."""
        logger.info(f"Performance profiling started (target: {self.target_fps} FPS)")
        self._set_current_task("Monitoring performance")
    
    def _on_stop(self) -> None:
        """Clean up on stop."""
        logger.info("Performance profiling stopped")
        self._set_current_task(None)
    
    def collect_metrics(self, 
                       frame_rate: float,
                       memory_usage_mb: float,
                       cpu_usage_percent: float,
                       gpu_usage_percent: float,
                       draw_calls: int = 0,
                       triangles: int = 0) -> PerformanceMetrics:
        """
        Collect performance metrics.
        
        Args:
            frame_rate: Current frame rate
            memory_usage_mb: Memory usage in MB
            cpu_usage_percent: CPU usage percentage
            gpu_usage_percent: GPU usage percentage
            draw_calls: Number of draw calls
            triangles: Number of triangles
            
        Returns:
            The collected metrics
        """
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            frame_rate=frame_rate,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent,
            gpu_usage_percent=gpu_usage_percent,
            draw_calls=draw_calls,
            triangles=triangles
        )
        
        # Store in history
        self._metrics_history.append(metrics)
        if len(self._metrics_history) > self._max_history_size:
            self._metrics_history.pop(0)
        
        # Publish metrics event
        self.event_bus.publish(Event(
            event_type=EventType.PERFORMANCE_METRICS_COLLECTED,
            source=self.agent_id,
            payload={
                'metrics': {
                    'frame_rate': frame_rate,
                    'memory_usage_mb': memory_usage_mb,
                    'cpu_usage_percent': cpu_usage_percent,
                    'gpu_usage_percent': gpu_usage_percent,
                    'draw_calls': draw_calls,
                    'triangles': triangles
                }
            }
        ))
        
        logger.debug(f"Metrics collected: {frame_rate:.1f} FPS, {memory_usage_mb:.1f} MB")
        
        return metrics
    
    def analyze_performance(self, metrics: PerformanceMetrics) -> PerformanceAnalysis:
        """
        Analyze performance metrics to identify issues.
        
        Args:
            metrics: The metrics to analyze
            
        Returns:
            Performance analysis with bottlenecks and recommendations
        """
        self._set_current_task("Analyzing performance")
        
        bottlenecks = self.detect_bottlenecks(metrics)
        recommendations = self.generate_recommendations(bottlenecks)
        
        # Create summary
        summary_parts = []
        if metrics.frame_rate < self.target_fps:
            summary_parts.append(f"Frame rate ({metrics.frame_rate:.1f} FPS) below target ({self.target_fps} FPS)")
        if metrics.memory_usage_mb > self.memory_threshold_mb:
            summary_parts.append(f"High memory usage ({metrics.memory_usage_mb:.1f} MB)")
        if not summary_parts:
            summary_parts.append("Performance within acceptable parameters")
        
        summary = ". ".join(summary_parts)
        
        analysis = PerformanceAnalysis(
            timestamp=datetime.now(),
            metrics=metrics,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            summary=summary
        )
        
        # Check if we should trigger an alert
        if bottlenecks:
            self._trigger_performance_alert(analysis)
        
        self._set_current_task(None)
        self._update_metrics(task_completed=True)
        
        logger.info(f"Performance analysis completed: {len(bottlenecks)} bottlenecks found")
        
        return analysis
    
    def detect_bottlenecks(self, metrics: PerformanceMetrics) -> List[Bottleneck]:
        """
        Detect performance bottlenecks from metrics.
        
        Args:
            metrics: Performance metrics to analyze
            
        Returns:
            List of detected bottlenecks
        """
        bottlenecks = []
        
        # Check frame rate
        if metrics.frame_rate < self.target_fps * 0.8:  # 80% of target
            severity = "critical" if metrics.frame_rate < self.target_fps * 0.5 else "high"
            bottlenecks.append(Bottleneck(
                bottleneck_type="frame_rate",
                severity=severity,
                description=f"Frame rate is {metrics.frame_rate:.1f} FPS, below target of {self.target_fps} FPS",
                metrics=metrics
            ))
        
        # Check memory usage
        if metrics.memory_usage_mb > self.memory_threshold_mb:
            severity = "high" if metrics.memory_usage_mb > self.memory_threshold_mb * 1.2 else "medium"
            bottlenecks.append(Bottleneck(
                bottleneck_type="memory",
                severity=severity,
                description=f"Memory usage is {metrics.memory_usage_mb:.1f} MB, exceeding threshold",
                metrics=metrics
            ))
        
        # Check CPU usage
        if metrics.cpu_usage_percent > 90:
            bottlenecks.append(Bottleneck(
                bottleneck_type="cpu",
                severity="high",
                description=f"CPU usage is {metrics.cpu_usage_percent:.1f}%, nearing maximum",
                metrics=metrics
            ))
        
        # Check GPU usage
        if metrics.gpu_usage_percent > 95:
            bottlenecks.append(Bottleneck(
                bottleneck_type="gpu",
                severity="high",
                description=f"GPU usage is {metrics.gpu_usage_percent:.1f}%, GPU-bound",
                metrics=metrics
            ))
        
        # Check draw calls
        if metrics.draw_calls > 3000:
            bottlenecks.append(Bottleneck(
                bottleneck_type="draw_calls",
                severity="medium",
                description=f"High draw call count ({metrics.draw_calls}), consider batching",
                metrics=metrics
            ))
        
        return bottlenecks
    
    def generate_recommendations(self, bottlenecks: List[Bottleneck]) -> List[Recommendation]:
        """
        Generate optimization recommendations based on bottlenecks.
        
        Args:
            bottlenecks: Detected bottlenecks
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        for bottleneck in bottlenecks:
            if bottleneck.bottleneck_type == "frame_rate":
                recommendations.append(Recommendation(
                    title="Optimize Rendering Pipeline",
                    description="Profile GPU and CPU usage to identify the primary bottleneck. "
                               "Consider reducing draw calls, optimizing materials, or implementing LOD.",
                    bottleneck=bottleneck,
                    priority="high",
                    estimated_impact="high",
                    implementation_difficulty="medium"
                ))
            
            elif bottleneck.bottleneck_type == "memory":
                recommendations.append(Recommendation(
                    title="Reduce Memory Usage",
                    description="Review asset streaming settings, texture compression, and "
                               "implement aggressive garbage collection. Check for memory leaks.",
                    bottleneck=bottleneck,
                    priority="high",
                    estimated_impact="high",
                    implementation_difficulty="medium"
                ))
            
            elif bottleneck.bottleneck_type == "cpu":
                recommendations.append(Recommendation(
                    title="Optimize CPU Performance",
                    description="Profile CPU usage to find hot spots. Consider optimizing "
                               "Blueprint logic, reducing tick frequency, or moving logic to C++.",
                    bottleneck=bottleneck,
                    priority="high",
                    estimated_impact="moderate",
                    implementation_difficulty="hard"
                ))
            
            elif bottleneck.bottleneck_type == "gpu":
                recommendations.append(Recommendation(
                    title="Optimize GPU Performance",
                    description="Review shader complexity, reduce overdraw, optimize post-processing, "
                               "and consider dynamic resolution scaling.",
                    bottleneck=bottleneck,
                    priority="high",
                    estimated_impact="high",
                    implementation_difficulty="medium"
                ))
            
            elif bottleneck.bottleneck_type == "draw_calls":
                recommendations.append(Recommendation(
                    title="Reduce Draw Calls",
                    description="Implement instancing for repeated objects, use mesh merging, "
                               "and enable static mesh batching where possible.",
                    bottleneck=bottleneck,
                    priority="medium",
                    estimated_impact="moderate",
                    implementation_difficulty="easy"
                ))
        
        return recommendations
    
    def _trigger_performance_alert(self, analysis: PerformanceAnalysis) -> None:
        """
        Trigger a performance alert event.
        
        Args:
            analysis: The performance analysis that triggered the alert
        """
        self.event_bus.publish(Event(
            event_type=EventType.PERFORMANCE_ALERT,
            source=self.agent_id,
            payload={
                'summary': analysis.summary,
                'bottleneck_count': len(analysis.bottlenecks),
                'bottlenecks': [
                    {
                        'type': b.bottleneck_type,
                        'severity': b.severity,
                        'description': b.description
                    }
                    for b in analysis.bottlenecks
                ],
                'recommendation_count': len(analysis.recommendations)
            }
        ))
        
        logger.warning(f"Performance alert triggered: {analysis.summary}")
    
    def get_metrics_history(self, limit: int = 100) -> List[PerformanceMetrics]:
        """
        Get recent performance metrics.
        
        Args:
            limit: Maximum number of metrics to return
            
        Returns:
            List of recent metrics
        """
        return self._metrics_history[-limit:]
    
    def get_average_fps(self, duration_seconds: int = 60) -> Optional[float]:
        """
        Calculate average FPS over a time period.
        
        Args:
            duration_seconds: Time period to average over
            
        Returns:
            Average FPS or None if insufficient data
        """
        if not self._metrics_history:
            return None
        
        now = datetime.now()
        recent_metrics = [
            m for m in self._metrics_history
            if (now - m.timestamp).total_seconds() <= duration_seconds
        ]
        
        if not recent_metrics:
            return None
        
        return sum(m.frame_rate for m in recent_metrics) / len(recent_metrics)
    
    def collect_metrics_from_ue(self) -> Optional[PerformanceMetrics]:
        """
        Collect real performance metrics from Unreal Engine via Remote Control API.
        
        Returns:
            PerformanceMetrics: An object containing FPS, memory usage, and GPU statistics.
            None if Remote Control client is not configured or connection fails.
        
        Raises:
            ConnectionError: If Unreal Engine is not connected or metrics cannot be retrieved.
        """
        if self.remote_control_client is None:
            logger.warning("Remote Control client not configured, cannot collect UE metrics")
            return None
        
        try:
            # Execute stat commands to get performance data
            fps_data = self._parse_stat_fps()
            gpu_data = self._parse_stat_gpu()
            memory_data = self._parse_stat_memory()
            
            # Create metrics from parsed data
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                frame_rate=fps_data.get('fps', 0.0),
                memory_usage_mb=memory_data.get('memory_mb', 0.0),
                cpu_usage_percent=fps_data.get('cpu_percent', 0.0),
                gpu_usage_percent=gpu_data.get('gpu_percent', 0.0),
                draw_calls=gpu_data.get('draw_calls', 0),
                triangles=gpu_data.get('triangles', 0)
            )
            
            # Store in history
            self._metrics_history.append(metrics)
            if len(self._metrics_history) > self._max_history_size:
                self._metrics_history.pop(0)
            
            # Publish metrics event
            self.event_bus.publish(Event(
                event_type=EventType.PERFORMANCE_METRICS_COLLECTED,
                source=self.agent_id,
                payload={
                    'metrics': {
                        'frame_rate': metrics.frame_rate,
                        'memory_usage_mb': metrics.memory_usage_mb,
                        'cpu_usage_percent': metrics.cpu_usage_percent,
                        'gpu_usage_percent': metrics.gpu_usage_percent,
                        'draw_calls': metrics.draw_calls,
                        'triangles': metrics.triangles
                    },
                    'source': 'unreal_engine'
                }
            ))
            
            logger.debug(f"UE Metrics collected: {metrics.frame_rate:.1f} FPS, {metrics.memory_usage_mb:.1f} MB")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics from Unreal Engine: {e}")
            return None
    
    def _parse_stat_fps(self) -> dict:
        """
        Execute 'stat fps' command and parse the output.
        
        Returns:
            Dictionary with fps and cpu_percent keys.
        """
        try:
            response = self.remote_control_client.execute_command("stat fps")
            if not response or not response.success:
                return {'fps': 0.0, 'cpu_percent': 0.0}
            
            # Parse stat fps output
            # Example format: "Frame time: 16.67ms (60.00 FPS)"
            output = response.data.get('output', '')
            
            fps_match = re.search(r'(\d+\.?\d*)\s*FPS', output, re.IGNORECASE)
            frame_time_match = re.search(r'(\d+\.?\d*)\s*ms', output, re.IGNORECASE)
            
            fps = float(fps_match.group(1)) if fps_match else 0.0
            
            # Estimate CPU usage based on frame time
            # Rough estimate: frame_time / target_frame_time * 100
            if frame_time_match:
                frame_time_ms = float(frame_time_match.group(1))
                target_frame_time_ms = 1000.0 / self.target_fps
                cpu_percent = min(100.0, (frame_time_ms / target_frame_time_ms) * 100.0)
            else:
                cpu_percent = 0.0
            
            return {'fps': fps, 'cpu_percent': cpu_percent}
            
        except Exception as e:
            logger.error(f"Failed to parse stat fps: {e}")
            return {'fps': 0.0, 'cpu_percent': 0.0}
    
    def _parse_stat_gpu(self) -> dict:
        """
        Execute 'stat gpu' command and parse the output.
        
        Returns:
            Dictionary with gpu_percent, draw_calls, and triangles keys.
        """
        try:
            response = self.remote_control_client.execute_command("stat gpu")
            if not response or not response.success:
                return {'gpu_percent': 0.0, 'draw_calls': 0, 'triangles': 0}
            
            # Parse stat gpu output
            # Example format varies by UE version, look for common patterns
            output = response.data.get('output', '')
            
            # Try to find GPU time
            gpu_time_match = re.search(r'GPU.*?(\d+\.?\d*)\s*ms', output, re.IGNORECASE)
            draw_calls_match = re.search(r'draw.*?calls.*?(\d+)', output, re.IGNORECASE)
            triangles_match = re.search(r'tris.*?(\d+)', output, re.IGNORECASE)
            
            # Estimate GPU usage based on GPU time
            # Rough estimate: gpu_time / target_frame_time * 100
            if gpu_time_match:
                gpu_time_ms = float(gpu_time_match.group(1))
                target_frame_time_ms = 1000.0 / self.target_fps
                gpu_percent = min(100.0, (gpu_time_ms / target_frame_time_ms) * 100.0)
            else:
                gpu_percent = 0.0
            
            draw_calls = int(draw_calls_match.group(1)) if draw_calls_match else 0
            triangles = int(triangles_match.group(1)) if triangles_match else 0
            
            return {
                'gpu_percent': gpu_percent,
                'draw_calls': draw_calls,
                'triangles': triangles
            }
            
        except Exception as e:
            logger.error(f"Failed to parse stat gpu: {e}")
            return {'gpu_percent': 0.0, 'draw_calls': 0, 'triangles': 0}
    
    def _parse_stat_memory(self) -> dict:
        """
        Execute 'stat memory' command and parse the output.
        
        Returns:
            Dictionary with memory_mb key.
        """
        try:
            response = self.remote_control_client.execute_command("stat memory")
            if not response or not response.success:
                return {'memory_mb': 0.0}
            
            # Parse stat memory output
            # Example format: "Physical: 2048 MB"
            output = response.data.get('output', '')
            
            # Look for memory values in MB
            memory_match = re.search(r'Physical.*?(\d+)\s*MB', output, re.IGNORECASE)
            
            if memory_match:
                memory_mb = float(memory_match.group(1))
            else:
                # Try alternate format
                memory_match = re.search(r'(\d+)\s*MB', output, re.IGNORECASE)
                memory_mb = float(memory_match.group(1)) if memory_match else 0.0
            
            return {'memory_mb': memory_mb}
            
        except Exception as e:
            logger.error(f"Failed to parse stat memory: {e}")
            return {'memory_mb': 0.0}
    
    def start_pie_profiling(self, duration_seconds: int = 60) -> Optional[PerformanceAnalysis]:
        """
        Start profiling during a PIE (Play In Editor) session.
        
        Collects performance metrics during PIE and generates analysis.
        
        Args:
            duration_seconds: How long to profile (default: 60 seconds)
        
        Returns:
            PerformanceAnalysis with findings, or None if failed
        """
        if self.remote_control_client is None:
            logger.error("Cannot start PIE profiling without Remote Control client")
            return None
        
        try:
            import time
            
            # Start PIE
            logger.info("Starting PIE for profiling")
            start_response = self.remote_control_client.execute_command("PIE.StartPlaySession")
            if not start_response or not start_response.success:
                logger.error("Failed to start PIE session")
                return None
            
            # Wait for PIE to start
            time.sleep(2)
            
            # Collect metrics during PIE
            logger.info(f"Profiling PIE session for {duration_seconds} seconds")
            collected_metrics = []
            start_time = time.time()
            
            while time.time() - start_time < duration_seconds:
                metrics = self.collect_metrics_from_ue()
                if metrics:
                    collected_metrics.append(metrics)
                time.sleep(1)  # Collect every second
            
            # Stop PIE
            logger.info("Stopping PIE session")
            self.remote_control_client.execute_command("PIE.StopPlaySession")
            
            # Analyze collected metrics
            if not collected_metrics:
                logger.warning("No metrics collected during PIE session")
                return None
            
            # Use the average or worst-case metrics for analysis
            avg_metrics = self._calculate_average_metrics(collected_metrics)
            analysis = self.analyze_performance(avg_metrics)
            
            logger.info(f"PIE profiling complete: {len(collected_metrics)} samples, {len(analysis.bottlenecks)} bottlenecks")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to profile PIE session: {e}")
            # Try to stop PIE if it's running
            try:
                self.remote_control_client.execute_command("PIE.StopPlaySession")
            except:
                pass
            return None
    
    def _calculate_average_metrics(self, metrics_list: List[PerformanceMetrics]) -> PerformanceMetrics:
        """
        Calculate average metrics from a list of metrics.
        
        Args:
            metrics_list: List of performance metrics
        
        Returns:
            Average metrics
        """
        if not metrics_list:
            return PerformanceMetrics(
                timestamp=datetime.now(),
                frame_rate=0.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                gpu_usage_percent=0.0,
                draw_calls=0,
                triangles=0
            )
        
        n = len(metrics_list)
        return PerformanceMetrics(
            timestamp=datetime.now(),
            frame_rate=sum(m.frame_rate for m in metrics_list) / n,
            memory_usage_mb=sum(m.memory_usage_mb for m in metrics_list) / n,
            cpu_usage_percent=sum(m.cpu_usage_percent for m in metrics_list) / n,
            gpu_usage_percent=sum(m.gpu_usage_percent for m in metrics_list) / n,
            draw_calls=int(sum(m.draw_calls for m in metrics_list) / n),
            triangles=int(sum(m.triangles for m in metrics_list) / n)
        )
