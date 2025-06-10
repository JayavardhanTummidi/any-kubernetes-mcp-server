# Contributing to Kubernetes MCP Server

Thank you for your interest in contributing to the Kubernetes MCP Server! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check the existing issues to see if the problem has already been reported. If it hasn't, create a new issue with the following information:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots or logs (if applicable)
- Environment details (OS, Python version, Kubernetes version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- A clear, descriptive title
- A detailed description of the proposed enhancement
- Any potential implementation details
- Why this enhancement would be useful to most users

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Add or update tests as necessary
5. Update documentation as necessary
6. Submit a pull request

#### Pull Request Guidelines

- Follow the existing code style
- Include tests for new features or bug fixes
- Update documentation for any changed functionality
- Keep pull requests focused on a single topic
- Reference any related issues in your pull request description

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. Run tests:
   ```bash
   python -m unittest discover tests
   ```

## Coding Style

This project follows PEP 8 style guidelines. Please ensure your code adheres to these standards.

You can check your code style with:
```bash
flake8 kubernetes_mcp_server tests
```

## Testing

Please write tests for any new features or bug fixes. Run the test suite before submitting a pull request:

```bash
python -m unittest discover tests
```

## Documentation

Documentation is a crucial part of this project. Please update the documentation when necessary:

- Update the README.md file for user-facing changes
- Update docstrings for any modified functions or classes
- Add examples for new features

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

## Versioning

This project follows [Semantic Versioning](https://semver.org/).

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

## Questions?

If you have any questions, please feel free to create an issue with the "question" label.

Thank you for contributing to the Kubernetes MCP Server!
