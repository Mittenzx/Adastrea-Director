# YAML Templates for Unreal Engine Import

**Last Updated:** 2025-11-22  
**Purpose:** Comprehensive list of YAML templates that need to be imported into Unreal Engine  
**Status:** Documentation

---

## Overview

This document provides a complete inventory of YAML template types supported by Adastrea Director that are designed for import into Unreal Engine. These templates are validated using JSON schemas before import to ensure data integrity.

The YAML validation system is located in the `validation/` directory and supports automatic validation and auto-fixing of common errors.

---

## Template Categories

Adastrea Director supports three primary YAML template categories for Unreal Engine integration:

### 1. Configuration Templates (`config`)
### 2. Data Table Templates (`data_table`)
### 3. Asset Definition Templates (`asset`)

---

## 1. Configuration Templates

**Schema File:** `schemas/config_schema.json`  
**Purpose:** Configuration files for game systems, settings, and parameters  
**Validation:** Auto-detects when YAML contains `version` and `settings` fields

### Schema Requirements

```json
{
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
```

### Valid Template Example

```yaml
# Game Configuration Template
version: "1.0.0"
settings:
  database:
    host: localhost
    port: 5432
  gameplay:
    difficulty: normal
    max_players: 4
  graphics:
    quality: high
    resolution: [1920, 1080]
```

### Use Cases in Unreal Engine

- Game mode configuration files
- Player settings and preferences
- System-wide parameters
- Feature flags and toggles
- Environment-specific settings (dev, staging, production)

---

## 2. Data Table Templates

**Schema File:** `schemas/data_table_schema.json`  
**Purpose:** Structured data for Unreal Engine Data Tables (CSV alternative)  
**Validation:** Auto-detects when YAML contains `rows` or `table` fields

### Schema Requirements

```json
{
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
```

### Valid Template Examples

#### Example 1: Items Data Table

```yaml
# Items Data Table
table: ItemsTable
rows:
  - id: 1
    name: Sword
    damage: 10
    durability: 100
    rarity: common
    price: 50
  - id: 2
    name: Shield
    defense: 15
    durability: 150
    rarity: uncommon
    price: 75
  - id: 3
    name: Potion
    healing: 50
    stack_size: 10
    rarity: common
    price: 25
```

#### Example 2: Character Stats Data Table

```yaml
# Character Stats Data Table
table: CharacterStatsTable
rows:
  - character_class: Warrior
    base_health: 150
    base_stamina: 100
    base_strength: 15
    base_agility: 8
    base_intelligence: 5
  - character_class: Mage
    base_health: 80
    base_stamina: 120
    base_strength: 5
    base_agility: 7
    base_intelligence: 18
  - character_class: Rogue
    base_health: 100
    base_stamina: 110
    base_strength: 10
    base_agility: 16
    base_intelligence: 8
```

#### Example 3: Enemy Data Table

```yaml
# Enemy Data Table
table: EnemyDataTable
rows:
  - enemy_id: goblin_01
    display_name: Goblin Scout
    level: 1
    health: 50
    damage: 5
    experience_reward: 10
    loot_table: common_loot
  - enemy_id: orc_warrior
    display_name: Orc Warrior
    level: 5
    health: 200
    damage: 15
    experience_reward: 50
    loot_table: warrior_loot
```

### Use Cases in Unreal Engine

- **Game Balance Data**: Items, weapons, armor stats
- **Character Data**: Classes, stats, progression tables
- **Enemy Data**: Monster stats, behaviors, loot tables
- **Quest Data**: Quest definitions, objectives, rewards
- **Dialogue Data**: Conversation trees and responses
- **Localization Data**: Multi-language text strings
- **Economy Data**: Pricing, vendor inventories, currency exchange rates
- **Level Data**: Wave spawning, checkpoint data, difficulty scaling

### Import Process for Data Tables

1. Create the YAML file following the schema
2. Validate using `validation/yaml_validator.py`
3. Convert YAML to CSV format (Unreal's native Data Table format)
4. Import CSV into Unreal Engine as Data Table asset
5. Create Blueprint struct matching the row structure
6. Reference the Data Table in Blueprints or C++

---

## 3. Asset Definition Templates

**Schema File:** `schemas/asset_schema.json`  
**Purpose:** Metadata and property definitions for Unreal Engine assets  
**Validation:** Auto-detects when YAML contains `name`, `type`, and `properties` fields

### Schema Requirements

```json
{
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
```

### Supported Asset Types

1. **Blueprint** - Blueprint class definitions
2. **Material** - Material property definitions
3. **Texture** - Texture import settings and metadata
4. **StaticMesh** - Static mesh import settings
5. **SkeletalMesh** - Skeletal mesh and animation settings

### Valid Template Examples

#### Example 1: Blueprint Asset

```yaml
# Player Character Blueprint
name: BP_PlayerCharacter
type: Blueprint
properties:
  health: 100
  speed: 5.0
  jump_height: 2.0
  inventory_size: 20
  starting_weapon: Sword
  can_sprint: true
  sprint_multiplier: 1.5
```

#### Example 2: Material Asset

```yaml
# Master Material Definition
name: M_Master_Character
type: Material
properties:
  base_color: [1.0, 1.0, 1.0]
  metallic: 0.0
  roughness: 0.8
  specular: 0.5
  emissive_strength: 0.0
  two_sided: false
  blend_mode: opaque
```

#### Example 3: Texture Asset

```yaml
# Texture Import Settings
name: T_Character_Diffuse
type: Texture
properties:
  compression: BC7
  srgb: true
  max_texture_size: 2048
  mip_gen_settings: FromTextureGroup
  lod_group: Character
  filter: Default
  address_x: Wrap
  address_y: Wrap
```

#### Example 4: Static Mesh Asset

```yaml
# Static Mesh Import Settings
name: SM_Building_Wall
type: StaticMesh
properties:
  import_materials: true
  import_textures: true
  auto_generate_collision: true
  collision_complexity: Complex
  generate_lightmap_uvs: true
  min_lightmap_resolution: 64
  lightmap_coordinate_index: 1
  build_scale: [1.0, 1.0, 1.0]
```

#### Example 5: Skeletal Mesh Asset

```yaml
# Skeletal Mesh Import Settings
name: SK_Character_Hero
type: SkeletalMesh
properties:
  import_mesh: true
  import_skeleton: true
  import_morph_targets: true
  import_animations: true
  skeleton_asset: SK_Hero_Skeleton
  physics_asset: PHYS_Hero
  create_physics_asset: true
  preserve_smoothing_groups: true
```

### Use Cases in Unreal Engine

- **Blueprint Configuration**: Pre-configure Blueprint properties before creation
- **Material Presets**: Define material property templates for consistency
- **Import Settings**: Standardize asset import settings across the project
- **Asset Metadata**: Store additional metadata not supported by native asset types
- **Batch Operations**: Configure multiple assets with consistent settings
- **Pipeline Automation**: Automate asset creation and configuration

---

## Validation System

### Automatic Validation

The YAML validation system (`validation/yaml_validator.py`) provides:

1. **Schema Validation**: Validates YAML against JSON schemas
2. **Auto-Detection**: Automatically detects template type from content
3. **Auto-Fix**: Fixes common errors like missing required fields
4. **Error Reporting**: Provides detailed error messages with line numbers
5. **Fix Suggestions**: Suggests corrections for validation errors

### Validation Workflow

```python
from validation.schema_manager import SchemaManager
from validation.yaml_validator import YAMLValidator

# Initialize validator
schema_manager = SchemaManager()
schema_manager.load_schemas()
validator = YAMLValidator(schema_manager)

# Validate YAML
result = validator.validate(yaml_content, schema_type='data_table')

if not result.is_valid:
    # Get fix suggestions
    fixes = validator.suggest_fixes(result)
    
    # Auto-fix if possible
    fixed_yaml = validator.auto_fix(yaml_content, result)
    
    # Re-validate
    result2 = validator.validate(fixed_yaml, schema_type='data_table')
```

### Common Validation Errors

1. **Missing Required Fields**: Auto-fixed by adding fields with default values
2. **Type Mismatches**: Must be manually corrected
3. **Enum Violations**: Asset type must be one of the allowed values
4. **Format Violations**: Version strings must follow semantic versioning (X.Y.Z)
5. **YAML Syntax Errors**: Invalid YAML syntax, indentation issues

---

## Code Generation Integration

The Code Generation Agent (`agents/code_generation_agent.py`) can generate validated YAML templates:

```python
from agents.code_generation_agent import CodeGenerationAgent

agent = CodeGenerationAgent(enable_yaml_validation=True)

# Generate a data table template
result = agent.generate_yaml_template(
    yaml_type="data_table",
    description="Items table with id, name, damage, and rarity",
    schema_type="data_table",
    auto_fix=True
)

if result["is_valid"]:
    print(result["yaml_content"])
else:
    print("Validation errors:", result["validation_result"].errors)
```

---

## Import Guidelines

### General Import Process

1. **Create Template**: Write YAML following the appropriate schema
2. **Validate**: Run through validation system to ensure correctness
3. **Auto-Fix**: Apply automatic fixes for common errors
4. **Convert**: Convert YAML to Unreal-compatible format if needed
5. **Import**: Import into Unreal Engine project
6. **Verify**: Test imported data in Unreal Engine

### Best Practices

1. **Use Validation**: Always validate templates before import
2. **Version Control**: Track template changes in version control
3. **Comments**: Add comments to explain complex configurations
4. **Consistency**: Use consistent naming conventions across templates
5. **Documentation**: Document custom properties and their usage
6. **Testing**: Test templates in development environment first
7. **Backup**: Keep backups of working templates

### Performance Considerations

- **Large Data Tables**: Split very large data tables into multiple files
- **Complex Assets**: Keep asset definitions simple and focused
- **Nested Data**: Avoid excessive nesting in configuration files
- **File Size**: Keep individual YAML files under 1MB for best performance

---

## Related Files and Modules

### Core Validation System

- `validation/yaml_validator.py` - YAML validation engine
- `validation/schema_manager.py` - Schema loading and management
- `validation/__init__.py` - Validation module exports

### Schema Definitions

- `schemas/config_schema.json` - Configuration template schema
- `schemas/data_table_schema.json` - Data table template schema
- `schemas/asset_schema.json` - Asset definition template schema

### Integration Points

- `agents/code_generation_agent.py` - Auto-generates validated YAML
- `config/remote_control_config.yaml` - Remote Control API configuration
- `tests/validation/` - Validation system tests

### Testing

- `tests/validation/test_yaml_validator.py` - Validator unit tests
- `tests/validation/test_schema_manager.py` - Schema manager tests
- `tests/validation/test_yaml_integration.py` - Integration tests

---

## Future Enhancements

### Planned Template Types

1. **Animation Templates**: Animation blueprint and montage definitions
2. **Sound Templates**: Audio asset configuration and mixing
3. **VFX Templates**: Visual effects and particle system definitions
4. **AI Templates**: Behavior tree and blackboard configurations
5. **UI Templates**: Widget blueprint and UMG definitions
6. **Level Templates**: Level streaming and world composition settings

### Planned Features

1. **YAML to CSV Converter**: Direct conversion for Data Table import
2. **Bulk Validation**: Validate multiple templates at once
3. **Template Library**: Pre-built templates for common use cases
4. **IDE Integration**: VS Code extension for template editing
5. **Visual Editor**: GUI for template creation and editing
6. **Import Automation**: Automated import pipeline for CI/CD

---

## Support and Documentation

For more information, see:

- **YAML Validation Guide**: `validation/README.md` (if exists)
- **Integration Guide**: `INTEGRATION_GUIDE.md`
- **Improvements Roadmap**: `IMPROVEMENTS.md` (Section 2: YAML Template Validation)
- **Phase 3 Guide**: `PHASE3_GUIDE.md`
- **Code Generation Agent**: `agents/code_generation_agent.py`

---

## Summary

Adastrea Director currently supports **three validated YAML template types** for Unreal Engine import:

1. **Configuration Templates** - Game settings and system configuration
2. **Data Table Templates** - Structured data for game content (items, characters, enemies, etc.)
3. **Asset Definition Templates** - Asset metadata and import settings (Blueprints, Materials, Meshes, Textures)

All templates are validated against JSON schemas with auto-fix capabilities to ensure 100% valid output before import into Unreal Engine.

---

**Last Updated:** 2025-11-22  
**Maintained By:** Adastrea Director Team  
**Version:** 1.0.0
