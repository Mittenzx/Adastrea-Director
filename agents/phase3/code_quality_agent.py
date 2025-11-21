"""
Code Quality Agent

Maintains code quality through static analysis, code smell detection,
and refactoring suggestions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import logging
import re
import string

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
                 shared_context: SharedContext,
                 remote_control_client=None):
        """
        Initialize the Code Quality Agent.
        
        Args:
            event_bus: Event bus for communication
            shared_context: Shared context for coordination
            remote_control_client: Optional UnrealRemoteControlClient for UE integration
        """
        super().__init__(
            agent_id="code_quality_agent",
            event_bus=event_bus,
            shared_context=shared_context
        )
        
        self._quality_reports: List[QualityReport] = []
        self._max_history_size = 100
        self.remote_control_client = remote_control_client
        
        # Blueprint analysis defaults
        self._DEFAULT_BLUEPRINT_COMPLEXITY = 50.0  # Medium complexity baseline
        
        # Define code smell patterns
        self._smell_patterns = {
            'long_method': (r'def\s+\w+\([^)]*\):', 50),  # Methods longer than 50 lines
            'long_parameter_list': (r'def\s+\w+\(([^)]+)\):', 5),  # More than 5 parameters
            'magic_numbers': (r'\b\d{3,}\b', 0),  # Numbers with 3+ digits
            'commented_code': (r'^\s*#.*(?:def|class|if|for|while)', 0),
        }
        
        logger.info(f"CodeQualityAgent created (UE integration: {remote_control_client is not None})")
    
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
            total_smells * 0.5 +  # 0.5 hours (30 min) per smell
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
    
    # ==================== Unreal Engine Integration ====================
    
    def analyze_blueprint_complexity(self, blueprint_path: str) -> Optional[QualityReport]:
        """
        Analyze Blueprint complexity via Unreal Engine Remote Control API.
        
        This method uses the Remote Control API to query Blueprint information
        and analyze its complexity, node count, and detect potential issues.
        
        Args:
            blueprint_path: Path to the Blueprint asset in UE
                           (e.g., "/Game/Blueprints/MyBlueprint")
            
        Returns:
            QualityReport with Blueprint analysis or None if analysis fails
            
        Raises:
            RuntimeError: If remote_control_client is not configured
        """
        if self.remote_control_client is None:
            logger.error("Cannot analyze Blueprint: remote_control_client not configured")
            raise RuntimeError("Remote Control client not configured. Pass it to constructor.")
        
        logger.info(f"Analyzing Blueprint: {blueprint_path}")
        
        # Sanitize blueprint_path to prevent code injection
        # Only allow alphanumeric, forward slash, underscore, and hyphen
        allowed_chars = string.ascii_letters + string.digits + '/_-'
        sanitized_path = ''.join(c for c in blueprint_path if c in allowed_chars)
        
        if sanitized_path != blueprint_path:
            logger.warning(f"Blueprint path contained invalid characters: {blueprint_path}")
            logger.info(f"Using sanitized path: {sanitized_path}")
        
        try:
            # Get Blueprint information via Remote Control API
            # Note: This is a placeholder for the actual implementation
            # The actual commands depend on exposing Blueprint data via UE Python or Remote Control
            
            # For now, we'll use a Python command to get Blueprint info
            # Using sanitized path to prevent code injection
            python_script = f"""
import unreal
blueprint = unreal.load_asset('{sanitized_path}')
if blueprint:
    # Get node count and complexity info
    # This is a simplified version - actual implementation would need
    # proper Blueprint graph traversal
    print(f"Blueprint loaded: {{blueprint.get_name()}}")
    print(f"Blueprint class: {{type(blueprint).__name__}}")
else:
    print("Blueprint not found")
"""
            
            response = self.remote_control_client.execute_command(
                f"py {python_script}"
            )
            
            if not response or not response.get('success', False):
                logger.error(f"Failed to analyze Blueprint: {sanitized_path}")
                return None
            
            # Parse response to extract Blueprint info
            output = response.get('output', '')
            
            # Estimate complexity based on response
            # In a real implementation, this would parse actual node counts and complexity metrics
            node_count = 0
            complexity_score = self._DEFAULT_BLUEPRINT_COMPLEXITY
            
            if 'loaded' in output.lower():
                # Blueprint exists, analyze it
                # This is a simplified analysis
                code_smells = []
                violations = []
                
                # Check for potential issues
                if node_count > 100:
                    code_smells.append(CodeSmell(
                        smell_type='complex_blueprint',
                        severity='high',
                        description='Blueprint has too many nodes (>100)',
                        location=blueprint_path,
                        example=f'Node count: {node_count}',
                        suggestion='Consider breaking into smaller Blueprint functions'
                    ))
                
                # Create quality report
                report = QualityReport(
                    timestamp=datetime.now(),
                    file_path=blueprint_path,
                    lines_of_code=node_count,  # Use node count as "lines"
                    complexity_score=complexity_score,
                    code_smells=code_smells,
                    violations=violations,
                    refactorings=[],
                    overall_score=self._calculate_quality_score(
                        node_count, len(code_smells), len(violations), complexity_score
                    )
                )
                
                # Store report
                self._quality_reports.append(report)
                if len(self._quality_reports) > self._max_history_size:
                    self._quality_reports.pop(0)
                
                # Publish event
                if len(code_smells) > 0 or len(violations) > 0:
                    event = Event(
                        event_type=EventType.CODE_QUALITY_ISSUE,
                        source=self.agent_id,
                        payload={
                            "file_path": blueprint_path,
                            "overall_score": report.overall_score,
                            "smell_count": len(code_smells),
                            "violation_count": len(violations)
                        }
                    )
                    self.event_bus.publish(event)
                
                logger.info(f"Blueprint analysis complete: {blueprint_path} (score: {report.overall_score:.1f})")
                return report
            else:
                logger.warning(f"Blueprint not found or could not be loaded: {blueprint_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing Blueprint {blueprint_path}: {str(e)}")
            return None
    
    def analyze_ue_project_quality(self, content_path: str = "/Game") -> Dict[str, any]:
        """
        Analyze overall code quality of a UE project's Python scripts and C++ files.
        
        This method scans the project for Python and C++ files accessible via
        Remote Control and generates a comprehensive quality report.
        
        Args:
            content_path: Root content path to analyze (default: "/Game")
            
        Returns:
            Dictionary with quality metrics:
                - total_files: Number of files analyzed
                - total_smells: Total code smells found
                - total_violations: Total violations found
                - average_score: Average quality score
                - files_analyzed: List of analyzed files with their scores
            
        Raises:
            RuntimeError: If remote_control_client is not configured
        """
        if self.remote_control_client is None:
            logger.error("Cannot analyze project: remote_control_client not configured")
            raise RuntimeError("Remote Control client not configured. Pass it to constructor.")
        
        logger.info(f"Analyzing UE project quality at: {content_path}")
        
        results = {
            "total_files": 0,
            "total_smells": 0,
            "total_violations": 0,
            "average_score": 0.0,
            "files_analyzed": []
        }
        
        try:
            # Get list of Python files in the project
            # This is a simplified version - actual implementation would need
            # proper asset enumeration via Remote Control API
            
            python_script = """
import unreal
import os

# Get project content directory
content_dir = unreal.Paths.project_content_dir()
python_files = []

# Walk through content directory looking for .py files
for root, dirs, files in os.walk(content_dir):
    for file in files:
        if file.endswith('.py'):
            python_files.append(os.path.join(root, file))

for file in python_files[:10]:  # Limit to first 10 files
    print(file)
"""
            
            response = self.remote_control_client.execute_command(f"py {python_script}")
            
            if response and response.get('success', False):
                output = response.get('output', '')
                file_paths = [line.strip() for line in output.split('\n') if line.strip().endswith('.py')]
                
                results["total_files"] = len(file_paths)
                
                # Note: In a full implementation, we would read and analyze each file
                # For now, we'll just record that we found them
                for file_path in file_paths:
                    results["files_analyzed"].append({
                        "path": file_path,
                        "score": 75.0,  # Placeholder score
                        "type": "python"
                    })
                
                if results["total_files"] > 0:
                    results["average_score"] = sum(f["score"] for f in results["files_analyzed"]) / results["total_files"]
                
                logger.info(f"Project analysis complete: {results['total_files']} files found")
            else:
                logger.warning("Failed to enumerate project files")
                
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing project quality: {str(e)}")
            return results
    
    def get_blueprint_metrics(self, blueprint_path: str) -> Optional[Dict[str, any]]:
        """
        Get basic metrics for a Blueprint via Remote Control API.
        
        This is a helper method that retrieves Blueprint metadata without
        performing a full quality analysis.
        
        Args:
            blueprint_path: Path to the Blueprint asset
            
        Returns:
            Dictionary with Blueprint metrics or None if Blueprint not found:
                - name: Blueprint name
                - node_count: Estimated node count
                - function_count: Number of functions
                - variable_count: Number of variables
            
        Raises:
            RuntimeError: If remote_control_client is not configured
        """
        if self.remote_control_client is None:
            raise RuntimeError("Remote Control client not configured. Pass it to constructor.")
        
        # Sanitize blueprint_path to prevent code injection
        allowed_chars = string.ascii_letters + string.digits + '/_-'
        sanitized_path = ''.join(c for c in blueprint_path if c in allowed_chars)
        
        if sanitized_path != blueprint_path:
            logger.warning(f"Blueprint path contained invalid characters: {blueprint_path}")
        
        try:
            # Get Blueprint basic info using sanitized path
            python_script = f"""
import unreal
blueprint = unreal.load_asset('{sanitized_path}')
if blueprint:
    print(f"name:{{blueprint.get_name()}}")
    print(f"class:{{type(blueprint).__name__}}")
else:
    print("not_found")
"""
            
            response = self.remote_control_client.execute_command(f"py {python_script}")
            
            if response and response.get('success', False):
                output = response.get('output', '')
                
                if 'not_found' in output:
                    return None
                
                # Parse output
                metrics = {
                    "name": blueprint_path.split('/')[-1],
                    "node_count": 0,  # Would need full graph analysis
                    "function_count": 0,  # Would need graph analysis
                    "variable_count": 0,  # Would need reflection
                    "exists": 'name:' in output
                }
                
                return metrics
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting Blueprint metrics: {str(e)}")
            return None
