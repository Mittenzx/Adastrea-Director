# Adastrea Director - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Option 1: Standalone Python Tools (Recommended for First-Time Users)

The standalone Python tools don't require Unreal Engine and demonstrate the core AI capabilities:

```bash
# 1. Clone the repository
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director

# 2. Install minimal dependencies (skip LLM dependencies for now)
pip install python-dotenv rich click

# 3. Test the planning system (P2 - Complete!)
python examples/planning_example.py

# 4. Test API key configuration
python test_api_keys.py --skip-api-test
```

### Option 2: Unreal Engine Integration (For UE Developers)

```bash
# 1. Clone the repository
git clone https://github.com/Mittenzx/Adastrea-Director.git

# 2. Copy plugin to your UE project
cp -r Adastrea-Director/Plugins/AdastreaDirector YourUEProject/Plugins/

# 3. Enable in Unreal Editor:
#    - Edit → Plugins → Search "Python" → Enable "Python Editor Script Plugin"
#    - Project Settings → Python → Enable "Remote Execution"

# 4. Test connection
python test_unreal_connection.py

# 5. Run MCP server
python unreal_mcp_cli.py
```

## 📋 What You Can Do

### Without Unreal Engine
- ✅ **Goal Planning** - Decompose development goals into tasks
- ✅ **Document Q&A** - Ask questions about your project docs
- ✅ **Autonomous Agents** - Performance profiling, bug detection
- ✅ **Code Generation** - Get implementation suggestions

### With Unreal Engine
- 🎮 **Editor Control** - Control UE via natural language
- 🎮 **Asset Management** - List, search, create assets
- 🎮 **Python Execution** - Run Python directly in UE Editor
- 🎮 **Blueprint Creation** - Create Blueprints via AI

## 🔧 Troubleshooting

### Common Issues

#### "No Unreal Engine multicast announcements"
```bash
# Run diagnostic tool
python test_unreal_connection.py

# Solutions:
# 1. Ensure Unreal Editor is running
# 2. Enable Python Editor Script Plugin
# 3. Enable Remote Execution in Project Settings
```

#### "Missing dependencies"
```bash
# Install all dependencies (takes time)
pip install -r requirements.txt

# Or install minimal set:
pip install python-dotenv rich click websocket-client
```

#### "C++ compilation failed"
- Use Blueprint-only project instead
- Or fix C++ build errors in Adastrea project

## 🎯 Quick Demos

### Demo 1: Planning System (2 minutes)
```bash
cd Adastrea-Director
python examples/planning_example.py
```

### Demo 2: UE Connection Test (1 minute)
```bash
cd Adastrea-Director
python test_unreal_connection.py
```

### Demo 3: MCP Server (Requires UE)
```bash
cd Adastrea-Director
python unreal_mcp_cli.py
# Then type: project, assets, python "import unreal; print('Hello UE!')"
```

## 📁 Project Structure

```
Adastrea-Director/
├── examples/              # Example scripts
├── mcp_server/           # Unreal Engine MCP server
├── Plugins/              # UE plugin (copy to your project)
├── requirements.txt      # Python dependencies
├── test_unreal_connection.py  # Connection diagnostic
├── unreal_mcp_cli.py     # Interactive UE control
└── WORK_SESSION_SUMMARY_2026-02-24.md  # Latest work
```

## 🆘 Need Help?

1. **Check the Wiki**: https://github.com/Mittenzx/Adastrea-Director/wiki
2. **Run diagnostics**: `python test_unreal_connection.py`
3. **Test minimal setup**: `python examples/planning_example.py`
4. **Review session summary**: `WORK_SESSION_SUMMARY_2026-02-24.md`

## 🎉 Success Criteria

### Minimum Viable Setup
- [ ] Clone repository
- [ ] Run planning example: `python examples/planning_example.py`
- [ ] See goal decomposition output

### Full Setup
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run all tests: `pytest`
- [ ] Connect to Unreal Engine: `python test_unreal_connection.py` shows SUCCESS
- [ ] Control UE via MCP: `python unreal_mcp_cli.py`

---

*Last Updated: 2026-02-24*  
*Based on work session findings - see WORK_SESSION_SUMMARY_2026-02-24.md for details*