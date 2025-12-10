#!/usr/bin/env python3
"""
Project Analytics Module

Collects and analyzes project statistics for debugging and analytics:
- Asset counts (meshes, blueprints, materials, textures)
- Blueprint complexity metrics
- Lines of code (LOC) tracking with history
- Placeholder content detection
- PIE session statistics (FPS, memory, frame time)
- Build time tracking
- Connection health monitoring
"""

import json
import logging
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AssetCounts:
    """Asset count statistics."""
    static_meshes: int = 0
    skeletal_meshes: int = 0
    blueprints: int = 0
    materials: int = 0
    textures: int = 0
    sounds: int = 0
    animations: int = 0
    particles: int = 0
    total: int = 0
    last_updated: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BlueprintStats:
    """Blueprint complexity statistics."""
    total_blueprints: int = 0
    actor_blueprints: int = 0
    component_blueprints: int = 0
    interface_blueprints: int = 0
    function_libraries: int = 0
    avg_node_count: float = 0.0
    max_node_count: int = 0
    total_nodes: int = 0
    last_updated: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class LOCStats:
    """Lines of code statistics with history."""
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    python_lines: int = 0
    cpp_lines: int = 0
    header_lines: int = 0
    blueprint_lines: int = 0
    last_updated: str = ""
    history: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def add_to_history(self):
        """Add current stats to history."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'total': self.total_lines,
            'code': self.code_lines,
            'comments': self.comment_lines
        }
        self.history.append(entry)
        # Keep only last 100 entries
        if len(self.history) > 100:
            self.history = self.history[-100:]


@dataclass
class PlaceholderContent:
    """Placeholder content detection."""
    default_cubes: int = 0
    default_spheres: int = 0
    temp_blueprints: int = 0
    missing_assets: int = 0
    placeholder_materials: int = 0
    placeholder_textures: int = 0
    locations: List[Dict] = field(default_factory=list)
    last_updated: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PIESession:
    """PIE (Play In Editor) session statistics."""
    session_id: str = ""
    start_time: str = ""
    end_time: str = ""
    duration_seconds: float = 0.0
    avg_fps: float = 0.0
    min_fps: float = 0.0
    max_fps: float = 0.0
    avg_frame_time_ms: float = 0.0
    avg_memory_mb: float = 0.0
    peak_memory_mb: float = 0.0
    draw_calls_avg: int = 0
    triangles_avg: int = 0
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ConnectionMetrics:
    """Connection health metrics between VS Code and UE."""
    vscode_connected: bool = False
    vscode_uptime_seconds: float = 0.0
    vscode_reconnect_count: int = 0
    vscode_last_activity: str = ""
    ue_connected: bool = False
    ue_uptime_seconds: float = 0.0
    ue_reconnect_count: int = 0
    ue_last_activity: str = ""
    avg_latency_ms: float = 0.0
    packet_loss_percent: float = 0.0
    last_updated: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BuildMetrics:
    """Build time and compilation metrics."""
    last_build_time_seconds: float = 0.0
    avg_build_time_seconds: float = 0.0
    total_builds: int = 0
    failed_builds: int = 0
    last_build_status: str = "unknown"
    last_build_timestamp: str = ""
    build_history: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def add_build(self, duration: float, success: bool):
        """Add a build to history."""
        self.total_builds += 1
        if not success:
            self.failed_builds += 1
        
        self.last_build_time_seconds = duration
        self.last_build_status = "success" if success else "failed"
        self.last_build_timestamp = datetime.now().isoformat()
        
        # Update average
        if self.total_builds > 0:
            self.avg_build_time_seconds = (
                (self.avg_build_time_seconds * (self.total_builds - 1) + duration) / 
                self.total_builds
            )
        
        # Add to history
        entry = {
            'timestamp': self.last_build_timestamp,
            'duration': duration,
            'success': success
        }
        self.build_history.append(entry)
        # Keep only last 50 builds
        if len(self.build_history) > 50:
            self.build_history = self.build_history[-50:]


class ProjectAnalytics:
    """
    Comprehensive project analytics collector.
    
    Collects and tracks various project metrics for debugging and analysis.
    """
    
    def __init__(self, data_dir: str = "./analytics_data"):
        """
        Initialize analytics collector.
        
        Args:
            data_dir: Directory to store analytics data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize metrics
        self.asset_counts = AssetCounts()
        self.blueprint_stats = BlueprintStats()
        self.loc_stats = LOCStats()
        self.placeholder_content = PlaceholderContent()
        self.connection_metrics = ConnectionMetrics()
        self.build_metrics = BuildMetrics()
        self.pie_sessions: List[PIESession] = []
        
        # Load existing data
        self._load_data()
        
        # Background update thread
        self._update_thread = None
        self._stop_updates = False
    
    def _load_data(self):
        """Load analytics data from disk."""
        try:
            data_file = self.data_dir / "analytics.json"
            if data_file.exists():
                with open(data_file, 'r') as f:
                    data = json.load(f)
                
                # Restore from saved data
                if 'asset_counts' in data:
                    self.asset_counts = AssetCounts(**data['asset_counts'])
                if 'blueprint_stats' in data:
                    self.blueprint_stats = BlueprintStats(**data['blueprint_stats'])
                if 'loc_stats' in data:
                    self.loc_stats = LOCStats(**data['loc_stats'])
                if 'placeholder_content' in data:
                    self.placeholder_content = PlaceholderContent(**data['placeholder_content'])
                if 'connection_metrics' in data:
                    self.connection_metrics = ConnectionMetrics(**data['connection_metrics'])
                if 'build_metrics' in data:
                    self.build_metrics = BuildMetrics(**data['build_metrics'])
                if 'pie_sessions' in data:
                    self.pie_sessions = [PIESession(**s) for s in data['pie_sessions']]
                
                logger.info("Analytics data loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load analytics data: {e}")
    
    def _save_data(self):
        """Save analytics data to disk."""
        try:
            data = {
                'asset_counts': self.asset_counts.to_dict(),
                'blueprint_stats': self.blueprint_stats.to_dict(),
                'loc_stats': self.loc_stats.to_dict(),
                'placeholder_content': self.placeholder_content.to_dict(),
                'connection_metrics': self.connection_metrics.to_dict(),
                'build_metrics': self.build_metrics.to_dict(),
                'pie_sessions': [s.to_dict() for s in self.pie_sessions[-50:]]  # Keep last 50
            }
            
            data_file = self.data_dir / "analytics.json"
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Analytics data saved")
        except Exception as e:
            logger.error(f"Error saving analytics data: {e}")
    
    def update_asset_counts(self, counts: Dict[str, int]):
        """Update asset counts."""
        self.asset_counts.static_meshes = counts.get('static_meshes', 0)
        self.asset_counts.skeletal_meshes = counts.get('skeletal_meshes', 0)
        self.asset_counts.blueprints = counts.get('blueprints', 0)
        self.asset_counts.materials = counts.get('materials', 0)
        self.asset_counts.textures = counts.get('textures', 0)
        self.asset_counts.sounds = counts.get('sounds', 0)
        self.asset_counts.animations = counts.get('animations', 0)
        self.asset_counts.particles = counts.get('particles', 0)
        self.asset_counts.total = sum([
            self.asset_counts.static_meshes,
            self.asset_counts.skeletal_meshes,
            self.asset_counts.blueprints,
            self.asset_counts.materials,
            self.asset_counts.textures,
            self.asset_counts.sounds,
            self.asset_counts.animations,
            self.asset_counts.particles
        ])
        self.asset_counts.last_updated = datetime.now().isoformat()
        self._save_data()
    
    def update_blueprint_stats(self, stats: Dict[str, Any]):
        """Update blueprint statistics."""
        self.blueprint_stats.total_blueprints = stats.get('total', 0)
        self.blueprint_stats.actor_blueprints = stats.get('actors', 0)
        self.blueprint_stats.component_blueprints = stats.get('components', 0)
        self.blueprint_stats.interface_blueprints = stats.get('interfaces', 0)
        self.blueprint_stats.function_libraries = stats.get('libraries', 0)
        self.blueprint_stats.avg_node_count = stats.get('avg_nodes', 0.0)
        self.blueprint_stats.max_node_count = stats.get('max_nodes', 0)
        self.blueprint_stats.total_nodes = stats.get('total_nodes', 0)
        self.blueprint_stats.last_updated = datetime.now().isoformat()
        self._save_data()
    
    def update_loc_stats(self, total: int, code: int, comments: int, blank: int,
                        python: int = 0, cpp: int = 0, header: int = 0, blueprint: int = 0):
        """Update lines of code statistics."""
        self.loc_stats.total_lines = total
        self.loc_stats.code_lines = code
        self.loc_stats.comment_lines = comments
        self.loc_stats.blank_lines = blank
        self.loc_stats.python_lines = python
        self.loc_stats.cpp_lines = cpp
        self.loc_stats.header_lines = header
        self.loc_stats.blueprint_lines = blueprint
        self.loc_stats.last_updated = datetime.now().isoformat()
        self.loc_stats.add_to_history()
        self._save_data()
    
    def update_placeholder_content(self, placeholders: Dict[str, Any]):
        """Update placeholder content detection."""
        self.placeholder_content.default_cubes = placeholders.get('cubes', 0)
        self.placeholder_content.default_spheres = placeholders.get('spheres', 0)
        self.placeholder_content.temp_blueprints = placeholders.get('temp_bps', 0)
        self.placeholder_content.missing_assets = placeholders.get('missing', 0)
        self.placeholder_content.placeholder_materials = placeholders.get('placeholder_mats', 0)
        self.placeholder_content.placeholder_textures = placeholders.get('placeholder_texs', 0)
        self.placeholder_content.locations = placeholders.get('locations', [])
        self.placeholder_content.last_updated = datetime.now().isoformat()
        self._save_data()
    
    def add_pie_session(self, session: PIESession):
        """Add a PIE session to history."""
        self.pie_sessions.append(session)
        # Keep only last 100 sessions
        if len(self.pie_sessions) > 100:
            self.pie_sessions = self.pie_sessions[-100:]
        self._save_data()
    
    def update_connection_metrics(self, vscode_connected: bool = None, ue_connected: bool = None,
                                  latency_ms: float = None):
        """Update connection metrics."""
        now = datetime.now().isoformat()
        
        if vscode_connected is not None:
            if vscode_connected and not self.connection_metrics.vscode_connected:
                # Connection established
                self.connection_metrics.vscode_reconnect_count += 1
            self.connection_metrics.vscode_connected = vscode_connected
            self.connection_metrics.vscode_last_activity = now
        
        if ue_connected is not None:
            if ue_connected and not self.connection_metrics.ue_connected:
                # Connection established
                self.connection_metrics.ue_reconnect_count += 1
            self.connection_metrics.ue_connected = ue_connected
            self.connection_metrics.ue_last_activity = now
        
        if latency_ms is not None:
            # Update running average
            if self.connection_metrics.avg_latency_ms == 0:
                self.connection_metrics.avg_latency_ms = latency_ms
            else:
                self.connection_metrics.avg_latency_ms = (
                    self.connection_metrics.avg_latency_ms * 0.9 + latency_ms * 0.1
                )
        
        self.connection_metrics.last_updated = now
        self._save_data()
    
    def add_build(self, duration: float, success: bool):
        """Add a build to metrics."""
        self.build_metrics.add_build(duration, success)
        self._save_data()
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all analytics metrics."""
        return {
            'asset_counts': self.asset_counts.to_dict(),
            'blueprint_stats': self.blueprint_stats.to_dict(),
            'loc_stats': self.loc_stats.to_dict(),
            'placeholder_content': self.placeholder_content.to_dict(),
            'connection_metrics': self.connection_metrics.to_dict(),
            'build_metrics': self.build_metrics.to_dict(),
            'pie_sessions': [s.to_dict() for s in self.pie_sessions[-10:]],  # Last 10
            'last_updated': datetime.now().isoformat()
        }
    
    def export_to_json(self, filepath: str):
        """Export all analytics data to JSON file."""
        data = self.get_all_metrics()
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Analytics data exported to {filepath}")
    
    def calculate_health_score(self) -> float:
        """
        Calculate an overall project health score (0-100).
        
        Based on:
        - Placeholder content ratio (lower is better)
        - Build success rate
        - Connection stability
        - Asset organization
        """
        score = 100.0
        
        # Placeholder penalty (up to -30 points)
        if self.asset_counts.total > 0:
            total_placeholders = (
                self.placeholder_content.default_cubes +
                self.placeholder_content.default_spheres +
                self.placeholder_content.temp_blueprints +
                self.placeholder_content.missing_assets
            )
            placeholder_ratio = total_placeholders / max(self.asset_counts.total, 1)
            score -= min(30, placeholder_ratio * 100)
        
        # Build success rate (up to -25 points for failures)
        if self.build_metrics.total_builds > 0:
            failure_rate = self.build_metrics.failed_builds / self.build_metrics.total_builds
            score -= min(25, failure_rate * 100)
        
        # Connection stability (up to -20 points)
        total_reconnects = (
            self.connection_metrics.vscode_reconnect_count +
            self.connection_metrics.ue_reconnect_count
        )
        if total_reconnects > 10:
            score -= min(20, (total_reconnects - 10) * 2)
        
        # PIE performance (up to -25 points for low FPS)
        if self.pie_sessions:
            recent_sessions = self.pie_sessions[-5:]  # Last 5 sessions
            valid_fps_sessions = [s.avg_fps for s in recent_sessions if s.avg_fps > 0]
            if valid_fps_sessions:
                avg_fps = sum(valid_fps_sessions) / len(valid_fps_sessions)
                if avg_fps < 30:
                    score -= 25
                elif avg_fps < 45:
                    score -= 15
                elif avg_fps < 60:
                    score -= 5
        
        return max(0, min(100, score))
