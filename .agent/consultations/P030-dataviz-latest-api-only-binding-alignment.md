# P030 - Datoviz Latest-API-Only Binding Alignment

## Prompt for ChatGPT Pro

You are advising on GSP_API, a Python visualization protocol/adapter project, and its Datoviz v0.4 backend. The project owner explicitly wants the long-term architecture to use the latest Datoviz C API and latest generated Python bindings only. They do not want local compatibility shims, legacy symbol support, or fake/mock-driven acceptance for this work.

Give a concrete architecture and implementation decision for aligning GSP's Datoviz adapter to the current Datoviz v0.4-dev API.

Relevant project facts:

- GSP_API repo branch: `agentic-gsp-vispy2`.
- Datoviz sibling checkout path: `/Users/cyrille/GIT/Viz/datoviz`.
- Datoviz branch: `v0.4-dev`.
- Datoviz commit inspected: `f5b81a397e3be69ecfffbffa88754c1c227e6820`.
- Datoviz checkout has pre-existing unrelated dirty state: `data` modified and `paper/paper.pdf` untracked. Do not rely on editing those.
- GSP currently has mission M214: "S050 Datoviz coordinate-space enum compatibility".
- M214 was originally scoped as a GSP-side compatibility fix, but the owner rejected that direction and requested latest API/latest bindings only.
- GSP must not promote Datoviz colorbar strictness or strict opaque depth until runtime evidence is complete.
- GSP must not edit the Datoviz checkout unless explicitly approved.

Observed current Datoviz Python facade facts from `PYTHONPATH=/Users/cyrille/GIT/Viz/datoviz python`:

```text
datoviz.__file__ = /Users/cyrille/GIT/Viz/datoviz/datoviz/__init__.py

Coordinate-space symbols:
DVZ_COORD_VIEW: absent
DVZ_COORD_DATA: absent
DVZ_VISUAL_COORD_VIEW: present, value 0
DVZ_VISUAL_COORD_DATA: present, value 1
DvzVisualCoordSpace: present
DvzVisualCoordSpace members:
  DVZ_VISUAL_COORD_DATA
  DVZ_VISUAL_COORD_PANEL
  DVZ_VISUAL_COORD_VIEW

Image/field symbols:
dvz_visual_set_texture: absent
dvz_visual_set_texture_rgba8: present
dvz_sampled_field_desc: present
dvz_field_data_view: present
dvz_sampled_field: present
dvz_sampled_field_set_data: present
dvz_visual_set_field: present

View3D camera/retained visual symbols:
dvz_panel_set_camera: absent
dvz_panel_view3d_desc: present
dvz_panel_set_view3d_desc: present
dvz_panel_camera: present
dvz_camera_desc: present
dvz_camera_set_orthographic_bounds: present
DvzPanelFrameInfo: present
```

Observed Datoviz C source/header facts at the same checkout:

```text
include/datoviz/scene/enums.h defines:
  DVZ_VISUAL_COORD_VIEW = 0
  DVZ_VISUAL_COORD_DATA = 1
  DVZ_VISUAL_COORD_PANEL = 2

include/datoviz/scene.h exposes:
  dvz_visual_set_texture_rgba8(...)
  dvz_visual_set_texture_r32f(...)

include/datoviz/scene/field.h exposes:
  dvz_sampled_field_desc()
  dvz_sampled_field(...)
  dvz_sampled_field_set_data(...)
  dvz_sampled_field_destroy(...)

The generated Python `_ctypes.py` contains:
  class DvzVisualCoordSpace:
    DVZ_VISUAL_COORD_VIEW = 0
    DVZ_VISUAL_COORD_DATA = 1
    DVZ_VISUAL_COORD_PANEL = 2
  module constants:
    DVZ_VISUAL_COORD_VIEW
    DVZ_VISUAL_COORD_DATA
    DVZ_VISUAL_COORD_PANEL
```

Current GSP adapter problem areas:

1. GSP's `src/gsp_datoviz/protocol_renderer.py` still uses or validates older names:
   - `DVZ_COORD_VIEW`
   - `DVZ_COORD_DATA`
   - `dvz_visual_set_texture`
   - `dvz_panel_set_camera`
2. The local compatibility path would have added aliases/fallbacks accepting both old and current names. The owner rejected that approach.
3. The desired approach is to update GSP to the latest Datoviz API contract and remove legacy-name support from this path.
4. Existing tests include many fake Datoviz facade classes. The owner does not want fake/mock-driven acceptance for this API alignment. Unit fakes may still exist elsewhere in the project, but the acceptance criteria for this work should be real generated-binding smoke and real Datoviz review-pack evidence.

Recent runtime evidence before rollback:

- A local compatibility patch was briefly tested and then removed.
- With compatibility patches, the S028 colorbar review-pack case rendered successfully in Datoviz and Matplotlib. This showed the current Datoviz runtime can render the colorbar path if GSP stops requiring stale symbols.
- The S050 strict-depth View3D case advanced past coordinate-space/import blockers but stopped at `Datoviz View3D camera binding is unavailable: missing dvz_panel_set_camera`, indicating GSP's View3D camera gate is stale relative to the retained `dvz_panel_view3d_desc` / `dvz_panel_set_view3d_desc` API.
- Those patch-generated artifacts were removed; do not treat them as committed evidence.

Question:

What is the correct latest-API-only architecture for GSP's Datoviz adapter now?

Please decide:

1. The exact Datoviz C/Python API symbols GSP should require for the current supported Datoviz backend.
2. Which legacy symbols GSP should delete from required checks and implementation paths.
3. Whether GSP should use sampled fields exclusively for images, or allow `dvz_visual_set_texture_rgba8` as a current API fallback.
4. Whether GSP View3D setup should use only retained panel View3D descriptors (`dvz_panel_view3d_desc`, `dvz_panel_set_view3d_desc`, `dvz_panel_camera`) and drop `dvz_panel_set_camera`.
5. How GSP should validate that generated Python bindings match the latest C API without relying on fake/mock acceptance.
6. How M214 should be re-scoped so it is not a "compatibility shim" mission but a latest-binding alignment mission.
7. Whether any Datoviz-side binding generation or C API work is required before GSP implementation should proceed.

Constraints:

- Do not propose local aliases that support both old and new symbol names as the primary architecture.
- Do not propose accepting fake/mock tests as the acceptance gate.
- Do not propose promoting Datoviz colorbar strictness or strict opaque depth based only on import/symbol checks.
- If Datoviz API or binding generation must change, say exactly what should change and what evidence should be produced.
- Keep the plan implementable by a coding agent in this repo.

Expected output format:

```text
Decision:
- [Clear recommendation: latest-only GSP adapter update now / Datoviz-side binding work first / stop and defer]

Required Datoviz API Contract:
| Area | Required C/Python symbols | Notes |

Legacy Symbols To Remove From GSP:
| Legacy symbol/path | Replacement | Migration notes |

GSP Implementation Plan:
1. ...
2. ...

Validation Plan:
1. Generated binding smoke checks:
   - exact command(s)
   - exact required assertions
2. Runtime review-pack checks:
   - exact command(s)
   - expected status
3. Tests/docs to update:
   - exact files and intent

M214 Rescope:
- New mission title
- Scope
- Stop conditions
- Acceptance criteria

Risks / Blockers:
- ...
```
