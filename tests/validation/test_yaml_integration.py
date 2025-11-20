"""
Integration tests for YAML validation with Code Generation Agent.
"""

import pytest

from validation.schema_manager import SchemaManager
from validation.yaml_validator import YAMLValidator


class TestYAMLIntegration:
    """Integration tests for YAML validation system."""
    
    @pytest.fixture
    def validator_system(self):
        """Create a complete validation system."""
        schema_manager = SchemaManager()
        schema_manager.load_schemas()
        validator = YAMLValidator(schema_manager)
        return validator
    
    def test_config_validation_workflow(self, validator_system):
        """Test complete workflow: validate, fix, re-validate."""
        # Invalid config (missing version)
        invalid_yaml = """
settings:
  database:
    host: localhost
    port: 5432
"""
        
        # Validate
        result = validator_system.validate(invalid_yaml, schema_type='config')
        assert not result.is_valid
        assert any('version' in error for error in result.errors)
        
        # Auto-fix
        fixed_yaml = validator_system.auto_fix(invalid_yaml, result)
        
        # Re-validate
        result2 = validator_system.validate(fixed_yaml, schema_type='config')
        assert result2.is_valid
        assert 'version' in fixed_yaml
    
    def test_data_table_generation_and_validation(self, validator_system):
        """Test generating and validating data table YAML."""
        # Valid data table
        yaml_content = """
table: ItemsTable
rows:
  - id: 1
    name: Sword
    damage: 10
  - id: 2
    name: Shield
    defense: 15
"""
        
        result = validator_system.validate(yaml_content, schema_type='data_table')
        assert result.is_valid
        assert result.schema_type == 'data_table'
    
    def test_asset_with_enum_validation(self, validator_system):
        """Test asset YAML with enum validation."""
        # Valid asset
        valid_asset = """
name: PlayerCharacter
type: Blueprint
properties:
  health: 100
  speed: 5.0
"""
        
        result = validator_system.validate(valid_asset, schema_type='asset')
        assert result.is_valid
        
        # Invalid asset (wrong enum value)
        invalid_asset = """
name: PlayerCharacter
type: InvalidType
properties:
  health: 100
"""
        
        result2 = validator_system.validate(invalid_asset, schema_type='asset')
        assert not result2.is_valid
        assert any('is not one of' in error for error in result2.errors)
    
    def test_fix_suggestions_workflow(self, validator_system):
        """Test getting and applying fix suggestions."""
        invalid_yaml = """
name: MyAsset
type: InvalidType
"""
        
        result = validator_system.validate(invalid_yaml, schema_type='asset')
        fixes = validator_system.suggest_fixes(result)
        
        assert len(fixes) > 0
        assert any(fix.fix_type == 'fix_enum' for fix in fixes)
        assert any('Blueprint' in fix.fix_description for fix in fixes)
    
    def test_auto_detect_and_validate(self, validator_system):
        """Test auto-detection combined with validation."""
        # Config-like structure
        yaml_content = """
version: "2.0.0"
settings:
  feature_flags:
    enable_new_ui: true
    enable_analytics: false
"""
        
        # Validate with auto-detection
        result = validator_system.validate(yaml_content)
        
        assert result.is_valid
        assert result.schema_type == 'config'
    
    def test_complex_nested_yaml_validation(self, validator_system):
        """Test validation of complex nested structures."""
        complex_yaml = """
version: "3.0.0"
settings:
  server:
    host: "0.0.0.0"
    port: 8080
    ssl:
      enabled: true
      cert_path: "/etc/ssl/cert.pem"
  database:
    primary:
      host: "db1.example.com"
      port: 5432
    replicas:
      - host: "db2.example.com"
        port: 5432
      - host: "db3.example.com"
        port: 5432
"""
        
        result = validator_system.validate(complex_yaml, schema_type='config')
        assert result.is_valid
    
    def test_validation_error_messages_are_helpful(self, validator_system):
        """Test that error messages are clear and actionable."""
        invalid_yaml = """
settings:
  key: value
"""
        
        result = validator_system.validate(invalid_yaml, schema_type='config')
        
        assert not result.is_valid
        assert len(result.errors) > 0
        
        # Error should mention the missing field
        error_text = ' '.join(result.errors)
        assert 'version' in error_text.lower()
        assert 'required' in error_text.lower()
