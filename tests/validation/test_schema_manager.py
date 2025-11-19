"""
Tests for the Schema Manager.
"""

import json
import os
import pytest
import tempfile
import shutil
from pathlib import Path

from validation.schema_manager import SchemaManager


class TestSchemaManager:
    """Tests for SchemaManager class."""
    
    @pytest.fixture
    def temp_schema_dir(self):
        """Create a temporary schema directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def schema_manager(self, temp_schema_dir):
        """Create a SchemaManager with temp directory."""
        return SchemaManager(schema_dir=temp_schema_dir)
    
    def test_initialization(self, schema_manager, temp_schema_dir):
        """Test SchemaManager initialization."""
        assert schema_manager.schema_dir == Path(temp_schema_dir)
        assert schema_manager.schemas == {}
        assert not schema_manager._loaded
    
    def test_load_schemas_creates_default(self, schema_manager):
        """Test that load_schemas creates default schemas if none exist."""
        schema_manager.load_schemas()
        
        assert schema_manager._loaded
        assert len(schema_manager.schemas) > 0
        assert 'config' in schema_manager.schemas
        assert 'data_table' in schema_manager.schemas
        assert 'asset' in schema_manager.schemas
    
    def test_get_schema(self, schema_manager):
        """Test getting a schema by type."""
        schema_manager.load_schemas()
        
        config_schema = schema_manager.get_schema('config')
        assert config_schema is not None
        assert 'properties' in config_schema
        assert 'version' in config_schema['properties']
    
    def test_get_nonexistent_schema(self, schema_manager):
        """Test getting a schema that doesn't exist."""
        schema_manager.load_schemas()
        
        schema = schema_manager.get_schema('nonexistent')
        assert schema is None
    
    def test_list_schema_types(self, schema_manager):
        """Test listing all schema types."""
        schema_manager.load_schemas()
        
        types = schema_manager.list_schema_types()
        assert isinstance(types, list)
        assert 'config' in types
        assert 'data_table' in types
        assert 'asset' in types
    
    def test_auto_detect_config_schema(self, schema_manager):
        """Test auto-detecting config schema type."""
        schema_manager.load_schemas()
        
        yaml_content = """
version: "1.0.0"
settings:
  key: value
"""
        
        detected_type = schema_manager.auto_detect_schema_type(yaml_content)
        assert detected_type == 'config'
    
    def test_auto_detect_data_table_schema(self, schema_manager):
        """Test auto-detecting data table schema type."""
        schema_manager.load_schemas()
        
        yaml_content = """
table: MyDataTable
rows:
  - id: 1
    name: Item1
"""
        
        detected_type = schema_manager.auto_detect_schema_type(yaml_content)
        assert detected_type == 'data_table'
    
    def test_auto_detect_asset_schema(self, schema_manager):
        """Test auto-detecting asset schema type."""
        schema_manager.load_schemas()
        
        yaml_content = """
name: MyAsset
type: Blueprint
properties:
  key: value
"""
        
        detected_type = schema_manager.auto_detect_schema_type(yaml_content)
        assert detected_type == 'asset'
    
    def test_auto_detect_invalid_yaml(self, schema_manager):
        """Test auto-detecting with invalid YAML."""
        schema_manager.load_schemas()
        
        yaml_content = "invalid: yaml: content:"
        
        detected_type = schema_manager.auto_detect_schema_type(yaml_content)
        assert detected_type is None
    
    def test_auto_detect_unknown_structure(self, schema_manager):
        """Test auto-detecting with unknown structure."""
        schema_manager.load_schemas()
        
        yaml_content = """
unknown_field: value
another_field: value
"""
        
        detected_type = schema_manager.auto_detect_schema_type(yaml_content)
        assert detected_type is None
    
    def test_load_custom_schema(self, temp_schema_dir):
        """Test loading a custom schema file."""
        # Create a custom schema
        custom_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Custom Schema",
            "type": "object",
            "required": ["custom_field"],
            "properties": {
                "custom_field": {"type": "string"}
            }
        }
        
        schema_file = Path(temp_schema_dir) / "custom_schema.json"
        with open(schema_file, 'w') as f:
            json.dump(custom_schema, f)
        
        # Load schemas
        manager = SchemaManager(schema_dir=temp_schema_dir)
        manager.load_schemas()
        
        # Check custom schema was loaded
        assert 'custom' in manager.schemas
        assert manager.schemas['custom']['title'] == 'Custom Schema'
    
    def test_invalid_schema_file(self, temp_schema_dir):
        """Test handling of invalid schema file."""
        # Create an invalid JSON file
        schema_file = Path(temp_schema_dir) / "invalid_schema.json"
        with open(schema_file, 'w') as f:
            f.write("invalid json content")
        
        # Attempt to load schemas
        manager = SchemaManager(schema_dir=temp_schema_dir)
        
        with pytest.raises(ValueError, match="Invalid JSON in schema file"):
            manager.load_schemas()
