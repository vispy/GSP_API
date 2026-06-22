# M030 - Datoviz v0.4-dev binding activation and live runtime smoke

## Goal

Activate the local Datoviz v0.4-dev Python facade for GSP smoke testing and identify remaining live
runtime blockers.

## State

Completed.

## Required reading

- `spec/backends/datoviz.md`
- `src/gsp_datoviz/protocol_renderer.py`
- `src/gsp_datoviz/capabilities.py`
- `src/gsp_datoviz/query.py`
- `tests/test_datoviz_v04_protocol_renderer.py`
- `../datoviz/build/manylinux-x86_64/wheel-stage/datoviz/__init__.py`
- `../datoviz/build/manylinux-x86_64/wheel-stage/datoviz/_ctypes.py`

## Expected tasks

- Confirm the default GSP environment still imports Datoviz 0.3.5.
- Activate the local v0.4-dev wheel-stage with `PYTHONPATH` and `LD_LIBRARY_PATH`.
- Add a durable GSP smoke tool for the v0.4 facade.
- Exercise adapter construction, point/image visual setup, sampled-field readiness, capture
  readiness, and bounded query gating.
- Record any binding blocker without editing the Datoviz repository.

## Allowed paths

- `tools/**`
- `tests/**`
- `src/gsp_datoviz/**`
- `spec/backends/datoviz.md`
- `.agent/**`

## Forbidden paths

- Datoviz repository edits.
- GSP lockfile dependency upgrade to Datoviz 0.4-dev without a release/dependency decision.
- Claiming query readiness while `DvzQueryResult` lacks Python-visible fields.
- Forcing GPU/headless capture as a mandatory local test.

## Acceptance criteria

- A smoke command can activate the local v0.4-dev wheel-stage and import the `dvz_*` facade.
- Smoke reports sampled-field and capture readiness.
- Smoke reports query readiness separately and verifies required `DvzQueryResult` fields when the binding is complete.
- Default GSP test suite remains clean with the pinned Datoviz 0.3.5 dependency.

## Result

Completed by local-main-codex. Added `tools/datoviz_v04_smoke.py`, verified v0.4-dev wheel-stage
facade activation, fixed the sampled-field slot-name call for ctypes `c_char_p`, made the static
capability test independent of the active Datoviz import, and verified the updated Datoviz query
binding after commit `8bb192c2da6df70279eedac5b2eaed9f45aab96c`.

Smoke command:

```bash
PYTHONPATH=../datoviz/build/manylinux-x86_64/wheel-stage:. \
LD_LIBRARY_PATH=../datoviz/build/manylinux-x86_64/wheel-stage/datoviz:../datoviz/build/manylinux-x86_64/src \
uv run python tools/datoviz_v04_smoke.py
```

Result:

- v0.4 facade: ready;
- sampled-field binding: ready;
- capture binding: ready;
- adapter point/image setup: ready;
- query binding: ready;
- promoted query modes: `panel-query`, `point-item`, `image-texel`;
- required `DvzQueryResult` fields: present and assignment/readback verified;
- bounded query wrapper: returns `dropped` when no resolved result is available during the single poll.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 145 passed, 6 skipped. The v0.4 wheel-stage path test reported 34 passed.

## Stop conditions

Stop before Datoviz repository edits, lockfile dependency upgrade, mandatory GPU/headless capture,
or query readiness claims while `DvzQueryResult._fields_` is missing.
