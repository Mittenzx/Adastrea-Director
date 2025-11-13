"""
Example: API Cost Tracking

This example demonstrates how to use the cost tracker to monitor API usage
in Adastrea Director.
"""

import sys
import os

# Add parent directory to path to import cost_tracker
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cost_tracker import cost_tracker, set_budgets


def example_1_basic_tracking():
    """Example 1: Basic cost tracking."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Cost Tracking")
    print("=" * 60)
    
    # Simulate some API calls
    print("\nSimulating API calls...")
    
    # Query agent call (GPT-3.5-turbo)
    cost_tracker.track_call(
        component="query_agent",
        model="gpt-3.5-turbo",
        input_tokens=1500,
        output_tokens=300
    )
    print("✓ Query agent call tracked")
    
    # Goal analysis call (GPT-4)
    cost_tracker.track_call(
        component="goal_analysis_agent",
        model="gpt-4",
        input_tokens=1200,
        output_tokens=800
    )
    print("✓ Goal analysis call tracked")
    
    # Task decomposition call (GPT-4)
    cost_tracker.track_call(
        component="task_decomposition_agent",
        model="gpt-4",
        input_tokens=1800,
        output_tokens=2500
    )
    print("✓ Task decomposition call tracked")
    
    # Print summary
    cost_tracker.print_summary()


def example_2_budget_alerts():
    """Example 2: Budget alerts."""
    print("\n" + "=" * 60)
    print("Example 2: Budget Alerts")
    print("=" * 60)
    
    # Set budgets
    print("\nSetting budgets: Daily=$1.00, Monthly=$20.00")
    set_budgets(daily=1.00, monthly=20.00)
    
    # Make an expensive call that exceeds daily budget
    print("\nMaking expensive API call (should trigger alert)...")
    cost_tracker.track_call(
        component="code_generation_agent",
        model="gpt-4",
        input_tokens=5000,
        output_tokens=10000
    )
    
    print("\nCurrent costs:")
    print(f"  Daily: ${cost_tracker.get_daily_cost():.2f}")
    print(f"  Monthly: ${cost_tracker.get_monthly_cost():.2f}")


def example_3_cost_breakdown():
    """Example 3: Cost breakdown analysis."""
    print("\n" + "=" * 60)
    print("Example 3: Cost Breakdown Analysis")
    print("=" * 60)
    
    # Get breakdown by component
    print("\nCost by Component:")
    by_component = cost_tracker.get_breakdown_by_component(days=30)
    for component, cost in sorted(by_component.items(), key=lambda x: x[1], reverse=True):
        print(f"  {component:<40} ${cost:.4f}")
    
    # Get breakdown by model
    print("\nCost by Model:")
    by_model = cost_tracker.get_breakdown_by_model(days=30)
    for model, cost in sorted(by_model.items(), key=lambda x: x[1], reverse=True):
        print(f"  {model:<40} ${cost:.4f}")
    
    # Get token usage
    print("\nToken Usage:")
    tokens = cost_tracker.get_token_usage(days=30)
    print(f"  Input tokens:  {tokens['input_tokens']:>10,}")
    print(f"  Output tokens: {tokens['output_tokens']:>10,}")
    print(f"  Total tokens:  {tokens['total_tokens']:>10,}")


def example_4_export_report():
    """Example 4: Export cost report."""
    print("\n" + "=" * 60)
    print("Example 4: Export Cost Report")
    print("=" * 60)
    
    # Export report to JSON
    report_file = "example_cost_report.json"
    cost_tracker.export_report(filename=report_file, days=30)
    print(f"\nCost report exported to: {report_file}")
    
    # Show what's in the report
    import json
    with open(report_file, 'r') as f:
        report = json.load(f)
    
    print("\nReport contents:")
    print(f"  Generated at: {report['generated_at']}")
    print(f"  Daily cost: ${report['costs']['daily']:.4f}")
    print(f"  Monthly cost: ${report['costs']['monthly']:.4f}")
    print(f"  Total calls: {report['call_counts']['total']}")


def example_5_integration():
    """Example 5: Integration with LangChain."""
    print("\n" + "=" * 60)
    print("Example 5: Integration with LangChain")
    print("=" * 60)
    
    print("\nExample code for integrating with your agents:")
    
    print("""
# In your agent code:
from cost_tracker import cost_tracker, track_langchain_call

class QueryAgent:
    def process_query(self, query: str) -> str:
        # Make LLM call
        response = self.chain.invoke({"question": query})
        
        # Track the cost
        track_langchain_call(response, "query_agent")
        
        return response["answer"]
""")
    
    print("\nThis automatically extracts token usage from LangChain responses")
    print("and tracks costs for each component.")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " Cost Tracking Examples ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Run examples
    example_1_basic_tracking()
    example_2_budget_alerts()
    example_3_cost_breakdown()
    example_4_export_report()
    example_5_integration()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60 + "\n")
    
    # Cleanup
    if os.path.exists("example_cost_report.json"):
        os.remove("example_cost_report.json")
        print("Cleaned up example files.")
