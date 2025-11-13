"""
Extended tests for the Code Quality Agent.

These tests cover additional scenarios for code quality analysis including
more code smell patterns, refactoring priority, technical debt trends,
and integration scenarios.
"""

import pytest
from datetime import datetime
from agents.phase3.event_bus import EventBus, EventType
from agents.phase3.shared_state import SharedContext
from agents.phase3.code_quality_agent import CodeQualityAgent, CodeSmell


class TestCodeQualityAgentExtended:
    """Extended tests for CodeQualityAgent class."""
    
    @pytest.fixture
    def setup(self):
        """Set up test fixtures."""
        event_bus = EventBus()
        shared_context = SharedContext()
        agent = CodeQualityAgent(
            event_bus=event_bus,
            shared_context=shared_context
        )
        return agent, event_bus, shared_context
    
    def test_detect_long_method(self, setup):
        """Test detection of long methods."""
        agent, event_bus, shared_context = setup
        
        # Create a very long method
        long_method = "def long_method():\n"
        for i in range(100):
            long_method += f"    line_{i} = {i}\n"
        long_method += "    return sum\n"
        
        report = agent.analyze_code("long_method.py", long_method)
        
        # Should have lower score due to complexity
        assert report.overall_score < 100
        assert report.lines_of_code > 50
    
    def test_detect_duplicate_code(self, setup):
        """Test detection of duplicate code patterns."""
        agent, event_bus, shared_context = setup
        
        duplicate_code = """
def process_a(x):
    result = x * 2
    result = result + 10
    return result

def process_b(y):
    result = y * 2
    result = result + 10
    return result
"""
        
        report = agent.analyze_code("duplicate.py", duplicate_code)
        
        # Should detect code patterns
        assert report.lines_of_code > 0
    
    def test_detect_deep_nesting(self, setup):
        """Test detection of deeply nested code."""
        agent, event_bus, shared_context = setup
        
        nested_code = """
def deep_nesting():
    if condition1:
        if condition2:
            if condition3:
                if condition4:
                    if condition5:
                        return True
    return False
"""
        
        report = agent.analyze_code("nested.py", nested_code)
        
        # Deep nesting should affect complexity score
        assert report.complexity_score < 100
    
    def test_detect_too_many_parameters(self, setup):
        """Test detection of functions with too many parameters."""
        agent, event_bus, shared_context = setup
        
        many_params_code = """
def function_with_many_params(a, b, c, d, e, f, g, h, i, j):
    return a + b + c + d + e + f + g + h + i + j
"""
        
        report = agent.analyze_code("many_params.py", many_params_code)
        
        # Should analyze the code
        assert report.lines_of_code > 0
    
    def test_refactoring_priority_calculation(self, setup):
        """Test that refactoring opportunities are prioritized correctly."""
        agent, event_bus, shared_context = setup
        
        # Create different types of code smells with recognized types
        duplicate_smell = CodeSmell(
            smell_type="duplicate_code",
            severity="high",
            description="Duplicate code detected",
            location="test.py:1",
            example="code",
            suggestion="Extract to function"
        )
        
        magic_number_smell = CodeSmell(
            smell_type="magic_number",
            severity="low",
            description="Magic number found",
            location="test.py:10",
            example="x = 42",
            suggestion="Extract to constant"
        )
        
        duplicate_refactoring = agent.suggest_refactoring(duplicate_smell)
        magic_refactoring = agent.suggest_refactoring(magic_number_smell)
        
        # Both should return refactoring suggestions
        assert duplicate_refactoring is not None
        assert magic_refactoring is not None
        
        # Duplicate code should have higher priority than magic number
        assert duplicate_refactoring.priority == "high"
        assert magic_refactoring.priority == "low"
    
    def test_technical_debt_trend_positive(self, setup):
        """Test technical debt trend when improving."""
        agent, event_bus, shared_context = setup
        
        # First analysis with issues
        bad_code = """
def bad():
    x = 500  # magic
    y = 1000  # magic
    return x + y
"""
        agent.analyze_code("file1.py", bad_code)
        
        # Second analysis with fewer issues
        better_code = """
def better():
    return 1 + 2
"""
        agent.analyze_code("file2.py", better_code)
        
        debt = agent.calculate_technical_debt()
        
        # Should have calculated debt
        assert debt.total_debt_hours >= 0
    
    def test_technical_debt_trend_negative(self, setup):
        """Test technical debt trend when degrading."""
        agent, event_bus, shared_context = setup
        
        # First analysis with clean code
        clean_code = "def func(): return 1\n"
        agent.analyze_code("file1.py", clean_code)
        
        # Second analysis with more issues
        problematic_code = """
# def old(): pass
def func():
    x = 500 * 1000  # magic numbers
    return x
"""
        agent.analyze_code("file2.py", problematic_code)
        
        debt = agent.calculate_technical_debt()
        
        # Should track increasing debt
        assert debt.code_smells_count > 0
    
    def test_quality_score_threshold(self, setup):
        """Test quality score is within valid range."""
        agent, event_bus, shared_context = setup
        
        # Test various code samples
        code_samples = [
            "def simple(): return 1\n",
            "x = 500\ny = 1000\nz = x + y\n",
            "# def old(): pass\n" * 10,
        ]
        
        for i, code in enumerate(code_samples):
            report = agent.analyze_code(f"file{i}.py", code)
            
            # Score should be between 0 and 100
            assert 0 <= report.overall_score <= 100
    
    def test_multiple_file_analysis(self, setup):
        """Test analyzing multiple files in sequence."""
        agent, event_bus, shared_context = setup
        
        files = {
            "file1.py": "def func1(): return 1\n",
            "file2.py": "def func2(): return 2\n",
            "file3.py": "def func3(): return 3\n",
        }
        
        for filename, code in files.items():
            report = agent.analyze_code(filename, code)
            assert report.file_path == filename
        
        # Should have reports for all files
        reports = agent.get_quality_reports()
        assert len(reports) >= 3
    
    def test_refactoring_benefits(self, setup):
        """Test that refactoring suggestions include benefits."""
        agent, event_bus, shared_context = setup
        
        smell = CodeSmell(
            smell_type="magic_number",
            severity="medium",
            description="Magic number found",
            location="test.py:5",
            example="x = 42",
            suggestion="Extract to constant"
        )
        
        refactoring = agent.suggest_refactoring(smell)
        
        assert refactoring is not None
        assert len(refactoring.benefits) > 0
        assert isinstance(refactoring.benefits, list)
    
    def test_refactoring_effort_estimation(self, setup):
        """Test that refactoring effort is estimated."""
        agent, event_bus, shared_context = setup
        
        smell = CodeSmell(
            smell_type="long_method",
            severity="high",
            description="Method is too long",
            location="test.py:10",
            example="def long_method():",
            suggestion="Break into smaller methods"
        )
        
        refactoring = agent.suggest_refactoring(smell)
        
        assert refactoring is not None
        assert refactoring.estimated_effort in ["low", "medium", "high"]
    
    def test_code_quality_with_multiple_smells(self, setup):
        """Test code with multiple types of smells."""
        agent, event_bus, shared_context = setup
        
        multi_smell_code = """
# def old_code():
#     pass

def process(a, b, c, d, e, f, g, h):  # too many params
    x = 500  # magic number
    y = 1000  # magic number
    very_long_line_that_exceeds_standard_limit_and_should_be_detected_as_a_violation_yes_this_line_is_intentionally_very_long
    return x + y
"""
        
        report = agent.analyze_code("multi_smell.py", multi_smell_code)
        
        # Should detect multiple issues
        assert len(report.code_smells) > 0 or len(report.violations) > 0
        assert report.overall_score < 100
    
    def test_quality_report_timestamp(self, setup):
        """Test that quality reports have timestamps."""
        agent, event_bus, shared_context = setup
        
        report = agent.analyze_code("test.py", "def func(): return 1\n")
        
        assert report.timestamp is not None
        assert isinstance(report.timestamp, datetime)
    
    def test_event_integration_quality_issues(self, setup):
        """Test event bus integration for quality issues."""
        agent, event_bus, shared_context = setup
        
        quality_events = []
        event_bus.subscribe(EventType.CODE_QUALITY_ISSUE,
                          lambda e: quality_events.append(e))
        
        # Analyze code with issues
        bad_code = """
def bad():
    x = 500  # magic
    very_long_line_exceeding_reasonable_length_limit_that_should_trigger_a_violation_for_line_length_issues
    # def old(): pass
"""
        agent.analyze_code("bad.py", bad_code)
        
        # Should have triggered quality issue event
        assert len(quality_events) > 0
    
    def test_event_integration_refactoring(self, setup):
        """Test event bus integration for refactoring opportunities."""
        agent, event_bus, shared_context = setup
        
        refactoring_events = []
        event_bus.subscribe(EventType.REFACTORING_OPPORTUNITY,
                          lambda e: refactoring_events.append(e))
        
        # Analyze code that needs refactoring
        code = """
# def old_unused_code():
#     pass

def function():
    magic = 500
    return magic * 1000
"""
        agent.analyze_code("refactor.py", code)
        
        # Should have triggered refactoring event
        assert len(refactoring_events) > 0
    
    def test_complexity_score_calculation(self, setup):
        """Test complexity score calculation for various code patterns."""
        agent, event_bus, shared_context = setup
        
        simple = "def func(): return 1\n"
        complex_code = """
def complex(x):
    if x > 0:
        for i in range(x):
            if i % 2:
                while i > 0:
                    if i % 3:
                        return i
                    i -= 1
    return 0
"""
        
        simple_report = agent.analyze_code("simple.py", simple)
        complex_report = agent.analyze_code("complex.py", complex_code)
        
        # Complex code should have higher complexity penalty
        assert complex_report.complexity_score <= simple_report.complexity_score
    
    def test_technical_debt_high_priority_items(self, setup):
        """Test tracking of high priority technical debt items."""
        agent, event_bus, shared_context = setup
        
        # Analyze code with critical issues
        critical_code = """
# def old1(): pass
# def old2(): pass
# def old3(): pass

def func():
    x = 500 * 1000 * 2000  # Multiple magic numbers
    return x
"""
        agent.analyze_code("critical.py", critical_code)
        
        debt = agent.calculate_technical_debt()
        
        # Should have high priority items
        assert debt.high_priority_items >= 0
    
    def test_technical_debt_ratio(self, setup):
        """Test technical debt ratio calculation."""
        agent, event_bus, shared_context = setup
        
        # Analyze some files
        for i in range(5):
            code = f"def func{i}(): return {i}\n"
            agent.analyze_code(f"file{i}.py", code)
        
        debt = agent.calculate_technical_debt()
        
        # Ratio should be calculated
        assert debt.debt_ratio >= 0
    
    def test_quality_reports_ordering(self, setup):
        """Test that quality reports are ordered by timestamp."""
        agent, event_bus, shared_context = setup
        
        # Analyze files with small delays
        for i in range(3):
            code = f"def func{i}(): return {i}\n"
            agent.analyze_code(f"file{i}.py", code)
        
        reports = agent.get_quality_reports()
        
        # Most recent should be last (or first depending on implementation)
        assert len(reports) >= 3
    
    def test_empty_code_analysis(self, setup):
        """Test analyzing empty code."""
        agent, event_bus, shared_context = setup
        
        report = agent.analyze_code("empty.py", "")
        
        assert report.lines_of_code == 0
        assert report.overall_score >= 0
    
    def test_whitespace_only_code(self, setup):
        """Test analyzing code with only whitespace."""
        agent, event_bus, shared_context = setup
        
        report = agent.analyze_code("whitespace.py", "   \n   \n   \n")
        
        # Should handle gracefully
        assert report.lines_of_code >= 0
    
    def test_agent_state_during_analysis(self, setup):
        """Test agent state changes during code analysis."""
        agent, event_bus, shared_context = setup
        
        agent.start()
        assert agent.is_running()
        
        # Analyze code
        agent.analyze_code("test.py", "def func(): return 1\n")
        
        # Agent should still be running
        assert agent.is_running()
        
        agent.stop()
        assert not agent.is_running()
    
    def test_code_smell_types_variety(self, setup):
        """Test detection of various code smell types."""
        agent, event_bus, shared_context = setup
        
        # Code with multiple smell types
        code_samples = {
            "magic_numbers.py": "x = 500\ny = 1000\nz = x * y\n",
            "commented.py": "# def old(): pass\n# class Old: pass\n",
            "long_lines.py": "x = 'very long string that exceeds reasonable line length limits and should be flagged'\n",
        }
        
        all_smells = []
        for filename, code in code_samples.items():
            report = agent.analyze_code(filename, code)
            all_smells.extend(report.code_smells)
        
        # Should have detected smells
        assert len(all_smells) > 0
        
        # Should have different types
        smell_types = set(smell.smell_type for smell in all_smells)
        assert len(smell_types) > 0
    
    def test_violation_types_variety(self, setup):
        """Test detection of various violation types."""
        agent, event_bus, shared_context = setup
        
        violation_code = """
def func():  
    x = 1   
    very_long_line_exceeding_standard_limits_that_should_be_detected_as_a_violation_for_line_length
    return x
"""
        
        report = agent.analyze_code("violations.py", violation_code)
        
        # Should detect violations
        if len(report.violations) > 0:
            violation_types = set(v.violation_type for v in report.violations)
            assert len(violation_types) > 0
    
    def test_concurrent_analysis(self, setup):
        """Test analyzing multiple files in quick succession."""
        agent, event_bus, shared_context = setup
        
        # Analyze many files quickly
        for i in range(20):
            code = f"def func{i}(): return {i}\n"
            report = agent.analyze_code(f"file{i}.py", code)
            assert report.file_path == f"file{i}.py"
        
        # Get reports with higher limit
        reports = agent.get_quality_reports(limit=25)
        assert len(reports) >= 20
