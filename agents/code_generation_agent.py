"""
Code Generation Agent

Responsible for generating code suggestions and examples for tasks.
"""

from typing import List, Dict, Any, Optional
import logging

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from agents.models import Task, Implementation, FileModification, Duration
from llm_config import get_llm

# Import validation components (optional, will be checked at runtime)
try:
    from validation.schema_manager import SchemaManager
    from validation.yaml_validator import YAMLValidator
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

logger = logging.getLogger(__name__)


class CodeSuggestionOutput(BaseModel):
    """Pydantic model for structured code generation output."""
    implementation_approaches: List[Dict[str, Any]] = Field(
        description="List of implementation approaches with name, description, pros, cons, complexity, and code_example"
    )
    file_modifications: List[Dict[str, Any]] = Field(
        description="List of file modifications with file_path, modification_type, description, and code_snippet"
    )
    required_libraries: List[str] = Field(description="List of required libraries or dependencies")


class CodeGenerationAgent:
    """
    Agent responsible for generating code suggestions and examples.
    
    This agent provides implementation approaches, boilerplate code, and
    specific file modification suggestions for tasks.
    """
    
    def __init__(
        self,
        model_name: str = None,
        temperature: float = 0.2,
        enable_yaml_validation: bool = True,
    ):
        """
        Initialize the Code Generation Agent.
        
        Args:
            model_name: Name of the LLM model to use (default: gemini-1.5-flash for Gemini, gpt-3.5-turbo for OpenAI)
            temperature: Temperature for response generation (lower = more deterministic)
            enable_yaml_validation: Enable YAML validation for generated templates
        """
        self.model_name = model_name
        self.temperature = temperature
        self.llm = get_llm(
            model_name=model_name,
            temperature=temperature,
        )
        
        # Setup output parser
        self.parser = PydanticOutputParser(pydantic_object=CodeSuggestionOutput)
        
        # Setup YAML validation (if available)
        self.yaml_validation_enabled = enable_yaml_validation and VALIDATION_AVAILABLE
        if self.yaml_validation_enabled:
            self.schema_manager = SchemaManager()
            self.yaml_validator = YAMLValidator(self.schema_manager)
            logger.info("YAML validation enabled")
        else:
            self.schema_manager = None
            self.yaml_validator = None
            if enable_yaml_validation and not VALIDATION_AVAILABLE:
                logger.warning("YAML validation requested but validation module not available")
        
        # Create prompt template for implementation suggestions
        self.implementation_prompt = PromptTemplate(
            template="""You are an expert software engineer specializing in game development with Unreal Engine and Python.

Task: {task_description}

Files to modify: {files_to_modify}
Files to create: {files_to_create}
Implementation notes: {implementation_notes}

Provide 2-3 different implementation approaches for this task. For each approach:
1. Name: Short name for the approach
2. Description: Brief explanation of the approach
3. Pros: List of advantages (2-4 points)
4. Cons: List of disadvantages (2-4 points)
5. Complexity: low, medium, or high
6. Code Example: A concise code example showing the key implementation (10-30 lines)

Also provide:
- Specific file modifications needed with code snippets
- Required libraries or dependencies

Consider:
- Best practices for game development
- Performance implications
- Maintainability and readability
- Testing considerations

{format_instructions}

Provide your suggestions in the specified JSON format.
""",
            input_variables=["task_description", "files_to_modify", "files_to_create", "implementation_notes"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
        
        # Create prompt template for boilerplate generation
        self.boilerplate_prompt = PromptTemplate(
            template="""You are an expert software engineer. Generate boilerplate code for the following task:

Task: {task_description}
File Type: {file_type}
Language: {language}

Generate clean, well-structured boilerplate code following best practices:
- Include necessary imports
- Add docstrings/comments
- Follow language conventions
- Include basic error handling
- Add type hints (if applicable)

Provide only the code, no explanations.
""",
            input_variables=["task_description", "file_type", "language"],
        )
    
    def suggest_implementation(self, task: Task) -> List[Implementation]:
        """
        Generate implementation approach suggestions for a task.
        
        Args:
            task: Task to generate suggestions for
        
        Returns:
            List of Implementation objects with different approaches
        """
        # Prepare input
        files_to_modify = ", ".join(task.files_to_modify) if task.files_to_modify else "None"
        files_to_create = ", ".join(task.files_to_create) if task.files_to_create else "None"
        
        # Generate suggestions
        chain = self.implementation_prompt | self.llm | self.parser
        result = chain.invoke({
            "task_description": task.description,
            "files_to_modify": files_to_modify,
            "files_to_create": files_to_create,
            "implementation_notes": task.implementation_notes or "None",
        })
        
        # Convert to Implementation objects
        implementations = []
        for approach in result.implementation_approaches:
            # Parse complexity and duration
            complexity = approach.get("complexity", "medium").lower()
            
            # Estimate duration based on complexity
            duration_map = {"low": 2.0, "medium": 4.0, "high": 8.0}
            duration = Duration(
                hours=duration_map.get(complexity, 4.0),
                confidence=0.6
            )
            
            implementation = Implementation(
                approach_name=approach.get("name", ""),
                description=approach.get("description", ""),
                pros=approach.get("pros", []),
                cons=approach.get("cons", []),
                complexity=complexity,
                estimated_duration=duration,
                code_example=approach.get("code_example", ""),
                required_libraries=result.required_libraries,
            )
            implementations.append(implementation)
        
        return implementations
    
    def generate_boilerplate(self, task: Task, language: str = "python") -> str:
        """
        Generate boilerplate code for a task.
        
        Args:
            task: Task to generate boilerplate for
            language: Programming language (default: python)
        
        Returns:
            String containing boilerplate code
        """
        # Determine file type from task
        file_type = "module"
        if task.files_to_create:
            first_file = task.files_to_create[0]
            if first_file.endswith(".py"):
                file_type = "Python module"
                language = "python"
            elif first_file.endswith((".cpp", ".h", ".hpp")):
                file_type = "C++ class"
                language = "cpp"
            elif first_file.endswith((".js", ".jsx", ".ts", ".tsx")):
                file_type = "JavaScript/TypeScript module"
                language = "javascript"
        
        # Generate boilerplate
        chain = self.boilerplate_prompt | self.llm
        result = chain.invoke({
            "task_description": task.description,
            "file_type": file_type,
            "language": language,
        })
        
        return result.content
    
    def create_example(self, task: Task, implementations: List[Implementation] = None) -> str:
        """
        Create a code example demonstrating the task implementation.
        
        Args:
            task: Task to create example for
            implementations: Optional pre-computed implementation suggestions to avoid redundant LLM calls
        
        Returns:
            String containing example code
        """
        # Use provided implementations or generate them
        if implementations is None:
            implementations = self.suggest_implementation(task)
        
        # Use the first implementation approach's code example
        if implementations and implementations[0].code_example:
            return implementations[0].code_example
        
        # Fallback to boilerplate
        return self.generate_boilerplate(task)
    
    def propose_modifications(self, task: Task) -> List[FileModification]:
        """
        Propose specific file modifications for a task.
        
        Args:
            task: Task to generate modifications for
        
        Returns:
            List of FileModification objects
        """
        # Prepare input
        files_to_modify = ", ".join(task.files_to_modify) if task.files_to_modify else "None"
        files_to_create = ", ".join(task.files_to_create) if task.files_to_create else "None"
        
        # Generate suggestions
        chain = self.implementation_prompt | self.llm | self.parser
        result = chain.invoke({
            "task_description": task.description,
            "files_to_modify": files_to_modify,
            "files_to_create": files_to_create,
            "implementation_notes": task.implementation_notes or "None",
        })
        
        # Convert to FileModification objects
        modifications = []
        for mod_dict in result.file_modifications:
            modification = FileModification(
                file_path=mod_dict.get("file_path", ""),
                modification_type=mod_dict.get("modification_type", "update"),
                description=mod_dict.get("description", ""),
                code_snippet=mod_dict.get("code_snippet", ""),
            )
            modifications.append(modification)
        
        return modifications
    
    def validate_code_syntax(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Validate code syntax (basic validation).
        
        Args:
            code: Code string to validate
            language: Programming language
        
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        if language.lower() == "python":
            import ast
            try:
                ast.parse(code)
            except SyntaxError as e:
                errors.append({
                    "line": e.lineno,
                    "message": str(e.msg),
                    "type": "SyntaxError",
                })
        
        # Basic checks for any language
        if not code.strip():
            warnings.append("Code is empty")
        
        if len(code.split('\n')) > 500:
            warnings.append("Code is very long (>500 lines), consider breaking into multiple files")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
    
    def generate_tests(self, task: Task, test_framework: str = "pytest") -> str:
        """
        Generate test code for a task.
        
        Args:
            task: Task to generate tests for
            test_framework: Testing framework to use
        
        Returns:
            String containing test code
        """
        test_prompt = PromptTemplate(
            template="""Generate {test_framework} tests for the following implementation task:

Task: {task_description}

Generate comprehensive tests that:
1. Test the main functionality
2. Test edge cases
3. Test error handling
4. Follow {test_framework} best practices

Provide only the test code with appropriate imports and setup.
""",
            input_variables=["task_description", "test_framework"],
        )
        
        chain = test_prompt | self.llm
        result = chain.invoke({
            "task_description": task.description,
            "test_framework": test_framework,
        })
        
        return result.content
    
    def generate_yaml_template(
        self,
        yaml_type: str,
        description: str,
        schema_type: Optional[str] = None,
        auto_fix: bool = True
    ) -> Dict[str, Any]:
        """
        Generate YAML template with automatic validation.
        
        Args:
            yaml_type: Type of YAML to generate (e.g., 'config', 'data_table', 'asset')
            description: Description of what the YAML should contain
            schema_type: Schema type to validate against (auto-detected if None)
            auto_fix: Whether to auto-fix validation errors
            
        Returns:
            Dictionary with:
                - yaml_content: Generated YAML string
                - is_valid: Whether YAML is valid
                - validation_result: Full validation result
                - fixes_applied: Whether auto-fixes were applied
        """
        yaml_prompt = PromptTemplate(
            template="""Generate a {yaml_type} YAML template with the following requirements:

{description}

Requirements:
1. Generate valid, well-formatted YAML
2. Include comments explaining each section
3. Use appropriate data types
4. Follow YAML best practices

Provide only the YAML content, no additional explanation.
""",
            input_variables=["yaml_type", "description"],
        )
        
        # Generate YAML
        chain = yaml_prompt | self.llm
        result = chain.invoke({
            "yaml_type": yaml_type,
            "description": description,
        })
        
        yaml_content = result.content
        
        # Validate if enabled
        if self.yaml_validation_enabled:
            validation_result = self.yaml_validator.validate(
                yaml_content,
                schema_type=schema_type
            )
            
            fixes_applied = False
            
            # Auto-fix if needed and enabled
            if not validation_result.is_valid and auto_fix:
                fixed_yaml = self.yaml_validator.auto_fix(yaml_content, validation_result)
                # Re-validate
                validation_result = self.yaml_validator.validate(
                    fixed_yaml,
                    schema_type=schema_type or validation_result.schema_type
                )
                if validation_result.is_valid:
                    yaml_content = fixed_yaml
                    fixes_applied = True
                    logger.info("YAML auto-fixed successfully")
                else:
                    logger.warning("YAML auto-fix did not fully resolve issues")
            
            # Embed validation errors as comments if still invalid
            if not validation_result.is_valid:
                error_comments = "\n# VALIDATION ERRORS:\n"
                for error in validation_result.errors:
                    error_comments += f"# - {error}\n"
                yaml_content = error_comments + yaml_content
                logger.warning(f"Generated YAML has validation errors: {validation_result.errors}")
            
            return {
                "yaml_content": yaml_content,
                "is_valid": validation_result.is_valid,
                "validation_result": validation_result,
                "fixes_applied": fixes_applied,
            }
        else:
            # No validation
            return {
                "yaml_content": yaml_content,
                "is_valid": True,  # Assume valid without validation
                "validation_result": None,
                "fixes_applied": False,
            }
    
    def validate_yaml(self, yaml_content: str, schema_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate YAML content against a schema.
        
        Args:
            yaml_content: YAML content to validate
            schema_type: Schema type to validate against (auto-detected if None)
            
        Returns:
            Dictionary with validation results
        """
        if not self.yaml_validation_enabled:
            logger.warning("YAML validation not enabled")
            return {
                "is_valid": True,
                "errors": [],
                "warnings": ["YAML validation not enabled"],
            }
        
        validation_result = self.yaml_validator.validate(yaml_content, schema_type)
        
        return {
            "is_valid": validation_result.is_valid,
            "errors": validation_result.errors,
            "warnings": validation_result.warnings,
            "schema_type": validation_result.schema_type,
        }
