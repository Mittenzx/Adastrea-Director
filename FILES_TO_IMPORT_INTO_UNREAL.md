# Files to Import Into Unreal Engine

**Last Updated:** 2025-11-22  
**Purpose:** Complete inventory of files in the repository that need to be imported into Unreal Engine  
**Repository:** Mittenzx/Adastrea-Director

---

## Overview

This document provides a comprehensive list of all files currently in the Adastrea Director repository that are designed to be imported into Unreal Engine, organized by category and purpose.

---

## Summary

Currently, the repository contains **4 files** that need to be imported into Unreal Engine:

1. **1 YAML Configuration File** - Remote Control API settings
2. **3 JSON Schema Files** - Template validation schemas

---

## 1. Configuration Files

### Remote Control API Configuration

**File:** `config/remote_control_config.yaml`  
**Type:** YAML Configuration  
**Purpose:** Configuration for Remote Control API integration with Unreal Engine  
**Size:** ~240 lines  
**Import Priority:** HIGH

**Description:**
This file configures how Adastrea Director connects to and interacts with Unreal Engine via the Remote Control API. It includes settings for WebSocket connections, version control integration, agent configuration, security, monitoring, and logging.

**Key Sections:**
- Remote Control API connection settings (host, port, timeout, retry)
- WebSocket connection settings for real-time updates
- Version control integration (Git, branches, commits, PRs)
- Agent configuration (performance profiling, bug detection, code quality)
- Security settings (access control, whitelisting, rate limiting)
- Monitoring and alerting settings
- Logging configuration
- Unreal Engine project settings

**Usage in Unreal:**
- Configure this file to match your Unreal Engine project settings
- Update the `unreal_engine.projects` section with your project paths
- Adjust Remote Control API port to match your UE Remote Control preset
- Import this file into your project's configuration directory
- Reference it from the Adastrea Director plugin settings

**Import Location:** `YourUnrealProject/Config/AdastreaDirector/`

**Dependencies:**
- Requires Unreal Engine Remote Control Plugin enabled
- Requires Unreal Engine Python Plugin enabled (for agent integration)

---

## 2. Schema Files (JSON)

These schema files are used for validating YAML templates before they are imported into Unreal Engine. While they are primarily used by the Python validation system, they can also be imported into Unreal for reference or editor tools.

### 2.1 Configuration Schema

**File:** `schemas/config_schema.json`  
**Type:** JSON Schema (Draft-07)  
**Purpose:** Validates configuration template YAML files  
**Size:** 16 lines  
**Import Priority:** MEDIUM

**Schema Definition:**
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

**Usage in Unreal:**
- Can be used by editor tools to validate config files
- Useful for custom editor validators or import tools
- Reference for creating configuration assets

**Import Location:** `YourUnrealProject/Content/AdastreaDirector/Schemas/`

---

### 2.2 Data Table Schema

**File:** `schemas/data_table_schema.json`  
**Type:** JSON Schema (Draft-07)  
**Purpose:** Validates data table template YAML files  
**Size:** 14 lines  
**Import Priority:** HIGH

**Schema Definition:**
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

**Usage in Unreal:**
- Validates YAML data before converting to Unreal Data Tables
- Can be integrated into custom import pipeline
- Reference for data table import tools

**Import Location:** `YourUnrealProject/Content/AdastreaDirector/Schemas/`

**Related Unreal Assets:**
- Use to create Data Table assets from validated YAML
- Convert YAML to CSV format, then import as Data Table
- Requires matching Blueprint struct for row structure

---

### 2.3 Asset Schema

**File:** `schemas/asset_schema.json`  
**Type:** JSON Schema (Draft-07)  
**Purpose:** Validates asset definition template YAML files  
**Size:** 22 lines  
**Import Priority:** MEDIUM

**Schema Definition:**
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

**Usage in Unreal:**
- Validates asset definition templates
- Can be used for asset import pipeline automation
- Reference for custom asset creation tools

**Import Location:** `YourUnrealProject/Content/AdastreaDirector/Schemas/`

**Supported Asset Types:**
- Blueprint
- Material
- Texture
- StaticMesh
- SkeletalMesh

---

## 3. Additional Files (Not for Direct Import)

The following files are part of the Adastrea Director system but are **NOT** directly imported into Unreal Engine. They are used by the Python backend or CI/CD workflows:

### GitHub Workflow Files

**Files:**
- `.github/workflows/populate-database.yml` - CI workflow for database population
- `.github/workflows/test-game-repo-integration.yml` - CI workflow for testing

**Purpose:** Automated testing and database population workflows  
**Import:** NOT REQUIRED - Used by GitHub Actions only

---

## Import Instructions

### Step 1: Import Configuration File

```bash
# Copy the config file to your Unreal project
cp config/remote_control_config.yaml /path/to/YourUnrealProject/Config/AdastreaDirector/
```

**Post-Import Configuration:**
1. Open `remote_control_config.yaml` in a text editor
2. Update the `unreal_engine.projects` section:
   ```yaml
   unreal_engine:
     projects:
       - name: "YourProjectName"
         path: "/path/to/YourUnrealProject"
         remote_control_port: 30010
   ```
3. Adjust security settings in the `security` section
4. Configure agent settings in the `agents` section

---

### Step 2: Import Schema Files (Optional)

```bash
# Create schemas directory in your Unreal project
mkdir -p /path/to/YourUnrealProject/Content/AdastreaDirector/Schemas/

# Copy schema files
cp schemas/*.json /path/to/YourUnrealProject/Content/AdastreaDirector/Schemas/
```

**Note:** These schemas are primarily used by the Python validation system. Importing them into Unreal is optional unless you're building custom editor tools that need to validate YAML templates.

---

### Step 3: Verify Import

After importing the files, verify:

1. **Configuration File:**
   - File exists at: `YourUnrealProject/Config/AdastreaDirector/remote_control_config.yaml`
   - File is readable and properly formatted
   - Settings match your project structure

2. **Schema Files (if imported):**
   - Files exist at: `YourUnrealProject/Content/AdastreaDirector/Schemas/`
   - JSON files are valid and properly formatted

---

## Integration with Unreal Plugin

The Adastrea Director Unreal Engine plugin (`Plugins/AdastreaDirector/`) integrates with these files:

### Plugin Files That Reference Imported Files

1. **`Plugins/AdastreaDirector/Python/rag_query.py`**
   - Uses Python backend to access configuration
   - Reads `remote_control_config.yaml` for connection settings

2. **`Plugins/AdastreaDirector/Source/`** (C++ plugin code)
   - May read configuration file for plugin settings
   - Integration with Remote Control API

---

## Template Generation (Future Files)

The repository contains code to **generate** YAML templates dynamically, but no pre-made templates are currently stored in the repository. Templates are generated on-demand by:

- **Code Generation Agent:** `agents/code_generation_agent.py`
- **Validation System:** `validation/yaml_validator.py`

**To create templates for import:**

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

# Save the generated template
with open("items_table.yaml", "w") as f:
    f.write(result["yaml_content"])
```

---

## File Import Checklist

Use this checklist when importing files into Unreal Engine:

- [ ] **Import `config/remote_control_config.yaml`**
  - [ ] Copy to project Config directory
  - [ ] Update project-specific settings
  - [ ] Verify YAML syntax is valid
  - [ ] Test Remote Control API connection

- [ ] **Import Schema Files (Optional)**
  - [ ] Copy `schemas/*.json` to Content directory
  - [ ] Verify JSON syntax is valid
  - [ ] Create editor tools if needed

- [ ] **Verify Plugin Integration**
  - [ ] Adastrea Director plugin is installed
  - [ ] Python backend is initialized
  - [ ] Remote Control API is enabled
  - [ ] Python Editor Script Plugin is enabled

- [ ] **Test Integration**
  - [ ] Open Unreal Editor
  - [ ] Start Adastrea Director panel
  - [ ] Verify connection to Python backend
  - [ ] Test Remote Control API communication

---

## Maintenance

### Updating Files

When updating files in the repository:

1. **Configuration File Updates:**
   - Pull latest from repository
   - Merge with your local customizations
   - Test in development environment first
   - Deploy to production

2. **Schema File Updates:**
   - Update schemas in repository
   - Regenerate templates if schemas change
   - Update validation rules in Python code

### Version Tracking

Track which versions of files you've imported:

```yaml
# Add to your project's documentation
imported_files:
  config/remote_control_config.yaml:
    version: "commit-hash"
    imported_date: "2025-11-22"
  schemas/config_schema.json:
    version: "commit-hash"
    imported_date: "2025-11-22"
```

---

## Troubleshooting

### Configuration File Not Found

**Problem:** Unreal can't find `remote_control_config.yaml`

**Solutions:**
1. Verify file path matches what plugin expects
2. Check file permissions (must be readable)
3. Ensure YAML syntax is valid
4. Check plugin is properly installed

### Schema Validation Fails

**Problem:** YAML templates fail validation

**Solutions:**
1. Update schema files to latest version
2. Verify JSON schema syntax
3. Check template structure matches schema requirements
4. Use auto-fix feature in Python validator

### Plugin Integration Issues

**Problem:** Plugin can't read configuration file

**Solutions:**
1. Verify Python backend is running
2. Check file paths in plugin settings
3. Ensure Remote Control API is enabled
4. Check plugin logs for errors

---

## Related Documentation

- **Template Types:** [YAML_TEMPLATES_FOR_UNREAL.md](YAML_TEMPLATES_FOR_UNREAL.md)
- **Quick Reference:** [YAML_TEMPLATES_QUICK_REFERENCE.md](YAML_TEMPLATES_QUICK_REFERENCE.md)
- **Plugin Installation:** [Plugins/AdastreaDirector/INSTALLATION.md](Plugins/AdastreaDirector/INSTALLATION.md)
- **Remote Control API:** [docs/remote-control/REMOTE_CONTROL_API.md](docs/remote-control/REMOTE_CONTROL_API.md)
- **Integration Guide:** [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

---

## Summary Table

| File | Type | Size | Priority | Purpose | Import Location |
|------|------|------|----------|---------|-----------------|
| `config/remote_control_config.yaml` | YAML | ~240 lines | HIGH | Remote Control API config | `Config/AdastreaDirector/` |
| `schemas/config_schema.json` | JSON | 16 lines | MEDIUM | Config validation schema | `Content/AdastreaDirector/Schemas/` |
| `schemas/data_table_schema.json` | JSON | 14 lines | HIGH | Data table validation schema | `Content/AdastreaDirector/Schemas/` |
| `schemas/asset_schema.json` | JSON | 22 lines | MEDIUM | Asset validation schema | `Content/AdastreaDirector/Schemas/` |

**Total Files to Import:** 4

---

**Last Updated:** 2025-11-22  
**Maintained By:** Adastrea Director Team  
**Version:** 1.0.0
