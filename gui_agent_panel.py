"""
Agent Monitoring Panel for Adastrea Director GUI.
Provides real-time monitoring of Phase 3 autonomous agents.
"""

import tkinter as tk
from tkinter import ttk
from gui_widgets import InfoCard, StatusBadge, CollapsibleFrame
from gui_colors import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY,
    FG_PRIMARY, BORDER_COLOR, ACCENT_BLUE, FONT_FAMILY
)


class AgentMonitorPanel(tk.Frame):
    """Panel for monitoring Phase 3 agents"""
    
    def __init__(self, parent, bg_color=BG_PRIMARY, **kwargs):
        super().__init__(parent, bg=bg_color, **kwargs)
        
        self.bg_color = bg_color
        self.bg_secondary = BG_SECONDARY
        self.bg_tertiary = BG_TERTIARY
        self.fg_color = FG_PRIMARY
        self.border_color = BORDER_COLOR
        self.accent_color = ACCENT_BLUE
        
        # Agent data
        self.agents = {
            "performance": {
                "name": "Performance Profiling",
                "icon": "⚡",
                "status": "unknown",
                "metrics": {}
            },
            "bug_detection": {
                "name": "Bug Detection",
                "icon": "🐛",
                "status": "unknown",
                "metrics": {}
            },
            "code_quality": {
                "name": "Code Quality",
                "icon": "✨",
                "status": "unknown",
                "metrics": {}
            }
        }
        
        self.create_ui()
    
    def create_ui(self):
        """Create the agent monitoring UI"""
        # Header
        header_frame = tk.Frame(self, bg=self.bg_color)
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(
            header_frame,
            text="🤖 Autonomous Agents",
            font=(FONT_FAMILY, 13, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(side=tk.LEFT)
        
        # Refresh button
        self.refresh_btn = tk.Button(
            header_frame,
            text="🔄",
            command=self.refresh_agents,
            font=(FONT_FAMILY, 10),
            bg="#343843",
            fg=self.fg_color,
            activebackground="#4a4e5a",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2"
        )
        self.refresh_btn.pack(side=tk.RIGHT)
        
        # Separator
        tk.Frame(
            self,
            height=1,
            bg=self.border_color
        ).pack(fill=tk.X)
        
        # Agent sections
        self.agent_sections = {}
        
        for agent_id, agent_data in self.agents.items():
            section = self.create_agent_section(agent_id, agent_data)
            self.agent_sections[agent_id] = section
    
    def create_agent_section(self, agent_id, agent_data):
        """Create a collapsible section for an agent"""
        # Container
        container = tk.Frame(self, bg=self.bg_color)
        container.pack(fill=tk.X, padx=15, pady=10)
        
        # Use collapsible frame
        section = CollapsibleFrame(
            container,
            title=f"{agent_data['icon']} {agent_data['name']}",
            bg_color=self.bg_tertiary
        )
        section.pack(fill=tk.BOTH, expand=True)
        
        # Status row
        status_row = tk.Frame(section.content, bg=self.bg_tertiary)
        status_row.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        tk.Label(
            status_row,
            text="Status:",
            font=(FONT_FAMILY, 9, "bold"),
            bg=self.bg_tertiary,
            fg="#858585"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        status_badge = StatusBadge(
            status_row,
            text="Unknown",
            status="neutral",
            bg=self.bg_tertiary
        )
        status_badge.pack(side=tk.LEFT)
        agent_data['status_badge'] = status_badge
        
        # Metrics grid
        metrics_frame = tk.Frame(section.content, bg=self.bg_tertiary, padx=10, pady=(0, 10))
        metrics_frame.pack(fill=tk.BOTH, expand=True)
        
        # Store metrics frame reference
        agent_data['metrics_frame'] = metrics_frame
        
        return section
    
    def refresh_agents(self):
        """Refresh agent status and metrics"""
        # This would connect to the IPC server or backend to get real agent status
        # For now, we'll show placeholder data
        
        # Example: Update performance agent
        self.update_agent_status("performance", "running", {
            "FPS": "60",
            "Memory": "4.2 GB",
            "CPU": "45%",
            "GPU": "62%"
        })
        
        self.update_agent_status("bug_detection", "idle", {
            "Critical": "0",
            "High": "2",
            "Medium": "5",
            "Low": "12"
        })
        
        self.update_agent_status("code_quality", "running", {
            "Issues": "8",
            "Warnings": "23",
            "Tech Debt": "Low",
            "Score": "85/100"
        })
    
    def update_agent_status(self, agent_id, status, metrics=None):
        """Update an agent's status and metrics"""
        if agent_id not in self.agents:
            return
        
        agent_data = self.agents[agent_id]
        
        # Update status badge
        status_map = {
            "running": ("Running", "success"),
            "idle": ("Idle", "info"),
            "error": ("Error", "error"),
            "unknown": ("Unknown", "neutral")
        }
        
        status_text, status_type = status_map.get(status, ("Unknown", "neutral"))
        if 'status_badge' in agent_data:
            agent_data['status_badge'].update_status(status_text, status_type)
        
        # Update metrics
        if metrics and 'metrics_frame' in agent_data:
            # Clear existing metrics
            for widget in agent_data['metrics_frame'].winfo_children():
                widget.destroy()
            
            # Create metric grid
            row = 0
            col = 0
            max_cols = 2
            
            for key, value in metrics.items():
                metric_frame = tk.Frame(
                    agent_data['metrics_frame'],
                    bg=self.bg_secondary,
                    highlightthickness=1,
                    highlightbackground=self.border_color
                )
                metric_frame.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
                
                inner = tk.Frame(metric_frame, bg=self.bg_secondary, padx=10, pady=8)
                inner.pack(fill=tk.BOTH, expand=True)
                
                tk.Label(
                    inner,
                    text=key,
                    font=(FONT_FAMILY, 8),
                    bg=self.bg_secondary,
                    fg="#858585",
                    anchor=tk.W
                ).pack(fill=tk.X)
                
                tk.Label(
                    inner,
                    text=value,
                    font=(FONT_FAMILY, 12, "bold"),
                    bg=self.bg_secondary,
                    fg=self.fg_color,
                    anchor=tk.W
                ).pack(fill=tk.X)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            # Configure grid weights
            for c in range(max_cols):
                agent_data['metrics_frame'].columnconfigure(c, weight=1)


def create_agent_dashboard_tab(parent, bg_color="#20232b"):
    """Create a complete agent dashboard tab"""
    container = tk.Frame(parent, bg=bg_color)
    
    # Title section
    title_frame = tk.Frame(container, bg=bg_color, padx=15, pady=15)
    title_frame.pack(fill=tk.X)
    
    tk.Label(
        title_frame,
        text="📊 Agent Dashboard",
        font=(FONT_FAMILY, 16, "bold"),
        bg=bg_color,
        fg="#e3e4e8"
    ).pack(side=tk.LEFT)
    
    # Subtitle
    tk.Label(
        title_frame,
        text="Monitor Phase 3 autonomous agents in real-time",
        font=(FONT_FAMILY, 10),
        bg=bg_color,
        fg="#858585"
    ).pack(side=tk.LEFT, padx=(20, 0))
    
    # Separator
    tk.Frame(
        container,
        height=2,
        bg="#3e3e42"
    ).pack(fill=tk.X)
    
    # Scrollable content
    canvas = tk.Canvas(container, bg=bg_color, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=bg_color)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Overview section
    overview_frame = tk.Frame(scrollable_frame, bg=bg_color, padx=15, pady=15)
    overview_frame.pack(fill=tk.X)
    
    tk.Label(
        overview_frame,
        text="System Overview",
        font=(FONT_FAMILY, 11, "bold"),
        bg=bg_color,
        fg="#e3e4e8"
    ).pack(anchor=tk.W, pady=(0, 10))
    
    # Overview metrics
    metrics_grid = tk.Frame(overview_frame, bg=bg_color)
    metrics_grid.pack(fill=tk.X)
    
    overview_metrics = [
        {"key": "agents_active", "title": "Active Agents", "value": "2/3", "icon": "🤖"},
        {"key": "alerts", "title": "Active Alerts", "value": "3", "icon": "⚠️"},
        {"key": "uptime", "title": "Uptime", "value": "2h 34m", "icon": "⏱️"},
        {"key": "health", "title": "System Health", "value": "Good", "icon": "💚"},
    ]
    
    for idx, metric in enumerate(overview_metrics):
        card = InfoCard(
            metrics_grid,
            title=metric["title"],
            value=metric["value"],
            icon=metric["icon"],
            bg_color="#2d2d30",
            border_color="#3e3e42"
        )
        card.grid(row=0, column=idx, padx=5, pady=5, sticky=tk.NSEW)
        metrics_grid.columnconfigure(idx, weight=1)
    
    # Agent monitor panel
    agent_panel = AgentMonitorPanel(scrollable_frame, bg_color=bg_color)
    agent_panel.pack(fill=tk.BOTH, expand=True)
    
    # Pack canvas and scrollbar
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    return container, agent_panel
