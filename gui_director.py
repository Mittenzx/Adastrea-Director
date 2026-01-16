# Standard library imports
import subprocess
import threading
import sys
import os
import json
import socket
import tempfile
from datetime import datetime
from pathlib import Path
from collections import deque

# Try to import tkinter (not available via pip - requires system package)
try:
    import tkinter as tk
    from tkinter import scrolledtext, messagebox, Menu, font, filedialog, ttk
except ImportError as e:
    print("=" * 70)
    print("ERROR: tkinter module not found")
    print("=" * 70)
    print("\nThe GUI requires tkinter, which is not installed via pip.")
    print("\nPlatform-specific installation instructions:")
    print("\n📦 Ubuntu/Debian:")
    print("  sudo apt-get install python3-tk")
    print("\n📦 Fedora/RHEL:")
    print("  sudo dnf install python3-tkinter")
    print("\n📦 Arch Linux:")
    print("  sudo pacman -S tk")
    print("\n📦 macOS:")
    print("  tkinter is included with Python from python.org")
    print("  If using Homebrew: brew install python-tk")
    print("\n📦 Windows:")
    print("  tkinter is included with Python from python.org")
    print("  Reinstall Python and ensure 'tcl/tk and IDLE' is checked")
    print("\n💡 Alternative: Use the CLI interface instead:")
    print("  python main.py")
    print("\n📚 For more help, see TROUBLESHOOTING.md (lines 483-492)")
    print("=" * 70)
    sys.exit(1)

# Import UE log capture module
from ue_log_capture import UELogCapture

# Import analytics modules
from project_analytics import ProjectAnalytics
from ue_data_collector import UEDataCollector

# Import logging configuration
from logging_config import setup_logging, get_logger

# Import new UI components
try:
    from gui_agent_panel import create_agent_dashboard_tab
    AGENT_PANEL_AVAILABLE = True
except ImportError:
    AGENT_PANEL_AVAILABLE = False
    # Note: Agent panel module not available - will skip creating agent dashboard tab

# Try to import psutil for system health monitoring (optional dependency)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Disable ChromaDB telemetry BEFORE any imports that might import chromadb
# This prevents "capture() takes 1 positional argument but 3 were given" errors
# ChromaDB checks for this variable and disables telemetry when set to "1"
os.environ["ANONYMIZED_TELEMETRY"] = "1"

# --- Configuration ---
# Path to the python executable running this script.
# This ensures we use the same Python environment where all the dependencies are installed.
PYTHON_EXECUTABLE = sys.executable

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Constants for ingestion logging
MAX_ERROR_LOG_LENGTH = 200  # Maximum characters to show in error logs to keep them concise and readable
PROGRESS_POLL_INTERVAL_MS = 500  # Progress file polling interval in milliseconds (balance between responsiveness and performance)

# Constants for test execution
TEST_OUTPUT_BATCH_SIZE = 10  # Number of output lines to batch before updating UI (improves performance)
TEST_STOP_TIMEOUT = 3  # Seconds to wait for graceful process termination before forcing kill

# Constants for Unreal MCP integration
MCP_PYTHON_PLACEHOLDER = "import unreal\nprint(unreal.SystemLibrary.get_engine_version())"
MCP_CONSOLE_PLACEHOLDER = "stat fps"

# Constants for IPC and connection monitoring
IPC_SERVER_PORT = 8765  # Default port for IPC server communication
LANDING_AUTO_REFRESH_INTERVAL_MS = 5000  # Auto-refresh interval for landing page (5 seconds)
LANDING_TAB_INDEX = 0  # Index of the landing tab in the notebook
CANVAS_RESIZE_DEBOUNCE_MS = 100  # Debounce delay for canvas resize events
INIT_REFRESH_DELAY_MS = 100  # Delay before initial refresh to ensure mainloop has started

# Constants for connection diagram layout
DIAGRAM_BOX_WIDTH = 120  # Width of component boxes in connection diagram
DIAGRAM_BOX_HEIGHT = 80  # Height of component boxes in connection diagram
DIAGRAM_STATUS_RADIUS = 8  # Radius of status indicator circles
DIAGRAM_STATUS_Y_OFFSET = 30  # Y offset from center for status indicators

class AdastreaDirectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Adastrea Director - AI Game Development Assistant")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Setup logging for GUI
        setup_logging(debug=False, console=True)
        self.logger = get_logger(__name__)
        self.logger.info("Adastrea Director GUI starting")
        
        # Enhanced color scheme - Unreal Engine 5 inspired with card-based design support
        # Base UE5 colors
        self.bg_color = "#20232b"  # UE5 background panel (darker, blueish)
        self.fg_color = "#e3e4e8"  # UE5 text color (light gray, slightly warm)
        self.accent_color = "#40a9ff"  # UE5 toolbar/button highlight (bright blue)
        self.button_bg = "#343843"  # UE5 button default (medium gray-blue)
        self.button_active = "#4a4e5a"  # Lighter variant for hover
        self.text_bg = "#2a2d35"  # Slightly lighter than background for input areas
        
        # Additional colors for card-based design from PR #13
        self.bg_secondary = "#252526"       # Secondary background (panels)
        self.bg_tertiary = "#2d2d30"        # Tertiary background (cards)
        self.fg_secondary = "#cccccc"       # Secondary text
        self.fg_muted = "#858585"           # Muted/disabled text
        self.accent_hover = "#5bb8ff"       # Accent hover state (lighter blue, UE5 style)
        self.accent_active = "#005a9e"      # Accent active state (darker blue)
        self.button_hover = "#4a4e5a"       # Button hover (same as button_active for UE5)
        self.border_color = "#3e3e42"       # Border color
        self.success_color = "#4ec9b0"      # Success/positive
        self.warning_color = "#ce9178"      # Warning/info
        self.error_color = "#f48771"        # Error/danger
        self.highlight_bg = "#094771"       # Selection/highlight background
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Set up window close protocol to cleanup resources
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Conversation history
        self.conversation_history = []
        
        # Create a single ttk.Style instance to be reused
        self.style = ttk.Style()
        self.style.theme_use('default')
        
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

        # Enhanced button style with better visual hierarchy (UE5 style with card design)
        button_style = {
            "font": ("Segoe UI", 10),
            "bg": self.button_bg,
            "fg": self.fg_color,
            "activebackground": self.button_hover,
            "activeforeground": self.fg_color,
            "relief": tk.FLAT,
            "padx": 18,  # UE5 style padding
            "pady": 9,   # UE5 style padding
            "cursor": "hand2",
            "borderwidth": 1,
            "highlightthickness": 1,
            "highlightbackground": self.button_bg,
            "highlightcolor": self.accent_color
        }

        self.ingest_folder_button = tk.Button(
            actions_inner,
            text="📁 Ingest Folder",
            command=self.ingest_folder,
            **button_style
        )
        self.ingest_folder_button.pack(side=tk.LEFT, padx=(0, 8))
        self.create_tooltip(self.ingest_folder_button, "Select a folder to ingest documents from")
        self.add_button_hover_effect(self.ingest_folder_button)

        self.ingest_file_button = tk.Button(
            actions_inner,
            text="📄 Ingest File",
            command=self.ingest_file,
            **button_style
        )
        self.ingest_file_button.pack(side=tk.LEFT, padx=(0, 8))
        self.create_tooltip(self.ingest_file_button, "Select a single file to ingest")
        self.add_button_hover_effect(self.ingest_file_button)

        self.ingest_repo_button = tk.Button(
            actions_inner,
            text="🔗 Ingest Repo",
            command=self.ingest_github_repo,
            **button_style
        )
        self.ingest_repo_button.pack(side=tk.LEFT, padx=(0, 8))
        self.create_tooltip(self.ingest_repo_button, "Ingest documents from a GitHub repository")
        self.add_button_hover_effect(self.ingest_repo_button)

        self.api_key_button = tk.Button(
            actions_inner,
            text="🔑 Set API Key",
            command=self.set_api_key,
            **button_style
        )
        self.api_key_button.pack(side=tk.LEFT, padx=(0, 8))
        self.create_tooltip(self.api_key_button, "Configure your Gemini API key (Ctrl+K)")
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
            "padx": 10,  # UE5 style padding
            "pady": 6,   # Balanced padding
            "cursor": "hand2",
            "width": 3,
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

        # --- Progress Bar Section (Initially hidden) ---
        self.progress_card = tk.Frame(main_frame, bg=self.bg_tertiary, highlightthickness=1,
                                     highlightbackground=self.border_color)
        # Don't pack yet - will be shown when ingestion starts
        
        progress_inner = tk.Frame(self.progress_card, bg=self.bg_tertiary, padx=15, pady=12)
        progress_inner.pack(fill=tk.X)
        
        # Progress label
        self.progress_label = tk.Label(
            progress_inner,
            text="Processing documents...",
            font=("Segoe UI", 10),
            bg=self.bg_tertiary,
            fg=self.fg_color,
            anchor=tk.W
        )
        self.progress_label.pack(fill=tk.X, pady=(0, 8))
        
        # Progress bar with custom style (reuse existing style instance)
        self.style.configure("Ingestion.Horizontal.TProgressbar",
                       troughcolor=self.text_bg,
                       background=self.accent_color,
                       borderwidth=0,
                       thickness=20)
        
        self.progress_bar = ttk.Progressbar(
            progress_inner,
            style="Ingestion.Horizontal.TProgressbar",
            orient=tk.HORIZONTAL,
            mode='determinate',
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Progress details label
        self.progress_details = tk.Label(
            progress_inner,
            text="",
            font=("Segoe UI", 9),
            bg=self.bg_tertiary,
            fg=self.fg_secondary,
            anchor=tk.W
        )
        self.progress_details.pack(fill=tk.X)
        
        # Initialize progress tracking variables
        self.progress_file = None
        self.progress_poll_id = None

        # --- Tabbed Interface (Card-based design) ---
        tabs_card = tk.Frame(main_frame, bg=self.bg_tertiary, highlightthickness=1,
                            highlightbackground=self.border_color)
        tabs_card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Style the notebook for dark theme (reuse existing style instance)
        self.style.configure('TNotebook', background=self.bg_tertiary, borderwidth=0)
        self.style.configure('TNotebook.Tab', 
                       background=self.button_bg, 
                       foreground=self.fg_color,
                       padding=[20, 10],
                       font=("Segoe UI", 10))
        self.style.map('TNotebook.Tab',
                 background=[('selected', self.bg_tertiary)],
                 foreground=[('selected', self.accent_color)])
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(tabs_card)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # --- Landing/Home Tab (What's Happening) ---
        self.create_landing_tab()
        
        # --- Conversation Tab ---
        conversation_tab = tk.Frame(self.notebook, bg=self.bg_tertiary)
        self.notebook.add(conversation_tab, text="💬 Conversation")
        
        # Header section for conversation
        response_header = tk.Frame(conversation_tab, bg=self.bg_tertiary, padx=15, pady=10)
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
        separator_line = tk.Frame(conversation_tab, height=1, bg=self.border_color)
        separator_line.pack(fill=tk.X)
        
        # Content frame with padding
        content_frame = tk.Frame(conversation_tab, bg=self.text_bg)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.current_font_size = 10
        self.response_font = font.Font(family="Consolas", size=self.current_font_size)
        
        self.response_text = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            height=20,
            state=tk.DISABLED,
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.accent_color,
            font=self.response_font,
            relief=tk.FLAT,
            padx=15,  # PR #13 padding
            pady=15,  # PR #13 padding
            selectbackground=self.highlight_bg,
            selectforeground=self.fg_color,
            borderwidth=0
        )
        self.response_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for better formatting (Unreal Engine inspired)
        self.response_text.tag_config("user", foreground="#40a9ff", font=("Segoe UI", self.current_font_size, "bold"))  # UE5 blue
        self.response_text.tag_config("assistant", foreground="#a5b8c8")  # Lighter blue-gray for assistant
        self.response_text.tag_config("timestamp", foreground="#6a7080", font=("Segoe UI", 8))  # Muted blue-gray
        self.response_text.tag_config("error", foreground="#ff5555")  # Brighter error red
        
        # --- Ingest List Tab ---
        self.create_ingest_list_tab()
        
        # --- Tests Tab ---
        self.create_tests_tab()
        
        # --- Unreal MCP Tab ---
        self.create_unreal_mcp_tab()
        
        # --- Status Dashboard Tab ---
        self.create_status_dashboard_tab()
        
        # --- Analytics Dashboard Tab ---
        self.create_analytics_dashboard_tab()
        
        # --- Agent Dashboard Tab (New!) ---
        if AGENT_PANEL_AVAILABLE:
            self.create_agent_dashboard_tab()
        
        # --- Servers Tab ---
        self.create_servers_tab()
        
        # --- Debug Logs Tab ---
        self.create_debug_logs_tab()

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
        
        # Input frame with enhanced styling (combines card design and UE5 style)
        input_container = tk.Frame(query_inner, bg=self.bg_tertiary)
        input_container.pack(fill=tk.X)
        
        # Entry field container with border (card design from PR #13)
        entry_frame = tk.Frame(input_container, bg=self.text_bg, highlightthickness=2,
                              highlightbackground=self.border_color)
        entry_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.query_entry = tk.Entry(
            entry_frame,
            font=("Segoe UI", 11),
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.accent_color,
            relief=tk.FLAT,
            highlightthickness=0,
            borderwidth=0
        )
        self.query_entry.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        self.query_entry.bind("<Return>", self.run_query_event)
        self.query_entry.bind("<Control-Return>", self.run_query_event)
        self.query_entry.focus()

        # Enhanced Ask button with UE5 style (combines card design and UE5 colors)
        self.ask_button = tk.Button(
            input_container,
            text="Send ▶",
            command=self.run_query,
            font=("Segoe UI", 11, "bold"),
            bg=self.accent_color,
            fg="#20232b",  # Dark text on bright button for UE5 style
            activebackground=self.accent_hover,  # Lighter blue on hover (UE5 style)
            activeforeground="#20232b",
            relief=tk.FLAT,
            padx=30,  # PR #13 padding
            pady=12,  # PR #13 padding
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
        self.status_var.set("Ready • Please set your Gemini API Key if you haven't")
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
        
        # Initialize analytics system
        self.project_analytics = ProjectAnalytics()
        self.ue_data_collector = UEDataCollector()
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Show welcome message
        self.show_welcome_message()

        self.check_api_key_on_startup()
        
        # Start auto-refresh for landing tab (every 5 seconds)
        self.landing_refresh_id = None
        self.start_landing_auto_refresh()
    
    def create_landing_tab(self):
        """Create the Landing/Home tab showing system status and connection diagram."""
        landing_tab = tk.Frame(self.notebook, bg=self.bg_tertiary)
        self.notebook.add(landing_tab, text="🏠 Home")
        
        # Header section
        landing_header = tk.Frame(landing_tab, bg=self.bg_tertiary, padx=15, pady=10)
        landing_header.pack(fill=tk.X)
        
        landing_label = tk.Label(
            landing_header,
            text="🏠 What's Happening",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_tertiary,
            fg=self.fg_color
        )
        landing_label.pack(side=tk.LEFT)
        
        # Refresh button
        refresh_landing_button = tk.Button(
            landing_header,
            text="🔄 Refresh",
            command=self.refresh_landing_status,
            font=("Segoe UI", 9),
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.button_hover,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.button_bg
        )
        refresh_landing_button.pack(side=tk.RIGHT)
        self.create_tooltip(refresh_landing_button, "Refresh system status")
        self.add_button_hover_effect(refresh_landing_button)
        
        # Separator line
        separator_line = tk.Frame(landing_tab, height=1, bg=self.border_color)
        separator_line.pack(fill=tk.X)
        
        # Main content area with scrollable frame
        content_frame = tk.Frame(landing_tab, bg=self.bg_tertiary)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create canvas for connection diagram
        diagram_frame = tk.Frame(content_frame, bg=self.bg_tertiary, 
                                highlightthickness=1, highlightbackground=self.border_color)
        diagram_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Title for diagram
        diagram_title = tk.Label(
            diagram_frame,
            text="System Connection Status",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_tertiary,
            fg=self.accent_color,
            anchor=tk.W
        )
        diagram_title.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        # Canvas for drawing connections
        self.landing_canvas = tk.Canvas(
            diagram_frame,
            bg=self.bg_color,
            height=300,
            highlightthickness=0
        )
        self.landing_canvas.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Storage for component references
        self.landing_components = {}
        
        # Bind canvas resize event once during initialization with debouncing
        if not hasattr(self, '_landing_resize_job'):
            self._landing_resize_job = None
        
        def on_resize(event):
            # Cancel previous scheduled redraw
            if self._landing_resize_job:
                self.root.after_cancel(self._landing_resize_job)
            # Schedule new redraw with configured debounce delay
            self._landing_resize_job = self.root.after(CANVAS_RESIZE_DEBOUNCE_MS, self.draw_connection_diagram)
        
        self.landing_canvas.bind("<Configure>", on_resize)
        
        # Log section
        log_frame = tk.Frame(content_frame, bg=self.bg_tertiary,
                            highlightthickness=1, highlightbackground=self.border_color)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_header = tk.Label(
            log_frame,
            text="📝 Recent Activity",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_tertiary,
            fg=self.accent_color,
            anchor=tk.W
        )
        log_header.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        # Log display
        log_text_frame = tk.Frame(log_frame, bg=self.text_bg)
        log_text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.landing_log = scrolledtext.ScrolledText(
            log_text_frame,
            wrap=tk.WORD,
            height=8,
            state=tk.DISABLED,
            bg=self.text_bg,
            fg=self.fg_color,
            font=("Consolas", 9),
            relief=tk.FLAT,
            padx=10,
            pady=10,
            selectbackground=self.highlight_bg,
            selectforeground=self.fg_color,
            borderwidth=0
        )
        self.landing_log.pack(fill=tk.BOTH, expand=True)
        
        # Configure log tags
        self.landing_log.tag_config("timestamp", foreground=self.fg_muted, font=("Consolas", 8))
        self.landing_log.tag_config("info", foreground=self.fg_secondary)
        self.landing_log.tag_config("success", foreground=self.success_color)
        self.landing_log.tag_config("warning", foreground=self.warning_color)
        self.landing_log.tag_config("error", foreground=self.error_color)
        
        # Initial log message
        self.log_to_landing("🏠 Welcome to Adastrea Director", "info")
        self.log_to_landing("System initializing...", "info")
        
        # Draw initial diagram
        self.draw_connection_diagram()
        
        # Initial status check
        self.refresh_landing_status()
    
    def create_ingest_list_tab(self):
        """Create the Ingest List tab showing ingested and pending documents."""
        ingest_tab = tk.Frame(self.notebook, bg=self.bg_tertiary)
        self.notebook.add(ingest_tab, text="📋 Ingest List")
        
        # Header section
        ingest_header = tk.Frame(ingest_tab, bg=self.bg_tertiary, padx=15, pady=10)
        ingest_header.pack(fill=tk.X)
        
        ingest_label = tk.Label(
            ingest_header,
            text="📋 Document Ingestion Status",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_tertiary,
            fg=self.fg_color
        )
        ingest_label.pack(side=tk.LEFT)
        
        # Refresh button
        refresh_button = tk.Button(
            ingest_header,
            text="🔄 Refresh",
            command=self.refresh_ingest_list,
            font=("Segoe UI", 9),
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.button_hover,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.button_bg
        )
        refresh_button.pack(side=tk.RIGHT)
        self.create_tooltip(refresh_button, "Refresh the ingestion status")
        self.add_button_hover_effect(refresh_button)
        
        # Separator line
        separator_line = tk.Frame(ingest_tab, height=1, bg=self.border_color)
        separator_line.pack(fill=tk.X)
        
        # Main content area with split panes
        content_frame = tk.Frame(ingest_tab, bg=self.bg_tertiary)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Use PanedWindow for resizable split
        paned_window = ttk.PanedWindow(content_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # --- Top Section: Ingested Documents ---
        ingested_frame = tk.Frame(paned_window, bg=self.bg_tertiary)
        
        ingested_header = tk.Label(
            ingested_frame,
            text="✅ Ingested Documents",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_tertiary,
            fg=self.success_color,
            anchor=tk.W
        )
        ingested_header.pack(fill=tk.X, pady=(0, 5))
        
        # Ingested documents list with scrollbar
        ingested_list_frame = tk.Frame(ingested_frame, bg=self.text_bg, 
                                      highlightthickness=1, highlightbackground=self.border_color)
        ingested_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.ingested_text = scrolledtext.ScrolledText(
            ingested_list_frame,
            wrap=tk.WORD,
            height=8,
            state=tk.DISABLED,
            bg=self.text_bg,
            fg=self.fg_color,
            font=("Consolas", 9),
            relief=tk.FLAT,
            padx=10,
            pady=10,
            selectbackground=self.highlight_bg,
            selectforeground=self.fg_color,
            borderwidth=0
        )
        self.ingested_text.pack(fill=tk.BOTH, expand=True)
        
        paned_window.add(ingested_frame, weight=1)
        
        # --- Bottom Section: Ingestion Log ---
        log_frame = tk.Frame(paned_window, bg=self.bg_tertiary)
        
        log_header_frame = tk.Frame(log_frame, bg=self.bg_tertiary)
        log_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        log_header = tk.Label(
            log_header_frame,
            text="📝 Ingestion Log",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_tertiary,
            fg=self.accent_color,
            anchor=tk.W
        )
        log_header.pack(side=tk.LEFT)
        
        # Clear log button
        clear_log_button = tk.Button(
            log_header_frame,
            text="🗑️ Clear",
            command=self.clear_ingestion_log,
            font=("Segoe UI", 8),
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.button_hover,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.button_bg
        )
        clear_log_button.pack(side=tk.RIGHT)
        self.create_tooltip(clear_log_button, "Clear the ingestion log")
        self.add_button_hover_effect(clear_log_button)
        
        # Ingestion log with scrollbar
        log_text_frame = tk.Frame(log_frame, bg=self.text_bg, 
                                  highlightthickness=1, highlightbackground=self.border_color)
        log_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.ingestion_log = scrolledtext.ScrolledText(
            log_text_frame,
            wrap=tk.WORD,
            height=8,
            state=tk.DISABLED,
            bg=self.text_bg,
            fg=self.fg_secondary,
            font=("Consolas", 8),
            relief=tk.FLAT,
            padx=10,
            pady=10,
            selectbackground=self.highlight_bg,
            selectforeground=self.fg_color,
            borderwidth=0
        )
        self.ingestion_log.pack(fill=tk.BOTH, expand=True)
        
        # Configure log tags for different message types
        self.ingestion_log.tag_config("timestamp", foreground=self.fg_muted, font=("Consolas", 8))
        self.ingestion_log.tag_config("info", foreground=self.fg_secondary)
        self.ingestion_log.tag_config("success", foreground=self.success_color)
        self.ingestion_log.tag_config("warning", foreground=self.warning_color)
        self.ingestion_log.tag_config("error", foreground=self.error_color)
        self.ingestion_log.tag_config("progress", foreground=self.accent_color)
        
        paned_window.add(log_frame, weight=1)
        
        # Add initial message to the log
        self.log_to_ingest_tab("📋 Ingestion log initialized. Start an ingestion to see progress here.", "info")
        
        # --- Statistics Section ---
        stats_frame = tk.Frame(content_frame, bg=self.bg_secondary, 
                              highlightthickness=1, highlightbackground=self.border_color)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        stats_inner = tk.Frame(stats_frame, bg=self.bg_secondary, padx=15, pady=10)
        stats_inner.pack(fill=tk.X)
        
        self.ingest_stats_label = tk.Label(
            stats_inner,
            text="Loading statistics...",
            font=("Segoe UI", 9),
            bg=self.bg_secondary,
            fg=self.fg_secondary,
            anchor=tk.W
        )
        self.ingest_stats_label.pack(side=tk.LEFT)
        
        # Delay initial load of ingest list until after mainloop starts
        self.root.after(INIT_REFRESH_DELAY_MS, self.refresh_ingest_list)
    
    def create_tests_tab(self):
        """Create the Tests tab for running Python test scripts."""
        tests_tab = tk.Frame(self.notebook, bg=self.bg_tertiary)
        self.notebook.add(tests_tab, text="🧪 Tests")
        
        # Header section
        tests_header = tk.Frame(tests_tab, bg=self.bg_tertiary, padx=15, pady=10)
        tests_header.pack(fill=tk.X)
        
        tests_label = tk.Label(
            tests_header,
            text="🧪 Test Suite Runner",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_tertiary,
            fg=self.fg_color
        )
        tests_label.pack(side=tk.LEFT)
        
        # Stop button for running tests
        self.stop_test_button = tk.Button(
            tests_header,
            text="⏹ Stop",
            command=self.stop_running_test,
            font=("Segoe UI", 9),
            bg=self.error_color,
            fg=self.bg_color,
            activebackground="#ff6b6b",
            activeforeground=self.bg_color,
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.error_color,
            state=tk.DISABLED
        )
        self.stop_test_button.pack(side=tk.RIGHT, padx=(0, 5))
        self.create_tooltip(self.stop_test_button, "Stop the currently running test")
        self.add_button_hover_effect(self.stop_test_button, hover_color="#ff6b6b")
        
        # Clear button
        clear_test_button = tk.Button(
            tests_header,
            text="🗑️ Clear",
            command=self.clear_test_output,
            font=("Segoe UI", 9),
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.button_hover,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.button_bg
        )
        clear_test_button.pack(side=tk.RIGHT)
        self.create_tooltip(clear_test_button, "Clear test output")
        self.add_button_hover_effect(clear_test_button)
        
        # Separator line
        separator_line = tk.Frame(tests_tab, height=1, bg=self.border_color)
        separator_line.pack(fill=tk.X)
        
        # Main content with split panes
        content_frame = tk.Frame(tests_tab, bg=self.bg_tertiary)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Use PanedWindow for resizable split
        paned_window = ttk.PanedWindow(content_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # --- Top Section: Test Buttons ---
        buttons_frame = tk.Frame(paned_window, bg=self.bg_tertiary)
        
        buttons_header = tk.Label(
            buttons_frame,
            text="📋 Test Categories",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_tertiary,
            fg=self.accent_color,
            anchor=tk.W
        )
        buttons_header.pack(fill=tk.X, pady=(0, 10))
        
        # Create a grid for test buttons
        button_grid = tk.Frame(buttons_frame, bg=self.bg_tertiary)
        button_grid.pack(fill=tk.BOTH, expand=True)
        
        # Button style for test buttons
        test_button_style = {
            "font": ("Segoe UI", 9),
            "bg": self.button_bg,
            "fg": self.fg_color,
            "activebackground": self.button_hover,
            "activeforeground": self.fg_color,
            "relief": tk.FLAT,
            "padx": 15,
            "pady": 8,
            "cursor": "hand2",
            "borderwidth": 1,
            "highlightthickness": 1,
            "highlightbackground": self.button_bg
        }
        
        # Row 0: All Tests
        all_tests_btn = tk.Button(
            button_grid,
            text="🚀 Run All Tests (pytest)",
            command=lambda: self.run_test_suite("all"),
            **test_button_style
        )
        all_tests_btn.grid(row=0, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(all_tests_btn, "Run the complete pytest test suite")
        self.add_button_hover_effect(all_tests_btn)
        
        # Row 1: Plugin Tests
        plugin_tests_btn = tk.Button(
            button_grid,
            text="🔌 Plugin Tests",
            command=lambda: self.run_test_suite("plugin"),
            **test_button_style
        )
        plugin_tests_btn.grid(row=1, column=0, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(plugin_tests_btn, "Run IPC, RAG, and UE Python API tests")
        self.add_button_hover_effect(plugin_tests_btn)
        
        # Row 1: Unit Tests
        unit_tests_btn = tk.Button(
            button_grid,
            text="⚙️ Unit Tests",
            command=lambda: self.run_test_suite("unit"),
            **test_button_style
        )
        unit_tests_btn.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(unit_tests_btn, "Run unit tests only")
        self.add_button_hover_effect(unit_tests_btn)
        
        # Row 2: Integration Tests
        integration_tests_btn = tk.Button(
            button_grid,
            text="🔗 Integration Tests",
            command=lambda: self.run_test_suite("integration"),
            **test_button_style
        )
        integration_tests_btn.grid(row=2, column=0, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(integration_tests_btn, "Run integration tests")
        self.add_button_hover_effect(integration_tests_btn)
        
        # Row 2: Phase 3 Tests
        phase3_tests_btn = tk.Button(
            button_grid,
            text="🎯 Phase 3 Tests",
            command=lambda: self.run_test_suite("phase3"),
            **test_button_style
        )
        phase3_tests_btn.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(phase3_tests_btn, "Run Phase 3 agent tests")
        self.add_button_hover_effect(phase3_tests_btn)
        
        # Row 3: Validation Scripts
        validation_btn = tk.Button(
            button_grid,
            text="✅ Validation Scripts",
            command=lambda: self.run_test_suite("validation"),
            **test_button_style
        )
        validation_btn.grid(row=3, column=0, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(validation_btn, "Run installation and compatibility checks")
        self.add_button_hover_effect(validation_btn)
        
        # Row 3: Remote Control Tests
        remote_tests_btn = tk.Button(
            button_grid,
            text="🌐 Remote Control Tests",
            command=lambda: self.run_test_suite("remote"),
            **test_button_style
        )
        remote_tests_btn.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(remote_tests_btn, "Run remote control API tests")
        self.add_button_hover_effect(remote_tests_btn)
        
        # Row 4: MCP Tests
        mcp_tests_btn = tk.Button(
            button_grid,
            text="🎮 MCP Tests",
            command=lambda: self.run_test_suite("mcp"),
            **test_button_style
        )
        mcp_tests_btn.grid(row=4, column=0, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(mcp_tests_btn, "Run MCP server tests")
        self.add_button_hover_effect(mcp_tests_btn)
        
        # Row 4: GUI Tests
        gui_tests_btn = tk.Button(
            button_grid,
            text="🖥️ GUI Tests",
            command=lambda: self.run_test_suite("gui"),
            **test_button_style
        )
        gui_tests_btn.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(gui_tests_btn, "Run GUI component tests")
        self.add_button_hover_effect(gui_tests_btn)
        
        # Row 5: Check Compatibility
        compat_btn = tk.Button(
            button_grid,
            text="🔍 Check Compatibility",
            command=lambda: self.run_test_suite("compatibility"),
            **test_button_style
        )
        compat_btn.grid(row=5, column=0, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(compat_btn, "Check system compatibility")
        self.add_button_hover_effect(compat_btn)
        
        # Row 5: Install Dependencies
        install_btn = tk.Button(
            button_grid,
            text="📦 Install Dependencies",
            command=lambda: self.run_test_suite("install"),
            **test_button_style
        )
        install_btn.grid(row=5, column=1, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(install_btn, "Run dependency installation script")
        self.add_button_hover_effect(install_btn)
        
        # Configure grid weights for equal column sizing
        button_grid.columnconfigure(0, weight=1)
        button_grid.columnconfigure(1, weight=1)
        
        paned_window.add(buttons_frame, weight=0)
        
        # --- Bottom Section: Test Output ---
        output_frame = tk.Frame(paned_window, bg=self.bg_tertiary)
        
        output_header_frame = tk.Frame(output_frame, bg=self.bg_tertiary)
        output_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        output_header = tk.Label(
            output_header_frame,
            text="📊 Test Output",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_tertiary,
            fg=self.accent_color,
            anchor=tk.W
        )
        output_header.pack(side=tk.LEFT)
        
        # Test status label
        self.test_status_label = tk.Label(
            output_header_frame,
            text="Ready",
            font=("Segoe UI", 9),
            bg=self.bg_tertiary,
            fg=self.fg_muted,
            anchor=tk.W
        )
        self.test_status_label.pack(side=tk.RIGHT)
        
        # Test output with scrollbar
        output_text_frame = tk.Frame(output_frame, bg=self.text_bg, 
                                     highlightthickness=1, highlightbackground=self.border_color)
        output_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.test_output = scrolledtext.ScrolledText(
            output_text_frame,
            wrap=tk.WORD,
            height=15,
            state=tk.DISABLED,
            bg=self.text_bg,
            fg=self.fg_color,
            font=("Consolas", 9),
            relief=tk.FLAT,
            padx=10,
            pady=10,
            selectbackground=self.highlight_bg,
            selectforeground=self.fg_color,
            borderwidth=0
        )
        self.test_output.pack(fill=tk.BOTH, expand=True)
        
        # Configure test output tags
        self.test_output.tag_config("header", foreground=self.accent_color, font=("Consolas", 10, "bold"))
        self.test_output.tag_config("pass", foreground=self.success_color, font=("Consolas", 9))
        self.test_output.tag_config("fail", foreground=self.error_color, font=("Consolas", 9))
        self.test_output.tag_config("warning", foreground=self.warning_color, font=("Consolas", 9))
        self.test_output.tag_config("info", foreground=self.fg_secondary, font=("Consolas", 9))
        self.test_output.tag_config("command", foreground=self.fg_muted, font=("Consolas", 8, "italic"))
        
        # Store button references for later access
        self.test_buttons = [
            all_tests_btn, plugin_tests_btn, unit_tests_btn,
            integration_tests_btn, phase3_tests_btn, validation_btn, remote_tests_btn,
            mcp_tests_btn, gui_tests_btn, compat_btn, install_btn
        ]
        
        paned_window.add(output_frame, weight=1)
        
        # Initialize test running state
        self.current_test_process = None
        self.test_process_lock = threading.Lock()
        
        # Add initial message
        self.test_output.config(state=tk.NORMAL)
        self.test_output.insert(tk.END, "🧪 Test Suite Runner\n\n", "header")
        self.test_output.insert(tk.END, "Select a test category above to run tests.\n", "info")
        self.test_output.insert(tk.END, "Test results will appear here.\n", "info")
        self.test_output.config(state=tk.DISABLED)

    def create_unreal_mcp_tab(self):
        """Create the Unreal MCP tab for Unreal Engine integration via MCP."""
        unreal_tab = tk.Frame(self.notebook, bg=self.bg_tertiary)
        self.notebook.add(unreal_tab, text="🎮 Unreal MCP")
        
        # Header section
        unreal_header = tk.Frame(unreal_tab, bg=self.bg_tertiary, padx=15, pady=10)
        unreal_header.pack(fill=tk.X)
        
        unreal_label = tk.Label(
            unreal_header,
            text="🎮 Unreal Engine MCP Integration",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_tertiary,
            fg=self.fg_color
        )
        unreal_label.pack(side=tk.LEFT)
        
        # Connection status indicator
        self.unreal_connection_frame = tk.Frame(unreal_header, bg=self.bg_tertiary)
        self.unreal_connection_frame.pack(side=tk.RIGHT)
        
        self.unreal_status_indicator = tk.Label(
            self.unreal_connection_frame,
            text="●",
            font=("Segoe UI", 10),
            bg=self.bg_tertiary,
            fg=self.fg_muted
        )
        self.unreal_status_indicator.pack(side=tk.LEFT, padx=(0, 5))
        
        self.unreal_status_label = tk.Label(
            self.unreal_connection_frame,
            text="Disconnected",
            font=("Segoe UI", 9),
            bg=self.bg_tertiary,
            fg=self.fg_muted
        )
        self.unreal_status_label.pack(side=tk.LEFT)
        
        # Separator line
        separator_line = tk.Frame(unreal_tab, height=1, bg=self.border_color)
        separator_line.pack(fill=tk.X)
        
        # Main content area
        content_frame = tk.Frame(unreal_tab, bg=self.bg_tertiary)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Use PanedWindow for resizable split
        paned_window = ttk.PanedWindow(content_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # --- Top Section: Connection and Tools ---
        tools_frame = tk.Frame(paned_window, bg=self.bg_tertiary)
        
        # Connection controls
        connection_frame = tk.Frame(tools_frame, bg=self.bg_tertiary)
        connection_frame.pack(fill=tk.X, pady=(0, 10))
        
        connection_label = tk.Label(
            connection_frame,
            text="🔌 Connection",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_tertiary,
            fg=self.accent_color,
            anchor=tk.W
        )
        connection_label.pack(side=tk.LEFT)
        
        # Connection buttons frame
        conn_buttons_frame = tk.Frame(connection_frame, bg=self.bg_tertiary)
        conn_buttons_frame.pack(side=tk.RIGHT)
        
        # Button style for MCP buttons
        mcp_button_style = {
            "font": ("Segoe UI", 9),
            "bg": self.button_bg,
            "fg": self.fg_color,
            "activebackground": self.button_hover,
            "activeforeground": self.fg_color,
            "relief": tk.FLAT,
            "padx": 15,
            "pady": 8,
            "cursor": "hand2",
            "borderwidth": 1,
            "highlightthickness": 1,
            "highlightbackground": self.button_bg
        }
        
        self.unreal_connect_button = tk.Button(
            conn_buttons_frame,
            text="🔗 Connect",
            command=self.connect_to_unreal,
            **mcp_button_style
        )
        self.unreal_connect_button.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(self.unreal_connect_button, "Connect to Unreal Engine via MCP")
        self.add_button_hover_effect(self.unreal_connect_button)
        
        self.unreal_disconnect_button = tk.Button(
            conn_buttons_frame,
            text="🔌 Disconnect",
            command=self.disconnect_from_unreal,
            state=tk.DISABLED,
            **mcp_button_style
        )
        self.unreal_disconnect_button.pack(side=tk.LEFT)
        self.create_tooltip(self.unreal_disconnect_button, "Disconnect from Unreal Engine")
        self.add_button_hover_effect(self.unreal_disconnect_button)
        
        # Tools section
        tools_label = tk.Label(
            tools_frame,
            text="🛠️ Quick Tools",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_tertiary,
            fg=self.accent_color,
            anchor=tk.W
        )
        tools_label.pack(fill=tk.X, pady=(10, 10))
        
        # Create a grid for tool buttons
        tool_grid = tk.Frame(tools_frame, bg=self.bg_tertiary)
        tool_grid.pack(fill=tk.BOTH, expand=True)
        
        # Row 0: Project Info and Map Info
        project_info_btn = tk.Button(
            tool_grid,
            text="📊 Project Info",
            command=lambda: self.run_mcp_tool("editor_project_info"),
            **mcp_button_style
        )
        project_info_btn.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(project_info_btn, "Get project information")
        self.add_button_hover_effect(project_info_btn)
        
        map_info_btn = tk.Button(
            tool_grid,
            text="🗺️ Map Info",
            command=lambda: self.run_mcp_tool("editor_get_map_info"),
            **mcp_button_style
        )
        map_info_btn.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(map_info_btn, "Get current map information")
        self.add_button_hover_effect(map_info_btn)
        
        # Row 1: List Assets and World Outliner
        list_assets_btn = tk.Button(
            tool_grid,
            text="📦 List Assets",
            command=lambda: self.run_mcp_tool("editor_list_assets"),
            **mcp_button_style
        )
        list_assets_btn.grid(row=1, column=0, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(list_assets_btn, "List all project assets")
        self.add_button_hover_effect(list_assets_btn)
        
        world_outliner_btn = tk.Button(
            tool_grid,
            text="🌍 World Outliner",
            command=lambda: self.run_mcp_tool("editor_get_world_outliner"),
            **mcp_button_style
        )
        world_outliner_btn.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(world_outliner_btn, "Get all actors in the current world")
        self.add_button_hover_effect(world_outliner_btn)
        
        # Row 2: Screenshot and List Tools
        screenshot_btn = tk.Button(
            tool_grid,
            text="📸 Screenshot",
            command=lambda: self.run_mcp_tool("editor_take_screenshot"),
            **mcp_button_style
        )
        screenshot_btn.grid(row=2, column=0, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(screenshot_btn, "Take a screenshot of the editor viewport")
        self.add_button_hover_effect(screenshot_btn)
        
        list_tools_btn = tk.Button(
            tool_grid,
            text="📋 List All Tools",
            command=self.list_mcp_tools,
            **mcp_button_style
        )
        list_tools_btn.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(list_tools_btn, "List all available MCP tools")
        self.add_button_hover_effect(list_tools_btn)
        
        # Configure grid weights for equal column sizing
        tool_grid.columnconfigure(0, weight=1)
        tool_grid.columnconfigure(1, weight=1)
        
        # Store tool button references
        self.mcp_tool_buttons = [
            project_info_btn, map_info_btn, list_assets_btn,
            world_outliner_btn, screenshot_btn, list_tools_btn
        ]
        
        paned_window.add(tools_frame, weight=0)
        
        # --- Middle Section: Python Code Execution ---
        python_frame = tk.Frame(paned_window, bg=self.bg_tertiary)
        
        python_header_frame = tk.Frame(python_frame, bg=self.bg_tertiary)
        python_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        python_label = tk.Label(
            python_header_frame,
            text="🐍 Python Execution",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_tertiary,
            fg=self.accent_color,
            anchor=tk.W
        )
        python_label.pack(side=tk.LEFT)
        
        # Execute button for Python
        execute_python_btn = tk.Button(
            python_header_frame,
            text="▶ Execute",
            command=self.execute_unreal_python,
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg="#20232b",
            activebackground=self.accent_hover,
            activeforeground="#20232b",
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            borderwidth=0
        )
        execute_python_btn.pack(side=tk.RIGHT)
        self.create_tooltip(execute_python_btn, "Execute Python code in Unreal Editor (Ctrl+Enter)")
        self.add_button_hover_effect(execute_python_btn, hover_color=self.accent_hover)
        
        # Python input area
        python_input_frame = tk.Frame(python_frame, bg=self.text_bg, 
                                     highlightthickness=1, highlightbackground=self.border_color)
        python_input_frame.pack(fill=tk.BOTH, expand=True)
        
        self.unreal_python_input = scrolledtext.ScrolledText(
            python_input_frame,
            wrap=tk.WORD,
            height=5,
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.accent_color,
            font=("Consolas", 10),
            relief=tk.FLAT,
            padx=10,
            pady=10,
            selectbackground=self.highlight_bg,
            selectforeground=self.fg_color,
            borderwidth=0
        )
        self.unreal_python_input.pack(fill=tk.BOTH, expand=True)
        
        # Add placeholder text
        self.unreal_python_input.insert(tk.END, MCP_PYTHON_PLACEHOLDER)
        
        # Bind Ctrl+Enter for execution
        self.unreal_python_input.bind("<Control-Return>", lambda e: self.execute_unreal_python())
        
        paned_window.add(python_frame, weight=1)
        
        # --- Console Command Section ---
        console_frame = tk.Frame(paned_window, bg=self.bg_tertiary)
        
        console_header_frame = tk.Frame(console_frame, bg=self.bg_tertiary)
        console_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        console_label = tk.Label(
            console_header_frame,
            text="💻 Console Command",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_tertiary,
            fg=self.accent_color,
            anchor=tk.W
        )
        console_label.pack(side=tk.LEFT)
        
        # Console input with entry and button
        console_input_frame = tk.Frame(console_frame, bg=self.bg_tertiary)
        console_input_frame.pack(fill=tk.X, pady=(0, 5))
        
        console_entry_frame = tk.Frame(console_input_frame, bg=self.text_bg, highlightthickness=1,
                                      highlightbackground=self.border_color)
        console_entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.unreal_console_entry = tk.Entry(
            console_entry_frame,
            font=("Consolas", 10),
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.accent_color,
            relief=tk.FLAT,
            highlightthickness=0,
            borderwidth=0
        )
        self.unreal_console_entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        self.unreal_console_entry.insert(0, MCP_CONSOLE_PLACEHOLDER)
        self.unreal_console_entry.bind("<Return>", lambda e: self.execute_console_command())
        
        execute_console_btn = tk.Button(
            console_input_frame,
            text="▶ Run",
            command=self.execute_console_command,
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg="#20232b",
            activebackground=self.accent_hover,
            activeforeground="#20232b",
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            borderwidth=0
        )
        execute_console_btn.pack(side=tk.RIGHT)
        self.create_tooltip(execute_console_btn, "Run console command in Unreal Engine")
        self.add_button_hover_effect(execute_console_btn, hover_color=self.accent_hover)
        
        paned_window.add(console_frame, weight=0)
        
        # --- Bottom Section: Output Display ---
        output_frame = tk.Frame(paned_window, bg=self.bg_tertiary)
        
        output_header_frame = tk.Frame(output_frame, bg=self.bg_tertiary)
        output_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        output_label = tk.Label(
            output_header_frame,
            text="📊 Output",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_tertiary,
            fg=self.accent_color,
            anchor=tk.W
        )
        output_label.pack(side=tk.LEFT)
        
        # Clear output button
        clear_output_btn = tk.Button(
            output_header_frame,
            text="🗑️ Clear",
            command=self.clear_mcp_output,
            font=("Segoe UI", 8),
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.button_hover,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.button_bg
        )
        clear_output_btn.pack(side=tk.RIGHT)
        self.create_tooltip(clear_output_btn, "Clear output display")
        self.add_button_hover_effect(clear_output_btn)
        
        # Output display
        output_text_frame = tk.Frame(output_frame, bg=self.text_bg, 
                                     highlightthickness=1, highlightbackground=self.border_color)
        output_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.unreal_mcp_output = scrolledtext.ScrolledText(
            output_text_frame,
            wrap=tk.WORD,
            height=10,
            state=tk.DISABLED,
            bg=self.text_bg,
            fg=self.fg_color,
            font=("Consolas", 9),
            relief=tk.FLAT,
            padx=10,
            pady=10,
            selectbackground=self.highlight_bg,
            selectforeground=self.fg_color,
            borderwidth=0
        )
        self.unreal_mcp_output.pack(fill=tk.BOTH, expand=True)
        
        # Configure output tags
        self.unreal_mcp_output.tag_config("header", foreground=self.accent_color, font=("Consolas", 10, "bold"))
        self.unreal_mcp_output.tag_config("success", foreground=self.success_color, font=("Consolas", 9))
        self.unreal_mcp_output.tag_config("error", foreground=self.error_color, font=("Consolas", 9))
        self.unreal_mcp_output.tag_config("info", foreground=self.fg_secondary, font=("Consolas", 9))
        self.unreal_mcp_output.tag_config("json", foreground=self.fg_color, font=("Consolas", 9))
        self.unreal_mcp_output.tag_config("timestamp", foreground=self.fg_muted, font=("Consolas", 8))
        
        paned_window.add(output_frame, weight=1)
        
        # Initialize MCP server reference
        self.unreal_mcp_server = None
        self.mcp_connected = False
        
        # Initialize UE log capture
        self.ue_log_capture = UELogCapture()
        self.ue_log_session_active = False
        
        # Add initial message
        self.log_mcp_output("🎮 Unreal Engine MCP Integration\n\n", "header")
        self.log_mcp_output("Connect to Unreal Engine to use MCP tools.\n", "info")
        self.log_mcp_output("Prerequisites:\n", "info")
        self.log_mcp_output("  1. Unreal Engine is running\n", "info")
        self.log_mcp_output("  2. Python Editor Script Plugin is enabled\n", "info")
        self.log_mcp_output("  3. Remote Execution is enabled in Project Settings\n\n", "info")
        self.log_mcp_output("Click 'Connect' to establish connection.\n", "info")

    def connect_to_unreal(self):
        """Connect to Unreal Engine via MCP server."""
        self.log_mcp_output("\n" + "="*50 + "\n", "info")
        self.log_mcp_output("Connecting to Unreal Engine...\n", "header")
        
        # Disable connect button while connecting
        self.unreal_connect_button.config(state=tk.DISABLED)
        self.update_unreal_status("Connecting...", self.accent_color)
        
        # Run connection in a thread
        def connect_thread():
            try:
                # Import the MCP server
                from mcp_server import UnrealMCPServer
                
                self.unreal_mcp_server = UnrealMCPServer()
                success = self.unreal_mcp_server.start()
                
                # Validate the return type and check if connected
                if success is True or (success is not False and self.unreal_mcp_server.is_connected()):
                    self.mcp_connected = True
                    try:
                        self.root.after(0, self._on_unreal_connected)
                    except RuntimeError as e:
                        if "main thread is not in main loop" in str(e):
                            self.logger.debug("Unreal connection callback deferred - mainloop not started yet")
                        else:
                            self.logger.error(f"Unexpected RuntimeError in connect_thread: {e}")
                            raise
                else:
                    try:
                        self.root.after(0, self._on_unreal_connection_failed, 
                                       "Could not connect to Unreal Engine. Make sure it's running with Remote Execution enabled.")
                    except RuntimeError as e:
                        if "main thread is not in main loop" in str(e):
                            self.logger.debug("Unreal connection failure callback deferred - mainloop not started yet")
                        else:
                            self.logger.error(f"Unexpected RuntimeError in connect_thread: {e}")
                            raise
            except ImportError as e:
                try:
                    self.root.after(0, self._on_unreal_connection_failed, 
                                   f"MCP server module not found: {e}")
                except RuntimeError as e:
                    if "main thread is not in main loop" in str(e):
                        self.logger.debug("Unreal import error callback deferred - mainloop not started yet")
                    else:
                        self.logger.error(f"Unexpected RuntimeError in connect_thread: {e}")
                        raise
            except Exception as e:
                try:
                    self.root.after(0, self._on_unreal_connection_failed, str(e))
                except RuntimeError as e:
                    if "main thread is not in main loop" in str(e):
                        self.logger.debug("Unreal exception callback deferred - mainloop not started yet")
                    else:
                        self.logger.error(f"Unexpected RuntimeError in connect_thread: {e}")
                        raise
        
        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()
    
    def _on_unreal_connected(self):
        """Handle successful Unreal Engine connection."""
        self.update_unreal_status("Connected", self.success_color)
        self.unreal_connect_button.config(state=tk.DISABLED)
        self.unreal_disconnect_button.config(state=tk.NORMAL)
        
        # Enable tool buttons
        for btn in self.mcp_tool_buttons:
            btn.config(state=tk.NORMAL)
        
        self.log_mcp_output("✅ Connected to Unreal Engine!\n", "success")
        self.log_mcp_output("You can now use the MCP tools.\n", "info")
        
        # Start UE log capture session
        try:
            log_path = self.ue_log_capture.start_session("gui_session")
            self.ue_log_session_active = True
            self.log_mcp_output(f"📝 Log capture started: {log_path.name}\n", "info")
            self.ue_log_capture.log("Connected to Unreal Engine via GUI", source="GUI", level="INFO")
        except Exception as e:
            self.log_mcp_output(f"⚠️ Warning: Could not start log capture: {e}\n", "warning")
        
        # Update analytics with connection status
        self.project_analytics.update_connection_metrics(ue_connected=True)
        
        # Set up UE data collector with MCP server
        if hasattr(self, "ue_data_collector") and self.ue_data_collector is not None:
            self.ue_data_collector.mcp_server = self.unreal_mcp_server
        else:
            self.ue_data_collector = UEDataCollector(mcp_server=self.unreal_mcp_server)
        
        # Get project info on connection
        self.run_mcp_tool("editor_project_info")
    
    def _on_unreal_connection_failed(self, error_message):
        """Handle failed Unreal Engine connection."""
        self.update_unreal_status("Connection Failed", self.error_color)
        self.unreal_connect_button.config(state=tk.NORMAL)
        self.unreal_disconnect_button.config(state=tk.DISABLED)
        self.mcp_connected = False
        
        self.log_mcp_output(f"❌ Connection failed: {error_message}\n", "error")
        self.log_mcp_output("\nTroubleshooting:\n", "info")
        self.log_mcp_output("  1. Ensure Unreal Engine Editor is running\n", "info")
        self.log_mcp_output("  2. Enable Python Editor Script Plugin (Edit → Plugins)\n", "info")
        self.log_mcp_output("  3. Enable Remote Execution (Project Settings → Python)\n", "info")
        self.log_mcp_output("  4. Try restarting Unreal Engine\n", "info")
    
    def disconnect_from_unreal(self):
        """Disconnect from Unreal Engine."""
        # End UE log capture session
        if self.ue_log_session_active:
            try:
                self.ue_log_capture.log("Disconnecting from Unreal Engine", source="GUI", level="INFO")
                self.ue_log_capture.end_session()
                self.ue_log_session_active = False
                self.log_mcp_output("📝 Log capture session ended.\n", "info")
            except Exception as e:
                self.log_mcp_output(f"⚠️ Warning: Error ending log capture: {e}\n", "warning")
        
        if self.unreal_mcp_server:
            try:
                self.unreal_mcp_server.stop()
            except Exception as e:
                self.log_mcp_output(f"Warning: Error during disconnect: {e}\n", "error")
            finally:
                self.unreal_mcp_server = None
        
        self.mcp_connected = False
        self.update_unreal_status("Disconnected", self.fg_muted)
        self.unreal_connect_button.config(state=tk.NORMAL)
        self.unreal_disconnect_button.config(state=tk.DISABLED)
        
        # Update analytics with connection status
        self.project_analytics.update_connection_metrics(ue_connected=False)
        
        self.log_mcp_output("\n🔌 Disconnected from Unreal Engine.\n", "info")
    
    def update_unreal_status(self, status_text, color):
        """Update the Unreal connection status display."""
        self.unreal_status_indicator.config(fg=color)
        self.unreal_status_label.config(text=status_text, fg=color)
    
    def run_mcp_tool(self, tool_name, arguments=None):
        """Run an MCP tool and display results."""
        if not self.mcp_connected or not self.unreal_mcp_server:
            self.log_mcp_output("❌ Not connected to Unreal Engine. Please connect first.\n", "error")
            return
        
        arguments = arguments or {}
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.log_mcp_output(f"\n[{timestamp}] ", "timestamp")
        self.log_mcp_output(f"Running: {tool_name}\n", "header")
        
        # Log the tool execution (result will be logged in _display_tool_result)
        if self.ue_log_session_active:
            params_str = json.dumps(arguments) if arguments else "{}"
            self.ue_log_capture.log(f"Executing tool: {tool_name} with parameters: {params_str}", 
                                   source="MCP-Tool", level="INFO")
        
        def run_tool_thread():
            try:
                result = self.unreal_mcp_server.handle_tool_call(tool_name, arguments)
                self.root.after(0, self._display_tool_result, result)
            except Exception as ex:
                error_msg = str(ex)
                # Log the error
                if self.ue_log_session_active:
                    self.ue_log_capture.log(f"Tool execution error: {error_msg}", source="MCP-Error", level="ERROR")
                self.root.after(0, lambda msg=error_msg: self.log_mcp_output(f"❌ Error: {msg}\n", "error"))
        
        thread = threading.Thread(target=run_tool_thread, daemon=True)
        thread.start()
    
    def _display_tool_result(self, result):
        """Display the result of an MCP tool call."""
        # Capture result for logging
        result_parts = []
        is_error = result.get("isError")
        
        if is_error:
            for content in result.get("content", []):
                if content.get("type") == "text":
                    error_text = content['text']
                    result_parts.append(error_text)
                    self.log_mcp_output(f"❌ {error_text}\n", "error")
        else:
            for content in result.get("content", []):
                if content.get("type") == "text":
                    # Try to pretty-print JSON
                    try:
                        data = json.loads(content["text"])
                        formatted = json.dumps(data, indent=2)
                        result_parts.append(formatted)
                        self.log_mcp_output(formatted + "\n", "json")
                    except json.JSONDecodeError:
                        text = content["text"]
                        result_parts.append(text)
                        self.log_mcp_output(text + "\n", "info")
                elif content.get("type") == "image":
                    image_info = f"[Image: {content.get('mimeType', 'unknown')}]"
                    result_parts.append(image_info)
                    self.log_mcp_output(f"{image_info}\n", "info")
        
        # Log the tool result to file
        result_text = '\n'.join(result_parts)
        if self.ue_log_session_active and result_text:
            level = "ERROR" if is_error else "INFO"
            self.ue_log_capture.log(f"Tool Result:\n{result_text}", source="MCP-Result", level=level)
    
    def list_mcp_tools(self):
        """List all available MCP tools."""
        if not self.mcp_connected or not self.unreal_mcp_server:
            self.log_mcp_output("❌ Not connected to Unreal Engine. Please connect first.\n", "error")
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_mcp_output(f"\n[{timestamp}] ", "timestamp")
        self.log_mcp_output("Available MCP Tools:\n\n", "header")
        
        tools = self.unreal_mcp_server.list_tools()
        for tool in tools:
            self.log_mcp_output(f"  📦 {tool['name']}\n", "success")
            self.log_mcp_output(f"     {tool['description']}\n\n", "info")
    
    def execute_unreal_python(self):
        """Execute Python code in Unreal Engine."""
        if not self.mcp_connected or not self.unreal_mcp_server:
            self.log_mcp_output("❌ Not connected to Unreal Engine. Please connect first.\n", "error")
            return
        
        code = self.unreal_python_input.get("1.0", tk.END).strip()
        if not code:
            self.log_mcp_output("❌ No Python code to execute.\n", "error")
            return
        
        # Log the Python execution (we'll capture the result in _display_tool_result)
        if self.ue_log_session_active:
            self.ue_log_capture.log(f"Executing Python code:\n{code}", source="GUI-Python", level="INFO")
        
        self.run_mcp_tool("editor_run_python", {"code": code})
    
    def execute_console_command(self):
        """Execute a console command in Unreal Engine."""
        if not self.mcp_connected or not self.unreal_mcp_server:
            self.log_mcp_output("❌ Not connected to Unreal Engine. Please connect first.\n", "error")
            return
        
        command = self.unreal_console_entry.get().strip()
        if not command:
            self.log_mcp_output("❌ No console command to execute.\n", "error")
            return
        
        # Log the console command execution
        if self.ue_log_session_active:
            self.ue_log_capture.log(f"Executing console command: {command}", source="GUI-Console", level="INFO")
        
        self.run_mcp_tool("editor_console_command", {"command": command})
    
    def log_mcp_output(self, message, tag="info"):
        """Append a message to the MCP output display."""
        self.unreal_mcp_output.config(state=tk.NORMAL)
        self.unreal_mcp_output.insert(tk.END, message, tag)
        self.unreal_mcp_output.see(tk.END)
        self.unreal_mcp_output.config(state=tk.DISABLED)
    
    def clear_mcp_output(self):
        """Clear the MCP output display."""
        self.unreal_mcp_output.config(state=tk.NORMAL)
        self.unreal_mcp_output.delete(1.0, tk.END)
        self.unreal_mcp_output.insert(tk.END, "🎮 Unreal Engine MCP Integration\n\n", "header")
        self.unreal_mcp_output.insert(tk.END, "Output cleared.\n", "info")
        self.unreal_mcp_output.config(state=tk.DISABLED)

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
    
    def refresh_ingest_list(self):
        """Refresh the ingestion list by querying the vector database."""
        def refresh_in_thread():
            try:
                # Get ingested documents from the database
                ingested_docs = self.get_ingested_documents()
                
                # Update UI on main thread - use try-except to handle early calls
                try:
                    self.root.after(0, self._update_ingest_list_ui, ingested_docs)
                except RuntimeError as e:
                    if "main thread is not in main loop" in str(e):
                        self.logger.debug("Ingest list update deferred - mainloop not started yet")
                    else:
                        self.logger.error(f"Unexpected RuntimeError in refresh_ingest_list: {e}")
                        raise
            except Exception as e:
                try:
                    self.root.after(0, self._show_ingest_error, str(e))
                except RuntimeError as e:
                    if "main thread is not in main loop" in str(e):
                        self.logger.debug("Ingest error display deferred - mainloop not started yet")
                    else:
                        self.logger.error(f"Unexpected RuntimeError in refresh_ingest_list: {e}")
                        raise
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=refresh_in_thread, daemon=True)
        thread.start()
    
    def get_ingested_documents(self):
        """
        Query the vector database to get a list of ingested documents.
        Returns a dictionary with document sources and their metadata.
        """
        try:
            # Import here to avoid requiring dependencies if not used
            # Use HuggingFace embeddings by default (no API key needed)
            # Or OpenAI if EMBEDDING_PROVIDER=openai
            try:
                from langchain_openai import OpenAIEmbeddings
            except ImportError:
                pass  # Will be handled by the ingestion script
            from langchain_chroma import Chroma
            
            persist_directory = os.path.join(SCRIPT_DIR, "chroma_db")
            
            # Check if database exists
            if not os.path.exists(persist_directory):
                return {
                    "status": "no_database",
                    "message": "No vector database found. Please ingest documents first.",
                    "documents": []
                }
            
            # Initialize embeddings and vector store
            # The actual embeddings are determined by EMBEDDING_PROVIDER environment variable
            # handled by the ingestion script (default: HuggingFace)
            # This is just for compatibility with the old code
            try:
                embeddings = OpenAIEmbeddings()
            except Exception:
                # If OpenAI embeddings fail, ingest script will use HuggingFace
                embeddings = None
            vectorstore = Chroma(
                collection_name="adastrea_docs",
                embedding_function=embeddings,
                persist_directory=persist_directory,
            )
            
            # Get collection and documents
            collection = vectorstore._collection
            count = collection.count()
            
            if count == 0:
                return {
                    "status": "empty",
                    "message": "Vector database is empty. Please ingest documents.",
                    "documents": []
                }
            
            # Get all documents with metadata
            results = collection.get(include=['metadatas'])
            
            # Extract unique source documents
            sources = {}
            if results and 'metadatas' in results:
                for metadata in results['metadatas']:
                    if metadata and 'source' in metadata:
                        source = metadata['source']
                        if source not in sources:
                            sources[source] = {
                                'path': source,
                                'chunks': 1
                            }
                        else:
                            sources[source]['chunks'] += 1
            
            return {
                "status": "success",
                "total_chunks": count,
                "total_documents": len(sources),
                "documents": sources
            }
            
        except ImportError:
            return {
                "status": "error",
                "message": "Required dependencies not installed. Please run: pip install -r requirements.txt",
                "documents": []
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error accessing database: {str(e)}",
                "documents": []
            }
    
    def _update_ingest_list_ui(self, result):
        """Update the UI with ingestion results."""
        # Update ingested documents list
        self.ingested_text.config(state=tk.NORMAL)
        self.ingested_text.delete(1.0, tk.END)
        
        if result["status"] == "success":
            documents = result["documents"]
            
            if documents:
                # Sort documents by path
                sorted_docs = sorted(documents.items(), key=lambda x: x[0])
                
                for doc_path, doc_info in sorted_docs:
                    # Get filename from path
                    filename = os.path.basename(doc_path)
                    chunks = doc_info['chunks']
                    
                    # Format the line
                    line = f"✅ {filename}\n"
                    self.ingested_text.insert(tk.END, line, "ingested")
                    self.ingested_text.insert(tk.END, f"   📍 {doc_path}\n", "path")
                    self.ingested_text.insert(tk.END, f"   📦 {chunks} chunk{'s' if chunks > 1 else ''}\n\n", "chunks")
                
                # Configure tags
                self.ingested_text.tag_config("ingested", foreground=self.success_color, font=("Consolas", 9, "bold"))
                self.ingested_text.tag_config("path", foreground=self.fg_muted, font=("Consolas", 8))
                self.ingested_text.tag_config("chunks", foreground=self.fg_secondary, font=("Consolas", 8))
            else:
                self.ingested_text.insert(tk.END, "No documents found in database.\n", "info")
                self.ingested_text.tag_config("info", foreground=self.fg_muted)
            
            # Update statistics
            self.ingest_stats_label.config(
                text=f"📊 Total: {result['total_documents']} documents • {result['total_chunks']} chunks"
            )
            
        elif result["status"] == "no_database":
            self.ingested_text.insert(tk.END, "⚠️ No vector database found\n\n", "warning")
            self.ingested_text.insert(tk.END, result["message"], "info")
            self.ingested_text.tag_config("warning", foreground=self.warning_color, font=("Consolas", 9, "bold"))
            self.ingested_text.tag_config("info", foreground=self.fg_secondary)
            self.ingest_stats_label.config(text="No database found")
            
        elif result["status"] == "empty":
            self.ingested_text.insert(tk.END, "ℹ️ Database is empty\n\n", "info_header")
            self.ingested_text.insert(tk.END, result["message"], "info")
            self.ingested_text.tag_config("info_header", foreground=self.accent_color, font=("Consolas", 9, "bold"))
            self.ingested_text.tag_config("info", foreground=self.fg_secondary)
            self.ingest_stats_label.config(text="0 documents • 0 chunks")
            
        else:  # error
            self.ingested_text.insert(tk.END, "❌ Error\n\n", "error_header")
            self.ingested_text.insert(tk.END, result["message"], "error")
            self.ingested_text.tag_config("error_header", foreground=self.error_color, font=("Consolas", 9, "bold"))
            self.ingested_text.tag_config("error", foreground=self.error_color)
            self.ingest_stats_label.config(text="Error loading data")
        
        self.ingested_text.config(state=tk.DISABLED)
    
    def _show_ingest_error(self, error_msg):
        """Show error message when refreshing ingest list fails."""
        self.ingested_text.config(state=tk.NORMAL)
        self.ingested_text.delete(1.0, tk.END)
        self.ingested_text.insert(tk.END, f"❌ Error refreshing list:\n{error_msg}\n", "error")
        self.ingested_text.tag_config("error", foreground=self.error_color)
        self.ingested_text.config(state=tk.DISABLED)
        self.ingest_stats_label.config(text="Error")
    
    def clear_ingestion_log(self):
        """Clear the ingestion log."""
        self.ingestion_log.config(state=tk.NORMAL)
        self.ingestion_log.delete(1.0, tk.END)
        self.ingestion_log.config(state=tk.DISABLED)
        self.log_to_ingest_tab("Log cleared", "info")
    
    def log_to_ingest_tab(self, message, level="info"):
        """
        Append a log message to the ingestion log.
        
        Args:
            message: The message to log
            level: Log level - "info", "success", "warning", "error", "progress"
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.ingestion_log.config(state=tk.NORMAL)
        self.ingestion_log.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.ingestion_log.insert(tk.END, f"{message}\n", level)
        self.ingestion_log.see(tk.END)
        self.ingestion_log.config(state=tk.DISABLED)
    
    # Class-level constants for syntax highlighting keywords (moved for performance)
    _ERROR_KEYWORDS = ['error', 'failed', '✗', '❌']
    _WARNING_KEYWORDS = ['warning', 'warn', '⚠']
    _SUCCESS_KEYWORDS = ['success', 'completed', '✓', '✅']
    _PROGRESS_KEYWORDS = ['ingestion in progress', 'processing']
    
    def _append_ingest_output_batch(self, lines):
        """
        Append multiple lines of ingestion output to the ingestion log.
        This batches multiple lines together to improve performance and avoid
        overwhelming the GUI event queue.
        
        Args:
            lines: List of output lines from the ingestion process
        """
        # Check if widget still exists before batch update
        try:
            if not self.ingestion_log.winfo_exists():
                return
        except tk.TclError:
            return
        
        # Batch all GUI operations into a single update
        try:
            self.ingestion_log.config(state=tk.NORMAL)
            for line in lines:
                # Determine log level for each line
                line_lower = line.lower()
                if any(word in line_lower for word in self._ERROR_KEYWORDS):
                    level = "error"
                elif any(word in line_lower for word in self._WARNING_KEYWORDS):
                    level = "warning"
                elif any(word in line_lower for word in self._SUCCESS_KEYWORDS):
                    level = "success"
                elif any(word in line_lower for word in self._PROGRESS_KEYWORDS):
                    level = "progress"
                else:
                    level = "info"
                
                self.ingestion_log.insert(tk.END, f"{line}\n", level)
            
            self.ingestion_log.see(tk.END)
            self.ingestion_log.config(state=tk.DISABLED)
        except tk.TclError:
            # Widget was destroyed during update
            pass
    
    def _append_ingest_output(self, line):
        """
        Append a line of ingestion output to the ingestion log.
        This is scheduled from a background thread via root.after() but executed 
        on the main GUI thread. Output lines are displayed without timestamp prefix 
        since they come from the subprocess with their own formatting.
        
        Args:
            line: Output line from the ingestion process
        """
        # Check if widget still exists before updating
        try:
            if not self.ingestion_log.winfo_exists():
                return
        except tk.TclError:
            return
        
        # Determine log level based on content for syntax highlighting
        line_lower = line.lower()
        if any(word in line_lower for word in self._ERROR_KEYWORDS):
            level = "error"
        elif any(word in line_lower for word in self._WARNING_KEYWORDS):
            level = "warning"
        elif any(word in line_lower for word in self._SUCCESS_KEYWORDS):
            level = "success"
        elif any(word in line_lower for word in self._PROGRESS_KEYWORDS):
            level = "progress"
        else:
            level = "info"
        
        # Insert without timestamp (subprocess output already formatted)
        try:
            self.ingestion_log.config(state=tk.NORMAL)
            self.ingestion_log.insert(tk.END, f"{line}\n", level)
            self.ingestion_log.see(tk.END)
            self.ingestion_log.config(state=tk.DISABLED)
        except tk.TclError:
            # Widget was destroyed during update
            pass
    
    def create_status_dashboard_tab(self):
        """Create the Status Dashboard tab showing connection and service status."""
        # Initialize status dictionary before creating status cards
        self.status_labels = {}
        
        status_tab = tk.Frame(self.notebook, bg=self.bg_tertiary)
        self.notebook.add(status_tab, text="📊 Status")
        
        # Header section
        status_header = tk.Frame(status_tab, bg=self.bg_tertiary, padx=15, pady=10)
        status_header.pack(fill=tk.X)
        
        status_label = tk.Label(
            status_header,
            text="📊 System Status Dashboard",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_tertiary,
            fg=self.fg_color
        )
        status_label.pack(side=tk.LEFT)
        
        # Collect UE Data button
        collect_ue_button = tk.Button(
            status_header,
            text="📥 Collect UE Data",
            command=self.collect_ue_analytics_data,
            font=("Segoe UI", 9),
            bg=self.accent_color,
            fg="#20232b",
            activebackground=self.accent_hover,
            activeforeground="#20232b",
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            borderwidth=0
        )
        collect_ue_button.pack(side=tk.RIGHT, padx=(0, 5))
        self.create_tooltip(collect_ue_button, "Collect analytics data from Unreal Engine")
        self.add_button_hover_effect(collect_ue_button, hover_color=self.accent_hover)
        
        # Test Connection button
        test_connection_button = tk.Button(
            status_header,
            text="🔍 Test Connection",
            command=self.test_all_connections,
            font=("Segoe UI", 9),
            bg=self.success_color,
            fg="#20232b",
            activebackground="#60e0c0",
            activeforeground="#20232b",
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            borderwidth=0
        )
        test_connection_button.pack(side=tk.RIGHT, padx=(0, 5))
        self.create_tooltip(test_connection_button, "Run comprehensive connection tests")
        self.add_button_hover_effect(test_connection_button, hover_color="#60e0c0")
        
        # Refresh button
        refresh_status_button = tk.Button(
            status_header,
            text="🔄 Refresh All",
            command=self.refresh_all_status,
            font=("Segoe UI", 9),
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.button_hover,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.button_bg
        )
        refresh_status_button.pack(side=tk.RIGHT)
        self.create_tooltip(refresh_status_button, "Refresh all status indicators")
        self.add_button_hover_effect(refresh_status_button)
        
        # Separator line
        separator_line = tk.Frame(status_tab, height=1, bg=self.border_color)
        separator_line.pack(fill=tk.X)
        
        # Main content area with scrollable frame
        content_frame = tk.Frame(status_tab, bg=self.bg_tertiary)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create a canvas with scrollbar for status cards
        canvas = tk.Canvas(content_frame, bg=self.bg_tertiary, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_tertiary)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # --- VS Code Extension Status Card ---
        self._create_status_card(
            scrollable_frame,
            "VS Code Extension",
            "🔌",
            [
                ("Connection", "vscode_connection"),
                ("Version", "vscode_version"),
                ("IPC Port", "vscode_port"),
                ("Auto-Connect", "vscode_autoconnect")
            ]
        )
        
        # --- Unreal Engine Plugin Status Card ---
        self._create_status_card(
            scrollable_frame,
            "Unreal Engine Plugin",
            "🎮",
            [
                ("Connection", "ue_connection"),
                ("Remote Execution", "ue_remote_exec"),
                ("Python Plugin", "ue_python_plugin"),
                ("MCP Server", "ue_mcp_server")
            ]
        )
        
        # --- Python Backend Services Card ---
        self._create_status_card(
            scrollable_frame,
            "Backend Services",
            "⚙️",
            [
                ("Agent Orchestrator", "agent_orchestrator"),
                ("Agent Dashboard", "agent_dashboard"),
                ("MCP Server", "mcp_server"),
                ("RAG System", "rag_system")
            ]
        )
        
        # --- API Configuration Card ---
        self._create_status_card(
            scrollable_frame,
            "API Configuration",
            "🔑",
            [
                ("LLM Provider", "llm_provider"),
                ("Gemini API Key", "gemini_key"),
                ("OpenAI API Key", "openai_key"),
                ("OpenRouter API Key", "openrouter_key"),
                ("Embedding Provider", "embedding_provider")
            ]
        )
        
        # --- System Health Card ---
        self._create_status_card(
            scrollable_frame,
            "System Health",
            "💚",
            [
                ("CPU Usage", "cpu_usage"),
                ("Memory Usage", "memory_usage"),
                ("Disk Space", "disk_space"),
                ("Python Version", "python_version")
            ]
        )
        
        # Initial status check
        self.root.after(500, self.refresh_all_status)
    
    def _create_status_card(self, parent, title, icon, fields):
        """Create a status card with specified fields."""
        card = tk.Frame(parent, bg=self.bg_secondary, highlightthickness=1,
                       highlightbackground=self.border_color)
        card.pack(fill=tk.X, pady=(0, 10))
        
        card_inner = tk.Frame(card, bg=self.bg_secondary, padx=15, pady=12)
        card_inner.pack(fill=tk.X)
        
        # Card header
        header = tk.Label(
            card_inner,
            text=f"{icon} {title}",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_secondary,
            fg=self.accent_color,
            anchor=tk.W
        )
        header.pack(fill=tk.X, pady=(0, 10))
        
        # Create field rows
        for field_name, field_key in fields:
            row = tk.Frame(card_inner, bg=self.bg_secondary)
            row.pack(fill=tk.X, pady=2)
            
            label = tk.Label(
                row,
                text=f"{field_name}:",
                font=("Segoe UI", 9),
                bg=self.bg_secondary,
                fg=self.fg_secondary,
                anchor=tk.W,
                width=18
            )
            label.pack(side=tk.LEFT)
            
            value_label = tk.Label(
                row,
                text="Checking...",
                font=("Segoe UI", 9),
                bg=self.bg_secondary,
                fg=self.fg_muted,
                anchor=tk.W
            )
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Store reference for updates
            self.status_labels[field_key] = value_label
    
    def refresh_all_status(self):
        """Refresh all status indicators."""
        self.update_status("Refreshing status...", "busy")
        
        # Run status checks in a thread to avoid blocking
        def check_status():
            try:
                # Check VS Code Extension
                self._check_vscode_extension()
                
                # Check Unreal Engine Plugin  
                self._check_ue_plugin()
                
                # Check Backend Services
                self._check_backend_services()
                
                # Check API Configuration
                self._check_api_config()
                
                # Check System Health
                self._check_system_health()
                
                self.root.after(0, lambda: self.update_status("Status refresh complete", "success"))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Status refresh error: {e}", "error"))
        
        thread = threading.Thread(target=check_status, daemon=True)
        thread.start()
    
    def _check_vscode_extension(self):
        """Check VS Code Extension status."""
        # Check if IPC port is listening
        host = "localhost"
        port = 5555
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                self._update_status_label("vscode_connection", "● Connected", self.success_color)
                self._update_status_label("vscode_port", f"{port}", self.fg_color)
            else:
                self._update_status_label("vscode_connection", "● Disconnected", self.error_color)
                self._update_status_label("vscode_port", f"{port} (not listening)", self.fg_muted)
        except Exception as e:
            self._update_status_label("vscode_connection", f"● Error: {e}", self.error_color)
            self._update_status_label("vscode_port", "N/A", self.fg_muted)
        
        # Check for extension files
        vscode_ext_path = os.path.join(SCRIPT_DIR, "vscode-extension")
        if os.path.exists(vscode_ext_path):
            package_json = os.path.join(vscode_ext_path, "package.json")
            if os.path.exists(package_json):
                try:
                    with open(package_json, 'r') as f:
                        data = json.load(f)
                        version = data.get('version', 'Unknown')
                        self._update_status_label("vscode_version", version, self.fg_color)
                except:
                    self._update_status_label("vscode_version", "Unknown", self.fg_muted)
            else:
                self._update_status_label("vscode_version", "Not found", self.fg_muted)
        else:
            self._update_status_label("vscode_version", "Not installed", self.fg_muted)
        
        self._update_status_label("vscode_autoconnect", "Configurable in extension settings", self.fg_secondary)
    
    def _check_ue_plugin(self):
        """Check Unreal Engine Plugin status."""
        # Use MCP connection status
        if hasattr(self, 'mcp_connected') and self.mcp_connected:
            self._update_status_label("ue_connection", "● Connected", self.success_color)
            self._update_status_label("ue_mcp_server", "● Running", self.success_color)
        else:
            self._update_status_label("ue_connection", "● Disconnected", self.fg_muted)
            self._update_status_label("ue_mcp_server", "● Not running", self.fg_muted)
        
        # Check for plugin files
        plugin_path = os.path.join(SCRIPT_DIR, "Plugins", "AdastreaDirector")
        if os.path.exists(plugin_path):
            self._update_status_label("ue_remote_exec", "Plugin files present", self.fg_color)
            self._update_status_label("ue_python_plugin", "Check UE Editor", self.fg_secondary)
        else:
            self._update_status_label("ue_remote_exec", "Plugin not found", self.fg_muted)
            self._update_status_label("ue_python_plugin", "N/A", self.fg_muted)
    
    def _check_backend_services(self):
        """Check Python backend services status."""
        # Check if various processes are running by looking for their PIDs
        if not PSUTIL_AVAILABLE:
            self._update_status_label("agent_orchestrator", "psutil not available", self.fg_muted)
            self._update_status_label("agent_dashboard", "psutil not available", self.fg_muted)
            self._update_status_label("mcp_server", "psutil not available", self.fg_muted)
            # Still check RAG
            chroma_path = os.path.join(SCRIPT_DIR, "chroma_db")
            if os.path.exists(chroma_path):
                self._update_status_label("rag_system", "● Database present", self.success_color)
            else:
                self._update_status_label("rag_system", "● No database", self.warning_color)
            return
        
        services = {
            "agent_orchestrator": "agent_orchestrator_cli.py",
            "agent_dashboard": "agent_dashboard.py",
            "mcp_server": "mcp_server",
        }
        
        for service_key, service_name in services.items():
            found = False
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        cmdline = proc.info.get('cmdline', [])
                        if cmdline and service_name in ' '.join(cmdline):
                            self._update_status_label(service_key, "● Running", self.success_color)
                            found = True
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception:
                pass
            
            if not found:
                self._update_status_label(service_key, "● Stopped", self.fg_muted)
        
        # Check RAG system (ChromaDB)
        chroma_path = os.path.join(SCRIPT_DIR, "chroma_db")
        if os.path.exists(chroma_path):
            self._update_status_label("rag_system", "● Database present", self.success_color)
        else:
            self._update_status_label("rag_system", "● No database", self.warning_color)
    
    def _check_api_config(self):
        """Check API configuration status."""
        # Check LLM provider
        llm_provider = os.getenv("LLM_PROVIDER", "gemini")
        self._update_status_label("llm_provider", llm_provider.title(), self.fg_color)
        
        # Check Gemini API key
        gemini_key = os.getenv("GEMINI_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            self._update_status_label("gemini_key", "● Configured", self.success_color)
        else:
            self._update_status_label("gemini_key", "● Not set", self.warning_color)
        
        # Check OpenAI API key
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self._update_status_label("openai_key", "● Configured", self.success_color)
        else:
            self._update_status_label("openai_key", "● Not set", self.fg_muted)
        
        # Check OpenRouter API key
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            self._update_status_label("openrouter_key", "● Configured", self.success_color)
        else:
            self._update_status_label("openrouter_key", "● Not set", self.fg_muted)
        
        # Check embedding provider
        embedding_provider = os.getenv("EMBEDDING_PROVIDER", "huggingface")
        self._update_status_label("embedding_provider", embedding_provider.title(), self.fg_color)
    
    def _check_system_health(self):
        """Check system health metrics."""
        if not PSUTIL_AVAILABLE:
            self._update_status_label("cpu_usage", "psutil not installed", self.fg_muted)
            self._update_status_label("memory_usage", "psutil not installed", self.fg_muted)
            self._update_status_label("disk_space", "psutil not installed", self.fg_muted)
            # Python version still works
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            self._update_status_label("python_version", python_version, self.fg_color)
            return
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_color = self.success_color if cpu_percent < 70 else self.warning_color if cpu_percent < 90 else self.error_color
            self._update_status_label("cpu_usage", f"{cpu_percent}%", cpu_color)
            
            # Memory usage
            memory = psutil.virtual_memory()
            mem_percent = memory.percent
            mem_color = self.success_color if mem_percent < 70 else self.warning_color if mem_percent < 90 else self.error_color
            self._update_status_label("memory_usage", f"{mem_percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)", mem_color)
            
            # Disk space
            disk = psutil.disk_usage(SCRIPT_DIR)
            disk_percent = disk.percent
            disk_color = self.success_color if disk_percent < 70 else self.warning_color if disk_percent < 90 else self.error_color
            self._update_status_label("disk_space", f"{disk_percent}% used ({disk.free // (1024**3)}GB free)", disk_color)
            
        except Exception as e:
            self._update_status_label("cpu_usage", f"Error: {e}", self.error_color)
            self._update_status_label("memory_usage", f"Error: {e}", self.error_color)
            self._update_status_label("disk_space", f"Error: {e}", self.error_color)
        
        # Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self._update_status_label("python_version", python_version, self.fg_color)
    
    def _update_status_label(self, key, text, color):
        """Update a status label with thread-safe UI update."""
        def update():
            if key in self.status_labels:
                self.status_labels[key].config(text=text, fg=color)
        
        self.root.after(0, update)
    
    def test_all_connections(self):
        """Run comprehensive connection tests and display results."""
        self.update_status("Running connection tests...", "busy")
        
        # Create a dialog to show test results
        dialog = tk.Toplevel(self.root)
        dialog.title("Connection Test Results")
        dialog.geometry("700x600")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(dialog, bg=self.bg_color)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(
            header_frame,
            text="🔍 Connection Test Results",
            font=("Segoe UI", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(side=tk.LEFT)
        
        # Status label
        status_label = tk.Label(
            header_frame,
            text="Testing...",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg=self.fg_muted
        )
        status_label.pack(side=tk.RIGHT)
        
        # Results area with scrollbar
        results_frame = tk.Frame(dialog, bg=self.bg_color)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            height=20,
            state=tk.DISABLED,
            bg=self.text_bg,
            fg=self.fg_color,
            font=("Consolas", 9),
            relief=tk.FLAT,
            padx=15,
            pady=15,
            selectbackground=self.highlight_bg,
            selectforeground=self.fg_color,
            borderwidth=0
        )
        results_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for colored output
        results_text.tag_config("header", foreground=self.accent_color, font=("Consolas", 10, "bold"))
        results_text.tag_config("pass", foreground=self.success_color)
        results_text.tag_config("fail", foreground=self.error_color)
        results_text.tag_config("error", foreground=self.warning_color)
        results_text.tag_config("info", foreground=self.fg_secondary)
        
        # Button frame
        button_frame = tk.Frame(dialog, bg=self.bg_color)
        button_frame.pack(side=tk.BOTTOM, pady=(0, 20))
        
        close_button = tk.Button(
            button_frame,
            text="Close",
            command=dialog.destroy,
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.button_active,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=30,
            pady=8,
            cursor="hand2",
            font=("Segoe UI", 10),
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.button_bg
        )
        close_button.pack()
        
        # Run tests in a thread
        def run_tests():
            try:
                # Try to connect to IPC server and run tests
                results_text.config(state=tk.NORMAL)
                results_text.insert(tk.END, "🔍 Running comprehensive connection tests...\n\n", "header")
                results_text.config(state=tk.DISABLED)
                
                # Check if IPC server is available
                host = "localhost"
                port = 5555
                
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    try:
                        sock.connect((host, port))
                        
                        # Send test_connection request
                        request = json.dumps({'type': 'test_connection', 'data': ''})
                        sock.sendall((request + '\n').encode('utf-8'))
                        
                        # Receive response (read until newline delimiter)
                        response_data = b''
                        while True:
                            chunk = sock.recv(1024)
                            if not chunk:
                                break
                            response_data += chunk
                            if b'\n' in chunk:
                                break
                        response_data = response_data.decode('utf-8').strip()
                    finally:
                        sock.close()
                    
                    # Parse response
                    response = json.loads(response_data)
                    
                    # Display results
                    results_text.config(state=tk.NORMAL)
                    
                    if response.get('status') == 'success':
                        overall_status = response.get('overall_status', 'unknown')
                        message = response.get('message', '')
                        
                        results_text.insert(tk.END, f"{message}\n\n", "pass" if overall_status == "pass" else "fail")
                        
                        # Display component results
                        components = response.get('components', {})
                        
                        for comp_name, comp_data in components.items():
                            comp_title = {
                                'backend': 'Python Backend',
                                'llm': 'LLM Connection',
                                'rag': 'RAG System'
                            }.get(comp_name, comp_name.title())
                            
                            results_text.insert(tk.END, f"\n{'='*60}\n", "info")
                            results_text.insert(tk.END, f"{comp_title}\n", "header")
                            results_text.insert(tk.END, f"{'='*60}\n\n", "info")
                            
                            tests = comp_data.get('tests', [])
                            for test in tests:
                                test_name = test.get('name', 'Unknown Test')
                                test_status = test.get('status', 'unknown')
                                test_message = test.get('message', '')
                                test_solution = test.get('solution', '')
                                
                                # Status icon and color
                                if test_status == 'pass':
                                    icon = "✅"
                                    tag = "pass"
                                elif test_status == 'fail':
                                    icon = "❌"
                                    tag = "fail"
                                else:
                                    icon = "⚠️"
                                    tag = "error"
                                
                                results_text.insert(tk.END, f"{icon} {test_name}\n", tag)
                                results_text.insert(tk.END, f"   {test_message}\n", "info")
                                
                                if test_solution:
                                    results_text.insert(tk.END, f"   💡 Solution: {test_solution}\n", "info")
                                
                                results_text.insert(tk.END, "\n")
                        
                        # Display next steps if any
                        next_steps = response.get('next_steps', [])
                        if next_steps:
                            results_text.insert(tk.END, f"\n{'='*60}\n", "info")
                            results_text.insert(tk.END, "Next Steps\n", "header")
                            results_text.insert(tk.END, f"{'='*60}\n\n", "info")
                            for step in next_steps:
                                results_text.insert(tk.END, f"{step}\n", "info")
                        
                        # Update status label
                        status_text = "✅ All tests passed!" if overall_status == "pass" else "❌ Some tests failed"
                        status_label.config(text=status_text, fg=self.success_color if overall_status == "pass" else self.error_color)
                        
                    else:
                        error_msg = response.get('error', 'Unknown error')
                        results_text.insert(tk.END, f"❌ Test failed: {error_msg}\n", "fail")
                        status_label.config(text="❌ Test failed", fg=self.error_color)
                    
                    results_text.config(state=tk.DISABLED)
                    results_text.see(tk.END)
                    
                    self.root.after(0, lambda: self.update_status("Connection test complete", "success"))
                    
                except socket.error as e:
                    results_text.config(state=tk.NORMAL)
                    results_text.insert(tk.END, "❌ Python Backend is not running\n\n", "fail")
                    results_text.insert(tk.END, "The IPC server (Python backend) is not reachable.\n", "info")
                    results_text.insert(tk.END, f"Error: {e}\n\n", "info")
                    results_text.insert(tk.END, "💡 Solution:\n", "header")
                    results_text.insert(tk.END, "1. Open a terminal in the project directory\n", "info")
                    # Try to find the actual script path
                    script_path = os.path.join("Plugins", "AdastreaDirector", "Python", "ipc_server.py")
                    if not os.path.exists(os.path.join(SCRIPT_DIR, script_path)):
                        script_path = "ipc_server.py"  # Fallback for different installation layouts
                    results_text.insert(tk.END, f"2. Run: python {script_path} --port {port}\n", "info")
                    results_text.insert(tk.END, "3. Wait for 'IPC Server started' message\n", "info")
                    results_text.insert(tk.END, "4. Click 'Test Connection' again\n", "info")
                    results_text.config(state=tk.DISABLED)
                    status_label.config(text="❌ Backend not running", fg=self.error_color)
                    self.root.after(0, lambda: self.update_status("Backend not running", "error"))
                    
            except Exception as e:
                results_text.config(state=tk.NORMAL)
                results_text.insert(tk.END, f"❌ Unexpected error: {e}\n", "fail")
                results_text.config(state=tk.DISABLED)
                status_label.config(text="❌ Error", fg=self.error_color)
                self.root.after(0, lambda: self.update_status(f"Test error: {e}", "error"))
        
        # Start test thread
        test_thread = threading.Thread(target=run_tests, daemon=True)
        test_thread.start()
    
    def create_analytics_dashboard_tab(self):
        """Create the Analytics Dashboard tab with project statistics and metrics."""
        # Initialize analytics labels dictionary first
        self.analytics_labels = {}
        
        analytics_tab = tk.Frame(self.notebook, bg=self.bg_tertiary)
        self.notebook.add(analytics_tab, text="📊 Analytics")
        
        # Header section
        analytics_header = tk.Frame(analytics_tab, bg=self.bg_tertiary, padx=15, pady=10)
        analytics_header.pack(fill=tk.X)
        
        analytics_label = tk.Label(
            analytics_header,
            text="📊 Project Analytics Dashboard",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_tertiary,
            fg=self.fg_color
        )
        analytics_label.pack(side=tk.LEFT)
        
        # Refresh button
        refresh_analytics_button = tk.Button(
            analytics_header,
            text="🔄 Refresh Data",
            command=self.refresh_analytics_data,
            font=("Segoe UI", 9),
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.button_hover,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.button_bg
        )
        refresh_analytics_button.pack(side=tk.RIGHT, padx=(0, 5))
        self.create_tooltip(refresh_analytics_button, "Refresh analytics from Unreal Engine")
        self.add_button_hover_effect(refresh_analytics_button)
        
        # Export button
        export_analytics_button = tk.Button(
            analytics_header,
            text="📥 Export",
            command=self.export_analytics_data,
            font=("Segoe UI", 9),
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.button_hover,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.button_bg
        )
        export_analytics_button.pack(side=tk.RIGHT)
        self.create_tooltip(export_analytics_button, "Export analytics data to JSON")
        self.add_button_hover_effect(export_analytics_button)
        
        # Separator line
        separator_line = tk.Frame(analytics_tab, height=1, bg=self.border_color)
        separator_line.pack(fill=tk.X)
        
        # Main content area with scrollable frame
        content_frame = tk.Frame(analytics_tab, bg=self.bg_tertiary)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(content_frame, bg=self.bg_tertiary, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_tertiary)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # --- Project Health Score Card ---
        self._create_analytics_card(
            scrollable_frame,
            "Project Health Score",
            "💚",
            [
                ("Overall Score", "health_score"),
                ("Status", "health_status"),
                ("Last Calculated", "health_updated")
            ]
        )
        
        # --- Asset Counts Card ---
        self._create_analytics_card(
            scrollable_frame,
            "Asset Inventory",
            "📦",
            [
                ("Static Meshes", "asset_static_meshes"),
                ("Skeletal Meshes", "asset_skeletal_meshes"),
                ("Blueprints", "asset_blueprints"),
                ("Materials", "asset_materials"),
                ("Textures", "asset_textures"),
                ("Sounds", "asset_sounds"),
                ("Animations", "asset_animations"),
                ("Particles", "asset_particles"),
                ("Total Assets", "asset_total")
            ]
        )
        
        # --- Blueprint Statistics Card ---
        self._create_analytics_card(
            scrollable_frame,
            "Blueprint Analysis",
            "🎯",
            [
                ("Total Blueprints", "bp_total"),
                ("Actor Blueprints", "bp_actors"),
                ("Component Blueprints", "bp_components"),
                ("Interface Blueprints", "bp_interfaces"),
                ("Function Libraries", "bp_libraries"),
                ("Average Nodes", "bp_avg_nodes"),
                ("Max Nodes", "bp_max_nodes")
            ]
        )
        
        # --- Lines of Code Card ---
        self._create_analytics_card(
            scrollable_frame,
            "Code Metrics",
            "📝",
            [
                ("Total Lines", "loc_total"),
                ("Code Lines", "loc_code"),
                ("Comment Lines", "loc_comments"),
                ("Blank Lines", "loc_blank"),
                ("Python", "loc_python"),
                ("C++", "loc_cpp"),
                ("Headers", "loc_headers"),
                ("Blueprint Scripts", "loc_blueprint")
            ]
        )
        
        # --- Placeholder Content Card ---
        self._create_analytics_card(
            scrollable_frame,
            "Placeholder Content",
            "⚠️",
            [
                ("Default Cubes", "placeholder_cubes"),
                ("Default Spheres", "placeholder_spheres"),
                ("Temp Blueprints", "placeholder_temp_bps"),
                ("Missing Assets", "placeholder_missing"),
                ("Placeholder Materials", "placeholder_mats"),
                ("Placeholder Textures", "placeholder_texs")
            ]
        )
        
        # --- Connection Metrics Card ---
        self._create_analytics_card(
            scrollable_frame,
            "Connection Health",
            "🔌",
            [
                ("VS Code Connected", "conn_vscode"),
                ("VS Code Uptime", "conn_vscode_uptime"),
                ("VS Code Reconnects", "conn_vscode_reconnects"),
                ("UE Connected", "conn_ue"),
                ("UE Uptime", "conn_ue_uptime"),
                ("UE Reconnects", "conn_ue_reconnects"),
                ("Avg Latency", "conn_latency")
            ]
        )
        
        # --- PIE Session Summary Card ---
        self._create_analytics_card(
            scrollable_frame,
            "PIE Sessions (Last 5)",
            "🎮",
            [
                ("Total Sessions", "pie_total"),
                ("Average FPS", "pie_avg_fps"),
                ("Average Frame Time", "pie_avg_frame_time"),
                ("Average Memory", "pie_avg_memory"),
                ("Peak Memory", "pie_peak_memory")
            ]
        )
        
        # --- Build Metrics Card ---
        self._create_analytics_card(
            scrollable_frame,
            "Build Statistics",
            "🔨",
            [
                ("Total Builds", "build_total"),
                ("Failed Builds", "build_failed"),
                ("Success Rate", "build_success_rate"),
                ("Last Build Time", "build_last_time"),
                ("Average Build Time", "build_avg_time"),
                ("Last Build Status", "build_last_status")
            ]
        )
        
        # Initial data load
        self.root.after(1000, self.refresh_analytics_data)
    
    def _create_analytics_card(self, parent, title, icon, fields):
        """Create an analytics card with specified fields."""
        card = tk.Frame(parent, bg=self.bg_secondary, highlightthickness=1,
                       highlightbackground=self.border_color)
        card.pack(fill=tk.X, pady=(0, 10))
        
        card_inner = tk.Frame(card, bg=self.bg_secondary, padx=15, pady=12)
        card_inner.pack(fill=tk.X)
        
        # Card header
        header = tk.Label(
            card_inner,
            text=f"{icon} {title}",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_secondary,
            fg=self.accent_color,
            anchor=tk.W
        )
        header.pack(fill=tk.X, pady=(0, 10))
        
        # Create field rows
        for field_name, field_key in fields:
            row = tk.Frame(card_inner, bg=self.bg_secondary)
            row.pack(fill=tk.X, pady=2)
            
            name_label = tk.Label(
                row,
                text=field_name + ":",
                font=("Segoe UI", 9),
                bg=self.bg_secondary,
                fg=self.fg_secondary,
                anchor=tk.W,
                width=20
            )
            name_label.pack(side=tk.LEFT)
            
            value_label = tk.Label(
                row,
                text="Loading...",
                font=("Segoe UI", 9, "bold"),
                bg=self.bg_secondary,
                fg=self.fg_color,
                anchor=tk.W
            )
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            self.analytics_labels[field_key] = value_label
    
    def refresh_analytics_data(self):
        """Refresh all analytics data from various sources."""
        def refresh_in_thread():
            try:
                # Get all metrics from analytics system
                metrics = self.project_analytics.get_all_metrics()
                
                # Update UI on main thread
                self.root.after(0, self._update_analytics_ui, metrics)
            except Exception as e:
                logger.error(f"Error refreshing analytics: {e}")
                self.root.after(0, self._show_analytics_error, str(e))
        
        # Update status
        self.update_status("Refreshing analytics data...", "busy")
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=refresh_in_thread, daemon=True)
        thread.start()
    
    def _update_analytics_ui(self, metrics):
        """Update analytics UI with collected metrics."""
        try:
            # Health Score
            health_score = self.project_analytics.calculate_health_score()
            self._update_analytics_label("health_score", f"{health_score:.1f}/100")
            
            if health_score >= 80:
                status_text = "Excellent"
                status_color = self.success_color
            elif health_score >= 60:
                status_text = "Good"
                status_color = self.accent_color
            elif health_score >= 40:
                status_text = "Fair"
                status_color = self.warning_color
            else:
                status_text = "Needs Attention"
                status_color = self.error_color
            
            self._update_analytics_label("health_status", status_text, status_color)
            self._update_analytics_label("health_updated", datetime.now().strftime("%H:%M:%S"))
            
            # Asset Counts (with comma formatting for large numbers)
            asset_counts = metrics.get('asset_counts', {})
            self._update_analytics_label("asset_static_meshes", f"{asset_counts.get('static_meshes', 0):,}")
            self._update_analytics_label("asset_skeletal_meshes", f"{asset_counts.get('skeletal_meshes', 0):,}")
            self._update_analytics_label("asset_blueprints", f"{asset_counts.get('blueprints', 0):,}")
            self._update_analytics_label("asset_materials", f"{asset_counts.get('materials', 0):,}")
            self._update_analytics_label("asset_textures", f"{asset_counts.get('textures', 0):,}")
            self._update_analytics_label("asset_sounds", f"{asset_counts.get('sounds', 0):,}")
            self._update_analytics_label("asset_animations", f"{asset_counts.get('animations', 0):,}")
            self._update_analytics_label("asset_particles", f"{asset_counts.get('particles', 0):,}")
            self._update_analytics_label("asset_total", f"{asset_counts.get('total', 0):,}")
            
            # Blueprint Stats
            bp_stats = metrics.get('blueprint_stats', {})
            self._update_analytics_label("bp_total", str(bp_stats.get('total_blueprints', 0)))
            self._update_analytics_label("bp_actors", str(bp_stats.get('actor_blueprints', 0)))
            self._update_analytics_label("bp_components", str(bp_stats.get('component_blueprints', 0)))
            self._update_analytics_label("bp_interfaces", str(bp_stats.get('interface_blueprints', 0)))
            self._update_analytics_label("bp_libraries", str(bp_stats.get('function_libraries', 0)))
            self._update_analytics_label("bp_avg_nodes", f"{bp_stats.get('avg_node_count', 0):.1f}")
            self._update_analytics_label("bp_max_nodes", str(bp_stats.get('max_node_count', 0)))
            
            # LOC Stats (with comma formatting)
            loc_stats = metrics.get('loc_stats', {})
            self._update_analytics_label("loc_total", f"{loc_stats.get('total_lines', 0):,}")
            self._update_analytics_label("loc_code", f"{loc_stats.get('code_lines', 0):,}")
            self._update_analytics_label("loc_comments", f"{loc_stats.get('comment_lines', 0):,}")
            self._update_analytics_label("loc_blank", f"{loc_stats.get('blank_lines', 0):,}")
            self._update_analytics_label("loc_python", f"{loc_stats.get('python_lines', 0):,}")
            self._update_analytics_label("loc_cpp", f"{loc_stats.get('cpp_lines', 0):,}")
            self._update_analytics_label("loc_headers", f"{loc_stats.get('header_lines', 0):,}")
            self._update_analytics_label("loc_blueprint", f"{loc_stats.get('blueprint_lines', 0):,}")
            
            # Placeholder Content
            placeholders = metrics.get('placeholder_content', {})
            self._update_analytics_label("placeholder_cubes", str(placeholders.get('default_cubes', 0)))
            self._update_analytics_label("placeholder_spheres", str(placeholders.get('default_spheres', 0)))
            self._update_analytics_label("placeholder_temp_bps", str(placeholders.get('temp_blueprints', 0)))
            self._update_analytics_label("placeholder_missing", str(placeholders.get('missing_assets', 0)))
            self._update_analytics_label("placeholder_mats", str(placeholders.get('placeholder_materials', 0)))
            self._update_analytics_label("placeholder_texs", str(placeholders.get('placeholder_textures', 0)))
            
            # Connection Metrics
            conn_metrics = metrics.get('connection_metrics', {})
            self._update_analytics_label("conn_vscode", "✅ Connected" if conn_metrics.get('vscode_connected') else "❌ Disconnected")
            uptime = conn_metrics.get('vscode_uptime_seconds', 0)
            self._update_analytics_label("conn_vscode_uptime", self._format_duration(uptime))
            self._update_analytics_label("conn_vscode_reconnects", str(conn_metrics.get('vscode_reconnect_count', 0)))
            
            self._update_analytics_label("conn_ue", "✅ Connected" if conn_metrics.get('ue_connected') else "❌ Disconnected")
            uptime = conn_metrics.get('ue_uptime_seconds', 0)
            self._update_analytics_label("conn_ue_uptime", self._format_duration(uptime))
            self._update_analytics_label("conn_ue_reconnects", str(conn_metrics.get('ue_reconnect_count', 0)))
            self._update_analytics_label("conn_latency", f"{conn_metrics.get('avg_latency_ms', 0):.1f} ms")
            
            # PIE Sessions
            pie_sessions = metrics.get('pie_sessions', [])
            self._update_analytics_label("pie_total", str(len(pie_sessions)))
            
            if pie_sessions:
                avg_fps = sum(s.get('avg_fps', 0) for s in pie_sessions) / len(pie_sessions)
                avg_frame_time = sum(s.get('avg_frame_time_ms', 0) for s in pie_sessions) / len(pie_sessions)
                avg_memory = sum(s.get('avg_memory_mb', 0) for s in pie_sessions) / len(pie_sessions)
                peak_memory = max(s.get('peak_memory_mb', 0) for s in pie_sessions)
                
                self._update_analytics_label("pie_avg_fps", f"{avg_fps:.1f}")
                self._update_analytics_label("pie_avg_frame_time", f"{avg_frame_time:.2f} ms")
                self._update_analytics_label("pie_avg_memory", f"{avg_memory:.1f} MB")
                self._update_analytics_label("pie_peak_memory", f"{peak_memory:.1f} MB")
            else:
                self._update_analytics_label("pie_avg_fps", "N/A")
                self._update_analytics_label("pie_avg_frame_time", "N/A")
                self._update_analytics_label("pie_avg_memory", "N/A")
                self._update_analytics_label("pie_peak_memory", "N/A")
            
            # Build Metrics
            build_metrics = metrics.get('build_metrics', {})
            total_builds = build_metrics.get('total_builds', 0)
            failed_builds = build_metrics.get('failed_builds', 0)
            
            self._update_analytics_label("build_total", str(total_builds))
            self._update_analytics_label("build_failed", str(failed_builds))
            
            if total_builds > 0:
                success_rate = ((total_builds - failed_builds) / total_builds) * 100
                self._update_analytics_label("build_success_rate", f"{success_rate:.1f}%")
            else:
                self._update_analytics_label("build_success_rate", "N/A")
            
            last_build_time = build_metrics.get('last_build_time_seconds', 0)
            avg_build_time = build_metrics.get('avg_build_time_seconds', 0)
            
            self._update_analytics_label("build_last_time", self._format_duration(last_build_time))
            self._update_analytics_label("build_avg_time", self._format_duration(avg_build_time))
            self._update_analytics_label("build_last_status", build_metrics.get('last_build_status', 'unknown').title())
            
            self.update_status("Analytics refreshed successfully", "success")
            
        except Exception as e:
            logger.error(f"Error updating analytics UI: {e}")
            self.update_status(f"Error updating analytics: {e}", "error")
    
    def _update_analytics_label(self, key, text, color=None):
        """Update an analytics label with thread-safe UI update."""
        if key in self.analytics_labels:
            self.analytics_labels[key].config(text=text)
            if color:
                self.analytics_labels[key].config(fg=color)
    
    def _format_duration(self, seconds):
        """Format duration in seconds to human-readable string."""
        if seconds == 0:
            return "0s"
        elif seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
    
    def _show_analytics_error(self, error_msg):
        """Show error message when refreshing analytics fails."""
        self.update_status(f"Analytics error: {error_msg}", "error")
        messagebox.showerror("Analytics Error", f"Failed to refresh analytics:\n{error_msg}")
    
    def export_analytics_data(self):
        """Export analytics data to JSON file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            try:
                self.project_analytics.export_to_json(filename)
                self.update_status("Analytics data exported successfully", "success")
                messagebox.showinfo("Export Successful", f"Analytics data exported to:\n{filename}")
            except Exception as e:
                self.update_status(f"Export failed: {e}", "error")
                messagebox.showerror("Export Error", f"Failed to export analytics:\n{e}")
    
    def collect_ue_analytics_data(self):
        """Collect analytics data from Unreal Engine."""
        if not self.ue_data_collector.is_connected():
            messagebox.showwarning(
                "Not Connected",
                "Not connected to Unreal Engine.\n\nPlease connect to UE via the Unreal MCP tab first."
            )
            return
        
        # Show progress
        self.update_status("Collecting data from Unreal Engine...", "busy")
        
        def collect_in_thread():
            try:
                import asyncio
                
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Collect asset counts
                asset_counts = loop.run_until_complete(self.ue_data_collector.collect_asset_counts())
                self.project_analytics.update_asset_counts(asset_counts)
                
                # Collect blueprint stats
                bp_stats = loop.run_until_complete(self.ue_data_collector.collect_blueprint_stats())
                self.project_analytics.update_blueprint_stats(bp_stats)
                
                # Collect placeholder content
                placeholders = loop.run_until_complete(self.ue_data_collector.collect_placeholder_content())
                self.project_analytics.update_placeholder_content(placeholders)
                
                # Close the loop
                loop.close()
                
                # Update UI
                self.root.after(0, self._on_ue_data_collected)
                
            except Exception as e:
                logger.error(f"Error collecting UE data: {e}")
                self.root.after(0, self._on_ue_data_collection_failed, str(e))
        
        # Run in thread
        thread = threading.Thread(target=collect_in_thread, daemon=True)
        thread.start()
    
    def _on_ue_data_collected(self):
        """Handle successful UE data collection."""
        self.update_status("UE data collected successfully", "success")
        messagebox.showinfo(
            "Data Collection Complete",
            "Analytics data has been collected from Unreal Engine.\n\nView the Analytics tab to see updated statistics."
        )
        
        # Refresh analytics display
        self.refresh_analytics_data()
    
    def _on_ue_data_collection_failed(self, error_msg):
        """Handle failed UE data collection."""
        self.update_status(f"Data collection failed: {error_msg}", "error")
        messagebox.showerror(
            "Data Collection Failed",
            f"Failed to collect data from Unreal Engine:\n\n{error_msg}\n\nMake sure UE is running and connected."
        )
    
    def create_servers_tab(self):
        """Create the Servers tab for managing backend servers."""
        servers_tab = tk.Frame(self.notebook, bg=self.bg_tertiary)
        self.notebook.add(servers_tab, text="🖥️ Servers")
        
        # Header section
        servers_header = tk.Frame(servers_tab, bg=self.bg_tertiary, padx=15, pady=10)
        servers_header.pack(fill=tk.X)
        
        servers_label = tk.Label(
            servers_header,
            text="🖥️ Backend Server Management",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_tertiary,
            fg=self.fg_color
        )
        servers_label.pack(side=tk.LEFT)
        
        # Stop All button
        stop_all_button = tk.Button(
            servers_header,
            text="⏹ Stop All",
            command=self.stop_all_servers,
            font=("Segoe UI", 9),
            bg=self.error_color,
            fg=self.bg_color,
            activebackground="#ff6b6b",
            activeforeground=self.bg_color,
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.error_color
        )
        stop_all_button.pack(side=tk.RIGHT, padx=(0, 5))
        self.create_tooltip(stop_all_button, "Stop all running servers")
        self.add_button_hover_effect(stop_all_button, hover_color="#ff6b6b")
        
        # Clear button
        clear_server_button = tk.Button(
            servers_header,
            text="🗑️ Clear",
            command=self.clear_server_output,
            font=("Segoe UI", 9),
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.button_hover,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.button_bg
        )
        clear_server_button.pack(side=tk.RIGHT)
        self.create_tooltip(clear_server_button, "Clear server output")
        self.add_button_hover_effect(clear_server_button)
        
        # Separator line
        separator_line = tk.Frame(servers_tab, height=1, bg=self.border_color)
        separator_line.pack(fill=tk.X)
        
        # Main content with split panes
        content_frame = tk.Frame(servers_tab, bg=self.bg_tertiary)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Use PanedWindow for resizable split
        paned_window = ttk.PanedWindow(content_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # --- Top Section: Server Controls ---
        controls_frame = tk.Frame(paned_window, bg=self.bg_tertiary)
        
        controls_header = tk.Label(
            controls_frame,
            text="🎛️ Server Controls",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_tertiary,
            fg=self.accent_color,
            anchor=tk.W
        )
        controls_header.pack(fill=tk.X, pady=(0, 10))
        
        # Create a grid for server control buttons
        control_grid = tk.Frame(controls_frame, bg=self.bg_tertiary)
        control_grid.pack(fill=tk.BOTH, expand=True)
        
        # Button style for server buttons
        server_button_style = {
            "font": ("Segoe UI", 9),
            "bg": self.button_bg,
            "fg": self.fg_color,
            "activebackground": self.button_hover,
            "activeforeground": self.fg_color,
            "relief": tk.FLAT,
            "padx": 15,
            "pady": 8,
            "cursor": "hand2",
            "borderwidth": 1,
            "highlightthickness": 1,
            "highlightbackground": self.button_bg
        }
        
        # Row 0: Agent Orchestrator
        agent_orch_btn = tk.Button(
            control_grid,
            text="▶ Agent Orchestrator",
            command=lambda: self.start_server("agent_orchestrator"),
            **server_button_style
        )
        agent_orch_btn.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(agent_orch_btn, "Start Agent Orchestrator CLI")
        self.add_button_hover_effect(agent_orch_btn)
        
        agent_orch_stop_btn = tk.Button(
            control_grid,
            text="⏹",
            command=lambda: self.stop_server("agent_orchestrator"),
            font=("Segoe UI", 9),
            bg=self.error_color,
            fg=self.bg_color,
            activebackground="#ff6b6b",
            activeforeground=self.bg_color,
            relief=tk.FLAT,
            padx=10,
            pady=8,
            cursor="hand2",
            width=3
        )
        agent_orch_stop_btn.grid(row=0, column=1, padx=(0, 5), pady=5)
        self.create_tooltip(agent_orch_stop_btn, "Stop Agent Orchestrator")
        self.add_button_hover_effect(agent_orch_stop_btn, hover_color="#ff6b6b")
        
        # Row 1: Agent Dashboard
        agent_dash_btn = tk.Button(
            control_grid,
            text="▶ Agent Dashboard",
            command=lambda: self.start_server("agent_dashboard"),
            **server_button_style
        )
        agent_dash_btn.grid(row=1, column=0, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(agent_dash_btn, "Start Agent Dashboard UI")
        self.add_button_hover_effect(agent_dash_btn)
        
        agent_dash_stop_btn = tk.Button(
            control_grid,
            text="⏹",
            command=lambda: self.stop_server("agent_dashboard"),
            font=("Segoe UI", 9),
            bg=self.error_color,
            fg=self.bg_color,
            activebackground="#ff6b6b",
            activeforeground=self.bg_color,
            relief=tk.FLAT,
            padx=10,
            pady=8,
            cursor="hand2",
            width=3
        )
        agent_dash_stop_btn.grid(row=1, column=1, padx=(0, 5), pady=5)
        self.create_tooltip(agent_dash_stop_btn, "Stop Agent Dashboard")
        self.add_button_hover_effect(agent_dash_stop_btn, hover_color="#ff6b6b")
        
        # Row 2: MCP Server
        mcp_server_btn = tk.Button(
            control_grid,
            text="▶ MCP Server",
            command=lambda: self.start_server("mcp_server"),
            **server_button_style
        )
        mcp_server_btn.grid(row=2, column=0, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(mcp_server_btn, "Start Unreal MCP Server")
        self.add_button_hover_effect(mcp_server_btn)
        
        mcp_server_stop_btn = tk.Button(
            control_grid,
            text="⏹",
            command=lambda: self.stop_server("mcp_server"),
            font=("Segoe UI", 9),
            bg=self.error_color,
            fg=self.bg_color,
            activebackground="#ff6b6b",
            activeforeground=self.bg_color,
            relief=tk.FLAT,
            padx=10,
            pady=8,
            cursor="hand2",
            width=3
        )
        mcp_server_stop_btn.grid(row=2, column=1, padx=(0, 5), pady=5)
        self.create_tooltip(mcp_server_stop_btn, "Stop MCP Server")
        self.add_button_hover_effect(mcp_server_stop_btn, hover_color="#ff6b6b")
        
        # Row 3: Demo Scripts Section Header
        demo_header = tk.Label(
            control_grid,
            text="Demo Scripts",
            font=("Segoe UI", 9, "bold"),
            bg=self.bg_tertiary,
            fg=self.fg_secondary,
            anchor=tk.W
        )
        demo_header.grid(row=3, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=(10, 5))
        
        # Row 4: Phase 3 Demo
        phase3_demo_btn = tk.Button(
            control_grid,
            text="▶ Phase 3 Demo",
            command=lambda: self.start_server("phase3_demo"),
            **server_button_style
        )
        phase3_demo_btn.grid(row=4, column=0, sticky=tk.EW, padx=5, pady=5)
        self.create_tooltip(phase3_demo_btn, "Run Phase 3 Orchestrator Demo")
        self.add_button_hover_effect(phase3_demo_btn)
        
        phase3_demo_stop_btn = tk.Button(
            control_grid,
            text="⏹",
            command=lambda: self.stop_server("phase3_demo"),
            font=("Segoe UI", 9),
            bg=self.error_color,
            fg=self.bg_color,
            activebackground="#ff6b6b",
            activeforeground=self.bg_color,
            relief=tk.FLAT,
            padx=10,
            pady=8,
            cursor="hand2",
            width=3
        )
        phase3_demo_stop_btn.grid(row=4, column=1, padx=(0, 5), pady=5)
        self.create_tooltip(phase3_demo_stop_btn, "Stop Phase 3 Demo")
        self.add_button_hover_effect(phase3_demo_stop_btn, hover_color="#ff6b6b")
        
        # Configure grid weights for proper column sizing
        control_grid.columnconfigure(0, weight=1)
        control_grid.columnconfigure(1, weight=0)
        
        paned_window.add(controls_frame, weight=0)
        
        # --- Bottom Section: Server Output ---
        output_frame = tk.Frame(paned_window, bg=self.bg_tertiary)
        
        output_header_frame = tk.Frame(output_frame, bg=self.bg_tertiary)
        output_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        output_header = tk.Label(
            output_header_frame,
            text="📊 Server Output",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_tertiary,
            fg=self.accent_color,
            anchor=tk.W
        )
        output_header.pack(side=tk.LEFT)
        
        # Server status label
        self.server_status_label = tk.Label(
            output_header_frame,
            text="Ready",
            font=("Segoe UI", 9),
            bg=self.bg_tertiary,
            fg=self.fg_muted,
            anchor=tk.W
        )
        self.server_status_label.pack(side=tk.RIGHT)
        
        # Server output with scrollbar
        output_text_frame = tk.Frame(output_frame, bg=self.text_bg, 
                                     highlightthickness=1, highlightbackground=self.border_color)
        output_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.server_output = scrolledtext.ScrolledText(
            output_text_frame,
            wrap=tk.WORD,
            height=15,
            state=tk.DISABLED,
            bg=self.text_bg,
            fg=self.fg_color,
            font=("Consolas", 9),
            relief=tk.FLAT,
            padx=10,
            pady=10,
            selectbackground=self.highlight_bg,
            selectforeground=self.fg_color,
            borderwidth=0
        )
        self.server_output.pack(fill=tk.BOTH, expand=True)
        
        # Configure server output tags
        self.server_output.tag_config("header", foreground=self.accent_color, font=("Consolas", 10, "bold"))
        self.server_output.tag_config("success", foreground=self.success_color, font=("Consolas", 9))
        self.server_output.tag_config("error", foreground=self.error_color, font=("Consolas", 9))
        self.server_output.tag_config("warning", foreground=self.warning_color, font=("Consolas", 9))
        self.server_output.tag_config("info", foreground=self.fg_secondary, font=("Consolas", 9))
        self.server_output.tag_config("command", foreground=self.fg_muted, font=("Consolas", 8, "italic"))
        
        paned_window.add(output_frame, weight=1)
        
        # Initialize server process tracking
        self.server_processes = {}
        self.server_process_lock = threading.Lock()
        
        # Add initial message
        self.server_output.config(state=tk.NORMAL)
        self.server_output.insert(tk.END, "🖥️ Server Management\n\n", "header")
        self.server_output.insert(tk.END, "Click a server button above to start services.\n", "info")
        self.server_output.insert(tk.END, "Output from running servers will appear here.\n", "info")
        self.server_output.config(state=tk.DISABLED)
    
    def create_debug_logs_tab(self):
        """Create the Debug Logs tab for viewing application logs."""
        debug_tab = tk.Frame(self.notebook, bg=self.bg_tertiary)
        self.notebook.add(debug_tab, text="🐛 Debug Logs")
        
        # Header section
        header_frame = tk.Frame(debug_tab, bg=self.bg_tertiary, padx=15, pady=10)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text="🐛 Debug Logs & Diagnostics",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_tertiary,
            fg=self.fg_color
        )
        title_label.pack(side=tk.LEFT)
        
        # Button frame for controls
        button_frame = tk.Frame(header_frame, bg=self.bg_tertiary)
        button_frame.pack(side=tk.RIGHT)
        
        # Refresh button
        refresh_button = tk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self.refresh_debug_logs,
            font=("Segoe UI", 9),
            bg=self.accent_color,
            fg=self.bg_color,
            activebackground=self.accent_hover,
            activeforeground=self.bg_color,
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2"
        )
        refresh_button.pack(side=tk.LEFT, padx=2)
        self.create_tooltip(refresh_button, "Refresh log display")
        
        # Auto-refresh checkbox
        self.auto_refresh_logs = tk.BooleanVar(value=False)
        auto_refresh_check = tk.Checkbutton(
            button_frame,
            text="Auto-refresh",
            variable=self.auto_refresh_logs,
            command=self.toggle_auto_refresh_logs,
            font=("Segoe UI", 9),
            bg=self.bg_tertiary,
            fg=self.fg_color,
            selectcolor=self.bg_color,
            activebackground=self.bg_tertiary,
            activeforeground=self.fg_color,
            cursor="hand2"
        )
        auto_refresh_check.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(auto_refresh_check, "Auto-refresh logs every 5 seconds")
        
        # Clear button
        clear_button = tk.Button(
            button_frame,
            text="🗑️ Clear",
            command=self.clear_debug_logs,
            font=("Segoe UI", 9),
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.button_hover,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2"
        )
        clear_button.pack(side=tk.LEFT, padx=2)
        self.create_tooltip(clear_button, "Clear log display")
        
        # Info section
        info_frame = tk.Frame(debug_tab, bg=self.bg_tertiary, padx=15, pady=5)
        info_frame.pack(fill=tk.X)
        
        self.log_file_label = tk.Label(
            info_frame,
            text="Log file: Checking...",
            font=("Segoe UI", 8),
            bg=self.bg_tertiary,
            fg=self.fg_secondary,
            anchor="w"
        )
        self.log_file_label.pack(side=tk.LEFT)
        
        # Log display area
        log_frame = tk.Frame(debug_tab, bg=self.bg_tertiary, padx=15, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text widget with scrollbar
        self.debug_log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            selectbackground=self.highlight_bg,
            selectforeground=self.fg_color,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            state=tk.DISABLED
        )
        self.debug_log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for log levels
        self.debug_log_text.tag_config("DEBUG", foreground="#858585")
        self.debug_log_text.tag_config("INFO", foreground="#40a9ff")
        self.debug_log_text.tag_config("WARNING", foreground="#ce9178")
        self.debug_log_text.tag_config("ERROR", foreground="#f48771")
        self.debug_log_text.tag_config("CRITICAL", foreground="#ff0000", font=("Consolas", 9, "bold"))
        
        # Initialize auto-refresh state
        self.log_refresh_timer = None
        
        # Load logs initially
        self.refresh_debug_logs()
    
    def refresh_debug_logs(self):
        """Refresh the debug logs display."""
        # Find the latest log file
        log_dir = Path(__file__).parent / "logs"
        if not log_dir.exists():
            self.debug_log_text.config(state=tk.NORMAL)
            self.debug_log_text.delete(1.0, tk.END)
            self.debug_log_text.insert(tk.END, "No logs directory found.\n")
            self.debug_log_text.insert(tk.END, "Logs will be created when the application runs.\n")
            self.debug_log_text.config(state=tk.DISABLED)
            self.log_file_label.config(text="Log file: None")
            return
        
        log_files = sorted(log_dir.glob("adastrea_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not log_files:
            self.debug_log_text.config(state=tk.NORMAL)
            self.debug_log_text.delete(1.0, tk.END)
            self.debug_log_text.insert(tk.END, "No log files found.\n")
            self.debug_log_text.config(state=tk.DISABLED)
            self.log_file_label.config(text="Log file: None")
            return
        
        latest_log = log_files[0]
        
        # Update log file label
        file_size = latest_log.stat().st_size
        size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.1f} MB"
        self.log_file_label.config(text=f"Log file: {latest_log.name} ({size_str})")
        
        # Read log file (last 10000 lines to avoid memory issues)
        try:
            with open(latest_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Keep last 10000 lines to avoid memory issues
                if len(lines) > 10000:
                    lines = lines[-10000:]
                log_content = ''.join(lines)
        except Exception as e:
            log_content = f"Error reading log file: {e}\n"
        
        # Update text widget
        self.debug_log_text.config(state=tk.NORMAL)
        self.debug_log_text.delete(1.0, tk.END)
        
        # Parse and colorize log content in chunks to avoid UI freezing
        lines = log_content.split('\n')
        chunk_size = 500  # Process 500 lines at a time
        
        for i in range(0, len(lines), chunk_size):
            chunk = lines[i:i + chunk_size]
            for line in chunk:
                if not line.strip():
                    self.debug_log_text.insert(tk.END, "\n")
                    continue
                
                # Detect log level and apply tag
                tag = None
                if " - DEBUG - " in line:
                    tag = "DEBUG"
                elif " - INFO - " in line:
                    tag = "INFO"
                elif " - WARNING - " in line:
                    tag = "WARNING"
                elif " - ERROR - " in line:
                    tag = "ERROR"
                elif " - CRITICAL - " in line:
                    tag = "CRITICAL"
                
                if tag:
                    self.debug_log_text.insert(tk.END, line + "\n", tag)
                else:
                    self.debug_log_text.insert(tk.END, line + "\n")
            
            # Update UI between chunks to keep responsive
            self.debug_log_text.update_idletasks()
        
        self.debug_log_text.config(state=tk.DISABLED)
        # Auto-scroll to bottom
        self.debug_log_text.see(tk.END)
    
    def clear_debug_logs(self):
        """Clear the debug logs display."""
        self.debug_log_text.config(state=tk.NORMAL)
        self.debug_log_text.delete(1.0, tk.END)
        self.debug_log_text.insert(tk.END, "Logs cleared. Click Refresh to reload.\n")
        self.debug_log_text.config(state=tk.DISABLED)
    
    def toggle_auto_refresh_logs(self):
        """Toggle auto-refresh for debug logs."""
        if self.auto_refresh_logs.get():
            # Start auto-refresh
            self.auto_refresh_logs_worker()
        else:
            # Stop auto-refresh
            if self.log_refresh_timer:
                self.root.after_cancel(self.log_refresh_timer)
                self.log_refresh_timer = None
    
    def auto_refresh_logs_worker(self):
        """Worker function for auto-refreshing logs."""
        if self.auto_refresh_logs.get():
            self.refresh_debug_logs()
            # Schedule next refresh
            self.log_refresh_timer = self.root.after(5000, self.auto_refresh_logs_worker)
    
    def start_server(self, server_type):
        """Start a backend server."""
        # Check if already running (thread-safe)
        with self.server_process_lock:
            if server_type in self.server_processes and self.server_processes[server_type] is not None:
                if self.server_processes[server_type].poll() is None:
                    messagebox.showwarning("Server Running", f"{server_type} is already running.")
                    return
        
        # Map server types to commands
        server_commands = {
            "agent_orchestrator": [PYTHON_EXECUTABLE, "agent_orchestrator_cli.py", "start", "--all"],
            "agent_dashboard": [PYTHON_EXECUTABLE, "agent_dashboard.py", "--auto-start"],
            "mcp_server": [PYTHON_EXECUTABLE, "-m", "mcp_server.server"],
            "phase3_demo": [PYTHON_EXECUTABLE, "phase3_demo.py"],
        }
        
        if server_type not in server_commands:
            messagebox.showerror("Error", f"Unknown server type: {server_type}")
            return
        
        command = server_commands[server_type]
        server_name = {
            "agent_orchestrator": "Agent Orchestrator",
            "agent_dashboard": "Agent Dashboard",
            "mcp_server": "MCP Server",
            "phase3_demo": "Phase 3 Demo",
        }[server_type]
        
        # Add header to output
        self.server_output.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.server_output.insert(tk.END, f"\n{'='*60}\n", "info")
        self.server_output.insert(tk.END, f"🖥️ Starting: {server_name}\n", "header")
        self.server_output.insert(tk.END, f"Started: {timestamp}\n", "info")
        self.server_output.insert(tk.END, f"Command: {' '.join(command)}\n\n", "command")
        self.server_output.config(state=tk.DISABLED)
        
        # Update status
        self.server_status_label.config(text=f"Starting: {server_name}", fg=self.accent_color)
        
        # Run server in thread
        thread = threading.Thread(target=self._run_server_command, args=(command, server_name, server_type), daemon=True)
        thread.start()
    
    def _run_server_command(self, command, server_name, server_type):
        """Execute server command and stream output."""
        process = None
        try:
            kwargs = {
                'stdout': subprocess.PIPE,
                'stderr': subprocess.STDOUT,
                'text': True,
                'cwd': SCRIPT_DIR,
                'bufsize': 1
            }
            
            if sys.platform == 'win32' and hasattr(subprocess, 'CREATE_NO_WINDOW'):
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            # Start the process (thread-safe)
            process = subprocess.Popen(command, **kwargs)
            with self.server_process_lock:
                self.server_processes[server_type] = process
            
            # Update status
            self.root.after(0, lambda: self.server_status_label.config(
                text=f"Running: {server_name}", fg=self.success_color))
            
            # Stream output
            try:
                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.root.after(0, self._append_server_output, line)
            except Exception as read_error:
                self.root.after(0, self._append_server_output, f"\nWarning: Error reading output: {read_error}\n")
            finally:
                if process.stdout:
                    process.stdout.close()
            
            # Wait for process to complete
            process.wait()
            returncode = process.returncode
            
            # Update UI with results
            self.root.after(0, self._finalize_server_results, returncode, server_name, server_type)
            
        except Exception as e:
            self.root.after(0, self._show_server_error, str(e), server_name, server_type)
        finally:
            # Ensure process cleanup (thread-safe)
            if process and process.poll() is None:
                try:
                    process.terminate()
                except Exception:
                    pass
            with self.server_process_lock:
                if server_type in self.server_processes:
                    self.server_processes[server_type] = None
    
    def _append_server_output(self, line):
        """Append a line to server output."""
        self.server_output.config(state=tk.NORMAL)
        # Determine tag based on content
        line_lower = line.lower()
        if "error" in line_lower or "failed" in line_lower:
            tag = "error"
        elif "warning" in line_lower or "warn" in line_lower:
            tag = "warning"
        elif "success" in line_lower or "started" in line_lower:
            tag = "success"
        else:
            tag = "info"
        
        self.server_output.insert(tk.END, line, tag)
        self.server_output.see(tk.END)
        self.server_output.config(state=tk.DISABLED)
    
    def _finalize_server_results(self, returncode, server_name, server_type):
        """Display final server results."""
        self.server_output.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.server_output.insert(tk.END, f"\n{'='*60}\n", "info")
        self.server_output.insert(tk.END, f"Stopped: {timestamp}\n", "info")
        
        if returncode == 0:
            self.server_output.insert(tk.END, f"✅ {server_name} exited normally\n", "success")
        else:
            self.server_output.insert(tk.END, f"❌ {server_name} exited with code: {returncode}\n", "error")
        
        self.server_output.config(state=tk.DISABLED)
        self.server_output.see(tk.END)
        
        self.server_status_label.config(text="Ready", fg=self.fg_muted)
    
    def _show_server_error(self, error_msg, server_name, server_type):
        """Show error when server execution fails."""
        self.server_output.config(state=tk.NORMAL)
        self.server_output.insert(tk.END, f"\n❌ Error running {server_name}:\n", "error")
        self.server_output.insert(tk.END, f"{error_msg}\n", "error")
        self.server_output.config(state=tk.DISABLED)
        self.server_output.see(tk.END)
        
        self.server_status_label.config(text="Error", fg=self.error_color)
    
    def stop_server(self, server_type):
        """Stop a specific server."""
        with self.server_process_lock:
            process = self.server_processes.get(server_type)
            
        if process and process.poll() is None:
            try:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                
                self.server_output.config(state=tk.NORMAL)
                self.server_output.insert(tk.END, f"\n⏹ {server_type} stopped by user\n", "warning")
                self.server_output.config(state=tk.DISABLED)
                self.server_output.see(tk.END)
                
                with self.server_process_lock:
                    self.server_processes[server_type] = None
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to stop {server_type}: {e}")
        else:
            messagebox.showinfo("Not Running", f"{server_type} is not currently running.")
    
    def stop_all_servers(self):
        """Stop all running servers."""
        with self.server_process_lock:
            running_servers = [(name, proc) for name, proc in self.server_processes.items() 
                             if proc is not None and proc.poll() is None]
        
        if not running_servers:
            messagebox.showinfo("No Servers", "No servers are currently running.")
            return
        
        for server_name, process in running_servers:
            try:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            except Exception:
                pass
        
        with self.server_process_lock:
            self.server_processes.clear()
        
        self.server_output.config(state=tk.NORMAL)
        self.server_output.insert(tk.END, f"\n⏹ All servers stopped\n", "warning")
        self.server_output.config(state=tk.DISABLED)
        self.server_output.see(tk.END)
        
        self.server_status_label.config(text="Ready", fg=self.fg_muted)
    
    def clear_server_output(self):
        """Clear the server output display."""
        self.server_output.config(state=tk.NORMAL)
        self.server_output.delete(1.0, tk.END)
        self.server_output.insert(tk.END, "🖥️ Server Management\n\n", "header")
        self.server_output.insert(tk.END, "Click a server button above to start services.\n", "info")
        self.server_output.insert(tk.END, "Output from running servers will appear here.\n", "info")
        self.server_output.config(state=tk.DISABLED)
        self.server_status_label.config(text="Ready", fg=self.fg_muted)
    
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
        edit_menu.add_command(label="Settings...", command=self.open_settings, accelerator="Ctrl+,")
        
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
        self.root.bind("<Control-u>", lambda e: self.ingest_folder())
        self.root.bind("<Control-U>", lambda e: self.ingest_folder())
        self.root.bind("<Control-l>", lambda e: self.clear_conversation())
        self.root.bind("<Control-L>", lambda e: self.clear_conversation())
        self.root.bind("<Control-e>", lambda e: self.export_conversation())
        self.root.bind("<Control-E>", lambda e: self.export_conversation())
        self.root.bind("<Control-comma>", lambda e: self.open_settings())
        # Note: Ctrl+C is handled separately for copy
    
    def show_welcome_message(self):
        """Display a welcome message on startup."""
        welcome = """🤖 Welcome to Adastrea Director!

Your AI-powered game development assistant is ready to help.

📊 Check the Home tab to see system connection status and recent activity.

Getting Started:
1. Set your Gemini API Key (🔑 button or Ctrl+K)
2. Load documents into the knowledge base:
   • 📁 Ingest Folder - Select a folder containing your docs (Ctrl+U)
   • 📄 Ingest File - Select a single document to add
   • 🔗 Ingest Repo - Clone and ingest from a GitHub repository
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
• Ctrl+U - Ingest folder

Type your question below to get started! 🚀
"""
        self.response_text.config(state=tk.NORMAL)
        self.response_text.insert(tk.END, welcome, "assistant")
        self.response_text.config(state=tk.DISABLED)
    
    def set_api_key(self):
        """Opens a dialog to ask for the API key."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Gemini API Key")
        dialog.geometry("450x230")
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
            text="Enter your Gemini API Key:",
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
        
        # Add checkbox for saving the API key
        save_var = tk.BooleanVar(value=True)  # Default to saving
        checkbox_frame = tk.Frame(dialog, bg=self.bg_color)
        checkbox_frame.pack(pady=(0, 10), padx=20)
        
        save_checkbox = tk.Checkbutton(
            checkbox_frame,
            text="Save API key for future sessions",
            variable=save_var,
            bg=self.bg_color,
            fg=self.fg_secondary,
            selectcolor=self.text_bg,
            activebackground=self.bg_color,
            activeforeground=self.fg_color,
            font=("Segoe UI", 9),
            cursor="hand2"
        )
        save_checkbox.pack(anchor=tk.W)
        
        def on_ok():
            key = key_entry.get()
            if key:
                os.environ['GEMINI_KEY'] = key
                os.environ['GOOGLE_API_KEY'] = key  # Also set for compatibility
                
                # Save to local config if checkbox is selected
                if save_var.get():
                    try:
                        import config_manager
                        config_manager.set_api_key("gemini", key)
                        self.update_status("API Key saved successfully • Ready to ingest or query", "success")
                        self.add_to_conversation("System", "Gemini API Key saved to local configuration.", is_system=True)
                    except Exception as e:
                        self.update_status(f"API Key set for session only (save failed: {e})", "warning")
                        self.add_to_conversation("System", "Gemini API Key set for current session.", is_system=True)
                else:
                    self.update_status("API Key set successfully • Ready to ingest or query", "success")
                    self.add_to_conversation("System", "Gemini API Key configured for current session.", is_system=True)
                
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
    
    def open_settings(self):
        """Opens a comprehensive settings dialog."""
        # Import config_manager once at the start
        try:
            import config_manager
        except ImportError:
            config_manager = None
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.geometry("550x600")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main container with scrollbar
        main_container = tk.Frame(dialog, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="⚙️ Settings",
            font=("Segoe UI", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # API Keys Section
        api_section = tk.LabelFrame(
            main_container,
            text="API Keys",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            padx=15,
            pady=10
        )
        api_section.pack(fill=tk.X, pady=(0, 15))
        
        # LLM Provider Selection
        llm_frame = tk.Frame(api_section, bg=self.bg_color)
        llm_frame.pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(
            llm_frame,
            text="LLM Provider:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        llm_provider_var = tk.StringVar(value=os.getenv("LLM_PROVIDER", "gemini"))
        llm_providers = [("Gemini (Recommended)", "gemini"), ("OpenAI", "openai"), ("OpenRouter", "openrouter")]
        
        for text, value in llm_providers:
            tk.Radiobutton(
                llm_frame,
                text=text,
                variable=llm_provider_var,
                value=value,
                bg=self.bg_color,
                fg=self.fg_color,
                selectcolor=self.text_bg,
                activebackground=self.bg_color,
                activeforeground=self.fg_color,
                font=("Segoe UI", 9)
            ).pack(side=tk.LEFT, padx=5)
        
        # Gemini API Key
        gemini_frame = tk.Frame(api_section, bg=self.bg_color)
        gemini_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            gemini_frame,
            text="Gemini API Key:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Segoe UI", 10)
        ).pack(anchor=tk.W, pady=(0, 5))
        
        gemini_key_entry = tk.Entry(
            gemini_frame,
            show='•',
            font=("Segoe UI", 9),
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.button_bg,
            highlightcolor=self.accent_color
        )
        gemini_key_entry.pack(fill=tk.X, pady=(0, 5))
        
        # Try to load existing key
        if config_manager:
            try:
                existing_key = config_manager.get_api_key("gemini")
                if existing_key:
                    gemini_key_entry.insert(0, existing_key)
            except (ImportError, KeyError, AttributeError):
                pass
        
        # OpenAI API Key
        openai_frame = tk.Frame(api_section, bg=self.bg_color)
        openai_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            openai_frame,
            text="OpenAI API Key:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Segoe UI", 10)
        ).pack(anchor=tk.W, pady=(0, 5))
        
        openai_key_entry = tk.Entry(
            openai_frame,
            show='•',
            font=("Segoe UI", 9),
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.button_bg,
            highlightcolor=self.accent_color
        )
        openai_key_entry.pack(fill=tk.X, pady=(0, 5))
        
        # Try to load existing key
        if config_manager:
            try:
                existing_key = config_manager.get_api_key("openai")
                if existing_key:
                    openai_key_entry.insert(0, existing_key)
            except (ImportError, KeyError, AttributeError):
                pass
        
        # OpenRouter API Key
        openrouter_frame = tk.Frame(api_section, bg=self.bg_color)
        openrouter_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            openrouter_frame,
            text="OpenRouter API Key:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Segoe UI", 10)
        ).pack(anchor=tk.W, pady=(0, 5))
        
        openrouter_key_entry = tk.Entry(
            openrouter_frame,
            show='•',
            font=("Segoe UI", 9),
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.button_bg,
            highlightcolor=self.accent_color
        )
        openrouter_key_entry.pack(fill=tk.X, pady=(0, 5))
        
        # Try to load existing key
        if config_manager:
            try:
                existing_key = config_manager.get_api_key("openrouter")
                if existing_key:
                    openrouter_key_entry.insert(0, existing_key)
            except (ImportError, KeyError, AttributeError):
                pass
        
        # Embedding Provider Selection
        embedding_frame = tk.Frame(api_section, bg=self.bg_color)
        embedding_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Label(
            embedding_frame,
            text="Embedding Provider:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        embedding_provider_var = tk.StringVar(value=os.getenv("EMBEDDING_PROVIDER", "huggingface"))
        embedding_providers = [("HuggingFace (Free)", "huggingface"), ("OpenAI", "openai")]
        
        for text, value in embedding_providers:
            tk.Radiobutton(
                embedding_frame,
                text=text,
                variable=embedding_provider_var,
                value=value,
                bg=self.bg_color,
                fg=self.fg_color,
                selectcolor=self.text_bg,
                activebackground=self.bg_color,
                activeforeground=self.fg_color,
                font=("Segoe UI", 9)
            ).pack(side=tk.LEFT, padx=5)
        
        # Display Settings Section
        display_section = tk.LabelFrame(
            main_container,
            text="Display",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            padx=15,
            pady=10
        )
        display_section.pack(fill=tk.X, pady=(0, 15))
        
        # Default Font Size
        font_frame = tk.Frame(display_section, bg=self.bg_color)
        font_frame.pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(
            font_frame,
            text="Default Font Size:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        font_size_var = tk.IntVar(value=self.current_font_size)
        font_spinbox = tk.Spinbox(
            font_frame,
            from_=8,
            to=20,
            textvariable=font_size_var,
            width=5,
            font=("Segoe UI", 9),
            bg=self.text_bg,
            fg=self.fg_color,
            buttonbackground=self.button_bg,
            relief=tk.FLAT
        )
        font_spinbox.pack(side=tk.LEFT)
        
        tk.Label(
            font_frame,
            text="pt",
            bg=self.bg_color,
            fg=self.fg_secondary,
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Auto-save Settings
        autosave_var = tk.BooleanVar(value=True)
        autosave_check = tk.Checkbutton(
            display_section,
            text="Auto-save settings",
            variable=autosave_var,
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.text_bg,
            activebackground=self.bg_color,
            activeforeground=self.fg_color,
            font=("Segoe UI", 9),
            cursor="hand2"
        )
        autosave_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Show timestamps
        timestamps_var = tk.BooleanVar(value=True)
        timestamps_check = tk.Checkbutton(
            display_section,
            text="Show timestamps in conversation",
            variable=timestamps_var,
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.text_bg,
            activebackground=self.bg_color,
            activeforeground=self.fg_color,
            font=("Segoe UI", 9),
            cursor="hand2"
        )
        timestamps_check.pack(anchor=tk.W)
        
        # Button Frame
        button_frame = tk.Frame(dialog, bg=self.bg_color)
        button_frame.pack(side=tk.BOTTOM, pady=(0, 20))
        
        def save_settings():
            """Save all settings."""
            try:
                # Save LLM provider
                os.environ['LLM_PROVIDER'] = llm_provider_var.get()
                
                # Save Gemini API key
                if config_manager:
                    gemini_key = gemini_key_entry.get().strip()
                    if gemini_key:
                        config_manager.set_api_key("gemini", gemini_key)
                        os.environ['GEMINI_KEY'] = gemini_key
                        os.environ['GOOGLE_API_KEY'] = gemini_key
                    
                    # Save OpenAI API key
                    openai_key = openai_key_entry.get().strip()
                    if openai_key:
                        config_manager.set_api_key("openai", openai_key)
                        os.environ['OPENAI_API_KEY'] = openai_key
                    
                    # Save OpenRouter API key
                    openrouter_key = openrouter_key_entry.get().strip()
                    if openrouter_key:
                        config_manager.set_api_key("openrouter", openrouter_key)
                        os.environ['OPENROUTER_API_KEY'] = openrouter_key
                
                # Save embedding provider
                os.environ['EMBEDDING_PROVIDER'] = embedding_provider_var.get()
                
                # Apply font size
                new_font_size = font_size_var.get()
                if 8 <= new_font_size <= 20:
                    self.current_font_size = new_font_size
                    self.response_font.configure(size=self.current_font_size)
                    self.response_text.tag_config("user", font=("Segoe UI", self.current_font_size, "bold"))
                
                # Save display preferences (autosave and timestamps)
                # Note: These are currently used for UI state and could be persisted to config in future
                autosave_enabled = autosave_var.get()
                show_timestamps_enabled = timestamps_var.get()
                # Apply these settings to the application state as needed
                
                self.update_status("Settings saved successfully", "success")
                self.add_to_conversation("System", "Settings updated and saved.", is_system=True)
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {e}")
        
        def cancel_settings():
            dialog.destroy()
        
        # Save button
        tk.Button(
            button_frame,
            text="Save",
            command=save_settings,
            bg=self.accent_color,
            fg="#20232b",
            activebackground=self.accent_hover,
            activeforeground="#20232b",
            relief=tk.FLAT,
            padx=30,
            pady=8,
            cursor="hand2",
            font=("Segoe UI", 10),
            borderwidth=0
        ).pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        tk.Button(
            button_frame,
            text="Cancel",
            command=cancel_settings,
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.button_active,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=30,
            pady=8,
            cursor="hand2",
            font=("Segoe UI", 10),
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.button_bg
        ).pack(side=tk.LEFT, padx=5)

    def check_api_key_on_startup(self):
        """Checks if the API key is set and prompts the user if not."""
        # Check for Gemini API key in local config, environment, or compatibility var
        has_key = False
        
        # Check local config first
        try:
            import config_manager
            stored_key = config_manager.get_api_key("gemini")
            if stored_key:
                os.environ['GEMINI_KEY'] = stored_key
                os.environ['GOOGLE_API_KEY'] = stored_key
                has_key = True
        except Exception:
            # Silently fail if config_manager is not available or config loading fails
            # This allows the app to continue and prompt for API key normally
            pass
        
        # Check environment variables
        if not has_key and (os.getenv("GEMINI_KEY") or os.getenv("GOOGLE_API_KEY")):
            has_key = True
        
        # Prompt for key if not found
        if not has_key:
            self.root.after(500, self.set_api_key)

    def ingest_folder(self):
        """Opens a folder selection dialog and ingests documents from the selected folder."""
        folder_path = filedialog.askdirectory(
            title="Select Folder to Ingest",
            initialdir=SCRIPT_DIR
        )
        
        if folder_path:
            self.add_to_conversation("System", f"Ingesting documents from: {folder_path}", is_system=True)
            self.log_to_ingest_tab(f"📁 Starting folder ingestion: {folder_path}", "info")
            self.run_script_in_thread('ingest.py', f"🤔 Ingesting documents from folder...", '--docs-dir', folder_path)
        else:
            self.update_status("Folder selection cancelled", "info")
    
    def ingest_file(self):
        """Opens a file selection dialog and ingests a single document."""
        file_path = filedialog.askopenfilename(
            title="Select File to Ingest",
            initialdir=SCRIPT_DIR,
            filetypes=[
                ("All Supported", "*.md *.txt *.py"),
                ("Markdown files", "*.md"),
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.add_to_conversation("System", f"Ingesting file: {file_path}", is_system=True)
            self.log_to_ingest_tab(f"📄 Starting file ingestion: {os.path.basename(file_path)}", "info")
            self.run_script_in_thread('ingest.py', f"🤔 Ingesting file...", '--file', file_path)
        else:
            self.update_status("File selection cancelled", "info")
    
    def ingest_github_repo(self):
        """Opens a dialog to input a GitHub repository URL and clones/ingests it."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ingest GitHub Repository")
        dialog.geometry("500x220")
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
            text="Enter GitHub Repository URL:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Segoe UI", 11)
        ).pack(pady=(20, 5), padx=20)
        
        tk.Label(
            dialog,
            text="Example: https://github.com/username/repository",
            bg=self.bg_color,
            fg=self.fg_muted,
            font=("Segoe UI", 9)
        ).pack(pady=(0, 10), padx=20)
        
        repo_entry = tk.Entry(
            dialog,
            font=("Segoe UI", 10),
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.button_bg,
            highlightcolor=self.accent_color,
            width=50
        )
        repo_entry.pack(pady=10, padx=20)
        repo_entry.focus()
        
        def on_ok():
            repo_url = repo_entry.get().strip()
            if repo_url:
                # Extract repo name from URL for folder name
                repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
                clone_dir = os.path.join('/tmp', f'github_repo_{repo_name}')
                
                # Clone the repository
                self.add_to_conversation("System", f"Cloning repository: {repo_url}", is_system=True)
                dialog.destroy()
                
                # Run git clone in a thread, then ingest
                self._clone_and_ingest_repo(repo_url, clone_dir)
            else:
                messagebox.showwarning("Invalid Input", "Please enter a valid GitHub repository URL.")
        
        def on_cancel():
            dialog.destroy()
        
        repo_entry.bind("<Return>", lambda e: on_ok())
        repo_entry.bind("<Escape>", lambda e: on_cancel())
        
        button_frame = tk.Frame(dialog, bg=self.bg_color)
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Clone & Ingest",
            command=on_ok,
            bg=self.accent_color,
            fg="#20232b",
            activebackground="#5bb8ff",
            activeforeground="#20232b",
            relief=tk.FLAT,
            padx=24,
            pady=8,
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
            activebackground=self.button_active,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=24,
            pady=8,
            cursor="hand2",
            font=("Segoe UI", 10),
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.button_bg
        ).pack(side=tk.LEFT, padx=5)
    
    def _clone_and_ingest_repo(self, repo_url, clone_dir):
        """Clone a GitHub repository and then ingest its documents."""
        import shutil
        
        # Disable buttons
        self.ingest_folder_button.config(state=tk.DISABLED)
        self.ingest_file_button.config(state=tk.DISABLED)
        self.ingest_repo_button.config(state=tk.DISABLED)
        self.ask_button.config(state=tk.DISABLED)
        self.update_status(f"Cloning repository...", "busy")
        
        def clone_and_ingest():
            try:
                # Remove existing directory if it exists
                if os.path.exists(clone_dir):
                    shutil.rmtree(clone_dir)
                
                # Clone the repository
                clone_process = subprocess.run(
                    ['git', 'clone', '--depth', '1', repo_url, clone_dir],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'  # Replace invalid UTF-8 sequences instead of failing
                )
                
                if clone_process.returncode != 0:
                    error_msg = f"Failed to clone repository:\n{clone_process.stderr}"
                    self.root.after(0, self._show_clone_error, error_msg)
                    return
                
                # Now ingest the cloned repository
                self.root.after(0, self._ingest_cloned_repo, clone_dir)
                
            except Exception as e:
                self.root.after(0, self._show_clone_error, str(e))
        
        thread = threading.Thread(target=clone_and_ingest)
        thread.start()
    
    def _show_clone_error(self, error_msg):
        """Show error message when cloning fails."""
        self.response_text.config(state=tk.NORMAL)
        self.response_text.insert(tk.END, "❌ ", "error")
        self.response_text.insert(tk.END, f"Error cloning repository:\n{error_msg}\n\n", "error")
        self.response_text.see(tk.END)
        self.response_text.config(state=tk.DISABLED)
        self.update_status("Failed to clone repository", "error")
        
        # Re-enable buttons
        self.ingest_folder_button.config(state=tk.NORMAL)
        self.ingest_file_button.config(state=tk.NORMAL)
        self.ingest_repo_button.config(state=tk.NORMAL)
        self.ask_button.config(state=tk.NORMAL)
    
    def _ingest_cloned_repo(self, clone_dir):
        """Ingest documents from the cloned repository."""
        self.add_to_conversation("System", f"Repository cloned successfully. Ingesting documents...", is_system=True)
        self.run_script_in_thread('ingest.py', f"🤔 Ingesting documents from repository...", '--docs-dir', clone_dir)

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
• Ctrl+, - Open Settings dialog

Actions:
• Enter or Ctrl+Enter - Send question
• Ctrl+U - Ingest folder (opens file dialog)

Navigation:
• Alt+F4 - Exit application
"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def show_about(self):
        """Display about information."""
        about_text = """Adastrea Director
AI Game Development Assistant

Version: 1.0.0 (MVP)
An intelligent assistant system for game development in Unreal Engine.

Features:
• Context-aware Q&A using RAG
• Document ingestion and processing
• Natural language interface
• Goal analysis and task decomposition
• Autonomous performance profiling and bug detection

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
    
    def show_progress_bar(self, label_text="Processing..."):
        """Show the progress bar with initial text."""
        self.progress_label.config(text=label_text)
        self.progress_details.config(text="")
        self.progress_bar['value'] = 0
        self.progress_card.pack(fill=tk.X, pady=(0, 15), before=self.notebook.master)
    
    def hide_progress_bar(self):
        """Hide the progress bar."""
        self.progress_card.pack_forget()
        if self.progress_poll_id:
            self.root.after_cancel(self.progress_poll_id)
            self.progress_poll_id = None
    
    def update_progress(self, percent, label_text=None, details_text=None):
        """Update the progress bar value and text."""
        self.progress_bar['value'] = percent
        if label_text:
            self.progress_label.config(text=label_text)
        if details_text:
            self.progress_details.config(text=details_text)
    
    def poll_progress_file(self):
        """Poll the progress file for updates."""
        if not self.progress_file:
            return
        
        try:
            with open(self.progress_file, 'r') as f:
                progress_data = json.load(f)
            
            percent = progress_data.get('percent', 0)
            label = progress_data.get('label', 'Processing...')
            details = progress_data.get('details', '')
            
            # Log progress updates to the ingestion log
            self.log_to_ingest_tab(f"{label}{': ' + details if details else ''}", "progress")
            
            self.update_progress(percent, label, details)
            
            # Continue polling if not complete
            if percent < 100:
                self.progress_poll_id = self.root.after(PROGRESS_POLL_INTERVAL_MS, self.poll_progress_file)
        except FileNotFoundError:
            # File is gone, stop polling
            self.hide_progress_bar()
        except json.JSONDecodeError:
            # File might be being written, try again
            self.progress_poll_id = self.root.after(PROGRESS_POLL_INTERVAL_MS, self.poll_progress_file)
        except IOError:
            # Other IO error, stop polling
            self.hide_progress_bar()
    
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
        self.ingest_folder_button.config(state=tk.DISABLED)
        self.ingest_file_button.config(state=tk.DISABLED)
        self.ingest_repo_button.config(state=tk.DISABLED)
        self.ask_button.config(state=tk.DISABLED)
        self.update_status(status_message, "busy")
        
        # Use absolute path for the script to ensure it can be found
        script_path = os.path.join(SCRIPT_DIR, script_name)
        command = [PYTHON_EXECUTABLE, script_path] + list(args)
        
        # Enable progress tracking for ingest.py
        show_progress = script_name == 'ingest.py'
        if show_progress:
            # Create a temporary progress file (using NamedTemporaryFile for security)
            temp_file = tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.json', 
                prefix='adastrea_progress_',
                delete=False
            )
            self.progress_file = temp_file.name
            temp_file.close()  # Close but don't delete (delete=False)
            command.extend(['--progress-file', self.progress_file])
            self.show_progress_bar("Preparing to ingest documents...")
            self.log_to_ingest_tab("⚙️ Initializing ingestion process...", "info")
            # Start polling the progress file at configured interval
            self.progress_poll_id = self.root.after(PROGRESS_POLL_INTERVAL_MS, self.poll_progress_file)

        thread = threading.Thread(target=self._execute_command, args=(command, show_progress))
        thread.start()

    def _get_subprocess_kwargs(self, merge_stderr=False):
        """
        Build subprocess.Popen kwargs with platform-specific settings.
        
        Args:
            merge_stderr: If True, merge stderr into stdout for unified streaming
            
        Returns:
            Dictionary of kwargs for subprocess.Popen
        """
        kwargs = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.STDOUT if merge_stderr else subprocess.PIPE,
            'text': True
        }
        if sys.platform == 'win32' and hasattr(subprocess, 'CREATE_NO_WINDOW'):
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        return kwargs
    
    def _execute_command(self, command, show_progress=False):
        """The actual command execution logic."""
        process = None
        try:
            # For ingestion, stream output line by line to the log
            if show_progress:
                # Line buffering for real-time output, keep stderr separate for better error handling
                kwargs = self._get_subprocess_kwargs(merge_stderr=False)
                kwargs['bufsize'] = 1  # Line buffering in text mode
                
                process = subprocess.Popen(command, **kwargs)
                
                # Batch output updates for better performance
                output_batch = []
                batch_size = 5  # Batch size for UI updates
                
                try:
                    # Stream stdout line by line until process completes
                    for line in iter(process.stdout.readline, ''):
                        # Strip line for display (original with newline not needed)
                        stripped_line = line.rstrip()
                        output_batch.append(stripped_line)
                        
                        # Batch UI updates to avoid overwhelming event queue
                        if len(output_batch) >= batch_size:
                            batch_copy = output_batch.copy()
                            self.root.after(0, self._append_ingest_output_batch, batch_copy)
                            output_batch.clear()
                    
                    # Send any remaining lines
                    if output_batch:
                        batch_copy = output_batch.copy()
                        self.root.after(0, self._append_ingest_output_batch, batch_copy)
                    
                    # Close stdout before reading stderr to avoid blocking
                    if process.stdout and not process.stdout.closed:
                        process.stdout.close()
                    
                    # Wait for process to complete to ensure all stderr is available
                    process.wait()
                    
                    # Read stderr after process completes (non-blocking)
                    stderr_output = process.stderr.read() if process.stderr else ""
                    
                except (IOError, UnicodeDecodeError, OSError) as read_error:
                    # Handle specific expected exceptions during output reading
                    error_type = type(read_error).__name__
                    error_msg = f"Warning: {error_type} reading ingestion process output: {read_error}"
                    self.root.after(0, self._append_ingest_output, error_msg)
                    stderr_output = ""
                    # Terminate the process if it's still running
                    if process.poll() is None:
                        process.terminate()
                        process.wait()
                finally:
                    # Ensure stdout is closed (stderr closed by communicate/read above)
                    if process.stdout and not process.stdout.closed:
                        process.stdout.close()
                    if process.stderr and not process.stderr.closed:
                        process.stderr.close()
                
                # Ensure process has completed and returncode is set
                if process.returncode is None:
                    process.wait()
                
                # Build summary output for conversation tab (not full duplicate)
                if process.returncode == 0:
                    output = "Ingestion completed successfully. See Ingest List tab for details."
                else:
                    # Include errors in summary for conversation tab
                    output = f"Ingestion failed with exit code {process.returncode}."
                    if stderr_output:
                        output += f"\n--- ERROR ---\n{stderr_output}"
            else:
                # For non-ingestion commands, use the old buffered method
                kwargs = self._get_subprocess_kwargs(merge_stderr=False)
                
                process = subprocess.Popen(command, **kwargs)
                stdout, stderr = process.communicate()
                output = stdout
                if process.returncode != 0:
                    output += f"\n--- ERROR ---\n{stderr}"
            
            # Schedule the UI update to run on the main thread
            self.root.after(0, self._update_ui_after_execution, output, process.returncode, show_progress)

        except Exception as e:
            # Ensure returncode is set for unexpected exceptions
            returncode = process.returncode if process and process.returncode is not None else 1
            self.root.after(0, self._update_ui_after_execution, str(e), returncode, show_progress)

    def _update_ui_after_execution(self, output, returncode, show_progress=False):
        """Updates the GUI elements after the script has finished."""
        # Clean up progress tracking if it was used
        if show_progress:
            self.hide_progress_bar()
            if self.progress_file and os.path.exists(self.progress_file):
                try:
                    os.remove(self.progress_file)
                except OSError:
                    pass
            self.progress_file = None
        
        # Clean up the output
        output = output.strip()
        
        if returncode == 0:
            if output:
                # Add assistant response to conversation
                self.add_to_conversation("Assistant", output)
            self.update_status("Ready • Waiting for your question", "success")
            # Log and refresh ingest list after successful ingestion
            if show_progress:
                self.log_to_ingest_tab("✅ Ingestion completed successfully", "success")
                self.refresh_ingest_list()
        else:
            # Add error to conversation
            error_message = f"Error occurred:\n{output}"
            self.response_text.config(state=tk.NORMAL)
            self.response_text.insert(tk.END, "❌ ", "error")
            self.response_text.insert(tk.END, error_message + "\n\n", "error")
            self.response_text.see(tk.END)
            self.response_text.config(state=tk.DISABLED)
            self.update_status("An error occurred • Check the conversation for details", "error")
            # Log error for ingestion failures (truncate long errors for readability)
            if show_progress:
                error_msg = output[:MAX_ERROR_LOG_LENGTH]
                if len(output) > MAX_ERROR_LOG_LENGTH:
                    error_msg += "..."
                self.log_to_ingest_tab(f"❌ Ingestion failed: {error_msg}", "error")
            
        self.ingest_folder_button.config(state=tk.NORMAL)
        self.ingest_file_button.config(state=tk.NORMAL)
        self.ingest_repo_button.config(state=tk.NORMAL)
        self.ask_button.config(state=tk.NORMAL)
        self.query_entry.focus()
    
    def run_test_suite(self, test_type):
        """Run a specific test suite."""
        # Check if a test is already running (thread-safe)
        with self.test_process_lock:
            if self.current_test_process is not None:
                messagebox.showwarning("Test Running", "A test is already running. Please wait for it to complete or stop it first.")
                return
        
        # Map test types to commands
        test_commands = {
            "all": [PYTHON_EXECUTABLE, "-m", "pytest", "-v", "--tb=short"],
            "plugin": [PYTHON_EXECUTABLE, "-m", "pytest", "-v", "Plugins/AdastreaDirector/Python/", "--tb=short"],
            "unit": [PYTHON_EXECUTABLE, "-m", "pytest", "-v", "-m", "unit", "--tb=short"],
            "integration": [PYTHON_EXECUTABLE, "-m", "pytest", "-v", "tests/integration/", "--tb=short"],
            "phase3": [PYTHON_EXECUTABLE, "-m", "pytest", "-v", "tests/phase3/", "--tb=short"],
            "validation": [PYTHON_EXECUTABLE, "validate_requirements.py"],
            "remote": [PYTHON_EXECUTABLE, "-m", "pytest", "-v", "tests/remote_control/", "--tb=short"],
            "mcp": [PYTHON_EXECUTABLE, "-m", "pytest", "-v", "tests/mcp_server/", "--tb=short"],
            "gui": [PYTHON_EXECUTABLE, "-m", "pytest", "-v", "tests/test_gui_director.py", "--tb=short"],
            "compatibility": [PYTHON_EXECUTABLE, "check_compatibility.py"],
            "install": [PYTHON_EXECUTABLE, "install_dependencies.py"]
        }
        
        if test_type not in test_commands:
            messagebox.showerror("Error", f"Unknown test type: {test_type}")
            return
        
        command = test_commands[test_type]
        test_name = {
            "all": "All Tests (pytest)",
            "plugin": "Plugin Tests",
            "unit": "Unit Tests",
            "integration": "Integration Tests",
            "phase3": "Phase 3 Tests",
            "validation": "Validation Scripts",
            "remote": "Remote Control Tests",
            "mcp": "MCP Tests",
            "gui": "GUI Tests",
            "compatibility": "Compatibility Check",
            "install": "Install Dependencies"
        }[test_type]
        
        # Clear previous output
        self.test_output.config(state=tk.NORMAL)
        self.test_output.delete(1.0, tk.END)
        
        # Add header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.test_output.insert(tk.END, f"🧪 Running: {test_name}\n", "header")
        self.test_output.insert(tk.END, f"Started: {timestamp}\n", "info")
        self.test_output.insert(tk.END, f"Command: {' '.join(command)}\n\n", "command")
        self.test_output.config(state=tk.DISABLED)
        
        # Update status
        self.test_status_label.config(text=f"Running: {test_name}", fg=self.accent_color)
        self.update_status(f"Running {test_name}...", "busy")
        
        # Disable all test buttons to prevent concurrent tests
        for btn in self.test_buttons:
            btn.config(state=tk.DISABLED)
        
        # Enable stop button
        self.stop_test_button.config(state=tk.NORMAL)
        
        # Run tests in thread (daemon=True ensures it won't prevent app shutdown)
        thread = threading.Thread(target=self._run_test_command, args=(command, test_name), daemon=True)
        thread.start()
    
    def _run_test_command(self, command, test_name):
        """Execute test command and stream output."""
        process = None
        try:
            # Change to script directory
            kwargs = {
                'stdout': subprocess.PIPE,
                'stderr': subprocess.STDOUT,
                'text': True,  # Handle text mode (universal_newlines deprecated)
                'cwd': SCRIPT_DIR,
                'bufsize': 1  # Line buffered
            }
            
            if sys.platform == 'win32' and hasattr(subprocess, 'CREATE_NO_WINDOW'):
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            # Start the process (thread-safe)
            process = subprocess.Popen(command, **kwargs)
            with self.test_process_lock:
                self.current_test_process = process
            
            # Stream output with batching to avoid flooding the event queue
            output_batch = []
            batch_size = TEST_OUTPUT_BATCH_SIZE
            
            try:
                for line in iter(process.stdout.readline, ''):
                    if line:
                        output_batch.append(line)
                        if len(output_batch) >= batch_size:
                            # Send batch to UI
                            batch_copy = output_batch.copy()
                            self.root.after(0, self._append_test_output_batch, batch_copy)
                            output_batch.clear()
                
                # Send any remaining lines
                if output_batch:
                    batch_copy = output_batch.copy()
                    self.root.after(0, self._append_test_output_batch, batch_copy)
                    
            except Exception as read_error:
                # Log read error but continue to get return code
                self.root.after(0, self._append_test_output, f"\nWarning: Error reading output: {read_error}\n")
            finally:
                # Ensure stdout is closed
                if process.stdout:
                    process.stdout.close()
            
            # Wait for process to complete
            process.wait()
            returncode = process.returncode
            
            # Update UI with results
            self.root.after(0, self._finalize_test_results, returncode, test_name)
            
        except Exception as e:
            self.root.after(0, self._show_test_error, str(e), test_name)
        finally:
            # Ensure process cleanup (thread-safe)
            if process and process.poll() is None:
                try:
                    process.terminate()
                except Exception:
                    pass
            with self.test_process_lock:
                self.current_test_process = None
    
    def _determine_output_tag(self, line):
        """Determine the appropriate tag for test output based on content."""
        line_lower = line.lower()
        if "passed" in line_lower or "✓" in line or "ok" in line_lower:
            return "pass"
        elif "failed" in line_lower or "error" in line_lower or "✗" in line:
            return "fail"
        elif "warning" in line_lower or "warn" in line_lower:
            return "warning"
        else:
            return "info"
    
    def _append_test_output(self, line):
        """Append a line to test output with appropriate formatting."""
        self.test_output.config(state=tk.NORMAL)
        tag = self._determine_output_tag(line)
        self.test_output.insert(tk.END, line, tag)
        self.test_output.see(tk.END)
        self.test_output.config(state=tk.DISABLED)
    
    def _append_test_output_batch(self, lines):
        """Append multiple lines to test output for better performance."""
        self.test_output.config(state=tk.NORMAL)
        
        for line in lines:
            tag = self._determine_output_tag(line)
            self.test_output.insert(tk.END, line, tag)
        
        self.test_output.see(tk.END)
        self.test_output.config(state=tk.DISABLED)
    
    def _finalize_test_results(self, returncode, test_name):
        """Display final test results."""
        self.test_output.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.test_output.insert(tk.END, f"\n{'='*60}\n", "info")
        self.test_output.insert(tk.END, f"Completed: {timestamp}\n", "info")
        
        if returncode == 0:
            self.test_output.insert(tk.END, f"✅ {test_name} PASSED\n", "pass")
            self.test_status_label.config(text=f"✅ {test_name} Passed", fg=self.success_color)
            self.update_status(f"{test_name} completed successfully", "success")
        else:
            self.test_output.insert(tk.END, f"❌ {test_name} FAILED (exit code: {returncode})\n", "fail")
            self.test_status_label.config(text=f"❌ {test_name} Failed", fg=self.error_color)
            self.update_status(f"{test_name} failed", "error")
        
        self.test_output.config(state=tk.DISABLED)
        self.test_output.see(tk.END)
        
        # Re-enable all test buttons
        for btn in self.test_buttons:
            btn.config(state=tk.NORMAL)
        
        # Disable stop button
        self.stop_test_button.config(state=tk.DISABLED)
    
    def _show_test_error(self, error_msg, test_name):
        """Show error when test execution fails."""
        self.test_output.config(state=tk.NORMAL)
        self.test_output.insert(tk.END, f"\n❌ Error running {test_name}:\n", "fail")
        self.test_output.insert(tk.END, f"{error_msg}\n", "fail")
        self.test_output.config(state=tk.DISABLED)
        self.test_output.see(tk.END)
        
        self.test_status_label.config(text=f"❌ Error", fg=self.error_color)
        self.update_status(f"Error running {test_name}", "error")
        
        # Re-enable all test buttons
        for btn in self.test_buttons:
            btn.config(state=tk.NORMAL)
        
        # Disable stop button
        self.stop_test_button.config(state=tk.DISABLED)
    
    def stop_running_test(self):
        """Stop the currently running test process."""
        # Get process reference thread-safely
        with self.test_process_lock:
            process = self.current_test_process
            
        if process:
            try:
                # Robust shutdown: try terminate first, then kill if needed
                process.terminate()
                
                # Wait briefly for graceful termination
                try:
                    process.wait(timeout=TEST_STOP_TIMEOUT)
                except subprocess.TimeoutExpired:
                    # Force kill if terminate didn't work
                    process.kill()
                    process.wait()
                
                self.test_output.config(state=tk.NORMAL)
                self.test_output.insert(tk.END, "\n⏹ Test execution stopped by user\n", "warning")
                self.test_output.config(state=tk.DISABLED)
                self.test_output.see(tk.END)
                
                self.test_status_label.config(text="⏹ Stopped", fg=self.warning_color)
                self.update_status("Test execution stopped", "warning")
                
                # Re-enable all test buttons
                for btn in self.test_buttons:
                    btn.config(state=tk.NORMAL)
                
                self.stop_test_button.config(state=tk.DISABLED)
                
                # Clear process reference thread-safely
                with self.test_process_lock:
                    self.current_test_process = None
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to stop test: {e}")
    
    def clear_test_output(self):
        """Clear the test output display."""
        self.test_output.config(state=tk.NORMAL)
        self.test_output.delete(1.0, tk.END)
        self.test_output.insert(tk.END, "🧪 Test Suite Runner\n\n", "header")
        self.test_output.insert(tk.END, "Select a test category above to run tests.\n", "info")
        self.test_output.insert(tk.END, "Test results will appear here.\n", "info")
        self.test_output.config(state=tk.DISABLED)
        self.test_status_label.config(text="Ready", fg=self.fg_muted)
    
    def draw_connection_diagram(self):
        """Draw the connection diagram showing VSCode, IPC, and Director."""
        # Clear canvas
        self.landing_canvas.delete("all")
        
        # Get canvas dimensions
        width = self.landing_canvas.winfo_width()
        height = self.landing_canvas.winfo_height()
        
        # Use default dimensions if canvas not yet rendered
        if width <= 1:
            width = 700
        if height <= 1:
            height = 300
        
        # Calculate positions for three components in a row
        spacing = width / 4
        y_center = height / 2
        
        # Component positions
        vscode_x = spacing
        ipc_x = spacing * 2
        director_x = spacing * 3
        
        # Use constants for component dimensions
        box_width = DIAGRAM_BOX_WIDTH
        box_height = DIAGRAM_BOX_HEIGHT
        
        # Draw connection lines first (so they appear behind boxes)
        # VSCode to IPC
        self.landing_components['line_vscode_ipc'] = self.landing_canvas.create_line(
            vscode_x + box_width/2, y_center,
            ipc_x - box_width/2, y_center,
            fill=self.fg_muted, width=2, dash=(5, 5)
        )
        
        # IPC to Director
        self.landing_components['line_ipc_director'] = self.landing_canvas.create_line(
            ipc_x + box_width/2, y_center,
            director_x - box_width/2, y_center,
            fill=self.fg_muted, width=2, dash=(5, 5)
        )
        
        # Draw VSCode component
        self.landing_canvas.create_rectangle(
            vscode_x - box_width/2, y_center - box_height/2,
            vscode_x + box_width/2, y_center + box_height/2,
            fill=self.bg_secondary, outline=self.border_color, width=2
        )
        self.landing_canvas.create_text(
            vscode_x, y_center - 15,
            text="🔌", font=("Segoe UI", 24), fill=self.fg_color
        )
        self.landing_canvas.create_text(
            vscode_x, y_center + 15,
            text="VSCode", font=("Segoe UI", 10, "bold"), fill=self.fg_color
        )
        self.landing_components['vscode_status'] = self.landing_canvas.create_oval(
            vscode_x - DIAGRAM_STATUS_RADIUS, y_center + DIAGRAM_STATUS_Y_OFFSET,
            vscode_x + DIAGRAM_STATUS_RADIUS, y_center + DIAGRAM_STATUS_Y_OFFSET + (DIAGRAM_STATUS_RADIUS * 2),
            fill=self.fg_muted, outline=""
        )
        
        # Draw IPC Server component
        self.landing_canvas.create_rectangle(
            ipc_x - box_width/2, y_center - box_height/2,
            ipc_x + box_width/2, y_center + box_height/2,
            fill=self.bg_secondary, outline=self.border_color, width=2
        )
        self.landing_canvas.create_text(
            ipc_x, y_center - 15,
            text="🔗", font=("Segoe UI", 24), fill=self.fg_color
        )
        self.landing_canvas.create_text(
            ipc_x, y_center + 15,
            text="IPC Server", font=("Segoe UI", 10, "bold"), fill=self.fg_color
        )
        self.landing_components['ipc_status'] = self.landing_canvas.create_oval(
            ipc_x - DIAGRAM_STATUS_RADIUS, y_center + DIAGRAM_STATUS_Y_OFFSET,
            ipc_x + DIAGRAM_STATUS_RADIUS, y_center + DIAGRAM_STATUS_Y_OFFSET + (DIAGRAM_STATUS_RADIUS * 2),
            fill=self.fg_muted, outline=""
        )
        
        # Draw Director component
        self.landing_canvas.create_rectangle(
            director_x - box_width/2, y_center - box_height/2,
            director_x + box_width/2, y_center + box_height/2,
            fill=self.bg_secondary, outline=self.border_color, width=2
        )
        self.landing_canvas.create_text(
            director_x, y_center - 15,
            text="⚡", font=("Segoe UI", 24), fill=self.fg_color
        )
        self.landing_canvas.create_text(
            director_x, y_center + 15,
            text="Director", font=("Segoe UI", 10, "bold"), fill=self.fg_color
        )
        self.landing_components['director_status'] = self.landing_canvas.create_oval(
            director_x - DIAGRAM_STATUS_RADIUS, y_center + DIAGRAM_STATUS_Y_OFFSET,
            director_x + DIAGRAM_STATUS_RADIUS, y_center + DIAGRAM_STATUS_Y_OFFSET + (DIAGRAM_STATUS_RADIUS * 2),
            fill=self.success_color, outline=""
        )
    
    def refresh_landing_status(self):
        """Refresh the status of all components on the landing page."""
        # Check VSCode connection
        vscode_connected = self.check_vscode_connection()
        
        # Check IPC server
        ipc_running = self.check_ipc_server()
        
        # Director is always running (this GUI is the director)
        director_running = True
        
        # Update status indicators
        if 'vscode_status' in self.landing_components:
            color = self.success_color if vscode_connected else self.error_color
            self.landing_canvas.itemconfig(self.landing_components['vscode_status'], fill=color)
        
        if 'ipc_status' in self.landing_components:
            color = self.success_color if ipc_running else self.error_color
            self.landing_canvas.itemconfig(self.landing_components['ipc_status'], fill=color)
        
        if 'director_status' in self.landing_components:
            color = self.success_color if director_running else self.error_color
            self.landing_canvas.itemconfig(self.landing_components['director_status'], fill=color)
        
        # Update connection lines
        if 'line_vscode_ipc' in self.landing_components:
            line_color = self.success_color if (vscode_connected and ipc_running) else self.fg_muted
            self.landing_canvas.itemconfig(self.landing_components['line_vscode_ipc'], 
                                          fill=line_color, dash=(5, 5) if not (vscode_connected and ipc_running) else ())
        
        if 'line_ipc_director' in self.landing_components:
            line_color = self.success_color if (ipc_running and director_running) else self.fg_muted
            self.landing_canvas.itemconfig(self.landing_components['line_ipc_director'], 
                                          fill=line_color, dash=(5, 5) if not (ipc_running and director_running) else ())
        
        # Log status updates
        status_msg = f"Status check: VSCode={'✓' if vscode_connected else '✗'}, IPC={'✓' if ipc_running else '✗'}, Director={'✓' if director_running else '✗'}"
        self.log_to_landing(status_msg, "success" if (vscode_connected and ipc_running and director_running) else "warning")
    
    def check_vscode_connection(self):
        """Check if VSCode extension is connected.
        
        Returns:
            bool: True if VSCode extension is connected, False otherwise
        
        TODO: Implement actual VSCode connection check. Possible approaches:
            1. Check for active WebSocket connection on VSCode extension port
            2. Query a status file/endpoint created by the extension
            3. Use IPC message protocol to ping the extension
            4. Check process list for VSCode with extension loaded
        """
        # Placeholder implementation - always returns False
        return False
    
    def check_ipc_server(self):
        """Check if IPC server is running by attempting to connect to the IPC port.
        
        Returns:
            bool: True if IPC server is reachable, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('localhost', IPC_SERVER_PORT))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def log_to_landing(self, message, level="info"):
        """Add a message to the landing page log.
        
        Args:
            message: The message to log
            level: Log level - "info", "success", "warning", "error"
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.landing_log.config(state=tk.NORMAL)
        self.landing_log.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.landing_log.insert(tk.END, f"{message}\n", level)
        self.landing_log.see(tk.END)
        self.landing_log.config(state=tk.DISABLED)
    
    def start_landing_auto_refresh(self):
        """Start automatic refresh of landing page status.
        
        The refresh interval is controlled by LANDING_AUTO_REFRESH_INTERVAL_MS constant.
        Refreshes only occur when the landing tab is visible to conserve resources.
        """
        def auto_refresh():
            # Only refresh if the landing tab is visible
            try:
                current_tab = self.notebook.index(self.notebook.select())
                if current_tab == LANDING_TAB_INDEX:
                    self.refresh_landing_status()
            except Exception:
                # Silently ignore exceptions (e.g., if notebook/tab doesn't exist during shutdown)
                pass
            
            # Schedule next refresh using configured interval
            self.landing_refresh_id = self.root.after(LANDING_AUTO_REFRESH_INTERVAL_MS, auto_refresh)
        
        # Start the auto-refresh cycle
        self.landing_refresh_id = self.root.after(LANDING_AUTO_REFRESH_INTERVAL_MS, auto_refresh)
    
    def stop_landing_auto_refresh(self):
        """Stop automatic refresh of landing page status."""
        if hasattr(self, 'landing_refresh_id') and self.landing_refresh_id:
            self.root.after_cancel(self.landing_refresh_id)
            self.landing_refresh_id = None
    
    def on_closing(self):
        """Handle application closing - cleanup resources."""
        # Stop the auto-refresh timer
        self.stop_landing_auto_refresh()
        
        # Destroy the window
        self.root.destroy()
    
    def create_agent_dashboard_tab(self):
        """Create the Agent Dashboard tab with Phase 3 agent monitoring"""
        if not AGENT_PANEL_AVAILABLE:
            return
        
        try:
            agent_tab, self.agent_panel = create_agent_dashboard_tab(
                self.notebook,
                bg_color=self.bg_color
            )
            self.notebook.add(agent_tab, text="🤖 Agents")
            
            # Trigger initial refresh
            if hasattr(self.agent_panel, 'refresh_agents'):
                self.root.after(1000, self.agent_panel.refresh_agents)
        except Exception as e:
            self.logger.error(f"Failed to create agent dashboard tab: {e}")

def main():
    root = tk.Tk()
    app = AdastreaDirectorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
