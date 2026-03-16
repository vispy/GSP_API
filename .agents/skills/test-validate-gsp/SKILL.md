---
name: test-validate-gsp
description: |
  Run comprehensive testing and validation for GSP_API. This skill handles pytest execution, type checking with mypy, and testing both visualization backends (Matplotlib and DatoViz). Use this skill whenever the user mentions testing, running tests, checking code quality, validating the visualization library, testing backends, or ensuring code health. Trigger whenever they want to verify the code works correctly or check for type errors. Also use this proactively when the user is making changes to the codebase and should validate their work.
compatibility: ""
---

# Test & Validate GSP_API

This skill runs the full test suite, checks code quality, and validates both visualization backends work correctly.

## What this skill does

1. **Run pytest** - Execute the test suite with coverage reporting
2. **Type check** - Run mypy to validate type hints across the codebase
3. **Test both backends** - Verify Matplotlib and DatoViz backends both work correctly
4. **Summary report** - Provide a clear pass/fail summary with any issues

## How to use this skill

When the user asks to:
- "Run the tests"
- "Check for type errors"
- "Validate the visualization backends"
- "Check code quality"
- "Make sure everything still works"

You should execute the test pipeline below.

## Test pipeline

### Prerequisites

Verify the project is at `/Users/jetienne/work/GSP_API` and dependencies are installed. If not, alert the user.

### Step 1: Run pytest with coverage

```bash
cd /Users/jetienne/work/GSP_API
python -m pytest tests/ -v --tb=short --cov=src --cov-report=term-missing
```

**What to look for:**
- All tests pass (green checkmarks)
- Coverage is ≥ 80% (aim higher)
- Any failures are clearly reported

### Step 2: Type check with mypy

```bash
cd /Users/jetienne/work/GSP_API
mypy src/ --strict --show-error-codes
```

**What to look for:**
- No "error:" lines (strict mode)
- If there are errors, list them clearly
- Type coverage should be comprehensive

### Step 3: Test both backends

Run a quick validation that both backends can be imported and instantiated:

```bash
cd /Users/jetienne/work/GSP_API
GSP_BACKEND=matplotlib python -c "import gsp; print('Matplotlib backend OK')"
GSP_BACKEND=datoviz python -c "import gsp; print('DatoViz backend OK')"
```

**What to look for:**
- Both commands output "backend OK" without errors
- No import errors or missing dependencies

### Reporting results

After running all three checks, provide a summary in this format:

```
✓ Tests: [X/Y passed, Z% coverage]
✓ Type checking: [clean or # issues found]
✓ Matplotlib backend: [working]
✓ DatoViz backend: [working]

Overall: [PASS / NEEDS ATTENTION]
```

If anything fails, explain the issue and suggest next steps (e.g., "Run `pytest tests/visualization/ -vv` for details").

## When to run this skill

- Before committing code
- After pulling changes
- When adding new features
- When the user explicitly asks about code quality or testing
- As part of a CI/CD workflow check
