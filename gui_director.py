import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu, font
import subprocess
import threading
import sys
import os
from datetime import datetime

# --- Configuration ---
# Path to the python executable running this script.
# This ensures we use the same Python environment where all the dependencies are installed.
PYTHON_EXECUTABLE = sys.executable

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class AdastreaDirectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Adastrea Director - AI Game Development Assistant")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Enhanced color scheme - Professional dark theme with better contrast
        self.bg_color = "#1e1e1e"           # Primary background
        self.bg_secondary = "#252526"       # Secondary background (panels)
        self.bg_tertiary = "#2d2d30"        # Tertiary background (cards)
        self.fg_color = "#e0e0e0"           # Primary text
        self.fg_secondary = "#cccccc"       # Secondary text
        self.fg_muted = "#858585"           # Muted/disabled text
        self.accent_color = "#007acc"       # Primary accent (blue)
        self.accent_hover = "#1e8ad6"       # Accent hover state (lighter blue)
        self.accent_active = "#005a9e"      # Accent active state (darker blue)
        self.button_bg = "#2d2d30"          # Button background
        self.button_hover = "#3e3e42"       # Button hover
        self.button_active = "#4e4e52"      # Button active/pressed
        self.text_bg = "#252526"            # Input/text areas
        self.border_color = "#3e3e42"       # Border color
        self.success_color = "#4ec9b0"      # Success/positive
        self.warning_color = "#ce9178"      # Warning/info
        self.error_color = "#f48771"        # Error/danger
        self.highlight_bg = "#094771"       # Selection/highlight background
        # Unreal Engine inspired color scheme
        self.bg_color = "#20232b"  # UE5 background panel (darker, blueish)
        self.fg_color = "#e3e4e8"  # UE5 text color (light gray, slightly warm)
        self.accent_color = "#40a9ff"  # UE5 toolbar/button highlight (bright blue)
        self.button_bg = "#343843"  # UE5 button default (medium gray-blue)
        self.button_active = "#4a4e5a"  # Lighter variant for hover
        self.text_bg = "#2a2d35"  # Slightly lighter than background for input areas
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Conversation history
        self.conversation_history = []
        
        # Create menu bar
        self.create_menu_bar()

        # --- Main Frame ---
        main_frame = tk.Frame(root, padx=15, pady=15, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Header Frame with Card Design ---
        header_card = tk.Frame(main_frame, bg=self.bg_tertiary, highlightthickness=1, 
                              highlightbackground=self.border_color)
        header_card.pack(fill=tk.X, pady=(0, 15))
        
        header_inner = tk.Frame(header_card, bg=self.bg_tertiary, padx=15, pady=12)
        header_inner.pack(fill=tk.BOTH, expand=True)
        
        # Title with icon
        title_frame = tk.Frame(header_inner, bg=self.bg_tertiary)
        title_frame.pack(side=tk.LEFT)
        # --- Header Frame with UE5-style border separator ---
        header_frame = tk.Frame(main_frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 8))
        
        title_label = tk.Label(
            title_frame,
            text="⚡ Adastrea Director",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_tertiary,
            fg=self.accent_color
        )
        title_label.pack(side=tk.LEFT)
        
        # Divider
        divider = tk.Frame(header_inner, width=2, bg=self.border_color)
        divider.pack(side=tk.LEFT, fill=tk.Y, padx=15)
        
        # Subtitle and status
        info_frame = tk.Frame(header_inner, bg=self.bg_tertiary)
        info_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        subtitle_label = tk.Label(
            info_frame,
            text="AI-Powered Game Development Assistant",
            font=("Segoe UI", 11),
            bg=self.bg_tertiary,
            fg=self.fg_secondary
        )
        subtitle_label.pack(anchor=tk.W)
        
        self.header_status_label = tk.Label(
            info_frame,
            text="● Ready",
            font=("Segoe UI", 9),
            bg=self.bg_tertiary,
            fg=self.success_color
        )
        self.header_status_label.pack(anchor=tk.W)

        # --- Top Frame for Action Buttons (Card-based layout) ---
        actions_card = tk.Frame(main_frame, bg=self.bg_tertiary, highlightthickness=1,
                               highlightbackground=self.border_color)
        actions_card.pack(fill=tk.X, pady=(0, 15))
        
        actions_inner = tk.Frame(actions_card, bg=self.bg_tertiary, padx=15, pady=10)
        actions_inner.pack(fill=tk.X)
        
        # Section label
        actions_label = tk.Label(
            actions_inner,
            text="Quick Actions",
            font=("Segoe UI", 9, "bold"),
            bg=self.bg_tertiary,
            fg=self.fg_muted
        )
        actions_label.pack(side=tk.LEFT, padx=(0, 15))
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # UE5-style separator line below header (7px bottom padding maintains original 15px total)
        header_separator = tk.Frame(main_frame, height=1, bg=self.accent_color)
        header_separator.pack(fill=tk.X, pady=(0, 7))

        # --- Top Frame for Buttons ---
        top_frame = tk.Frame(main_frame, bg=self.bg_color)
        top_frame.pack(fill=tk.X, pady=(0, 15))

        # Enhanced button style with better visual hierarchy
        button_style = {
            "font": ("Segoe UI", 10),
            "bg": self.button_bg,
            "fg": self.fg_color,
            "activebackground": self.button_hover,
            "activeforeground": self.fg_color,
            "relief": tk.FLAT,
            "padx": 15,
            "pady": 8,
            "cursor": "hand2",
            "borderwidth": 1,
            "highlightthickness": 0
            "padx": 18,  # Slightly more padding for UE5 style
            "pady": 9,   # Slightly more vertical padding
            "cursor": "hand2",
            "borderwidth": 1,
            "highlightthickness": 1,
            "highlightbackground": self.button_bg,
            "highlightcolor": self.accent_color
        }

        self.ingest_button = tk.Button(
            actions_inner,
            text="📚 Update Knowledge Base",
            command=self.run_ingestion,
            **button_style
        )
        self.ingest_button.pack(side=tk.LEFT, padx=(0, 8))
        self.create_tooltip(self.ingest_button, "Load and process project documents (Ctrl+U)")
        self.add_button_hover_effect(self.ingest_button)

        self.api_key_button = tk.Button(
            actions_inner,
            text="🔑 Set API Key",
            command=self.set_api_key,
            **button_style
        )
        self.api_key_button.pack(side=tk.LEFT, padx=(0, 8))
        self.create_tooltip(self.api_key_button, "Configure your OpenAI API key (Ctrl+K)")
        self.add_button_hover_effect(self.api_key_button)

        self.clear_button = tk.Button(
            actions_inner,
            text="🗑️ Clear",
            command=self.clear_conversation,
            **button_style
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 8))
        self.create_tooltip(self.clear_button, "Clear conversation history (Ctrl+L)")
        self.add_button_hover_effect(self.clear_button)
        
        self.copy_button = tk.Button(
            actions_inner,
            text="📋 Copy",
            command=self.copy_response,
            **button_style
        )
        self.copy_button.pack(side=tk.LEFT)
        self.create_tooltip(self.copy_button, "Copy last response to clipboard (Ctrl+C)")
        self.add_button_hover_effect(self.copy_button)

        # Separator
        separator = tk.Frame(actions_inner, width=2, bg=self.border_color)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Font size controls with enhanced styling
        font_frame = tk.Frame(actions_inner, bg=self.bg_tertiary)
        font_frame.pack(side=tk.RIGHT)
        
        tk.Label(
            font_frame, 
            text="Text Size:", 
            bg=self.bg_tertiary, 
            fg=self.fg_muted, 
            font=("Segoe UI", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        small_button_style = {
            "font": ("Segoe UI", 9, "bold"),
            "bg": self.button_bg,
            "fg": self.fg_color,
            "activebackground": self.button_hover,
            "activeforeground": self.fg_color,
            "relief": tk.FLAT,
            "padx": 10,
            "pady": 6,
            "cursor": "hand2",
            "width": 3
            "padx": 10,  # Slightly more padding
            "pady": 5,   # Better vertical alignment
            "cursor": "hand2",
            "borderwidth": 1,
            "highlightthickness": 1,
            "highlightbackground": self.button_bg
        }
        
        self.decrease_font_button = tk.Button(
            font_frame,
            text="A-",
            command=self.decrease_font,
            **small_button_style
        )
        self.decrease_font_button.pack(side=tk.LEFT, padx=(0, 4))
        self.create_tooltip(self.decrease_font_button, "Decrease font size (min 8pt)")
        self.add_button_hover_effect(self.decrease_font_button)
        
        self.increase_font_button = tk.Button(
            font_frame,
            text="A+",
            command=self.increase_font,
            **small_button_style
        )
        self.increase_font_button.pack(side=tk.LEFT)
        self.create_tooltip(self.increase_font_button, "Increase font size (max 20pt)")
        self.add_button_hover_effect(self.increase_font_button)

        # --- Response Display Area (Card-based design) ---
        response_card = tk.Frame(main_frame, bg=self.bg_tertiary, highlightthickness=1,
                                highlightbackground=self.border_color)
        response_card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        # --- Response Display Area with UE5-style border ---
        response_frame = tk.Frame(main_frame, bg=self.bg_color)
        response_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Header section
        response_header = tk.Frame(response_card, bg=self.bg_tertiary, padx=15, pady=10)
        response_header.pack(fill=tk.X)
        
        response_label = tk.Label(
            response_header,
            text="💬 Conversation History",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_tertiary,
            fg=self.fg_color
        )
        response_label.pack(side=tk.LEFT)
        
        # Conversation stats
        self.stats_label = tk.Label(
            response_header,
            text="0 messages",
            font=("Segoe UI", 9),
            bg=self.bg_tertiary,
            fg=self.fg_muted
        )
        self.stats_label.pack(side=tk.RIGHT)
        
        # Separator line
        separator_line = tk.Frame(response_card, height=1, bg=self.border_color)
        separator_line.pack(fill=tk.X)
        
        # Content frame with padding
        content_frame = tk.Frame(response_card, bg=self.text_bg)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.current_font_size = 10
        self.response_font = font.Font(family="Consolas", size=self.current_font_size)
        
        # Container frame with UE5-style border for visual depth
        text_container = tk.Frame(response_frame, bg=self.button_bg, padx=1, pady=1)
        text_container.pack(fill=tk.BOTH, expand=True)
        
        self.response_text = scrolledtext.ScrolledText(
            content_frame,
            text_container,
            wrap=tk.WORD,
            height=20,
            state=tk.DISABLED,
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.accent_color,
            font=self.response_font,
            relief=tk.FLAT,
            padx=15,
            pady=15,
            selectbackground=self.highlight_bg,
            selectforeground=self.fg_color
            padx=12,
            pady=12,
            borderwidth=0
        )
        self.response_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for better formatting (Unreal Engine inspired)
        self.response_text.tag_config("user", foreground="#40a9ff", font=("Segoe UI", self.current_font_size, "bold"))  # UE5 blue
        self.response_text.tag_config("assistant", foreground="#a5b8c8")  # Lighter blue-gray for assistant
        self.response_text.tag_config("timestamp", foreground="#6a7080", font=("Segoe UI", 8))  # Muted blue-gray
        self.response_text.tag_config("error", foreground="#ff5555")  # Brighter error red

        # --- Query Input Area (Card-based design) ---
        query_card = tk.Frame(main_frame, bg=self.bg_tertiary, highlightthickness=1,
                             highlightbackground=self.border_color)
        query_card.pack(fill=tk.X, pady=(0, 0))
        
        query_inner = tk.Frame(query_card, bg=self.bg_tertiary, padx=15, pady=12)
        query_inner.pack(fill=tk.X)
        # --- Query Input Area with UE5-style separator ---
        # Add separator line above input area
        input_separator = tk.Frame(main_frame, height=1, bg=self.button_bg)
        input_separator.pack(fill=tk.X, pady=(0, 15))
        
        query_frame = tk.Frame(main_frame, bg=self.bg_color)
        query_frame.pack(fill=tk.X, pady=(0, 0))
        
        # Increased bottom padding from 5px to 8px for UE5-style spacing and improved visual alignment
        query_header = tk.Frame(query_frame, bg=self.bg_color)
        query_header.pack(fill=tk.X, pady=(0, 8))
        
        # Header with icon
        query_label = tk.Label(
            query_inner,
            text="💭 Ask a Question",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_tertiary,
            fg=self.fg_color
        )
        query_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Input frame with enhanced styling
        input_container = tk.Frame(query_inner, bg=self.bg_tertiary)
        input_container.pack(fill=tk.X)
        
        # Entry field container with border
        entry_frame = tk.Frame(input_container, bg=self.text_bg, highlightthickness=2,
                              highlightbackground=self.border_color)
        entry_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Container with border for input field (UE5 style)
        entry_container = tk.Frame(input_frame, bg=self.button_bg, padx=1, pady=1)
        entry_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.query_entry = tk.Entry(
            entry_frame,
            entry_container,
            font=("Segoe UI", 11),
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.accent_color,
            relief=tk.FLAT,
            highlightthickness=0,
            borderwidth=0
        )
        self.query_entry.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
            highlightthickness=1,
            highlightbackground=self.button_bg,
            highlightcolor=self.accent_color,
            borderwidth=0
        )
        self.query_entry.pack(fill=tk.BOTH, expand=True, ipady=8, ipadx=10)
        self.query_entry.bind("<Return>", self.run_query_event)
        self.query_entry.bind("<Control-Return>", self.run_query_event)
        self.query_entry.focus()

        # Enhanced Ask button with better styling
        self.ask_button = tk.Button(
            input_container,
            text="Send ▶",
            command=self.run_query,
            font=("Segoe UI", 11, "bold"),
            bg=self.accent_color,
            fg="white",
            activebackground=self.accent_active,
            activeforeground="white",
            relief=tk.FLAT,
            padx=30,
            pady=12,
            fg="#20232b",  # Dark text on bright button for UE5 style
            activebackground="#5bb8ff",  # Lighter blue on hover
            activeforeground="#20232b",
            relief=tk.FLAT,
            padx=28,  # More padding for prominence
            pady=10,  # Better vertical padding
            cursor="hand2",
            borderwidth=0
        )
        self.ask_button.pack(side=tk.RIGHT)
        self.create_tooltip(self.ask_button, "Send your question (Enter or Ctrl+Enter)")
        
        # Add hover effect to primary button with custom accent color
        self.add_button_hover_effect(self.ask_button, hover_color=self.accent_hover)
        
        # Add focus effect to entry
        def entry_focus_in(e):
            entry_frame.config(highlightbackground=self.accent_color)
        def entry_focus_out(e):
            entry_frame.config(highlightbackground=self.border_color)
        self.query_entry.bind("<FocusIn>", entry_focus_in)
        self.query_entry.bind("<FocusOut>", entry_focus_out)
        
        # --- Enhanced Status Bar ---
        status_frame = tk.Frame(root, bg=self.bg_secondary, highlightthickness=1,
                               highlightbackground=self.border_color)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        status_inner = tk.Frame(status_frame, bg=self.bg_secondary)
        status_inner.pack(fill=tk.X, padx=15, pady=8)
        
        # Status indicator
        self.status_indicator = tk.Label(
            status_inner,
            text="●",
            font=("Segoe UI", 10),
            bg=self.bg_secondary,
            fg=self.success_color
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 8))
        
        # Status text
        self.status_var = tk.StringVar()
        self.status_var.set("Ready • Please set your OpenAI API Key if you haven't")
        status_label = tk.Label(
            status_inner,
            textvariable=self.status_var,
            bg=self.bg_secondary,
            fg=self.fg_secondary,
            font=("Segoe UI", 9),
            anchor=tk.W
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Version info
        version_label = tk.Label(
            status_inner,
            text="v1.0.0",
            bg=self.bg_secondary,
            fg=self.fg_muted,
            font=("Segoe UI", 8)
        )
        version_label.pack(side=tk.RIGHT)
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Show welcome message
        self.show_welcome_message()

        self.check_api_key_on_startup()

    def update_status(self, message, status_type="info"):
        """
        Update status bar with message and indicator color.
        
        Args:
            message: Status message to display
            status_type: Type of status - "success", "error", "warning", "info", "busy"
        """
        self.status_var.set(message)
        
        # Update indicator color based on status type
        color_map = {
            "success": self.success_color,
            "error": self.error_color,
            "warning": self.warning_color,
            "info": self.fg_secondary,
            "busy": self.accent_color
        }
        
        self.status_indicator.config(fg=color_map.get(status_type, self.fg_secondary))
        
        # Update header status as well
        if hasattr(self, 'header_status_label'):
            status_text = {
                "success": "● Ready",
                "error": "● Error",
                "warning": "● Warning",
                "info": "● Ready",
                "busy": "● Processing"
            }
            self.header_status_label.config(
                text=status_text.get(status_type, "● Ready"),
                fg=color_map.get(status_type, self.fg_secondary)
            )
    
    def create_menu_bar(self):
        """Create the application menu bar with dark theme styling."""
        menubar = Menu(self.root, bg=self.button_bg, fg=self.fg_color, 
                      activebackground=self.button_active, activeforeground=self.fg_color)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0, bg=self.button_bg, fg=self.fg_color,
                        activebackground=self.button_active, activeforeground=self.fg_color)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Conversation...", command=self.export_conversation, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        
        # Edit menu
        edit_menu = Menu(menubar, tearoff=0, bg=self.button_bg, fg=self.fg_color,
                        activebackground=self.button_active, activeforeground=self.fg_color)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy Response", command=self.copy_response, accelerator="Ctrl+C")
        edit_menu.add_command(label="Clear Conversation", command=self.clear_conversation, accelerator="Ctrl+L")
        edit_menu.add_separator()
        edit_menu.add_command(label="Set API Key", command=self.set_api_key, accelerator="Ctrl+K")
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0, bg=self.button_bg, fg=self.fg_color,
                        activebackground=self.button_active, activeforeground=self.fg_color)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
    
    def add_button_hover_effect(self, button, hover_color=None):
        """Add smooth hover effect to buttons for better visual feedback.
        
        Args:
            button: The button widget to add hover effect to
            hover_color: Optional custom hover color. If None, uses self.button_hover
        """
        original_bg = button.cget("background")
        hover_bg = hover_color if hover_color else self.button_hover
        
        def on_enter(e):
            button.config(background=hover_bg)
        
        def on_leave(e):
            button.config(background=original_bg)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget that appears after a delay."""
        tooltip_id = None
        
        def show_tooltip(event):
            nonlocal tooltip_id
            # Cancel any pending tooltip
            if tooltip_id:
                widget.after_cancel(tooltip_id)
            # Schedule tooltip to appear after 500ms delay
            tooltip_id = widget.after(500, lambda: display_tooltip(event))
        
        def display_tooltip(event):
            nonlocal tooltip_id
            tooltip_id = None
            
            # Create tooltip window
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            
            # Position tooltip below and slightly to the right of cursor
            x = event.widget.winfo_rootx() + 10
            y = event.widget.winfo_rooty() + event.widget.winfo_height() + 5
            tooltip.wm_geometry(f"+{x}+{y}")
            
            # Create tooltip label with Unreal Engine styling
            label = tk.Label(
                tooltip,
                text=text,
                background="#343843",  # UE5 button default color
                foreground="#e3e4e8",  # UE5 text color
                relief=tk.SOLID,
                borderwidth=1,
                font=("Segoe UI", 9),
                padx=5,
                pady=3
            )
            label.pack()
            
            # Configure border color with UE5 style
            tooltip.configure(bg="#40a9ff", highlightthickness=1, highlightbackground="#40a9ff")
            
            widget.tooltip = tooltip
        
        def hide_tooltip(event):
            nonlocal tooltip_id
            # Cancel pending tooltip
            if tooltip_id:
                widget.after_cancel(tooltip_id)
                tooltip_id = None
            # Destroy existing tooltip
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.root.bind("<Control-k>", lambda e: self.set_api_key())
        self.root.bind("<Control-K>", lambda e: self.set_api_key())
        self.root.bind("<Control-u>", lambda e: self.run_ingestion())
        self.root.bind("<Control-U>", lambda e: self.run_ingestion())
        self.root.bind("<Control-l>", lambda e: self.clear_conversation())
        self.root.bind("<Control-L>", lambda e: self.clear_conversation())
        self.root.bind("<Control-e>", lambda e: self.export_conversation())
        self.root.bind("<Control-E>", lambda e: self.export_conversation())
        # Note: Ctrl+C is handled separately for copy
    
    def show_welcome_message(self):
        """Display a welcome message on startup."""
        welcome = """🤖 Welcome to Adastrea Director!

Your AI-powered game development assistant is ready to help.

Getting Started:
1. Set your OpenAI API Key (🔑 button or Ctrl+K)
2. Update the knowledge base with your project docs (📚 button or Ctrl+U)
3. Ask questions about your game design, code, or documentation

Try asking:
• "What is the main gameplay loop?"
• "Describe the player abilities"
• "How should I implement the quantum phase mechanic?"

Keyboard Shortcuts:
• Enter or Ctrl+Enter - Send question
• Ctrl+L - Clear conversation
• Ctrl+C - Copy last response
• Ctrl+K - Set API key
• Ctrl+U - Update knowledge base

Type your question below to get started! 🚀
"""
        self.response_text.config(state=tk.NORMAL)
        self.response_text.insert(tk.END, welcome, "assistant")
        self.response_text.config(state=tk.DISABLED)
    
    def set_api_key(self):
        """Opens a dialog to ask for the API key."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Set OpenAI API Key")
        dialog.geometry("450x180")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(
            dialog,
            text="Enter your OpenAI API Key:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Segoe UI", 11)
        ).pack(pady=(20, 10), padx=20)
        
        key_entry = tk.Entry(
            dialog,
            show='•',  # Use bullet character for masking per design spec
            font=("Segoe UI", 10),
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.button_bg,
            highlightcolor=self.accent_color,
            width=40
        )
        key_entry.pack(pady=10, padx=20)
        key_entry.focus()
        
        def on_ok():
            key = key_entry.get()
            if key:
                os.environ['OPENAI_API_KEY'] = key
                self.update_status("API Key set successfully • Ready to ingest or query", "success")
                self.add_to_conversation("System", "API Key configured successfully.", is_system=True)
                dialog.destroy()
            else:
                messagebox.showwarning("Invalid Input", "Please enter a valid API key.")
        
        def on_cancel():
            dialog.destroy()
        
        key_entry.bind("<Return>", lambda e: on_ok())
        key_entry.bind("<Escape>", lambda e: on_cancel())
        
        button_frame = tk.Frame(dialog, bg=self.bg_color)
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="OK",
            command=on_ok,
            bg=self.accent_color,
            fg="#20232b",  # Dark text on bright button for UE5 style
            activebackground="#5bb8ff",  # Lighter blue on hover
            activeforeground="#20232b",
            relief=tk.FLAT,
            padx=24,  # More padding for UE5 style
            pady=8,   # Better vertical padding
            cursor="hand2",
            font=("Segoe UI", 10),
            borderwidth=0
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=on_cancel,
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.button_active,  # Lighter on hover
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=24,  # More padding for UE5 style
            pady=8,   # Better vertical padding
            cursor="hand2",
            font=("Segoe UI", 10),
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.button_bg
        ).pack(side=tk.LEFT, padx=5)

    def check_api_key_on_startup(self):
        """Checks if the API key is set and prompts the user if not."""
        if not os.getenv("OPENAI_API_KEY"):
            self.root.after(500, self.set_api_key)

    def run_ingestion(self):
        """Runs the ingest.py script in a separate thread."""
        self.run_script_in_thread('ingest.py', "🤔 Ingesting documents...")

    def clear_conversation(self):
        """Clear the conversation display with confirmation."""
        # Only ask for confirmation if there's actual conversation content
        if self.conversation_history:
            result = messagebox.askyesno(
                "Clear Conversation",
                "Are you sure you want to clear the entire conversation history?\n\nThis action cannot be undone.",
                icon='warning'
            )
            if not result:
                return
        
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete(1.0, tk.END)
        self.response_text.config(state=tk.DISABLED)
        self.conversation_history = []
        self.update_message_count()
        self.update_status("Conversation cleared • Ready for new questions", "success")
        self.show_welcome_message()
    
    def copy_response(self):
        """Copy the last response to clipboard."""
        try:
            if self.conversation_history:
                last_response = self.conversation_history[-1]
                if last_response['role'] == 'assistant':
                    self.root.clipboard_clear()
                    self.root.clipboard_append(last_response['content'])
                    self.update_status("Response copied to clipboard", "success")
                else:
                    messagebox.showinfo("No Response", "No assistant response to copy.")
            else:
                messagebox.showinfo("Empty", "No conversation to copy.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy: {e}")
    
    def export_conversation(self):
        """Export conversation to a text file."""
        if not self.conversation_history:
            messagebox.showinfo("Empty", "No conversation to export.")
            return
        
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Markdown files", "*.md"), ("All files", "*.*")],
            initialfile=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("Adastrea Director Conversation\n")
                    f.write("=" * 50 + "\n\n")
                    for entry in self.conversation_history:
                        timestamp = entry.get('timestamp', '')
                        role = entry['role'].upper()
                        content = entry['content']
                        f.write(f"[{timestamp}] {role}:\n{content}\n\n")
                self.update_status(f"Conversation exported successfully", "success")
                messagebox.showinfo("Success", f"Conversation exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def increase_font(self):
        """Increase font size."""
        if self.current_font_size < 20:
            self.current_font_size += 1
            self.response_font.configure(size=self.current_font_size)
            self.response_text.tag_config("user", font=("Segoe UI", self.current_font_size, "bold"))
            self.update_status(f"Text size increased to {self.current_font_size}pt", "info")
    
    def decrease_font(self):
        """Decrease font size."""
        if self.current_font_size > 8:
            self.current_font_size -= 1
            self.response_font.configure(size=self.current_font_size)
            self.response_text.tag_config("user", font=("Segoe UI", self.current_font_size, "bold"))
            self.update_status(f"Text size decreased to {self.current_font_size}pt", "info")
    
    def show_shortcuts(self):
        """Display keyboard shortcuts."""
        shortcuts = """Keyboard Shortcuts

File Operations:
• Ctrl+E - Export conversation to file

Editing:
• Ctrl+C - Copy last response
• Ctrl+L - Clear conversation
• Ctrl+K - Set API Key

Actions:
• Enter or Ctrl+Enter - Send question
• Ctrl+U - Update knowledge base

Navigation:
• Alt+F4 - Exit application
"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def show_about(self):
        """Display about information."""
        about_text = """Adastrea Director
AI Game Development Assistant

Version: 1.0.0 (Phase 1)
An intelligent assistant system for game development in Unreal Engine.

Features:
• Context-aware Q&A using RAG
• Document ingestion and processing
• Natural language interface

GitHub: Mittenzx/Adastrea-Director
"""
        messagebox.showinfo("About Adastrea Director", about_text)
    
    def add_to_conversation(self, role, content, is_system=False):
        """Add a message to the conversation display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.conversation_history.append({
            'role': role.lower(),
            'content': content,
            'timestamp': timestamp
        })
        
        # Update message count
        self.update_message_count()
        
        self.response_text.config(state=tk.NORMAL)
        
        # Add timestamp
        self.response_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add role and content
        if is_system:
            self.response_text.insert(tk.END, f"{role}: ", "timestamp")
            self.response_text.insert(tk.END, f"{content}\n\n", "assistant")
        elif role.lower() == "you":
            self.response_text.insert(tk.END, f"{role}: ", "user")
            self.response_text.insert(tk.END, f"{content}\n\n", "")
        else:
            self.response_text.insert(tk.END, f"{role}: ", "assistant")
            self.response_text.insert(tk.END, f"{content}\n\n", "")
        
        self.response_text.see(tk.END)
        self.response_text.config(state=tk.DISABLED)
    
    def update_message_count(self):
        """Update the message count in the conversation header."""
        count = len(self.conversation_history)
        plural = "message" if count == 1 else "messages"
        self.stats_label.config(text=f"{count} {plural}")
    
    def run_query_event(self, event):
        """Handler for pressing Enter in the query box."""
        self.run_query()
        return "break"  # Prevent default behavior
        
    def run_query(self):
        """Runs the main.py query script in a separate thread."""
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showwarning("Input Error", "Please enter a question.")
            return
        
        # Add user query to conversation
        self.add_to_conversation("You", query)
        
        # Clear the input field
        self.query_entry.delete(0, tk.END)
        
        # Add quotes around the query to handle multi-word inputs correctly
        self.run_script_in_thread('main.py', f'🤔 Processing your question...', query)

    def run_script_in_thread(self, script_name, status_message, *args):
        """
        Generic function to run a python script in a thread to keep the GUI responsive.
        """
        self.ingest_button.config(state=tk.DISABLED)
        self.ask_button.config(state=tk.DISABLED)
        self.update_status(status_message, "busy")
        
        # Use absolute path for the script to ensure it can be found
        script_path = os.path.join(SCRIPT_DIR, script_name)
        command = [PYTHON_EXECUTABLE, script_path] + list(args)

        thread = threading.Thread(target=self._execute_command, args=(command,))
        thread.start()

    def _execute_command(self, command):
        """The actual command execution logic."""
        try:
            # Use CREATE_NO_WINDOW on Windows to prevent console window from appearing
            kwargs = {'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE, 'text': True}
            if sys.platform == 'win32' and hasattr(subprocess, 'CREATE_NO_WINDOW'):
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            process = subprocess.Popen(command, **kwargs)
            stdout, stderr = process.communicate()
            
            output = stdout
            if process.returncode != 0:
                output += f"\n--- ERROR ---\n{stderr}"
            
            # Schedule the UI update to run on the main thread
            self.root.after(0, self._update_ui_after_execution, output, process.returncode)

        except Exception as e:
            self.root.after(0, self._update_ui_after_execution, str(e), 1)

    def _update_ui_after_execution(self, output, returncode):
        """Updates the GUI elements after the script has finished."""
        # Clean up the output
        output = output.strip()
        
        if returncode == 0:
            if output:
                # Add assistant response to conversation
                self.add_to_conversation("Assistant", output)
            self.update_status("Ready • Waiting for your question", "success")
        else:
            # Add error to conversation
            error_message = f"Error occurred:\n{output}"
            self.response_text.config(state=tk.NORMAL)
            self.response_text.insert(tk.END, "❌ ", "error")
            self.response_text.insert(tk.END, error_message + "\n\n", "error")
            self.response_text.see(tk.END)
            self.response_text.config(state=tk.DISABLED)
            self.update_status("An error occurred • Check the conversation for details", "error")
            
        self.ingest_button.config(state=tk.NORMAL)
        self.ask_button.config(state=tk.NORMAL)
        self.query_entry.focus()

def main():
    root = tk.Tk()
    app = AdastreaDirectorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
