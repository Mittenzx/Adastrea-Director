#!/usr/bin/env python3
"""
Unreal Engine Comprehensive Information Collector

This script collects extensive information about a game project from inside
the Unreal Engine editor. It provides agents with detailed context about:
- Project configuration and metadata
- Assets (counts, types, sizes, locations)
- Actors and level content
- Blueprints (complexity, structure, dependencies)
- Materials and textures
- Performance metrics
- Editor settings and plugins
- Build configuration
- Source code structure

USAGE:
    This script must be run from within Unreal Engine's Python environment.
    
    In UE Editor:
    1. Enable Python Editor Script Plugin
    2. Window > Developer Tools > Python Console
    3. Run: execfile("Plugins/AdastreaDirector/Python/ue_info_collector.py")
    
    Or programmatically:
    import ue_info_collector
    info = ue_info_collector.collect_all_info()
    ue_info_collector.print_report(info)
    ue_info_collector.save_to_json(info, "ue_project_info.json")
"""

import sys
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

# Check if running in Unreal Engine
try:
    import unreal
    UNREAL_AVAILABLE = True
except ImportError:
    UNREAL_AVAILABLE = False
    print("WARNING: Not running inside Unreal Engine. Some features will be unavailable.")
    

class UEInfoCollector:
    """Collects comprehensive information about the UE project."""
    
    def __init__(self):
        """Initialize the collector."""
        if not UNREAL_AVAILABLE:
            print("⚠ WARNING: Unreal Python API not available")
            print("This script must be run inside Unreal Engine's Python environment")
            self.available = False
            return
        
        self.available = True
        self._init_subsystems()
    
    def _init_subsystems(self):
        """Initialize UE subsystems."""
        try:
            self.asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
            self.editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
            self.editor_asset_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
            self.unreal_editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
            self.level_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
            print("✓ UE subsystems initialized")
        except Exception as e:
            print(f"✗ Failed to initialize subsystems: {e}")
            self.available = False
    
    # ============================================================================
    # Project Information
    # ============================================================================
    
    def collect_project_info(self) -> Dict[str, Any]:
        """Collect basic project information."""
        if not self.available:
            return {"error": "UE not available"}
        
        info = {
            "collection_time": datetime.now().isoformat(),
            "engine_version": {},
            "project": {},
            "paths": {}
        }
        
        try:
            # Engine version
            info["engine_version"] = {
                "major": unreal.SystemLibrary.get_engine_version(),
                "full": str(unreal.SystemLibrary.get_engine_version())
            }
            
            # Project directory
            project_dir = unreal.SystemLibrary.get_project_directory()
            info["paths"]["project_directory"] = project_dir
            info["paths"]["project_content_directory"] = unreal.SystemLibrary.get_project_content_directory()
            info["paths"]["project_saved_directory"] = unreal.SystemLibrary.get_project_saved_directory()
            
            # Current level
            world = self.unreal_editor_subsystem.get_editor_world()
            if world:
                info["project"]["current_level"] = world.get_name()
                info["project"]["current_level_path"] = world.get_path_name()
            
            # Project name (extract from path)
            info["project"]["name"] = os.path.basename(project_dir.rstrip('/\\'))
            
            print("✓ Collected project info")
            
        except Exception as e:
            print(f"✗ Error collecting project info: {e}")
            info["error"] = str(e)
        
        return info
    
    # ============================================================================
    # Asset Information
    # ============================================================================
    
    def collect_asset_info(self) -> Dict[str, Any]:
        """Collect comprehensive asset information."""
        if not self.available:
            return {"error": "UE not available"}
        
        info = {
            "total_assets": 0,
            "by_type": {},
            "by_path": {},
            "largest_assets": [],
            "recently_modified": [],
            "naming_conventions": {}
        }
        
        try:
            # Get all assets
            all_assets = self.asset_registry.get_all_assets()
            info["total_assets"] = len(all_assets)
            
            asset_details = []
            type_counts = defaultdict(int)
            path_counts = defaultdict(int)
            
            for asset_data in all_assets:
                asset_class = str(asset_data.asset_class_path.asset_name)
                asset_path = str(asset_data.package_name)
                asset_name = str(asset_data.asset_name)
                
                # Count by type
                type_counts[asset_class] += 1
                
                # Count by top-level path
                path_parts = asset_path.split('/')
                if len(path_parts) > 1:
                    top_path = f"/{path_parts[1]}" if path_parts[1] else "/Game"
                    path_counts[top_path] += 1
                
                # Collect asset details
                asset_details.append({
                    "name": asset_name,
                    "class": asset_class,
                    "path": asset_path
                })
            
            # Sort and store by type
            info["by_type"] = dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True))
            info["by_path"] = dict(sorted(path_counts.items(), key=lambda x: x[1], reverse=True))
            
            # Analyze naming conventions
            info["naming_conventions"] = self._analyze_naming_conventions(asset_details)
            
            print(f"✓ Collected info on {info['total_assets']} assets")
            
        except Exception as e:
            print(f"✗ Error collecting asset info: {e}")
            info["error"] = str(e)
        
        return info
    
    def _analyze_naming_conventions(self, assets: List[Dict]) -> Dict[str, Any]:
        """Analyze asset naming conventions."""
        conventions = {
            "prefixes": defaultdict(int),
            "suffixes": defaultdict(int),
            "has_prefix": 0,
            "has_suffix": 0
        }
        
        common_prefixes = ['BP_', 'M_', 'MI_', 'T_', 'SM_', 'SK_', 'A_', 'S_', 'P_', 'E_', 'W_']
        common_suffixes = ['_C', '_Inst', '_Mat', '_Tex']
        
        for asset in assets:
            name = asset["name"]
            
            # Check prefixes
            for prefix in common_prefixes:
                if name.startswith(prefix):
                    conventions["prefixes"][prefix] += 1
                    conventions["has_prefix"] += 1
                    break
            
            # Check suffixes
            for suffix in common_suffixes:
                if name.endswith(suffix):
                    conventions["suffixes"][suffix] += 1
                    conventions["has_suffix"] += 1
                    break
        
        # Convert defaultdict to regular dict for JSON serialization
        conventions["prefixes"] = dict(conventions["prefixes"])
        conventions["suffixes"] = dict(conventions["suffixes"])
        
        return conventions
    
    # ============================================================================
    # Blueprint Information
    # ============================================================================
    
    def collect_blueprint_info(self) -> Dict[str, Any]:
        """Collect detailed blueprint information."""
        if not self.available:
            return {"error": "UE not available"}
        
        info = {
            "total_blueprints": 0,
            "by_parent_class": {},
            "actor_blueprints": 0,
            "component_blueprints": 0,
            "interface_blueprints": 0,
            "function_libraries": 0,
            "widget_blueprints": 0,
            "animation_blueprints": 0,
            "largest_blueprints": []
        }
        
        try:
            # Get all blueprint assets
            bp_filter = unreal.ARFilter(
                class_names=["Blueprint"],
                recursive_paths=True
            )
            blueprints = self.asset_registry.get_assets(bp_filter)
            info["total_blueprints"] = len(blueprints)
            
            parent_class_counts = defaultdict(int)
            
            for bp_data in blueprints:
                bp_path = str(bp_data.package_name)
                
                try:
                    # Try to load and analyze blueprint
                    bp = unreal.load_asset(bp_path)
                    if bp:
                        # Get parent class
                        bp_class = bp.get_class()
                        if bp_class:
                            parent = bp_class.get_super_class()
                            if parent:
                                parent_name = parent.get_name()
                                parent_class_counts[parent_name] += 1
                                
                                # Categorize by type
                                if 'Actor' in parent_name:
                                    info["actor_blueprints"] += 1
                                elif 'Component' in parent_name:
                                    info["component_blueprints"] += 1
                                elif 'Interface' in parent_name:
                                    info["interface_blueprints"] += 1
                                elif 'FunctionLibrary' in parent_name or 'Library' in parent_name:
                                    info["function_libraries"] += 1
                                elif 'Widget' in parent_name or 'UserWidget' in parent_name:
                                    info["widget_blueprints"] += 1
                                elif 'Anim' in parent_name:
                                    info["animation_blueprints"] += 1
                
                except (RuntimeError, AttributeError) as e:
                    # Skip blueprints that fail to load or have missing attributes
                    # This is expected for some blueprint types
                    pass
            
            info["by_parent_class"] = dict(sorted(parent_class_counts.items(), key=lambda x: x[1], reverse=True))
            
            print(f"✓ Collected info on {info['total_blueprints']} blueprints")
            
        except Exception as e:
            print(f"✗ Error collecting blueprint info: {e}")
            info["error"] = str(e)
        
        return info
    
    # ============================================================================
    # Level and Actor Information
    # ============================================================================
    
    def collect_level_info(self) -> Dict[str, Any]:
        """Collect information about levels and actors."""
        if not self.available:
            return {"error": "UE not available"}
        
        info = {
            "current_level": {},
            "all_levels": [],
            "actors": {},
            "lighting": {},
            "volumes": {}
        }
        
        try:
            # Get current world
            world = self.unreal_editor_subsystem.get_editor_world()
            if not world:
                info["error"] = "No world loaded"
                return info
            
            info["current_level"]["name"] = world.get_name()
            info["current_level"]["path"] = world.get_path_name()
            
            # Get all actors in current level
            all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
            info["actors"]["total"] = len(all_actors)
            
            # Categorize actors
            actor_types = defaultdict(int)
            light_actors = []
            volume_actors = []
            
            for actor in all_actors:
                actor_class = actor.get_class().get_name()
                actor_types[actor_class] += 1
                
                # Collect lighting info
                if 'Light' in actor_class:
                    light_actors.append({
                        "name": actor.get_name(),
                        "class": actor_class,
                        "location": str(actor.get_actor_location())
                    })
                
                # Collect volume info
                if 'Volume' in actor_class:
                    volume_actors.append({
                        "name": actor.get_name(),
                        "class": actor_class
                    })
            
            info["actors"]["by_type"] = dict(sorted(actor_types.items(), key=lambda x: x[1], reverse=True))
            info["lighting"]["total_lights"] = len(light_actors)
            info["lighting"]["lights"] = light_actors[:20]  # Limit to first 20
            info["volumes"]["total_volumes"] = len(volume_actors)
            info["volumes"]["types"] = volume_actors[:20]  # Limit to first 20
            
            # Find all level assets
            level_filter = unreal.ARFilter(
                class_names=["World"],
                recursive_paths=True
            )
            levels = self.asset_registry.get_assets(level_filter)
            info["all_levels"] = [str(level.package_name) for level in levels]
            
            print(f"✓ Collected info on {info['actors']['total']} actors in current level")
            
        except Exception as e:
            print(f"✗ Error collecting level info: {e}")
            info["error"] = str(e)
        
        return info
    
    # ============================================================================
    # Material Information
    # ============================================================================
    
    def collect_material_info(self) -> Dict[str, Any]:
        """Collect information about materials and textures."""
        if not self.available:
            return {"error": "UE not available"}
        
        info = {
            "materials": {"total": 0, "instances": 0, "functions": 0},
            "textures": {"total": 0, "by_type": {}},
            "shader_complexity": {}
        }
        
        try:
            # Count materials
            material_filter = unreal.ARFilter(
                class_names=["Material"],
                recursive_paths=True
            )
            materials = self.asset_registry.get_assets(material_filter)
            info["materials"]["total"] = len(materials)
            
            # Count material instances
            mi_filter = unreal.ARFilter(
                class_names=["MaterialInstanceConstant"],
                recursive_paths=True
            )
            material_instances = self.asset_registry.get_assets(mi_filter)
            info["materials"]["instances"] = len(material_instances)
            
            # Count material functions
            mf_filter = unreal.ARFilter(
                class_names=["MaterialFunction"],
                recursive_paths=True
            )
            material_functions = self.asset_registry.get_assets(mf_filter)
            info["materials"]["functions"] = len(material_functions)
            
            # Count textures
            texture_filter = unreal.ARFilter(
                class_names=["Texture2D", "TextureCube", "TextureRenderTarget2D"],
                recursive_paths=True
            )
            textures = self.asset_registry.get_assets(texture_filter)
            info["textures"]["total"] = len(textures)
            
            # Categorize textures
            texture_types = defaultdict(int)
            for tex in textures:
                tex_class = str(tex.asset_class_path.asset_name)
                texture_types[tex_class] += 1
            
            info["textures"]["by_type"] = dict(texture_types)
            
            print(f"✓ Collected info on {info['materials']['total']} materials and {info['textures']['total']} textures")
            
        except Exception as e:
            print(f"✗ Error collecting material info: {e}")
            info["error"] = str(e)
        
        return info
    
    # ============================================================================
    # Plugin Information
    # ============================================================================
    
    def collect_plugin_info(self) -> Dict[str, Any]:
        """Collect information about installed plugins."""
        if not self.available:
            return {"error": "UE not available"}
        
        info = {
            "total_plugins": 0,
            "enabled_plugins": [],
            "disabled_plugins": [],
            "plugin_categories": {}
        }
        
        try:
            # Get plugin manager
            plugin_manager = unreal.PluginBlueprintLibrary
            
            # Get all plugins (this is a simplified version)
            # In a real implementation, you'd parse .uplugin files
            info["note"] = "Plugin enumeration requires file system access"
            
            # Try to get some plugin info from project directory
            project_dir = unreal.SystemLibrary.get_project_directory()
            plugins_dir = os.path.join(project_dir, "Plugins")
            
            if os.path.exists(plugins_dir):
                plugins = []
                for item in os.listdir(plugins_dir):
                    plugin_path = os.path.join(plugins_dir, item)
                    if os.path.isdir(plugin_path):
                        # Check for .uplugin file
                        uplugin_files = [f for f in os.listdir(plugin_path) if f.endswith('.uplugin')]
                        if uplugin_files:
                            plugins.append(item)
                
                info["project_plugins"] = plugins
                info["total_plugins"] = len(plugins)
            
            print(f"✓ Found {info['total_plugins']} project plugins")
            
        except Exception as e:
            print(f"✗ Error collecting plugin info: {e}")
            info["error"] = str(e)
        
        return info
    
    # ============================================================================
    # Performance Information
    # ============================================================================
    
    def collect_performance_info(self) -> Dict[str, Any]:
        """Collect performance-related information."""
        if not self.available:
            return {"error": "UE not available"}
        
        info = {
            "editor_stats": {},
            "rendering": {},
            "memory": {}
        }
        
        try:
            # Note: Actual performance metrics require PIE or game running
            # This collects configuration and available info
            
            info["note"] = "Detailed performance metrics available during PIE session"
            info["instructions"] = "Run 'stat fps', 'stat unit', 'stat memory' in console during PIE"
            
            # Get some basic info
            world = self.unreal_editor_subsystem.get_editor_world()
            if world:
                info["editor_stats"]["world_loaded"] = True
                info["editor_stats"]["world_name"] = world.get_name()
            
            print("✓ Collected performance info (limited in editor mode)")
            
        except Exception as e:
            print(f"✗ Error collecting performance info: {e}")
            info["error"] = str(e)
        
        return info
    
    # ============================================================================
    # Source Code Information
    # ============================================================================
    
    def collect_source_info(self) -> Dict[str, Any]:
        """Collect information about C++ source code."""
        if not self.available:
            return {"error": "UE not available"}
        
        info = {
            "has_source": False,
            "modules": [],
            "classes": 0
        }
        
        try:
            project_dir = unreal.SystemLibrary.get_project_directory()
            source_dir = os.path.join(project_dir, "Source")
            
            if os.path.exists(source_dir):
                info["has_source"] = True
                
                # Count modules
                modules = []
                for item in os.listdir(source_dir):
                    module_path = os.path.join(source_dir, item)
                    if os.path.isdir(module_path) and not item.startswith('.'):
                        modules.append(item)
                
                info["modules"] = modules
                
                # Count C++ files
                cpp_files = 0
                header_files = 0
                for root, dirs, files in os.walk(source_dir):
                    cpp_files += len([f for f in files if f.endswith('.cpp')])
                    header_files += len([f for f in files if f.endswith('.h')])
                
                info["cpp_files"] = cpp_files
                info["header_files"] = header_files
                info["total_source_files"] = cpp_files + header_files
            
            print(f"✓ Collected source code info: {info['total_source_files'] if info['has_source'] else 0} files")
            
        except Exception as e:
            print(f"✗ Error collecting source info: {e}")
            info["error"] = str(e)
        
        return info
    
    # ============================================================================
    # Animation Information
    # ============================================================================
    
    def collect_animation_info(self) -> Dict[str, Any]:
        """Collect information about animations and skeletal assets."""
        if not self.available:
            return {"error": "UE not available"}
        
        info = {
            "skeletal_meshes": 0,
            "animations": 0,
            "animation_blueprints": 0,
            "skeletons": 0
        }
        
        try:
            # Skeletal meshes
            sk_filter = unreal.ARFilter(
                class_names=["SkeletalMesh"],
                recursive_paths=True
            )
            skeletal_meshes = self.asset_registry.get_assets(sk_filter)
            info["skeletal_meshes"] = len(skeletal_meshes)
            
            # Animation sequences
            anim_filter = unreal.ARFilter(
                class_names=["AnimSequence"],
                recursive_paths=True
            )
            animations = self.asset_registry.get_assets(anim_filter)
            info["animations"] = len(animations)
            
            # Animation blueprints
            anim_bp_filter = unreal.ARFilter(
                class_names=["AnimBlueprint"],
                recursive_paths=True
            )
            anim_bps = self.asset_registry.get_assets(anim_bp_filter)
            info["animation_blueprints"] = len(anim_bps)
            
            # Skeletons
            skel_filter = unreal.ARFilter(
                class_names=["Skeleton"],
                recursive_paths=True
            )
            skeletons = self.asset_registry.get_assets(skel_filter)
            info["skeletons"] = len(skeletons)
            
            print(f"✓ Collected animation info: {info['animations']} animations")
            
        except Exception as e:
            print(f"✗ Error collecting animation info: {e}")
            info["error"] = str(e)
        
        return info
    
    # ============================================================================
    # Audio Information
    # ============================================================================
    
    def collect_audio_info(self) -> Dict[str, Any]:
        """Collect information about audio assets."""
        if not self.available:
            return {"error": "UE not available"}
        
        info = {
            "sound_waves": 0,
            "sound_cues": 0,
            "sound_classes": 0
        }
        
        try:
            # Sound waves
            sw_filter = unreal.ARFilter(
                class_names=["SoundWave"],
                recursive_paths=True
            )
            sound_waves = self.asset_registry.get_assets(sw_filter)
            info["sound_waves"] = len(sound_waves)
            
            # Sound cues
            sc_filter = unreal.ARFilter(
                class_names=["SoundCue"],
                recursive_paths=True
            )
            sound_cues = self.asset_registry.get_assets(sc_filter)
            info["sound_cues"] = len(sound_cues)
            
            # Sound classes
            scl_filter = unreal.ARFilter(
                class_names=["SoundClass"],
                recursive_paths=True
            )
            sound_classes = self.asset_registry.get_assets(scl_filter)
            info["sound_classes"] = len(sound_classes)
            
            print(f"✓ Collected audio info: {info['sound_waves']} sound waves")
            
        except Exception as e:
            print(f"✗ Error collecting audio info: {e}")
            info["error"] = str(e)
        
        return info


# ============================================================================
# Main Collection Function
# ============================================================================

def collect_all_info() -> Dict[str, Any]:
    """
    Collect all available information about the UE project.
    
    Returns:
        Dictionary containing all collected information
    """
    print("\n" + "="*60)
    print("Unreal Engine Project Information Collector")
    print("="*60 + "\n")
    
    if not UNREAL_AVAILABLE:
        print("✗ ERROR: Not running inside Unreal Engine!")
        print("This script must be run from UE's Python environment.")
        return {"error": "Not running in Unreal Engine"}
    
    collector = UEInfoCollector()
    
    if not collector.available:
        return {"error": "Failed to initialize collector"}
    
    # Collect all information
    all_info = {}
    
    print("Collecting project information...")
    all_info["project_info"] = collector.collect_project_info()
    
    print("\nCollecting asset information...")
    all_info["assets"] = collector.collect_asset_info()
    
    print("\nCollecting blueprint information...")
    all_info["blueprints"] = collector.collect_blueprint_info()
    
    print("\nCollecting level information...")
    all_info["levels"] = collector.collect_level_info()
    
    print("\nCollecting material information...")
    all_info["materials"] = collector.collect_material_info()
    
    print("\nCollecting plugin information...")
    all_info["plugins"] = collector.collect_plugin_info()
    
    print("\nCollecting performance information...")
    all_info["performance"] = collector.collect_performance_info()
    
    print("\nCollecting source code information...")
    all_info["source"] = collector.collect_source_info()
    
    print("\nCollecting animation information...")
    all_info["animation"] = collector.collect_animation_info()
    
    print("\nCollecting audio information...")
    all_info["audio"] = collector.collect_audio_info()
    
    print("\n" + "="*60)
    print("Collection Complete!")
    print("="*60 + "\n")
    
    return all_info


# ============================================================================
# Output Functions
# ============================================================================

def print_report(info: Dict[str, Any], detailed: bool = False):
    """
    Print a human-readable report of the collected information.
    
    Args:
        info: Information dictionary from collect_all_info()
        detailed: Whether to print detailed information
    """
    print("\n" + "="*60)
    print("PROJECT INFORMATION REPORT")
    print("="*60 + "\n")
    
    # Project Info
    if "project_info" in info:
        proj = info["project_info"]
        print("PROJECT")
        print("-" * 60)
        if "project" in proj:
            print(f"  Name: {proj['project'].get('name', 'Unknown')}")
            print(f"  Current Level: {proj['project'].get('current_level', 'Unknown')}")
        if "engine_version" in proj:
            print(f"  Engine Version: {proj['engine_version'].get('full', 'Unknown')}")
        print()
    
    # Assets
    if "assets" in info:
        assets = info["assets"]
        print("ASSETS")
        print("-" * 60)
        print(f"  Total Assets: {assets.get('total_assets', 0)}")
        if "by_type" in assets and assets["by_type"]:
            print("  Top Asset Types:")
            for asset_type, count in list(assets["by_type"].items())[:10]:
                print(f"    - {asset_type}: {count}")
        print()
    
    # Blueprints
    if "blueprints" in info:
        bp = info["blueprints"]
        print("BLUEPRINTS")
        print("-" * 60)
        print(f"  Total Blueprints: {bp.get('total_blueprints', 0)}")
        print(f"  Actor Blueprints: {bp.get('actor_blueprints', 0)}")
        print(f"  Widget Blueprints: {bp.get('widget_blueprints', 0)}")
        print(f"  Animation Blueprints: {bp.get('animation_blueprints', 0)}")
        print()
    
    # Levels
    if "levels" in info:
        levels = info["levels"]
        if "actors" in levels:
            print("LEVEL ACTORS")
            print("-" * 60)
            print(f"  Total Actors: {levels['actors'].get('total', 0)}")
            if "by_type" in levels["actors"] and levels["actors"]["by_type"]:
                print("  Top Actor Types:")
                for actor_type, count in list(levels["actors"]["by_type"].items())[:10]:
                    print(f"    - {actor_type}: {count}")
        print()
    
    # Materials
    if "materials" in info:
        mats = info["materials"]
        print("MATERIALS & TEXTURES")
        print("-" * 60)
        if "materials" in mats:
            print(f"  Materials: {mats['materials'].get('total', 0)}")
            print(f"  Material Instances: {mats['materials'].get('instances', 0)}")
            print(f"  Material Functions: {mats['materials'].get('functions', 0)}")
        if "textures" in mats:
            print(f"  Textures: {mats['textures'].get('total', 0)}")
        print()
    
    # Animation
    if "animation" in info:
        anim = info["animation"]
        print("ANIMATION")
        print("-" * 60)
        print(f"  Skeletal Meshes: {anim.get('skeletal_meshes', 0)}")
        print(f"  Animations: {anim.get('animations', 0)}")
        print(f"  Animation Blueprints: {anim.get('animation_blueprints', 0)}")
        print()
    
    # Audio
    if "audio" in info:
        audio = info["audio"]
        print("AUDIO")
        print("-" * 60)
        print(f"  Sound Waves: {audio.get('sound_waves', 0)}")
        print(f"  Sound Cues: {audio.get('sound_cues', 0)}")
        print()
    
    # Source Code
    if "source" in info:
        source = info["source"]
        print("SOURCE CODE")
        print("-" * 60)
        print(f"  Has C++ Source: {source.get('has_source', False)}")
        if source.get('has_source'):
            print(f"  Modules: {', '.join(source.get('modules', []))}")
            print(f"  Total Source Files: {source.get('total_source_files', 0)}")
        print()
    
    # Plugins
    if "plugins" in info:
        plugins = info["plugins"]
        print("PLUGINS")
        print("-" * 60)
        print(f"  Project Plugins: {plugins.get('total_plugins', 0)}")
        if "project_plugins" in plugins:
            for plugin in plugins["project_plugins"]:
                print(f"    - {plugin}")
        print()
    
    print("="*60)


def save_to_json(info: Dict[str, Any], filename: str = "ue_project_info.json"):
    """
    Save collected information to a JSON file.
    
    Args:
        info: Information dictionary from collect_all_info()
        filename: Output filename
    """
    try:
        # Get project saved directory
        if UNREAL_AVAILABLE:
            saved_dir = unreal.SystemLibrary.get_project_saved_directory()
            filepath = os.path.join(saved_dir, filename)
        else:
            filepath = filename
        
        with open(filepath, 'w') as f:
            json.dump(info, f, indent=2)
        
        print(f"✓ Information saved to: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"✗ Error saving to JSON: {e}")
        return None


def save_to_markdown(info: Dict[str, Any], filename: str = "ue_project_info.md"):
    """
    Save collected information to a Markdown file.
    
    Args:
        info: Information dictionary from collect_all_info()
        filename: Output filename
    """
    try:
        # Get project saved directory
        if UNREAL_AVAILABLE:
            saved_dir = unreal.SystemLibrary.get_project_saved_directory()
            filepath = os.path.join(saved_dir, filename)
        else:
            filepath = filename
        
        with open(filepath, 'w') as f:
            f.write("# Unreal Engine Project Information\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Project Info
            if "project_info" in info:
                f.write("## Project\n\n")
                proj = info["project_info"]
                if "project" in proj:
                    f.write(f"- **Name:** {proj['project'].get('name', 'Unknown')}\n")
                    f.write(f"- **Current Level:** {proj['project'].get('current_level', 'Unknown')}\n")
                if "engine_version" in proj:
                    f.write(f"- **Engine Version:** {proj['engine_version'].get('full', 'Unknown')}\n")
                f.write("\n")
            
            # Assets
            if "assets" in info:
                f.write("## Assets\n\n")
                assets = info["assets"]
                f.write(f"- **Total Assets:** {assets.get('total_assets', 0)}\n\n")
                if "by_type" in assets and assets["by_type"]:
                    f.write("### By Type\n\n")
                    for asset_type, count in list(assets["by_type"].items())[:20]:
                        f.write(f"- {asset_type}: {count}\n")
                    f.write("\n")
            
            # Blueprints
            if "blueprints" in info:
                f.write("## Blueprints\n\n")
                bp = info["blueprints"]
                f.write(f"- **Total Blueprints:** {bp.get('total_blueprints', 0)}\n")
                f.write(f"- **Actor Blueprints:** {bp.get('actor_blueprints', 0)}\n")
                f.write(f"- **Widget Blueprints:** {bp.get('widget_blueprints', 0)}\n")
                f.write(f"- **Animation Blueprints:** {bp.get('animation_blueprints', 0)}\n")
                f.write("\n")
            
            # Levels
            if "levels" in info and "actors" in info["levels"]:
                f.write("## Level Content\n\n")
                actors = info["levels"]["actors"]
                f.write(f"- **Total Actors:** {actors.get('total', 0)}\n\n")
                if "by_type" in actors and actors["by_type"]:
                    f.write("### Actor Types\n\n")
                    for actor_type, count in list(actors["by_type"].items())[:10]:
                        f.write(f"- {actor_type}: {count}\n")
                    f.write("\n")
            
            # Materials
            if "materials" in info:
                f.write("## Materials & Textures\n\n")
                mats = info["materials"]
                if "materials" in mats:
                    f.write(f"- **Materials:** {mats['materials'].get('total', 0)}\n")
                    f.write(f"- **Material Instances:** {mats['materials'].get('instances', 0)}\n")
                if "textures" in mats:
                    f.write(f"- **Textures:** {mats['textures'].get('total', 0)}\n")
                f.write("\n")
            
            # Animation
            if "animation" in info:
                f.write("## Animation\n\n")
                anim = info["animation"]
                f.write(f"- **Skeletal Meshes:** {anim.get('skeletal_meshes', 0)}\n")
                f.write(f"- **Animations:** {anim.get('animations', 0)}\n")
                f.write(f"- **Animation Blueprints:** {anim.get('animation_blueprints', 0)}\n")
                f.write("\n")
            
            # Audio
            if "audio" in info:
                f.write("## Audio\n\n")
                audio = info["audio"]
                f.write(f"- **Sound Waves:** {audio.get('sound_waves', 0)}\n")
                f.write(f"- **Sound Cues:** {audio.get('sound_cues', 0)}\n")
                f.write("\n")
            
            # Source Code
            if "source" in info:
                f.write("## Source Code\n\n")
                source = info["source"]
                f.write(f"- **Has C++ Source:** {source.get('has_source', False)}\n")
                if source.get('has_source'):
                    f.write(f"- **Modules:** {', '.join(source.get('modules', []))}\n")
                    f.write(f"- **Total Source Files:** {source.get('total_source_files', 0)}\n")
                f.write("\n")
        
        print(f"✓ Information saved to: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"✗ Error saving to Markdown: {e}")
        return None


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    """Main execution when run directly."""
    
    # Collect all information
    info = collect_all_info()
    
    # Print report
    print_report(info)
    
    # Save to files
    json_file = save_to_json(info)
    md_file = save_to_markdown(info)
    
    print("\n" + "="*60)
    print("USAGE NOTES FOR AGENTS")
    print("="*60)
    print("\nThis information can help agents to:")
    print("  • Understand project structure and organization")
    print("  • Identify asset naming conventions")
    print("  • Analyze blueprint complexity and patterns")
    print("  • Detect potential performance issues")
    print("  • Find optimization opportunities")
    print("  • Understand the technology stack")
    print("  • Make informed decisions about code changes")
    print("\nFiles saved:")
    if json_file:
        print(f"  • JSON: {json_file}")
    if md_file:
        print(f"  • Markdown: {md_file}")
    print("\n" + "="*60)
