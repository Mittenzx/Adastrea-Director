# Tests Tab - Quick Start Guide

## What is the Tests Tab?

The Tests tab is a new feature in the Adastrea Director GUI that lets you run Python test scripts with a simple button click. No command-line knowledge needed!

## Getting Started (3 Easy Steps)

### Step 1: Open the GUI
```bash
python gui_director.py
```

### Step 2: Click the Tests Tab
Look for the **"🧪 Tests"** tab at the top of the window (third tab, after Conversation and Ingest List).

### Step 3: Click a Test Button
Choose any test category and click to run:
- 🚀 Run All Tests
- 🔌 Plugin Tests
- ⚙️ Unit Tests
- And more...

That's it! Watch the results appear in real-time.

## Understanding the Results

### Colors Tell the Story
- ✅ **Green text** = Tests passing (good!)
- ❌ **Red text** = Tests failing (needs attention)
- ⚠️ **Yellow text** = Warnings (check if important)
- ℹ️ **Grey text** = Information (just FYI)

### Final Summary
At the end, you'll see either:
- **✅ Tests PASSED** (everything works!)
- **❌ Tests FAILED** (something needs fixing)

## Common Tasks

### Running Plugin Tests
**Why**: Verify your plugin installation is working correctly

**How**: 
1. Click the **"🔌 Plugin Tests"** button
2. Wait for tests to complete (usually 10-30 seconds)
3. Check for green ✅ at the bottom

**What it tests**: IPC communication, RAG modules, UE Python API

### Running All Tests
**Why**: Complete verification of the entire system

**How**: 
1. Click the **"🚀 Run All Tests (pytest)"** button
2. Wait for tests to complete (may take 1-5 minutes)
3. Check the final summary

**What it tests**: Everything - unit tests, integration tests, all features

### Stopping a Test
**Why**: If a test is taking too long or you need to cancel

**How**: 
1. Click the **"⏹ Stop"** button (top-right, red)
2. Test will terminate immediately
3. You can start a new test

### Clearing Output
**Why**: Clean up before running a new test

**How**: 
1. Click the **"🗑️ Clear"** button (top-right)
2. Output area resets
3. Ready for next test

## FAQ

### Q: Can I run multiple tests at once?
**A**: No, only one test at a time. This prevents conflicts and ensures accurate results.

### Q: How long do tests take?
**A**: 
- Plugin Tests: ~30 seconds
- Unit Tests: ~1 minute
- All Tests: ~5 minutes
- Others: varies

### Q: What if tests fail?
**A**: 
1. Read the red error messages
2. They usually tell you what's wrong
3. Fix the issue
4. Run the test again

### Q: Can I copy test output?
**A**: Yes! Click in the output area, select text, and press Ctrl+C (or Cmd+C on Mac).

### Q: Do I need pytest installed?
**A**: Yes, it's included in `requirements.txt`. If tests don't run, make sure you ran:
```bash
pip install -r requirements.txt
```

## Tips & Tricks

### Tip 1: Start Small
Don't start with "Run All Tests" - try a smaller category first like "Unit Tests" or "Plugin Tests".

### Tip 2: Watch the Output
Don't just wait for the final result - watch the output stream. It can help you understand what's being tested.

### Tip 3: Use Clear
Click "Clear" before each test run to make it easier to see just the new results.

### Tip 4: Check Tooltips
Hover over any button to see a tooltip explaining what it does.

### Tip 5: Stop If Needed
Don't hesitate to stop a test if it's taking too long - you won't break anything.

## Troubleshooting

### Problem: Tests button is greyed out
**Solution**: Another test is running. Wait for it to finish or click "Stop".

### Problem: "Command not found" error
**Solution**: Make sure pytest is installed:
```bash
pip install pytest
```

### Problem: Tests fail immediately
**Solution**: Check that you're in the correct directory with all project files.

### Problem: Output shows weird characters
**Solution**: This is normal for some test frameworks - just ignore them and look for green/red indicators.

### Problem: GUI freezes during tests
**Solution**: This shouldn't happen! If it does, restart the GUI and report the issue.

## Test Category Details

### 🚀 Run All Tests
- **Runs**: Complete pytest suite
- **Time**: ~5 minutes
- **Use when**: You want to verify everything

### 🔌 Plugin Tests
- **Runs**: IPC, RAG, UE Python API tests
- **Time**: ~30 seconds
- **Use when**: Checking plugin installation

### ⚙️ Unit Tests
- **Runs**: Unit tests only
- **Time**: ~1 minute
- **Use when**: Testing core functionality

### 🔗 Integration Tests
- **Runs**: Integration tests
- **Time**: ~2 minutes
- **Use when**: Testing component interactions

### 🎯 Phase 3 Tests
- **Runs**: Phase 3 agent tests
- **Time**: ~1 minute
- **Use when**: Testing autonomous agents

### ✅ Validation Scripts
- **Runs**: Installation & compatibility checks
- **Time**: ~10 seconds
- **Use when**: Verifying setup

### 🌐 Remote Control Tests
- **Runs**: Remote API tests
- **Time**: ~30 seconds
- **Use when**: Testing remote control features

## Best Practices

1. **Run validation first**: Start with "✅ Validation Scripts" to ensure setup is correct
2. **Test specific areas**: Use category buttons instead of "Run All Tests" when debugging
3. **Stop if stuck**: Don't let tests run forever - stop after 10 minutes max
4. **Clear between runs**: Use "Clear" to make output easier to read
5. **Read error messages**: They usually tell you exactly what's wrong

## Need More Help?

- **Feature Documentation**: See `TESTS_TAB_FEATURE.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Visual Guide**: See `TESTS_TAB_SCREENSHOT_DESCRIPTION.md`
- **Security Info**: See `SECURITY_SUMMARY.md`

## Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│  TESTS TAB QUICK REFERENCE                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  🚀 All Tests      = Everything (~5 min)       │
│  🔌 Plugin Tests   = Plugin check (~30 sec)    │
│  ⚙️ Unit Tests     = Core tests (~1 min)       │
│  🔗 Integration    = Components (~2 min)       │
│  🎯 Phase 3        = Agents (~1 min)           │
│  ✅ Validation     = Setup check (~10 sec)     │
│  🌐 Remote         = API tests (~30 sec)       │
│                                                 │
│  ⏹ Stop = Terminate test                       │
│  🗑️ Clear = Reset output                        │
│                                                 │
│  ✅ Green = Pass    ❌ Red = Fail              │
│  ⚠️ Yellow = Warn   ℹ️ Grey = Info             │
└─────────────────────────────────────────────────┘
```

---

**Happy Testing!** 🧪✨

If you encounter any issues or have suggestions, please open an issue on GitHub.
