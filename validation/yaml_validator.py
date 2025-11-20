"""
YAML Validator for Template Validation.

This module validates YAML templates against JSON schemas and provides
auto-fix capabilities for common issues.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

import yaml
from jsonschema import Draft7Validator

from validation.schema_manager import SchemaManager

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """
    Result of YAML validation.
    
    Attributes:
        is_valid: Whether the YAML is valid
        errors: List of validation errors
        warnings: List of warnings (non-critical issues)
        schema_type: Type of schema used for validation
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    schema_type: Optional[str] = None


@dataclass
class Fix:
    """
    A suggested fix for a validation error.
    
    Attributes:
        error: The error message
        fix_type: Type of fix (add_field, fix_type, fix_format)
        fix_description: Human-readable description
        auto_fixable: Whether this can be auto-fixed
        suggested_value: Suggested value for the fix
    """
    error: str
    fix_type: str
    fix_description: str
    auto_fixable: bool
    suggested_value: Optional[Any] = None


class YAMLValidator:
    """
    Validates YAML content against JSON schemas.
    
    Provides validation, error reporting, fix suggestions, and auto-fix
    capabilities for common validation issues.
    """
    
    def __init__(self, schema_manager: SchemaManager):
        """
        Initialize the YAML Validator.
        
        Args:
            schema_manager: Schema manager for loading schemas
        """
        self.schema_manager = schema_manager
        logger.info("YAMLValidator initialized")
    
    def validate(self, yaml_content: str, schema_type: Optional[str] = None) -> ValidationResult:
        """
        Validate YAML against schema.
        
        Args:
            yaml_content: YAML content as a string
            schema_type: Type of schema to validate against (auto-detected if None)
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult(is_valid=True)
        
        # Parse YAML
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            result.is_valid = False
            result.errors.append(f"YAML parsing error: {str(e)}")
            return result
        
        # Auto-detect schema type if not provided
        if schema_type is None:
            schema_type = self.schema_manager.auto_detect_schema_type(yaml_content)
            if schema_type is None:
                result.warnings.append("Could not auto-detect schema type")
                return result
        
        result.schema_type = schema_type
        
        # Load schema
        schema = self.schema_manager.get_schema(schema_type)
        if schema is None:
            result.warnings.append(f"Schema not found: {schema_type}")
            return result
        
        # Validate against schema
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(data))
        
        if errors:
            result.is_valid = False
            for error in errors:
                # Format error message
                path = '.'.join(str(p) for p in error.path) if error.path else 'root'
                error_msg = f"At {path}: {error.message}"
                result.errors.append(error_msg)
                logger.debug(f"Validation error: {error_msg}")
        else:
            logger.info(f"YAML validated successfully against schema: {schema_type}")
        
        return result
    
    def suggest_fixes(self, validation_result: ValidationResult) -> List[Fix]:
        """
        Suggest fixes for validation errors.
        
        Args:
            validation_result: Result from validation
            
        Returns:
            List of suggested fixes
        """
        fixes = []
        
        for error in validation_result.errors:
            fix = self._analyze_error_and_suggest_fix(error)
            if fix:
                fixes.append(fix)
        
        logger.info(f"Generated {len(fixes)} fix suggestions")
        return fixes
    
    def auto_fix(self, yaml_content: str, validation_result: ValidationResult) -> str:
        """
        Automatically fix common validation issues.
        
        Applies simple fixes like:
        - Adding required fields with default values
        - Fixing obvious type mismatches
        - Correcting format issues
        
        Args:
            yaml_content: Original YAML content
            validation_result: Validation result with errors
            
        Returns:
            Fixed YAML content (may still be invalid if not all fixes are auto-fixable)
        """
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError:
            return yaml_content  # Cannot fix parsing errors
        if not isinstance(data, dict):
            return yaml_content  # Nothing to fix if data is not a dict
        
        # Get schema
        if validation_result.schema_type:
            schema = self.schema_manager.get_schema(validation_result.schema_type)
            if schema and 'required' in schema:
                # Add missing required fields with default values
                for required_field in schema['required']:
                    if required_field not in data:
                        default_value = self._get_default_value_for_field(
                            schema.get('properties', {}).get(required_field, {})
                        )
                        data[required_field] = default_value
                        logger.info(f"Auto-fixed: Added required field '{required_field}'")
        
        # Convert back to YAML
        fixed_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False)
        return fixed_yaml
    
    def _analyze_error_and_suggest_fix(self, error: str) -> Optional[Fix]:
        """Analyze an error and suggest a fix."""
        # Missing required field
        if "is a required property" in error:
            match = re.search(r"'(\w+)' is a required property", error)
            if match:
                field_name = match.group(1)
                return Fix(
                    error=error,
                    fix_type="add_field",
                    fix_description=f"Add required field: {field_name}",
                    auto_fixable=True,
                    suggested_value=None
                )
        
        # Type mismatch
        if "is not of type" in error:
            match = re.search(r"is not of type '(\w+)'", error)
            if match:
                expected_type = match.group(1)
                return Fix(
                    error=error,
                    fix_type="fix_type",
                    fix_description=f"Value should be of type: {expected_type}",
                    auto_fixable=False
                )
        
        # Pattern mismatch
        if "does not match" in error:
            return Fix(
                error=error,
                fix_type="fix_format",
                fix_description="Fix value format to match pattern",
                auto_fixable=False
            )
        
        # Enum violation
        if "is not one of" in error:
            match = re.search(r"is not one of \[(.*?)\]", error)
            if match:
                valid_values = match.group(1)
                return Fix(
                    error=error,
                    fix_type="fix_enum",
                    fix_description=f"Value must be one of: {valid_values}",
                    auto_fixable=False
                )
        
        return None
    
    def _get_default_value_for_field(self, field_schema: Dict[str, Any]) -> Any:
        """Get default value for a field based on its schema."""
        # Check if there's a default value in the schema
        if 'default' in field_schema:
            return field_schema['default']
        
        field_type = field_schema.get('type', 'string')
        
        if field_type == 'string':
            # Check for pattern requirements (e.g., semantic version)
            if 'pattern' in field_schema:
                pattern = field_schema['pattern']
                # Use regex to detect semantic version pattern
                # Pattern from JSON will have single backslashes: \d+\.\d+\.\d+
                if r'\d+' in pattern and r'\.' in pattern:
                    return '0.0.0'  # Default semantic version
            return ''
        elif field_type == 'number' or field_type == 'integer':
            return 0
        elif field_type == 'boolean':
            return False
        elif field_type == 'array':
            return []
        elif field_type == 'object':
            return {}
        
        return None
