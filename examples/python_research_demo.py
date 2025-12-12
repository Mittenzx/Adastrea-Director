#!/usr/bin/env python3
"""
Content Generation and Validation Examples

This script demonstrates the new content generation and validation utilities
for Unreal Engine Python API.

These examples show practical use cases for:
- Procedural content generation
- Material library creation
- Asset validation workflows
- Batch processing operations

IMPORTANT: This script must be run from within Unreal Engine's Python environment.

Usage in Unreal Engine:
    1. Enable Python Editor Script Plugin
    2. Open Python Console (Window → Developer Tools → Python Console)
    3. Run: execfile("path/to/this/file.py")
    
Or copy specific examples and run them in the Python Console.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    import unreal
    from ue_content_generation import (
        ProceduralEnvironmentGenerator,
        MaterialSystemAutomation,
        batch_spawn_actors,
        ActorSpawnConfig
    )
    from ue_content_validation import (
        TextureValidator,
        MeshValidator,
        MaterialValidator,
        batch_validate_assets,
        validate_folder,
        generate_validation_report
    )
except ImportError as e:
    print(f"Error: Failed to import utilities: {e}")
    print("Make sure you're running this inside Unreal Engine")
    sys.exit(1)


def example_1_create_test_grid():
    """
    Example 1: Create a grid of test actors
    
    This demonstrates basic procedural level layout.
    """
    print("\n" + "=" * 60)
    print("Example 1: Create Test Grid")
    print("=" * 60)
    
    try:
        gen = ProceduralEnvironmentGenerator()
        
        # Create a 5x5 grid of static mesh actors
        actors = gen.create_actor_grid(
            actor_class=unreal.StaticMeshActor,
            rows=5,
            cols=5,
            spacing=200.0,
            center=(0.0, 0.0, 0.0)
        )
        
        print(f"✓ Created grid with {len(actors)} actors")
        print(f"  Grid size: 5x5")
        print(f"  Spacing: 200 units")
        print(f"  Check your level for the new actors!")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_2_create_circular_lights():
    """
    Example 2: Create circular arrangement of lights
    
    This demonstrates circular layout for environmental lighting.
    """
    print("\n" + "=" * 60)
    print("Example 2: Circular Light Arrangement")
    print("=" * 60)
    
    try:
        gen = ProceduralEnvironmentGenerator()
        
        # Create 8 point lights in a circle
        lights = gen.create_circular_layout(
            actor_class=unreal.PointLight,
            count=8,
            radius=500.0,
            center=(0.0, 0.0, 200.0),
            face_center=True
        )
        
        print(f"✓ Created {len(lights)} lights in circular pattern")
        print(f"  Radius: 500 units")
        print(f"  Height: 200 units")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_3_scatter_props():
    """
    Example 3: Randomly scatter props
    
    This demonstrates random scattering for environment population.
    """
    print("\n" + "=" * 60)
    print("Example 3: Random Prop Scattering")
    print("=" * 60)
    
    try:
        gen = ProceduralEnvironmentGenerator()
        
        # Scatter 20 actors randomly
        props = gen.generate_random_scatter(
            actor_class=unreal.StaticMeshActor,
            count=20,
            bounds=(-500, -500, 500, 500),
            height_range=(0, 0),
            random_rotation=True,
            random_scale=(0.8, 1.2)
        )
        
        print(f"✓ Scattered {len(props)} props")
        print(f"  Area: 1000x1000 units")
        print(f"  Scale variation: 0.8 - 1.2")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_4_create_material_library():
    """
    Example 4: Create material instance library
    
    This demonstrates automated material instance creation.
    
    NOTE: Update the parent_material_path to match your project!
    """
    print("\n" + "=" * 60)
    print("Example 4: Material Instance Library")
    print("=" * 60)
    
    try:
        mat_auto = MaterialSystemAutomation()
        
        # Define color variants
        variants = {
            'MI_Red': {
                'BaseColor': (1.0, 0.0, 0.0),
                'Metallic': 0.5,
                'Roughness': 0.3
            },
            'MI_Blue': {
                'BaseColor': (0.0, 0.0, 1.0),
                'Metallic': 0.3,
                'Roughness': 0.5
            },
            'MI_Green': {
                'BaseColor': (0.0, 1.0, 0.0),
                'Metallic': 0.7,
                'Roughness': 0.2
            },
            'MI_Yellow': {
                'BaseColor': (1.0, 1.0, 0.0),
                'Metallic': 0.4,
                'Roughness': 0.4
            }
        }
        
        # NOTE: Update this path to match your project!
        parent_material = '/Game/Materials/M_MasterMaterial'
        destination = '/Game/Materials/Generated'
        
        print(f"Parent material: {parent_material}")
        print(f"Destination: {destination}")
        print(f"Creating {len(variants)} material instances...")
        
        # Check if parent exists
        if not unreal.EditorAssetLibrary.does_asset_exist(parent_material):
            print(f"⚠ Parent material not found: {parent_material}")
            print("  Please update the path in the script to match your project")
            return
        
        # Create library
        materials = mat_auto.create_material_library(
            parent_material_path=parent_material,
            destination_path=destination,
            variants=variants
        )
        
        print(f"✓ Created {len(materials)} material instances")
        print(f"  Check {destination} in Content Browser")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_5_batch_spawn_custom():
    """
    Example 5: Batch spawn with custom configurations
    
    This demonstrates spawning multiple actors with different settings.
    """
    print("\n" + "=" * 60)
    print("Example 5: Batch Spawn Custom Actors")
    print("=" * 60)
    
    try:
        # Define actor configurations
        configs = [
            ActorSpawnConfig(
                actor_class=unreal.StaticMeshActor,
                location=(0.0, 0.0, 0.0),
                actor_name="MainProp",
                tags=["gameplay", "important"]
            ),
            ActorSpawnConfig(
                actor_class=unreal.PointLight,
                location=(0.0, 0.0, 200.0),
                actor_name="MainLight",
                tags=["lighting"]
            ),
            ActorSpawnConfig(
                actor_class=unreal.StaticMeshActor,
                location=(200.0, 0.0, 0.0),
                scale=(1.5, 1.5, 1.5),
                actor_name="LargeProp",
                tags=["prop"]
            ),
            ActorSpawnConfig(
                actor_class=unreal.StaticMeshActor,
                location=(-200.0, 0.0, 0.0),
                scale=(0.5, 0.5, 0.5),
                actor_name="SmallProp",
                tags=["prop"]
            )
        ]
        
        # Spawn all actors
        actors = batch_spawn_actors(configs)
        
        print(f"✓ Spawned {len(actors)} actors with custom configurations")
        for i, actor in enumerate(actors):
            print(f"  {i+1}. {actor.get_actor_label()}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_6_validate_single_asset():
    """
    Example 6: Validate a single asset
    
    This demonstrates validation of individual assets.
    
    NOTE: Update the asset paths to match your project!
    """
    print("\n" + "=" * 60)
    print("Example 6: Validate Single Asset")
    print("=" * 60)
    
    try:
        # Example texture path - update to match your project!
        texture_path = '/Game/Textures/T_ExampleTexture'
        
        print(f"Validating: {texture_path}")
        
        # Check if asset exists
        if not unreal.EditorAssetLibrary.does_asset_exist(texture_path):
            print(f"⚠ Asset not found: {texture_path}")
            print("  Please update the path in the script to match your project")
            return
        
        # Validate texture
        validator = TextureValidator(
            require_prefix=True,
            require_power_of_2=True,
            max_dimension=4096
        )
        
        result = validator.validate(texture_path)
        print("\n" + result.get_summary())
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_7_validate_folder():
    """
    Example 7: Validate all assets in a folder
    
    This demonstrates batch validation workflows.
    
    NOTE: Update the folder path to match your project!
    """
    print("\n" + "=" * 60)
    print("Example 7: Validate Folder")
    print("=" * 60)
    
    try:
        # Example folder - update to match your project!
        folder_path = '/Game/Textures'
        
        print(f"Validating folder: {folder_path}")
        
        # Check if folder exists
        if not unreal.EditorAssetLibrary.does_directory_exist(folder_path):
            print(f"⚠ Folder not found: {folder_path}")
            print("  Please update the path in the script to match your project")
            return
        
        # Validate all assets in folder
        results = validate_folder(
            folder_path=folder_path,
            recursive=True,
            validators=[
                TextureValidator(),
                MeshValidator(),
                MaterialValidator()
            ]
        )
        
        # Print summary
        total = len(results)
        passed = sum(1 for r in results if r.is_valid)
        failed = total - passed
        
        print(f"\n✓ Validation Complete")
        print(f"  Total assets: {total}")
        print(f"  Passed: {passed} ({100 * passed / total:.1f}%)")
        print(f"  Failed: {failed} ({100 * failed / total:.1f}%)")
        
        # Show failed assets
        if failed > 0:
            print(f"\n  Failed assets:")
            for result in results:
                if not result.is_valid:
                    print(f"    - {result.asset_name}: {len(result.issues)} issues")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_8_generate_validation_report():
    """
    Example 8: Generate validation report
    
    This demonstrates report generation for documentation.
    
    NOTE: Update paths to match your project!
    """
    print("\n" + "=" * 60)
    print("Example 8: Generate Validation Report")
    print("=" * 60)
    
    try:
        # Validate multiple asset paths
        asset_paths = [
            '/Game/Textures/T_Example1',
            '/Game/Meshes/SM_Example1',
            '/Game/Materials/M_Example1'
        ]
        
        print(f"Validating {len(asset_paths)} assets...")
        
        # Filter existing assets
        existing_paths = [
            path for path in asset_paths
            if unreal.EditorAssetLibrary.does_asset_exist(path)
        ]
        
        if not existing_paths:
            print("⚠ No assets found. Please update paths in the script.")
            return
        
        # Validate
        results = batch_validate_assets(existing_paths)
        
        # Generate report
        report_path = '/Temp/validation_report.txt'
        report = generate_validation_report(results, report_path)
        
        print(f"\n✓ Report generated")
        print(f"  Saved to: {report_path}")
        print("\n" + "=" * 60)
        print("REPORT PREVIEW:")
        print("=" * 60)
        # Print first 20 lines
        lines = report.split('\n')[:20]
        print('\n'.join(lines))
        if len(report.split('\n')) > 20:
            print("... (truncated)")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def run_all_examples():
    """Run all examples in sequence."""
    print("\n" + "=" * 60)
    print("UE Content Generation & Validation Examples")
    print("=" * 60)
    
    # Check if running in UE
    try:
        version = unreal.SystemLibrary.get_engine_version()
        print(f"\nUnreal Engine Version: {version}")
    except Exception:
        print("\n✗ ERROR: Not running inside Unreal Engine!")
        print("This script must be run from UE's Python environment.")
        return
    
    print("\nRunning examples...")
    print("\nNOTE: Some examples require updating asset paths to match your project!")
    print("      Examples that create geometry will modify your current level.")
    
    # Ask for confirmation
    response = input("\nContinue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Content Generation Examples
    print("\n" + "=" * 60)
    print("CONTENT GENERATION EXAMPLES")
    print("=" * 60)
    
    example_1_create_test_grid()
    example_2_create_circular_lights()
    example_3_scatter_props()
    example_4_create_material_library()
    example_5_batch_spawn_custom()
    
    # Validation Examples
    print("\n" + "=" * 60)
    print("CONTENT VALIDATION EXAMPLES")
    print("=" * 60)
    
    example_6_validate_single_asset()
    example_7_validate_folder()
    example_8_generate_validation_report()
    
    print("\n" + "=" * 60)
    print("All Examples Complete!")
    print("=" * 60)
    print("\nCheck your Unreal Editor for the generated content.")
    print("Review validation results for any issues found.")


# Individual example functions can be called directly
if __name__ == "__main__":
    run_all_examples()
