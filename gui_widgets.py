"""
Enhanced UI widgets for Adastrea Director GUI.
Provides reusable, modern components for better UX.
"""

import tkinter as tk
from tkinter import ttk
from gui_colors import (
    STATUS_SUCCESS, STATUS_ERROR, STATUS_WARNING, STATUS_INFO, STATUS_NEUTRAL,
    BUTTON_PRIMARY_BG, BUTTON_PRIMARY_FG, BUTTON_PRIMARY_HOVER,
    BUTTON_SECONDARY_BG, BUTTON_SECONDARY_FG, BUTTON_SECONDARY_HOVER,
    BUTTON_SUCCESS_BG, BUTTON_SUCCESS_FG, BUTTON_SUCCESS_HOVER,
    BUTTON_DANGER_BG, BUTTON_DANGER_FG, BUTTON_DANGER_HOVER,
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, FG_PRIMARY,
    FONT_FAMILY, ACCENT_BLUE
)


# Color scheme mappings for StatusBadge
STATUS_BADGE_COLORS = {
    "success": {"bg": STATUS_SUCCESS, "fg": "#1e1e1e"},
    "error": {"bg": STATUS_ERROR, "fg": "#1e1e1e"},
    "warning": {"bg": STATUS_WARNING, "fg": "#1e1e1e"},
    "info": {"bg": STATUS_INFO, "fg": "#1e1e1e"},
    "neutral": {"bg": STATUS_NEUTRAL, "fg": "#ffffff"}
}

# Button style configurations
BUTTON_STYLES = {
    "primary": {
        "bg": BUTTON_PRIMARY_BG,
        "fg": BUTTON_PRIMARY_FG,
        "hover": BUTTON_PRIMARY_HOVER
    },
    "secondary": {
        "bg": BUTTON_SECONDARY_BG,
        "fg": BUTTON_SECONDARY_FG,
        "hover": BUTTON_SECONDARY_HOVER
    },
    "success": {
        "bg": BUTTON_SUCCESS_BG,
        "fg": BUTTON_SUCCESS_FG,
        "hover": BUTTON_SUCCESS_HOVER
    },
    "danger": {
        "bg": BUTTON_DANGER_BG,
        "fg": BUTTON_DANGER_FG,
        "hover": BUTTON_DANGER_HOVER
    }
}

# Global flag to track if ttk styles have been configured
_TTK_STYLES_CONFIGURED = False


class StatusBadge(tk.Frame):
    """A modern status badge with icon and text"""
    
    def __init__(self, parent, text="", status="neutral", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.status = status
        self.text_var = tk.StringVar(value=text)
        
        # Configure frame
        color_scheme = STATUS_BADGE_COLORS.get(status, STATUS_BADGE_COLORS["neutral"])
        self.configure(bg=color_scheme["bg"], padx=8, pady=4, relief=tk.FLAT)
        
        # Label
        self.label = tk.Label(
            self,
            textvariable=self.text_var,
            font=(FONT_FAMILY, 9, "bold"),
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
            color_scheme = STATUS_BADGE_COLORS.get(status, STATUS_BADGE_COLORS["neutral"])
            self.configure(bg=color_scheme["bg"])
            self.label.configure(bg=color_scheme["bg"], fg=color_scheme["fg"])


class CollapsibleFrame(tk.Frame):
    """A collapsible section with header"""
    
    def __init__(self, parent, title="Section", bg_color=BG_TERTIARY, **kwargs):
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
            font=(FONT_FAMILY, 10),
            bg=bg_color,
            fg=ACCENT_BLUE,
            cursor="hand2"
        )
        self.toggle_icon.pack(side=tk.LEFT, padx=(5, 10))
        
        # Title
        self.title_label = tk.Label(
            self.header,
            text=title,
            font=(FONT_FAMILY, 11, "bold"),
            bg=bg_color,
            fg=FG_PRIMARY,
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
    
    def __init__(self, parent, title="", value="", icon="📊", bg_color=BG_TERTIARY, border_color="#3e3e42", **kwargs):
        super().__init__(parent, bg=bg_color, highlightthickness=2, highlightbackground=border_color, **kwargs)
        
        # Inner padding frame
        inner = tk.Frame(self, bg=bg_color, padx=15, pady=12)
        inner.pack(fill=tk.BOTH, expand=True)
        
        # Icon
        icon_label = tk.Label(
            inner,
            text=icon,
            font=(FONT_FAMILY, 20),
            bg=bg_color,
            fg=FG_PRIMARY
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Text container
        text_frame = tk.Frame(inner, bg=bg_color)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Title
        self.title_label = tk.Label(
            text_frame,
            text=title,
            font=(FONT_FAMILY, 9),
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
            font=(FONT_FAMILY, 14, "bold"),
            bg=bg_color,
            fg=FG_PRIMARY,
            anchor=tk.W
        )
        self.value_label.pack(fill=tk.X)
    
    def update_value(self, value):
        """Update the card value"""
        self.value_var.set(value)


class ActionButton(tk.Button):
    """Enhanced button with hover effects"""
    
    def __init__(self, parent, text="", icon="", command=None, style="primary", **kwargs):
        style_config = BUTTON_STYLES.get(style, BUTTON_STYLES["secondary"])
        
        # Button text with icon
        button_text = f"{icon} {text}" if icon else text
        
        super().__init__(
            parent,
            text=button_text,
            command=command,
            font=(FONT_FAMILY, 10),
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


def _configure_ttk_styles():
    """Configure ttk styles once for all widgets"""
    global _TTK_STYLES_CONFIGURED
    if not _TTK_STYLES_CONFIGURED:
        style = ttk.Style()
        style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor=BG_SECONDARY,
            background=ACCENT_BLUE,
            borderwidth=0,
            thickness=20
        )
        _TTK_STYLES_CONFIGURED = True


class ProgressIndicator(tk.Frame):
    """A modern progress indicator with label"""
    
    def __init__(self, parent, label="Processing...", bg_color=BG_TERTIARY, **kwargs):
        super().__init__(parent, bg=bg_color, **kwargs)
        
        self.bg_color = bg_color
        self.label_var = tk.StringVar(value=label)
        
        # Label
        self.label = tk.Label(
            self,
            textvariable=self.label_var,
            font=(FONT_FAMILY, 10),
            bg=bg_color,
            fg=FG_PRIMARY,
            anchor=tk.W
        )
        self.label.pack(fill=tk.X, pady=(0, 8))
        
        # Configure ttk styles once
        _configure_ttk_styles()
        
        # Progress bar
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
            font=(FONT_FAMILY, 9),
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
    
    def __init__(self, parent, metrics=None, bg_color=BG_PRIMARY, **kwargs):
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
                bg_color=BG_TERTIARY,
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
    
    def __init__(self, parent, tabs=None, on_select=None, bg_color=BG_PRIMARY, **kwargs):
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
                font=(FONT_FAMILY, 10, "bold"),
                bg=BUTTON_SECONDARY_BG,
                fg=BUTTON_SECONDARY_FG,
                activebackground=BUTTON_SECONDARY_HOVER,
                activeforeground=BUTTON_SECONDARY_FG,
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
                    btn.configure(bg=BUTTON_PRIMARY_BG, fg=BUTTON_PRIMARY_FG)
                else:
                    btn.configure(bg=BUTTON_SECONDARY_BG, fg=BUTTON_SECONDARY_FG)
            
            self.current_tab = index
            
            # Call callback
            if self.on_select:
                self.on_select(index)
