# Datoviz v0.4 Header And Binding Evidence Refresh

Status: M018 evidence refresh.

Date: 2026-06-22.

## Summary

The sibling Datoviz checkout at `../datoviz` is on branch `v0.4-dev` at commit `bc9adbb40`.
Its headers expose the v0.4 query, capability, sampled-field, and native axis APIs needed for the
next GSP Datoviz parity work.

The current GSP Python environment does not expose those APIs. `import datoviz` resolves to the
installed package `datoviz 0.3.5` at `.venv/lib/python3.13/site-packages/datoviz/__init__.py`, with
no public `dvz_*` symbols and no `DvzQueryResult` or `DvzCapabilitySnapshot` ctypes classes.

Result: keep the GSP Datoviz adapter capability-gated. Header evidence is positive, but runtime
v0.4 binding evidence is not available in this environment until a v0.4-dev source-built Python
facade/raw binding is installed or put on `PYTHONPATH`.

## Local Datoviz Header Evidence

Checked in `../datoviz`:

| Evidence | Result |
|---|---|
| Branch | `v0.4-dev` |
| Commit | `bc9adbb40` |
| Dirty state | `data` modified in sibling checkout; treated as read-only |
| Query API header | `include/datoviz/scene/interaction.h` |
| Query result struct | `include/datoviz/scene/types.h` |
| Capability snapshot header | `include/datoviz/scene/frame_plan.h` |
| Sampled-field header | `include/datoviz/scene/field.h` |
| Axis API header | `include/datoviz/scene.h` |

Confirmed header symbols:

- `dvz_query_request()`
- `dvz_panel_query_px()`
- `dvz_scene_poll_query()`
- `dvz_panel_query_now_px()`
- `dvz_capability_snapshot()`
- `dvz_sampled_field()`
- `dvz_sampled_field_set_data()`
- `dvz_visual_set_field()`
- `dvz_panel_axis()`
- `dvz_axis_set_label()`
- `dvz_axis_set_tick_policy()`
- `dvz_axis_set_grid()`
- `dvz_panel_visible_domain()`
- `dvz_panel_transform_point()`
- `dvz_panel_set_domain()`

The current header `DvzQueryResult` struct includes the fields GSP needs for a bounded decoder:

- request/frame identity: `request_id`, `freshness_serial`
- status and hit: `status`, `hit`
- scene identity: `scene_id`, `figure_id`, `panel_id`, `visual_id`, `visual_family`, `profile`
- panel/framebuffer positions: `panel_position`, `framebuffer_position`
- raw and resolved targets: `raw_parent_target`, `raw_parent_id`, `raw_target`, `raw_id`,
  `resolved_parent_target`, `resolved_parent_id`, `resolved_target`, `resolved_id`
- item payload ids: `item_id`, `group_id`, `auxiliary_id`, `instance_id`, `face_id`,
  `primitive_id`, `vertex_id`, `voxel_id`, `texel_id`
- coordinate payloads: `visual_position`, `data_position`, `uvw`, guarded by `has_*` flags
- displayed and source-value payloads: `depth`, `display_rgba`, `value_kind`, `scalar`, `vector`,
  `category_id`, `label`, `unit`, `scale`

## Current GSP Python Binding Evidence

Checked from `/home/cyrille/GIT/Viz/GSP_API` with `PYTHONPATH=. uv run python`.

| Python-visible object | Present |
|---|---:|
| `datoviz.__version__` | `0.3.5` |
| `dvz_capability_snapshot` | no |
| `DvzCapabilitySnapshot` | no |
| `dvz_panel_query_px` | no |
| `dvz_panel_query_now_px` | no |
| `dvz_scene_poll_query` | no |
| `DvzQueryRequest` | no |
| `DvzQueryResult` | no |
| `dvz_panel_axis` | no |
| `dvz_axis_set_label` | no |
| `dvz_axis_set_tick_policy` | no |
| `dvz_axis_set_grid` | no |
| `dvz_sampled_field` | no |
| `dvz_sampled_field_set_data` | no |
| `dvz_visual_set_field` | no |

## GSP Implications

- The existing `gsp_datoviz.protocol_renderer` skip-clean behavior is still correct in this
  environment.
- Do not advertise Datoviz query modes from GSP yet.
- Do not replace static Datoviz capabilities with runtime translation until
  `DvzCapabilitySnapshot` is Python-visible.
- A future decoder can be specified against the current header field list, but implementation tests
  need either synthetic ctypes-compatible objects or a source-built v0.4-dev binding.
- The next executable Datoviz mission should first establish the v0.4 Python facade/raw binding
  import path, then implement bounded capability translation and query-result decoding.
