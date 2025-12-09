# Quick Start: Using GitHub Copilot with UE Logs

A quick reference for accessing Unreal Engine logs with GitHub Copilot in VSCode.

## TL;DR

✅ **Already set up!** The `.copilotignore` file in this repo makes UE logs visible to Copilot.

## Usage

### Step 1: Open a UE Log File
```
<YourProject>/Saved/Logs/YourProject.log
```

### Step 2: Ask Copilot for Help

**In Copilot Chat** (Ctrl+Shift+I or Cmd+Shift+I):
```
What's causing the crash in this log?
Explain this error: [paste error message]
How can I fix this warning?
@workspace What errors are in Saved/Logs/?
```

**In Code Comments:**
```cpp
// TODO: Fix crash from MyProject.log line 1234
// Error: Assertion failed: IsValid()
```
Copilot will suggest fixes based on the log context.

### Step 3: Get Instant Analysis

Copilot can:
- ✅ Identify crash causes
- ✅ Explain error messages
- ✅ Suggest fixes
- ✅ Analyze performance issues
- ✅ Debug blueprint/Python errors

## Common Log Locations

| Type | Location |
|------|----------|
| **Project Logs** | `<Project>/Saved/Logs/<ProjectName>.log` |
| **Plugin Logs** | `<Project>/Saved/Logs/AdastreaDirector.log` |
| **Test Logs** | `tests/*.log` |

## Example Workflows

### 🔥 Debug a Crash
1. Open `Saved/Logs/MyProject.log`
2. Find the crash (search for "Fatal error")
3. Ask Copilot: "What caused this crash?"

### ⚠️ Fix a Warning
1. Copy the warning from UE Output Log
2. Ask Copilot: "What does this warning mean?"
3. Implement suggested fix

### 🚀 Optimize Performance
1. Enable profiling: `stat unit` in UE console
2. Open the log file
3. Ask Copilot: "What's causing performance issues?"

## What's Included

The `.copilotignore` configuration includes:
- ✅ All `.log` files in the repository
- ✅ UE logs in `Saved/Logs/` directories
- ✅ Test logs
- ❌ Very large crash dumps (`.dmp`, `.crash`)
- ❌ Verbose build logs

## Troubleshooting

**Copilot not seeing logs?**
1. Ensure `.copilotignore` exists in repo root
2. Reload VSCode window (Ctrl+Shift+P → "Reload Window")
3. Open the log file directly
4. Use `@workspace` in Copilot Chat

**Log file too large?**
- Limit: ~1MB for optimal performance
- Solution: Delete old logs or use specific log sections

## Full Documentation

📖 **Complete guide:** [COPILOT_UE_LOGS_GUIDE.md](COPILOT_UE_LOGS_GUIDE.md)

Topics covered:
- Detailed setup instructions
- Advanced usage patterns
- Security considerations
- Integration with UE Python API
- Troubleshooting guide
- FAQ

## Summary

🎯 **Three steps to AI-powered UE debugging:**
1. ✅ Setup is done (`.copilotignore` included)
2. 📂 Open a UE log file
3. 💬 Ask Copilot for help

That's it! Start debugging smarter with AI assistance.

---

*Part of the Adastrea Director project*
