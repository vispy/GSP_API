# M148 - S035 navigation protocol validation

## Stage

S035 - Retained View2D Navigation and Pan/Zoom

## Status

Completed by local-main-codex.

## Summary

Implement protocol-owned dataclasses/enums/validation for S035 navigation actions, results, revision
tokens, diagnostics, and capability records.

## Deliverables

- Navigation action/result protocol models.
- Validation for finite pixel deltas, finite positive zoom factors, target panel/view ids, and stale
  revision diagnostics.
- Capability records for `interaction.view2d.navigation.v1` and retained-update placement.
- Focused unit tests.

## Stop Condition

Stop before backend runtime behavior if the ADR/spec baseline is not accepted.

## Result

Completed. Added `src/gsp/protocol/navigation.py` with S035 navigation actions, controller metadata,
result validation, diagnostic codes, and retained-update placement vocabulary. Exported the models
from `gsp.protocol`, added navigation capability/placement helpers to `CapabilitySnapshot`, and
covered the protocol model with focused tests.

Validation performed:

- `uv run python -m py_compile src/gsp/protocol/navigation.py src/gsp/protocol/capabilities.py src/gsp/protocol/__init__.py tests/test_navigation_protocol.py`
- `uv run ruff check src/gsp/protocol/navigation.py src/gsp/protocol/capabilities.py src/gsp/protocol/__init__.py tests/test_navigation_protocol.py`
- `uv run pytest tests/test_navigation_protocol.py tests/test_transform_protocol.py tests/test_layout_protocol.py -q`
- `uv run mypy src/gsp/protocol/ --strict --show-error-codes`
- `uv run pytest tests/ -q` (`449 passed, 3 skipped`)
