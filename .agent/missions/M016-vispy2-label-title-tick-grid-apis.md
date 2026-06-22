# M016 - VisPy2 label/title/tick/grid APIs

## Goal

Implement public VisPy2 guide APIs that emit semantic `AxisGuide`, `TickSpec`, and
`PanelTextGuide` intent.

## State

Completed.

## Required reading

- `.agent/consultations/P003-response.md`
- `spec/vispy2/api.md`
- `src/vispy2/protocol.py`
- `src/gsp/protocol/guides.py`
- `src/gsp/protocol/ticks.py`
- `tests/test_vispy2_protocol_mvp.py`

## Expected tasks

- Add public APIs for x/y labels, title, explicit x/y ticks, and grid visibility.
- Preserve semantic guide objects as protocol intent.
- Keep generated guides out of `Figure.visuals()`.
- Render through the Matplotlib reference path using S012 guide semantics.

## Allowed paths

- `src/vispy2/**`
- `tests/**`
- `spec/vispy2/**`
- `.agent/**`
- `STATUS.md`

## Forbidden paths

- Backend-provider implementation details in the public VisPy2 API.
- General Matplotlib compatibility beyond the bounded guide API names.
- Query-scope architecture.
- Adding guide-generated primitives to the user visual stream.

## Acceptance criteria

- `Axes.set_xlabel()`, `set_ylabel()`, `set_title()`, `set_xticks()`, `set_yticks()`, and `grid()`
  update semantic protocol guides.
- Getter methods expose the stored label/title/tick state where useful.
- Matplotlib reference rendering honors the emitted labels, title, ticks, and grid intent.
- `Figure.visuals()` remains data visuals only.
- Full test suite passes.

## Result

Completed by local-main-codex. Added bounded VisPy2 guide APIs backed by semantic protocol guide
objects and tests for guide structure, getters/title clearing, Matplotlib reference rendering, and
data-visual stream invariants.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 100 passed, 1 skipped.

## Stop conditions

Stop if a public API would expose backend-provider details, require broad Matplotlib compatibility,
or mutate user visual lists with generated guide primitives.
