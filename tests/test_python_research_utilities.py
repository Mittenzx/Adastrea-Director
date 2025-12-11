#!/usr/bin/env python3
"""
Tests for UE Content Generation, Validation, and Batch Processing Utilities

These tests verify the functionality of the new Python utilities for Unreal Engine.

Note: These are unit tests for the utility classes themselves, not integration tests
that require a running Unreal Engine instance.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestContentGenerationUtilities(unittest.TestCase):
    """Test content generation utilities."""
    
    def test_actor_spawn_config_dataclass(self):
        """Test ActorSpawnConfig dataclass creation."""
        from ue_content_generation import ActorSpawnConfig
        
        config = ActorSpawnConfig(
            actor_class=Mock(),
            location=(100, 200, 300),
            actor_name="TestActor"
        )
        
        self.assertEqual(config.location, (100, 200, 300))
        self.assertEqual(config.actor_name, "TestActor")
        self.assertEqual(config.rotation, (0.0, 0.0, 0.0))  # Default
    
    def test_procedural_environment_generator_imports(self):
        """Test that ProceduralEnvironmentGenerator can be imported."""
        try:
            from ue_content_generation import ProceduralEnvironmentGenerator
            # Class exists
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import ProceduralEnvironmentGenerator")
    
    def test_material_system_automation_imports(self):
        """Test that MaterialSystemAutomation can be imported."""
        try:
            from ue_content_generation import MaterialSystemAutomation
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import MaterialSystemAutomation")
    
    def test_blueprint_template_system_imports(self):
        """Test that BlueprintTemplateSystem can be imported."""
        try:
            from ue_content_generation import BlueprintTemplateSystem
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import BlueprintTemplateSystem")


class TestContentValidationUtilities(unittest.TestCase):
    """Test content validation utilities."""
    
    def test_validation_severity_enum(self):
        """Test ValidationSeverity enum values."""
        from ue_content_validation import ValidationSeverity
        
        self.assertEqual(ValidationSeverity.INFO.value, "Info")
        self.assertEqual(ValidationSeverity.WARNING.value, "Warning")
        self.assertEqual(ValidationSeverity.ERROR.value, "Error")
        self.assertEqual(ValidationSeverity.CRITICAL.value, "Critical")
    
    def test_validation_result_dataclass(self):
        """Test ValidationResult dataclass."""
        from ue_content_validation import ValidationResult, ValidationSeverity
        
        result = ValidationResult(
            asset_path="/Game/Test",
            asset_name="Test",
            asset_class="Texture",
            is_valid=True
        )
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.issues), 0)
        
        # Add an issue
        result.add_issue("Test error", ValidationSeverity.ERROR)
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.issues), 1)
    
    def test_validation_result_summary(self):
        """Test ValidationResult summary generation."""
        from ue_content_validation import ValidationResult, ValidationSeverity
        
        result = ValidationResult(
            asset_path="/Game/Test",
            asset_name="TestAsset",
            asset_class="Texture",
            is_valid=True
        )
        
        result.add_warning("Test warning")
        result.add_info("Test info")
        
        summary = result.get_summary()
        self.assertIn("TestAsset", summary)
        self.assertIn("PASS", summary)
    
    def test_texture_validator_power_of_2_check(self):
        """Test power of 2 validation logic."""
        from ue_content_validation import TextureValidator
        
        # Test power of 2 detection
        self.assertTrue(TextureValidator._is_power_of_2(2))
        self.assertTrue(TextureValidator._is_power_of_2(4))
        self.assertTrue(TextureValidator._is_power_of_2(512))
        self.assertTrue(TextureValidator._is_power_of_2(1024))
        self.assertTrue(TextureValidator._is_power_of_2(2048))
        
        self.assertFalse(TextureValidator._is_power_of_2(3))
        self.assertFalse(TextureValidator._is_power_of_2(100))
        self.assertFalse(TextureValidator._is_power_of_2(1023))
    
    def test_naming_convention_validator(self):
        """Test naming convention validation."""
        from ue_content_validation import NamingConventionValidator
        
        # Test texture naming
        error = NamingConventionValidator.validate_asset_name(
            "T_Rock", "Texture"
        )
        self.assertIsNone(error)  # Valid
        
        error = NamingConventionValidator.validate_asset_name(
            "Rock", "Texture"
        )
        self.assertIsNotNone(error)  # Invalid
        self.assertIn("T_", error)
        
        # Test material naming
        error = NamingConventionValidator.validate_asset_name(
            "M_BaseMaterial", "Material"
        )
        self.assertIsNone(error)  # Valid
        
        error = NamingConventionValidator.validate_asset_name(
            "BaseMaterial", "Material"
        )
        self.assertIsNotNone(error)  # Invalid
    
    def test_validators_import(self):
        """Test that all validators can be imported."""
        try:
            from ue_content_validation import (
                TextureValidator,
                MeshValidator,
                MaterialValidator,
                BaseValidator
            )
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import validators")


class TestBatchProcessingUtilities(unittest.TestCase):
    """Test batch processing utilities."""
    
    def test_batch_result_dataclass(self):
        """Test BatchResult dataclass."""
        from ue_batch_processing import BatchResult
        
        result = BatchResult(
            total_count=10,
            success_count=8,
            failed_count=2,
            failed_items=["Item1", "Item2"],
            operation="Test Operation"
        )
        
        self.assertEqual(result.total_count, 10)
        self.assertEqual(result.success_count, 8)
        self.assertEqual(result.failed_count, 2)
    
    def test_batch_result_summary(self):
        """Test BatchResult summary generation."""
        from ue_batch_processing import BatchResult
        
        result = BatchResult(
            total_count=5,
            success_count=4,
            failed_count=1,
            failed_items=["FailedItem"],
            operation="Test Operation"
        )
        
        summary = result.get_summary()
        self.assertIn("Test Operation", summary)
        self.assertIn("Total: 5", summary)
        self.assertIn("Success: 4", summary)
        self.assertIn("FailedItem", summary)
    
    def test_batch_processors_import(self):
        """Test that batch processors can be imported."""
        try:
            from ue_batch_processing import (
                AssetBatchProcessor,
                LevelBatchOperations,
                batch_generate_lods,
                batch_optimize_textures
            )
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import batch processors")


class TestModuleStructure(unittest.TestCase):
    """Test overall module structure and documentation."""
    
    def test_content_generation_module_docstring(self):
        """Test content generation module has proper documentation."""
        import ue_content_generation
        
        self.assertIsNotNone(ue_content_generation.__doc__)
        self.assertIn("Content Generation", ue_content_generation.__doc__)
    
    def test_content_validation_module_docstring(self):
        """Test content validation module has proper documentation."""
        import ue_content_validation
        
        self.assertIsNotNone(ue_content_validation.__doc__)
        self.assertIn("Content Validation", ue_content_validation.__doc__)
    
    def test_batch_processing_module_docstring(self):
        """Test batch processing module has proper documentation."""
        import ue_batch_processing
        
        self.assertIsNotNone(ue_batch_processing.__doc__)
        self.assertIn("Batch Processing", ue_batch_processing.__doc__)
    
    def test_all_modules_have_logger(self):
        """Test that all modules set up logging."""
        import ue_content_generation
        import ue_content_validation
        import ue_batch_processing
        
        # Check that logger is defined
        self.assertTrue(hasattr(ue_content_generation, 'logger'))
        self.assertTrue(hasattr(ue_content_validation, 'logger'))
        self.assertTrue(hasattr(ue_batch_processing, 'logger'))
    
    def test_modules_check_unreal_availability(self):
        """Test that modules check for Unreal availability."""
        import ue_content_generation
        import ue_content_validation
        import ue_batch_processing
        
        # Check that UNREAL_AVAILABLE is defined
        self.assertTrue(hasattr(ue_content_generation, 'UNREAL_AVAILABLE'))
        self.assertTrue(hasattr(ue_content_validation, 'UNREAL_AVAILABLE'))
        self.assertTrue(hasattr(ue_batch_processing, 'UNREAL_AVAILABLE'))


class TestResearchDocument(unittest.TestCase):
    """Test that research document exists and is properly formatted."""
    
    def test_research_document_exists(self):
        """Test that research document file exists."""
        doc_path = os.path.join(project_root, 'PYTHON_RESEARCH_UE427.md')
        self.assertTrue(os.path.exists(doc_path), 
                       f"Research document not found at {doc_path}")
    
    def test_research_document_content(self):
        """Test that research document has expected sections."""
        doc_path = os.path.join(project_root, 'PYTHON_RESEARCH_UE427.md')
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key sections
        self.assertIn("# Unreal Engine Python API Research", content)
        self.assertIn("## Core Python API Capabilities", content)
        self.assertIn("## Content Generation Strategies", content)
        self.assertIn("## Content Validation Framework", content)
        self.assertIn("## New Implementation Areas", content)
        self.assertIn("## Best Practices", content)
        
        # Check for UE 5.7 reference
        self.assertIn("5.7", content)
        
        # Check for references
        self.assertIn("## References", content)


class TestExamplesScript(unittest.TestCase):
    """Test that examples script exists and is properly structured."""
    
    def test_examples_script_exists(self):
        """Test that examples script exists."""
        examples_path = os.path.join(
            project_root, 'examples', 'python_research_demo.py'
        )
        self.assertTrue(os.path.exists(examples_path),
                       f"Examples script not found at {examples_path}")
    
    def test_examples_script_has_functions(self):
        """Test that examples script has example functions."""
        examples_path = os.path.join(
            project_root, 'examples', 'python_research_demo.py'
        )
        
        with open(examples_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for example functions
        self.assertIn("def example_1_create_test_grid", content)
        self.assertIn("def example_2_create_circular_lights", content)
        self.assertIn("def example_3_scatter_props", content)
        self.assertIn("def example_4_create_material_library", content)
        self.assertIn("def example_5_batch_spawn_custom", content)
        self.assertIn("def example_6_validate_single_asset", content)
        self.assertIn("def example_7_validate_folder", content)
        self.assertIn("def example_8_generate_validation_report", content)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestContentGenerationUtilities))
    suite.addTests(loader.loadTestsFromTestCase(TestContentValidationUtilities))
    suite.addTests(loader.loadTestsFromTestCase(TestBatchProcessingUtilities))
    suite.addTests(loader.loadTestsFromTestCase(TestModuleStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestResearchDocument))
    suite.addTests(loader.loadTestsFromTestCase(TestExamplesScript))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
