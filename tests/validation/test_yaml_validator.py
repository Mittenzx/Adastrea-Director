"""
Tests for the YAML Validator.
"""

import pytest
import tempfile
import shutil

from validation.schema_manager import SchemaManager
from validation.yaml_validator import YAMLValidator


class TestYAMLValidator:
    """Tests for YAMLValidator class."""
    
    @pytest.fixture
    def temp_schema_dir(self):
        """Create a temporary schema directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def schema_manager(self, temp_schema_dir):
        """Create a SchemaManager."""
        manager = SchemaManager(schema_dir=temp_schema_dir)
        manager.load_schemas()
        return manager
    
    @pytest.fixture
    def validator(self, schema_manager):
        """Create a YAMLValidator."""
        return YAMLValidator(schema_manager)
    
    def test_initialization(self, validator, schema_manager):
        """Test YAMLValidator initialization."""
        assert validator.schema_manager == schema_manager
    
    def test_validate_valid_config(self, validator):
        """Test validating valid config YAML."""
        yaml_content = """
version: "1.0.0"
settings:
  key: value
"""
        
        result = validator.validate(yaml_content, schema_type='config')
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.schema_type == 'config'
    
    def test_validate_missing_required_field(self, validator):
        """Test validating YAML with missing required field."""
        yaml_content = """
settings:
  key: value
"""
        
        result = validator.validate(yaml_content, schema_type='config')
        
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any('version' in error for error in result.errors)
    
    def test_validate_invalid_yaml_syntax(self, validator):
        """Test validating invalid YAML syntax."""
        yaml_content = "invalid: yaml: syntax:"
        
        result = validator.validate(yaml_content, schema_type='config')
        
        assert not result.is_valid
        assert any('parsing error' in error.lower() for error in result.errors)
    
    def test_validate_with_auto_detect(self, validator):
        """Test validation with schema auto-detection."""
        yaml_content = """
version: "1.0.0"
settings:
  key: value
"""
        
        result = validator.validate(yaml_content)  # No schema_type provided
        
        assert result.is_valid
        assert result.schema_type == 'config'
    
    def test_validate_auto_detect_failure(self, validator):
        """Test validation when auto-detection fails."""
        yaml_content = """
unknown_field: value
"""
        
        result = validator.validate(yaml_content)  # No schema_type provided
        
        assert result.is_valid  # No validation performed
        assert len(result.warnings) > 0
        assert any('auto-detect' in warning.lower() for warning in result.warnings)
    
    def test_validate_nonexistent_schema(self, validator):
        """Test validating with non-existent schema."""
        yaml_content = """
field: value
"""
        
        result = validator.validate(yaml_content, schema_type='nonexistent')
        
        assert result.is_valid  # No validation performed
        assert len(result.warnings) > 0
        assert any('schema not found' in warning.lower() for warning in result.warnings)
    
    def test_suggest_fixes_for_missing_field(self, validator):
        """Test fix suggestions for missing required field."""
        yaml_content = """
settings:
  key: value
"""
        
        result = validator.validate(yaml_content, schema_type='config')
        fixes = validator.suggest_fixes(result)
        
        assert len(fixes) > 0
        assert any(fix.fix_type == 'add_field' for fix in fixes)
        assert any(fix.auto_fixable for fix in fixes)
    
    def test_auto_fix_missing_required_field(self, validator):
        """Test auto-fixing missing required field."""
        yaml_content = """
settings:
  key: value
"""
        
        result = validator.validate(yaml_content, schema_type='config')
        fixed_yaml = validator.auto_fix(yaml_content, result)
        
        # Validate fixed YAML
        fixed_result = validator.validate(fixed_yaml, schema_type='config')
        assert fixed_result.is_valid
        assert 'version' in fixed_yaml
    
    def test_auto_fix_unparseable_yaml(self, validator):
        """Test auto-fix with unparseable YAML returns original."""
        yaml_content = "invalid: yaml: syntax:"
        
        result = validator.validate(yaml_content, schema_type='config')
        fixed_yaml = validator.auto_fix(yaml_content, result)
        
        # Should return original since it can't be parsed
        assert fixed_yaml == yaml_content
    
    def test_validate_data_table(self, validator):
        """Test validating data table YAML."""
        yaml_content = """
table: MyDataTable
rows:
  - id: 1
    name: Item1
  - id: 2
    name: Item2
"""
        
        result = validator.validate(yaml_content, schema_type='data_table')
        
        assert result.is_valid
        assert result.schema_type == 'data_table'
    
    def test_validate_asset(self, validator):
        """Test validating asset YAML."""
        yaml_content = """
name: MyBlueprint
type: Blueprint
properties:
  health: 100
  speed: 5.0
"""
        
        result = validator.validate(yaml_content, schema_type='asset')
        
        assert result.is_valid
        assert result.schema_type == 'asset'
    
    def test_validate_asset_invalid_type(self, validator):
        """Test validating asset with invalid type enum."""
        yaml_content = """
name: MyAsset
type: InvalidType
properties:
  key: value
"""
        
        result = validator.validate(yaml_content, schema_type='asset')
        
        assert not result.is_valid
        assert any('is not one of' in error for error in result.errors)
    
    def test_suggest_fixes_for_enum_violation(self, validator):
        """Test fix suggestions for enum violation."""
        yaml_content = """
name: MyAsset
type: InvalidType
properties:
  key: value
"""
        
        result = validator.validate(yaml_content, schema_type='asset')
        fixes = validator.suggest_fixes(result)
        
        assert len(fixes) > 0
        assert any(fix.fix_type == 'fix_enum' for fix in fixes)
    
    def test_validate_complex_nested_structure(self, validator):
        """Test validating complex nested YAML structure."""
        yaml_content = """
version: "2.0.0"
settings:
  database:
    host: localhost
    port: 5432
  features:
    - name: feature1
      enabled: true
    - name: feature2
      enabled: false
"""
        
        result = validator.validate(yaml_content, schema_type='config')
        
        # Should be valid (schema allows any object for settings)
        assert result.is_valid
