# Upgrade Notes - Dependencies Update

## Overview

The dependencies in `requirements.txt` have been updated to resolve compatibility issues with modern Python versions (3.12+) and to support NumPy 2.0.

## Key Changes

### Python Version Requirement

- **Old**: Python 3.8+
- **New**: Python 3.9+ (3.12+ recommended)

### Major Package Updates

#### NumPy (Critical Change)
- **Old**: `numpy==1.24.3`
- **New**: `numpy>=2.0.0,<3.0.0`
- **Reason**: Old versions require compilation from source on Python 3.12+, causing installation failures. NumPy 2.0+ provides pre-built binary wheels for modern Python versions.

#### Pandas
- **Old**: `pandas==2.0.3`
- **New**: `pandas>=2.2.0,<3.0.0`
- **Reason**: Pandas 2.2+ is compatible with NumPy 2.0 and required for the updated NumPy version.

#### LangChain Ecosystem
- **Old**: 
  - `langchain==0.1.0`
  - `langchain-openai==0.0.2`
  - `langchain-community==0.0.10`
- **New**: 
  - `langchain>=0.3.19,<0.4.0`
  - `langchain-openai>=0.3.0,<0.4.0`
  - `langchain-community>=0.3.27,<0.4.0`
- **Reason**: 
  - LangChain 0.3.19+ supports NumPy 2.0
  - Version 0.3.27+ of langchain-community fixes a critical XML External Entity (XXE) vulnerability

#### ChromaDB
- **Old**: `chromadb==0.4.22`
- **New**: `chromadb>=0.5.23,<0.6.0`
- **Reason**: Updated to support NumPy 2.0 through the langchain-chroma integration

#### Sentence Transformers
- **Old**: `sentence-transformers==2.2.2`
- **New**: `sentence-transformers>=3.3.0,<4.0.0`
- **Reason**: Version 3.3+ supports NumPy 2.0 and Python 3.12

#### OpenAI
- **Old**: `openai==1.6.1`
- **New**: `openai>=1.57.0,<2.0.0`
- **Reason**: Updated to latest stable version for improved features and bug fixes

### Other Package Updates

All other packages have been updated to their latest compatible versions:

- `pypdf`: 3.17.4 → 5.1.0
- `markdown`: 3.5.1 → 3.7
- `beautifulsoup4`: 4.12.2 → 4.12.3
- `tiktoken`: 0.5.2 → 0.8.0
- `python-dotenv`: 1.0.0 → 1.0.1
- `rich`: 13.7.0 → 13.9.4
- `pydantic`: 2.5.3 → 2.10.3
- `pytest`: 7.4.3 → 8.3.4
- `pytest-cov`: 4.1.0 → 6.0.0
- `black`: 23.12.1 → 24.10.0
- `flake8`: 7.0.0 → 7.1.1
- `mypy`: 1.8.0 → 1.13.0

## Breaking Changes

### NumPy 2.0 Breaking Changes

NumPy 2.0 introduced some breaking changes:

1. **Removed dtype aliases**: `np.float_`, `np.int_`, etc. have been removed. Use `np.float64`, `np.int64` instead.
2. **Some functions changed behavior**: Refer to the [NumPy 2.0 migration guide](https://numpy.org/devdocs/numpy_2_0_migration_guide.html) for details.

### LangChain 0.3 Changes

LangChain 0.3 introduced:

1. **Mandatory Pydantic 2**: The codebase now requires Pydantic 2.x
2. **API changes**: Some APIs have been updated or deprecated. Refer to [LangChain v0.3 announcement](https://blog.langchain.com/announcing-langchain-v0-3/) for details.

## Migration Guide

### For Existing Users

1. **Backup your environment**: If you have an existing environment, consider creating a new one:
   ```bash
   python -m venv venv-new
   source venv-new/bin/activate  # On Windows: venv-new\Scripts\activate
   ```

2. **Install updated requirements**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Validate installation**:
   ```bash
   python validate_requirements.py
   ```

4. **Test your application**: Run your existing code to ensure compatibility.

### For New Users

Simply follow the standard installation instructions in the README:

```bash
pip install -r requirements.txt
```

## Compatibility Matrix

| Package | Python 3.9 | Python 3.10 | Python 3.11 | Python 3.12+ |
|---------|-----------|-------------|-------------|--------------|
| numpy 2.0+ | ✓ | ✓ | ✓ | ✓ |
| pandas 2.2+ | ✓ | ✓ | ✓ | ✓ |
| langchain 0.3+ | ✓ | ✓ | ✓ | ✓ |
| chromadb 0.5+ | ✓ | ✓ | ✓ | ✓ |
| sentence-transformers 3.3+ | ✓ | ✓ | ✓ | ✓ |

## Security Improvements

- **Fixed**: XML External Entity (XXE) vulnerability in langchain-community (CVE reported, fixed in 0.3.27+)
- All packages updated to latest stable versions with security patches

## Troubleshooting

### Installation Issues

If you encounter installation issues:

1. **Clear pip cache**:
   ```bash
   pip cache purge
   ```

2. **Upgrade pip**:
   ```bash
   pip install --upgrade pip
   ```

3. **Install in order** (if dependency resolution fails):
   ```bash
   pip install numpy pandas
   pip install -r requirements.txt
   ```

### Runtime Errors

If you see NumPy-related errors:

1. **Check NumPy version**:
   ```python
   import numpy as np
   print(np.__version__)  # Should be 2.0 or higher
   ```

2. **Update deprecated code**: Replace any usage of removed NumPy aliases:
   - `np.float_` → `np.float64`
   - `np.int_` → `np.int64`
   - etc.

## References

- [NumPy 2.0 Release Notes](https://numpy.org/doc/stable/release/2.0.0-notes.html)
- [NumPy 2.0 Migration Guide](https://numpy.org/devdocs/numpy_2_0_migration_guide.html)
- [LangChain v0.3 Announcement](https://blog.langchain.com/announcing-langchain-v0-3/)
- [Pandas 2.2 Release Notes](https://pandas.pydata.org/docs/whatsnew/v2.2.0.html)

## Questions or Issues?

If you encounter any problems with the updated dependencies, please:

1. Check this document for troubleshooting steps
2. Run the validation script: `python validate_requirements.py`
3. Open an issue on the GitHub repository with details about your environment and the error
