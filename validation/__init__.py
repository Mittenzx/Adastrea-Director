"""
Validation module for YAML template validation.

This module provides schema management and YAML validation capabilities
to ensure generated templates are valid and conform to defined schemas.
"""

from validation.schema_manager import SchemaManager
from validation.yaml_validator import YAMLValidator, ValidationResult, Fix

__all__ = ['SchemaManager', 'YAMLValidator', 'ValidationResult', 'Fix']
