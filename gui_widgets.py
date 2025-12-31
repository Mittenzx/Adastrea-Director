"""
Enhanced UI widgets for Adastrea Director GUI.
Provides reusable, modern components for better UX.
"""

import tkinter as tk
from tkinter import ttk


class StatusBadge(tk.Frame):
    """A modern status badge with icon and text"""
    
    def __init__(self, parent, text="", status="neutral", **kwargs):
        super().__init__(parent, **kwargs)
        
        # Color scheme
        self.colors = {
            "success": {"bg": "#4ec9b0", "fg": "#1e1e1e"},
            "error": {"bg": "#f48771", "fg": "#1e1e1e"},
            "warning": {"bg": "#ce9178", "fg": "#1e1e1e"},
            "info": {"bg": "#40a9ff", "fg": "#1e1e1e"},
            "neutral": {"bg": "#858585", "fg": "#ffffff"}
        }
        
        self.status = status
        self.text_var = tk.StringVar(value=text)
        
        # Configure frame
        color_scheme = self.colors.get(status, self.colors["neutral"])
        self.configure(bg=color_scheme["bg"], padx=8, pady=4, relief=tk.FLAT)
        
        # Label
        self.label = tk.Label(
            self,
            textvariable=self.text_var,
            font=("Segoe UI", 9, "bold"),
            bg=color_scheme["bg"],
            fg=color_scheme["fg"]
        )
        self.label.pack()
    
    def update_status(self, text=None, status=None):
        """Update badge text and/or status"""
        if text is not None:
            self.text_var.set(text)
        if status is not None:
            self.status = status
            color_scheme = self.colors.get(status, self.colors["neutral"])
            self.configure(bg=color_scheme["bg"])
            self.label.configure(bg=color_scheme["bg"], fg=color_scheme["fg"])


class CollapsibleFrame(tk.Frame):
    """A collapsible section with header"""
    
    def __init__(self, parent, title="Section", bg_color="#2d2d30", **kwargs):
        super().__init__(parent, bg=bg_color, **kwargs)
        
        self.is_expanded = True
        self.bg_color = bg_color
        
        # Header frame
        self.header = tk.Frame(self, bg=bg_color, cursor="hand2")
        self.header.pack(fill=tk.X, pady=(0, 5))
        
        # Toggle indicator
        self.toggle_icon = tk.Label(
            self.header,
            text="▼",
            font=("Segoe UI", 10),
            bg=bg_color,
            fg="#40a9ff",
            cursor="hand2"
        )
        self.toggle_icon.pack(side=tk.LEFT, padx=(5, 10))
        
        # Title
        self.title_label = tk.Label(
            self.header,
            text=title,
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            fg="#e3e4e8",
            cursor="hand2"
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Content frame
        self.content = tk.Frame(self, bg=bg_color)
        self.content.pack(fill=tk.BOTH, expand=True)
        
        # Bind click events
        self.header.bind("<Button-1>", lambda e: self.toggle())
        self.toggle_icon.bind("<Button-1>", lambda e: self.toggle())
        self.title_label.bind("<Button-1>", lambda e: self.toggle())
    
    def toggle(self):
        """Toggle expanded/collapsed state"""
        if self.is_expanded:
            self.content.pack_forget()
            self.toggle_icon.config(text="▶")
            self.is_expanded = False
        else:
            self.content.pack(fill=tk.BOTH, expand=True)
            self.toggle_icon.config(text="▼")
            self.is_expanded = True


class InfoCard(tk.Frame):
    """A modern card widget for displaying information"""
    
    def __init__(self, parent, title="", value="", icon="📊", bg_color="#2d2d30", border_color="#3e3e42", **kwargs):
        super().__init__(parent, bg=bg_color, highlightthickness=2, highlightbackground=border_color, **kwargs)
        
        # Inner padding frame
        inner = tk.Frame(self, bg=bg_color, padx=15, pady=12)
        inner.pack(fill=tk.BOTH, expand=True)
        
        # Icon
        icon_label = tk.Label(
            inner,
            text=icon,
            font=("Segoe UI", 20),
            bg=bg_color,
            fg="#e3e4e8"
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Text container
        text_frame = tk.Frame(inner, bg=bg_color)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Title
        self.title_label = tk.Label(
            text_frame,
            text=title,
            font=("Segoe UI", 9),
            bg=bg_color,
            fg="#858585",
            anchor=tk.W
        )
        self.title_label.pack(fill=tk.X)
        
        # Value
        self.value_var = tk.StringVar(value=value)
        self.value_label = tk.Label(
            text_frame,
            textvariable=self.value_var,
            font=("Segoe UI", 14, "bold"),
            bg=bg_color,
            fg="#e3e4e8",
            anchor=tk.W
        )
        self.value_label.pack(fill=tk.X)
    
    def update_value(self, value):
        """Update the card value"""
        self.value_var.set(value)


class ActionButton(tk.Button):
    """Enhanced button with hover effects"""
    
    def __init__(self, parent, text="", icon="", command=None, style="primary", **kwargs):
        # Color schemes
        styles = {
            "primary": {
                "bg": "#40a9ff",
                "fg": "#20232b",
                "hover": "#5bb8ff"
            },
            "secondary": {
                "bg": "#343843",
                "fg": "#e3e4e8",
                "hover": "#4a4e5a"
            },
            "success": {
                "bg": "#4ec9b0",
                "fg": "#20232b",
                "hover": "#6dd6c0"
            },
            "danger": {
                "bg": "#f48771",
                "fg": "#20232b",
                "hover": "#ff9a84"
            }
        }
        
        style_config = styles.get(style, styles["secondary"])
        
        # Button text with icon
        button_text = f"{icon} {text}" if icon else text
        
        super().__init__(
            parent,
            text=button_text,
            command=command,
            font=("Segoe UI", 10),
            bg=style_config["bg"],
            fg=style_config["fg"],
            activebackground=style_config["hover"],
            activeforeground=style_config["fg"],
            relief=tk.FLAT,
            padx=18,
            pady=9,
            cursor="hand2",
            borderwidth=0,
            **kwargs
        )
        
        # Store colors for hover effect
        self.default_bg = style_config["bg"]
        self.hover_bg = style_config["hover"]
        
        # Bind hover events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Handle mouse enter"""
        self.configure(bg=self.hover_bg)
    
    def _on_leave(self, event):
        """Handle mouse leave"""
        self.configure(bg=self.default_bg)


class ProgressIndicator(tk.Frame):
    """A modern progress indicator with label"""
    
    def __init__(self, parent, label="Processing...", bg_color="#2d2d30", **kwargs):
        super().__init__(parent, bg=bg_color, **kwargs)
        
        self.bg_color = bg_color
        self.label_var = tk.StringVar(value=label)
        
        # Label
        self.label = tk.Label(
            self,
            textvariable=self.label_var,
            font=("Segoe UI", 10),
            bg=bg_color,
            fg="#e3e4e8",
            anchor=tk.W
        )
        self.label.pack(fill=tk.X, pady=(0, 8))
        
        # Progress bar
        style = ttk.Style()
        style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor="#252526",
            background="#40a9ff",
            borderwidth=0,
            thickness=20
        )
        
        self.progress_bar = ttk.Progressbar(
            self,
            style="Modern.Horizontal.TProgressbar",
            orient=tk.HORIZONTAL,
            mode='determinate',
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Details label
        self.details_var = tk.StringVar(value="")
        self.details = tk.Label(
            self,
            textvariable=self.details_var,
            font=("Segoe UI", 9),
            bg=bg_color,
            fg="#858585",
            anchor=tk.W
        )
        self.details.pack(fill=tk.X)
    
    def update_progress(self, percent, label=None, details=None):
        """Update progress"""
        self.progress_bar['value'] = percent
        if label is not None:
            self.label_var.set(label)
        if details is not None:
            self.details_var.set(details)


class MetricsPanel(tk.Frame):
    """A panel showing multiple metric cards"""
    
    def __init__(self, parent, metrics=None, bg_color="#20232b", **kwargs):
        super().__init__(parent, bg=bg_color, **kwargs)
        
        self.bg_color = bg_color
        self.cards = {}
        
        if metrics:
            self.create_metrics(metrics)
    
    def create_metrics(self, metrics):
        """Create metric cards from a list of dicts"""
        # Calculate columns (max 4 per row)
        cols = min(len(metrics), 4)
        
        for idx, metric in enumerate(metrics):
            row = idx // cols
            col = idx % cols
            
            card = InfoCard(
                self,
                title=metric.get("title", "Metric"),
                value=metric.get("value", "0"),
                icon=metric.get("icon", "📊"),
                bg_color="#2d2d30",
                border_color="#3e3e42"
            )
            card.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            
            # Store reference
            key = metric.get("key", f"metric_{idx}")
            self.cards[key] = card
        
        # Configure grid weights
        for col in range(cols):
            self.columnconfigure(col, weight=1)
    
    def update_metric(self, key, value):
        """Update a specific metric"""
        if key in self.cards:
            self.cards[key].update_value(value)


class TabBar(tk.Frame):
    """A modern tab bar with radio-style buttons"""
    
    def __init__(self, parent, tabs=None, on_select=None, bg_color="#20232b", **kwargs):
        super().__init__(parent, bg=bg_color, **kwargs)
        
        self.bg_color = bg_color
        self.on_select = on_select
        self.current_tab = 0
        self.tab_buttons = []
        
        if tabs:
            self.create_tabs(tabs)
    
    def create_tabs(self, tabs):
        """Create tab buttons"""
        for idx, tab in enumerate(tabs):
            btn = tk.Button(
                self,
                text=tab.get("text", f"Tab {idx}"),
                font=("Segoe UI", 10, "bold"),
                bg="#343843",
                fg="#e3e4e8",
                activebackground="#4a4e5a",
                activeforeground="#e3e4e8",
                relief=tk.FLAT,
                padx=20,
                pady=10,
                cursor="hand2",
                borderwidth=0,
                command=lambda i=idx: self.select_tab(i)
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))
            self.tab_buttons.append(btn)
        
        # Select first tab
        if self.tab_buttons:
            self.select_tab(0)
    
    def select_tab(self, index):
        """Select a tab"""
        if 0 <= index < len(self.tab_buttons):
            # Update button states
            for idx, btn in enumerate(self.tab_buttons):
                if idx == index:
                    btn.configure(bg="#40a9ff", fg="#20232b")
                else:
                    btn.configure(bg="#343843", fg="#e3e4e8")
            
            self.current_tab = index
            
            # Call callback
            if self.on_select:
                self.on_select(index)
