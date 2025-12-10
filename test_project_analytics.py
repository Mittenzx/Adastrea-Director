#!/usr/bin/env python3
"""
Tests for Project Analytics Module
"""

import pytest
import os
import json
import tempfile
from project_analytics import (
    ProjectAnalytics,
    AssetCounts,
    BlueprintStats,
    LOCStats,
    PlaceholderContent,
    PIESession,
    ConnectionMetrics,
    BuildMetrics
)


@pytest.fixture
def temp_analytics_dir():
    """Create a temporary directory for analytics data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def analytics(temp_analytics_dir):
    """Create a ProjectAnalytics instance with temporary directory."""
    return ProjectAnalytics(data_dir=temp_analytics_dir)


def test_asset_counts_initialization():
    """Test AssetCounts dataclass initialization."""
    counts = AssetCounts()
    assert counts.static_meshes == 0
    assert counts.blueprints == 0
    assert counts.total == 0


def test_blueprint_stats_initialization():
    """Test BlueprintStats dataclass initialization."""
    stats = BlueprintStats()
    assert stats.total_blueprints == 0
    assert stats.actor_blueprints == 0
    assert stats.avg_node_count == 0.0


def test_loc_stats_initialization():
    """Test LOCStats dataclass initialization."""
    stats = LOCStats()
    assert stats.total_lines == 0
    assert stats.code_lines == 0
    assert stats.history == []


def test_loc_stats_add_to_history():
    """Test adding LOC stats to history."""
    stats = LOCStats(total_lines=1000, code_lines=800, comment_lines=150, blank_lines=50)
    stats.add_to_history()
    
    assert len(stats.history) == 1
    assert stats.history[0]['total'] == 1000
    assert stats.history[0]['code'] == 800


def test_placeholder_content_initialization():
    """Test PlaceholderContent dataclass initialization."""
    content = PlaceholderContent()
    assert content.default_cubes == 0
    assert content.locations == []


def test_pie_session_initialization():
    """Test PIESession dataclass initialization."""
    session = PIESession(
        session_id="test_123",
        avg_fps=60.0,
        avg_memory_mb=512.0
    )
    assert session.session_id == "test_123"
    assert session.avg_fps == 60.0
    assert session.avg_memory_mb == 512.0


def test_connection_metrics_initialization():
    """Test ConnectionMetrics dataclass initialization."""
    metrics = ConnectionMetrics()
    assert not metrics.vscode_connected
    assert not metrics.ue_connected
    assert metrics.vscode_reconnect_count == 0


def test_build_metrics_initialization():
    """Test BuildMetrics dataclass initialization."""
    metrics = BuildMetrics()
    assert metrics.total_builds == 0
    assert metrics.failed_builds == 0
    assert metrics.build_history == []


def test_build_metrics_add_build():
    """Test adding builds to BuildMetrics."""
    metrics = BuildMetrics()
    
    # Add successful build
    metrics.add_build(45.5, True)
    assert metrics.total_builds == 1
    assert metrics.failed_builds == 0
    assert metrics.last_build_time_seconds == 45.5
    assert metrics.last_build_status == "success"
    
    # Add failed build
    metrics.add_build(30.2, False)
    assert metrics.total_builds == 2
    assert metrics.failed_builds == 1
    assert metrics.last_build_status == "failed"
    
    # Check average
    assert metrics.avg_build_time_seconds == (45.5 + 30.2) / 2


def test_project_analytics_initialization(analytics):
    """Test ProjectAnalytics initialization."""
    assert analytics.data_dir.exists()
    assert isinstance(analytics.asset_counts, AssetCounts)
    assert isinstance(analytics.blueprint_stats, BlueprintStats)
    assert isinstance(analytics.loc_stats, LOCStats)


def test_update_asset_counts(analytics):
    """Test updating asset counts."""
    counts = {
        'static_meshes': 100,
        'blueprints': 50,
        'materials': 75,
        'textures': 200
    }
    
    analytics.update_asset_counts(counts)
    
    assert analytics.asset_counts.static_meshes == 100
    assert analytics.asset_counts.blueprints == 50
    assert analytics.asset_counts.materials == 75
    assert analytics.asset_counts.textures == 200
    assert analytics.asset_counts.total == 425  # Sum of all


def test_update_blueprint_stats(analytics):
    """Test updating blueprint statistics."""
    stats = {
        'total': 50,
        'actors': 30,
        'components': 15,
        'interfaces': 5,
        'avg_nodes': 45.5,
        'max_nodes': 200
    }
    
    analytics.update_blueprint_stats(stats)
    
    assert analytics.blueprint_stats.total_blueprints == 50
    assert analytics.blueprint_stats.actor_blueprints == 30
    assert analytics.blueprint_stats.avg_node_count == 45.5
    assert analytics.blueprint_stats.max_node_count == 200


def test_update_loc_stats(analytics):
    """Test updating LOC statistics."""
    analytics.update_loc_stats(
        total=10000,
        code=8000,
        comments=1500,
        blank=500,
        python=3000,
        cpp=5000
    )
    
    assert analytics.loc_stats.total_lines == 10000
    assert analytics.loc_stats.code_lines == 8000
    assert analytics.loc_stats.comment_lines == 1500
    assert analytics.loc_stats.python_lines == 3000
    assert analytics.loc_stats.cpp_lines == 5000
    assert len(analytics.loc_stats.history) == 1


def test_update_placeholder_content(analytics):
    """Test updating placeholder content."""
    placeholders = {
        'cubes': 5,
        'spheres': 3,
        'temp_bps': 10,
        'missing': 2,
        'locations': [
            {'type': 'cube', 'name': 'DefaultCube_1', 'location': '(0,0,0)'}
        ]
    }
    
    analytics.update_placeholder_content(placeholders)
    
    assert analytics.placeholder_content.default_cubes == 5
    assert analytics.placeholder_content.default_spheres == 3
    assert analytics.placeholder_content.temp_blueprints == 10
    assert len(analytics.placeholder_content.locations) == 1


def test_add_pie_session(analytics):
    """Test adding PIE sessions."""
    session1 = PIESession(
        session_id="test_1",
        avg_fps=60.0,
        avg_memory_mb=512.0,
        duration_seconds=300.0
    )
    
    session2 = PIESession(
        session_id="test_2",
        avg_fps=55.0,
        avg_memory_mb=480.0,
        duration_seconds=250.0
    )
    
    analytics.add_pie_session(session1)
    analytics.add_pie_session(session2)
    
    assert len(analytics.pie_sessions) == 2
    assert analytics.pie_sessions[0].session_id == "test_1"
    assert analytics.pie_sessions[1].session_id == "test_2"


def test_update_connection_metrics(analytics):
    """Test updating connection metrics."""
    # Connect VS Code
    analytics.update_connection_metrics(vscode_connected=True)
    assert analytics.connection_metrics.vscode_connected == True
    assert analytics.connection_metrics.vscode_reconnect_count == 1
    
    # Connect UE
    analytics.update_connection_metrics(ue_connected=True)
    assert analytics.connection_metrics.ue_connected == True
    assert analytics.connection_metrics.ue_reconnect_count == 1
    
    # Update latency
    analytics.update_connection_metrics(latency_ms=15.5)
    assert analytics.connection_metrics.avg_latency_ms == 15.5


def test_add_build(analytics):
    """Test adding builds."""
    analytics.add_build(60.0, True)
    analytics.add_build(45.0, True)
    analytics.add_build(75.0, False)
    
    assert analytics.build_metrics.total_builds == 3
    assert analytics.build_metrics.failed_builds == 1
    assert analytics.build_metrics.last_build_time_seconds == 75.0
    assert analytics.build_metrics.last_build_status == "failed"


def test_get_all_metrics(analytics):
    """Test getting all metrics."""
    # Set up some data
    analytics.update_asset_counts({'static_meshes': 10, 'blueprints': 5})
    analytics.update_loc_stats(1000, 800, 150, 50)
    
    metrics = analytics.get_all_metrics()
    
    assert 'asset_counts' in metrics
    assert 'blueprint_stats' in metrics
    assert 'loc_stats' in metrics
    assert 'placeholder_content' in metrics
    assert 'connection_metrics' in metrics
    assert 'build_metrics' in metrics
    assert 'pie_sessions' in metrics
    assert 'last_updated' in metrics


def test_export_to_json(analytics, temp_analytics_dir):
    """Test exporting analytics to JSON."""
    # Set up some data
    analytics.update_asset_counts({'static_meshes': 10})
    
    export_path = os.path.join(temp_analytics_dir, "export.json")
    analytics.export_to_json(export_path)
    
    assert os.path.exists(export_path)
    
    # Verify content
    with open(export_path, 'r') as f:
        data = json.load(f)
    
    assert 'asset_counts' in data
    assert data['asset_counts']['static_meshes'] == 10


def test_calculate_health_score_perfect(analytics):
    """Test health score calculation for perfect project."""
    # Perfect project: no placeholders, all builds successful, stable connections
    analytics.update_asset_counts({'static_meshes': 100, 'blueprints': 50})
    analytics.update_placeholder_content({'cubes': 0, 'spheres': 0, 'temp_bps': 0, 'missing': 0})
    analytics.add_build(60.0, True)
    analytics.add_build(55.0, True)
    analytics.update_connection_metrics(vscode_connected=True)
    analytics.update_connection_metrics(ue_connected=True)
    
    score = analytics.calculate_health_score()
    assert score >= 95  # Should be very high


def test_calculate_health_score_with_issues(analytics):
    """Test health score calculation with various issues."""
    # Project with issues
    analytics.update_asset_counts({'static_meshes': 100, 'blueprints': 50})
    
    # Lots of placeholders
    analytics.update_placeholder_content({
        'cubes': 20,
        'spheres': 15,
        'temp_bps': 10,
        'missing': 5
    })
    
    # Some failed builds
    analytics.add_build(60.0, True)
    analytics.add_build(55.0, False)
    analytics.add_build(50.0, False)
    
    # Multiple reconnections
    for _ in range(15):
        analytics.update_connection_metrics(vscode_connected=True)
    
    score = analytics.calculate_health_score()
    assert score < 80  # Should be lower due to issues


def test_data_persistence(temp_analytics_dir):
    """Test that analytics data persists across instances."""
    # Create first instance and add data
    analytics1 = ProjectAnalytics(data_dir=temp_analytics_dir)
    analytics1.update_asset_counts({'static_meshes': 42, 'blueprints': 13})
    analytics1.update_loc_stats(5000, 4000, 800, 200)
    
    # Create second instance - should load existing data
    analytics2 = ProjectAnalytics(data_dir=temp_analytics_dir)
    
    assert analytics2.asset_counts.static_meshes == 42
    assert analytics2.asset_counts.blueprints == 13
    assert analytics2.loc_stats.total_lines == 5000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
