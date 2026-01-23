# Manual Testing Checklist

This checklist should be completed by a human tester with access to a real Unreal Engine project and API keys.

## Pre-Test Setup

### Environment Setup
- [ ] Unreal Engine 5.x installed and working
- [ ] Adastrea Director plugin installed in a test project
- [ ] Valid Google Gemini API key available
- [ ] Valid OpenAI API key available (optional, for provider switching tests)

### Project Configuration
- [ ] Test project has been created or opened
- [ ] Plugin is enabled in the project
- [ ] No existing `.env` file in project root (will create fresh)

## Test Suite

### Test 1: No .env File (Error Handling)

**Objective**: Verify plugin provides helpful error messages when .env is missing

**Steps**:
1. [ ] Ensure no `.env` file exists in project root
2. [ ] Start Unreal Engine and open test project
3. [ ] Open Adastrea Director panel
4. [ ] Open Settings dialog
5. [ ] Click "Test API Key" button

**Expected Results**:
- [ ] Should show error: "❌ No API key found for gemini"
- [ ] Error message should include instructions to create .env file
- [ ] Error message should specify environment variable name (GEMINI_API_KEY)

**Steps (continued)**:
6. [ ] Close Settings
7. [ ] Type a query in the main panel: "What is Unreal Engine?"
8. [ ] Click Send Query or press Enter

**Expected Results**:
- [ ] Should show configuration error message (not stuck at "Thinking...")
- [ ] Error should mention missing API key
- [ ] Error should guide user to configure .env file
- [ ] Should include "Please configure your API key in Settings"

---

### Test 2: Create .env with Gemini Key

**Objective**: Verify .env file creation and Gemini key loading

**Steps**:
1. [ ] In project root, copy `.env.example` to `.env`
2. [ ] Edit `.env` and add: `GEMINI_API_KEY=your-actual-key-here`
3. [ ] Save the file
4. [ ] **Important**: Restart Unreal Engine completely
5. [ ] Open test project
6. [ ] Open Settings dialog
7. [ ] Click "Test API Key" button

**Expected Results**:
- [ ] Should show success: "✓ API key loaded: AIza...4567" (or similar masked key)
- [ ] Should state: "Key format appears valid"
- [ ] Should suggest: "Test with a query to verify it works with the API"
- [ ] Masked key should show first 8 and last 4 characters (or less if short key)

---

### Test 3: Query with Valid Configuration

**Objective**: Verify queries work end-to-end with configured API key

**Steps**:
1. [ ] With .env file configured and UE restarted (from Test 2)
2. [ ] Open Adastrea Director panel
3. [ ] Type a simple query: "What is Unreal Engine?"
4. [ ] Click Send Query or press Enter
5. [ ] Observe the response area

**Expected Results**:
- [ ] Should show "⏳ Thinking..." initially
- [ ] Should transition to showing actual AI response (not stuck)
- [ ] Response should be formatted with header and footer
- [ ] Should include the original query at bottom
- [ ] No error messages should appear

**Test Variations**:
6. [ ] Try another query: "Explain Blueprint scripting"
7. [ ] Try a longer query with multiple sentences
8. [ ] Try a technical question about C++ in UE

**Expected Results**:
- [ ] All queries should complete successfully
- [ ] Responses should be relevant to the queries
- [ ] No "Thinking..." hang-ups

---

### Test 4: API Key Priority (Legacy Variables)

**Objective**: Verify priority order for Gemini key variables

**Setup**: Edit `.env` file to test priority

**Test 4a: GEMINI_API_KEY (Primary)**
1. [ ] Edit `.env`: `GEMINI_API_KEY=primary_key_test`
2. [ ] Restart Unreal Engine
3. [ ] Settings → Test API Key
4. [ ] Should show masked version of "primary_key_test"

**Test 4b: GEMINI_KEY (Legacy)**
1. [ ] Edit `.env`: Remove GEMINI_API_KEY, add `GEMINI_KEY=legacy_key_test`
2. [ ] Restart Unreal Engine
3. [ ] Settings → Test API Key
4. [ ] Should show masked version of "legacy_key_test"

**Test 4c: GOOGLE_API_KEY (Fallback)**
1. [ ] Edit `.env`: Remove GEMINI_KEY, add `GOOGLE_API_KEY=fallback_key_test`
2. [ ] Restart Unreal Engine
3. [ ] Settings → Test API Key
4. [ ] Should show masked version of "fallback_key_test"

**Test 4d: Multiple Keys (Priority)**
1. [ ] Edit `.env`: Add all three keys with different values
   ```
   GEMINI_API_KEY=primary
   GEMINI_KEY=secondary
   GOOGLE_API_KEY=tertiary
   ```
2. [ ] Restart Unreal Engine
3. [ ] Settings → Test API Key
4. [ ] Should show masked version of "primary" (highest priority)

---

### Test 5: Provider Switching (OpenAI)

**Objective**: Verify OpenAI provider works correctly

**Prerequisite**: Valid OpenAI API key

**Steps**:
1. [ ] Edit `.env`: Add `OPENAI_API_KEY=your-openai-key-here`
2. [ ] Restart Unreal Engine
3. [ ] Open Settings dialog
4. [ ] Change provider from "Gemini (Recommended)" to "OpenAI"
5. [ ] Click Save
6. [ ] Click "Test API Key"

**Expected Results**:
- [ ] Should show: "✓ API key loaded: sk-...xxxx"
- [ ] Masked key should show OpenAI key format

**Steps (continued)**:
7. [ ] Close Settings
8. [ ] Type query: "What is Unreal Engine?"
9. [ ] Send query

**Expected Results**:
- [ ] Query should complete successfully
- [ ] Response should come from OpenAI (GPT model)
- [ ] No errors or "Thinking..." hang

---

### Test 6: Case Insensitivity

**Objective**: Verify provider names work regardless of case

**Test 6a: Lowercase in config**
1. [ ] Check `Saved/AdastreaDirector/config.ini`
2. [ ] Should contain: `LLMProvider=gemini` (lowercase)
3. [ ] Open Settings → Verify Gemini is selected
4. [ ] Test API Key → Should work

**Test 6b: Mixed case handling**
1. [ ] Manually edit config.ini: `LLMProvider=Gemini` (capital G)
2. [ ] Restart Unreal Engine
3. [ ] Test API Key → Should still work
4. [ ] Send a query → Should work (not "Unknown provider" error)

---

### Test 7: Edge Cases

**Test 7a: Short API Key**
1. [ ] Edit `.env`: `GEMINI_API_KEY=short` (less than 12 characters)
2. [ ] Restart Unreal Engine
3. [ ] Settings → Test API Key

**Expected Results**:
- [ ] Should show masked key: "shor..." (not crash)
- [ ] Should handle gracefully without string index errors

**Test 7b: Empty API Key**
1. [ ] Edit `.env`: `GEMINI_API_KEY=` (empty value)
2. [ ] Restart Unreal Engine
3. [ ] Settings → Test API Key

**Expected Results**:
- [ ] Should show "❌ No API key found for gemini"
- [ ] Should provide configuration instructions

**Test 7c: Whitespace in Key**
1. [ ] Edit `.env`: `GEMINI_API_KEY=  key_with_spaces  ` (spaces before/after)
2. [ ] Restart Unreal Engine
3. [ ] Settings → Test API Key

**Expected Results**:
- [ ] Should show masked key without leading/trailing spaces
- [ ] Whitespace should be trimmed automatically

**Test 7d: Invalid Provider**
1. [ ] Manually edit config.ini: `LLMProvider=invalid_provider`
2. [ ] Restart Unreal Engine
3. [ ] Try to send a query

**Expected Results**:
- [ ] Should show validation error
- [ ] Error should list valid providers: "gemini, openai"

---

### Test 8: Configuration Changes

**Test 8a: Runtime changes (should NOT work)**
1. [ ] Start UE with valid .env
2. [ ] Edit .env file (change API key)
3. [ ] Do NOT restart UE
4. [ ] Settings → Test API Key

**Expected Results**:
- [ ] Should show OLD key (changes not detected)
- [ ] This confirms keys are loaded at startup only

**Test 8b: After restart (should work)**
1. [ ] Restart Unreal Engine
2. [ ] Settings → Test API Key

**Expected Results**:
- [ ] Should show NEW key from edited .env
- [ ] This confirms restart applies changes

---

### Test 9: Security Verification

**Objective**: Verify API keys are not exposed in logs or UI

**Steps**:
1. [ ] With valid API key configured
2. [ ] Open Output Log window
3. [ ] Send a query
4. [ ] Review Output Log for any key exposure

**Expected Results**:
- [ ] Full API key should NOT appear in logs
- [ ] Only masked version should appear (if any)
- [ ] No security warnings about exposed keys

---

### Test 10: Documentation Verification

**Objective**: Verify documentation is accurate and helpful

**Steps**:
1. [ ] Read `API_KEY_CONFIGURATION.md`
2. [ ] Follow the Quick Start section step-by-step
3. [ ] Verify all instructions work as described
4. [ ] Check troubleshooting section matches actual errors

**Expected Results**:
- [ ] All instructions should be accurate
- [ ] Links should work
- [ ] Examples should match actual behavior
- [ ] Error messages in docs match actual error messages

---

## Test Summary

### Pass/Fail Criteria

**Must Pass** (Critical):
- [ ] Test 1: Error handling without .env
- [ ] Test 2: .env file creation and key loading
- [ ] Test 3: Queries work with valid configuration
- [ ] Test 4d: Priority order works correctly
- [ ] Test 7a: Short keys don't crash

**Should Pass** (Important):
- [ ] Test 4: All legacy variable names work
- [ ] Test 5: OpenAI provider works
- [ ] Test 6: Case insensitivity works
- [ ] Test 7b-d: Edge cases handled gracefully
- [ ] Test 9: No security issues

**Nice to Have**:
- [ ] Test 8: Configuration change behavior documented
- [ ] Test 10: Documentation accurate

### Test Results

**Test Date**: _________________

**Tested By**: _________________

**UE Version**: _________________

**Plugin Version**: _________________

**Overall Result**: ⬜ PASS / ⬜ FAIL / ⬜ PARTIAL

**Notes**:
```
(Add any observations, issues found, or suggestions here)






```

### Issues Found

| Test # | Issue Description | Severity | Status |
|--------|------------------|----------|--------|
| | | | |
| | | | |
| | | | |

**Severity Levels**:
- **Critical**: Prevents basic functionality
- **Major**: Significantly impacts user experience
- **Minor**: Cosmetic or edge case issue
- **Enhancement**: Suggested improvement

---

## Follow-Up Actions

After completing manual tests:

1. [ ] Document any bugs found in GitHub issues
2. [ ] Update documentation if instructions are unclear
3. [ ] Consider adding automated tests for critical paths
4. [ ] Update this checklist based on testing experience
5. [ ] Share test results with development team

---

## Automated Testing Considerations

**Potential Automated Tests** (for future):
- Unit test for .env file parsing
- Integration test for settings validation
- Mock HTTP test for LLM client
- UI automation test for Settings dialog

**Currently Tested**:
- ✅ .env parsing logic (C++ standalone test)

**Not Currently Tested** (requires UE environment):
- ⏳ Full plugin integration
- ⏳ UI interactions
- ⏳ LLM client communication
