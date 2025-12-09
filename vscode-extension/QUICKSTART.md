# VS Code Extension Quick Start Guide

Get started with the Adastrea Director VS Code extension in 5 minutes!

## Prerequisites

- VS Code 1.80.0 or higher
- Node.js 18+ (for development)
- Python 3.9+ (for the Director IPC server)

## Step 1: Install Dependencies

```bash
cd vscode-extension
npm install
```

## Step 2: Compile the Extension

```bash
npm run compile
```

## Step 3: Start the Director IPC Server

In a separate terminal, start the Director IPC server:

```bash
cd ..
python Plugins/AdastreaDirector/Python/ipc_server.py --port 5555
```

You should see output like:
```
2025-12-09 11:16:29,853 - AdastreaIPCServer - INFO - IPC Server started on 127.0.0.1:5555
2025-12-09 11:16:29,853 - AdastreaIPCServer - INFO - Waiting for connections from Unreal Engine plugin...
```

## Step 4: Test the Integration (Optional)

Run the integration tests to verify everything works:

```bash
node test-integration.js
```

Expected output:
```
============================================================
Adastrea Director VS Code Extension - Integration Tests
============================================================

Test 1: Connection
  ✓ Connected successfully

Test 2: Health Check (Ping)
  ✓ Ping successful

Test 3: Query Request
  ✓ Query successful
  
...

============================================================
Test Results
============================================================
Passed: 5
Failed: 0
Total:  5
============================================================
```

## Step 5: Run the Extension in VS Code

1. Open the `vscode-extension` folder in VS Code:
   ```bash
   code .
   ```

2. Press `F5` to launch the extension in debug mode
   - This will open a new VS Code window titled "Extension Development Host"

3. In the Extension Development Host window:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) to open the Command Palette
   - Type "Director: Connect" and select "Director: Connect to Unreal Engine"
   - You should see "Connected to Adastrea Director" message

4. Try asking a question:
   - Press `Ctrl+Shift+P` again
   - Type "Director: Ask" and select "Director: Ask Question"
   - Enter a question like "How do I create a player character in Unreal Engine?"
   - View the response in the Output panel (View → Output → Adastrea Director)

## Step 6: Check the Status Bar

Look at the bottom-left of VS Code. You should see:
- 🟢 **Director: Connected** - when successfully connected
- 🔴 **Director: Error** - when there's a connection error
- ⚫ **Director: Disconnected** - when not connected

Click the status bar item to check the current status.

## Available Commands

All commands are available through the Command Palette (`Ctrl+Shift+P`):

1. **Director: Connect to Unreal Engine** - Connect to the IPC server
2. **Director: Disconnect from Unreal Engine** - Disconnect from the server
3. **Director: Ask Question** - Ask a question to the Director AI
4. **Director: Check Connection Status** - Check connection state

## Troubleshooting

### "Connection Refused" Error

**Cause:** The IPC server is not running.

**Solution:** Start the IPC server:
```bash
python Plugins/AdastreaDirector/Python/ipc_server.py --port 5555
```

### Port Already in Use

**Cause:** Another process is using port 5555.

**Solution:** Find and stop the process using port 5555:
```bash
# On Linux/Mac
lsof -i :5555
kill <PID>

# On Windows
netstat -ano | findstr :5555
taskkill /PID <PID> /F
```

### Extension Not Loading

**Cause:** Compilation errors or missing dependencies.

**Solution:**
1. Clean and rebuild:
   ```bash
   rm -rf out node_modules
   npm install
   npm run compile
   ```

2. Check for TypeScript errors:
   ```bash
   npx tsc --noEmit
   ```

### Health Check Failures

**Cause:** IPC server is not responding correctly.

**Solution:**
1. Check server logs for errors
2. Restart the IPC server
3. Try disconnecting and reconnecting in VS Code

## Configuration

Configure the extension in VS Code settings (`Ctrl+,`):

```json
{
  "director.ipc.host": "localhost",
  "director.ipc.port": 5555,
  "director.autoConnect": false,
  "director.reconnectInterval": 5000,
  "director.maxReconnectAttempts": 3
}
```

## Next Steps

- Explore the [README.md](README.md) for detailed documentation
- Check the [parent repository](https://github.com/Mittenzx/Adastrea-Director) for more features
- Read about [Phase 2 planning](https://github.com/Mittenzx/Adastrea-Director/wiki) in the wiki

## Development Tips

### Watch Mode

During development, run the compiler in watch mode:
```bash
npm run watch
```

This will automatically recompile when you save files.

### Debugging

1. Set breakpoints in your TypeScript code
2. Press `F5` to start debugging
3. The extension runs in the Extension Development Host window
4. Debug output appears in the Debug Console

### Testing

Run unit tests (when available):
```bash
npm test
```

Run integration tests:
```bash
node test-integration.js
```

## Support

- [GitHub Issues](https://github.com/Mittenzx/Adastrea-Director/issues)
- [Documentation](https://github.com/Mittenzx/Adastrea-Director/wiki)

---

**Happy coding with Adastrea Director! 🎮✨**
