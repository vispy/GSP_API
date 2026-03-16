---
name: docs-examples-gsp
description: |
  Create and update example scripts for GSP_API visualization library. This skill generates clean, well-documented example scripts that demonstrate both Matplotlib and DatoViz backends. Use this skill when the user wants to create new examples, update existing examples, demonstrate visualization capabilities, or show how to use the library. Trigger on phrases like "create an example", "write an example script", "show how to use", "demonstrate the visualization", "create examples for both backends", or "add example code". Use this for documentation, tutorials, and showcasing library features.
compatibility: ""
---

# Documentation & Examples for GSP_API

This skill creates and updates example scripts that demonstrate GSP_API's visualization capabilities.

## What this skill does

1. **Create example scripts** - Write clean, well-commented Python scripts demonstrating library usage
2. **Show both backends** - Provide examples using both Matplotlib and DatoViz backends
3. **Document examples** - Add docstrings and comments explaining what each example does
4. **Organize examples** - Place examples in the `examples/` directory with clear naming
5. **Verify examples** - Test that example scripts run without errors

## How to use this skill

When the user asks to:
- "Create an example"
- "Write a demo script"
- "Show how to use the visualization features"
- "Add an example for both backends"
- "Create example documentation"
- "Update examples"

You should create or update example scripts following the pattern below.

## Example script structure

Every example script should follow this template:

```python
"""
Example: [Clear title describing what this demonstrates]

This example shows how to [specific capability].

Backends tested: Matplotlib, DatoViz
"""

import gsp
import numpy as np

def main():
    """Run the visualization example."""
    # Set up data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    # Create visualization
    plot = gsp.Plot()
    plot.line(x, y, label="sin(x)")
    plot.title("Example: Line Plot")
    plot.xlabel("X axis")
    plot.ylabel("Y axis")
    plot.show()

if __name__ == "__main__":
    main()
```

### Key characteristics:

- **Docstring at top** - Clear description of what the example demonstrates
- **Imports section** - All imports listed clearly
- **main() function** - Logic organized in a function
- **Comments** - Explain key steps, especially setup and configuration
- **Minimal complexity** - Focused on demonstrating ONE feature
- **Both backends** - Works with `GSP_BACKEND=matplotlib` and `GSP_BACKEND=datoviz`

## Example creation workflow

### Step 1: Determine example scope

Ask the user what they want to demonstrate:
- Simple line plot?
- Multi-series comparison?
- Real data visualization?
- Backend-specific features?

### Step 2: Write the example

Create a file in `/Users/jetienne/work/GSP_API/examples/example_<name>.py` following the template above.

Keep it:
- **Self-contained** - Can run with just `python example_<name>.py`
- **Educational** - Comments explain the "why" not just the "what"
- **Complete** - Includes data generation or loading

### Step 3: Test with both backends

```bash
cd /Users/jetienne/work/GSP_API

# Test Matplotlib
GSP_BACKEND=matplotlib python examples/example_<name>.py

# Test DatoViz
GSP_BACKEND=datoviz python examples/example_<name>.py
```

**Success criteria:**
- Script runs without errors
- Visualization appears (or file is created if headless)
- Both backends work (or gracefully skip if not available)

### Step 4: Update examples index (if applicable)

If there's an `examples/README.md` or index file, add the new example with:
- File name
- One-line description
- What it demonstrates

## Reporting results

After creating an example:

```
✓ Created: examples/example_<name>.py
✓ Tested with Matplotlib backend
✓ Tested with DatoViz backend
✓ Added to examples documentation

The example demonstrates [what it shows] and is ready to use.
```

## When to run this skill

- Creating new examples for the library
- Updating existing examples
- Demonstrating specific features
- Creating tutorials
- Documenting how to use the library
- User asks for example code
