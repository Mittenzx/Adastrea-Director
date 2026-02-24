# Enhanced Adastrea Director Plugin Tools

## 🚀 Overview

This document describes the enhanced tools and utilities created to improve the Adastrea Director plugin experience. These tools address common issues with Unreal Engine Python Remote Execution setup and provide better error handling, diagnostics, and user guidance.

## 📋 Enhanced Tools

### 1. `configure_unreal_python.py` - Configuration Helper
**Purpose**: Helps users configure Unreal Engine for Python Remote Execution.

**Features**:
- Checks current Python Remote Execution configuration
- Creates automatic configuration files for Unreal Engine
- Generates setup instructions
- Provides troubleshooting guidance

**Usage**:
```bash
# Check current configuration
python configure_unreal_python.py --check

# Create automatic configuration
python configure_unreal_python.py --create-config

# Get setup instructions
python configure_unreal_python.py --instructions
```

### 2. `test_unreal_connection.py` - Connection Diagnostic
**Purpose**: Diagnoses Unreal Engine Python Remote Execution connectivity.

**Features**:
- Tests multicast discovery (239.0.0.1:6766)
- Tests direct command endpoint (127.0.0.1:6776)
- Provides clear error messages
- Suggests troubleshooting steps

**Usage**:
```bash
python test_unreal_connection.py
```

### 3. `server_enhanced.py` - Enhanced MCP Server
**Purpose**: Improved MCP server with better error handling and diagnostics.

**Features**:
- Enhanced error messages with actionable steps
- Automatic configuration checking
- Diagnostic information
- User-friendly connection help
- Backward compatible with original server

**Usage**:
```bash
# Start enhanced server
python -m mcp_server.server_enhanced

# With diagnostics
python -m mcp_server.server_enhanced --diagnostics

# Check configuration only
python -m mcp_server.server_enhanced --check
```

### 4. `unreal_mcp_cli_enhanced.py` - Enhanced CLI
**Purpose**: Improved command-line interface with better user experience.

**Features**:
- Enhanced interactive mode
- Setup help command
- Diagnostic information
- Better error messages
- Backward compatible with original CLI

**Usage**:
```bash
# Interactive mode
python unreal_mcp_cli_enhanced.py

# Show setup help
python unreal_mcp_cli_enhanced.py --setup-help

# Show diagnostics
python unreal_mcp_cli_enhanced.py --diagnostics

# Standard commands (same as original)
python unreal_mcp_cli_enhanced.py project-info
python unreal_mcp_cli_enhanced.py list-assets
```

### 5. `enhanced_error_handling.py` - Error Handling Module
**Purpose**: Provides enhanced error messages for MCP server.

**Features**:
- Detailed connection error messages
- Tool execution error handling
- Installation guide generation
- Can be imported by other modules

**Usage**:
```python
from mcp_server.enhanced_error_handling import (
    get_enhanced_connection_error,
    get_tool_execution_error,
    get_installation_guide
)
```

## 🛠️ Installation & Setup

### Quick Setup Script
```bash
# Run the comprehensive setup
python configure_unreal_python.py --create-config
python test_unreal_connection.py
python unreal_mcp_cli_enhanced.py --setup-help
```

### Manual Setup Steps
1. **Enable Python Plugin in Unreal Engine**:
   - Edit → Plugins → Search "Python" → Enable "Python Editor Script Plugin"

2. **Enable Remote Execution**:
   - Edit → Project Settings → Search "Python" → Check "Enable Remote Execution"
   - Set "Multicast Bind Address" to "0.0.0.0"

3. **Verify Configuration**:
   ```bash
   python test_unreal_connection.py
   ```

4. **Start Enhanced Tools**:
   ```bash
   python unreal_mcp_cli_enhanced.py
   ```

## 🔧 Troubleshooting

### Common Issues & Solutions

#### Issue: "Not connected to Unreal Engine"
**Solution**:
```bash
# Diagnose the issue
python test_unreal_connection.py

# Get setup instructions
python configure_unreal_python.py --instructions

# Try automatic configuration
python configure_unreal_python.py --create-config
```

#### Issue: Python plugin not found in Unreal Engine
**Solution**:
1. Install via Epic Games Launcher
2. Under "Engine" plugins, not "Project" plugins
3. Restart Unreal Editor after installation

#### Issue: Port conflicts (6766 or 6776)
**Solution**:
1. Check if another application is using the ports
2. Change ports in Unreal Engine Project Settings
3. Update MCP server configuration accordingly

#### Issue: Firewall blocking connections
**Solution**:
1. Add firewall exceptions for ports 6766 and 6776
2. Allow UnrealEditor.exe through firewall
3. Test with firewall temporarily disabled

## 📊 Diagnostic Commands

### Quick Health Check
```bash
# Comprehensive health check
python verify_repository.py
python test_unreal_connection.py
python configure_unreal_python.py --check
```

### Connection Testing
```bash
# Test basic connectivity
python test_unreal_connection.py

# Test with enhanced diagnostics
python -m mcp_server.server_enhanced --check

# Test MCP server functionality
python unreal_mcp_cli_enhanced.py --diagnostics
```

### Configuration Verification
```bash
# Verify repository structure
python verify_repository.py

# Check Python configuration
python configure_unreal_python.py --check

# Test all tools
python unreal_mcp_cli_enhanced.py list-tools
```

## 🎯 Usage Examples

### Example 1: Complete Setup Workflow
```bash
# Step 1: Check current setup
python configure_unreal_python.py --check

# Step 2: Configure Unreal Engine
python configure_unreal_python.py --create-config

# Step 3: Launch Unreal Engine Editor
# (Manual step - open your project)

# Step 4: Verify connection
python test_unreal_connection.py

# Step 5: Use enhanced CLI
python unreal_mcp_cli_enhanced.py
```

### Example 2: Quick Diagnostic Workflow
```bash
# When experiencing issues:
python test_unreal_connection.py
python unreal_mcp_cli_enhanced.py --diagnostics
python configure_unreal_python.py --instructions
```

### Example 3: Development Workflow
```bash
# Start enhanced MCP server
python -m mcp_server.server_enhanced --debug

# In another terminal, test commands
python unreal_mcp_cli_enhanced.py project-info
python unreal_mcp_cli_enhanced.py list-assets
python unreal_mcp_cli_enhanced.py run-python "import unreal; print('Hello UE!')"
```

## 📁 File Structure

```
Adastrea-Director/
├── configure_unreal_python.py          # Configuration helper
├── test_unreal_connection.py           # Connection diagnostic
├── unreal_mcp_cli_enhanced.py          # Enhanced CLI
├── verify_repository.py                # Repository verification
├── mcp_server/
│   ├── server_enhanced.py              # Enhanced MCP server
│   └── enhanced_error_handling.py      # Error handling module
├── UNREAL_PYTHON_SETUP.md              # Setup documentation
├── UNREAL_PYTHON_INSTALLATION_GUIDE.md # Installation guide
└── ENHANCED_PLUGIN_TOOLS.md            # This document
```

## 🔄 Integration with Original Tools

### Backward Compatibility
All enhanced tools are designed to be backward compatible:
- `unreal_mcp_cli_enhanced.py` can run all original commands
- `server_enhanced.py` extends the original server class
- Configuration files work with both original and enhanced tools

### Migration Path
1. Start using enhanced tools alongside original tools
2. Gradually replace original tools with enhanced versions
3. Enhanced tools can be used as drop-in replacements

## 🚀 Getting Started for New Users

### For First-Time Users
```bash
# 1. Clone the repository
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director

# 2. Verify repository
python verify_repository.py

# 3. Get setup instructions
python configure_unreal_python.py --instructions

# 4. Follow the setup instructions
# ... (setup Unreal Engine)

# 5. Test connection
python test_unreal_connection.py

# 6. Start using the tools
python unreal_mcp_cli_enhanced.py
```

### For Existing Users
```bash
# 1. Update your repository
git pull origin main

# 2. Try the enhanced tools
python unreal_mcp_cli_enhanced.py --diagnostics

# 3. Use enhanced error messages
python -m mcp_server.server_enhanced

# 4. Provide feedback on the enhanced tools
```

## 📈 Benefits of Enhanced Tools

### For Users
- ✅ Better error messages with actionable steps
- ✅ Automatic configuration assistance
- ✅ Comprehensive diagnostic tools
- ✅ Clear setup instructions
- ✅ Reduced setup time and frustration

### For Developers
- ✅ Modular design for easy maintenance
- ✅ Backward compatibility
- ✅ Comprehensive testing tools
- ✅ Better debugging information
- ✅ Easier issue diagnosis

### For the Project
- ✅ Reduced support burden
- ✅ Better user experience
- ✅ More reliable installations
- ✅ Comprehensive documentation
- ✅ Professional tooling ecosystem

## 🤝 Contributing

### Adding New Enhanced Tools
1. Follow the existing patterns in the enhanced tools
2. Maintain backward compatibility
3. Include comprehensive documentation
4. Add diagnostic capabilities
5. Test with the verification scripts

### Reporting Issues
1. Use the diagnostic tools first
2. Include output from: `python test_unreal_connection.py`
3. Include output from: `python configure_unreal_python.py --check`
4. Describe the exact steps to reproduce

### Improving Documentation
1. Update the setup guides as needed
2. Add new troubleshooting scenarios
3. Improve error message clarity
4. Add more usage examples

## 📚 Related Documentation

- [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) - Quick start guide
- [WORK_SESSION_SUMMARY_2026-02-24.md](WORK_SESSION_SUMMARY_2026-02-24.md) - Work session summary
- [UNREAL_PYTHON_SETUP.md](UNREAL_PYTHON_SETUP.md) - Unreal Engine setup guide
- [Plugins/AdastreaDirector/README.md](Plugins/AdastreaDirector/README.md) - Plugin documentation

## 🏁 Conclusion

The enhanced plugin tools provide a significantly improved experience for setting up and using the Adastrea Director plugin. With better error messages, automatic configuration, and comprehensive diagnostics, users can get up and running faster with fewer issues.

**Start using the enhanced tools today:**
```bash
python unreal_mcp_cli_enhanced.py --setup-help
```

---

*Last Updated: 2026-02-24*  
*Created as part of the Adastrea Director plugin enhancement project*