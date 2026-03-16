---
name: dev-setup-gsp
description: |
  Set up the GSP_API development environment. This skill handles installing Python dependencies, setting up optional visualization backends (Matplotlib and DatoViz), configuring pre-commit hooks for code quality, and initializing the project structure. Use this skill when the user wants to set up a fresh development environment, install dependencies, prepare backends, or configure git hooks. Trigger on phrases like "set up the project", "install dependencies", "configure pre-commit", "initialize the environment", or "get everything working". Use this for onboarding new developers or resetting the environment.
compatibility: ""
---

# Development Setup for GSP_API

This skill sets up a complete development environment for GSP_API, including dependencies, optional backends, and git hooks.

## What this skill does

1. **Install Python dependencies** - Install core requirements from pyproject.toml or requirements.txt
2. **Configure visualization backends** - Install Matplotlib and DatoViz packages
3. **Set up pre-commit hooks** - Configure automated linting and formatting on git commit
4. **Initialize project structure** - Verify/create necessary directories
5. **Verify setup** - Test that imports work and environment is ready

## How to use this skill

When the user asks to:
- "Set up the development environment"
- "Install dependencies"
- "Configure pre-commit hooks"
- "Get the project ready for development"
- "Fresh install of GSP_API"

You should execute the setup pipeline below.

## Setup pipeline

### Prerequisites

- Ensure Python ≥ 3.9 is available (`python --version`)
- Working pip and git
- Project is at `/Users/jetienne/work/GSP_API`

### Step 1: Install core dependencies

```bash
cd /Users/jetienne/work/GSP_API
pip install -e ".[dev]"
```

If that fails, try:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**What to look for:**
- "Successfully installed" messages
- No error messages about missing packages
- The `gsp` package is now importable

### Step 2: Install optional visualization backends

```bash
# Install Matplotlib (standard backend)
pip install matplotlib

# Install DatoViz (alternative backend)
pip install datoviz
```

**What to look for:**
- Both packages install without errors
- If DatoViz fails, note it (it may have platform-specific requirements)

### Step 3: Set up pre-commit hooks

```bash
cd /Users/jetienne/work/GSP_API
pip install pre-commit
pre-commit install
```

**What to look for:**
- "pre-commit installed at .git/hooks/pre-commit"
- The `.pre-commit-config.yaml` file exists and defines linting rules

### Step 4: Create/verify project structure

```bash
cd /Users/jetienne/work/GSP_API
mkdir -p tests examples docs src
```

Verify these directories exist:
- `src/` or package directory (where `gsp` code lives)
- `tests/` (pytest test files)
- `examples/` (example scripts)
- `docs/` (documentation)

### Step 5: Verify setup

```bash
cd /Users/jetienne/work/GSP_API

# Test core import
python -c "import gsp; print('✓ gsp imported successfully')"

# Test backends
GSP_BACKEND=matplotlib python -c "import gsp; print('✓ Matplotlib backend available')"
GSP_BACKEND=datoviz python -c "import gsp; print('✓ DatoViz backend available')" 2>/dev/null || echo "✗ DatoViz not available (optional)"

# Test pytest
python -m pytest --version
```

## Reporting results

Provide a checklist summary:

```
Development Environment Setup Complete
✓ Core dependencies installed
✓ Matplotlib backend available
✓ DatoViz backend available (or note if optional/skipped)
✓ Pre-commit hooks configured
✓ Project structure verified
✓ Import verification passed

Environment ready for development!
```

If anything fails, explain which step failed and suggest debugging steps.

## When to run this skill

- New developer onboarding
- Fresh clone of the repository
- After major dependency updates
- When setting up CI/CD environment
- When the user explicitly asks to "set up" or "install"
