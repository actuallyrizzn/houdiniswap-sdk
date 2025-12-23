# Contributing to Houdini Swap Python SDK

Thank you for your interest in contributing to the Houdini Swap Python SDK! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the issue list to see if the problem has already been reported. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Environment details** (Python version, OS, SDK version)
- **Error messages** or logs
- **Minimal code example** that reproduces the issue

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** - why is this enhancement useful?
- **Proposed solution** (if you have one)
- **Alternatives considered** (if any)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow the coding style (see below)
   - Add tests if applicable
   - Update documentation
   - Update CHANGELOG.md
4. **Commit your changes**:
   ```bash
   git commit -m "feat: Add new feature"
   ```
   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `test:` for tests
   - `chore:` for maintenance
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request** on GitHub

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/actuallyrizzn/houdiniswap-sdk.git
   cd houdiniswap-sdk
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install development dependencies** (if available):
   ```bash
   pip install -e ".[dev]"
   ```

## Coding Standards

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use descriptive variable and function names

### Code Formatting

We recommend using:
- `black` for code formatting
- `mypy` for type checking
- `pylint` or `flake8` for linting

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include type information in docstrings
- Document exceptions that can be raised
- Include usage examples for complex functions

### Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage
- Include edge cases and error conditions

## Project Structure

```
houdiniswap-sdk/
├── houdiniswap/          # Main package
│   ├── __init__.py
│   ├── client.py        # Main client class
│   ├── models.py        # Data models
│   └── exceptions.py    # Exception classes
├── docs/                # Documentation
├── examples/            # Example code
├── tests/               # Test suite (if exists)
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── setup.py
```

## Review Process

1. All PRs require review from maintainers
2. Maintainers may request changes
3. Address review comments promptly
4. Once approved, maintainers will merge

## Questions?

If you have questions about contributing:

- Check existing issues and discussions
- Open a new issue with the `question` label
- Contact the maintainers

Thank you for contributing! 🎉

