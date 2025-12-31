# MCP Integration Quick Start

**Quick reference for integrating Adastrea-Director with Adastrea-MCP**

---

## 🎯 Goal

Connect Adastrea-MCP (Node.js) to Adastrea-Director (Python) so AI agents get both:
- **Static analysis** (code structure, knowledge, generation) from Adastrea-MCP
- **Runtime control** (live editor, Python execution, console) from Adastrea-Director

---

## 📋 Current Status

### ✅ What's Working

**Adastrea-Director MCP** (this repo):
- 13 MCP tools via stdio
- Works with VS Code Copilot
- Python Remote Execution to UE
- 84 tests passing

**Adastrea-MCP** (separate repo):
- 37 MCP tools, 13 resources
- Infrastructure ready to call Director
- Phases 1-3.1 complete
- UE5.6+ knowledge database

### ❌ What's Missing

**REST API in Adastrea-Director**
- Adastrea-MCP needs HTTP endpoints
- Currently has MCP stdio only
- Need 6 core REST endpoints

---

## 🏗️ Architecture

```
AI Agent (Claude, VS Code)
    ↓ stdio MCP
Adastrea-MCP (Node.js) [37 tools]
    ↓ HTTP REST
Adastrea-Director (Python) [13 tools] ← TO BE IMPLEMENTED
    ↓ Python Remote Execution
Unreal Engine Editor
```

---

## 🔧 Implementation Steps

### Step 1: Create REST API Module

```bash
cd /path/to/Adastrea-Director
mkdir rest_api
touch rest_api/__init__.py
touch rest_api/server.py
touch rest_api/routes.py
touch rest_api/models.py
```

### Step 2: Install Dependencies

Add to `requirements.txt`:
```
flask>=3.0.0
flask-cors>=4.0.0
```

Or use FastAPI:
```
fastapi>=0.104.0
uvicorn>=0.24.0
```

### Step 3: Implement Server

**⚠️ SECURITY WARNING:**

The REST API endpoints expose **highly privileged operations** including:
- Arbitrary Python code execution in Unreal Editor
- Full console command access
- Direct UE Editor control

**Required Security Measures:**
1. **CORS**: Restrict to trusted origins only (NOT `origins: "*"`)
2. **Network**: Bind to localhost only (127.0.0.1)
3. **Authentication**: Consider adding API key/token authentication
4. **Validation**: Always validate and sanitize inputs
5. **Firewall**: Ensure firewall blocks external access to port 3001

**Never expose these endpoints to untrusted networks or origins!**

---

**rest_api/server.py** (Flask example):
```python
from flask import Flask, jsonify, request
from flask_cors import CORS
from mcp_server import UnrealMCPServer
import logging
import threading

app = Flask(__name__)

# Security: Restrict CORS to trusted local origins only
# IMPORTANT: These endpoints execute arbitrary code in UE - protect them!
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Example: local MCP UI
    # Add other trusted origins as needed
]
CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}})

# Lazily initialize MCP server on first use
mcp_server = None
mcp_lock = threading.Lock()

def get_mcp_server():
    """
    Ensure the UnrealMCPServer is started and connected.
    Returns the server instance, or None if it could not be started.
    """
    global mcp_server
    # Fast path without lock
    if mcp_server is not None and mcp_server.is_connected():
        return mcp_server

    with mcp_lock:
        # Re-check state after acquiring the lock
        if mcp_server is not None and mcp_server.is_connected():
            return mcp_server

        server = UnrealMCPServer()
        try:
            started = server.start()
        except Exception:
            logging.exception("Failed to start UnrealMCPServer")
            return None

        if not started:
            logging.error("UnrealMCPServer.start() returned False; server not started")
            return None

        mcp_server = server
        return mcp_server

@app.route('/health', methods=['GET'])
def health():
    server = get_mcp_server()
    editor_connected = bool(server and server.is_connected())
    return jsonify({
        'editorConnected': editor_connected,
        'version': '1.0.0',
        'capabilities': ['console', 'python', 'assets']
    })

@app.route('/api/editor/state', methods=['GET'])
def editor_state():
    server = get_mcp_server()
    if not server or not server.is_connected():
        return jsonify({'error': 'Not connected'}), 503
    
    # Get current level using existing MCP tools
    result = server.handle_tool_call('editor_get_map_info', {})
    return jsonify({
        'isRunning': True,
        'currentLevel': result.get('name', 'Unknown'),
        'editingContext': {'mode': 'LevelEditor'}
    })

@app.route('/api/project/info', methods=['GET'])
def project_info():
    server = get_mcp_server()
    if not server or not server.is_connected():
        return jsonify({'error': 'Not connected'}), 503
    
    result = server.handle_tool_call('editor_project_info', {})
    return jsonify(result)

@app.route('/api/console/execute', methods=['POST'])
def console_execute():
    # Safely parse JSON body; returns None on invalid/missing JSON
    data = request.get_json(silent=True) or {}
    command = data.get('command')
    
    if command is None:
        return jsonify({'error': 'Missing required field: command'}), 400
    
    server = get_mcp_server()
    if not server or not server.is_connected():
        return jsonify({'error': 'Not connected'}), 503
    
    result = server.handle_tool_call('editor_console_command', {
        'command': command
    })
    
    return jsonify({
        'command': command,
        'output': result.get('content', [{}])[0].get('text', ''),
        'success': not result.get('isError', False)
    })

@app.route('/api/python/execute', methods=['POST'])
def python_execute():
    # Safely parse JSON body; returns None on invalid/missing JSON
    data = request.get_json(silent=True) or {}
    code = data.get('code')
    
    if code is None:
        return jsonify({'error': 'Missing required field: code'}), 400
    
    server = get_mcp_server()
    if not server or not server.is_connected():
        return jsonify({'error': 'Not connected'}), 503
    
    result = server.handle_tool_call('editor_run_python', {
        'code': code
    })
    
    return jsonify({
        'code': code,
        'output': result.get('content', [{}])[0].get('text', '') if not result.get('isError', False) else '',
        'success': not result.get('isError', False),
        'error': result.get('content', [{}])[0].get('text', '') if result.get('isError', False) else None
    })

@app.route('/api/assets/list', methods=['POST'])
def list_assets():
    data = request.get_json(silent=True) or {}
    asset_filter = data.get('filter')
    
    server = get_mcp_server()
    if not server or not server.is_connected():
        return jsonify({'error': 'Not connected'}), 503
    
    result = server.handle_tool_call('editor_list_assets', {})
    
    # Parse and filter assets if needed
    assets = result.get('content', [{}])[0].get('text', '').split('\n')
    
    # Convert to structured format
    asset_list = []
    for asset_path in assets:
        if asset_path.strip():
            asset_list.append({
                'assetPath': asset_path,
                'assetName': asset_path.split('/')[-1],
                'assetClass': 'Unknown'  # Could parse from path
            })
    
    return jsonify(asset_list)

def main():
    app.run(host='localhost', port=3001, debug=False)

if __name__ == '__main__':
    main()
```

### Step 4: Run the Server

```bash
# Terminal 1: Start REST API
cd /path/to/Adastrea-Director
python -m rest_api.server

# Terminal 2: Start Unreal Engine with Python plugin

# Terminal 3: Test API
curl http://localhost:3001/health
```

### Step 5: Configure Adastrea-MCP

In Adastrea-MCP, set environment variable:

```bash
export DIRECTOR_URL=http://localhost:3001
```

Or in MCP client configuration:
```json
{
  "mcpServers": {
    "adastrea-mcp": {
      "command": "node",
      "args": ["/path/to/Adastrea-MCP/build/index.js"],
      "env": {
        "DIRECTOR_URL": "http://localhost:3001"
      }
    }
  }
}
```

### Step 6: Test Integration

From Adastrea-MCP repository:
```bash
# Should now connect to Director REST API
npm run build
node build/index.js
```

---

## 🧪 Testing Checklist

### Basic Connectivity
- [ ] REST API starts without errors
- [ ] `/health` endpoint returns 200 OK
- [ ] Adastrea-MCP can reach Director at configured URL

### Tool Operations
- [ ] Console command execution works
- [ ] Python code execution works
- [ ] Asset listing returns data
- [ ] Project info returns correct data
- [ ] Editor state returns current level

### Error Handling
- [ ] Graceful response when UE not running
- [ ] Proper HTTP status codes (200, 503, etc.)
- [ ] Clear error messages in responses
- [ ] Timeout handling works

### Integration
- [ ] Adastrea-MCP receives correct responses
- [ ] Static analysis falls back correctly when Director unavailable
- [ ] No port conflicts
- [ ] CORS headers allow MCP client connections

---

## 🐛 Troubleshooting

### Problem: REST API won't start

**Check**:
```bash
# Is port 3001 already in use?
lsof -i :3001  # Linux/Mac
netstat -ano | findstr :3001  # Windows

# Check Python version
python --version  # Should be 3.9+

# Check dependencies
pip install flask flask-cors
```

### Problem: Adastrea-MCP can't connect

**Check**:
```bash
# Can you reach the API directly?
curl http://localhost:3001/health

# Is DIRECTOR_URL set correctly in Adastrea-MCP?
echo $DIRECTOR_URL

# Check firewall
# Ensure localhost connections allowed
```

### Problem: UE commands failing

**Check**:
- Is Unreal Engine running?
- Is Python Editor Script Plugin enabled?
- Is Remote Execution enabled in Project Settings?
- Check UE Editor logs for Python errors

### Problem: CORS errors

**⚠️ SECURITY WARNING:** Never use `origins: "*"` with these endpoints!

**Secure Solution**:
```python
# In rest_api/server.py
from flask_cors import CORS

app = Flask(__name__)

# Restrict CORS to trusted local origins only
# These endpoints execute arbitrary code - protect them!
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Example: local MCP UI
    # Add other trusted origins as needed
]

CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}})
```

**Why this matters:**
- These endpoints execute arbitrary Python code and console commands
- With `origins: "*"`, any website could attack your local dev environment
- Always restrict to specific trusted origins
- Consider adding authentication for additional security

---

## 📊 Endpoints Reference

| Endpoint | Method | Purpose | UE Required? |
|----------|--------|---------|--------------|
| `/health` | GET | Connection status | No |
| `/api/editor/state` | GET | Current editor state | Yes |
| `/api/project/info` | GET | Project information | Yes |
| `/api/console/execute` | POST | Run console command | Yes |
| `/api/python/execute` | POST | Execute Python code | Yes |
| `/api/assets/list` | POST | List project assets | Yes |

---

## 🎓 Usage Examples

### From AI Agent (via Adastrea-MCP)

**List all materials in project:**
```
"List all materials in the Adastrea project"
```
→ Adastrea-MCP calls Director `/api/assets/list` with filter "Material"

**Execute Python to spawn actor:**
```
"Spawn a cube at position 0,0,100"
```
→ Adastrea-MCP calls Director `/api/python/execute` with spawn code

**Get project information:**
```
"What Unreal Engine version is Adastrea using?"
```
→ Adastrea-MCP calls Director `/api/project/info`

---

## 📚 Next Steps

After basic integration works:

1. **Add Authentication** (optional)
   - API keys for security
   - Token-based auth

2. **Add WebSocket Support**
   - Real-time bidirectional communication
   - Editor event subscriptions

3. **Optimize Performance**
   - Connection pooling
   - Response caching
   - Batch operations

4. **Improve Error Handling**
   - Retry logic
   - Circuit breakers
   - Better error messages

5. **Documentation**
   - OpenAPI/Swagger spec
   - Interactive API docs
   - Video tutorials

---

## 🔗 Related Documents

- **[MCP_READINESS_PLAN.md](./MCP_READINESS_PLAN.md)** - Complete integration strategy
- **[MCP_SERVER_GUIDE.md](../../mcp_server/MCP_SERVER_GUIDE.md)** - Adastrea-Director MCP usage
- **Adastrea-MCP Docs** - `INTEGRATION_NOTES.md`, `NEXT_STEPS.md` in separate repo

---

## ⚡ Quick Commands

```bash
# Start REST API server
python -m rest_api.server

# Test health endpoint
curl http://localhost:3001/health

# Execute console command
curl -X POST http://localhost:3001/api/console/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "stat fps"}'

# Execute Python code
curl -X POST http://localhost:3001/api/python/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "import unreal; print(unreal.SystemLibrary.get_engine_version())"}'
```

---

**Status**: Ready to implement  
**Complexity**: Moderate  
**Time Estimate**: 1-2 weeks  
**Priority**: High

Let's make it happen! 🚀
