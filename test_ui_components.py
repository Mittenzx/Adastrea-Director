#!/usr/bin/env python3
"""
Test script for new UI components.
Demonstrates the enhanced widgets in a standalone window.
"""

import sys
import tkinter as tk
from tkinter import ttk

# Import new widgets
try:
    from gui_widgets import (
        StatusBadge, CollapsibleFrame, InfoCard, ActionButton, MetricsPanel
    )
    from gui_agent_panel import create_agent_dashboard_tab
    WIDGETS_AVAILABLE = True
except ImportError as e:
    print(f"Error importing widgets: {e}")
    WIDGETS_AVAILABLE = False
    sys.exit(1)


class UITestWindow:
    """Test window for new UI components"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Adastrea Director - UI Component Test")
        self.root.geometry("1200x800")
        self.root.configure(bg="#20232b")
        
        # Create notebook for different component demos
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Style the notebook
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background="#2d2d30", borderwidth=0)
        style.configure('TNotebook.Tab',
                       background="#343843",
                       foreground="#e3e4e8",
                       padding=[20, 10],
                       font=("Segoe UI", 10))
        style.map('TNotebook.Tab',
                 background=[('selected', "#2d2d30")],
                 foreground=[('selected', "#40a9ff")])
        
        # Create test tabs
        self.create_badges_tab()
        self.create_cards_tab()
        self.create_buttons_tab()
        self.create_collapsible_tab()
        self.create_metrics_tab()
        self.create_agent_tab()
    
    def create_badges_tab(self):
        """Test StatusBadge widgets"""
        tab = tk.Frame(self.notebook, bg="#20232b")
        self.notebook.add(tab, text="Status Badges")
        
        content = tk.Frame(tab, bg="#20232b", padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            content,
            text="Status Badge Examples",
            font=("Segoe UI", 16, "bold"),
            bg="#20232b",
            fg="#e3e4e8"
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Badge container
        badge_frame = tk.Frame(content, bg="#20232b")
        badge_frame.pack(anchor=tk.W, pady=10)
        
        badges = [
            ("Connected", "success"),
            ("Processing", "info"),
            ("Warning", "warning"),
            ("Error", "error"),
            ("Unknown", "neutral")
        ]
        
        for text, status in badges:
            badge = StatusBadge(badge_frame, text=text, status=status, bg="#20232b")
            badge.pack(side=tk.LEFT, padx=5)
    
    def create_cards_tab(self):
        """Test InfoCard widgets"""
        tab = tk.Frame(self.notebook, bg="#20232b")
        self.notebook.add(tab, text="Info Cards")
        
        content = tk.Frame(tab, bg="#20232b", padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            content,
            text="Info Card Examples",
            font=("Segoe UI", 16, "bold"),
            bg="#20232b",
            fg="#e3e4e8"
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Card grid
        card_grid = tk.Frame(content, bg="#20232b")
        card_grid.pack(fill=tk.X)
        
        cards = [
            {"title": "Active Agents", "value": "3/3", "icon": "🤖"},
            {"title": "FPS", "value": "60", "icon": "⚡"},
            {"title": "Memory", "value": "4.2 GB", "icon": "💾"},
            {"title": "CPU Usage", "value": "45%", "icon": "🔥"},
        ]
        
        for idx, card_data in enumerate(cards):
            card = InfoCard(
                card_grid,
                title=card_data["title"],
                value=card_data["value"],
                icon=card_data["icon"],
                bg_color="#2d2d30",
                border_color="#3e3e42"
            )
            card.grid(row=0, column=idx, padx=5, pady=5, sticky=tk.NSEW)
            card_grid.columnconfigure(idx, weight=1)
    
    def create_buttons_tab(self):
        """Test ActionButton widgets"""
        tab = tk.Frame(self.notebook, bg="#20232b")
        self.notebook.add(tab, text="Action Buttons")
        
        content = tk.Frame(tab, bg="#20232b", padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            content,
            text="Action Button Examples",
            font=("Segoe UI", 16, "bold"),
            bg="#20232b",
            fg="#e3e4e8"
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Button grid
        button_frame = tk.Frame(content, bg="#20232b")
        button_frame.pack(anchor=tk.W, pady=10)
        
        buttons = [
            ("Primary", "🚀", "primary"),
            ("Secondary", "📁", "secondary"),
            ("Success", "✅", "success"),
            ("Danger", "❌", "danger"),
        ]
        
        for text, icon, style in buttons:
            btn = ActionButton(
                button_frame,
                text=text,
                icon=icon,
                style=style,
                command=lambda t=text: self.show_message(f"{t} clicked!")
            )
            btn.pack(side=tk.LEFT, padx=5)
    
    def create_collapsible_tab(self):
        """Test CollapsibleFrame widgets"""
        tab = tk.Frame(self.notebook, bg="#20232b")
        self.notebook.add(tab, text="Collapsible Sections")
        
        content = tk.Frame(tab, bg="#20232b", padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            content,
            text="Collapsible Frame Examples",
            font=("Segoe UI", 16, "bold"),
            bg="#20232b",
            fg="#e3e4e8"
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Create collapsible sections
        for i in range(3):
            section = CollapsibleFrame(
                content,
                title=f"Section {i + 1}: Example Content",
                bg_color="#2d2d30"
            )
            section.pack(fill=tk.X, pady=5)
            
            # Add content
            inner_content = tk.Label(
                section.content,
                text=f"This is the content for section {i + 1}.\nClick the header to collapse/expand.",
                bg="#2d2d30",
                fg="#e3e4e8",
                justify=tk.LEFT,
                padx=20,
                pady=15
            )
            inner_content.pack(fill=tk.X)
    
    def create_metrics_tab(self):
        """Test MetricsPanel widget"""
        tab = tk.Frame(self.notebook, bg="#20232b")
        self.notebook.add(tab, text="Metrics Panel")
        
        content = tk.Frame(tab, bg="#20232b", padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            content,
            text="Metrics Panel Example",
            font=("Segoe UI", 16, "bold"),
            bg="#20232b",
            fg="#e3e4e8"
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Metrics panel
        metrics = [
            {"key": "fps", "title": "FPS", "value": "60", "icon": "⚡"},
            {"key": "memory", "title": "Memory", "value": "4.2 GB", "icon": "💾"},
            {"key": "cpu", "title": "CPU", "value": "45%", "icon": "🔥"},
            {"key": "gpu", "title": "GPU", "value": "62%", "icon": "🎮"},
            {"key": "agents", "title": "Active Agents", "value": "3/3", "icon": "🤖"},
            {"key": "alerts", "title": "Alerts", "value": "2", "icon": "⚠️"},
        ]
        
        panel = MetricsPanel(content, metrics=metrics, bg_color="#20232b")
        panel.pack(fill=tk.X)
        
        # Update button
        update_btn = ActionButton(
            content,
            text="Simulate Update",
            icon="🔄",
            style="primary",
            command=lambda: self.update_metrics(panel)
        )
        update_btn.pack(pady=20)
    
    def create_agent_tab(self):
        """Test AgentMonitorPanel widget"""
        tab = tk.Frame(self.notebook, bg="#20232b")
        self.notebook.add(tab, text="Agent Monitor")
        
        # Use the complete dashboard factory
        agent_content, self.agent_panel = create_agent_dashboard_tab(
            tab,
            bg_color="#20232b"
        )
        agent_content.pack(fill=tk.BOTH, expand=True)
        
        # Trigger initial refresh
        self.root.after(500, self.agent_panel.refresh_agents)
    
    def show_message(self, message):
        """Show a simple message"""
        print(f"[UI Test] {message}")
    
    def update_metrics(self, panel):
        """Simulate metric updates"""
        import random
        
        updates = {
            "fps": str(random.randint(55, 60)),
            "memory": f"{random.uniform(4.0, 4.5):.1f} GB",
            "cpu": f"{random.randint(40, 50)}%",
            "gpu": f"{random.randint(55, 70)}%",
            "agents": f"{random.randint(2, 3)}/3",
            "alerts": str(random.randint(0, 5)),
        }
        
        for key, value in updates.items():
            panel.update_metric(key, value)
        
        print("[UI Test] Metrics updated!")


def main():
    """Run the UI component test"""
    if not WIDGETS_AVAILABLE:
        print("Error: UI widgets not available")
        return 1
    
    print("=" * 60)
    print("Adastrea Director - UI Component Test")
    print("=" * 60)
    print("\nTesting new UI components...")
    print("- Status Badges")
    print("- Info Cards")
    print("- Action Buttons")
    print("- Collapsible Frames")
    print("- Metrics Panel")
    print("- Agent Monitor Panel")
    print("\nClose the window to exit.")
    print("=" * 60)
    
    root = tk.Tk()
    _app = UITestWindow(root)
    root.mainloop()
    
    print("\n✅ UI component test completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
