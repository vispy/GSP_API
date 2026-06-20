# Datoviz v0.4 Backend Spec - Draft

Datoviz v0.4 is the flagship high-performance GPU backend for GSP.

The old GSP Datoviz adapter targeting Datoviz v0.3 should be treated as legacy mapping reference only.

Target mapping:

- GSP session -> Datoviz scene/app/view runtime;
- GSP figure/panel -> Datoviz figure/panel;
- GSP resources -> Datoviz scene buffers, textures, sampled fields;
- GSP visual families -> Datoviz v0.4 visual constructors;
- GSP queries -> Datoviz panel query system;
- GSP capabilities -> Datoviz capability snapshot.

M004 must identify exact API gaps before implementation.

## M004 assessment result

Detailed assessment lives in `docs/datoviz_v04_gap_analysis.md`.

The implementation target is the C-shaped Datoviz v0.4 scene/app API exposed through the top-level
Python facade (`import datoviz as dvz`) and raw ctypes bindings. Do not target the old v0.3-style
Python wrapper surface (`datoviz.App`, `datoviz.visuals`, `datoviz._panel`, `datoviz._figure`,
`datoviz._texture`): those modules/classes were absent in the inspected local v0.4 package.

### First backend slice target

| GSP concept | Datoviz v0.4 target | Status |
|---|---|---|
| Session/server | `dvz_scene()` plus app/view lifecycle | feasible |
| Figure/canvas | `dvz_figure(scene, width, height, flags)` | feasible |
| Panel/viewport | `dvz_panel()` or `dvz_panel_full()` | feasible; convert GSP pixel viewports to normalized panel desc |
| Point visual | `dvz_point()` plus `dvz_visual_set_data()` for `position`, `color`, `diameter` | feasible after point-size semantic alignment |
| Image visual | `dvz_image()` plus `position`, `texcoords`, sampled field or texture binding | feasible after image origin/interpolation confirmation |
| Capabilities | `dvz_capability_snapshot()` | feasible |
| Queries | `dvz_panel_query()` / `dvz_scene_poll_query()` | conceptually aligned; Python binding cannot yet decode `DvzQueryResult` fields |
| Capture | offscreen view capture or `dvz.capture()` | feasible for PNG screenshots only |

### Implementation constraints

- Use `DvzCapabilitySnapshot` to build GSP `CapabilitySnapshot` before planning.
- Treat screenshot capture as sRGB RGBA8 output, not scientific readback.
- Use sampled fields (`dvz_sampled_field`, `dvz_visual_set_field`) for scalar/color images where possible; `dvz_visual_set_texture` is a transitional RGBA8 convenience path.
- Do not claim query support in the Python GSP adapter until query results are decodable.
- Do not edit the Datoviz repository from this repo; create handoff tasks for Datoviz-side API or binding gaps.
