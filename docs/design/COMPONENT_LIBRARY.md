# Adastrea Director - Component Library

## Overview

This component library provides reusable UI components for the Adastrea Director application. Each component is documented with specifications, code examples, and usage guidelines.

---

## Table of Contents

1. [Buttons](#buttons)
2. [Input Fields](#input-fields)
3. [Text Display](#text-display)
4. [Dialogs](#dialogs)
5. [Status Bar](#status-bar)
6. [Menus](#menus)
7. [Tooltips](#tooltips)
8. [Frames & Containers](#frames--containers)

---

## Buttons

### Primary Button

**Purpose**: Main call-to-action buttons

**Visual Appearance**:
- Background: Accent color (#007acc)
- Text: White (#ffffff)
- Bold, prominent styling

**Code Example**:

```python
primary_button = tk.Button(
    parent,
    text="Ask ▶",
    command=callback_function,
    font=("Segoe UI", 11, "bold"),
    bg="#007acc",
    fg="white",
    activebackground="#005a9e",
    activeforeground="white",
    relief=tk.FLAT,
    padx=25,
    pady=8,
    cursor="hand2"
)
primary_button.pack(side=tk.RIGHT)
```

**Usage Guidelines**:
- Use for primary actions only (one per section)
- Keep text short and action-oriented
- Include icon (emoji) for quick recognition

**Variations**:
- Default state: Accent color background
- Hover state: Darker accent color (#005a9e)
- Disabled state: Reduced opacity (not implemented yet)

---

### Secondary Button

**Purpose**: Supporting actions, less critical operations

**Visual Appearance**:
- Background: Button background color (#2d2d30)
- Text: Primary text color (#e0e0e0)
- Standard weight styling

**Code Example**:

```python
secondary_button_style = {
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

secondary_button = tk.Button(
    parent,
    text="📚 Update Knowledge Base",
    command=callback_function,
    **secondary_button_style
)
secondary_button.pack(side=tk.LEFT, padx=(0, 10))
```

**Usage Guidelines**:
- Use for supporting actions
- Group related buttons together
- Always include tooltips
- Maintain 10px spacing between buttons

**Variations**:
- Default state: Button background
- Hover state: Slightly lighter (#3e3e42)

---

### Small Button

**Purpose**: Compact controls (font size, minor actions)

**Visual Appearance**:
- Same colors as secondary button
- Smaller font (9pt)
- Less padding

**Code Example**:

```python
small_button = tk.Button(
    parent,
    text="A+",
    command=callback_function,
    font=("Segoe UI", 9),
    bg="#2d2d30",
    fg="#e0e0e0",
    activebackground="#3e3e42",
    relief=tk.FLAT,
    padx=8,
    pady=4,
    cursor="hand2"
)
small_button.pack(side=tk.LEFT, padx=(0, 5))
```

**Usage Guidelines**:
- Use for utility controls
- Keep text very short (2-3 characters or single icon)
- Group with related controls

---

### Button Helper Functions

```python
def create_primary_button(parent, text, command, icon=""):
    """Create a primary action button with consistent styling."""
    button_text = f"{icon} {text}" if icon else text
    return tk.Button(
        parent,
        text=button_text,
        command=command,
        font=("Segoe UI", 11, "bold"),
        bg="#007acc",
        fg="white",
        activebackground="#005a9e",
        activeforeground="white",
        relief=tk.FLAT,
        padx=25,
        pady=8,
        cursor="hand2"
    )

def create_secondary_button(parent, text, command, icon=""):
    """Create a secondary action button with consistent styling."""
    button_text = f"{icon} {text}" if icon else text
    return tk.Button(
        parent,
        text=button_text,
        command=command,
        font=("Segoe UI", 10),
        bg="#2d2d30",
        fg="#e0e0e0",
        activebackground="#3e3e42",
        activeforeground="#e0e0e0",
        relief=tk.FLAT,
        padx=15,
        pady=8,
        cursor="hand2"
    )
```

---

## Input Fields

### Text Entry Field

**Purpose**: Single-line text input

**Visual Appearance**:
- Dark background (#252526)
- Light text (#e0e0e0)
- Accent color focus border (#007acc)

**Code Example**:

```python
entry_field = tk.Entry(
    parent,
    font=("Segoe UI", 11),
    bg="#252526",
    fg="#e0e0e0",
    insertbackground="#e0e0e0",  # Cursor color
    relief=tk.FLAT,
    highlightthickness=1,
    highlightbackground="#2d2d30",  # Unfocused border
    highlightcolor="#007acc"  # Focused border
)
entry_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=8, ipadx=5)

# Bind keyboard shortcuts
entry_field.bind("<Return>", callback_function)
entry_field.bind("<Control-Return>", callback_function)
```

**Usage Guidelines**:
- Use for short text input (questions, API keys, etc.)
- Bind Enter key for submission
- Clear field after successful submission
- Return focus after operations

**Helper Function**:

```python
def create_entry_field(parent, placeholder="", on_return=None):
    """Create a styled text entry field."""
    entry = tk.Entry(
        parent,
        font=("Segoe UI", 11),
        bg="#252526",
        fg="#e0e0e0",
        insertbackground="#e0e0e0",
        relief=tk.FLAT,
        highlightthickness=1,
        highlightbackground="#2d2d30",
        highlightcolor="#007acc"
    )
    
    if on_return:
        entry.bind("<Return>", on_return)
        entry.bind("<Control-Return>", on_return)
    
    return entry
```

---

### Password Entry Field

**Purpose**: Masked text input for sensitive data

**Code Example**:

```python
password_entry = tk.Entry(
    parent,
    font=("Segoe UI", 11),
    bg="#252526",
    fg="#e0e0e0",
    insertbackground="#e0e0e0",
    relief=tk.FLAT,
    highlightthickness=1,
    highlightbackground="#2d2d30",
    highlightcolor="#007acc",
    show="•"  # Mask character
)
password_entry.pack(fill=tk.X, pady=10)
```

**Usage Guidelines**:
- Use for API keys, passwords
- Always mask input with `show="•"`
- Provide clear labeling

---

## Text Display

### Scrolled Text Widget

**Purpose**: Multi-line, read-only text display

**Visual Appearance**:
- Dark background (#252526)
- Light text (#e0e0e0)
- Scrollable when content exceeds viewport

**Code Example**:

```python
from tkinter import scrolledtext

text_display = scrolledtext.ScrolledText(
    parent,
    wrap=tk.WORD,
    height=20,
    state=tk.DISABLED,  # Read-only
    bg="#252526",
    fg="#e0e0e0",
    insertbackground="#e0e0e0",
    font=("Consolas", 10),
    relief=tk.FLAT,
    padx=10,
    pady=10
)
text_display.pack(fill=tk.BOTH, expand=True)

# Configure text tags for formatting
text_display.tag_config("user", foreground="#4ec9b0", font=("Segoe UI", 10, "bold"))
text_display.tag_config("assistant", foreground="#ce9178")
text_display.tag_config("timestamp", foreground="#858585", font=("Segoe UI", 8))
text_display.tag_config("error", foreground="#f48771")
```

**Usage Guidelines**:
- Set state to DISABLED for read-only display
- Enable temporarily when adding content
- Use tags for syntax highlighting/formatting
- Auto-scroll to bottom after updates

**Helper Functions**:

```python
def append_to_text_widget(widget, text, tag=None):
    """Append text to a scrolled text widget with optional tag."""
    widget.config(state=tk.NORMAL)
    if tag:
        widget.insert(tk.END, text, tag)
    else:
        widget.insert(tk.END, text)
    widget.config(state=tk.DISABLED)
    widget.see(tk.END)  # Scroll to bottom

def clear_text_widget(widget):
    """Clear all content from a text widget."""
    widget.config(state=tk.NORMAL)
    widget.delete(1.0, tk.END)
    widget.config(state=tk.DISABLED)
```

---

### Label

**Purpose**: Static text display

**Code Example**:

```python
# Section header
header_label = tk.Label(
    parent,
    text="💬 Conversation",
    font=("Segoe UI", 11, "bold"),
    bg="#1e1e1e",
    fg="#e0e0e0"
)
header_label.pack(side=tk.LEFT)

# Regular label
regular_label = tk.Label(
    parent,
    text="Your Question:",
    font=("Segoe UI", 10),
    bg="#1e1e1e",
    fg="#e0e0e0"
)
regular_label.pack(side=tk.LEFT, padx=(0, 5))
```

**Usage Guidelines**:
- Use for section headers and static text
- Match background color to parent
- Use appropriate font size for hierarchy

---

## Dialogs

### Custom Dialog Base

**Purpose**: Modal dialog windows

**Code Example**:

```python
class CustomDialog:
    """Base class for custom dialogs."""
    
    def __init__(self, parent, title, width=400, height=200):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.transient(parent)  # Keep on top of parent
        self.dialog.grab_set()  # Modal behavior
        
        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Styling
        self.dialog.configure(bg="#2d2d30")
        
        # Result
        self.result = None
        
    def wait(self):
        """Wait for dialog to close and return result."""
        self.dialog.wait_window()
        return self.result
```

---

### API Key Dialog

**Purpose**: Secure API key input

**Code Example**:

```python
class APIKeyDialog(CustomDialog):
    """Dialog for setting API key."""
    
    def __init__(self, parent):
        super().__init__(parent, "Set OpenAI API Key", 400, 200)
        
        # Content frame
        content_frame = tk.Frame(self.dialog, bg="#2d2d30", padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label
        label = tk.Label(
            content_frame,
            text="Enter your OpenAI API key:",
            font=("Segoe UI", 10),
            bg="#2d2d30",
            fg="#e0e0e0"
        )
        label.pack(pady=(0, 10))
        
        # Entry field
        self.entry = tk.Entry(
            content_frame,
            font=("Segoe UI", 11),
            bg="#252526",
            fg="#e0e0e0",
            insertbackground="#e0e0e0",
            relief=tk.FLAT,
            show="•"  # Masked input
        )
        self.entry.pack(fill=tk.X, pady=(0, 20))
        self.entry.focus()
        self.entry.bind("<Return>", lambda e: self.on_ok())
        self.entry.bind("<Escape>", lambda e: self.on_cancel())
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg="#2d2d30")
        button_frame.pack()
        
        ok_button = tk.Button(
            button_frame,
            text="OK",
            command=self.on_ok,
            font=("Segoe UI", 10),
            bg="#007acc",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor="hand2"
        )
        ok_button.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=self.on_cancel,
            font=("Segoe UI", 10),
            bg="#2d2d30",
            fg="#e0e0e0",
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor="hand2"
        )
        cancel_button.pack(side=tk.LEFT)
    
    def on_ok(self):
        """Handle OK button click."""
        self.result = self.entry.get().strip()
        self.dialog.destroy()
    
    def on_cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.dialog.destroy()
```

**Usage**:

```python
dialog = APIKeyDialog(root)
api_key = dialog.wait()
if api_key:
    # Use the API key
    pass
```

---

### Message Dialog

**Purpose**: Simple information display

**Code Example**:

```python
# Use tkinter's built-in message boxes with custom styling
from tkinter import messagebox

def show_info(title, message):
    """Show info message."""
    messagebox.showinfo(title, message)

def show_warning(title, message):
    """Show warning message."""
    messagebox.showwarning(title, message)

def show_error(title, message):
    """Show error message."""
    messagebox.showerror(title, message)

def ask_yes_no(title, message):
    """Ask yes/no question."""
    return messagebox.askyesno(title, message)
```

---

## Status Bar

**Purpose**: Display application status

**Code Example**:

```python
class StatusBar:
    """Status bar component."""
    
    def __init__(self, parent):
        self.status_var = tk.StringVar()
        self.status_var.set("✓ Ready")
        
        self.bar = tk.Label(
            parent,
            textvariable=self.status_var,
            bd=1,
            relief=tk.FLAT,
            anchor=tk.W,
            bg="#2d2d30",
            fg="#e0e0e0",
            font=("Segoe UI", 9),
            padx=10,
            pady=5
        )
        self.bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def set_status(self, message, icon="✓"):
        """Update status with icon."""
        self.status_var.set(f"{icon} {message}")
    
    def set_ready(self, message="Ready"):
        """Set ready status."""
        self.set_status(message, "✓")
    
    def set_processing(self, message="Processing..."):
        """Set processing status."""
        self.set_status(message, "🤔")
    
    def set_error(self, message):
        """Set error status."""
        self.set_status(message, "❌")
    
    def set_success(self, message):
        """Set success status."""
        self.set_status(message, "✓")
```

**Usage**:

```python
status_bar = StatusBar(root)
status_bar.set_processing("Loading documents...")
# ... do work ...
status_bar.set_success("Documents loaded successfully")
```

---

## Menus

### Menu Bar

**Purpose**: Application menu system

**Code Example**:

```python
def create_menu_bar(root, callbacks):
    """Create application menu bar."""
    menubar = Menu(root, bg="#2d2d30", fg="#e0e0e0")
    root.config(menu=menubar)
    
    # File menu
    file_menu = Menu(menubar, tearoff=0, bg="#2d2d30", fg="#e0e0e0")
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(
        label="Export Conversation...",
        command=callbacks['export'],
        accelerator="Ctrl+E"
    )
    file_menu.add_separator()
    file_menu.add_command(
        label="Exit",
        command=root.quit,
        accelerator="Alt+F4"
    )
    
    # Edit menu
    edit_menu = Menu(menubar, tearoff=0, bg="#2d2d30", fg="#e0e0e0")
    menubar.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(
        label="Copy Response",
        command=callbacks['copy'],
        accelerator="Ctrl+C"
    )
    edit_menu.add_command(
        label="Clear Conversation",
        command=callbacks['clear'],
        accelerator="Ctrl+L"
    )
    edit_menu.add_separator()
    edit_menu.add_command(
        label="Set API Key",
        command=callbacks['set_api_key'],
        accelerator="Ctrl+K"
    )
    
    # Help menu
    help_menu = Menu(menubar, tearoff=0, bg="#2d2d30", fg="#e0e0e0")
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="Keyboard Shortcuts", command=callbacks['shortcuts'])
    help_menu.add_command(label="About", command=callbacks['about'])
    
    return menubar
```

**Usage**:

```python
callbacks = {
    'export': export_conversation,
    'copy': copy_response,
    'clear': clear_conversation,
    'set_api_key': set_api_key,
    'shortcuts': show_shortcuts,
    'about': show_about
}
menu = create_menu_bar(root, callbacks)
```

---

## Tooltips

**Purpose**: Contextual help on hover

**Code Example**:

```python
class ToolTip:
    """Tooltip component."""
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        
        # Bind events
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """Show tooltip after delay."""
        if self.tooltip:
            return
        
        # Create tooltip window
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip = tk.Toplevel()
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Tooltip content
        label = tk.Label(
            self.tooltip,
            text=self.text,
            background="#2d2d30",
            foreground="#e0e0e0",
            font=("Segoe UI", 9),
            relief=tk.SOLID,
            borderwidth=1,
            padx=5,
            pady=3
        )
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Hide tooltip."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def create_tooltip(widget, text):
    """Helper function to create tooltip."""
    return ToolTip(widget, text)
```

**Usage**:

```python
button = tk.Button(parent, text="Click Me")
create_tooltip(button, "This button does something (Ctrl+X)")
```

---

## Frames & Containers

### Styled Frame

**Purpose**: Container with consistent styling

**Code Example**:

```python
def create_frame(parent, padding=15):
    """Create a styled frame."""
    frame = tk.Frame(
        parent,
        bg="#1e1e1e",
        padx=padding,
        pady=padding
    )
    return frame

def create_section_frame(parent, title, icon=""):
    """Create a section with header."""
    # Main frame
    section = tk.Frame(parent, bg="#1e1e1e")
    
    # Header
    header = tk.Frame(section, bg="#1e1e1e")
    header.pack(fill=tk.X, pady=(0, 5))
    
    title_text = f"{icon} {title}" if icon else title
    label = tk.Label(
        header,
        text=title_text,
        font=("Segoe UI", 11, "bold"),
        bg="#1e1e1e",
        fg="#e0e0e0"
    )
    label.pack(side=tk.LEFT)
    
    # Content frame
    content = tk.Frame(section, bg="#1e1e1e")
    content.pack(fill=tk.BOTH, expand=True)
    
    return section, content
```

**Usage**:

```python
section, content = create_section_frame(parent, "Conversation", "💬")
section.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

# Add widgets to content frame
text_widget = create_text_display(content)
text_widget.pack(fill=tk.BOTH, expand=True)
```

---

## Complete Example

Here's how to combine components to create a simple interface:

```python
import tkinter as tk
from tkinter import scrolledtext

class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple App")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")
        
        # Main frame
        main_frame = create_frame(root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Label(
            main_frame,
            text="🤖 My Application",
            font=("Segoe UI", 16, "bold"),
            bg="#1e1e1e",
            fg="#007acc"
        )
        header.pack(pady=(0, 15))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        btn1 = create_secondary_button(
            button_frame, "Action 1", self.action1, "📚"
        )
        btn1.pack(side=tk.LEFT, padx=(0, 10))
        
        btn2 = create_secondary_button(
            button_frame, "Action 2", self.action2, "🔑"
        )
        btn2.pack(side=tk.LEFT)
        
        # Content section
        section, content = create_section_frame(main_frame, "Content", "💬")
        section.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.text_display = scrolledtext.ScrolledText(
            content,
            wrap=tk.WORD,
            height=20,
            state=tk.DISABLED,
            bg="#252526",
            fg="#e0e0e0",
            font=("Consolas", 10),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.text_display.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        input_section, input_content = create_section_frame(
            main_frame, "Input", "❓"
        )
        input_section.pack(fill=tk.X)
        
        input_frame = tk.Frame(input_content, bg="#1e1e1e")
        input_frame.pack(fill=tk.X)
        
        self.entry = create_entry_field(input_frame, on_return=self.submit)
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=8, ipadx=5)
        
        submit_btn = create_primary_button(input_frame, "Submit", self.submit, "▶")
        submit_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Status bar
        self.status = StatusBar(root)
        self.status.set_ready("Application ready")
    
    def action1(self):
        self.status.set_processing("Performing action 1...")
        # Do something
        self.status.set_success("Action 1 completed")
    
    def action2(self):
        self.status.set_processing("Performing action 2...")
        # Do something
        self.status.set_success("Action 2 completed")
    
    def submit(self, event=None):
        text = self.entry.get().strip()
        if not text:
            return
        
        append_to_text_widget(self.text_display, f"Input: {text}\n")
        self.entry.delete(0, tk.END)
        self.status.set_success("Input processed")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()
```

---

## Best Practices

### Component Creation

1. **Consistency**: Use design tokens for all styling
2. **Reusability**: Create helper functions for common components
3. **Accessibility**: Include keyboard support and focus management
4. **Documentation**: Add docstrings to all helper functions

### Styling

1. **Colors**: Use defined color palette
2. **Typography**: Follow type scale
3. **Spacing**: Use spacing system (5px increments)
4. **Flat Design**: Use `relief=tk.FLAT` for modern appearance

### Interaction

1. **Feedback**: Provide visual feedback for all interactions
2. **States**: Implement hover and active states
3. **Cursors**: Use appropriate cursor types
4. **Tooltips**: Add tooltips to all interactive elements

### Performance

1. **Updates**: Batch text widget updates
2. **State Management**: Use DISABLED state for read-only widgets
3. **Memory**: Clean up unused widgets
4. **Threading**: Run long operations in background threads

---

## Related Documentation

- [UI/UX Design System](UI_UX_DESIGN_SYSTEM.md) - Complete design system
- [Design Guide](DESIGN_GUIDE.md) - Visual specifications
- [GUI Improvements](GUI_IMPROVEMENTS.md) - Implementation details

---

*Last Updated: 2025-11-08*
*Version: 1.0*
