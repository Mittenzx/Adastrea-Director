# Adastrea Project Setup

## Overview

This repository serves a dual purpose:

1. **Plugin Distribution** - The `Plugins/AdastreaDirector/` folder contains a production-ready Unreal Engine plugin
2. **Development Project** - The repository root is a minimal UE5.6 project for plugin development and testing

## Project Structure

```
Adastrea-Director/
├── Adastrea.uproject          # Main project file
├── Source/                     # Minimal game module source
│   ├── Adastrea/              # Runtime module
│   │   ├── Adastrea.Build.cs
│   │   ├── Adastrea.cpp
│   │   └── Adastrea.h
│   ├── Adastrea.Target.cs     # Game target
│   └── AdastreaEditor.Target.cs # Editor target
├── Config/                     # Project configuration
│   ├── DefaultEngine.ini
│   ├── DefaultEditor.ini
│   ├── DefaultGame.ini
│   └── DefaultInput.ini
├── Content/                    # Content directory (empty by default)
├── Plugins/
│   └── AdastreaDirector/      # The main plugin
└── [Python files and documentation...]
```

## Why This Structure?

### Problem Solved

Previously, attempting to generate project files with UnrealBuildTool would fail:

```bash
dotnet UnrealBuildTool.dll -projectfiles -project="Adastrea.uproject"
# Error: Unable to find project file based on argument Adastrea.uproject
```

### Solution

By adding a minimal `.uproject` file and supporting files, developers can now:

1. **Generate project files directly** from the repository root
2. **Test plugin changes** without manually creating a separate UE project
3. **Run CI/CD builds** and automated tests
4. **Debug plugin code** in Visual Studio/Xcode/Rider

## For Plugin Users

If you want to use the AdastreaDirector plugin in your own project:

1. Copy `Plugins/AdastreaDirector/` to your project's `Plugins/` folder
2. Regenerate your project files
3. Build your project

See [Installation Guide](Plugins/AdastreaDirector/Documentation/guides/INSTALLATION.md) for detailed instructions.

## For Plugin Developers

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mittenzx/Adastrea-Director.git
   cd Adastrea-Director
   ```

2. **Generate project files**
   
   **Windows:**
   - Right-click `Adastrea.uproject`
   - Select "Generate Visual Studio project files"
   
   **Mac:**
   - Right-click `Adastrea.uproject`
   - Select "Generate Xcode project files"
   
   **Linux:**
   ```bash
   /Path/To/UnrealEngine/Engine/Build/BatchFiles/Linux/GenerateProjectFiles.sh \
     -project="/path/to/Adastrea-Director/Adastrea.uproject"
   ```

3. **Open in your IDE**
   - Windows: Open `Adastrea.sln` in Visual Studio
   - Mac: Open `Adastrea.xcworkspace` in Xcode
   - Linux: Use your preferred IDE (Rider, CLion, etc.)

4. **Build the project**
   - Set configuration to "Development Editor"
   - Build the project
   - The plugin will be compiled as part of the build

### Working with the Plugin

The main plugin code is located in:
- `Plugins/AdastreaDirector/Source/AdastreaDirector/` - Core plugin module
- `Plugins/AdastreaDirector/Source/AdastreaDirectorEditor/` - Editor UI module

When you make changes to plugin code:
1. Build the project
2. Launch the Unreal Editor
3. The plugin will be loaded automatically
4. Test your changes in the editor

### Python Components

The repository also includes Python components for standalone use:
- `main.py` - Standalone Python GUI/CLI
- `agents/` - Autonomous agents (performance, bug detection, code quality)
- `ingest.py` - Document ingestion system
- `planner.py` - Task planning system

These can be used independently of Unreal Engine.

## Configuration Files

### Adastrea.uproject

Configured for UE 5.6 with the following plugins enabled:
- **AdastreaDirector** - The main plugin
- **PythonScriptPlugin** - For Python scripting support
- **EditorScriptingUtilities** - For editor automation

### Source Files

The `Source/Adastrea/` module is a minimal game module that:
- Provides a valid build target for UnrealBuildTool
- Allows the project to compile and run
- Does not interfere with plugin functionality
- Can be safely ignored when using the plugin in other projects

The module is intentionally minimal to reduce maintenance overhead.

## Build Artifacts

The following directories are generated during build and excluded from git:
- `Binaries/` - Compiled binaries
- `Build/` - Build intermediate files
- `DerivedDataCache/` - Derived data cache
- `Intermediate/` - Intermediate build files
- `Saved/` - Saved editor data, logs, etc.
- `*.sln`, `*.xcodeproj`, `*.xcworkspace` - IDE project files

These are excluded via `.gitignore`.

## Troubleshooting

### "Cannot find Adastrea.uproject"

Make sure you're running commands from the repository root where `Adastrea.uproject` is located.

### "Module 'Adastrea' not found"

Regenerate project files and rebuild. The Adastrea module should be automatically detected.

### Plugin doesn't load in editor

1. Check that the plugin is enabled in Edit → Plugins
2. Check the Output Log for errors
3. Rebuild the project in Development Editor configuration

### Python dependencies not found

The Python components are separate from the UE plugin. Install Python dependencies with:
```bash
pip install -r requirements.txt
```

## CI/CD Integration

For automated builds and tests, use:

```bash
# Generate project files
/Path/To/UnrealEngine/Engine/Build/BatchFiles/RunUBT.sh \
  -projectfiles -project="Adastrea.uproject"

# Build the project
/Path/To/UnrealEngine/Engine/Build/BatchFiles/RunUBT.sh \
  AdastreaEditor Win64 Development -project="Adastrea.uproject"
```

## Version Requirements

- **Unreal Engine:** 5.6 (configured), compatible with 5.0+
- **Visual Studio:** 2019 or 2022 (Windows)
- **Xcode:** 13+ (macOS)
- **Python:** 3.9+ (for standalone components)

## Questions?

- **Plugin Usage:** See [Installation Guide](Plugins/AdastreaDirector/Documentation/guides/INSTALLATION.md)
- **Development:** See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Issues:** https://github.com/Mittenzx/Adastrea-Director/issues

---

**Last Updated:** January 2026  
**UE Version:** 5.6  
**Plugin Version:** 1.0.0
