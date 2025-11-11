"""
Goal Analysis Agent

Responsible for parsing and understanding high-level development goals.
"""

import uuid
from typing import List, Dict, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from agents.models import Goal, GoalType, Constraint, ProjectScope, TaskPriority


class GoalParsingOutput(BaseModel):
    """Pydantic model for structured goal parsing output."""
    goal_type: str = Field(description="Type of goal: feature, bug_fix, optimization, refactoring, documentation, testing, infrastructure, or other")
    key_objectives: List[str] = Field(description="List of key objectives extracted from the goal")
    constraints: List[Dict[str, str]] = Field(description="List of constraints with 'description' and 'type' fields")
    priority: str = Field(description="Priority level: critical, high, medium, or low")
    affected_systems: List[str] = Field(description="List of system areas affected (e.g., UI, combat, networking)")
    complexity: str = Field(description="Estimated complexity: low, medium, high, or very_high")


class GoalAnalysisAgent:
    """
    Agent responsible for analyzing and understanding development goals.
    
    This agent parses natural language goal descriptions and extracts structured
    information including objectives, constraints, classification, and scope.
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.3,
    ):
        """
        Initialize the Goal Analysis Agent.
        
        Args:
            model_name: Name of the OpenAI model to use
            temperature: Temperature for response generation (lower = more focused)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
        )
        
        # Setup output parser
        self.parser = PydanticOutputParser(pydantic_object=GoalParsingOutput)
        
        # Create prompt template
        self.prompt_template = PromptTemplate(
            template="""You are an expert software development planning assistant specializing in game development with Unreal Engine.

Analyze the following development goal and extract structured information:

Goal Description:
{goal_description}

Extract the following information:
1. Goal Type: Classify as one of: feature, bug_fix, optimization, refactoring, documentation, testing, infrastructure, or other
2. Key Objectives: List the main objectives (3-5 bullet points)
3. Constraints: Identify any constraints or requirements (technical, resource, time, etc.)
4. Priority: Assess priority as critical, high, medium, or low
5. Affected Systems: Identify which game systems or areas are affected (e.g., UI, combat, player movement, inventory)
6. Complexity: Estimate overall complexity as low, medium, high, or very_high

Consider the context of game development in Unreal Engine when analyzing the goal.

{format_instructions}

Provide your analysis in the specified JSON format.
""",
            input_variables=["goal_description"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
    
    def parse_goal(self, goal_description: str, context: Dict[str, Any] = None) -> Goal:
        """
        Parse a natural language goal description into a structured Goal object.
        
        Args:
            goal_description: Natural language description of the goal
            context: Optional context dictionary (project info, current state, etc.)
        
        Returns:
            Goal object with extracted information
        """
        # Generate analysis using LLM
        chain = self.prompt_template | self.llm | self.parser
        result = chain.invoke({"goal_description": goal_description})
        
        # Convert to Goal object
        goal_id = str(uuid.uuid4())[:8]
        
        # Parse goal type
        goal_type = GoalType.OTHER
        try:
            goal_type = GoalType(result.goal_type.lower())
        except (ValueError, AttributeError):
            # Default to OTHER if not recognized
            pass
        
        # Parse priority
        priority = TaskPriority.MEDIUM
        try:
            priority = TaskPriority(result.priority.lower())
        except (ValueError, AttributeError):
            # If priority value is not recognized or missing, default to MEDIUM
            pass
        
        # Create constraints
        constraints = []
        for constraint_dict in result.constraints:
            constraints.append(Constraint(
                description=constraint_dict.get("description", ""),
                constraint_type=constraint_dict.get("type", "general"),
                is_hard=constraint_dict.get("type") in ["technical", "dependency"]
            ))
        
        # Create project scope
        scope = ProjectScope(
            systems=result.affected_systems,
            estimated_complexity=result.complexity
        )
        
        # Create Goal object
        goal = Goal(
            id=goal_id,
            description=goal_description,
            goal_type=goal_type,
            constraints=constraints,
            scope=scope,
            priority=priority,
            metadata={
                "key_objectives": result.key_objectives,
                "parsed_at": datetime.now().isoformat(),
            }
        )
        
        return goal
    
    def identify_constraints(self, goal: Goal) -> List[Constraint]:
        """
        Identify additional constraints for a goal based on its type and scope.
        
        Args:
            goal: Goal object to analyze
        
        Returns:
            List of identified constraints
        """
        # Return existing constraints (could be extended with additional analysis)
        return goal.constraints
    
    def classify_goal(self, goal: Goal) -> GoalType:
        """
        Classify or reclassify a goal's type.
        
        Args:
            goal: Goal object to classify
        
        Returns:
            GoalType classification
        """
        return goal.goal_type
    
    def determine_scope(self, goal: Goal, project_structure: Dict[str, Any] = None) -> ProjectScope:
        """
        Determine or refine the project scope for a goal.
        
        Args:
            goal: Goal object to analyze
            project_structure: Optional dictionary containing project file structure
        
        Returns:
            ProjectScope object with identified scope
        """
        if project_structure:
            # If project structure is provided, we could refine the scope
            # by identifying specific files and directories
            # This is a placeholder for more sophisticated analysis
            pass
        
        return goal.scope if goal.scope else ProjectScope()
    
    def analyze_goal_feasibility(self, goal: Goal) -> Dict[str, Any]:
        """
        Analyze the feasibility of a goal.
        
        Args:
            goal: Goal object to analyze
        
        Returns:
            Dictionary with feasibility analysis
        """
        # Simple heuristic-based feasibility analysis
        complexity_score = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "very_high": 4,
        }.get(goal.scope.estimated_complexity if goal.scope else "medium", 2)
        
        constraint_count = len(goal.constraints)
        hard_constraints = sum(1 for c in goal.constraints if c.is_hard)
        
        # Calculate feasibility score (0-100)
        base_score = 100
        complexity_penalty = complexity_score * 10
        constraint_penalty = constraint_count * 5
        hard_constraint_penalty = hard_constraints * 10
        
        feasibility_score = max(0, base_score - complexity_penalty - constraint_penalty - hard_constraint_penalty)
        
        # Determine risk level
        if feasibility_score >= 75:
            risk_level = "low"
        elif feasibility_score >= 50:
            risk_level = "medium"
        elif feasibility_score >= 25:
            risk_level = "high"
        else:
            risk_level = "very_high"
        
        return {
            "feasibility_score": feasibility_score,
            "risk_level": risk_level,
            "complexity": goal.scope.estimated_complexity if goal.scope else "unknown",
            "constraint_count": constraint_count,
            "hard_constraints": hard_constraints,
            "recommendations": self._generate_recommendations(goal, risk_level),
        }
    
    def _generate_recommendations(self, goal: Goal, risk_level: str) -> List[str]:
        """Generate recommendations based on goal analysis."""
        recommendations = []
        
        if risk_level in ["high", "very_high"]:
            recommendations.append("Consider breaking this goal into smaller, more manageable goals")
        
        if goal.scope and goal.scope.estimated_complexity in ["high", "very_high"]:
            recommendations.append("Plan for adequate testing and code review")
            recommendations.append("Consider prototyping critical components first")
        
        hard_constraints = [c for c in goal.constraints if c.is_hard]
        if len(hard_constraints) > 3:
            recommendations.append("Review hard constraints to identify if any can be relaxed")
        
        if goal.goal_type == GoalType.FEATURE:
            recommendations.append("Create user stories or acceptance criteria")
            recommendations.append("Consider performance implications early")
        
        return recommendations
