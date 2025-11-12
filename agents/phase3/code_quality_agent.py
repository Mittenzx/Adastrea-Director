"""
Code Quality Agent

Maintains code quality through static analysis, code smell detection,
and refactoring suggestions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging
import re

from .base_agent import BaseAutonomousAgent
from .event_bus import Event, EventBus, EventType
from .shared_state import SharedContext

logger = logging.getLogger(__name__)


@dataclass
class CodeSmell:
    """
    A code smell detected in the codebase.
    
    Attributes:
        smell_type: Type of code smell
        severity: Severity level
        description: Description of the issue
        location: File and line number
        example: Code example showing the smell
        suggestion: How to fix it
    """
    smell_type: str
    severity: str
    description: str
    location: str
    example: str
    suggestion: str


@dataclass
class Violation:
    """
    A coding standard violation.
    
    Attributes:
        violation_type: Type of violation
        rule: The rule that was violated
        severity: Severity level
        description: Description
        location: File and line number
        fix: Suggested fix
    """
    violation_type: str
    rule: str
    severity: str
    description: str
    location: str
    fix: Optional[str] = None


@dataclass
class Refactoring:
    """
    A refactoring opportunity.
    
    Attributes:
        refactoring_type: Type of refactoring
        priority: Priority level
        description: Description of the refactoring
        location: Where to apply the refactoring
        code_smell: Related code smell
        estimated_effort: Estimated effort to implement
        benefits: Benefits of the refactoring
    """
    refactoring_type: str
    priority: str
    description: str
    location: str
    code_smell: Optional[CodeSmell] = None
    estimated_effort: str = "medium"
    benefits: List[str] = field(default_factory=list)


@dataclass
class QualityReport:
    """
    A code quality analysis report.
    
    Attributes:
        timestamp: When analysis was performed
        file_path: File that was analyzed
        lines_of_code: Number of lines
        complexity_score: Complexity metric
        code_smells: Detected code smells
        violations: Standard violations
        refactorings: Refactoring opportunities
        overall_score: Overall quality score (0-100)
    """
    timestamp: datetime
    file_path: str
    lines_of_code: int
    complexity_score: float
    code_smells: List[CodeSmell]
    violations: List[Violation]
    refactorings: List[Refactoring]
    overall_score: float


@dataclass
class TechnicalDebtScore:
    """
    Technical debt metrics for the project.
    
    Attributes:
        total_debt_hours: Estimated hours to fix all issues
        debt_ratio: Debt ratio (debt / codebase size)
        code_smells_count: Number of code smells
        violations_count: Number of violations
        high_priority_items: Number of high priority items
        trend: Trend direction (improving, stable, worsening)
    """
    total_debt_hours: float
    debt_ratio: float
    code_smells_count: int
    violations_count: int
    high_priority_items: int
    trend: str = "stable"


class CodeQualityAgent(BaseAutonomousAgent):
    """
    Agent that maintains code quality standards.
    
    Capabilities:
    - Static code analysis
    - Detect code smells and anti-patterns
    - Suggest refactoring opportunities
    - Enforce coding standards
    - Track technical debt
    """
    
    def __init__(self,
                 event_bus: EventBus,
                 shared_context: SharedContext):
        """
        Initialize the Code Quality Agent.
        
        Args:
            event_bus: Event bus for communication
            shared_context: Shared context for coordination
        """
        super().__init__(
            agent_id="code_quality_agent",
            event_bus=event_bus,
            shared_context=shared_context
        )
        
        self._quality_reports: List[QualityReport] = []
        self._max_history_size = 100
        
        # Define code smell patterns
        self._smell_patterns = {
            'long_method': (r'def\s+\w+\([^)]*\):', 50),  # Methods longer than 50 lines
            'long_parameter_list': (r'def\s+\w+\(([^)]+)\):', 5),  # More than 5 parameters
            'magic_numbers': (r'\b\d{3,}\b', 0),  # Numbers with 3+ digits
            'commented_code': (r'^\s*#.*(?:def|class|if|for|while)', 0),
        }
        
        logger.info("CodeQualityAgent created")
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events."""
        # Could subscribe to code change events in the future
        pass
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        pass
    
    def _on_start(self) -> None:
        """Initialize code quality monitoring on start."""
        logger.info("Code quality monitoring started")
        self._set_current_task("Monitoring code quality")
    
    def _on_stop(self) -> None:
        """Clean up on stop."""
        logger.info("Code quality monitoring stopped")
        self._set_current_task(None)
    
    def analyze_code(self, file_path: str, code_content: str) -> QualityReport:
        """
        Analyze code for quality issues.
        
        Args:
            file_path: Path to the file being analyzed
            code_content: Content of the file
            
        Returns:
            Quality analysis report
        """
        self._set_current_task(f"Analyzing {file_path}")
        
        lines = code_content.split('\n')
        lines_of_code = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        
        # Detect code smells
        code_smells = self.detect_code_smells(code_content, file_path)
        
        # Check standards
        violations = self.check_standards(file_path, code_content)
        
        # Generate refactoring suggestions
        refactorings = []
        for smell in code_smells:
            refactoring = self.suggest_refactoring(smell)
            if refactoring:
                refactorings.append(refactoring)
        
        # Calculate complexity (simplified)
        complexity_score = self._calculate_complexity(code_content)
        
        # Calculate overall score
        overall_score = self._calculate_quality_score(
            lines_of_code,
            len(code_smells),
            len(violations),
            complexity_score
        )
        
        report = QualityReport(
            timestamp=datetime.now(),
            file_path=file_path,
            lines_of_code=lines_of_code,
            complexity_score=complexity_score,
            code_smells=code_smells,
            violations=violations,
            refactorings=refactorings,
            overall_score=overall_score
        )
        
        # Store report
        self._quality_reports.append(report)
        if len(self._quality_reports) > self._max_history_size:
            self._quality_reports.pop(0)
        
        # Publish quality issue event if problems found
        if code_smells or violations:
            self.event_bus.publish(Event(
                event_type=EventType.CODE_QUALITY_ISSUE,
                source=self.agent_id,
                payload={
                    'file_path': file_path,
                    'code_smells': len(code_smells),
                    'violations': len(violations),
                    'overall_score': overall_score
                }
            ))
        
        # Publish refactoring opportunities
        if refactorings:
            self.event_bus.publish(Event(
                event_type=EventType.REFACTORING_OPPORTUNITY,
                source=self.agent_id,
                payload={
                    'file_path': file_path,
                    'refactoring_count': len(refactorings),
                    'refactorings': [
                        {
                            'type': r.refactoring_type,
                            'priority': r.priority,
                            'description': r.description
                        }
                        for r in refactorings[:5]  # Top 5
                    ]
                }
            ))
        
        self._set_current_task(None)
        self._update_metrics(task_completed=True)
        
        logger.info(f"Code analysis completed for {file_path}: score {overall_score:.1f}/100")
        
        return report
    
    def detect_code_smells(self, code_content: str, file_path: str) -> List[CodeSmell]:
        """
        Detect code smells in the code.
        
        Args:
            code_content: Code to analyze
            file_path: Path to the file
            
        Returns:
            List of detected code smells
        """
        smells = []
        lines = code_content.split('\n')
        
        # Check for long methods
        current_method = None
        method_start = 0
        method_lines = 0
        
        for i, line in enumerate(lines):
            # Detect method start
            if re.match(r'^\s*(def|function|class)\s+', line):
                # Save previous method if it was long
                if current_method and method_lines > 50:
                    smells.append(CodeSmell(
                        smell_type="long_method",
                        severity="medium",
                        description=f"Method is too long ({method_lines} lines)",
                        location=f"{file_path}:{method_start}",
                        example="\n".join(lines[method_start:method_start+5]),
                        suggestion="Break into smaller, focused methods"
                    ))
                
                current_method = line
                method_start = i + 1
                method_lines = 0
            elif current_method:
                method_lines += 1
        
        # Check for magic numbers
        for i, line in enumerate(lines):
            matches = re.findall(r'\b(\d{3,})\b', line)
            for match in matches:
                # Ignore years and common values
                if match not in ['1000', '1024', '2024', '2025']:
                    smells.append(CodeSmell(
                        smell_type="magic_number",
                        severity="low",
                        description=f"Magic number found: {match}",
                        location=f"{file_path}:{i+1}",
                        example=line.strip(),
                        suggestion="Extract to a named constant"
                    ))
        
        # Check for commented code
        for i, line in enumerate(lines):
            if re.match(r'^\s*#.*(?:def|class|if|for|while)', line):
                smells.append(CodeSmell(
                    smell_type="commented_code",
                    severity="low",
                    description="Commented out code found",
                    location=f"{file_path}:{i+1}",
                    example=line.strip(),
                    suggestion="Remove commented code or document why it's kept"
                ))
        
        # Check for duplicate code (simplified - just look for identical lines)
        line_counts: Dict[str, List[int]] = {}
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and len(stripped) > 20:
                if stripped not in line_counts:
                    line_counts[stripped] = []
                line_counts[stripped].append(i + 1)
        
        for line_text, line_numbers in line_counts.items():
            if len(line_numbers) > 2:
                smells.append(CodeSmell(
                    smell_type="duplicate_code",
                    severity="medium",
                    description=f"Duplicate code found in {len(line_numbers)} locations",
                    location=f"{file_path}:{line_numbers[0]}",
                    example=line_text[:60] + "...",
                    suggestion="Extract to a reusable function or method"
                ))
        
        return smells
    
    def check_standards(self, file_path: str, code_content: str) -> List[Violation]:
        """
        Check code against coding standards.
        
        Args:
            file_path: Path to the file
            code_content: Code to check
            
        Returns:
            List of violations
        """
        violations = []
        lines = code_content.split('\n')
        
        for i, line in enumerate(lines):
            # Check line length
            if len(line) > 120:
                violations.append(Violation(
                    violation_type="line_length",
                    rule="PEP8: Maximum line length is 120 characters",
                    severity="low",
                    description=f"Line exceeds 120 characters ({len(line)} chars)",
                    location=f"{file_path}:{i+1}",
                    fix="Break into multiple lines"
                ))
            
            # Check trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                violations.append(Violation(
                    violation_type="trailing_whitespace",
                    rule="PEP8: No trailing whitespace",
                    severity="low",
                    description="Line has trailing whitespace",
                    location=f"{file_path}:{i+1}",
                    fix="Remove trailing whitespace"
                ))
            
            # Check for tabs (should use spaces)
            if '\t' in line:
                violations.append(Violation(
                    violation_type="tabs_instead_of_spaces",
                    rule="PEP8: Use spaces for indentation",
                    severity="low",
                    description="Line uses tabs instead of spaces",
                    location=f"{file_path}:{i+1}",
                    fix="Replace tabs with 4 spaces"
                ))
        
        return violations
    
    def suggest_refactoring(self, code_smell: CodeSmell) -> Optional[Refactoring]:
        """
        Suggest a refactoring for a code smell.
        
        Args:
            code_smell: The code smell to address
            
        Returns:
            Refactoring suggestion or None
        """
        refactoring_map = {
            'long_method': Refactoring(
                refactoring_type="extract_method",
                priority="medium",
                description="Extract method: Break long method into smaller, focused methods",
                location=code_smell.location,
                code_smell=code_smell,
                estimated_effort="medium",
                benefits=[
                    "Improved readability",
                    "Better testability",
                    "Easier maintenance"
                ]
            ),
            'magic_number': Refactoring(
                refactoring_type="extract_constant",
                priority="low",
                description="Extract constant: Replace magic number with named constant",
                location=code_smell.location,
                code_smell=code_smell,
                estimated_effort="easy",
                benefits=[
                    "Improved readability",
                    "Easier to maintain",
                    "Self-documenting code"
                ]
            ),
            'duplicate_code': Refactoring(
                refactoring_type="extract_function",
                priority="high",
                description="Extract function: Remove duplication by extracting to reusable function",
                location=code_smell.location,
                code_smell=code_smell,
                estimated_effort="medium",
                benefits=[
                    "DRY principle",
                    "Single source of truth",
                    "Easier to maintain"
                ]
            ),
            'commented_code': Refactoring(
                refactoring_type="remove_dead_code",
                priority="low",
                description="Remove dead code: Delete commented code or add explanation",
                location=code_smell.location,
                code_smell=code_smell,
                estimated_effort="easy",
                benefits=[
                    "Cleaner codebase",
                    "Less confusion"
                ]
            ),
        }
        
        return refactoring_map.get(code_smell.smell_type)
    
    def calculate_technical_debt(self) -> TechnicalDebtScore:
        """
        Calculate overall technical debt for the project.
        
        Returns:
            Technical debt metrics
        """
        self._set_current_task("Calculating technical debt")
        
        if not self._quality_reports:
            return TechnicalDebtScore(
                total_debt_hours=0.0,
                debt_ratio=0.0,
                code_smells_count=0,
                violations_count=0,
                high_priority_items=0,
                trend="stable"
            )
        
        # Aggregate across all reports
        total_smells = sum(len(r.code_smells) for r in self._quality_reports)
        total_violations = sum(len(r.violations) for r in self._quality_reports)
        total_lines = sum(r.lines_of_code for r in self._quality_reports)
        
        # Estimate debt hours (rough estimate)
        debt_hours = (
            total_smells * 0.5 +  # 30 min per smell
            total_violations * 0.1  # 6 min per violation
        )
        
        # Calculate debt ratio
        debt_ratio = debt_hours / (total_lines / 100.0) if total_lines > 0 else 0.0
        
        # Count high priority items
        high_priority = sum(
            len([s for s in r.code_smells if s.severity in ['high', 'critical']])
            for r in self._quality_reports
        )
        
        # Determine trend (simplified - compare to previous calculations)
        trend = "stable"
        
        debt_score = TechnicalDebtScore(
            total_debt_hours=debt_hours,
            debt_ratio=debt_ratio,
            code_smells_count=total_smells,
            violations_count=total_violations,
            high_priority_items=high_priority,
            trend=trend
        )
        
        self._set_current_task(None)
        self._update_metrics(task_completed=True)
        
        logger.info(f"Technical debt calculated: {debt_hours:.1f} hours, ratio {debt_ratio:.2f}")
        
        return debt_score
    
    def _calculate_complexity(self, code_content: str) -> float:
        """
        Calculate cyclomatic complexity (simplified).
        
        Args:
            code_content: Code to analyze
            
        Returns:
            Complexity score
        """
        # Count decision points
        decision_keywords = ['if', 'elif', 'else', 'for', 'while', 'and', 'or', 'except']
        complexity = 1  # Base complexity
        
        for keyword in decision_keywords:
            complexity += code_content.count(f' {keyword} ')
            complexity += code_content.count(f'\n{keyword} ')
        
        # Normalize by lines of code
        lines = len([l for l in code_content.split('\n') if l.strip()])
        if lines > 0:
            complexity = complexity / lines * 100
        
        return min(complexity, 100.0)  # Cap at 100
    
    def _calculate_quality_score(self,
                                lines_of_code: int,
                                smell_count: int,
                                violation_count: int,
                                complexity: float) -> float:
        """
        Calculate an overall quality score.
        
        Args:
            lines_of_code: Number of lines
            smell_count: Number of code smells
            violation_count: Number of violations
            complexity: Complexity score
            
        Returns:
            Quality score (0-100, higher is better)
        """
        # Start with perfect score
        score = 100.0
        
        # Deduct for code smells
        if lines_of_code > 0:
            smell_penalty = (smell_count / lines_of_code) * 1000
            score -= min(smell_penalty, 30.0)
        
        # Deduct for violations
        if lines_of_code > 0:
            violation_penalty = (violation_count / lines_of_code) * 500
            score -= min(violation_penalty, 20.0)
        
        # Deduct for complexity
        complexity_penalty = (complexity / 100.0) * 20
        score -= complexity_penalty
        
        return max(score, 0.0)
    
    def get_quality_reports(self, limit: int = 10) -> List[QualityReport]:
        """
        Get recent quality reports.
        
        Args:
            limit: Maximum number of reports to return
            
        Returns:
            List of quality reports
        """
        return self._quality_reports[-limit:]
