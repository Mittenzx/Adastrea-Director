# Phase 2: Semi-Autonomous Development Guide

This guide covers the Phase 2 features of the Adastrea Director VS Code extension, which enables semi-autonomous code generation, automated testing, and intelligent approval workflows.

## Overview

Phase 2 transforms the extension from a basic assistant to a semi-autonomous development partner that can:

- 🤖 **Generate and apply code automatically** based on natural language goals
- ✅ **Run tests automatically** after code changes
- 👤 **Request human approval** before applying changes
- 📊 **Learn from feedback** to improve future suggestions
- 🎯 **Auto-approve** high-confidence changes based on thresholds

## New Features

### 1. Code Generation and Application

#### Command: `Director: Generate and Apply Code`

Generates code modifications based on your goal and applies them with approval workflow.

**How to use:**
1. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Run `Director: Generate and Apply Code`
3. Enter your goal (e.g., "Add a player health system")
4. Review generated modifications
5. Approve or reject each change

**Features:**
- Multiple implementation approaches
- Confidence scoring for each modification
- Auto-approval for high-confidence changes
- Diff preview before applying
- Option to edit manually

### 2. Automated Testing

#### Command: `Director: Run Tests`

Execute tests via the IPC server and view results in a dedicated output channel.

**How to use:**
1. Open Command Palette
2. Run `Director: Run Tests`
3. Select test suite (All, IPC, Plugin, Unit, Integration, Remote)
4. View results in the output channel

**Features:**
- Multiple test suites supported
- Detailed test results with pass/fail counts
- Navigation to test failure locations
- Optional webview for visual results
- Integration with feedback system

### 3. Approval Workflow

The approval workflow provides intelligent decision-making for code changes:

**Approval Options:**
- ✓ **Approve** - Apply the change immediately
- ✗ **Reject** - Reject the change with optional reason
- 👁 **Preview Diff** - View side-by-side comparison
- ✎ **Edit** - Open file for manual editing

**Confidence Levels:**
- **High (≥90%)**: Auto-applied if threshold is met
- **Medium (60-89%)**: Requires manual review
- **Low (<60%)**: Requires manual review with warning

#### Command: `Director: Review Pending Changes`

Review and manage code changes waiting for approval.

#### Command: `Director: View Approval History`

View statistics and history of all approval decisions.

**Statistics include:**
- Total decisions made
- Approval rate
- Auto-approval count
- Recent decisions with reasons

### 4. Feedback and Learning

The extension collects feedback to improve future suggestions through continuous learning.

#### Command: `Director: Provide Feedback`

Manually provide feedback on a suggestion.

**Feedback types:**
- Star ratings (1-5)
- Approval/rejection reasons
- Suggestions for improvement

#### Command: `Director: Show Feedback Statistics`

View comprehensive feedback statistics in a webview:
- Total feedback items
- Approval rate
- Average rating
- Common rejection reasons
- Frequently approved file patterns

**How feedback is used:**
1. Collected locally in workspace state
2. Sent to IPC server for analysis
3. Used to adjust confidence scores
4. Influences future code generation

### 5. Configuration

#### Auto-Approval Threshold

Set the confidence level required for automatic code application.

**Command:** `Director: Set Auto-Approval Threshold`

**Settings:**
```json
{
  "director.autoApprovalThreshold": 0.9  // 0.0 to 1.0
}
```

- `0.9` (default) - Only very confident changes auto-apply
- `1.0` - Never auto-apply (always ask)
- `0.0` - Always auto-apply (not recommended)

#### Other Settings

```json
{
  "director.autoRunTests": false,          // Run tests after code changes
  "director.enableFeedbackCollection": true // Collect feedback automatically
}
```

## Workflow Examples

### Example 1: Add a New Feature

```
1. Run: "Director: Generate and Apply Code"
2. Enter: "Add a player inventory system with 10 slots"
3. Review: 5 modifications proposed
   - PlayerInventory.cpp (create) - 85% confidence → Review required
   - PlayerInventory.h (create) - 85% confidence → Review required
   - Player.cpp (modify) - 92% confidence → Auto-approved ✓
   - Player.h (modify) - 88% confidence → Review required
   - InventoryUI.cpp (create) - 75% confidence → Review required
4. Approve: Review and approve each modification
5. Test: Run "Director: Run Tests" to verify
6. Feedback: Provide rating if prompted
```

### Example 2: Quick Fix with Auto-Approval

```
1. Set threshold: "Director: Set Auto-Approval Threshold" → 0.85
2. Generate: "Director: Generate and Apply Code"
3. Enter: "Fix null pointer check in UpdateHealth function"
4. Result: Change has 95% confidence → Auto-applied ✓
5. Verify: Code is applied immediately
6. Test: Tests run automatically (if enabled)
```

### Example 3: Review and Modify

```
1. Generate: "Director: Generate and Apply Code"
2. Enter: "Optimize render loop"
3. Review: Pending changes appear
4. Preview: Click "Preview Diff" to see changes
5. Decide: Choose "Edit" to modify manually
6. Apply: Make your changes manually
7. Feedback: Reject with reason "Optimization was too aggressive"
```

## Best Practices

### Setting Confidence Thresholds

- **Conservative (0.95)**: Only obvious fixes auto-apply
- **Balanced (0.90)**: Recommended default
- **Aggressive (0.80)**: Faster development, more risk
- **Manual (1.00)**: Always review every change

### Providing Good Feedback

**Do:**
- Explain why you rejected a change
- Rate suggestions honestly
- Provide specific improvement suggestions
- Review approval history regularly

**Don't:**
- Approve without reviewing
- Reject without reason
- Set threshold too low
- Ignore confidence scores

### Using Auto-Approval Safely

1. **Start conservative** - Begin with high threshold (0.95)
2. **Review history** - Check approval statistics regularly
3. **Adjust based on results** - Lower threshold if accurate
4. **Use for specific file types** - Different thresholds per project
5. **Always test** - Enable auto-run tests for safety

## Troubleshooting

### Code Not Being Generated

**Problem:** No modifications generated
**Solutions:**
- Ensure IPC server is running and connected
- Check that planning agents are available
- Verify LLM API key is configured
- Try more specific goals

### Auto-Approval Not Working

**Problem:** Changes always require approval
**Solutions:**
- Check threshold setting (must be < 1.0)
- Verify confidence scores (must exceed threshold)
- Review generated code confidence levels
- Lower threshold if appropriate

### Tests Failing After Application

**Problem:** Tests fail after code is applied
**Solutions:**
- Review the changes that were applied
- Check test output for specific errors
- Use "Review Pending Changes" before applying
- Set lower auto-approval threshold
- Provide feedback to improve future suggestions

### Feedback Not Being Saved

**Problem:** Feedback statistics show no data
**Solutions:**
- Ensure feedback collection is enabled
- Check workspace state storage
- Verify IPC connection for sync
- Use "Show Feedback Statistics" to verify

## Advanced Usage

### Custom Approval Workflows

You can customize the approval workflow by:

1. Setting different thresholds for different file types
2. Creating custom approval rules via settings
3. Using preview mode for all changes
4. Disabling auto-approval entirely

### Integration with Tests

Enable automatic testing after code application:

```json
{
  "director.autoRunTests": true
}
```

This will:
1. Apply approved code changes
2. Automatically run tests
3. Show results immediately
4. Request feedback if tests fail

### Feedback Analytics

Use feedback statistics to:
- Identify common rejection reasons
- Find problematic file patterns
- Measure approval success rate
- Improve threshold settings
- Train the AI on preferences

## Phase 2 vs Phase 1

| Feature | Phase 1 | Phase 2 |
|---------|---------|---------|
| Code Generation | ❌ | ✅ Automated |
| Code Application | ❌ | ✅ With approval |
| Testing | ❌ | ✅ Automated |
| Approval Workflow | ❌ | ✅ Intelligent |
| Feedback Loop | ❌ | ✅ Learning |
| Confidence Scoring | ❌ | ✅ Per-change |
| Auto-Approval | ❌ | ✅ Configurable |

## Future Enhancements (Phase 3)

Coming in Phase 3:
- 🚀 Fully autonomous development
- 🤖 Multi-agent collaboration
- 🔄 Continuous refactoring
- 📈 Performance optimization
- 🐛 Automatic bug detection
- 🧪 Test generation

## Support and Feedback

- **Issues**: [GitHub Issues](https://github.com/Mittenzx/Adastrea-Director/issues)
- **Documentation**: [Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki)
- **Feedback**: Use `Director: Provide Feedback` command

---

**Version**: 0.2.0  
**Phase**: 2 - Semi-Autonomous Development  
**Status**: ✅ Complete
