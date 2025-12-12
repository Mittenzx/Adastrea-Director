#!/usr/bin/env python3
"""
Unreal Engine Content Generation Utilities

This module provides utilities for procedural content generation in Unreal Engine
using the Python API. These utilities can be used with any UE version (4.27+, 5.x).

Features:
- Procedural asset creation
- Material instance generation
- Blueprint creation from templates
- Level layout automation
- Batch asset processing

Usage:
    # Import in UE Python environment
    from ue_content_generation import (
        ProceduralEnvironmentGenerator,
        MaterialSystemAutomation,
        BlueprintTemplateSystem
    )
    
    # Generate content
    env_gen = ProceduralEnvironmentGenerator()
    env_gen.create_actor_grid(unreal.StaticMeshActor, 10, 10, 200.0)

Note: This module must be run inside Unreal Engine's Python environment.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('UEContentGeneration')

# Check if we're running inside Unreal Engine
try:
    import unreal
    UNREAL_AVAILABLE = True
    logger.info("Unreal Python API available")
except ImportError:
    UNREAL_AVAILABLE = False
    logger.warning("Unreal Python API not available - stub mode")
    
    # Create stub for development/testing
    class unreal:
        """Stub for development outside Unreal Engine."""
        pass


@dataclass
class ActorSpawnConfig:
    """Configuration for spawning actors."""
    actor_class: Any
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    actor_name: Optional[str] = None
    tags: List[str] = None


class ProceduralEnvironmentGenerator:
    """
    Generate procedural environments with assets.
    
    This class provides utilities for creating procedural layouts,
    environments, and level content using Python scripting.
    """
    
    def __init__(self):
        """Initialize the environment generator."""
        if not UNREAL_AVAILABLE:
            raise RuntimeError("Unreal Python API not available")
        
        self.editor_level_lib = unreal.EditorLevelLibrary
        self.editor_actor_subsystem = unreal.get_editor_subsystem(
            unreal.EditorActorSubsystem
        )
        logger.info("Procedural Environment Generator initialized")
    
    def create_actor_grid(
        self,
        actor_class: Any,
        rows: int,
        cols: int,
        spacing: float,
        center: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    ) -> List[Any]:
        """
        Create a grid of actors in the level.
        
        Args:
            actor_class: Class of actor to spawn (e.g., unreal.StaticMeshActor)
            rows: Number of rows in grid
            cols: Number of columns in grid
            spacing: Distance between actors
            center: Center point of the grid
            
        Returns:
            List of spawned actor references
            
        Example:
            gen = ProceduralEnvironmentGenerator()
            actors = gen.create_actor_grid(
                unreal.StaticMeshActor,
                rows=10,
                cols=10,
                spacing=200.0
            )
        """
        actors = []
        
        # Calculate grid offset to center it
        offset_x = -(rows - 1) * spacing / 2.0
        offset_y = -(cols - 1) * spacing / 2.0
        
        with unreal.ScopedEditorTransaction("Create Actor Grid"):
            for row in range(rows):
                for col in range(cols):
                    location = unreal.Vector(
                        center[0] + offset_x + (row * spacing),
                        center[1] + offset_y + (col * spacing),
                        center[2]
                    )
                    
                    try:
                        actor = self.editor_level_lib.spawn_actor_from_class(
                            actor_class,
                            location
                        )
                        
                        if actor:
                            # Set actor label
                            actor.set_actor_label(f"GridActor_{row}_{col}")
                            actors.append(actor)
                    except Exception as e:
                        logger.error(f"Failed to spawn actor at ({row}, {col}): {e}")
        
        logger.info(f"Created grid with {len(actors)} actors")
        return actors
    
    def create_circular_layout(
        self,
        actor_class: Any,
        count: int,
        radius: float,
        center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        face_center: bool = True
    ) -> List[Any]:
        """
        Create a circular layout of actors.
        
        Args:
            actor_class: Class of actor to spawn
            count: Number of actors in circle
            radius: Radius of the circle
            center: Center point of the circle
            face_center: If True, actors face toward center
            
        Returns:
            List of spawned actor references
            
        Example:
            gen = ProceduralEnvironmentGenerator()
            actors = gen.create_circular_layout(
                unreal.PointLight,
                count=8,
                radius=500.0
            )
        """
        import math
        actors = []
        
        angle_step = 360.0 / count
        
        with unreal.ScopedEditorTransaction("Create Circular Layout"):
            for i in range(count):
                angle = math.radians(angle_step * i)
                
                # Calculate position
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                location = unreal.Vector(x, y, center[2])
                
                # Calculate rotation to face center
                if face_center:
                    rotation = unreal.Rotator(
                        0.0,
                        math.degrees(angle) + 180.0,
                        0.0
                    )
                else:
                    rotation = unreal.Rotator(0.0, 0.0, 0.0)
                
                try:
                    actor = self.editor_level_lib.spawn_actor_from_class(
                        actor_class,
                        location,
                        rotation
                    )
                    
                    if actor:
                        actor.set_actor_label(f"CircleActor_{i}")
                        actors.append(actor)
                except Exception as e:
                    logger.error(f"Failed to spawn actor {i}: {e}")
        
        logger.info(f"Created circular layout with {len(actors)} actors")
        return actors
    
    def generate_random_scatter(
        self,
        actor_class: Any,
        count: int,
        bounds: Tuple[float, float, float, float],
        height_range: Tuple[float, float] = (0.0, 0.0),
        random_rotation: bool = True,
        random_scale: Tuple[float, float] = (1.0, 1.0)
    ) -> List[Any]:
        """
        Scatter actors randomly within bounds.
        
        Args:
            actor_class: Class of actor to spawn
            count: Number of actors to scatter
            bounds: (min_x, min_y, max_x, max_y) boundaries
            height_range: (min_z, max_z) height range
            random_rotation: Randomize Z rotation if True
            random_scale: (min_scale, max_scale) for random scaling
            
        Returns:
            List of spawned actor references
            
        Example:
            gen = ProceduralEnvironmentGenerator()
            # Scatter 50 trees in a 1000x1000 area
            trees = gen.generate_random_scatter(
                unreal.StaticMeshActor,
                count=50,
                bounds=(-500, -500, 500, 500),
                random_scale=(0.8, 1.2)
            )
        """
        import random
        actors = []
        
        min_x, min_y, max_x, max_y = bounds
        min_z, max_z = height_range
        min_scale, max_scale = random_scale
        
        with unreal.ScopedEditorTransaction("Random Scatter"):
            for i in range(count):
                # Random position
                x = random.uniform(min_x, max_x)
                y = random.uniform(min_y, max_y)
                z = random.uniform(min_z, max_z)
                location = unreal.Vector(x, y, z)
                
                # Random rotation
                if random_rotation:
                    yaw = random.uniform(0.0, 360.0)
                    rotation = unreal.Rotator(0.0, yaw, 0.0)
                else:
                    rotation = unreal.Rotator(0.0, 0.0, 0.0)
                
                try:
                    actor = self.editor_level_lib.spawn_actor_from_class(
                        actor_class,
                        location,
                        rotation
                    )
                    
                    if actor:
                        # Random scale
                        if min_scale != max_scale:
                            scale = random.uniform(min_scale, max_scale)
                            actor.set_actor_scale3d(
                                unreal.Vector(scale, scale, scale)
                            )
                        
                        actor.set_actor_label(f"ScatterActor_{i}")
                        actors.append(actor)
                except Exception as e:
                    logger.error(f"Failed to spawn actor {i}: {e}")
        
        logger.info(f"Scattered {len(actors)} actors")
        return actors


class MaterialSystemAutomation:
    """
    Automate material instance creation and configuration.
    
    This class provides utilities for batch creating and configuring
    material instances, useful for creating material libraries and variants.
    """
    
    def __init__(self):
        """Initialize the material system automation."""
        if not UNREAL_AVAILABLE:
            raise RuntimeError("Unreal Python API not available")
        
        self.asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        self.material_editing_lib = unreal.MaterialEditingLibrary
        logger.info("Material System Automation initialized")
    
    def create_material_instance(
        self,
        parent_material_path: str,
        instance_name: str,
        destination_path: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """
        Create a material instance from a parent material.
        
        Args:
            parent_material_path: Path to parent material
            instance_name: Name for new material instance
            destination_path: Where to save the instance
            parameters: Dict of parameter names and values to set
            
        Returns:
            Created material instance or None if failed
            
        Example:
            mat_auto = MaterialSystemAutomation()
            instance = mat_auto.create_material_instance(
                '/Game/Materials/M_Master',
                'MI_Red',
                '/Game/Materials/Instances',
                parameters={'BaseColor': (1.0, 0.0, 0.0), 'Metallic': 0.5}
            )
        """
        try:
            # Load parent material
            parent_material = unreal.load_asset(parent_material_path)
            if not parent_material:
                logger.error(f"Parent material not found: {parent_material_path}")
                return None
            
            # Create factory
            factory = unreal.MaterialInstanceConstantFactoryNew()
            factory.initial_parent = parent_material
            
            # Create asset
            with unreal.ScopedEditorTransaction("Create Material Instance"):
                material_instance = self.asset_tools.create_asset(
                    asset_name=instance_name,
                    package_path=destination_path,
                    asset_class=unreal.MaterialInstanceConstant,
                    factory=factory
                )
                
                if not material_instance:
                    logger.error("Failed to create material instance")
                    return None
                
                # Set parameters if provided
                if parameters:
                    for param_name, param_value in parameters.items():
                        self._set_material_parameter(
                            material_instance,
                            param_name,
                            param_value
                        )
                
                # Save the asset
                unreal.EditorAssetLibrary.save_loaded_asset(material_instance)
                
            logger.info(f"Created material instance: {instance_name}")
            return material_instance
            
        except Exception as e:
            logger.error(f"Failed to create material instance: {e}")
            return None
    
    def _set_material_parameter(
        self,
        material_instance: Any,
        param_name: str,
        param_value: Any
    ):
        """Set a material instance parameter based on value type."""
        try:
            if isinstance(param_value, (int, float)):
                # Scalar parameter
                self.material_editing_lib.set_material_instance_scalar_parameter_value(
                    material_instance, param_name, float(param_value)
                )
            elif isinstance(param_value, (tuple, list)) and len(param_value) in [3, 4]:
                # Vector parameter
                if len(param_value) == 3:
                    color = unreal.LinearColor(
                        param_value[0], param_value[1], param_value[2], 1.0
                    )
                else:
                    color = unreal.LinearColor(*param_value)
                
                self.material_editing_lib.set_material_instance_vector_parameter_value(
                    material_instance, param_name, color
                )
            elif isinstance(param_value, str):
                # Texture parameter
                texture = unreal.load_asset(param_value)
                if texture:
                    self.material_editing_lib.set_material_instance_texture_parameter_value(
                        material_instance, param_name, texture
                    )
            else:
                logger.warning(f"Unsupported parameter type for {param_name}")
        except Exception as e:
            logger.error(f"Failed to set parameter {param_name}: {e}")
    
    def create_material_library(
        self,
        parent_material_path: str,
        destination_path: str,
        variants: Dict[str, Dict[str, Any]]
    ) -> List[Any]:
        """
        Create a library of material instances.
        
        Args:
            parent_material_path: Path to parent material
            destination_path: Where to save instances
            variants: Dict mapping instance names to their parameters
            
        Returns:
            List of created material instances
            
        Example:
            mat_auto = MaterialSystemAutomation()
            variants = {
                'MI_Red': {'BaseColor': (1, 0, 0), 'Metallic': 0.5},
                'MI_Blue': {'BaseColor': (0, 0, 1), 'Metallic': 0.3},
                'MI_Green': {'BaseColor': (0, 1, 0), 'Metallic': 0.7}
            }
            materials = mat_auto.create_material_library(
                '/Game/Materials/M_Master',
                '/Game/Materials/ColorLibrary',
                variants
            )
        """
        instances = []
        
        for instance_name, parameters in variants.items():
            instance = self.create_material_instance(
                parent_material_path,
                instance_name,
                destination_path,
                parameters
            )
            if instance:
                instances.append(instance)
        
        logger.info(f"Created material library with {len(instances)} instances")
        return instances


class BlueprintTemplateSystem:
    """
    Create and configure Blueprints from templates.
    
    This class provides utilities for creating Blueprint assets
    programmatically, useful for generating Blueprint variants.
    """
    
    def __init__(self):
        """Initialize the Blueprint template system."""
        if not UNREAL_AVAILABLE:
            raise RuntimeError("Unreal Python API not available")
        
        self.asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        logger.info("Blueprint Template System initialized")
    
    def create_blueprint_from_class(
        self,
        parent_class: Any,
        blueprint_name: str,
        destination_path: str
    ) -> Optional[Any]:
        """
        Create a new Blueprint from a parent class.
        
        Args:
            parent_class: Parent class for the Blueprint
            blueprint_name: Name for the new Blueprint
            destination_path: Where to save the Blueprint
            
        Returns:
            Created Blueprint or None if failed
            
        Example:
            bp_system = BlueprintTemplateSystem()
            blueprint = bp_system.create_blueprint_from_class(
                unreal.Actor,
                'BP_CustomActor',
                '/Game/Blueprints'
            )
        """
        try:
            factory = unreal.BlueprintFactory()
            factory.set_editor_property('parent_class', parent_class)
            
            with unreal.ScopedEditorTransaction("Create Blueprint"):
                blueprint = self.asset_tools.create_asset(
                    asset_name=blueprint_name,
                    package_path=destination_path,
                    asset_class=unreal.Blueprint,
                    factory=factory
                )
                
                if blueprint:
                    unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
                    logger.info(f"Created Blueprint: {blueprint_name}")
                    return blueprint
                else:
                    logger.error("Failed to create Blueprint")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to create Blueprint: {e}")
            return None


# Utility functions

def batch_spawn_actors(
    actor_configs: List[ActorSpawnConfig]
) -> List[Any]:
    """
    Spawn multiple actors from configuration list.
    
    Args:
        actor_configs: List of ActorSpawnConfig objects
        
    Returns:
        List of spawned actors
        
    Example:
        configs = [
            ActorSpawnConfig(
                unreal.StaticMeshActor,
                location=(0, 0, 0),
                actor_name="Actor1"
            ),
            ActorSpawnConfig(
                unreal.PointLight,
                location=(0, 0, 200),
                actor_name="Light1"
            )
        ]
        actors = batch_spawn_actors(configs)
    """
    if not UNREAL_AVAILABLE:
        raise RuntimeError("Unreal Python API not available")
    
    editor_level_lib = unreal.EditorLevelLibrary
    actors = []
    
    with unreal.ScopedEditorTransaction("Batch Spawn Actors"):
        for config in actor_configs:
            try:
                location = unreal.Vector(*config.location)
                rotation = unreal.Rotator(*config.rotation)
                
                actor = editor_level_lib.spawn_actor_from_class(
                    config.actor_class,
                    location,
                    rotation
                )
                
                if actor:
                    if config.scale != (1.0, 1.0, 1.0):
                        actor.set_actor_scale3d(unreal.Vector(*config.scale))
                    
                    if config.actor_name:
                        actor.set_actor_label(config.actor_name)
                    
                    if config.tags:
                        for tag in config.tags:
                            actor.tags.append(unreal.Name(tag))
                    
                    actors.append(actor)
            except Exception as e:
                logger.error(f"Failed to spawn actor: {e}")
    
    logger.info(f"Batch spawned {len(actors)} actors")
    return actors


# Example usage (when run in UE)
if __name__ == "__main__":
    if UNREAL_AVAILABLE:
        print("=" * 60)
        print("UE Content Generation Utilities - Demo")
        print("=" * 60)
        
        # Example: Create a grid of actors
        print("\n1. Creating actor grid...")
        try:
            env_gen = ProceduralEnvironmentGenerator()
            actors = env_gen.create_actor_grid(
                unreal.StaticMeshActor,
                rows=5,
                cols=5,
                spacing=200.0
            )
            print(f"   Created {len(actors)} actors in grid")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\nDemo complete. Check Unreal Editor for results.")
    else:
        print("This script must be run inside Unreal Engine's Python environment")
