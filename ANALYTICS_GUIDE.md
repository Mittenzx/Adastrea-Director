# Analytics Dashboard Guide

## Overview

The Adastrea Director Analytics Dashboard provides comprehensive project statistics and debugging insights to help you monitor and optimize your Unreal Engine game development workflow.

## Features

### 1. Project Health Score (0-100)

The health score is an overall indicator of your project's quality and stability, calculated based on:

- **Placeholder Content** (up to -30 points): Measures the ratio of temporary/placeholder assets
- **Build Success Rate** (up to -25 points): Tracks build failures over time
- **Connection Stability** (up to -20 points): Monitors reconnection frequency
- **PIE Performance** (up to -25 points): Evaluates gameplay FPS metrics

**Interpretation:**
- 80-100: Excellent - Project is in great shape
- 60-79: Good - Minor issues to address
- 40-59: Fair - Several improvements needed
- 0-39: Needs Attention - Critical issues require immediate action

### 2. Asset Inventory

Tracks all assets in your UE project by type:

- **Static Meshes**: 3D models for level geometry
- **Skeletal Meshes**: Animated character models
- **Blueprints**: Visual scripting assets
- **Materials**: Shader definitions
- **Textures**: 2D images and maps
- **Sounds**: Audio files
- **Animations**: Animation sequences
- **Particles**: Visual effects
- **Total Assets**: Sum of all asset types

**Use Cases:**
- Monitor project growth over time
- Identify asset-heavy categories
- Track content creation progress
- Detect unusual asset count changes

### 3. Blueprint Analysis

Detailed statistics about Blueprint assets:

- **Total Blueprints**: All blueprint assets
- **Actor Blueprints**: Blueprints that can be placed in levels
- **Component Blueprints**: Reusable component blueprints
- **Interface Blueprints**: Blueprint interfaces
- **Function Libraries**: Blueprint function libraries
- **Average Nodes**: Mean node count per blueprint
- **Max Nodes**: Largest blueprint by node count

**Benefits:**
- Identify overly complex blueprints
- Monitor blueprint organization
- Track blueprint creation trends
- Find blueprints that may need refactoring

### 4. Code Metrics

Lines of code (LOC) tracking with historical data:

- **Total Lines**: All lines including blanks
- **Code Lines**: Actual code (excluding comments/blanks)
- **Comment Lines**: Documentation and comments
- **Blank Lines**: Empty lines for formatting
- **Python**: Python script lines
- **C++**: C++ source code lines
- **Headers**: C++ header file lines
- **Blueprint Scripts**: Blueprint graph node equivalents

**Features:**
- Historical tracking of code growth
- Language distribution breakdown
- Comment ratio analysis
- Code density metrics

### 5. Placeholder Content Detection

Automatically identifies temporary/placeholder content:

- **Default Cubes**: Basic cube primitives
- **Default Spheres**: Basic sphere primitives
- **Temp Blueprints**: Blueprints with "temp" or "test" in name
- **Missing Assets**: Assets that failed to load
- **Placeholder Materials**: Materials marked as placeholders
- **Placeholder Textures**: Temporary textures

**Why It Matters:**
- Ensure production-ready assets
- Track content replacement progress
- Identify forgotten temporary content
- Maintain professional quality standards

### 6. Connection Health

Monitors the health of connections between tools:

- **VS Code Connected**: Connection status to VS Code extension
- **VS Code Uptime**: How long VS Code has been connected
- **VS Code Reconnects**: Number of connection interruptions
- **UE Connected**: Connection status to Unreal Engine
- **UE Uptime**: How long UE has been connected
- **UE Reconnects**: Number of UE connection interruptions
- **Avg Latency**: Average communication delay in milliseconds

**Use Cases:**
- Diagnose connection issues
- Monitor integration stability
- Track network performance
- Identify connectivity patterns

### 7. PIE Sessions (Play In Editor)

Performance metrics from PIE testing:

- **Total Sessions**: Number of PIE sessions recorded
- **Average FPS**: Mean frames per second across sessions
- **Average Frame Time**: Mean time per frame in milliseconds
- **Average Memory**: Mean memory usage during gameplay
- **Peak Memory**: Highest memory usage recorded

**Analysis:**
- Track performance over time
- Identify performance regressions
- Compare session performance
- Monitor memory usage trends

### 8. Build Statistics

Compilation and build metrics:

- **Total Builds**: All build attempts
- **Failed Builds**: Builds that failed
- **Success Rate**: Percentage of successful builds
- **Last Build Time**: Duration of most recent build
- **Average Build Time**: Mean build duration
- **Last Build Status**: Success or failure

**Benefits:**
- Monitor build health
- Track compilation time trends
- Identify build issues early
- Optimize build processes

## Using the Analytics Dashboard

### Initial Setup

1. **Launch the GUI**
   ```bash
   python gui_director.py
   ```

2. **Connect to Unreal Engine**
   - Go to the "🎮 Unreal MCP" tab
   - Click "🔗 Connect"
   - Ensure UE is running with Python Editor Script Plugin enabled

3. **Navigate to Analytics**
   - Click the "📊 Analytics" tab
   - View current metrics (loaded from disk if available)

### Collecting Data from Unreal Engine

#### Manual Collection

1. Navigate to "📊 Status" tab
2. Click "📥 Collect UE Data" button
3. Wait for data collection to complete
4. View updated metrics in Analytics tab

#### Automatic Collection

- Data is automatically collected when connecting to UE
- Connection metrics update in real-time
- Analytics persist to disk automatically

### Refreshing Data

- Click "🔄 Refresh Data" in Analytics tab to reload from disk
- Updates all metric cards with latest data
- Recalculates health score

### Exporting Analytics

1. Click "📥 Export" in Analytics tab
2. Choose save location
3. Data exports as JSON file with timestamp
4. Use exported data for:
   - External analysis
   - Reporting
   - Historical tracking
   - Team sharing

## Data Storage

### Location

Analytics data is stored in:
```
./analytics_data/analytics.json
```

### Format

JSON format with complete metrics:
```json
{
  "asset_counts": { ... },
  "blueprint_stats": { ... },
  "loc_stats": { ... },
  "placeholder_content": { ... },
  "connection_metrics": { ... },
  "build_metrics": { ... },
  "pie_sessions": [ ... ]
}
```

### Persistence

- Data automatically saves after updates
- Persists between application restarts
- Historical data maintained (last 100 entries)

## Troubleshooting

### No Data Appearing

**Symptoms:** All metrics show 0 or "N/A"

**Solutions:**
1. Ensure you're connected to Unreal Engine
2. Click "Collect UE Data" button
3. Check UE connection in MCP tab
4. Verify Python Editor Script Plugin is enabled in UE

### Data Collection Fails

**Symptoms:** Error message when collecting data

**Solutions:**
1. Check UE is running and not busy
2. Verify MCP connection is stable
3. Check UE logs for Python errors
4. Try reconnecting to UE
5. Restart both GUI and UE if needed

### Incorrect Health Score

**Symptoms:** Health score doesn't match expectations

**Understanding:**
- Health score is calculated automatically
- Based on multiple weighted factors
- May need multiple data points for accuracy
- Factors: placeholders (-30), builds (-25), connections (-20), FPS (-25)

**Improvement Tips:**
- Reduce placeholder content
- Improve build success rate
- Stabilize connections
- Optimize PIE performance

### Missing PIE Data

**Symptoms:** PIE metrics show "N/A"

**Solutions:**
1. PIE sessions must be recorded manually (future: automatic)
2. Add PIE sessions programmatically:
   ```python
   from project_analytics import PIESession
   analytics.add_pie_session(PIESession(
       session_id="test_1",
       avg_fps=60.0,
       avg_memory_mb=512.0,
       duration_seconds=300.0
   ))
   ```
3. Future updates will add automatic PIE monitoring

## Advanced Usage

### Programmatic Access

Access analytics in Python code:

```python
from project_analytics import ProjectAnalytics

# Initialize
analytics = ProjectAnalytics()

# Update metrics
analytics.update_asset_counts({'static_meshes': 100, 'blueprints': 50})
analytics.update_loc_stats(10000, 8000, 1500, 500)

# Get health score
score = analytics.calculate_health_score()

# Export data
analytics.export_to_json("my_analytics.json")
```

### Custom Health Metrics

Modify health score calculation in `project_analytics.py`:

```python
def calculate_health_score(self) -> float:
    score = 100.0
    
    # Add your custom penalties
    # Example: Penalize for low test coverage
    if self.test_coverage < 80:
        score -= 20
    
    return max(0, min(100, score))
```

### Integration with CI/CD

Export analytics in your build pipeline:

```bash
# Collect and export analytics
python -c "
from project_analytics import ProjectAnalytics
analytics = ProjectAnalytics()
analytics.export_to_json('build_analytics.json')
"

# Use in reporting or fail builds based on health score
```

## Best Practices

1. **Regular Data Collection**
   - Collect UE data daily or after major changes
   - Track trends over time
   - Establish baseline metrics

2. **Monitor Health Score**
   - Aim for 80+ health score
   - Address issues when score drops below 60
   - Track score trends, not just absolute values

3. **Reduce Placeholders**
   - Replace temporary content before milestones
   - Name placeholders consistently for detection
   - Track placeholder reduction over sprints

4. **Optimize Builds**
   - Monitor build time trends
   - Investigate sudden build time increases
   - Maintain >90% build success rate

5. **Track PIE Performance**
   - Record PIE sessions regularly
   - Compare performance after changes
   - Maintain 60+ FPS target

6. **Export Regularly**
   - Export analytics weekly for reporting
   - Share with team for visibility
   - Archive for historical analysis

## Future Enhancements

Planned features:

- [ ] Live charts and graphs
- [ ] Automatic PIE session capture
- [ ] Asset usage analytics
- [ ] Memory profiling integration
- [ ] Alert system for critical thresholds
- [ ] Custom metric definitions
- [ ] Team collaboration features
- [ ] Historical trend visualization
- [ ] Automated reporting

## Support

For issues or questions:

1. Check this guide first
2. Review troubleshooting section
3. Check GitHub issues
4. Create new issue with:
   - Description of problem
   - Steps to reproduce
   - Analytics export (if applicable)
   - Error messages or logs

## Summary

The Analytics Dashboard provides crucial insights into your UE project's health and progress. Use it to:

- Monitor project quality
- Track development progress  
- Identify issues early
- Optimize workflows
- Share metrics with team

Keep your health score high and your development smooth! 🚀
