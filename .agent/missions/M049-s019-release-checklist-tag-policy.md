# M049 - S019 release checklist and tag policy

## Stage

S019 - Packaging, docs, and examples

## Status

Completed by local-main-codex.

## Summary

Recorded the explicit release checklist and tag/publish policy needed to close S019. The policy keeps
tagging and publication as explicit user-approved operations, requires a clean validation surface, and
documents optional backend constraints.

## Validation

- `PYTHONPATH=. uv run mypy src/ --strict --show-error-codes`
- `PYTHONPATH=. uv run pytest -q`
- `uv run mkdocs build --strict`
- `uv build`
- `python -m json.tool .agent/status.json >/dev/null`
- `git diff --check`
