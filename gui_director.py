import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu, font, filedialog, ttk
import subprocess
import threading
import sys
import os
import json
import tempfile
from datetime import datetime
from pathlib import Path

# Disable ChromaDB telemetry BEFORE any imports that might import chromadb
# This prevents "capture() takes 1 positional argument but 3 were given" errors
os.environ["ANONYMIZED_TELEMETRY"] = "False"

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
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Show welcome message
        self.show_welcome_message()

        self.check_api_key_on_startup()
    
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
        
        # Main content area with two sections
        content_frame = tk.Frame(ingest_tab, bg=self.bg_tertiary)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # --- Ingested Documents Section ---
        ingested_frame = tk.Frame(content_frame, bg=self.bg_tertiary)
        ingested_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
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
        self.ingested_text.pack(fill=tk.BOTH, expand=True)
        
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
        
        # Initial load of ingest list
        self.refresh_ingest_list()

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
                
                # Update UI on main thread
                self.root.after(0, self._update_ingest_list_ui, ingested_docs)
            except Exception as e:
                self.root.after(0, self._show_ingest_error, str(e))
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=refresh_in_thread)
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
            from langchain_community.vectorstores import Chroma
            
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
        self.root.bind("<Control-u>", lambda e: self.ingest_folder())
        self.root.bind("<Control-U>", lambda e: self.ingest_folder())
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
        
        def on_ok():
            key = key_entry.get()
            if key:
                os.environ['GEMINI_KEY'] = key
                os.environ['GOOGLE_API_KEY'] = key  # Also set for compatibility
                self.update_status("API Key set successfully • Ready to ingest or query", "success")
                self.add_to_conversation("System", "Gemini API Key configured successfully.", is_system=True)
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
        # Check for Gemini API key (primary) or Google API key (compatibility)
        if not (os.getenv("GEMINI_KEY") or os.getenv("GOOGLE_API_KEY")):
            self.root.after(500, self.set_api_key)

    def ingest_folder(self):
        """Opens a folder selection dialog and ingests documents from the selected folder."""
        folder_path = filedialog.askdirectory(
            title="Select Folder to Ingest",
            initialdir=SCRIPT_DIR
        )
        
        if folder_path:
            self.add_to_conversation("System", f"Ingesting documents from: {folder_path}", is_system=True)
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
            
            self.update_progress(percent, label, details)
            
            # Continue polling if not complete
            if percent < 100:
                self.progress_poll_id = self.root.after(100, self.poll_progress_file)
        except FileNotFoundError:
            # File is gone, stop polling
            self.hide_progress_bar()
        except json.JSONDecodeError:
            # File might be being written, try again
            self.progress_poll_id = self.root.after(100, self.poll_progress_file)
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
            # Start polling the progress file
            self.progress_poll_id = self.root.after(500, self.poll_progress_file)

        thread = threading.Thread(target=self._execute_command, args=(command, show_progress))
        thread.start()

    def _execute_command(self, command, show_progress=False):
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
            self.root.after(0, self._update_ui_after_execution, output, process.returncode, show_progress)

        except Exception as e:
            self.root.after(0, self._update_ui_after_execution, str(e), 1, show_progress)

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
            # Refresh ingest list after successful ingestion
            if show_progress:
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
            
        self.ingest_folder_button.config(state=tk.NORMAL)
        self.ingest_file_button.config(state=tk.NORMAL)
        self.ingest_repo_button.config(state=tk.NORMAL)
        self.ask_button.config(state=tk.NORMAL)
        self.query_entry.focus()

def main():
    root = tk.Tk()
    app = AdastreaDirectorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
