# M018 - Datoviz v0.4 header/binding evidence refresh

## Goal

Refresh Datoviz v0.4 header and Python-binding evidence before the next query/capability parity
implementation mission.

## State

Completed.

## Required reading

- `spec/backends/datoviz.md`
- `docs/datoviz_v04_gap_analysis.md`
- `.agent/tasks/DATOVIZ-V04-QUERY-BINDING.md`
- `.agent/tasks/DATOVIZ-V04-CAPABILITY-PARITY.md`
- `.agent/tasks/DATOVIZ-V04-PYTHON-FACADE-CONTRACT.md`
- `../datoviz/include/datoviz/scene/types.h`
- `../datoviz/include/datoviz/scene/interaction.h`
- `../datoviz/include/datoviz/scene/frame_plan.h`
- `../datoviz/include/datoviz/scene/field.h`

## Expected tasks

- Inspect `../datoviz` as read-only authority.
- Record branch, commit, dirty-state caveat, and relevant v0.4 header symbols.
- Check active GSP Python import shape for Datoviz v0.4 facade/raw bindings.
- Update Datoviz docs/spec/tasks with the current blocker state.

## Allowed paths

- `docs/**`
- `spec/backends/datoviz.md`
- `.agent/**`

## Forbidden paths

- External Datoviz repository edits.
- Runtime Datoviz query/capability implementation.
- Claiming query support in `gsp_datoviz` while active bindings are Datoviz 0.3.5.

## Acceptance criteria

- Evidence file records current local header and Python-binding findings.
- Datoviz backend spec no longer overstates runtime Python field availability.
- Query/capability handoff tasks identify the v0.4 Python binding import path as the next blocker.
- Full test suite passes.

## Result

Completed by local-main-codex. Added `docs/datoviz_v04_binding_evidence.md`, updated the Datoviz
gap analysis/spec, and corrected Datoviz handoff tasks to distinguish v0.4-dev header readiness
from the current GSP environment's Datoviz 0.3.5 binding.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 105 passed, 1 skipped.

## Stop conditions

Stop if the work requires editing `../datoviz`, installing a new Datoviz binding, or making protocol
query/capability design decisions beyond recording the evidence.
