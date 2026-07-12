# Contributing

Public documentation follows the authority order in `PROJECT_CHARTER.md`. A source implementation
does not redefine protocol semantics when it conflicts with an accepted specification.

Before submitting a change:

```bash
uv run pytest
uv run mypy src
uv run ruff check .
uv run mkdocs build --strict
```

Protocol changes must update the normative specification, capability identifiers, diagnostics,
tests, and affected backend profiles together. A screenshot can support visual review but cannot
promote strict support without semantic evidence.
