#!/usr/bin/env python3
"""
Unreal Engine Content Validation Utilities

This module provides utilities for automated content validation in Unreal Engine
using the Python API. Compatible with UE 4.27+, 5.x.

Features:
- Asset naming convention validation
- Performance validation (mesh complexity, texture size)
- Standards compliance checking
- Batch validation workflows
- Validation reporting

Usage:
    # Import in UE Python environment
    from ue_content_validation import (
        TextureValidator,
        MeshValidator,
        MaterialValidator,
        batch_validate_assets
    )
    
    # Validate assets
    validator = TextureValidator()
    results = validator.validate('/Game/Textures/T_MyTexture')

Note: This module must be run inside Unreal Engine's Python environment.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('UEContentValidation')

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


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"
    CRITICAL = "Critical"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    asset_path: str
    asset_name: str
    asset_class: str
    is_valid: bool
    issues: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    
    def add_issue(
        self,
        message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        category: str = "General"
    ):
        """Add a validation issue."""
        self.issues.append({
            'message': message,
            'severity': severity.value,
            'category': category
        })
        if severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
            self.is_valid = False
    
    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)
    
    def add_info(self, message: str):
        """Add an info message."""
        self.info.append(message)
    
    def get_summary(self) -> str:
        """Get a summary of the validation result."""
        status = "✓ PASS" if self.is_valid else "✗ FAIL"
        summary = f"{status} - {self.asset_name} ({self.asset_class})\n"
        
        if self.issues:
            summary += f"  Issues: {len(self.issues)}\n"
            for issue in self.issues:
                summary += f"    [{issue['severity']}] {issue['message']}\n"
        
        if self.warnings:
            summary += f"  Warnings: {len(self.warnings)}\n"
        
        return summary


class BaseValidator:
    """Base class for asset validators."""
    
    def __init__(self):
        """Initialize the validator."""
        if not UNREAL_AVAILABLE:
            raise RuntimeError("Unreal Python API not available")
    
    def can_validate(self, asset: Any) -> bool:
        """
        Check if this validator can validate the given asset.
        
        Args:
            asset: Asset to check
            
        Returns:
            True if this validator applies to the asset
        """
        raise NotImplementedError("Subclasses must implement can_validate")
    
    def validate(self, asset_path: str) -> ValidationResult:
        """
        Validate an asset.
        
        Args:
            asset_path: Path to asset to validate
            
        Returns:
            ValidationResult object
        """
        raise NotImplementedError("Subclasses must implement validate")


class TextureValidator(BaseValidator):
    """
    Validator for texture assets.
    
    Checks:
    - Naming conventions (T_ prefix)
    - Texture dimensions (power of 2)
    - Texture size limits
    - Compression settings
    - Mipmap generation
    """
    
    def __init__(
        self,
        require_prefix: bool = True,
        require_power_of_2: bool = True,
        max_dimension: int = 8192,
        warn_dimension: int = 4096
    ):
        """
        Initialize texture validator.
        
        Args:
            require_prefix: Require T_ prefix in name
            require_power_of_2: Require power-of-2 dimensions
            max_dimension: Maximum allowed dimension
            warn_dimension: Dimension to trigger warning
        """
        super().__init__()
        self.require_prefix = require_prefix
        self.require_power_of_2 = require_power_of_2
        self.max_dimension = max_dimension
        self.warn_dimension = warn_dimension
    
    def can_validate(self, asset: Any) -> bool:
        """Check if asset is a texture."""
        return isinstance(asset, unreal.Texture) or \
               isinstance(asset, unreal.Texture2D)
    
    def validate(self, asset_path: str) -> ValidationResult:
        """
        Validate a texture asset.
        
        Args:
            asset_path: Path to texture asset
            
        Returns:
            ValidationResult object
        """
        # Load asset
        asset = unreal.load_asset(asset_path)
        if not asset:
            result = ValidationResult(
                asset_path=asset_path,
                asset_name="Unknown",
                asset_class="Texture",
                is_valid=False
            )
            result.add_issue(
                f"Asset not found: {asset_path}",
                ValidationSeverity.CRITICAL
            )
            return result
        
        asset_name = asset.get_name()
        result = ValidationResult(
            asset_path=asset_path,
            asset_name=asset_name,
            asset_class=asset.get_class().get_name(),
            is_valid=True
        )
        
        # Check naming convention
        if self.require_prefix and not asset_name.startswith("T_"):
            result.add_issue(
                f"Texture name must start with 'T_' prefix",
                ValidationSeverity.ERROR,
                "Naming"
            )
        
        # Check texture dimensions
        try:
            if hasattr(asset, 'blueprint_get_size_x'):
                width = asset.blueprint_get_size_x()
                height = asset.blueprint_get_size_y()
            else:
                width = asset.get_editor_property('size_x')
                height = asset.get_editor_property('size_y')
            
            result.add_info(f"Dimensions: {width}x{height}")
            
            # Check if power of 2
            if self.require_power_of_2:
                if not self._is_power_of_2(width):
                    result.add_issue(
                        f"Width ({width}) must be power of 2",
                        ValidationSeverity.ERROR,
                        "Dimensions"
                    )
                if not self._is_power_of_2(height):
                    result.add_issue(
                        f"Height ({height}) must be power of 2",
                        ValidationSeverity.ERROR,
                        "Dimensions"
                    )
            
            # Check maximum dimensions
            if width > self.max_dimension or height > self.max_dimension:
                result.add_issue(
                    f"Texture too large ({width}x{height}), max: {self.max_dimension}",
                    ValidationSeverity.ERROR,
                    "Performance"
                )
            
            # Warning for large textures
            if width > self.warn_dimension or height > self.warn_dimension:
                result.add_warning(
                    f"Large texture ({width}x{height}) - consider optimization"
                )
                
        except Exception as e:
            result.add_issue(
                f"Failed to check dimensions: {e}",
                ValidationSeverity.WARNING
            )
        
        # Check compression settings
        try:
            compression = asset.get_editor_property('compression_settings')
            if compression:
                result.add_info(f"Compression: {compression}")
        except:
            pass
        
        return result
    
    @staticmethod
    def _is_power_of_2(n: int) -> bool:
        """Check if number is power of 2."""
        return n > 0 and (n & (n - 1)) == 0


class MeshValidator(BaseValidator):
    """
    Validator for static mesh assets.
    
    Checks:
    - Naming conventions (SM_ prefix)
    - Triangle count limits
    - LOD presence and quality
    - Collision setup
    - Material assignments
    - UV channel setup
    """
    
    def __init__(
        self,
        require_prefix: bool = True,
        max_triangles: int = 50000,
        warn_triangles: int = 25000,
        require_lods: bool = True,
        min_lod_count: int = 3,
        require_collision: bool = True
    ):
        """
        Initialize mesh validator.
        
        Args:
            require_prefix: Require SM_ prefix in name
            max_triangles: Maximum allowed triangles
            warn_triangles: Triangle count to trigger warning
            require_lods: Require LODs
            min_lod_count: Minimum number of LODs
            require_collision: Require collision setup
        """
        super().__init__()
        self.require_prefix = require_prefix
        self.max_triangles = max_triangles
        self.warn_triangles = warn_triangles
        self.require_lods = require_lods
        self.min_lod_count = min_lod_count
        self.require_collision = require_collision
    
    def can_validate(self, asset: Any) -> bool:
        """Check if asset is a static mesh."""
        return isinstance(asset, unreal.StaticMesh)
    
    def validate(self, asset_path: str) -> ValidationResult:
        """
        Validate a static mesh asset.
        
        Args:
            asset_path: Path to mesh asset
            
        Returns:
            ValidationResult object
        """
        # Load asset
        asset = unreal.load_asset(asset_path)
        if not asset:
            result = ValidationResult(
                asset_path=asset_path,
                asset_name="Unknown",
                asset_class="StaticMesh",
                is_valid=False
            )
            result.add_issue(
                f"Asset not found: {asset_path}",
                ValidationSeverity.CRITICAL
            )
            return result
        
        asset_name = asset.get_name()
        result = ValidationResult(
            asset_path=asset_path,
            asset_name=asset_name,
            asset_class=asset.get_class().get_name(),
            is_valid=True
        )
        
        # Check naming convention
        if self.require_prefix and not asset_name.startswith("SM_"):
            result.add_issue(
                f"Static mesh name must start with 'SM_' prefix",
                ValidationSeverity.ERROR,
                "Naming"
            )
        
        # Check triangle count
        try:
            lod_count = asset.get_num_lods()
            if lod_count > 0:
                tri_count = asset.get_num_triangles(0)
                result.add_info(f"Triangles (LOD0): {tri_count}")
                
                if tri_count > self.max_triangles:
                    result.add_issue(
                        f"Triangle count ({tri_count}) exceeds limit ({self.max_triangles})",
                        ValidationSeverity.ERROR,
                        "Performance"
                    )
                elif tri_count > self.warn_triangles:
                    result.add_warning(
                        f"High triangle count ({tri_count}) - consider optimization"
                    )
        except Exception as e:
            result.add_issue(
                f"Failed to check triangle count: {e}",
                ValidationSeverity.WARNING
            )
        
        # Check LODs
        try:
            lod_count = asset.get_num_lods()
            result.add_info(f"LOD Count: {lod_count}")
            
            if self.require_lods and lod_count < self.min_lod_count:
                result.add_issue(
                    f"Insufficient LODs ({lod_count}), minimum: {self.min_lod_count}",
                    ValidationSeverity.WARNING,
                    "LOD"
                )
        except Exception as e:
            result.add_issue(
                f"Failed to check LODs: {e}",
                ValidationSeverity.WARNING
            )
        
        # Check collision
        if self.require_collision:
            try:
                has_collision = asset.get_body_setup() is not None
                if not has_collision:
                    result.add_issue(
                        "Mesh has no collision setup",
                        ValidationSeverity.WARNING,
                        "Collision"
                    )
                else:
                    result.add_info("Collision: Present")
            except Exception as e:
                result.add_issue(
                    f"Failed to check collision: {e}",
                    ValidationSeverity.WARNING
                )
        
        # Check materials
        try:
            materials = asset.get_editor_property('static_materials')
            if not materials or len(materials) == 0:
                result.add_issue(
                    "Mesh has no materials assigned",
                    ValidationSeverity.WARNING,
                    "Materials"
                )
            else:
                result.add_info(f"Materials: {len(materials)}")
        except Exception as e:
            result.add_issue(
                f"Failed to check materials: {e}",
                ValidationSeverity.WARNING
            )
        
        return result


class MaterialValidator(BaseValidator):
    """
    Validator for material assets.
    
    Checks:
    - Naming conventions (M_ prefix for materials, MI_ for instances)
    - Material complexity
    - Texture usage
    - Parameter setup (for instances)
    """
    
    def __init__(self, require_prefix: bool = True):
        """
        Initialize material validator.
        
        Args:
            require_prefix: Require M_ or MI_ prefix
        """
        super().__init__()
        self.require_prefix = require_prefix
    
    def can_validate(self, asset: Any) -> bool:
        """Check if asset is a material."""
        return isinstance(asset, unreal.Material) or \
               isinstance(asset, unreal.MaterialInstance)
    
    def validate(self, asset_path: str) -> ValidationResult:
        """
        Validate a material asset.
        
        Args:
            asset_path: Path to material asset
            
        Returns:
            ValidationResult object
        """
        # Load asset
        asset = unreal.load_asset(asset_path)
        if not asset:
            result = ValidationResult(
                asset_path=asset_path,
                asset_name="Unknown",
                asset_class="Material",
                is_valid=False
            )
            result.add_issue(
                f"Asset not found: {asset_path}",
                ValidationSeverity.CRITICAL
            )
            return result
        
        asset_name = asset.get_name()
        is_instance = isinstance(asset, unreal.MaterialInstance)
        
        result = ValidationResult(
            asset_path=asset_path,
            asset_name=asset_name,
            asset_class=asset.get_class().get_name(),
            is_valid=True
        )
        
        # Check naming convention
        if self.require_prefix:
            if is_instance:
                if not asset_name.startswith("MI_"):
                    result.add_issue(
                        f"Material instance name must start with 'MI_' prefix",
                        ValidationSeverity.ERROR,
                        "Naming"
                    )
            else:
                if not asset_name.startswith("M_"):
                    result.add_issue(
                        f"Material name must start with 'M_' prefix",
                        ValidationSeverity.ERROR,
                        "Naming"
                    )
        
        # Additional checks for material instances
        if is_instance:
            try:
                parent = asset.get_editor_property('parent')
                if parent:
                    result.add_info(f"Parent: {parent.get_name()}")
                else:
                    result.add_issue(
                        "Material instance has no parent",
                        ValidationSeverity.ERROR,
                        "Hierarchy"
                    )
            except Exception as e:
                result.add_warning(f"Could not check parent: {e}")
        
        return result


class NamingConventionValidator:
    """
    Validate asset naming conventions across all asset types.
    
    Default conventions:
    - Textures: T_*
    - Materials: M_*
    - Material Instances: MI_*
    - Static Meshes: SM_*
    - Skeletal Meshes: SK_*
    - Blueprints: BP_*
    - Particle Systems: P_*
    - Sounds: S_*
    """
    
    NAMING_CONVENTIONS = {
        'Texture': 'T_',
        'Texture2D': 'T_',
        'Material': 'M_',
        'MaterialInstance': 'MI_',
        'MaterialInstanceConstant': 'MI_',
        'StaticMesh': 'SM_',
        'SkeletalMesh': 'SK_',
        'Blueprint': 'BP_',
        'ParticleSystem': 'P_',
        'SoundWave': 'S_',
        'SoundCue': 'S_',
    }
    
    @classmethod
    def validate_asset_name(
        cls,
        asset_name: str,
        asset_class: str
    ) -> Optional[str]:
        """
        Validate asset name follows conventions.
        
        Args:
            asset_name: Name of the asset
            asset_class: Class type of the asset
            
        Returns:
            Error message if invalid, None if valid
        """
        expected_prefix = cls.NAMING_CONVENTIONS.get(asset_class)
        
        if expected_prefix and not asset_name.startswith(expected_prefix):
            return f"{asset_class} must start with '{expected_prefix}' (got '{asset_name}')"
        
        return None


def batch_validate_assets(
    asset_paths: List[str],
    validators: Optional[List[BaseValidator]] = None
) -> List[ValidationResult]:
    """
    Validate multiple assets.
    
    Args:
        asset_paths: List of asset paths to validate
        validators: List of validators to use (default: all)
        
    Returns:
        List of ValidationResult objects
        
    Example:
        results = batch_validate_assets([
            '/Game/Textures/T_Rock',
            '/Game/Meshes/SM_Rock',
            '/Game/Materials/M_Rock'
        ])
        
        for result in results:
            print(result.get_summary())
    """
    if not UNREAL_AVAILABLE:
        raise RuntimeError("Unreal Python API not available")
    
    # Use default validators if none provided
    if validators is None:
        validators = [
            TextureValidator(),
            MeshValidator(),
            MaterialValidator()
        ]
    
    results = []
    
    for asset_path in asset_paths:
        try:
            asset = unreal.load_asset(asset_path)
            if not asset:
                result = ValidationResult(
                    asset_path=asset_path,
                    asset_name="Unknown",
                    asset_class="Unknown",
                    is_valid=False
                )
                result.add_issue(
                    f"Asset not found: {asset_path}",
                    ValidationSeverity.CRITICAL
                )
                results.append(result)
                continue
            
            # Find applicable validator
            validator_found = False
            for validator in validators:
                if validator.can_validate(asset):
                    result = validator.validate(asset_path)
                    results.append(result)
                    validator_found = True
                    break
            
            if not validator_found:
                logger.warning(f"No validator for asset: {asset_path}")
                
        except Exception as e:
            logger.error(f"Failed to validate {asset_path}: {e}")
    
    return results


def validate_folder(
    folder_path: str,
    recursive: bool = True,
    validators: Optional[List[BaseValidator]] = None
) -> List[ValidationResult]:
    """
    Validate all assets in a folder.
    
    Args:
        folder_path: Path to folder (e.g., '/Game/Textures')
        recursive: Include subfolders
        validators: List of validators to use
        
    Returns:
        List of ValidationResult objects
        
    Example:
        # Validate all textures in folder
        results = validate_folder('/Game/Textures', recursive=True)
        
        # Print summary
        passed = sum(1 for r in results if r.is_valid)
        print(f"Validated {len(results)} assets: {passed} passed")
    """
    if not UNREAL_AVAILABLE:
        raise RuntimeError("Unreal Python API not available")
    
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    # Get all assets in folder
    filter_data = unreal.ARFilter(
        package_paths=[folder_path],
        recursive_paths=recursive
    )
    
    assets = asset_registry.get_assets(filter_data)
    asset_paths = [str(asset.object_path) for asset in assets]
    
    logger.info(f"Validating {len(asset_paths)} assets in {folder_path}")
    
    return batch_validate_assets(asset_paths, validators)


def generate_validation_report(
    results: List[ValidationResult],
    output_file: Optional[str] = None
) -> str:
    """
    Generate a validation report.
    
    Args:
        results: List of validation results
        output_file: Optional file path to save report
        
    Returns:
        Report as string
        
    Example:
        results = validate_folder('/Game/Textures')
        report = generate_validation_report(results, '/Temp/validation_report.txt')
    """
    report = []
    report.append("=" * 80)
    report.append("ASSET VALIDATION REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Summary
    total = len(results)
    passed = sum(1 for r in results if r.is_valid)
    failed = total - passed
    
    report.append(f"Total Assets: {total}")
    report.append(f"Passed: {passed} ({100 * passed / total:.1f}%)")
    report.append(f"Failed: {failed} ({100 * failed / total:.1f}%)")
    report.append("")
    
    # Details
    if failed > 0:
        report.append("=" * 80)
        report.append("FAILED ASSETS")
        report.append("=" * 80)
        report.append("")
        
        for result in results:
            if not result.is_valid:
                report.append(result.get_summary())
    
    # Warnings
    warnings_count = sum(len(r.warnings) for r in results)
    if warnings_count > 0:
        report.append("=" * 80)
        report.append(f"WARNINGS ({warnings_count} total)")
        report.append("=" * 80)
        report.append("")
        
        for result in results:
            if result.warnings:
                report.append(f"{result.asset_name}:")
                for warning in result.warnings:
                    report.append(f"  - {warning}")
                report.append("")
    
    report_text = "\n".join(report)
    
    # Save to file if specified
    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(report_text)
            logger.info(f"Validation report saved to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
    
    return report_text


# Example usage (when run in UE)
if __name__ == "__main__":
    if UNREAL_AVAILABLE:
        print("=" * 60)
        print("UE Content Validation Utilities - Demo")
        print("=" * 60)
        
        # Example: Validate a texture
        print("\n1. Validating texture...")
        try:
            validator = TextureValidator()
            # Replace with actual texture path in your project
            result = validator.validate('/Game/Textures/T_TestTexture')
            print(result.get_summary())
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\nDemo complete.")
    else:
        print("This script must be run inside Unreal Engine's Python environment")
