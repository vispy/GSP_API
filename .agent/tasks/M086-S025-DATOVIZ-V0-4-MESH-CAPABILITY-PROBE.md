# M086-S025 - S025 Datoviz v0.4 mesh capability probe

## Mission

M086

## Goal

Refresh Datoviz v0.4 mesh API evidence before implementing or rejecting the adapter path.

## Status

Completed.

## Deliverables

- Probe installed bindings and sibling `../datoviz` headers/examples.
- Record retained mesh constructors, attribute names, material/lighting support, and capture requirements.
- Add banned legacy-symbol checks if relevant.

## Acceptance

- Mission output is committed or explicitly reported as blocked.
- Mission Control status is updated before closeout.
- Validation is proportional to the touched surface.

## Stop Conditions

- Stop if local Datoviz evidence conflicts with M083 semantics.


## Completed

- Added mesh symbol and capability evidence to the Datoviz v0.4 visual QA probe.
- Probes retained mesh constructor, geometry/index upload, material/depth helpers, and deferred texture evidence.
- Expanded sibling source scanning to include Datoviz C feature examples as well as visual examples and headers.
- Added focused probe test with injected fake facade/raw modules.
- Validation: `uv run pytest tests/test_visual_qa_harness.py tests/test_datoviz_v04_protocol_renderer.py -q`; `python3 -m compileall -q src/gsp/qa/visual/datoviz_probe.py`; `git diff --check`.
