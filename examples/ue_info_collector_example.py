#!/usr/bin/env python3
"""
Example: Using UE Info Collector

This example demonstrates how to use the ue_info_collector.py script
to gather comprehensive information about your Unreal Engine project.

This example shows:
1. Basic usage - collecting all information
2. Selective collection - collecting only specific categories
3. Saving outputs in different formats
4. Using the information for analysis

IMPORTANT: This script must be run from within Unreal Engine's Python environment.
"""

import sys
import os

# Add plugin Python directory to path
plugin_python_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'Plugins', 'AdastreaDirector', 'Python'
)
if os.path.exists(plugin_python_dir):
    sys.path.insert(0, plugin_python_dir)

try:
    import ue_info_collector
    import unreal
except ImportError as e:
    print(f"Error: Failed to import required modules: {e}")
    print("Make sure you're running this inside Unreal Engine")
    sys.exit(1)


def example_basic_usage():
    """Example 1: Basic usage - collect all information."""
    print("\n" + "="*60)
    print("Example 1: Basic Usage - Collect All Information")
    print("="*60 + "\n")
    
    # Collect all information
    info = ue_info_collector.collect_all_info()
    
    # Print a summary report to console
    ue_info_collector.print_report(info)
    
    # Save to JSON
    json_file = ue_info_collector.save_to_json(info, "example_project_info.json")
    print(f"\n✓ JSON saved to: {json_file}")
    
    # Save to Markdown
    md_file = ue_info_collector.save_to_markdown(info, "example_project_info.md")
    print(f"✓ Markdown saved to: {md_file}")


def example_selective_collection():
    """Example 2: Selective collection - only collect specific categories."""
    print("\n" + "="*60)
    print("Example 2: Selective Collection")
    print("="*60 + "\n")
    
    # Create collector instance
    collector = ue_info_collector.UEInfoCollector()
    
    if not collector.available:
        print("✗ Collector not available")
        return
    
    # Collect only assets
    print("Collecting asset information only...")
    assets = collector.collect_asset_info()
    print(f"\n✓ Found {assets.get('total_assets', 0)} total assets")
    
    # Show top 5 asset types
    if "by_type" in assets and assets["by_type"]:
        print("\nTop 5 asset types:")
        for asset_type, count in list(assets["by_type"].items())[:5]:
            print(f"  {count:4d}  {asset_type}")
    
    # Collect only blueprints
    print("\n\nCollecting blueprint information only...")
    blueprints = collector.collect_blueprint_info()
    print(f"\n✓ Found {blueprints.get('total_blueprints', 0)} total blueprints")
    print(f"  - Actor Blueprints: {blueprints.get('actor_blueprints', 0)}")
    print(f"  - Widget Blueprints: {blueprints.get('widget_blueprints', 0)}")
    print(f"  - Animation Blueprints: {blueprints.get('animation_blueprints', 0)}")


def example_analysis():
    """Example 3: Using collected information for analysis."""
    print("\n" + "="*60)
    print("Example 3: Project Analysis")
    print("="*60 + "\n")
    
    # Collect information
    collector = ue_info_collector.UEInfoCollector()
    
    if not collector.available:
        print("✗ Collector not available")
        return
    
    # Analyze asset organization
    print("Analyzing asset organization...\n")
    
    assets = collector.collect_asset_info()
    
    # Check naming conventions
    if "naming_conventions" in assets:
        conventions = assets["naming_conventions"]
        total_assets = assets.get("total_assets", 1)
        
        print("NAMING CONVENTION COMPLIANCE:")
        print("-" * 60)
        
        has_prefix = conventions.get("has_prefix", 0)
        prefix_pct = (has_prefix / total_assets * 100) if total_assets > 0 else 0
        print(f"Assets with standard prefixes: {has_prefix}/{total_assets} ({prefix_pct:.1f}%)")
        
        if conventions.get("prefixes"):
            print("\nMost common prefixes:")
            for prefix, count in sorted(conventions["prefixes"].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {prefix}: {count}")
        
        # Recommendations
        print("\nRECOMMENDATIONS:")
        if prefix_pct < 80:
            print("  ⚠ Consider using consistent naming prefixes (BP_, M_, T_, etc.)")
        else:
            print("  ✓ Good naming convention compliance")
    
    # Analyze blueprint complexity
    print("\n\nAnalyzing blueprint complexity...\n")
    
    blueprints = collector.collect_blueprint_info()
    total_bps = blueprints.get("total_blueprints", 0)
    
    if total_bps > 0:
        print("BLUEPRINT DISTRIBUTION:")
        print("-" * 60)
        print(f"Total Blueprints: {total_bps}")
        print(f"  Actor BPs:     {blueprints.get('actor_blueprints', 0):4d} ({blueprints.get('actor_blueprints', 0)/total_bps*100:.1f}%)")
        print(f"  Widget BPs:    {blueprints.get('widget_blueprints', 0):4d} ({blueprints.get('widget_blueprints', 0)/total_bps*100:.1f}%)")
        print(f"  Anim BPs:      {blueprints.get('animation_blueprints', 0):4d} ({blueprints.get('animation_blueprints', 0)/total_bps*100:.1f}%)")
        print(f"  Component BPs: {blueprints.get('component_blueprints', 0):4d} ({blueprints.get('component_blueprints', 0)/total_bps*100:.1f}%)")
    
    # Analyze level content
    print("\n\nAnalyzing level content...\n")
    
    levels = collector.collect_level_info()
    
    if "actors" in levels:
        total_actors = levels["actors"].get("total", 0)
        print("LEVEL CONTENT:")
        print("-" * 60)
        print(f"Total Actors: {total_actors}")
        
        if "by_type" in levels["actors"] and levels["actors"]["by_type"]:
            print("\nTop actor types:")
            for actor_type, count in list(levels["actors"]["by_type"].items())[:5]:
                pct = (count / total_actors * 100) if total_actors > 0 else 0
                print(f"  {count:4d} ({pct:5.1f}%)  {actor_type}")
    
    # Material and texture analysis
    print("\n\nAnalyzing materials and textures...\n")
    
    materials = collector.collect_material_info()
    
    if "materials" in materials and "textures" in materials:
        mat_count = materials["materials"].get("total", 0)
        mi_count = materials["materials"].get("instances", 0)
        tex_count = materials["textures"].get("total", 0)
        
        print("MATERIAL ANALYSIS:")
        print("-" * 60)
        print(f"Materials:          {mat_count}")
        print(f"Material Instances: {mi_count}")
        print(f"Textures:           {tex_count}")
        
        if mat_count > 0:
            instance_ratio = mi_count / mat_count
            print(f"\nInstance Ratio: {instance_ratio:.2f} instances per material")
            
            if instance_ratio < 2:
                print("  ⚠ Consider using more material instances for better performance")
            elif instance_ratio > 10:
                print("  ℹ High instance usage - ensure material parents are optimized")
            else:
                print("  ✓ Good balance of materials and instances")


def example_project_health_check():
    """Example 4: Project health check."""
    print("\n" + "="*60)
    print("Example 4: Project Health Check")
    print("="*60 + "\n")
    
    # Collect all information
    info = ue_info_collector.collect_all_info()
    
    print("PROJECT HEALTH CHECK")
    print("-" * 60)
    
    issues = []
    warnings = []
    good = []
    
    # Check asset count
    total_assets = info.get("assets", {}).get("total_assets", 0)
    if total_assets == 0:
        issues.append("No assets found in project")
    elif total_assets < 10:
        warnings.append("Very few assets - is this a new project?")
    else:
        good.append(f"Project has {total_assets} assets")
    
    # Check blueprints
    total_bps = info.get("blueprints", {}).get("total_blueprints", 0)
    if total_bps == 0:
        warnings.append("No blueprints found")
    else:
        good.append(f"Project has {total_bps} blueprints")
    
    # Check source code
    has_source = info.get("source", {}).get("has_source", False)
    if has_source:
        source_files = info.get("source", {}).get("total_source_files", 0)
        good.append(f"Project has C++ source ({source_files} files)")
    
    # Check actors in level
    total_actors = info.get("levels", {}).get("actors", {}).get("total", 0)
    if total_actors == 0:
        warnings.append("No actors in current level")
    elif total_actors > 10000:
        warnings.append(f"Very high actor count ({total_actors}) - may impact performance")
    else:
        good.append(f"Level has {total_actors} actors")
    
    # Print results
    if issues:
        print("\n❌ ISSUES:")
        for issue in issues:
            print(f"  • {issue}")
    
    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  • {warning}")
    
    if good:
        print("\n✅ GOOD:")
        for item in good:
            print(f"  • {item}")
    
    if not issues and not warnings:
        print("\n✅ No issues found - project looks healthy!")
    
    print("\n" + "-" * 60)


def run_all_examples():
    """Run all examples."""
    print("\n" + "="*60)
    print("UE Info Collector - Examples")
    print("="*60)
    
    # Check if running in UE
    if not ue_info_collector.UNREAL_AVAILABLE:
        print("\n✗ ERROR: Not running inside Unreal Engine!")
        print("This script must be run from UE's Python environment.")
        return
    
    try:
        # Run examples
        example_basic_usage()
        
        input("\nPress Enter to continue to next example...")
        example_selective_collection()
        
        input("\nPress Enter to continue to next example...")
        example_analysis()
        
        input("\nPress Enter to continue to next example...")
        example_project_health_check()
        
        print("\n" + "="*60)
        print("All Examples Complete!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
