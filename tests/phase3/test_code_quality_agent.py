"""
Tests for the Code Quality Agent.
"""

import pytest
from agents.phase3.event_bus import EventBus, EventType
from agents.phase3.shared_state import SharedContext, AgentStatus
from agents.phase3.code_quality_agent import (
    CodeQualityAgent,
    CodeSmell,
    Violation,
    Refactoring,
    QualityReport
)


class TestCodeQualityAgent:
    """Tests for CodeQualityAgent class."""
    
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
    
    def test_agent_initialization(self, setup):
        """Test agent initialization."""
        agent, event_bus, shared_context = setup
        
        assert agent.agent_id == "code_quality_agent"
        assert not agent.is_running()
    
    def test_agent_start_stop(self, setup):
        """Test starting and stopping the agent."""
        agent, event_bus, shared_context = setup
        
        agent.start()
        assert agent.is_running()
        assert agent.get_status() == AgentStatus.BUSY
        
        agent.stop()
        assert not agent.is_running()
        assert agent.get_status() == AgentStatus.STOPPED
    
    def test_analyze_clean_code(self, setup):
        """Test analyzing clean code."""
        agent, event_bus, shared_context = setup
        
        clean_code = """
def simple_function(x, y):
    return x + y

def another_function(a):
    return a * 2
"""
        
        report = agent.analyze_code("clean.py", clean_code)
        
        assert report.file_path == "clean.py"
        assert report.lines_of_code > 0
        assert report.overall_score > 70  # Should score well
    
    def test_detect_magic_numbers(self, setup):
        """Test detecting magic numbers."""
        agent, event_bus, shared_context = setup
        
        code_with_magic = """
def calculate(x):
    return x * 500
    
def process(y):
    if y > 1000:
        return y / 250
    return 0
"""
        
        report = agent.analyze_code("magic.py", code_with_magic)
        
        # Should detect magic numbers (500, 1000, 250)
        magic_smells = [s for s in report.code_smells if s.smell_type == "magic_number"]
        assert len(magic_smells) > 0
    
    def test_detect_commented_code(self, setup):
        """Test detecting commented code."""
        agent, event_bus, shared_context = setup
        
        code_with_comments = """
def active_function(x):
    return x + 1

# def old_function(x):
#     return x * 2

# class OldClass:
#     pass
"""
        
        report = agent.analyze_code("comments.py", code_with_comments)
        
        # Should detect commented code
        comment_smells = [s for s in report.code_smells if s.smell_type == "commented_code"]
        assert len(comment_smells) > 0
    
    def test_detect_line_length_violations(self, setup):
        """Test detecting line length violations."""
        agent, event_bus, shared_context = setup
        
        long_line_code = """
def function():
    very_long_variable_name = "This is a very long string that extends way beyond the recommended line length limit and should trigger a violation"
"""
        
        report = agent.analyze_code("longlines.py", long_line_code)
        
        # Should detect line length violations
        line_violations = [v for v in report.violations if v.violation_type == "line_length"]
        assert len(line_violations) > 0
    
    def test_detect_trailing_whitespace(self, setup):
        """Test detecting trailing whitespace."""
        agent, event_bus, shared_context = setup
        
        code_with_whitespace = "def function():  \n    return 42   \n"
        
        report = agent.analyze_code("whitespace.py", code_with_whitespace)
        
        # Should detect trailing whitespace
        ws_violations = [v for v in report.violations if v.violation_type == "trailing_whitespace"]
        assert len(ws_violations) > 0
    
    def test_generate_refactoring_suggestions(self, setup):
        """Test generating refactoring suggestions."""
        agent, event_bus, shared_context = setup
        
        code_smell = CodeSmell(
            smell_type="magic_number",
            severity="low",
            description="Magic number found",
            location="test.py:1",
            example="x = 42",
            suggestion="Extract to constant"
        )
        
        refactoring = agent.suggest_refactoring(code_smell)
        
        assert refactoring is not None
        assert refactoring.refactoring_type == "extract_constant"
        assert refactoring.code_smell == code_smell
        assert len(refactoring.benefits) > 0
    
    def test_refactoring_events(self, setup):
        """Test that refactoring opportunities trigger events."""
        agent, event_bus, shared_context = setup
        
        # Track refactoring events
        refactorings = []
        event_bus.subscribe(EventType.REFACTORING_OPPORTUNITY, 
                          lambda e: refactorings.append(e))
        
        code_with_issues = """
# def old_code():
#     pass

def function():
    x = 500  # magic number
    return x * 1000  # another magic
"""
        
        report = agent.analyze_code("refactor.py", code_with_issues)
        
        # Should trigger refactoring event
        assert len(refactorings) > 0
    
    def test_calculate_quality_score(self, setup):
        """Test quality score calculation."""
        agent, event_bus, shared_context = setup
        
        # Code with known issues
        problematic_code = """
def bad_function():
    x = 500  # magic
    y = 1000  # magic
    very_long_line = "This line is intentionally very long to trigger a line length violation that should reduce the quality score"
    return x + y
"""
        
        report = agent.analyze_code("bad.py", problematic_code)
        
        # Score should be less than 100 due to issues
        assert report.overall_score < 100
        assert report.overall_score >= 0
    
    def test_calculate_technical_debt(self, setup):
        """Test technical debt calculation."""
        agent, event_bus, shared_context = setup
        
        # Analyze some files to build history
        code1 = "def func(): return 500 * 1000  # magic numbers\n" * 5
        code2 = "# def old(): pass\n" * 3
        
        agent.analyze_code("file1.py", code1)
        agent.analyze_code("file2.py", code2)
        
        debt = agent.calculate_technical_debt()
        
        assert debt.total_debt_hours > 0
        assert debt.code_smells_count > 0
        assert debt.debt_ratio >= 0
    
    def test_technical_debt_with_no_history(self, setup):
        """Test technical debt calculation with no history."""
        agent, event_bus, shared_context = setup
        
        debt = agent.calculate_technical_debt()
        
        # Should return zero values
        assert debt.total_debt_hours == 0
        assert debt.code_smells_count == 0
        assert debt.violations_count == 0
    
    def test_quality_reports_history(self, setup):
        """Test quality reports history tracking."""
        agent, event_bus, shared_context = setup
        
        # Analyze multiple files
        for i in range(5):
            code = f"def func{i}(): return {i}\n"
            agent.analyze_code(f"file{i}.py", code)
        
        reports = agent.get_quality_reports()
        assert len(reports) >= 5
    
    def test_quality_reports_limit(self, setup):
        """Test quality reports history limit."""
        agent, event_bus, shared_context = setup
        
        # Analyze many files
        for i in range(10):
            code = f"def func{i}(): return {i}\n"
            agent.analyze_code(f"file{i}.py", code)
        
        # Get limited results
        limited_reports = agent.get_quality_reports(limit=3)
        assert len(limited_reports) == 3
        
        # Should be the most recent
        assert limited_reports[0].file_path == "file7.py"
        assert limited_reports[2].file_path == "file9.py"
    
    def test_code_quality_issue_event(self, setup):
        """Test that quality issues trigger events."""
        agent, event_bus, shared_context = setup
        
        quality_issues = []
        event_bus.subscribe(EventType.CODE_QUALITY_ISSUE,
                          lambda e: quality_issues.append(e))
        
        # Code with issues
        bad_code = """
def function():
    x = 500  # magic number
    very_long_line_that_exceeds_the_recommended_maximum_length_and_should_trigger_a_violation_for_sure_yes_indeed
    return x
"""
        
        report = agent.analyze_code("bad.py", bad_code)
        
        # Should trigger quality issue event
        assert len(quality_issues) > 0
        assert quality_issues[0].payload['file_path'] == "bad.py"
    
    def test_complexity_calculation(self, setup):
        """Test complexity calculation."""
        agent, event_bus, shared_context = setup
        
        simple_code = "def func(): return 1\n"
        complex_code = """
def complex_func(x):
    if x > 0:
        if x < 10:
            for i in range(x):
                if i % 2 == 0:
                    while i > 0:
                        i -= 1
    elif x < 0:
        pass
    else:
        pass
    return x
"""
        
        simple_report = agent.analyze_code("simple.py", simple_code)
        complex_report = agent.analyze_code("complex.py", complex_code)
        
        # Complex code should have lower score due to higher complexity
        # (complexity affects quality negatively)
        assert complex_report.complexity_score < 100.0
        assert simple_report.lines_of_code < complex_report.lines_of_code
