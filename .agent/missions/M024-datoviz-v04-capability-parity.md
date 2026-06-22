# M024 - Datoviz v0.4 capability parity

## Goal

Translate Datoviz v0.4 capability snapshots into GSP `CapabilitySnapshot` without overclaiming
query/runtime support.

## State

Completed.

## Required reading

- `.agent/tasks/DATOVIZ-V04-PARITY-NEXT-PACK.md`
- `.agent/tasks/DATOVIZ-V04-CAPABILITY-PARITY.md`
- `spec/backends/datoviz.md`
- `src/gsp_datoviz/protocol_renderer.py`
- `src/gsp_datoviz/capabilities.py`
- `tests/test_datoviz_v04_protocol_renderer.py`
- `../datoviz/include/datoviz/scene/types.h`
- `../datoviz/src/scene/frame_plan/capabilities.c`

## Expected tasks

- Add a bounded Datoviz-to-GSP capability translator.
- Use `dvz_capability_snapshot()` when the active v0.4 Python facade exposes it.
- Preserve ambiguous/raw Datoviz fields in metadata.
- Keep Datoviz query support unadvertised until query decode parity lands.
- Add fake snapshot tests and skip-clean real runtime smoke.

## Allowed paths

- `src/gsp_datoviz/**`
- `tests/**`
- `spec/backends/datoviz.md`
- `.agent/**`

## Forbidden paths

- Datoviz runtime query implementation.
- Datoviz repository edits.
- Old Datoviz v0.3 `App` / `visuals` API assumptions.
- Tiled-source or sampled-field implementation.

## Acceptance criteria

- Capability translation tests use a fake/synthetic Datoviz snapshot object.
- Real `dvz_capability_snapshot()` smoke skips cleanly if the active Datoviz binding is unavailable.
- Query modes remain empty until Datoviz query decoding is implemented.
- Full test suite passes.

## Result

Completed by local-main-codex. Added conservative Datoviz capability translation, raw capability
metadata preservation, runtime renderer integration, skip-clean capability smoke, and spec notes.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 130 passed, 2 skipped.

## Stop conditions

Stop before query decode/runtime query implementation, Datoviz repo edits, sampled-field parity, or
tiled-source support.
