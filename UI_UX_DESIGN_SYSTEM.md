# Adastrea Director - UI/UX Design System

## Overview

This document defines the comprehensive UI/UX design system for Adastrea Director, an AI-powered game development assistant. The design system ensures consistency, accessibility, and a professional user experience across all interfaces.

---

## Design Principles

### 1. **Clarity**
- Information should be clear and easy to understand
- Use familiar patterns and conventions
- Avoid unnecessary complexity

### 2. **Efficiency**
- Minimize steps required to complete tasks
- Provide keyboard shortcuts for power users
- Offer contextual help and tooltips

### 3. **Consistency**
- Maintain uniform appearance across all interfaces
- Use predictable interaction patterns
- Apply design tokens consistently

### 4. **Accessibility**
- Support keyboard navigation
- Provide adequate color contrast
- Offer adjustable font sizes
- Include visual and textual feedback

### 5. **Professionalism**
- Modern, polished appearance
- Reduced visual clutter
- Thoughtful use of color and typography

---

## Color System

### Primary Palette

#### Background Colors
```
Dark Background:     #1e1e1e  (Primary background)
Text Background:     #252526  (Input fields, text areas)
Button Background:   #2d2d30  (Buttons, controls)
Button Active:       #3e3e42  (Active/hover state)
```

#### Foreground Colors
```
Primary Text:        #e0e0e0  (Main text color)
Accent Color:        #007acc  (Brand color, links, emphasis)
White Text:          #ffffff  (High contrast text on accent)
```

#### Semantic Colors

**Success/Positive:**
```
Green:               #4ec9b0  (User messages, success states)
```

**Warning/Information:**
```
Orange:              #ce9178  (Assistant messages, info states)
Cyan:                #4ec9b0  (User input, interactive elements)
```

**Error/Danger:**
```
Red:                 #f48771  (Error messages, warnings)
```

**Neutral/Secondary:**
```
Gray:                #858585  (Timestamps, secondary text)
```

### Color Usage Guidelines

1. **Text on Dark Background**: Use `#e0e0e0` for primary text
2. **Emphasis**: Use `#007acc` for important elements
3. **Interactive Elements**: Use hover states with `#3e3e42`
4. **Status Indicators**: Use semantic colors (green for success, red for error)

### Contrast Requirements

- All text must meet WCAG AA standards (4.5:1 for normal text, 3:1 for large text)
- Interactive elements must be distinguishable from non-interactive elements
- Focus states must be clearly visible

---

## Typography

### Font Families

#### Interface Font
```
Primary: "Segoe UI", system-ui, -apple-system, sans-serif
Fallback: System default sans-serif
```

Use for:
- Headers and titles
- Labels and buttons
- Navigation and menus

#### Code/Monospace Font
```
Primary: "Consolas", "Monaco", "Courier New", monospace
Fallback: System default monospace
```

Use for:
- Code snippets
- Conversation history
- Technical output

### Type Scale

```
Large Title:     16pt  (bold)  - Main application title
Title:           14pt  (bold)  - Section headers
Subtitle:        11pt  (bold)  - Subsection headers
Body Large:      11pt          - Input fields, prominent text
Body:            10pt          - Standard body text, conversation
Body Small:      9pt           - Labels, tertiary text
Caption:         8pt           - Timestamps, metadata
```

### Typography Guidelines

1. **Hierarchy**: Use size and weight to establish hierarchy
2. **Line Height**: Maintain 1.4-1.6 line height for readability
3. **Letter Spacing**: Use default spacing; adjust only for headings if needed
4. **Bold Usage**: Use bold sparingly for emphasis
5. **Alignment**: Left-align text for optimal readability

---

## Spacing System

### Base Unit: 5px

Our spacing system uses a 5px base unit for consistency.

```
XXS:  5px   (0.25rem)  - Tight spacing within components
XS:   10px  (0.5rem)   - Default padding in small elements
S:    15px  (0.75rem)  - Standard padding in frames
M:    20px  (1rem)     - Spacing between sections
L:    30px  (1.5rem)   - Large gaps between major sections
XL:   40px  (2rem)     - Extra large spacing
XXL:  60px  (3rem)     - Maximum spacing
```

### Spacing Guidelines

1. **Padding**: Use XS-S (10-15px) for internal component padding
2. **Margins**: Use M-L (20-30px) between distinct sections
3. **Button Spacing**: 10px horizontal gap between buttons
4. **Vertical Rhythm**: Maintain consistent 15-20px spacing between elements
5. **Frame Padding**: Use 15px for main frame padding

---

## Components

### Buttons

#### Primary Button
- **Purpose**: Main call-to-action
- **Background**: `#007acc` (accent color)
- **Text**: `#ffffff` (white)
- **Font**: Segoe UI, 11pt, bold
- **Padding**: 25px horizontal, 8px vertical
- **Border Radius**: 0px (flat design)
- **Hover**: `#005a9e` (darker blue)
- **Example**: "Ask" button

```python
{
    "font": ("Segoe UI", 11, "bold"),
    "bg": "#007acc",
    "fg": "white",
    "activebackground": "#005a9e",
    "activeforeground": "white",
    "relief": tk.FLAT,
    "padx": 25,
    "pady": 8,
    "cursor": "hand2"
}
```

#### Secondary Button
- **Purpose**: Supporting actions
- **Background**: `#2d2d30` (button background)
- **Text**: `#e0e0e0` (primary text)
- **Font**: Segoe UI, 10pt
- **Padding**: 15px horizontal, 8px vertical
- **Border Radius**: 0px (flat design)
- **Hover**: `#3e3e42` (button active)
- **Example**: "Update Knowledge Base", "Set API Key"

```python
{
    "font": ("Segoe UI", 10),
    "bg": "#2d2d30",
    "fg": "#e0e0e0",
    "activebackground": "#3e3e42",
    "activeforeground": "#e0e0e0",
    "relief": tk.FLAT,
    "padx": 15,
    "pady": 8,
    "cursor": "hand2"
}
```

#### Button States
- **Normal**: Default appearance
- **Hover**: Slightly lighter background
- **Active/Pressed**: Visual feedback on click
- **Disabled**: Reduced opacity (50%), no cursor change

#### Button Best Practices
1. Use icons (emoji) for quick recognition
2. Provide tooltips with keyboard shortcuts
3. Make primary actions prominent
4. Group related buttons together
5. Maintain consistent button height

### Input Fields

#### Text Entry Field
- **Background**: `#252526` (text background)
- **Text**: `#e0e0e0` (primary text)
- **Font**: Segoe UI, 11pt
- **Border**: 1px, `#2d2d30` (button background)
- **Focus Border**: 1px, `#007acc` (accent color)
- **Padding**: 8px vertical, 5px horizontal
- **Border Radius**: 0px (flat design)

```python
{
    "font": ("Segoe UI", 11),
    "bg": "#252526",
    "fg": "#e0e0e0",
    "insertbackground": "#e0e0e0",
    "relief": tk.FLAT,
    "highlightthickness": 1,
    "highlightbackground": "#2d2d30",
    "highlightcolor": "#007acc"
}
```

#### Input Field Guidelines
1. Clear focus states with accent color border
2. Placeholder text in secondary color
3. Auto-clear after submission for convenience
4. Support keyboard shortcuts (Enter to submit)
5. Provide visual feedback on validation

### Text Display Areas

#### Scrolled Text Area
- **Background**: `#252526` (text background)
- **Text**: `#e0e0e0` (primary text)
- **Font**: Consolas, 10pt (monospace)
- **Padding**: 10px internal padding
- **Border**: None (flat design)
- **Scrollbar**: System default

```python
{
    "wrap": tk.WORD,
    "state": tk.DISABLED,
    "bg": "#252526",
    "fg": "#e0e0e0",
    "insertbackground": "#e0e0e0",
    "font": ("Consolas", 10),
    "relief": tk.FLAT,
    "padx": 10,
    "pady": 10
}
```

#### Text Tags (for formatted content)
```python
user_tag = {
    "foreground": "#4ec9b0",
    "font": ("Segoe UI", 10, "bold")
}

assistant_tag = {
    "foreground": "#ce9178"
}

timestamp_tag = {
    "foreground": "#858585",
    "font": ("Segoe UI", 8)
}

error_tag = {
    "foreground": "#f48771"
}
```

### Status Bar

#### Design
- **Background**: `#2d2d30` (button background)
- **Text**: `#e0e0e0` (primary text)
- **Font**: Segoe UI, 9pt
- **Height**: Auto (based on content)
- **Padding**: 10px horizontal, 5px vertical
- **Position**: Bottom of window

#### Status Messages
- **Ready**: "✓ Ready. [Description]"
- **Processing**: "🤔 Processing..."
- **Success**: "✓ Success: [Message]"
- **Error**: "❌ Error: [Message]"

#### Status Bar Guidelines
1. Always provide clear feedback
2. Use emoji icons for quick recognition
3. Keep messages concise but informative
4. Update in real-time during operations

### Tooltips

#### Design
- **Background**: `#2d2d30` with slight transparency
- **Text**: `#e0e0e0`
- **Font**: Segoe UI, 9pt
- **Border**: 1px solid `#3e3e42`
- **Padding**: 5px
- **Border Radius**: 3px (slightly rounded)

#### Tooltip Content
- Short description of element function
- Keyboard shortcut (if applicable)
- Max 2 lines of text

#### Tooltip Guidelines
1. Provide tooltips for all interactive elements
2. Show on hover after 500ms delay
3. Include keyboard shortcuts in parentheses
4. Use clear, action-oriented language

### Dialogs

#### Modal Dialog
- **Background**: `#2d2d30` (button background)
- **Text**: `#e0e0e0` (primary text)
- **Border**: 1px solid `#3e3e42`
- **Title Bar**: Accent color bar or bold title
- **Padding**: 20px
- **Buttons**: Standard button styles

#### Dialog Types

**API Key Dialog:**
- Password-masked input field
- OK/Cancel buttons
- Centered on screen
- Modal (blocks main window)

**About Dialog:**
- Application name and version
- Brief description
- Credits/attribution
- Close button

**Export Dialog:**
- File format options
- File name input
- Save location picker
- Save/Cancel buttons

#### Dialog Guidelines
1. Center dialogs on parent window
2. Make dialogs modal for important actions
3. Support Escape key to cancel
4. Support Enter key to confirm
5. Provide clear action buttons

### Menu Bar

#### Design
- **Background**: `#2d2d30` (button background)
- **Text**: `#e0e0e0` (primary text)
- **Active Background**: `#3e3e42` (button active)
- **Font**: Segoe UI, 10pt

#### Menu Structure

```
File
├── Export Conversation...  (Ctrl+E)
├── ─────────────────────
└── Exit                   (Alt+F4)

Edit
├── Copy Response          (Ctrl+C)
├── Clear Conversation     (Ctrl+L)
├── ─────────────────────
└── Set API Key           (Ctrl+K)

Help
├── Keyboard Shortcuts
└── About
```

#### Menu Guidelines
1. Group related actions together
2. Use separators to divide sections
3. Show keyboard shortcuts
4. Keep menu depth to 2 levels maximum

---

## Iconography

### Icon System

We use emoji icons for quick recognition and universal compatibility.

#### Icon Mapping

```
🤖  Application/AI/Assistant
📚  Knowledge/Documents/Library
🔑  Security/API Key/Authentication
❓  Question/Help/Query
💬  Conversation/Chat/Message
🗑️  Delete/Clear/Remove
📋  Copy/Clipboard
▶   Execute/Run/Send
✓   Success/Complete/OK
❌  Error/Fail/Cancel
🤔  Processing/Thinking/Working
⚠️  Warning/Caution
```

#### Icon Guidelines
1. Use consistent icons for same actions across interface
2. Place icons before text labels
3. Ensure icons are recognizable at small sizes
4. Use emoji for cross-platform compatibility
5. Don't rely solely on color to convey meaning

---

## Layout

### Window Structure

```
┌─────────────────────────────────────────┐
│ Menu Bar                                 │
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │ Header (Title + Subtitle)           │ │
│ ├─────────────────────────────────────┤ │
│ │ Action Buttons + Font Controls      │ │
│ ├─────────────────────────────────────┤ │
│ │                                     │ │
│ │ Conversation Display Area           │ │
│ │ (Scrollable)                        │ │
│ │                                     │ │
│ ├─────────────────────────────────────┤ │
│ │ Question Input + Ask Button         │ │
│ └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ Status Bar                               │
└─────────────────────────────────────────┘
```

### Window Specifications

```
Default Size:     1000x700px
Minimum Size:     800x600px
Resizable:        Yes
Position:         Centered on screen
Background:       #1e1e1e (dark background)
```

### Layout Guidelines

1. **Visual Hierarchy**: Header → Actions → Content → Input → Status
2. **Frame Padding**: 15px around main content
3. **Section Spacing**: 15px between major sections
4. **Button Groups**: 10px spacing between buttons
5. **Expansion**: Conversation area expands to fill available space

---

## Interaction Patterns

### Keyboard Shortcuts

#### Primary Actions
```
Enter / Ctrl+Enter    Send question
Ctrl+K                Set API Key
Ctrl+U                Update knowledge base
Ctrl+L                Clear conversation
Ctrl+C                Copy last response
Ctrl+E                Export conversation
```

#### Navigation
```
Tab                   Move to next field
Shift+Tab             Move to previous field
Escape                Cancel dialog
Alt+F4                Exit application
```

#### Accessibility
```
A-                    Decrease font size
A+                    Increase font size
```

### Mouse Interactions

#### Hover States
- Buttons: Lighten background color
- Links: Show underline
- Tooltips: Display after 500ms

#### Click States
- Buttons: Brief darker background flash
- Input fields: Show focus border
- Text selection: Standard OS selection color

#### Cursor Types
- **Hand/Pointer**: Buttons, links, clickable elements
- **Text/I-beam**: Input fields, text areas
- **Arrow/Default**: Non-interactive areas

### Focus Management

1. **Initial Focus**: Question input field on launch
2. **After Submit**: Return focus to input field
3. **Dialog Focus**: First input field or primary button
4. **Tab Order**: Logical left-to-right, top-to-bottom
5. **Focus Indicators**: Accent color border on focused elements

---

## Accessibility

### WCAG 2.1 Compliance

#### Level AA Requirements

**Contrast Ratios:**
- Normal text (10-11pt): 4.5:1 minimum
- Large text (14pt+): 3:1 minimum
- UI components: 3:1 minimum

**Text:**
- Resizable without loss of functionality
- Line height minimum 1.5x font size
- Paragraph spacing minimum 2x font size

**Navigation:**
- All functionality available via keyboard
- Focus order is logical and intuitive
- Focus indicators are visible

#### Current Compliance

✓ Color contrast meets AA standards
✓ All interactive elements keyboard accessible
✓ Font size adjustable (8pt to 20pt)
✓ Clear focus indicators
✓ Logical tab order
✓ Tooltips provide additional context

### Accessibility Features

1. **Keyboard Navigation**: Full support for all actions
2. **Font Size Control**: Adjustable text size
3. **High Contrast**: Dark theme with sufficient contrast
4. **Screen Reader Support**: Proper labeling and structure
5. **Focus Management**: Clear, visible focus states
6. **Alternative Text**: Icons accompanied by text labels

---

## Animation & Transitions

### Current Approach

The current design prioritizes instant feedback and clarity over decorative animations. This approach:
- Reduces complexity
- Improves performance
- Ensures accessibility
- Provides immediate feedback

### Future Considerations

If animations are added, they should be:

```
Duration:        150-300ms (fast, subtle)
Easing:          ease-out for entrances
                 ease-in for exits
Types:           Fade, slide, scale
Purpose:         Provide feedback, guide attention
Option:          Respect system "reduce motion" settings
```

### Animation Guidelines (if implemented)

1. Keep animations subtle and purposeful
2. Never delay user actions with animations
3. Provide option to disable animations
4. Use consistent timing across all animations
5. Test with accessibility tools

---

## Responsive Design

### Window Resizing

The application supports window resizing with these behaviors:

**Minimum Size**: 800x600px
- Ensures all controls remain usable
- Prevents layout breaking
- Maintains readability

**Resize Behavior**:
- Conversation area expands/contracts vertically
- All elements maintain proper spacing
- Text wraps appropriately
- Scrollbars appear when needed

### Adaptive Elements

1. **Conversation Display**: Expands to fill available vertical space
2. **Input Field**: Stretches to fill horizontal space
3. **Buttons**: Fixed size, maintain spacing
4. **Status Bar**: Full width, fixed height
5. **Scrollbars**: Appear automatically when content exceeds viewport

---

## Best Practices

### General Guidelines

1. **Consistency**: Use design tokens consistently throughout
2. **Clarity**: Make actions and states obvious
3. **Feedback**: Provide immediate, clear feedback for all actions
4. **Efficiency**: Minimize clicks and keystrokes required
5. **Forgiveness**: Make actions reversible when possible

### Code Implementation

```python
# Define color scheme
colors = {
    "bg": "#1e1e1e",
    "fg": "#e0e0e0",
    "accent": "#007acc",
    "button_bg": "#2d2d30",
    "button_active": "#3e3e42",
    "text_bg": "#252526"
}

# Define typography
fonts = {
    "title": ("Segoe UI", 16, "bold"),
    "subtitle": ("Segoe UI", 11, "bold"),
    "body": ("Segoe UI", 10),
    "code": ("Consolas", 10)
}

# Define spacing
spacing = {
    "xxs": 5,
    "xs": 10,
    "s": 15,
    "m": 20,
    "l": 30,
    "xl": 40
}

# Use design tokens
frame = tk.Frame(root, bg=colors["bg"], padx=spacing["s"])
```

### Testing Checklist

- [ ] All text meets contrast requirements
- [ ] All actions accessible via keyboard
- [ ] All interactive elements have tooltips
- [ ] Focus states are clearly visible
- [ ] Window resizes gracefully
- [ ] Font size controls work properly
- [ ] Status bar updates appropriately
- [ ] Error messages are clear and helpful
- [ ] Buttons provide visual feedback
- [ ] Dialogs are modal and centered

---

## Resources

### Design Tools

- **Color Palette**: Use existing color scheme defined above
- **Typography**: System fonts (Segoe UI, Consolas)
- **Icons**: Emoji (universal compatibility)
- **Layout**: Tkinter (Python GUI framework)

### External References

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design](https://material.io/) - For general UI principles
- [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/) - For interaction patterns
- [Microsoft Fluent Design](https://www.microsoft.com/design/fluent/) - For Windows-like appearance

### Related Documentation

- [GUI Improvements](GUI_IMPROVEMENTS.md) - Detailed feature documentation
- [GUI Visual Comparison](GUI_VISUAL_COMPARISON.md) - Before/after comparison
- [GUI Quick Start](GUI_QUICK_START.md) - User guide
- [Project Plan](PROJECT_PLAN.md) - Overall project roadmap

---

## Future Enhancements

### Phase 2 Considerations

As the project evolves, consider:

1. **Web Interface**: Adapt design system for web technologies
2. **Mobile Support**: Responsive design for mobile devices
3. **Theming**: Light theme option, custom themes
4. **Customization**: User-adjustable color schemes
5. **Advanced Components**: Charts, graphs, visualizations

### Ongoing Improvements

- Gather user feedback on usability
- Conduct accessibility audits
- Monitor design trends
- Refine based on usage patterns
- Update documentation as design evolves

---

## Version History

| Version | Date       | Changes                                    |
|---------|------------|-------------------------------------------|
| 1.0     | 2025-11-08 | Initial design system documentation       |

---

## Contact

For design system questions or suggestions:
- Open an issue on GitHub
- Reference this document in design discussions
- Propose changes via pull requests

---

*Last Updated: 2025-11-08*
*Maintained by: Adastrea Director Team*
