# Contributing to Adastrea Director

Thank you for your interest in contributing to Adastrea Director! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager
- An OpenAI API key (for Phase 1)

### Setting Up Your Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mittenzx/Adastrea-Director.git
   cd Adastrea-Director
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Test the installation:**
   ```bash
   # Ingest the sample documentation
   python ingest.py --docs-dir .
   
   # Start the assistant
   python main.py
   ```

## Project Structure

```
Adastrea-Director/
├── README.md              # Project overview
├── PROJECT_PLAN.md        # Detailed roadmap
├── AGENTS.md              # Agent architecture docs
├── CONTRIBUTING.md        # This file
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── .gitignore            # Git ignore rules
├── ingest.py             # Document ingestion script
├── main.py               # Main CLI application
├── GDD_TEMPLATE.md       # GDD template
└── SAMPLE_GDD.md         # Example GDD
```

## Development Workflow

### Making Changes

1. **Create a new branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write clean, readable code
   - Follow Python PEP 8 style guidelines
   - Add docstrings to functions and classes
   - Update documentation if needed

3. **Test your changes:**
   - Ensure existing functionality still works
   - Test new features thoroughly
   - Run code formatters (black, flake8)

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: brief description of your changes"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Update the Roadmap:**
   - **REQUIRED:** Update ROADMAP.md if your changes complete features, phases, or milestones
   - Mark completed items with ✅ and add completion dates
   - Update metrics with actual results
   - Add lessons learned and impacts on future work
   - See "Contributing to the Roadmap" section in ROADMAP.md for details

7. **Create a Pull Request:**
   - Go to the GitHub repository
   - Click "New Pull Request"
   - Describe your changes clearly
   - Reference any related issues
   - **Include "Roadmap Updates" section** if you modified ROADMAP.md

### Commit Message Guidelines

We follow conventional commit format:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

Example:
```
feat: add support for PDF document ingestion
fix: resolve memory leak in vector database
docs: update README with installation steps
```

## Code Style

### Python

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions/classes
- Keep functions focused and small
- Use meaningful variable names

### Example:

```python
def process_document(file_path: str, chunk_size: int = 1000) -> List[str]:
    """
    Process a document and split it into chunks.
    
    Args:
        file_path: Path to the document file
        chunk_size: Maximum size of each chunk
        
    Returns:
        List of document chunks
    """
    # Implementation here
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_ingestion.py
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names
- Test both success and failure cases

## Documentation

### Updating Documentation

- Update README.md for user-facing changes
- **Update ROADMAP.md when completing features/phases/milestones (REQUIRED)**
- Update AGENTS.md for architecture changes
- Add inline comments for complex logic
- Update docstrings when changing function signatures

**Note:** ROADMAP.md has replaced PROJECT_PLAN.md as the primary planning document.

### Documentation Style

- Use clear, concise language
- Include code examples where helpful
- Keep formatting consistent
- Use markdown for all documentation

## Areas for Contribution

### Phase 1 (Current)

- [ ] Additional document loaders (PDF, DOCX, code files)
- [ ] Improved chunking strategies
- [ ] Query optimization
- [ ] Better error handling
- [ ] Unit tests
- [ ] Documentation improvements

### Future Phases

- [ ] Task decomposition algorithms (Phase 2)
- [ ] Performance monitoring agents (Phase 3)
- [ ] Creative content generation (Phase 4)

## Getting Help

- **Issues:** Check existing issues or create a new one
- **Discussions:** Use GitHub Discussions for questions
- **Documentation:** Review PROJECT_PLAN.md and AGENTS.md

## Code Review Process

1. Pull requests require at least one review
2. All tests must pass
3. Code must follow style guidelines
4. Documentation must be updated
5. **ROADMAP.md must be updated** if completing features/phases/milestones
6. No merge conflicts

### Roadmap Update Requirements

All PRs that complete significant work **must update ROADMAP.md**:

✅ **Update ROADMAP.md when your PR:**
- Completes a feature or major enhancement
- Finishes a phase or milestone
- Adds new agents or capabilities
- Changes project direction or priorities
- Discovers important technical insights

📝 **What to update:**
- Change ⏳ to ✅ for completed items
- Add actual completion dates
- Update metrics with actual results
- Add lessons learned
- Note impacts on future phases

See the "Contributing to the Roadmap" section in ROADMAP.md for detailed guidelines and examples.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Questions?

Feel free to:
- Open an issue
- Start a discussion
- Contact the maintainers

---

Thank you for contributing to Adastrea Director! Your efforts help make game development more accessible and efficient.
