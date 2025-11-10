#!/usr/bin/env python3
"""
Goal Analysis Agent for Phase 2 Planning

This agent is responsible for parsing and understanding high-level development goals.
It extracts key objectives, identifies constraints, classifies goal types, and 
determines project scope.
"""

import re
from typing import List, Dict, Any
from planning_models import (
    Goal, GoalType, Constraint, ConstraintType, 
    ProjectScope, TaskPriority
)
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


class GoalAnalysisAgent:
    """Agent responsible for parsing and understanding development goals."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.3):
        """
        Initialize the goal analysis agent.
        
        Args:
            model_name: Name of the OpenAI model to use
            temperature: Temperature for response generation (lower for more focused)
        """
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self._initialize_chains()
    
    def _initialize_chains(self):
        """Initialize LLM chains for different analysis tasks."""
        
        # Chain for parsing and understanding goals
        parse_template = """You are an expert software architect analyzing development goals.

Given the following goal description, extract the following information:

Goal Description: {goal_description}

Provide your analysis in the following format:

GOAL TYPE: [feature/bug_fix/optimization/refactoring/documentation/testing/infrastructure]
PRIORITY: [critical/high/medium/low]
KEY OBJECTIVES: 
- [List key objectives, one per line]

CONSTRAINTS:
- [List constraints, format: TYPE - description (severity: low/medium/high)]
  Types: time, resource, technical, dependency, quality

AFFECTED AREAS:
- [List affected code areas/modules/systems]

COMPLEXITY: [low/medium/high]
REQUIRES NEW DEPENDENCIES: [yes/no]
BREAKING CHANGES: [yes/no]
DOCUMENTATION NEEDS:
- [List documentation that needs to be created/updated]

Be specific and practical in your analysis."""

        self.parse_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=parse_template,
                input_variables=["goal_description"]
            )
        )
    
    def parse_goal(self, goal_description: str) -> Goal:
        """
        Parse a natural language goal description into a structured Goal object.
        
        Args:
            goal_description: Natural language description of the goal
            
        Returns:
            Structured Goal object
        """
        # Get LLM analysis
        response = self.parse_chain.invoke({"goal_description": goal_description})
        analysis_text = response["text"]
        
        # Parse the LLM response
        goal = Goal(description=goal_description)
        
        # Extract goal type
        goal_type_match = re.search(r'GOAL TYPE:\s*\[?(\w+)', analysis_text, re.IGNORECASE)
        if goal_type_match:
            try:
                goal.goal_type = GoalType(goal_type_match.group(1).lower())
            except ValueError:
                goal.goal_type = GoalType.FEATURE
        
        # Extract priority
        priority_match = re.search(r'PRIORITY:\s*\[?(\w+)', analysis_text, re.IGNORECASE)
        if priority_match:
            try:
                goal.priority = TaskPriority(priority_match.group(1).upper())
            except ValueError:
                goal.priority = TaskPriority.MEDIUM
        
        # Extract constraints
        constraints_section = re.search(
            r'CONSTRAINTS:(.*?)(?=AFFECTED AREAS:|$)', 
            analysis_text, 
            re.IGNORECASE | re.DOTALL
        )
        if constraints_section:
            constraint_lines = constraints_section.group(1).strip().split('\n')
            for line in constraint_lines:
                line = line.strip('- ').strip()
                if line and not line.startswith('['):
                    constraint = self._parse_constraint_line(line)
                    if constraint:
                        goal.constraints.append(constraint)
        
        # Extract scope information
        scope = ProjectScope()
        
        # Affected areas
        areas_section = re.search(
            r'AFFECTED AREAS:(.*?)(?=COMPLEXITY:|$)', 
            analysis_text, 
            re.IGNORECASE | re.DOTALL
        )
        if areas_section:
            area_lines = areas_section.group(1).strip().split('\n')
            for line in area_lines:
                line = line.strip('- ').strip()
                if line and not line.startswith('['):
                    scope.affected_areas.append(line)
        
        # Complexity
        complexity_match = re.search(r'COMPLEXITY:\s*\[?(\w+)', analysis_text, re.IGNORECASE)
        if complexity_match:
            scope.estimated_complexity = complexity_match.group(1).lower()
        
        # New dependencies
        deps_match = re.search(r'REQUIRES NEW DEPENDENCIES:\s*\[?(yes|no)', analysis_text, re.IGNORECASE)
        if deps_match:
            scope.requires_new_dependencies = deps_match.group(1).lower() == 'yes'
        
        # Breaking changes
        breaking_match = re.search(r'BREAKING CHANGES:\s*\[?(yes|no)', analysis_text, re.IGNORECASE)
        if breaking_match:
            scope.breaking_changes = breaking_match.group(1).lower() == 'yes'
        
        # Documentation needs
        docs_section = re.search(
            r'DOCUMENTATION NEEDS:(.*?)$', 
            analysis_text, 
            re.IGNORECASE | re.DOTALL
        )
        if docs_section:
            doc_lines = docs_section.group(1).strip().split('\n')
            for line in doc_lines:
                line = line.strip('- ').strip()
                if line and not line.startswith('['):
                    scope.documentation_needs.append(line)
        
        goal.scope = scope
        goal.metadata['raw_analysis'] = analysis_text
        
        return goal
    
    def _parse_constraint_line(self, line: str) -> Constraint:
        """
        Parse a constraint line from the LLM response.
        
        Args:
            line: Constraint line in format "TYPE - description (severity: level)"
            
        Returns:
            Constraint object or None if parsing fails
        """
        # Try to match: TYPE - description (severity: level)
        match = re.match(
            r'(\w+)\s*-\s*(.*?)\s*\(severity:\s*(\w+)\)',
            line,
            re.IGNORECASE
        )
        
        if match:
            constraint_type_str = match.group(1).lower()
            description = match.group(2).strip()
            severity = match.group(3).lower()
            
            try:
                constraint_type = ConstraintType(constraint_type_str)
            except ValueError:
                constraint_type = ConstraintType.TECHNICAL
            
            return Constraint(
                constraint_type=constraint_type,
                description=description,
                severity=severity
            )
        
        # Fallback: create a general technical constraint
        return Constraint(
            constraint_type=ConstraintType.TECHNICAL,
            description=line,
            severity="medium"
        )
    
    def identify_constraints(self, goal: Goal) -> List[Constraint]:
        """
        Identify constraints for a given goal.
        
        Args:
            goal: The goal to analyze
            
        Returns:
            List of identified constraints
        """
        # If goal already has constraints from parsing, return them
        if goal.constraints:
            return goal.constraints
        
        # Otherwise, reparse the goal to extract constraints
        reparsed_goal = self.parse_goal(goal.description)
        return reparsed_goal.constraints
    
    def classify_goal(self, goal: Goal) -> GoalType:
        """
        Classify the type of a goal.
        
        Args:
            goal: The goal to classify
            
        Returns:
            GoalType enum value
        """
        # If goal already has a type from parsing, return it
        if goal.goal_type != GoalType.FEATURE:  # FEATURE is default
            return goal.goal_type
        
        # Use simple keyword-based classification as fallback
        description_lower = goal.description.lower()
        
        if any(word in description_lower for word in ['fix', 'bug', 'error', 'issue']):
            return GoalType.BUG_FIX
        elif any(word in description_lower for word in ['optimize', 'performance', 'speed', 'faster']):
            return GoalType.OPTIMIZATION
        elif any(word in description_lower for word in ['refactor', 'restructure', 'cleanup', 'reorganize']):
            return GoalType.REFACTORING
        elif any(word in description_lower for word in ['document', 'documentation', 'readme', 'guide']):
            return GoalType.DOCUMENTATION
        elif any(word in description_lower for word in ['test', 'testing', 'coverage', 'unit test']):
            return GoalType.TESTING
        elif any(word in description_lower for word in ['infrastructure', 'ci/cd', 'deploy', 'pipeline']):
            return GoalType.INFRASTRUCTURE
        else:
            return GoalType.FEATURE
    
    def determine_scope(self, goal: Goal) -> ProjectScope:
        """
        Determine the scope of a goal's impact on the project.
        
        Args:
            goal: The goal to analyze
            
        Returns:
            ProjectScope object
        """
        # If goal already has scope from parsing, return it
        if goal.scope:
            return goal.scope
        
        # Otherwise, reparse the goal to extract scope
        reparsed_goal = self.parse_goal(goal.description)
        return reparsed_goal.scope if reparsed_goal.scope else ProjectScope()
