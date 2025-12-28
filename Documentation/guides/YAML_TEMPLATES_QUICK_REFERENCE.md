# YAML Templates Quick Reference

Quick reference guide for YAML templates that need to be imported into Unreal Engine.

---

## Template Types Summary

| Template Type | Schema File | Required Fields | Common Use Cases |
|---------------|-------------|-----------------|------------------|
| **Configuration** | `config_schema.json` | `version`, `settings` | Game settings, system config, feature flags |
| **Data Table** | `data_table_schema.json` | `table` | Items, characters, enemies, quests, dialogue |
| **Asset** | `asset_schema.json` | `name`, `type` | Blueprint props, material presets, import settings |

---

## 1. Configuration Template

**Quick Example:**
```yaml
version: "1.0.0"
settings:
  gameplay:
    difficulty: normal
    max_players: 4
```

**Use for:** Game configs, settings, parameters

---

## 2. Data Table Template

**Quick Example:**
```yaml
table: ItemsTable
rows:
  - id: 1
    name: Sword
    damage: 10
  - id: 2
    name: Shield
    defense: 15
```

**Use for:** Game data (items, stats, enemies, quests)

---

## 3. Asset Template

**Quick Example:**
```yaml
name: BP_PlayerCharacter
type: Blueprint
properties:
  health: 100
  speed: 5.0
```

**Asset Types:** `Blueprint`, `Material`, `Texture`, `StaticMesh`, `SkeletalMesh`

**Use for:** Asset metadata and import settings

---

## Validation

```python
from validation.schema_manager import SchemaManager
from validation.yaml_validator import YAMLValidator

# Setup
schema_manager = SchemaManager()
schema_manager.load_schemas()
validator = YAMLValidator(schema_manager)

# Validate
result = validator.validate(yaml_content, schema_type='data_table')

# Auto-fix if needed
if not result.is_valid:
    fixed_yaml = validator.auto_fix(yaml_content, result)
```

---

## Common Data Table Examples

### Items Table
```yaml
table: ItemsTable
rows:
  - id: 1
    name: Sword
    damage: 10
    rarity: common
    price: 50
```

### Character Stats Table
```yaml
table: CharacterStatsTable
rows:
  - character_class: Warrior
    base_health: 150
    base_strength: 15
    base_agility: 8
```

### Enemy Data Table
```yaml
table: EnemyDataTable
rows:
  - enemy_id: goblin_01
    display_name: Goblin Scout
    health: 50
    damage: 5
```

---

## Files Reference

- **Validators:** `validation/yaml_validator.py`, `validation/schema_manager.py`
- **Schemas:** `schemas/*.json`
- **Tests:** `tests/validation/`
- **Full Documentation:** `YAML_TEMPLATES_FOR_UNREAL.md`

---

**For detailed information, see:** [YAML_TEMPLATES_FOR_UNREAL.md](YAML_TEMPLATES_FOR_UNREAL.md)
