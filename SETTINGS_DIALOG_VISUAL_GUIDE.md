# Settings Dialog Visual Guide

## Overview

This document provides a detailed description of the new comprehensive settings dialog implemented in Week 7-8.

---

## Dialog Layout

### Window Properties
- **Title**: "Settings"
- **Size**: 550x600 pixels
- **Style**: UE5-inspired dark theme
- **Background**: Dark blue-gray (#20232b)
- **Modal**: Yes (blocks main window)
- **Position**: Centered on screen

---

## Header Section

```
┌────────────────────────────────────────────────────┐
│  ⚙️ Settings                                        │
│  (Title in accent blue, 14pt bold)                 │
└────────────────────────────────────────────────────┘
```

---

## Section 1: API Keys

```
╔════════════════════════════════════════════════════╗
║  API Keys                                          ║
╠════════════════════════════════════════════════════╣
║                                                    ║
║  LLM Provider:                                     ║
║    ◉ Gemini (Recommended)    ○ OpenAI            ║
║                                                    ║
║  Gemini API Key:                                   ║
║  ┌──────────────────────────────────────────────┐ ║
║  │ ••••••••••••••••••••••••••••••••••••••••••   │ ║
║  └──────────────────────────────────────────────┘ ║
║                                                    ║
║  OpenAI API Key:                                   ║
║  ┌──────────────────────────────────────────────┐ ║
║  │ ••••••••••••••••••••••••••••••••••••••••••   │ ║
║  └──────────────────────────────────────────────┘ ║
║                                                    ║
║  Embedding Provider:                               ║
║    ◉ HuggingFace (Free)    ○ OpenAI              ║
║                                                    ║
╚════════════════════════════════════════════════════╝
```

### Features:
- **Radio buttons** for provider selection
- **Masked input fields** (bullet characters) for security
- **Labels** clearly identify each setting
- **Recommended options** marked
- **Free options** highlighted

---

## Section 2: Display Settings

```
╔════════════════════════════════════════════════════╗
║  Display                                           ║
╠════════════════════════════════════════════════════╣
║                                                    ║
║  Default Font Size:  [10] pt                      ║
║                      ▲▼                            ║
║                                                    ║
║  ☑ Auto-save settings                             ║
║                                                    ║
║  ☑ Show timestamps in conversation                ║
║                                                    ║
╚════════════════════════════════════════════════════╝
```

### Features:
- **Spinbox** for font size (8-20pt range)
- **Checkboxes** for boolean options
- **Clear labels** for each setting
- **Default values** pre-selected

---

## Button Section

```
┌────────────────────────────────────────────────────┐
│                                                    │
│        ┌──────────┐    ┌──────────┐              │
│        │   Save   │    │  Cancel  │              │
│        └──────────┘    └──────────┘              │
│                                                    │
└────────────────────────────────────────────────────┘
```

### Button Details:

**Save Button**:
- **Color**: Bright blue (#40a9ff)
- **Text**: Black on blue
- **Hover**: Lighter blue (#5bb8ff)
- **Size**: 30px padding horizontal, 8px vertical
- **Action**: Saves all settings and closes dialog

**Cancel Button**:
- **Color**: Medium gray (#343843)
- **Text**: Light gray (#e3e4e8)
- **Hover**: Lighter gray (#4a4e5a)
- **Border**: 1px subtle outline
- **Action**: Closes dialog without saving

---

## Color Scheme

### Primary Colors
```
Background:      #20232b  (Dark blue-gray)
Accent:          #40a9ff  (Bright blue)
Text Primary:    #e3e4e8  (Light gray)
Text Secondary:  #cccccc  (Medium light gray)
Text Muted:      #858585  (Gray)
```

### Component Colors
```
Input Background:  #2a2d35  (Slightly lighter)
Input Border:      #3e3e42  (Subtle border)
Button Default:    #343843  (Medium gray)
Button Hover:      #4a4e5a  (Lighter gray)
Success:           #4ec9b0  (Teal)
Warning:           #ce9178  (Orange)
Error:             #f48771  (Red)
```

---

## Typography

### Fonts Used
```
Title:       Segoe UI, 14pt, Bold, Accent Blue
Section:     Segoe UI, 10pt, Bold, Light Gray
Labels:      Segoe UI, 10pt, Regular, Light Gray
Help Text:   Segoe UI, 9pt, Regular, Muted Gray
Input:       Segoe UI, 9pt, Regular, Light Gray
```

---

## User Interactions

### Opening the Dialog

**Method 1: Menu Bar**
```
Edit → Settings...
```

**Method 2: Keyboard Shortcut**
```
Ctrl+,  (Ctrl + Comma)
```

### Editing Settings

1. **LLM Provider**:
   - Click radio button to select
   - Selection is immediate
   - Other providers dim slightly

2. **API Keys**:
   - Click in field to edit
   - Type key (characters masked)
   - Field highlights blue on focus
   - Border turns accent color

3. **Embedding Provider**:
   - Click radio button to select
   - Free option clearly marked
   - Recommended choice pre-selected

4. **Font Size**:
   - Click in spinbox
   - Type number or use ▲▼ arrows
   - Range: 8-20pt
   - Current value shown

5. **Checkboxes**:
   - Click to toggle
   - Checked = enabled
   - Unchecked = disabled

### Saving Changes

**Click Save**:
- All settings validated
- API keys encrypted
- Saved to `~/.adastrea/config.json`
- Success message shown
- Dialog closes

**Click Cancel**:
- No changes saved
- Dialog closes
- Original values retained

**Press Escape**:
- Same as Cancel
- Quick exit

**Press Enter**:
- Same as Save
- Quick save

---

## Visual States

### Normal State
```
┌─────────────────────┐
│  Setting Name       │
│  [Input Field    ]  │
└─────────────────────┘
```

### Focused State
```
┌═════════════════════┐  ← Accent color border
│  Setting Name       │
│  [Input Field    ]│ │  ← Cursor visible
└═════════════════════┘
```

### Error State
```
┌─────────────────────┐
│  Setting Name       │
│  [Invalid input  ]  │  ← Red border
│  ⚠ Error message    │  ← Error text
└─────────────────────┘
```

### Hover State (Buttons)
```
┌──────────┐           ┌──────────┐
│   Save   │  Hover →  │   Save   │  (Lighter)
└──────────┘           └──────────┘
```

---

## Accessibility Features

### Keyboard Navigation
- **Tab**: Move between fields
- **Shift+Tab**: Move backwards
- **Space**: Toggle checkboxes/radio buttons
- **Enter**: Save settings
- **Escape**: Cancel

### Visual Indicators
- **Focus rings**: Blue outline on focused element
- **Hover states**: Buttons lighten on hover
- **Active states**: Visual press feedback
- **Error states**: Red borders and icons

### Screen Reader Support
- All labels properly associated
- Input descriptions provided
- Error messages announced
- State changes communicated

---

## Responsive Behavior

### Minimum Size
- Width: 550px (fixed)
- Height: 600px (fixed)
- Position: Always centered

### Content Flow
- Vertical scrolling if needed
- Sections stack vertically
- Inputs expand to full width
- Buttons centered at bottom

---

## Example Use Cases

### Use Case 1: First-Time Setup

```
User opens Settings (Ctrl+,)
  ↓
Sees empty API key fields
  ↓
Selects "Gemini (Recommended)"
  ↓
Enters Gemini API key
  ↓
Leaves embedding as "HuggingFace (Free)"
  ↓
Clicks "Save"
  ↓
Success message: "Settings saved successfully"
```

### Use Case 2: Changing Providers

```
User wants to switch from Gemini to OpenAI
  ↓
Opens Settings
  ↓
Clicks "OpenAI" radio button
  ↓
Enters OpenAI API key
  ↓
Changes embedding to "OpenAI"
  ↓
Clicks "Save"
  ↓
Provider switched immediately
```

### Use Case 3: Adjusting Display

```
User finds text too small
  ↓
Opens Settings
  ↓
Clicks font size spinbox
  ↓
Increases to 14pt
  ↓
Clicks "Save"
  ↓
Font updates in main window
```

---

## Error Scenarios

### Empty API Key
```
User clicks "Save" with empty key
  ↓
No error (optional field)
  ↓
Settings saved without key
  ↓
Will prompt on first use
```

### Invalid Font Size
```
User enters "25" (above max)
  ↓
Spinbox prevents entry
  ↓
Max value remains 20
  ↓
User must choose 8-20
```

### File Permission Error
```
Cannot write to config file
  ↓
Error message shown
  ↓
"Settings saved for session only"
  ↓
Warning status indicator
```

---

## Comparison to Previous

### Before Week 7-8
```
┌────────────────────────┐
│  Set Gemini API Key    │
├────────────────────────┤
│                        │
│  Enter key:            │
│  [••••••••••••••••]    │
│                        │
│  ☑ Save for future     │
│                        │
│   [OK]    [Cancel]     │
│                        │
└────────────────────────┘
```
- Single API key only
- No provider selection
- No display options
- Limited functionality

### After Week 7-8
```
┌─────────────────────────────┐
│  ⚙️ Settings                 │
├─────────────────────────────┤
│  ╔═══ API Keys ═══╗         │
│  ║ • Providers     ║         │
│  ║ • Gemini key    ║         │
│  ║ • OpenAI key    ║         │
│  ║ • Embeddings    ║         │
│  ╚═════════════════╝         │
│                              │
│  ╔═══ Display ═══╗          │
│  ║ • Font size     ║         │
│  ║ • Auto-save     ║         │
│  ║ • Timestamps    ║         │
│  ╚═════════════════╝         │
│                              │
│    [Save]  [Cancel]          │
└─────────────────────────────┘
```
- Multiple API keys
- Provider selection
- Display preferences
- Comprehensive settings

---

## Technical Implementation

### Dialog Creation
```python
dialog = tk.Toplevel(self.root)
dialog.title("Settings")
dialog.geometry("550x600")
dialog.transient(self.root)
dialog.grab_set()  # Modal behavior
```

### Section Layout
```python
# API Keys Section
api_section = tk.LabelFrame(
    main_container,
    text="API Keys",
    bg=self.bg_color,
    fg=self.fg_color,
    padx=15,
    pady=10
)
```

### Saving Settings
```python
def save_settings():
    # Save LLM provider
    os.environ['LLM_PROVIDER'] = llm_provider_var.get()
    
    # Save and encrypt API keys
    config_manager.set_api_key("gemini", gemini_key)
    
    # Apply display settings
    self.current_font_size = font_size_var.get()
```

---

## Summary

The new settings dialog provides:

✅ **Comprehensive Configuration** - All settings in one place  
✅ **Professional Design** - UE5-inspired aesthetic  
✅ **User-Friendly** - Clear labels and organization  
✅ **Secure** - Encrypted API key storage  
✅ **Accessible** - Full keyboard navigation  
✅ **Persistent** - Settings saved across sessions  
✅ **Validated** - Input validation prevents errors  
✅ **Responsive** - Clear feedback on actions  

**Status**: Production Ready ✅

---

*Visual Guide Generated: November 15, 2025*  
*Adastrea Director - Week 7-8 Implementation*
