# Adastrea Director - Visual Design Guide

## Overview

This visual design guide provides detailed specifications and examples for implementing the Adastrea Director UI. It complements the [UI/UX Design System](UI_UX_DESIGN_SYSTEM.md) with visual examples and practical implementation guidance.

---

## Quick Reference

### Color Swatches

```
███ #1e1e1e  Dark Background    (Main background)
███ #252526  Text Background    (Input fields)
███ #2d2d30  Button Background  (Buttons)
███ #3e3e42  Button Active      (Hover state)
███ #007acc  Accent Color       (Primary actions)
███ #e0e0e0  Primary Text       (Main text)
███ #4ec9b0  User Color         (User messages)
███ #ce9178  Assistant Color    (Assistant messages)
███ #858585  Secondary Text     (Timestamps)
███ #f48771  Error Color        (Error messages)
```

### Typography Scale

```
16pt  █████████████████  Large Title
14pt  ████████████████   Title
11pt  █████████████      Subtitle / Body Large
10pt  ████████████       Body
9pt   ███████████        Body Small
8pt   ██████████         Caption
```

---

## Component Specifications

### 1. Window Layout

```
┌────────────────────────────────────────────────────────┐
│ File  Edit  Help                                       │  Menu (24px)
├────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────┐ │
│ │  🤖 Adastrea Director   AI Game Development Assistant │  Header (60px)
│ └────────────────────────────────────────────────────┘ │
│ ┌────────────────────────────────────────────────────┐ │
│ │ 📚 Update KB  🔑 Set Key  🗑️ Clear  📋 Copy    A- A+ │  Actions (50px)
│ └────────────────────────────────────────────────────┘ │
│ ┌────────────────────────────────────────────────────┐ │
│ │ 💬 Conversation                                    │ │  Label (30px)
│ ├────────────────────────────────────────────────────┤ │
│ │                                                    │ │
│ │  [Conversation content scrolls here]               │ │  Content (flex)
│ │                                                    │ │
│ ├────────────────────────────────────────────────────┤ │
│ │ ❓ Your Question:                                  │ │  Label (30px)
│ ├────────────────────────────────────────────────────┤ │
│ │ [Type your question here...]        [Ask ▶]       │ │  Input (60px)
│ └────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────┤
│ ✓ Ready. Please set your OpenAI API Key if you haven't │  Status (30px)
└────────────────────────────────────────────────────────┘

Total: 1000x700px (min 800x600px)
```

### 2. Button Specifications

#### Primary Button (Ask)

```
┌─────────────────────┐
│      Ask ▶          │  Height: 44px
└─────────────────────┘  Width: Auto (content + padding)

Colors:
  Background: #007acc
  Text: #ffffff
  Hover: #005a9e
  
Typography:
  Font: Segoe UI, 11pt, Bold
  
Spacing:
  Padding: 25px horizontal, 8px vertical
  Margin: 10px from input field
```

#### Secondary Button (Actions)

```
┌───────────────────────────┐
│  📚 Update Knowledge Base  │  Height: 40px
└───────────────────────────┘  Width: Auto (content + padding)

Colors:
  Background: #2d2d30
  Text: #e0e0e0
  Hover: #3e3e42
  
Typography:
  Font: Segoe UI, 10pt
  
Spacing:
  Padding: 15px horizontal, 8px vertical
  Margin: 10px right
```

#### Small Button (Font Controls)

```
┌─────┐
│ A+  │  Height: 32px
└─────┘  Width: Auto (content + padding)

Colors:
  Background: #2d2d30
  Text: #e0e0e0
  Hover: #3e3e42
  
Typography:
  Font: Segoe UI, 9pt
  
Spacing:
  Padding: 8px horizontal, 4px vertical
  Margin: 5px between controls
```

### 3. Input Field Specifications

#### Text Entry Field

```
┌──────────────────────────────────────────────────────┐
│ Type your question here...                           │  Height: 44px
└──────────────────────────────────────────────────────┘  Width: Flex (fills space)

States:
  Normal:
    Background: #252526
    Border: 1px solid #2d2d30
    Text: #e0e0e0
    
  Focus:
    Background: #252526
    Border: 1px solid #007acc
    Text: #e0e0e0
    
  Disabled:
    Background: #1e1e1e
    Border: 1px solid #2d2d30
    Text: #858585
    
Typography:
  Font: Segoe UI, 11pt
  
Spacing:
  Padding: 8px vertical, 5px horizontal
  Margin: 10px right of button
```

### 4. Text Display Area

#### Conversation Display

```
┌────────────────────────────────────────────────────┐
│ [12:34:56] You:                                    │
│ What is the main gameplay loop?                    │
│                                                    │
│ [12:35:01] Assistant:                             │
│ Based on the game design documents, the main      │
│ gameplay loop involves...                         │
│                                                    │
│ [Scrollable content continues...]                 │
└────────────────────────────────────────────────────┘

Colors:
  Background: #252526
  User text: #4ec9b0 (bold)
  Assistant text: #ce9178
  Timestamp: #858585
  Error: #f48771
  
Typography:
  Font: Consolas, 10pt (monospace)
  Line height: 1.5
  
Spacing:
  Padding: 10px internal
  Margin: 5px between messages
```

### 5. Status Bar

```
┌────────────────────────────────────────────────────┐
│ ✓ Ready. Please set your OpenAI API Key if you... │  Height: 30px
└────────────────────────────────────────────────────┘  Width: Full width

Colors:
  Background: #2d2d30
  Text: #e0e0e0
  
Typography:
  Font: Segoe UI, 9pt
  
Spacing:
  Padding: 10px horizontal, 5px vertical
```

### 6. Dialog Specifications

#### API Key Dialog

```
┌────────────────────────────────────┐
│  Set OpenAI API Key                │  Title bar
├────────────────────────────────────┤
│                                    │
│  Enter your API key:               │  20px padding
│  ┌──────────────────────────────┐ │
│  │ ••••••••••••••••••••••••••••• │ │  Password field
│  └──────────────────────────────┘ │
│                                    │
│         ┌─────┐      ┌─────┐     │
│         │ OK  │      │Cancel│     │  Buttons
│         └─────┘      └─────┘     │
│                                    │
└────────────────────────────────────┘

Size: 400x200px (centered)
Modal: Yes (blocks main window)
```

---

## Message Formatting Examples

### User Message

```
┌────────────────────────────────────────────────────┐
│ [12:34:56] You:                                    │  Timestamp (gray)
│ What is the main gameplay loop?                    │  Message (cyan, bold)
└────────────────────────────────────────────────────┘
```

### Assistant Message

```
┌────────────────────────────────────────────────────┐
│ [12:35:01] Assistant:                             │  Timestamp (gray)
│ Based on the game design documents, the main      │  Message (orange)
│ gameplay loop involves exploration, combat, and   │
│ resource gathering. Players will...               │
└────────────────────────────────────────────────────┘
```

### System Message

```
┌────────────────────────────────────────────────────┐
│ [12:35:15] System:                                │  Timestamp (gray)
│ API key has been set successfully.                │  Message (gray)
└────────────────────────────────────────────────────┘
```

### Error Message

```
┌────────────────────────────────────────────────────┐
│ [12:35:30] Error:                                 │  Timestamp (gray)
│ Failed to connect to OpenAI API. Please check     │  Message (red)
│ your API key and internet connection.             │
└────────────────────────────────────────────────────┘
```

---

## Welcome Message Design

```
┌────────────────────────────────────────────────────┐
│ [12:30:00] System:                                │
│ Welcome to Adastrea Director! 🎮                  │
│                                                    │
│ Getting Started:                                  │
│ 1. Set your OpenAI API key (🔑 button or Ctrl+K) │
│ 2. Update knowledge base (📚 button or Ctrl+U)   │
│ 3. Ask questions about your project               │
│                                                    │
│ Example Questions:                                │
│ • "What is the main gameplay loop?"               │
│ • "Describe the player character abilities"      │
│ • "What are the technical requirements?"         │
│                                                    │
│ Keyboard Shortcuts:                               │
│ • Enter/Ctrl+Enter - Send question                │
│ • Ctrl+K - Set API Key                           │
│ • Ctrl+U - Update knowledge base                 │
│ • Ctrl+L - Clear conversation                     │
│                                                    │
│ For more shortcuts, see Help > Keyboard Shortcuts │
└────────────────────────────────────────────────────┘
```

---

## Tooltip Examples

```
Hover over button:
┌──────────────────────────────────────────┐
│ 📚 Update Knowledge Base                 │  Button
└──────────────────────────────────────────┘
           ↓
    ┌─────────────────────────────────────────┐
    │ Load and process project documents      │  Tooltip
    │ (Ctrl+U)                                 │
    └─────────────────────────────────────────┘
```

---

## Responsive Behavior

### Large Window (1200x800)

```
┌─────────────────────────────────────────────────────────┐
│ Menu Bar                                                 │
├─────────────────────────────────────────────────────────┤
│ Header                                                   │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Actions                                              │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │                                                      │ │
│ │                                                      │ │
│ │ Conversation (More visible content)                 │ │
│ │                                                      │ │
│ │                                                      │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │ Input                                                │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ Status Bar                                               │
└─────────────────────────────────────────────────────────┘
```

### Minimum Window (800x600)

```
┌──────────────────────────────────────────┐
│ Menu Bar                                  │
├──────────────────────────────────────────┤
│ Header                                    │
│ ┌──────────────────────────────────────┐ │
│ │ Actions (wraps if needed)            │ │
│ ├──────────────────────────────────────┤ │
│ │                                      │ │
│ │ Conversation (scrollable)            │ │
│ │                                      │ │
│ ├──────────────────────────────────────┤ │
│ │ Input                                │ │
│ └──────────────────────────────────────┘ │
├──────────────────────────────────────────┤
│ Status Bar                                │
└──────────────────────────────────────────┘
```

---

## State Diagrams

### Application States

```
┌──────────┐
│  Start   │
└────┬─────┘
     │
     ▼
┌──────────────┐     ┌──────────────┐
│ API Key Set? │────>│ Show Welcome │
└──────┬───────┘ No  └──────────────┘
       │ Yes
       ▼
┌──────────────┐     ┌──────────────┐
│    Ready     │<───>│  Processing  │
└──────────────┘     └──────────────┘
       │                     │
       ▼                     ▼
┌──────────────┐     ┌──────────────┐
│   Success    │     │    Error     │
└──────────────┘     └──────────────┘
```

### Button States

```
┌────────┐  hover   ┌────────┐  click   ┌────────┐  release ┌────────┐
│ Normal │ ──────>  │ Hover  │ ──────>  │ Active │ ──────>  │ Normal │
└────────┘          └────────┘          └────────┘          └────────┘
    │                                                             │
    └─────────────────────────────────────────────────────────┘
```

---

## Interaction Flows

### Asking a Question

```
User types question
         │
         ▼
User clicks "Ask" or presses Enter
         │
         ▼
Input field clears
         │
         ▼
Status: "🤔 Processing..."
         │
         ▼
Question appears in conversation (cyan)
         │
         ▼
API call to backend
         │
         ├──> Success
         │         │
         │         ▼
         │    Response appears (orange)
         │         │
         │         ▼
         │    Status: "✓ Ready"
         │         │
         │         ▼
         │    Focus returns to input
         │
         └──> Error
                   │
                   ▼
              Error message appears (red)
                   │
                   ▼
              Status: "❌ Error: [details]"
                   │
                   ▼
              Focus returns to input
```

### Setting API Key

```
User clicks "🔑 Set API Key" or presses Ctrl+K
         │
         ▼
Dialog appears (centered, modal)
         │
         ▼
User enters API key (masked)
         │
         ├──> User clicks OK or presses Enter
         │         │
         │         ▼
         │    Key is saved
         │         │
         │         ▼
         │    Dialog closes
         │         │
         │         ▼
         │    System message: "API key set"
         │         │
         │         ▼
         │    Status: "✓ Ready"
         │
         └──> User clicks Cancel or presses Escape
                   │
                   ▼
              Dialog closes
                   │
                   ▼
              No changes made
```

---

## Typography Hierarchy Example

```
🤖 Adastrea Director                         ← 16pt Bold (Title)
   AI Game Development Assistant             ← 10pt Regular (Subtitle)

💬 Conversation                               ← 11pt Bold (Section Header)

   [12:34:56] You:                           ← 8pt Regular (Timestamp)
   What is the main gameplay loop?           ← 10pt Bold (User Message)
   
   [12:35:01] Assistant:                     ← 8pt Regular (Timestamp)
   Based on the game design documents...     ← 10pt Regular (Assistant Message)

❓ Your Question:                             ← 11pt Bold (Section Header)
   [Type here...]                            ← 11pt Regular (Input)

✓ Ready. Please set your OpenAI API Key...   ← 9pt Regular (Status)
```

---

## Color Application Examples

### Light on Dark (Primary Pattern)

```
Background: #1e1e1e
      ┌────────────────────────────────────┐
      │                                    │
      │  Text: #e0e0e0                     │
      │                                    │
      │  ┌────────────────────────┐       │
      │  │ Input: #252526         │       │
      │  │ Text: #e0e0e0          │       │
      │  └────────────────────────┘       │
      │                                    │
      │  ┌─────────┐                      │
      │  │ Button  │  #2d2d30             │
      │  │ #e0e0e0 │                      │
      │  └─────────┘                      │
      │                                    │
      └────────────────────────────────────┘
```

### Accent Color Usage

```
Primary Action (Ask Button):
┌─────────────┐
│   #007acc   │  Background
│   #ffffff   │  Text
└─────────────┘

Hover State:
┌─────────────┐
│   #005a9e   │  Darker blue
│   #ffffff   │  Text
└─────────────┘

Focus Indicator:
┌─────────────────┐
│                 │
│  Input Field    │  1px border: #007acc
│                 │
└─────────────────┘
```

### Semantic Colors in Context

```
Success Message:
✓ Knowledge base updated successfully.
  └── Green icon, gray text

Processing:
🤔 Processing your question...
   └── Thinking icon, gray text

Error Message:
❌ Error: Failed to connect to API
   └── Red icon, red text

User Message:
You: What is the player health system?
└── Cyan text, bold

Assistant Message:
Assistant: The player health system uses...
└── Orange text, regular
```

---

## Measurement Reference

### Standard Measurements

```
┌─────────────────────────────────────┐
│ ← 15px padding →                    │  Frame padding
│                                     │
│ Element 1                           │
│ ↕ 15px                              │  Between sections
│ Element 2                           │
│                                     │
│ ┌─────────┐ ↔ 10px ← ┌─────────┐  │  Button spacing
│ │ Button1 │          │ Button2 │  │
│ └─────────┘          └─────────┘  │
│                                     │
│ ← 8px → Text ← 8px →               │  Button padding (vertical)
│         ↕                           │
│        8px                          │  Button padding (horizontal)
│                                     │
└─────────────────────────────────────┘
```

### Vertical Rhythm

```
┌──────────────────────────────────┐
│ Header (60px)                    │  Fixed height
├──────────────────────────────────┤
│ Actions (50px)                   │  Fixed height
├──────────────────────────────────┤
│                                  │
│ Conversation (flex)              │  Grows to fill space
│                                  │
├──────────────────────────────────┤
│ Input (60px)                     │  Fixed height
├──────────────────────────────────┤
│ Status (30px)                    │  Fixed height
└──────────────────────────────────┘
```

---

## Platform Considerations

### Windows

- Uses Segoe UI font (native)
- Window controls in top-right
- Alt+F4 to close
- Standard window decorations

### macOS

- Segoe UI falls back to system font
- Window controls in top-left
- Cmd+Q to quit
- Native window style

### Linux

- Font fallback to system sans-serif
- Window controls vary by desktop environment
- Alt+F4 or Ctrl+Q to close
- Theme respects system settings

---

## Implementation Checklist

### Basic Structure
- [ ] Window with correct dimensions (1000x700)
- [ ] Minimum size constraint (800x600)
- [ ] Dark background color (#1e1e1e)
- [ ] Proper padding (15px)

### Header
- [ ] Title with correct font (Segoe UI, 16pt, bold)
- [ ] Subtitle with correct font (Segoe UI, 10pt)
- [ ] Accent color for title (#007acc)
- [ ] Proper spacing

### Action Buttons
- [ ] Update Knowledge Base button
- [ ] Set API Key button
- [ ] Clear Conversation button
- [ ] Copy Response button
- [ ] Font size controls (A-, A+)
- [ ] Consistent styling
- [ ] Tooltips on all buttons

### Conversation Area
- [ ] Scrollable text widget
- [ ] Dark background (#252526)
- [ ] Proper padding (10px)
- [ ] Text tags configured:
  - [ ] User (cyan, bold)
  - [ ] Assistant (orange)
  - [ ] Timestamp (gray, small)
  - [ ] Error (red)
- [ ] Monospace font (Consolas)

### Input Section
- [ ] Label with icon
- [ ] Text entry field with proper styling
- [ ] Focus indicator (accent color border)
- [ ] Ask button (accent background)
- [ ] Enter key binding
- [ ] Ctrl+Enter key binding

### Status Bar
- [ ] Bottom position
- [ ] Full width
- [ ] Proper background color
- [ ] Emoji status indicators
- [ ] Updates with actions

### Menu Bar
- [ ] File menu with Export and Exit
- [ ] Edit menu with Copy, Clear, Set API Key
- [ ] Help menu with Shortcuts and About
- [ ] Keyboard shortcuts displayed

### Keyboard Shortcuts
- [ ] Ctrl+K - Set API Key
- [ ] Ctrl+U - Update Knowledge Base
- [ ] Ctrl+L - Clear Conversation
- [ ] Ctrl+C - Copy Response
- [ ] Ctrl+E - Export Conversation
- [ ] Enter - Submit question
- [ ] Ctrl+Enter - Submit question

### Accessibility
- [ ] All interactive elements keyboard accessible
- [ ] Logical tab order
- [ ] Focus indicators visible
- [ ] Font size adjustable
- [ ] Color contrast meets WCAG AA

---

## Design Tokens Reference

Quick copy-paste for implementation:

```python
# Colors
COLORS = {
    'bg_dark': '#1e1e1e',
    'bg_text': '#252526',
    'bg_button': '#2d2d30',
    'bg_button_active': '#3e3e42',
    'fg_primary': '#e0e0e0',
    'fg_accent': '#007acc',
    'fg_accent_hover': '#005a9e',
    'fg_user': '#4ec9b0',
    'fg_assistant': '#ce9178',
    'fg_secondary': '#858585',
    'fg_error': '#f48771',
    'fg_white': '#ffffff'
}

# Typography
FONTS = {
    'title': ('Segoe UI', 16, 'bold'),
    'subtitle': ('Segoe UI', 11, 'bold'),
    'body_large': ('Segoe UI', 11),
    'body': ('Segoe UI', 10),
    'body_small': ('Segoe UI', 9),
    'caption': ('Segoe UI', 8),
    'code': ('Consolas', 10)
}

# Spacing
SPACING = {
    'xxs': 5,
    'xs': 10,
    's': 15,
    'm': 20,
    'l': 30,
    'xl': 40,
    'xxl': 60
}

# Dimensions
DIMENSIONS = {
    'window_width': 1000,
    'window_height': 700,
    'window_min_width': 800,
    'window_min_height': 600,
    'button_height': 40,
    'input_height': 44,
    'status_height': 30
}
```

---

## Conclusion

This visual design guide provides the necessary specifications for implementing a consistent, professional UI for Adastrea Director. Follow these guidelines to ensure a cohesive user experience.

For complete design principles and additional information, refer to:
- [UI/UX Design System](UI_UX_DESIGN_SYSTEM.md)
- [GUI Improvements](GUI_IMPROVEMENTS.md)
- [Project Plan](PROJECT_PLAN.md)

---

*Last Updated: 2025-11-08*
*Version: 1.0*
