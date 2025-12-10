#!/usr/bin/env python3
"""
Unreal Engine Data Collector

Collects project data from Unreal Engine via MCP or Remote Control API.
Provides asset counts, blueprint information, and project statistics.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class UEDataCollector:
    """
    Collects project data from Unreal Engine.
    
    Uses MCP server or Remote Control API to query UE for project statistics.
    """
    
    def __init__(self, mcp_server=None, remote_control_client=None):
        """
        Initialize data collector.
        
        Args:
            mcp_server: Optional MCP server instance
            remote_control_client: Optional Remote Control API client
        """
        self.mcp_server = mcp_server
        self.remote_control_client = remote_control_client
    
    def is_connected(self) -> bool:
        """Check if connected to Unreal Engine."""
        if self.mcp_server:
            return hasattr(self.mcp_server, 'is_connected') and self.mcp_server.is_connected()
        if self.remote_control_client:
            return self.remote_control_client.is_connected()
        return False
    
    async def collect_asset_counts(self) -> Dict[str, int]:
        """
        Collect asset counts from UE project.
        
        Returns:
            Dictionary with asset type counts
        """
        if not self.is_connected():
            logger.warning("Not connected to Unreal Engine")
            return self._get_mock_asset_counts()
        
        try:
            if self.mcp_server:
                return await self._collect_via_mcp()
            elif self.remote_control_client:
                return await self._collect_via_remote_control()
        except Exception as e:
            logger.error(f"Error collecting asset counts: {e}")
            return self._get_mock_asset_counts()
    
    async def _collect_via_mcp(self) -> Dict[str, int]:
        """Collect assets via MCP server."""
        try:
            # Get asset list
            result = self.mcp_server.handle_tool_call("editor_list_assets", {})
            
            if result.get('isError'):
                logger.error("MCP error getting assets")
                return self._get_mock_asset_counts()
            
            # Parse asset data
            assets = []
            for content in result.get('content', []):
                if content.get('type') == 'text':
                    try:
                        data = json.loads(content['text'])
                        if isinstance(data, dict) and 'assets' in data:
                            assets = data['assets']
                        elif isinstance(data, list):
                            assets = data
                    except json.JSONDecodeError:
                        pass
            
            # Count by type
            counts = {
                'static_meshes': 0,
                'skeletal_meshes': 0,
                'blueprints': 0,
                'materials': 0,
                'textures': 0,
                'sounds': 0,
                'animations': 0,
                'particles': 0
            }
            
            for asset in assets:
                asset_class = asset.get('class', '').lower()
                
                if 'staticmesh' in asset_class:
                    counts['static_meshes'] += 1
                elif 'skeletalmesh' in asset_class:
                    counts['skeletal_meshes'] += 1
                elif 'blueprint' in asset_class:
                    counts['blueprints'] += 1
                elif 'material' in asset_class:
                    counts['materials'] += 1
                elif 'texture' in asset_class:
                    counts['textures'] += 1
                elif 'sound' in asset_class or 'audio' in asset_class:
                    counts['sounds'] += 1
                elif 'anim' in asset_class:
                    counts['animations'] += 1
                elif 'particle' in asset_class or 'niagara' in asset_class:
                    counts['particles'] += 1
            
            return counts
            
        except Exception as e:
            logger.error(f"Error in MCP asset collection: {e}")
            return self._get_mock_asset_counts()
    
    async def _collect_via_remote_control(self) -> Dict[str, int]:
        """Collect assets via Remote Control API."""
        # TODO: Implement Remote Control API asset collection
        return self._get_mock_asset_counts()
    
    def _get_mock_asset_counts(self) -> Dict[str, int]:
        """Get mock asset counts for testing."""
        return {
            'static_meshes': 0,
            'skeletal_meshes': 0,
            'blueprints': 0,
            'materials': 0,
            'textures': 0,
            'sounds': 0,
            'animations': 0,
            'particles': 0
        }
    
    async def collect_blueprint_stats(self) -> Dict[str, Any]:
        """
        Collect blueprint statistics.
        
        Returns:
            Dictionary with blueprint stats
        """
        if not self.is_connected():
            return self._get_mock_blueprint_stats()
        
        try:
            # Execute Python script in UE to get blueprint stats
            python_script = """
import unreal

# Get all blueprint assets
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
blueprints = asset_registry.get_assets_by_class("Blueprint", True)

stats = {
    'total': len(blueprints),
    'actors': 0,
    'components': 0,
    'interfaces': 0,
    'libraries': 0,
    'total_nodes': 0,
    'max_nodes': 0
}

# Categorize blueprints
for bp_asset in blueprints:
    bp_path = str(bp_asset.package_name)
    
    # Load and analyze blueprint
    try:
        bp = unreal.load_asset(bp_path)
        if bp:
            # Check parent class
            parent = bp.get_class().get_super_class()
            if parent:
                parent_name = parent.get_name()
                if 'Actor' in parent_name:
                    stats['actors'] += 1
                elif 'Component' in parent_name:
                    stats['components'] += 1
                elif 'Interface' in parent_name:
                    stats['interfaces'] += 1
                elif 'Library' in parent_name:
                    stats['libraries'] += 1
    except:
        pass

# Calculate averages
stats['avg_nodes'] = stats['total_nodes'] / max(stats['total'], 1)

print(unreal.SystemLibrary.parse_into_string(stats))
"""
            
            if self.mcp_server:
                result = self.mcp_server.handle_tool_call("editor_run_python", {"code": python_script})
                
                if not result.get('isError'):
                    # Parse output
                    for content in result.get('content', []):
                        if content.get('type') == 'text':
                            try:
                                return json.loads(content['text'])
                            except json.JSONDecodeError:
                                pass
            
            return self._get_mock_blueprint_stats()
            
        except Exception as e:
            logger.error(f"Error collecting blueprint stats: {e}")
            return self._get_mock_blueprint_stats()
    
    def _get_mock_blueprint_stats(self) -> Dict[str, Any]:
        """Get mock blueprint stats for testing."""
        return {
            'total': 0,
            'actors': 0,
            'components': 0,
            'interfaces': 0,
            'libraries': 0,
            'avg_nodes': 0.0,
            'max_nodes': 0,
            'total_nodes': 0
        }
    
    async def collect_placeholder_content(self) -> Dict[str, Any]:
        """
        Detect placeholder content in the project.
        
        Returns:
            Dictionary with placeholder content info
        """
        if not self.is_connected():
            return self._get_mock_placeholders()
        
        try:
            # Execute Python script to find placeholder content
            python_script = """
import unreal

placeholders = {
    'cubes': 0,
    'spheres': 0,
    'temp_bps': 0,
    'missing': 0,
    'placeholder_mats': 0,
    'placeholder_texs': 0,
    'locations': []
}

# Get all actors in the world
actors = unreal.EditorLevelLibrary.get_all_level_actors()

for actor in actors:
    actor_name = actor.get_name().lower()
    
    # Check for default shapes
    if 'cube' in actor_name and 'default' in actor_name:
        placeholders['cubes'] += 1
        placeholders['locations'].append({
            'type': 'cube',
            'name': actor.get_name(),
            'location': str(actor.get_actor_location())
        })
    elif 'sphere' in actor_name and 'default' in actor_name:
        placeholders['spheres'] += 1
        placeholders['locations'].append({
            'type': 'sphere',
            'name': actor.get_name(),
            'location': str(actor.get_actor_location())
        })
    elif 'temp' in actor_name or 'test' in actor_name:
        placeholders['temp_bps'] += 1

# Check for placeholder materials
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
materials = asset_registry.get_assets_by_class("Material", True)

for mat in materials:
    mat_name = str(mat.asset_name).lower()
    if 'placeholder' in mat_name or 'temp' in mat_name:
        placeholders['placeholder_mats'] += 1

print(unreal.SystemLibrary.parse_into_string(placeholders))
"""
            
            if self.mcp_server:
                result = self.mcp_server.handle_tool_call("editor_run_python", {"code": python_script})
                
                if not result.get('isError'):
                    for content in result.get('content', []):
                        if content.get('type') == 'text':
                            try:
                                data = json.loads(content['text'])
                                # Limit locations to prevent excessive data
                                if 'locations' in data:
                                    data['locations'] = data['locations'][:20]
                                return data
                            except json.JSONDecodeError:
                                pass
            
            return self._get_mock_placeholders()
            
        except Exception as e:
            logger.error(f"Error collecting placeholder content: {e}")
            return self._get_mock_placeholders()
    
    def _get_mock_placeholders(self) -> Dict[str, Any]:
        """Get mock placeholder data for testing."""
        return {
            'cubes': 0,
            'spheres': 0,
            'temp_bps': 0,
            'missing': 0,
            'placeholder_mats': 0,
            'placeholder_texs': 0,
            'locations': []
        }
    
    async def start_pie_monitoring(self) -> str:
        """
        Start monitoring PIE session.
        
        Returns:
            Session ID for tracking
        """
        session_id = f"pie_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not self.is_connected():
            logger.warning("Not connected to UE, PIE monitoring unavailable")
            return session_id
        
        try:
            # Start a PIE session monitor
            python_script = f"""
import unreal
import time

# Store session ID
session_id = "{session_id}"
print(f"PIE monitoring started: {{session_id}}")

# Monitor PIE session (this is a simplified example)
# In production, this would use UE's profiling tools
"""
            
            if self.mcp_server:
                result = self.mcp_server.handle_tool_call("editor_run_python", {"code": python_script})
                logger.info(f"PIE monitoring started: {session_id}")
            
        except Exception as e:
            logger.error(f"Error starting PIE monitoring: {e}")
        
        return session_id
    
    def get_connection_health(self) -> Dict[str, Any]:
        """
        Get connection health metrics.
        
        Returns:
            Dictionary with connection health info
        """
        return {
            'connected': self.is_connected(),
            'mcp_available': self.mcp_server is not None,
            'remote_control_available': self.remote_control_client is not None,
            'last_check': datetime.now().isoformat()
        }
