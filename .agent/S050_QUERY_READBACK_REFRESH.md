# S050 Query/Readback Refresh

Generated: 2026-07-03

## Result

M205 refreshed Datoviz query/readback status wording without changing public semantics.

## Updated Boundary

| Area | Current boundary |
|---|---|
| Data-scope point/image query | Bounded queue/poll/decode path remains supported when v0.4 query bindings are present. |
| Guide/all-rendered query | Capability-gated through Datoviz panel-frame guide hit/readback APIs; unsupported when those APIs or matching snapshot ids are unavailable. |
| `hit_policy=all` | Still unsupported in the Datoviz path. |
| Extension payloads | Unsupported except accepted scalar/query payload decoration paths. |
| Scientific/raw readback | Still deferred; PNG capture is screenshot/export only. |
| Mesh-triangle picking | Still unadvertised; blocked on upstream Datoviz face/triangle query and freshness API evidence from M200. |

## Validation

- `PYTHONPATH=src python -m pytest tests/test_datoviz_v04_protocol_renderer.py::test_datoviz_panel_frame_guide_query_returns_hit_with_matching_snapshot_id tests/test_datoviz_v04_protocol_renderer.py::test_datoviz_capabilities_report_native_guide_query_when_frame_hit_api_exists tests/test_datoviz_v04_protocol_renderer.py::test_query_panel_rejects_unadvertised_scopes_and_policies tests/test_datoviz_v04_protocol_renderer.py::test_datoviz_capabilities_promote_png_output_only_when_capture_binding_is_ready tests/test_datoviz_v04_protocol_renderer.py::test_datoviz_renderer_mesh_triangle_pick_reports_structured_unsupported`

## Stop Conditions Preserved

- No Datoviz mesh-triangle picking capability was advertised.
- No public query semantics changed.
- No sibling Datoviz files were edited.
