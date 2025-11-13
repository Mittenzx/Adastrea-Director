"""
cost_tracker.py - API Cost Tracking for Adastrea Director

This module provides cost tracking functionality for monitoring OpenAI API usage
across all components of the Adastrea Director system.

Usage:
    from cost_tracker import cost_tracker, track_langchain_call
    
    # Track an API call
    response = llm.invoke(prompt)
    track_langchain_call(response, "query_agent")
    
    # View costs
    cost_tracker.print_summary()
    
    # Check budgets
    if cost_tracker.get_daily_cost() > 5.0:
        print("Daily budget exceeded!")
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class APICall:
    """Record of a single API call."""
    timestamp: str
    component: str  # "query_agent", "goal_agent", etc.
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APICall':
        """Create from dictionary."""
        return cls(**data)


class CostTracker:
    """
    Track API costs for Adastrea Director.
    
    This class monitors API usage across all components and provides
    cost analysis, budget alerts, and detailed reporting.
    """
    
    # OpenAI pricing (per 1M tokens) - Updated November 2025
    PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "gpt-3.5-turbo-16k": {"input": 0.50, "output": 1.50},
        "text-embedding-3-small": {"input": 0.020, "output": 0.020},
        "text-embedding-3-large": {"input": 0.130, "output": 0.130},
        "text-embedding-ada-002": {"input": 0.100, "output": 0.100},
    }
    
    def __init__(
        self,
        log_file: str = "api_costs.json",
        daily_budget: Optional[float] = None,
        monthly_budget: Optional[float] = None
    ):
        """
        Initialize the cost tracker.
        
        Args:
            log_file: Path to the JSON file for storing cost history
            daily_budget: Optional daily budget limit (USD)
            monthly_budget: Optional monthly budget limit (USD)
        """
        self.log_file = log_file
        self.daily_budget = daily_budget
        self.monthly_budget = monthly_budget
        self.calls: List[APICall] = []
        self._load_history()
    
    def _load_history(self):
        """Load call history from file."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.calls = [APICall.from_dict(call) for call in data]
            except Exception as e:
                print(f"Warning: Could not load cost history: {e}")
                self.calls = []
    
    def _save_history(self):
        """Save call history to file."""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(
                    [call.to_dict() for call in self.calls],
                    f,
                    indent=2
                )
        except Exception as e:
            print(f"Warning: Could not save cost history: {e}")
    
    def _calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost for an API call.
        
        Args:
            model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in USD
        """
        if model not in self.PRICING:
            print(f"Warning: Unknown model '{model}', cost not tracked accurately")
            # Use GPT-4 pricing as upper bound estimate
            pricing = self.PRICING.get("gpt-4", {"input": 30.0, "output": 60.0})
        else:
            pricing = self.PRICING[model]
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost
    
    def track_call(
        self,
        component: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Track an API call.
        
        Args:
            component: Name of the component making the call
                      (e.g., "query_agent", "goal_analysis_agent")
            model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost of this API call in USD
        """
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        
        call = APICall(
            timestamp=datetime.now().isoformat(),
            component=component,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost
        )
        
        self.calls.append(call)
        self._save_history()
        
        # Check budgets and alert if exceeded
        self._check_budgets()
        
        return cost
    
    def _check_budgets(self):
        """Check if budgets are exceeded and print warnings."""
        if self.daily_budget is not None:
            daily = self.get_daily_cost()
            if daily > self.daily_budget:
                print(
                    f"⚠️  ALERT: Daily budget exceeded! "
                    f"${daily:.2f} > ${self.daily_budget:.2f}"
                )
        
        if self.monthly_budget is not None:
            monthly = self.get_monthly_cost()
            if monthly > self.monthly_budget:
                print(
                    f"⚠️  ALERT: Monthly budget exceeded! "
                    f"${monthly:.2f} > ${self.monthly_budget:.2f}"
                )
    
    def get_daily_cost(self) -> float:
        """Get total cost for today."""
        today = datetime.now().date()
        return sum(
            call.cost
            for call in self.calls
            if datetime.fromisoformat(call.timestamp).date() == today
        )
    
    def get_weekly_cost(self) -> float:
        """Get total cost for the last 7 days."""
        week_ago = datetime.now() - timedelta(days=7)
        return sum(
            call.cost
            for call in self.calls
            if datetime.fromisoformat(call.timestamp) > week_ago
        )
    
    def get_monthly_cost(self) -> float:
        """Get total cost for the last 30 days."""
        month_ago = datetime.now() - timedelta(days=30)
        return sum(
            call.cost
            for call in self.calls
            if datetime.fromisoformat(call.timestamp) > month_ago
        )
    
    def get_total_cost(self) -> float:
        """Get total cost for all tracked calls."""
        return sum(call.cost for call in self.calls)
    
    def get_breakdown_by_component(
        self,
        days: int = 30
    ) -> Dict[str, float]:
        """
        Get cost breakdown by component.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary mapping component names to costs
        """
        cutoff = datetime.now() - timedelta(days=days)
        breakdown = {}
        
        for call in self.calls:
            if datetime.fromisoformat(call.timestamp) > cutoff:
                breakdown[call.component] = (
                    breakdown.get(call.component, 0) + call.cost
                )
        
        return breakdown
    
    def get_breakdown_by_model(
        self,
        days: int = 30
    ) -> Dict[str, float]:
        """
        Get cost breakdown by model.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary mapping model names to costs
        """
        cutoff = datetime.now() - timedelta(days=days)
        breakdown = {}
        
        for call in self.calls:
            if datetime.fromisoformat(call.timestamp) > cutoff:
                breakdown[call.model] = (
                    breakdown.get(call.model, 0) + call.cost
                )
        
        return breakdown
    
    def get_token_usage(
        self,
        days: int = 30
    ) -> Dict[str, int]:
        """
        Get token usage statistics.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with input_tokens, output_tokens, and total_tokens
        """
        cutoff = datetime.now() - timedelta(days=days)
        input_tokens = 0
        output_tokens = 0
        
        for call in self.calls:
            if datetime.fromisoformat(call.timestamp) > cutoff:
                input_tokens += call.input_tokens
                output_tokens += call.output_tokens
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }
    
    def get_call_count(
        self,
        days: int = 30,
        component: Optional[str] = None
    ) -> int:
        """
        Get number of API calls.
        
        Args:
            days: Number of days to look back
            component: Optional component filter
            
        Returns:
            Number of API calls
        """
        cutoff = datetime.now() - timedelta(days=days)
        count = 0
        
        for call in self.calls:
            if datetime.fromisoformat(call.timestamp) > cutoff:
                if component is None or call.component == component:
                    count += 1
        
        return count
    
    def print_summary(self, days: int = 30):
        """
        Print a summary of costs.
        
        Args:
            days: Number of days to include in component/model breakdown
        """
        print("\n" + "=" * 60)
        print(" API Cost Summary ".center(60, "="))
        print("=" * 60)
        
        print(f"\n{'Period':<20} {'Cost':>15} {'Calls':>10}")
        print("-" * 60)
        print(f"{'Daily (Today)':<20} ${self.get_daily_cost():>14.4f} {self.get_call_count(days=1):>10}")
        print(f"{'Weekly (7 days)':<20} ${self.get_weekly_cost():>14.4f} {self.get_call_count(days=7):>10}")
        print(f"{'Monthly (30 days)':<20} ${self.get_monthly_cost():>14.4f} {self.get_call_count(days=30):>10}")
        print(f"{'Total (All Time)':<20} ${self.get_total_cost():>14.4f} {self.get_call_count(days=9999):>10}")
        
        # Token usage
        tokens = self.get_token_usage(days)
        print(f"\n{'Token Usage (Last ' + str(days) + ' Days)'}")
        print("-" * 60)
        print(f"{'Input Tokens:':<30} {tokens['input_tokens']:>15,}")
        print(f"{'Output Tokens:':<30} {tokens['output_tokens']:>15,}")
        print(f"{'Total Tokens:':<30} {tokens['total_tokens']:>15,}")
        
        # Budget status
        if self.daily_budget or self.monthly_budget:
            print(f"\n{'Budget Status'}")
            print("-" * 60)
            if self.daily_budget:
                daily = self.get_daily_cost()
                pct = (daily / self.daily_budget) * 100
                status = "✓" if daily <= self.daily_budget else "✗"
                print(f"{status} Daily Budget:    ${daily:.2f} / ${self.daily_budget:.2f} ({pct:.1f}%)")
            if self.monthly_budget:
                monthly = self.get_monthly_cost()
                pct = (monthly / self.monthly_budget) * 100
                status = "✓" if monthly <= self.monthly_budget else "✗"
                print(f"{status} Monthly Budget:  ${monthly:.2f} / ${self.monthly_budget:.2f} ({pct:.1f}%)")
        
        # Component breakdown
        print(f"\n{'Cost by Component (Last ' + str(days) + ' Days)'}")
        print("-" * 60)
        by_component = self.get_breakdown_by_component(days)
        if by_component:
            for component, cost in sorted(
                by_component.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                calls = self.get_call_count(days, component)
                print(f"{component:<40} ${cost:>8.4f} ({calls:>4} calls)")
        else:
            print("No data available")
        
        # Model breakdown
        print(f"\n{'Cost by Model (Last ' + str(days) + ' Days)'}")
        print("-" * 60)
        by_model = self.get_breakdown_by_model(days)
        if by_model:
            for model, cost in sorted(
                by_model.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                print(f"{model:<40} ${cost:>8.4f}")
        else:
            print("No data available")
        
        print("\n" + "=" * 60 + "\n")
    
    def export_report(
        self,
        filename: str = "cost_report.json",
        days: int = 30
    ):
        """
        Export cost report to JSON file.
        
        Args:
            filename: Output filename
            days: Number of days to include in report
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "period_days": days,
            "costs": {
                "daily": self.get_daily_cost(),
                "weekly": self.get_weekly_cost(),
                "monthly": self.get_monthly_cost(),
                "total": self.get_total_cost()
            },
            "call_counts": {
                "daily": self.get_call_count(days=1),
                "weekly": self.get_call_count(days=7),
                "monthly": self.get_call_count(days=30),
                "total": self.get_call_count(days=9999)
            },
            "token_usage": self.get_token_usage(days),
            "by_component": self.get_breakdown_by_component(days),
            "by_model": self.get_breakdown_by_model(days)
        }
        
        if self.daily_budget:
            report["budgets"] = {"daily": self.daily_budget}
        if self.monthly_budget:
            report["budgets"] = report.get("budgets", {})
            report["budgets"]["monthly"] = self.monthly_budget
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Cost report exported to {filename}")
        except Exception as e:
            print(f"Error exporting cost report: {e}")
    
    def clear_old_data(self, days: int = 90):
        """
        Clear data older than specified days.
        
        Args:
            days: Keep data from the last N days
        """
        cutoff = datetime.now() - timedelta(days=days)
        original_count = len(self.calls)
        
        self.calls = [
            call for call in self.calls
            if datetime.fromisoformat(call.timestamp) > cutoff
        ]
        
        removed_count = original_count - len(self.calls)
        if removed_count > 0:
            self._save_history()
            print(f"Cleared {removed_count} old records (kept last {days} days)")


# Global cost tracker instance
cost_tracker = CostTracker()


def track_langchain_call(response: Any, component: str) -> float:
    """
    Track a LangChain API call.
    
    This is a convenience function that extracts token usage from LangChain
    response objects and tracks them with the global cost tracker.
    
    Args:
        response: LangChain response object (must have response_metadata)
        component: Component name (e.g., "query_agent", "goal_analysis_agent")
        
    Returns:
        Cost of the API call in USD, or 0.0 if tracking failed
        
    Usage:
        response = llm.invoke(prompt)
        track_langchain_call(response, "query_agent")
    """
    try:
        # Try to extract token usage from response
        if hasattr(response, 'response_metadata'):
            metadata = response.response_metadata
            if 'token_usage' in metadata:
                usage = metadata['token_usage']
                model = metadata.get('model_name', 'unknown')
                
                return cost_tracker.track_call(
                    component=component,
                    model=model,
                    input_tokens=usage.get('prompt_tokens', 0),
                    output_tokens=usage.get('completion_tokens', 0)
                )
        
        # Try alternative response structure
        if hasattr(response, 'usage_metadata'):
            metadata = response.usage_metadata
            model = getattr(response, 'model', 'unknown')
            
            return cost_tracker.track_call(
                component=component,
                model=model,
                input_tokens=metadata.get('input_tokens', 0),
                output_tokens=metadata.get('output_tokens', 0)
            )
        
        print(f"Warning: Could not extract token usage from response for {component}")
        return 0.0
        
    except Exception as e:
        print(f"Warning: Error tracking API call for {component}: {e}")
        return 0.0


def set_budgets(daily: Optional[float] = None, monthly: Optional[float] = None):
    """
    Set budget limits for the global cost tracker.
    
    Args:
        daily: Daily budget in USD (None to disable)
        monthly: Monthly budget in USD (None to disable)
        
    Usage:
        set_budgets(daily=5.0, monthly=100.0)
    """
    cost_tracker.daily_budget = daily
    cost_tracker.monthly_budget = monthly
    print(f"Budget set: Daily=${daily}, Monthly=${monthly}")


if __name__ == "__main__":
    # Demo usage
    print("Cost Tracker Demo")
    print("-" * 60)
    
    # Simulate some API calls
    print("\nSimulating API calls...")
    cost_tracker.track_call("query_agent", "gpt-3.5-turbo", 1500, 300)
    cost_tracker.track_call("goal_analysis_agent", "gpt-4", 1200, 800)
    cost_tracker.track_call("task_decomposition_agent", "gpt-4", 1800, 2500)
    cost_tracker.track_call("code_generation_agent", "gpt-4", 2000, 3000)
    
    # Print summary
    cost_tracker.print_summary()
    
    # Export report
    cost_tracker.export_report("demo_cost_report.json")
