# Contributing to Adastrea Director

Thank you for your interest in contributing to Adastrea Director! This guide will help you get started with contributing to the project.

## 🌟 Ways to Contribute

You can contribute in many ways:

- **Code Contributions:** New features, bug fixes, optimizations
- **Documentation:** Improvements to guides, tutorials, API docs
- **Testing:** Writing tests, reporting bugs, testing new features
- **Design:** UI/UX improvements, mockups, design system
- **Community:** Helping others, answering questions, sharing knowledge

## 🚀 Getting Started

### Prerequisites

- Git
- Python 3.9+ (3.12+ recommended)
- Familiarity with the project (read [README](https://github.com/Mittenzx/Adastrea-Director/blob/main/README.md))

### Setting Up Development Environment

1. **Fork the repository:**
   - Visit [Adastrea-Director](https://github.com/Mittenzx/Adastrea-Director)
   - Click "Fork" button

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Adastrea-Director.git
   cd Adastrea-Director
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/Mittenzx/Adastrea-Director.git
   ```

4. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Verify installation:**
   ```bash
   pytest
   ```

## 📝 Development Workflow

### 1. Create a Branch

Create a new branch for your work:

```bash
# Update your fork
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `test/` - Test additions/improvements
- `refactor/` - Code refactoring

### 2. Make Your Changes

**Code Changes:**
- Follow [Code Style](#code-style) guidelines
- Write clean, readable code
- Add comments for complex logic
- Update documentation if needed

**Documentation Changes:**
- Use clear, concise language
- Include code examples where helpful
- Keep formatting consistent
- Update related pages

**Test Changes:**
- Write tests for new features
- Ensure existing tests pass
- Aim for high code coverage

### 3. Test Your Changes

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_ingestion.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test category
pytest -m unit
pytest -m integration
```

Manual testing:

```bash
# Test CLI
python main.py

# Test GUI
python gui_director.py

# Test planning
python planner.py --interactive

# Test agents
python agent_orchestrator_cli.py status
```

### 4. Commit Your Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat: add new feature description"
```

**Commit message format:**
```
<type>: <short description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Formatting (no code change)
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

**Examples:**
```
feat: add support for PDF document ingestion
fix: resolve memory leak in vector database
docs: update installation guide for Apple Silicon
test: add integration tests for planning system
refactor: simplify query processing logic
```

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Create Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill out the PR template:
   - **Title:** Clear, descriptive title
   - **Description:** What changes and why
   - **Related Issues:** Link to issues (e.g., "Fixes #123")
   - **Testing:** How you tested the changes
   - **Screenshots:** For UI changes

5. Submit the PR

### 7. Address Review Feedback

- Respond to reviewer comments
- Make requested changes
- Push updates to the same branch
- Re-request review when ready

## 📐 Code Style

### Python Style Guide

Follow [PEP 8](https://pep8.org/) guidelines:

**Formatting:**
- 4 spaces for indentation (no tabs)
- Max line length: 100 characters
- Use descriptive variable names
- Add blank lines between functions

**Naming Conventions:**
```python
# Classes: PascalCase
class MyClass:
    pass

# Functions/Methods: snake_case
def my_function():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3

# Private: prefix with underscore
def _private_function():
    pass
```

**Type Hints:**
```python
def process_document(file_path: str, chunk_size: int = 1000) -> List[str]:
    """Process a document and return chunks."""
    pass
```

**Docstrings:**
```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: Description of when this is raised
    """
    pass
```

### Code Quality Tools

We use these tools (run before committing):

```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .

# Sort imports
isort .
```

## 🧪 Testing Guidelines

### Writing Tests

**Test Structure:**
```python
import pytest

def test_feature_name():
    """Test that feature does X."""
    # Arrange
    setup_data = create_test_data()
    
    # Act
    result = function_under_test(setup_data)
    
    # Assert
    assert result == expected_value
```

**Test Categories:**

Use markers for test categories:
```python
@pytest.mark.unit
def test_unit_functionality():
    pass

@pytest.mark.integration
def test_integration_workflow():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

**Fixtures:**
```python
@pytest.fixture
def sample_document():
    """Provide sample document for tests."""
    return "Sample document content"

def test_ingestion(sample_document):
    result = ingest(sample_document)
    assert result is not None
```

### Test Coverage

- Aim for >80% code coverage
- Write tests for:
  - New features
  - Bug fixes
  - Edge cases
  - Error handling

```bash
# Check coverage
pytest --cov=. --cov-report=term-missing
```

## 📚 Documentation Guidelines

### Code Documentation

**Module Docstrings:**
```python
"""
Module for document ingestion.

This module handles ingestion of various document types,
converting them into chunks and storing in the vector database.
"""
```

**Function Documentation:**
- Always include docstrings for public functions
- Document parameters, return values, and exceptions
- Include usage examples for complex functions

### Wiki Documentation

When updating wiki:

1. Edit files in `wiki/` directory
2. Follow markdown best practices
3. Include navigation links
4. Add examples and screenshots
5. Update table of contents
6. Test links work

See [Wiki README](../README.md) for details.

## 🔍 Pull Request Guidelines

### Before Submitting

Checklist before creating PR:

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts
- [ ] Branch is up-to-date with main

### PR Description

Include in your PR:

**Title:**
- Clear and descriptive
- Follow commit message conventions

**Description:**
- What changes were made
- Why the changes were necessary
- How the changes were tested
- Related issues (e.g., "Fixes #123")

**Screenshots:**
- For UI changes, include before/after screenshots
- Annotate screenshots if needed

**Testing:**
- How you tested the changes
- Test results
- Manual testing steps

### Review Process

1. **Automated Checks:** CI runs tests automatically
2. **Code Review:** Maintainers review your code
3. **Feedback:** Address review comments
4. **Approval:** PR approved by maintainer
5. **Merge:** PR merged into main

**Response Time:**
- Initial review: Usually within 1-3 days
- Follow-up: 1-2 days
- Merge: After approval and passing checks

## 🐛 Reporting Bugs

### Before Reporting

1. Check [existing issues](https://github.com/Mittenzx/Adastrea-Director/issues)
2. Try latest version
3. Search documentation

### Bug Report Template

Include:

**Description:**
- Clear description of the bug
- Expected behavior
- Actual behavior

**Reproduction Steps:**
1. Step-by-step instructions
2. Minimal example to reproduce
3. Any relevant code snippets

**Environment:**
- OS and version
- Python version
- Adastrea Director version
- Relevant dependencies

**Logs:**
- Error messages
- Stack traces
- Relevant log output

**Screenshots:**
- If applicable, add screenshots

## 💡 Requesting Features

### Feature Request Process

1. **Search Existing Requests:** Check [discussions](https://github.com/Mittenzx/Adastrea-Director/discussions)
2. **Create Discussion:** Explain your idea
3. **Gather Feedback:** Discuss with community
4. **Create Issue:** If approved, create feature request issue

### Feature Request Template

Include:

**Problem:**
- What problem does this solve?
- Who benefits from this feature?

**Proposed Solution:**
- How should it work?
- What's the user experience?

**Alternatives:**
- What alternatives did you consider?
- Why is your solution best?

**Additional Context:**
- Mockups or diagrams
- Examples from other tools
- Related issues or discussions

## 🏆 Recognition

Contributors are recognized in:

- [README](https://github.com/Mittenzx/Adastrea-Director/blob/main/README.md) contributors section
- [Release notes](https://github.com/Mittenzx/Adastrea-Director/releases)
- Project documentation

## 📞 Getting Help

Need help contributing?

- **💬 [Discussions](https://github.com/Mittenzx/Adastrea-Director/discussions)** - Ask questions
- **📖 [Wiki](../Home.md)** - Read documentation
- **👨‍💻 [Code Reference](Code-Reference.md)** - API documentation

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to Adastrea Director!** 🎉

Your contributions help make game development more accessible and efficient.

[← Back to Home](../Home.md)
