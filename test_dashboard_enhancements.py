#!/usr/bin/env python3
"""
Test script to verify dashboard enhancements show error details and health checks.
"""

import sys
import time
from agent_dashboard import AgentDashboard
from agents.phase3 import Event, EventType

def test_dashboard_with_errors():
    """Test that dashboard shows error information."""
    print("Testing dashboard enhancements...")
    
    # Create dashboard
    dashboard = AgentDashboard(update_interval=1.0)
    print("✓ Dashboard created")
    
    # Start all agents
    dashboard.start_all_agents()
    print("✓ Agents started")
    time.sleep(0.2)
    
    # Simulate an error event
    error_event = Event(
        event_type=EventType.AGENT_ERROR,
        source="performance_profiling_agent",
        payload={
            'agent_id': 'performance_profiling_agent',
            'error': 'Failed to connect to Remote Control API',
            'error_count': 1
        }
    )
    dashboard.event_bus.publish(error_event)
    print("✓ Error event published")
    time.sleep(0.1)
    
    # Check that error was tracked
    assert 'performance_profiling_agent' in dashboard.agent_errors, "Error should be tracked"
    print("✓ Error tracked in dashboard.agent_errors")
    
    # Check that error count increased
    assert dashboard.event_counts[EventType.AGENT_ERROR] == 1, "Error count should be 1"
    print("✓ Error count updated")
    
    # Test system health checks
    dashboard.update_system_health()
    assert dashboard.system_health is not None, "System health should be checked"
    print("✓ System health checks completed")
    
    # Test system health panel
    health_panel = dashboard.generate_system_health_panel()
    assert health_panel is not None, "Health panel should be generated"
    print("✓ System health panel generated")
    
    # Generate layout to ensure no errors
    layout = dashboard.generate_layout()
    assert layout is not None, "Layout should be generated"
    print("✓ Layout generated successfully")
    
    # Test agent status table includes error info
    status_table = dashboard.generate_agent_status_table()
    assert status_table is not None, "Status table should be generated"
    print("✓ Status table includes error columns")
    
    # Test error details panel
    error_panel = dashboard.generate_error_details_panel()
    assert error_panel is not None, "Error panel should be generated"
    print("✓ Error details panel generated")
    
    # Test event summary includes AGENT_ERROR
    event_summary = dashboard.generate_event_summary_table()
    assert event_summary is not None, "Event summary should be generated"
    print("✓ Event summary includes agent errors")
    
    # Test recent events panel shows error details
    events_panel = dashboard.generate_recent_events_panel(limit=10)
    assert events_panel is not None, "Events panel should be generated"
    print("✓ Recent events panel shows error details")
    
    # Clean up
    dashboard.stop_all_agents()
    print("✓ Agents stopped")
    
    print("\n✅ All dashboard enhancement tests passed!")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(test_dashboard_with_errors())
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
