# S050 Datoviz Live Point/Image Payload Evidence

Date: 2026-07-03

Mission: M216 - S050 Datoviz live point/image payload parity evidence

## Outcome

Completed with a narrowed Datoviz query capability posture.

The current local Datoviz v0.4-dev binding exposes the current query API as
`dvz_panel_query_px()`, plus `dvz_query_request()`, `dvz_scene_poll_query()`, and a decodable
`DvzQueryResult`. GSP now uses the current `dvz_panel_query_px()` symbol only.

Live runtime evidence proves point identity queries, but not image texel/color/value parity.

## Evidence

Artifact:

- `artifacts/visual_qa/s050/m216-live-query-payload/smoke.json`

Local Datoviz checkout used read-only:

- path: `/Users/cyrille/GIT/Viz/datoviz`
- branch: `v0.4-dev`
- commit: `a9492af6526fbb722e2c0783811758f1b15be10e`
- imported module: `/Users/cyrille/GIT/Viz/datoviz/datoviz/__init__.py`

The sibling checkout had pre-existing dirty files and was not modified.

## Runtime Result

The current smoke reports:

| Field | Result |
|---|---|
| `query_ready` | `true` |
| `query_modes` | `panel-query`, `point-item`, `view3d-ray` |
| overlapping query | `hit`, frontmost `image`, visual id present, no item/texel/color/value |
| isolated point query | `hit`, `visual_family="point"`, `item_id=0`, no displayed color/value |
| isolated image query | `hit`, `visual_family="image"`, visual id present, no `texel`, displayed color, or value |

Synthetic `DvzQueryResult` field readback still confirms that the generated ctypes struct exposes
`item_id`, `texel_id`, `display_rgba`, scalar/vector values, and labels. The remaining gap is live
runtime population of those fields for image/color/value payloads.

## Decision

Advertise only what the live runtime proves:

- keep `panel-query`;
- keep `point-item` for point identity;
- remove `image-texel` from Datoviz capability advertisement;
- reject non-identity Datoviz live data query payload requests unless an explicitly supported scalar
  extension payload can be decorated from retained GSP-side metadata.

No public query contract was weakened. No Datoviz files were edited.

## Validation

Passed:

```bash
PYTHONPATH=src python -m pytest \
  tests/test_datoviz_v04_protocol_renderer.py \
  -k 'query_binding or panel_query or query_panel or imported_datoviz_query or capability'
```

Result: `19 passed, 124 deselected`.

Passed:

```bash
PYTHONPATH=src python -m pytest tests/test_datoviz_v04_probe.py -q
```

Result: `5 passed`.

Passed:

```bash
PYTHONPATH=/Users/cyrille/GIT/Viz/datoviz:src \
  python tools/datoviz_v04_smoke.py --require-query-ready --require-live-query-hit
```

Result: `ok=true`, with the narrowed query modes and payload evidence above.
