"""
Schema Manager for YAML Template Validation.

This module manages JSON schemas for validating YAML templates generated
by the Code Generation Agent.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class SchemaManager:
    """
    Manages JSON schemas for YAML validation.
    
    Loads and provides access to schemas stored in the schemas/ directory.
    Supports auto-detection of schema types based on YAML content.
    """
    
    def __init__(self, schema_dir: str = "schemas"):
        """
        Initialize the Schema Manager.
        
        Args:
            schema_dir: Directory containing JSON schema files
        """
        self.schema_dir = Path(schema_dir)
        self.schemas: Dict[str, dict] = {}
        self._loaded = False
        logger.info(f"SchemaManager initialized with directory: {self.schema_dir}")
    
    def load_schemas(self) -> None:
        """
        Load all JSON schemas from the schema directory.
        
        Scans the schema directory for .json files and loads them into memory.
        Each schema file should be named with the pattern: {schema_type}_schema.json
        
        Raises:
            FileNotFoundError: If schema directory doesn't exist
            ValueError: If schema files are invalid JSON
        """
        if not self.schema_dir.exists():
            logger.warning(f"Schema directory not found: {self.schema_dir}")
            logger.info("Creating schema directory...")
            self.schema_dir.mkdir(parents=True, exist_ok=True)
            self._create_default_schemas()
        
        schema_files = list(self.schema_dir.glob("*.json"))
        
        if not schema_files:
            logger.warning("No schema files found, creating defaults...")
            self._create_default_schemas()
            schema_files = list(self.schema_dir.glob("*.json"))
        
        for schema_file in schema_files:
            try:
                with open(schema_file, 'r') as f:
                    schema = json.load(f)
                
                # Extract schema type from filename (e.g., "config_schema.json" -> "config")
                schema_type = schema_file.stem.replace('_schema', '')
                self.schemas[schema_type] = schema
                logger.info(f"Loaded schema: {schema_type}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to load schema {schema_file}: {e}")
                raise ValueError(f"Invalid JSON in schema file: {schema_file}")
        
        self._loaded = True
        logger.info(f"Loaded {len(self.schemas)} schemas")
    
    def get_schema(self, schema_type: str) -> Optional[dict]:
        """
        Get a schema by type.
        
        Args:
            schema_type: Type of schema (e.g., 'config', 'data_table')
            
        Returns:
            Schema dictionary or None if not found
        """
        if not self._loaded:
            self.load_schemas()
        
        schema = self.schemas.get(schema_type)
        if schema is None:
            logger.warning(f"Schema not found: {schema_type}")
        return schema
    
    def list_schema_types(self) -> List[str]:
        """
        List all available schema types.
        
        Returns:
            List of schema type names
        """
        if not self._loaded:
            self.load_schemas()
        
        return list(self.schemas.keys())
    
    def auto_detect_schema_type(self, yaml_content: str) -> Optional[str]:
        """
        Auto-detect the schema type based on YAML content.
        
        Uses heuristics to identify the schema type:
        - Looks for key indicators in the YAML structure
        - Checks for specific required fields
        
        Args:
            yaml_content: YAML content as a string
            
        Returns:
            Detected schema type or None if cannot determine
        """
        import yaml
        
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError:
            return None
        
        if not isinstance(data, dict):
            return None
        
        # Check for common patterns
        if 'version' in data and 'settings' in data:
            return 'config'
        elif 'rows' in data or 'table' in data:
            return 'data_table'
        elif 'name' in data and 'type' in data and 'properties' in data:
            return 'asset'
        
        return None
    
    def _create_default_schemas(self) -> None:
        """Create default schema files."""
        # Config schema
        config_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Configuration Schema",
            "type": "object",
            "required": ["version", "settings"],
            "properties": {
                "version": {
                    "type": "string",
                    "pattern": "^\\d+\\.\\d+\\.\\d+$"
                },
                "settings": {
                    "type": "object"
                }
            }
        }
        
        # Data table schema
        data_table_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Data Table Schema",
            "type": "object",
            "required": ["table"],
            "properties": {
                "table": {
                    "type": "string"
                },
                "rows": {
                    "type": "array",
                    "items": {
                        "type": "object"
                    }
                }
            }
        }
        
        # Asset schema
        asset_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Asset Schema",
            "type": "object",
            "required": ["name", "type"],
            "properties": {
                "name": {
                    "type": "string",
                    "minLength": 1
                },
                "type": {
                    "type": "string",
                    "enum": ["Blueprint", "Material", "Texture", "StaticMesh", "SkeletalMesh"]
                },
                "properties": {
                    "type": "object"
                }
            }
        }
        
        # Write schemas to files
        schemas_to_create = {
            'config': config_schema,
            'data_table': data_table_schema,
            'asset': asset_schema
        }
        
        for schema_type, schema_data in schemas_to_create.items():
            schema_file = self.schema_dir / f"{schema_type}_schema.json"
            with open(schema_file, 'w') as f:
                json.dump(schema_data, f, indent=2)
            logger.info(f"Created default schema: {schema_type}")
