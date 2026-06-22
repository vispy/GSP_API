# M012 - Strict tick resolver and guide-provider foundation

## Goal

Implement the deterministic reference foundation for semantic guide/tick realization:

- `auto-linear-nice-v0` tick resolution;
- explicit tick pass-through semantics;
- protocol/reference tests for strict guide intent;
- Matplotlib strict-provider readiness without relying on Matplotlib native locator output;
- preservation of the invariant that generated guides/axes are not appended to `Figure.visuals()`.

This mission prepares M013 to perform actual Matplotlib guide/title/grid rendering.

## State

Planned.

## Required reading

- `PROJECT_CHARTER.md`
- `ARCHITECTURE.md`
- `adr/ADR-0005-axis-realization-providers-v04dev.md`
- `.agent/consultations/P003-response.md`
- `src/gsp/protocol/panels.py`
- `src/gsp/protocol/guides.py`
- `src/gsp/protocol/capabilities.py`
- `src/gsp_matplotlib/capabilities.py`
- `src/gsp_datoviz/capabilities.py`
- `src/vispy2/protocol.py`
- `tests/test_axis_provider_capabilities.py`
- `tests/test_vispy2_protocol_mvp.py`
- `tests/test_datoviz_v04_protocol_renderer.py`

## Expected tasks

- Add a small pure-Python deterministic tick resolver for `auto-linear-nice-v0`.
- Keep the resolver backend-independent.
- Define resolver behavior for normal increasing linear limits, degenerate limits, explicit ticks and labels, and invalid/non-finite limits.
- Add tests proving auto ticks are deterministic and not delegated to Matplotlib locators.
- Add tests proving explicit tick values and labels are preserved exactly at the protocol/reference layer.
- Add tests that guide/tick preparation does not mutate `Figure.visuals()`.
- Confirm Matplotlib capability declaration remains strict only for semantics it can support.
- Confirm Datoviz capability behavior remains provider-gated.

## Allowed paths

- `src/gsp/protocol/**`
- `src/gsp_matplotlib/**`
- `src/vispy2/**`, only for tests or minimal integration required to preserve current invariants
- `tests/**`
- `spec/**`, only for brief resolver/fixture notes
- `.agent/tasks/**`
- `.agent/missions/**`
- `.agent/status.json`
- `STATUS.md`

## Forbidden paths

- External Datoviz repositories.
- Datoviz v0.3 plotting APIs or old `panel.axes(...)` examples.
- Matplotlib native auto tick output as the GSP conformance definition.
- Appending generated axes, guides, ticks, labels, or titles to `Figure.visuals()`.
- Real remote fetch, credentials, cache, retry, prefetch, progressive loading, or plugin-loading work.

## Acceptance criteria

- A deterministic `auto-linear-nice-v0` resolver exists and is covered by unit tests.
- Explicit ticks and labels are preserved exactly through the protocol/reference layer.
- Auto tick fixtures are stable across test runs and do not depend on Matplotlib locators.
- Existing point/image/query/VisPy2 MVP tests still pass.
- `Figure.visuals()` continues to return user data visuals only.
- Matplotlib remains declared strict only for the current semantic slice.
- Datoviz behavior remains provider-gated and skip-clean when v0.4 bindings are unavailable.

## Tests

```bash
PYTHONPATH=. uv run pytest tests/test_tick_resolver.py
PYTHONPATH=. uv run pytest tests/test_axis_provider_capabilities.py
PYTHONPATH=. uv run pytest tests/test_vispy2_protocol_mvp.py
PYTHONPATH=. uv run pytest tests/test_datoviz_v04_protocol_renderer.py
PYTHONPATH=. uv run pytest
```

## Stop conditions

Stop if:

- `TickSpec` lacks enough information to distinguish explicit ticks from auto resolver requests;
- `AxisGuide` requires an ADR-level model change;
- correct behavior would require making Matplotlib native locator output normative;
- implementation would append generated guide/tick/title objects into `Figure.visuals()`;
- Datoviz capability changes would require guessing behavior from unavailable Python bindings.

