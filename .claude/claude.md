# Claude Context for GSP_API

## Project Overview

**GSP_API** is a scientific visualization library for Python that provides a unified interface for creating visualizations across multiple backends. Currently supporting:
- **Matplotlib** - Standard, widely-compatible backend
- **DatoViz** - Alternative high-performance visualization backend

The library aims to provide clean, intuitive APIs for data visualization while abstracting away backend-specific implementation details.

**Location:** `/Users/jetienne/work/GSP_API`

---

## Project Structure

```
GSP_API/
├── src/gsp/                    # Main package source code
│   ├── __init__.py            # Package initialization & backend selection
│   ├── plot.py                # Core plotting interface
│   ├── backends/              # Backend implementations
│   │   ├── matplotlib_backend.py
│   │   └── datoviz_backend.py
│   └── utils/                 # Utility functions
├── tests/                      # Pytest test suite
│   ├── test_plot.py
│   ├── test_backends.py
│   └── test_visualization.py
├── examples/                   # Example scripts
│   ├── example_basic.py
│   ├── example_advanced.py
│   └── README.md
├── docs/                       # Documentation
├── .agents/skills/             # Installed Cowork skills
│   ├── test-validate-gsp.skill
│   ├── dev-setup-gsp.skill
│   ├── docs-examples-gsp.skill
│   └── build-release-gsp.skill
├── pyproject.toml             # Project metadata & dependencies
├── requirements.txt           # Core dependencies
├── requirements-dev.txt       # Development dependencies
├── .pre-commit-config.yaml    # Git hook configuration
└── claude.md                  # This file
```

---

## Development Guidelines

### Code Style & Conventions

- **Language:** Python 3.9+
- **Type hints:** All functions should have type annotations (strict mypy compliance)
- **Code format:** Clean, readable code prioritizing clarity over cleverness
- **Docstrings:** Use Google-style docstrings for all public functions
- **Testing:** Comprehensive test coverage (target ≥80% coverage)

### Backend Selection

The active backend is determined by the `GSP_BACKEND` environment variable:

```bash
# Use Matplotlib (default)
GSP_BACKEND=matplotlib python script.py

# Use DatoViz
GSP_BACKEND=datoviz python script.py
```

Backend selection happens at import time in `src/gsp/__init__.py`.

### Testing Requirements

All changes should pass:
1. **pytest** - Unit and integration tests
2. **mypy** - Type checking (strict mode)
3. **Both backends** - Verify Matplotlib and DatoViz both work

Run validation before committing:
```bash
test-validate-gsp  # Uses installed Cowork skill
```

Or manually:
```bash
pytest tests/ -v --cov=src --cov-report=term-missing
mypy src/ --strict --show-error-codes
GSP_BACKEND=matplotlib python -c "import gsp"
GSP_BACKEND=datoviz python -c "import gsp"
```

### Development Workflow

1. **Create branch** for feature/fix
2. **Write tests first** (TDD approach recommended)
3. **Implement feature** with type hints
4. **Run validation** with `test-validate-gsp` skill
5. **Create examples** if it's a user-facing feature
6. **Commit** with clear message
7. **Push and create PR**

### Creating Examples

When adding new features, create example scripts in `examples/`:
- Use `example_<feature_name>.py` naming
- Include docstrings explaining what's demonstrated
- Test with both backends
- Use the `docs-examples-gsp` skill to help create them

---

## Installed Cowork Skills

Four custom skills are available to automate common workflows:

### 1. test-validate-gsp
**Trigger:** "Run tests", "Check for type errors", "Validate code quality"

Runs:
- pytest with coverage
- mypy type checking (strict)
- Both backend validation

Example: `"Run the tests and check for type errors"`

### 2. dev-setup-gsp
**Trigger:** "Set up the environment", "Install dependencies", "Configure pre-commit"

Sets up:
- Python dependencies
- Visualization backends
- Pre-commit hooks
- Project structure verification

Example: `"Set up the development environment"`

### 3. docs-examples-gsp
**Trigger:** "Create an example", "Write a demo script", "Show how to use"

Creates:
- Clean, documented example scripts
- Examples for both backends
- Self-contained, runnable code

Example: `"Create an example showing how to plot data with both backends"`

### 4. build-release-gsp
**Trigger:** "Prepare a release", "Generate release notes", "Create examples for release"

Prepares:
- Visualization examples (both backends)
- Formatted release notes
- Pre-release checklist

Example: `"Prepare a release for version 1.1.0"`

---

## Key Directories & Files

| File/Directory | Purpose |
|---|---|
| `src/gsp/` | Main library source code |
| `tests/` | Test suite (pytest) |
| `examples/` | Example scripts for users |
| `docs/` | Documentation files |
| `pyproject.toml` | Project metadata, dependencies, build config |
| `.pre-commit-config.yaml` | Git hooks for linting/formatting |
| `.agents/skills/` | Installed Cowork automation skills |

---

## Dependencies

### Core Dependencies
- Python ≥ 3.9
- matplotlib (required for Matplotlib backend)
- datoviz (optional, for DatoViz backend)
- numpy (for data handling)

### Development Dependencies
- pytest (testing)
- pytest-cov (coverage reporting)
- mypy (type checking)
- pre-commit (git hooks)

Install with:
```bash
pip install -e ".[dev]"
```

---

## Important Notes

### Type Hints
All new code must have complete type hints. Run mypy with `--strict` mode:
```bash
mypy src/ --strict --show-error-codes
```

Type errors block commits (pre-commit hook).

### Backend Compatibility
Every public API must work with both Matplotlib and DatoViz backends. When implementing features:
1. Write backend-agnostic interface in `src/gsp/`
2. Implement in `src/gsp/backends/matplotlib_backend.py`
3. Implement in `src/gsp/backends/datoviz_backend.py`
4. Test both with the `test-validate-gsp` skill

### Testing
- Write tests for new features
- Target ≥80% code coverage
- Test both backends
- Use descriptive test names

---

## Quick Commands

```bash
# Set up development environment
dev-setup-gsp  # or: "Set up the development environment"

# Run tests and validation
test-validate-gsp  # or: "Run the tests"

# Create an example
docs-examples-gsp  # or: "Create an example showing..."

# Prepare a release
build-release-gsp  # or: "Prepare a release with notes"

# Switch backends for testing
GSP_BACKEND=matplotlib python script.py
GSP_BACKEND=datoviz python script.py
```

---

## Getting Help

When working with this project:
- Refer to installed skills for automation (test-validate-gsp, dev-setup-gsp, etc.)
- Check `examples/` for usage patterns
- Review type hints in source code for API guidance
- Run tests to validate changes before committing
