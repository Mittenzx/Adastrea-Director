"""
Tests for Phase 2 planning agents.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from agents.goal_analysis_agent import GoalAnalysisAgent, GoalParsingOutput
from agents.task_decomposition_agent import TaskDecompositionAgent, TaskDecompositionOutput
from agents.code_generation_agent import CodeGenerationAgent, CodeSuggestionOutput
from agents.models import (
    Goal,
    GoalType,
    Task,
    TaskPriority,
    TaskStatus,
    Constraint,
    ProjectScope,
    Duration,
)


class TestGoalAnalysisAgent:
    """Tests for GoalAnalysisAgent."""
    
    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response for goal parsing."""
        return GoalParsingOutput(
            goal_type="feature",
            key_objectives=[
                "Implement player movement",
                "Add collision detection",
                "Create input handling"
            ],
            constraints=[
                {"description": "Must work with existing input system", "type": "technical"},
                {"description": "Performance target: 60 FPS", "type": "resource"}
            ],
            priority="high",
            affected_systems=["player", "physics", "input"],
            complexity="medium"
        )
    
    @pytest.fixture
    def agent(self):
        """Create GoalAnalysisAgent with mocked LLM."""
        with patch('agents.goal_analysis_agent.ChatOpenAI'):
            return GoalAnalysisAgent(model_name="gpt-4", temperature=0.3)
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.model_name == "gpt-4"
        assert agent.temperature == 0.3
        assert agent.llm is not None
    
    @pytest.mark.skip(reason="Requires live LLM API call - tested in integration tests")
    def test_parse_goal(self, agent, mock_llm_response):
        """Test goal parsing - requires live API."""
        pass
    
    def test_identify_constraints(self, agent):
        """Test constraint identification."""
        constraint = Constraint("Test constraint", "technical")
        goal = Goal(
            id="test-1",
            description="Test goal",
            goal_type=GoalType.FEATURE,
            constraints=[constraint]
        )
        
        constraints = agent.identify_constraints(goal)
        assert len(constraints) == 1
        assert constraints[0].description == "Test constraint"
    
    def test_classify_goal(self, agent):
        """Test goal classification."""
        goal = Goal(
            id="test-1",
            description="Test goal",
            goal_type=GoalType.BUG_FIX
        )
        
        goal_type = agent.classify_goal(goal)
        assert goal_type == GoalType.BUG_FIX
    
    def test_determine_scope(self, agent):
        """Test scope determination."""
        scope = ProjectScope(systems=["UI", "combat"])
        goal = Goal(
            id="test-1",
            description="Test goal",
            goal_type=GoalType.FEATURE,
            scope=scope
        )
        
        determined_scope = agent.determine_scope(goal)
        assert determined_scope == scope
        assert "UI" in determined_scope.systems
    
    def test_analyze_goal_feasibility_high_score(self, agent):
        """Test feasibility analysis for simple goal."""
        goal = Goal(
            id="test-1",
            description="Simple documentation update",
            goal_type=GoalType.DOCUMENTATION,
            scope=ProjectScope(estimated_complexity="low"),
            constraints=[]
        )
        
        analysis = agent.analyze_goal_feasibility(goal)
        
        assert "feasibility_score" in analysis
        assert "risk_level" in analysis
        assert analysis["feasibility_score"] >= 75
        assert analysis["risk_level"] == "low"
    
    def test_analyze_goal_feasibility_low_score(self, agent):
        """Test feasibility analysis for complex goal."""
        constraints = [
            Constraint("Hard constraint 1", "technical", is_hard=True),
            Constraint("Hard constraint 2", "technical", is_hard=True),
            Constraint("Hard constraint 3", "technical", is_hard=True),
        ]
        goal = Goal(
            id="test-1",
            description="Complex system overhaul",
            goal_type=GoalType.REFACTORING,
            scope=ProjectScope(estimated_complexity="very_high"),
            constraints=constraints
        )
        
        analysis = agent.analyze_goal_feasibility(goal)
        
        assert analysis["feasibility_score"] < 75
        assert analysis["risk_level"] in ["high", "very_high"]
        assert len(analysis["recommendations"]) > 0


class TestTaskDecompositionAgent:
    """Tests for TaskDecompositionAgent."""
    
    @pytest.fixture
    def mock_task_output(self):
        """Mock LLM response for task decomposition."""
        return TaskDecompositionOutput(
            tasks=[
                {
                    "description": "Set up project structure",
                    "priority": "high",
                    "estimated_hours": 2.0,
                    "dependencies": [],
                    "files_to_create": ["main.py"],
                },
                {
                    "description": "Implement core functionality",
                    "priority": "high",
                    "estimated_hours": 6.0,
                    "dependencies": ["Set up project structure"],
                    "files_to_modify": ["main.py"],
                },
                {
                    "description": "Write tests",
                    "priority": "medium",
                    "estimated_hours": 3.0,
                    "dependencies": ["Implement core functionality"],
                    "files_to_create": ["test_main.py"],
                },
            ]
        )
    
    @pytest.fixture
    def agent(self):
        """Create TaskDecompositionAgent with mocked LLM."""
        with patch('agents.task_decomposition_agent.ChatOpenAI'):
            return TaskDecompositionAgent(model_name="gpt-4", temperature=0.3)
    
    @pytest.fixture
    def sample_goal(self):
        """Create a sample goal."""
        return Goal(
            id="goal-1",
            description="Build a new feature",
            goal_type=GoalType.FEATURE,
            scope=ProjectScope(estimated_complexity="medium"),
            metadata={"key_objectives": ["Objective 1", "Objective 2"]}
        )
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.model_name == "gpt-4"
        assert agent.temperature == 0.3
    
    @pytest.mark.skip(reason="Requires live LLM API call - tested in integration tests")
    def test_decompose_goal(self, agent, sample_goal, mock_task_output):
        """Test goal decomposition - requires live API."""
        pass
    
    def test_estimate_effort_existing(self, agent):
        """Test effort estimation for task with existing estimate."""
        duration = Duration(hours=5.0)
        task = Task(
            id="task-1",
            description="Test task",
            goal_id="goal-1",
            estimated_duration=duration
        )
        
        estimated = agent.estimate_effort(task)
        assert estimated.hours == 5.0
    
    def test_estimate_effort_no_estimate(self, agent):
        """Test effort estimation for task without estimate."""
        task = Task(
            id="task-1",
            description="Test task",
            goal_id="goal-1",
        )
        
        estimated = agent.estimate_effort(task)
        assert estimated.hours > 0
        assert estimated.confidence == 0.5
    
    def test_identify_dependencies(self, agent):
        """Test dependency identification."""
        task1 = Task(id="task-1", description="Task 1", goal_id="goal-1")
        task2 = Task(id="task-2", description="Task 2", goal_id="goal-1", dependencies=["task-1"])
        
        dep_graph = agent.identify_dependencies([task1, task2])
        
        assert len(dep_graph.tasks) == 2
        assert "task-1" in dep_graph.adjacency_list
        assert "task-2" in dep_graph.adjacency_list
    
    def test_prioritize_tasks(self, agent):
        """Test task prioritization."""
        task1 = Task(
            id="task-1",
            description="Low priority",
            goal_id="goal-1",
            priority=TaskPriority.LOW,
            dependencies=[]
        )
        task2 = Task(
            id="task-2",
            description="High priority",
            goal_id="goal-1",
            priority=TaskPriority.HIGH,
            dependencies=[]
        )
        task3 = Task(
            id="task-3",
            description="Depends on task 2",
            goal_id="goal-1",
            priority=TaskPriority.HIGH,
            dependencies=["task-2"]
        )
        
        prioritized = agent.prioritize_tasks([task1, task2, task3])
        
        # Check that task 2 comes before task 3 (dependency order)
        task2_idx = next(i for i, t in enumerate(prioritized) if t.id == "task-2")
        task3_idx = next(i for i, t in enumerate(prioritized) if t.id == "task-3")
        assert task2_idx < task3_idx
        
        # All tasks should be present
        assert len(prioritized) == 3
    
    def test_refine_task_breakdown_small_task(self, agent):
        """Test task refinement for small task."""
        task = Task(
            id="task-1",
            description="Small task",
            goal_id="goal-1",
            estimated_duration=Duration(hours=4.0)
        )
        
        refined = agent.refine_task_breakdown(task, max_hours=8.0)
        
        # Should return original task unchanged
        assert len(refined) == 1
        assert refined[0] == task
    
    def test_refine_task_breakdown_large_task(self, agent):
        """Test task refinement for large task."""
        task = Task(
            id="task-1",
            description="Large task",
            goal_id="goal-1",
            estimated_duration=Duration(hours=20.0)
        )
        
        refined = agent.refine_task_breakdown(task, max_hours=8.0)
        
        # Should break into multiple subtasks
        assert len(refined) > 1
        total_hours = sum(t.estimated_duration.hours for t in refined)
        assert abs(total_hours - 20.0) < 1.0  # Allow small rounding difference


class TestCodeGenerationAgent:
    """Tests for CodeGenerationAgent."""
    
    @pytest.fixture
    def mock_code_output(self):
        """Mock LLM response for code generation."""
        return CodeSuggestionOutput(
            implementation_approaches=[
                {
                    "name": "Direct Implementation",
                    "description": "Straightforward approach",
                    "pros": ["Simple", "Fast"],
                    "cons": ["Less flexible"],
                    "complexity": "low",
                    "code_example": "def example(): pass"
                },
                {
                    "name": "Advanced Implementation",
                    "description": "More sophisticated approach",
                    "pros": ["Flexible", "Scalable"],
                    "cons": ["Complex"],
                    "complexity": "high",
                    "code_example": "class Example: pass"
                }
            ],
            file_modifications=[
                {
                    "file_path": "main.py",
                    "modification_type": "update",
                    "description": "Add new function",
                    "code_snippet": "def new_func(): pass"
                }
            ],
            required_libraries=["numpy", "pandas"]
        )
    
    @pytest.fixture
    def agent(self):
        """Create CodeGenerationAgent with mocked LLM."""
        with patch('agents.code_generation_agent.ChatOpenAI'):
            return CodeGenerationAgent(model_name="gpt-4", temperature=0.2)
    
    @pytest.fixture
    def sample_task(self):
        """Create a sample task."""
        return Task(
            id="task-1",
            description="Implement data processing module",
            goal_id="goal-1",
            files_to_create=["processor.py"],
            files_to_modify=["__init__.py"]
        )
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.model_name == "gpt-4"
        assert agent.temperature == 0.2
    
    @pytest.mark.skip(reason="Requires live LLM API call - tested in integration tests")
    def test_suggest_implementation(self, agent, sample_task, mock_code_output):
        """Test implementation suggestion generation - requires live API."""
        pass
    
    def test_generate_boilerplate(self, agent, sample_task):
        """Test boilerplate generation."""
        expected_code = "# Boilerplate code\ndef main():\n    pass"
        mock_response = Mock()
        mock_response.content = expected_code
        
        with patch.object(agent, 'boilerplate_prompt') as mock_template:
            mock_chain = Mock()
            mock_chain.invoke.return_value = mock_response
            mock_template.__or__ = Mock(return_value=mock_chain)
            agent.llm = Mock()
            
            boilerplate = agent.generate_boilerplate(sample_task, language="python")
            
            assert isinstance(boilerplate, str)
            assert boilerplate == expected_code
    
    @pytest.mark.skip(reason="Requires live LLM API call - tested in integration tests")
    def test_propose_modifications(self, agent, sample_task, mock_code_output):
        """Test file modification proposals - requires live API."""
        pass
    
    def test_validate_code_syntax_valid_python(self, agent):
        """Test code syntax validation for valid Python."""
        code = """
def hello():
    print("Hello, World!")
    return True
"""
        result = agent.validate_code_syntax(code, language="python")
        
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_code_syntax_invalid_python(self, agent):
        """Test code syntax validation for invalid Python."""
        code = """
def hello(
    print("Missing closing paren")
"""
        result = agent.validate_code_syntax(code, language="python")
        
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_code_syntax_warnings(self, agent):
        """Test code syntax validation warnings."""
        # Very long code
        code = "\n".join(["# Line " + str(i) for i in range(600)])
        result = agent.validate_code_syntax(code, language="python")
        
        assert len(result["warnings"]) > 0
        assert any("long" in w.lower() for w in result["warnings"])
    
    def test_generate_tests(self, agent, sample_task):
        """Test test code generation."""
        mock_response = Mock()
        mock_response.content = """
import pytest

def test_processor():
    assert True
"""
        
        with patch('agents.code_generation_agent.PromptTemplate') as mock_template:
            mock_chain = Mock()
            mock_chain.invoke.return_value = mock_response
            mock_template.return_value.__or__ = Mock(return_value=mock_chain)
            
            # Manually set up the chain
            agent.llm = Mock()
            test_code = agent.generate_tests(sample_task, test_framework="pytest")
            
            # Since we're mocking heavily, just check it returns a string
            assert isinstance(test_code, str)
