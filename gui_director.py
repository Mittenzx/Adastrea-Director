import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, Menu, font
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

        # --- Header Frame with UE5-style border separator ---
        header_frame = tk.Frame(main_frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 8))
        
        title_label = tk.Label(
            header_frame,
            text="🤖 Adastrea Director",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(
            header_frame,
            text="AI Game Development Assistant",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg=self.fg_color
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # UE5-style separator line below header (7px bottom padding maintains original 15px total)
        header_separator = tk.Frame(main_frame, height=1, bg=self.accent_color)
        header_separator.pack(fill=tk.X, pady=(0, 7))

        # --- Top Frame for Buttons ---
        top_frame = tk.Frame(main_frame, bg=self.bg_color)
        top_frame.pack(fill=tk.X, pady=(0, 15))

        button_style = {
            "font": ("Segoe UI", 10),
            "bg": self.button_bg,
            "fg": self.fg_color,
            "activebackground": self.button_active,
            "activeforeground": self.fg_color,
            "relief": tk.FLAT,
            "padx": 18,  # Slightly more padding for UE5 style
            "pady": 9,   # Slightly more vertical padding
            "cursor": "hand2",
            "borderwidth": 1,
            "highlightthickness": 1,
            "highlightbackground": self.button_bg,
            "highlightcolor": self.accent_color
        }

        self.ingest_button = tk.Button(
            top_frame,
            text="📚 Update Knowledge Base",
            command=self.run_ingestion,
            **button_style
        )
        self.ingest_button.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(self.ingest_button, "Load and process project documents (Ctrl+U)")

        self.api_key_button = tk.Button(
            top_frame,
            text="🔑 Set API Key",
            command=self.set_api_key,
            **button_style
        )
        self.api_key_button.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(self.api_key_button, "Configure your OpenAI API key (Ctrl+K)")

        self.clear_button = tk.Button(
            top_frame,
            text="🗑️ Clear",
            command=self.clear_conversation,
            **button_style
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(self.clear_button, "Clear conversation history (Ctrl+L)")
        
        self.copy_button = tk.Button(
            top_frame,
            text="📋 Copy",
            command=self.copy_response,
            **button_style
        )
        self.copy_button.pack(side=tk.LEFT)
        self.create_tooltip(self.copy_button, "Copy last response to clipboard (Ctrl+C)")

        # Font size controls
        font_frame = tk.Frame(top_frame, bg=self.bg_color)
        font_frame.pack(side=tk.RIGHT)
        
        tk.Label(font_frame, text="Font:", bg=self.bg_color, fg=self.fg_color, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        small_button_style = {
            "font": ("Segoe UI", 9),
            "bg": self.button_bg,
            "fg": self.fg_color,
            "activebackground": self.button_active,
            "activeforeground": self.fg_color,
            "relief": tk.FLAT,
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
        self.decrease_font_button.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(self.decrease_font_button, "Decrease font size (min 8pt)")
        
        self.increase_font_button = tk.Button(
            font_frame,
            text="A+",
            command=self.increase_font,
            **small_button_style
        )
        self.increase_font_button.pack(side=tk.LEFT)
        self.create_tooltip(self.increase_font_button, "Increase font size (max 20pt)")

        # --- Response Display Area with UE5-style border ---
        response_frame = tk.Frame(main_frame, bg=self.bg_color)
        response_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        response_header = tk.Frame(response_frame, bg=self.bg_color)
        response_header.pack(fill=tk.X, pady=(0, 5))
        
        response_label = tk.Label(
            response_header,
            text="💬 Conversation",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        response_label.pack(side=tk.LEFT)
        
        self.current_font_size = 10
        self.response_font = font.Font(family="Consolas", size=self.current_font_size)
        
        # Container frame with UE5-style border for visual depth
        text_container = tk.Frame(response_frame, bg=self.button_bg, padx=1, pady=1)
        text_container.pack(fill=tk.BOTH, expand=True)
        
        self.response_text = scrolledtext.ScrolledText(
            text_container,
            wrap=tk.WORD,
            height=20,
            state=tk.DISABLED,
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            font=self.response_font,
            relief=tk.FLAT,
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

        # --- Query Input Area with UE5-style separator ---
        # Add separator line above input area
        input_separator = tk.Frame(main_frame, height=1, bg=self.button_bg)
        input_separator.pack(fill=tk.X, pady=(0, 15))
        
        query_frame = tk.Frame(main_frame, bg=self.bg_color)
        query_frame.pack(fill=tk.X, pady=(0, 0))
        
        # Increased bottom padding from 5px to 8px for UE5-style spacing and improved visual alignment
        query_header = tk.Frame(query_frame, bg=self.bg_color)
        query_header.pack(fill=tk.X, pady=(0, 8))
        
        query_label = tk.Label(
            query_header,
            text="❓ Your Question:",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        query_label.pack(side=tk.LEFT)
        
        # Input frame with button
        input_frame = tk.Frame(query_frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X)
        
        # Container with border for input field (UE5 style)
        entry_container = tk.Frame(input_frame, bg=self.button_bg, padx=1, pady=1)
        entry_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.query_entry = tk.Entry(
            entry_container,
            font=("Segoe UI", 11),
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.button_bg,
            highlightcolor=self.accent_color,
            borderwidth=0
        )
        self.query_entry.pack(fill=tk.BOTH, expand=True, ipady=8, ipadx=10)
        self.query_entry.bind("<Return>", self.run_query_event)
        self.query_entry.bind("<Control-Return>", self.run_query_event)
        self.query_entry.focus()

        self.ask_button = tk.Button(
            input_frame,
            text="Ask ▶",
            command=self.run_query,
            font=("Segoe UI", 11, "bold"),
            bg=self.accent_color,
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
        
        # --- Status Bar ---
        self.status_var = tk.StringVar()
        self.status_var.set("✓ Ready. Please set your OpenAI API Key if you haven't.")
        status_bar = tk.Label(
            root,
            textvariable=self.status_var,
            bd=1,
            relief=tk.FLAT,
            anchor=tk.W,
            bg=self.button_bg,
            fg=self.fg_color,
            font=("Segoe UI", 9),
            padx=10,
            pady=5
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Show welcome message
        self.show_welcome_message()

        self.check_api_key_on_startup()

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
                self.status_var.set("✓ API Key set successfully. Ready to ingest or query.")
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
        self.status_var.set("✓ Conversation cleared.")
        self.show_welcome_message()
    
    def copy_response(self):
        """Copy the last response to clipboard."""
        try:
            if self.conversation_history:
                last_response = self.conversation_history[-1]
                if last_response['role'] == 'assistant':
                    self.root.clipboard_clear()
                    self.root.clipboard_append(last_response['content'])
                    self.status_var.set("✓ Response copied to clipboard.")
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
                self.status_var.set(f"✓ Conversation exported to {filename}")
                messagebox.showinfo("Success", f"Conversation exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def increase_font(self):
        """Increase font size."""
        if self.current_font_size < 20:
            self.current_font_size += 1
            self.response_font.configure(size=self.current_font_size)
            self.response_text.tag_config("user", font=("Segoe UI", self.current_font_size, "bold"))
            self.status_var.set(f"Font size: {self.current_font_size}")
    
    def decrease_font(self):
        """Decrease font size."""
        if self.current_font_size > 8:
            self.current_font_size -= 1
            self.response_font.configure(size=self.current_font_size)
            self.response_text.tag_config("user", font=("Segoe UI", self.current_font_size, "bold"))
            self.status_var.set(f"Font size: {self.current_font_size}")
    
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
        self.status_var.set(status_message)
        
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
            self.status_var.set("✓ Ready.")
        else:
            # Add error to conversation
            error_message = f"Error occurred:\n{output}"
            self.response_text.config(state=tk.NORMAL)
            self.response_text.insert(tk.END, "❌ ", "error")
            self.response_text.insert(tk.END, error_message + "\n\n", "error")
            self.response_text.see(tk.END)
            self.response_text.config(state=tk.DISABLED)
            self.status_var.set("❌ An error occurred. Check the response window for details.")
            
        self.ingest_button.config(state=tk.NORMAL)
        self.ask_button.config(state=tk.NORMAL)
        self.query_entry.focus()

def main():
    root = tk.Tk()
    app = AdastreaDirectorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
