# P026 - Datoviz-Exact 2D Interaction and Axis Synchronization

## Prompt for ChatGPT Pro

You are advising on GSP_API, a Python visualization protocol/library that targets multiple backends, including Matplotlib as a strict reference and Datoviz v0.4-dev as the flagship GPU backend.

We need a design decision for 2D interaction. The user reports two issues:

1. During 2D interaction, the axes do not change when the viewport/view changes.
2. The desired behavior is exactly the same 2D interaction as Datoviz: same mouse convention, same constants, same sensitivity, same pan/zoom math.

Critical project constraint for this decision:

- This stage should not preserve legacy interaction or axes code for API compatibility.
- Breaking API compatibility is acceptable and preferred if it produces a cleaner, Datoviz-exact,
  canonical design.
- Legacy `vispy2.axes.AxesDisplay`, `AxesPanZoom`, `AxesManaged`, old viewport-event panzoom
  conventions, and approximate `base_scale` behavior should be treated as migration material only,
  not as public API that must continue to work unchanged.
- If the best design is to remove, replace, or deprecate old helpers immediately, recommend that
  directly. Do not propose compatibility shims unless they are strictly temporary and clearly marked
  for deletion.

Project authority/order:

1. PROJECT_CHARTER.md
2. ARCHITECTURE.md
3. SPEC_INDEX.md
4. spec/**
5. accepted ADRs in adr/** and .agent/decisions/**
6. LEGACY_MAP.md
7. existing source code

Relevant accepted GSP facts:

- `spec/navigation.md` is the accepted S035 authority for View2D navigation.
- S035 public navigation is canonical `View2D` updates through semantic actions: `pan_by`, `zoom_about`, `set_view`, and `reset_view`.
- Raw mouse, wheel, keyboard, touch, toolkit, browser, Matplotlib, Datoviz, and VisPy event streams are explicitly not public protocol objects.
- Strict GSP backends adapt native input events into semantic navigation actions and apply accepted `View2D` updates.
- Backend-native controllers such as Datoviz `dvz_view_panzoom()` are not strict GSP navigation unless their resulting state is synchronized back into canonical `View2D`.
- After accepted navigation, guides and data visuals must consume the same accepted `View2D` snapshot. Render/query/readback must identify matching view/layout snapshots where strictness is claimed.
- Datoviz guide/layout support is currently adapted/partial; native axes are available for review, but guide query and all-rendered guide contributions remain unsupported.

Current GSP implementation facts:

- `src/gsp/protocol/navigation.py` has `View2DNavigationInputAdapter`, default `zoom_base=1.1`.
- The adapter maps:
  - left drag to `PanByAction`
  - wheel to `ZoomAboutAction` with factor `zoom_base ** scroll_steps`
  - right drag to independent x/y `ZoomAboutAction` with factors:
    - `zoom_base ** (dx_px / (panel_width * 0.05))`
    - `zoom_base ** (dy_px / (panel_height * 0.05))`
- `src/gsp_datoviz/protocol_renderer.py` has `_DatovizLiveView2DNavigation`, which subscribes to Datoviz pointer input, converts pointer callbacks into the GSP adapter, applies canonical `View2D`, then calls `apply_retained_view2d_navigation()`.
- `apply_retained_view2d_navigation()` calls `apply_datoviz_data_view2d()`, which sets `dvz_panel_set_domain(panel, X/Y, min, max)` when available and then calls `dvz_panel_set_view2d(panel, panel_view)`.
- `configure_view2d_axes()` creates native Datoviz panel axes and configures tick policy, grid, labels, optional explicit ticks, and sets the panel domains for the initial `View2D`.
- Legacy `src/vispy2/axes/axes_display.py` generates axes as GSP primitives and rebuilds them only when `AxesDisplay.set_limits_dunit()` is called.
- Legacy `src/vispy2/axes/axes_panzoom.py` owns an independent pan/zoom implementation and updates `AxesDisplay` limits; it is not tied to canonical S035 `View2D`.

Current Datoviz source evidence from local checkout `/Users/cyrille/GIT/Viz/datoviz`, branch `v0.4-dev`, commit `32ad98848`:

Relevant file: `src/controller/panzoom.c`.

Constants:

```c
#define DVZ_PANZOOM_ZOOM_MIN_DEFAULT 1e-3f
#define DVZ_PANZOOM_ZOOM_MAX_DEFAULT 1e+4f

#if defined(__APPLE__)
#define DVZ_PANZOOM_ZOOM_DRAG_COEF  .003
#define DVZ_PANZOOM_ZOOM_WHEEL_COEF  12.0
#else
#define DVZ_PANZOOM_ZOOM_DRAG_COEF  .002
#define DVZ_PANZOOM_ZOOM_WHEEL_COEF 120.0
#endif
```

Coordinate conventions:

```c
_normalize_pos:
out[0] = -1.0f + 2.0f * in[0] / w;
out[1] = +1.0f - 2.0f * in[1] / h;

_normalize_shift:
out[0] = +2.0f * in[0] / w;
out[1] = -2.0f * in[1] / h;
```

Pan:

```c
pan[0] = pan_center[0] + shift[0] / zoom_x;
pan[1] = pan_center[1] + shift[1] / zoom_y;
```

Right-drag zoom:

```c
a = .5f * (w + h);
zoom_x = zoom_center_x * exp(DRAG_COEF * a * normalized_shift_x);
zoom_y = zoom_center_y * exp(DRAG_COEF * a * normalized_shift_y);
px = center_x * (1 / zoom_center_x - 1 / zoom_x) * zoom_x;
py = center_y * (1 / zoom_center_y - 1 / zoom_y) * zoom_y;
pan_x = pan_center_x - px / zoom_x;
pan_y = pan_center_y - py / zoom_y;
```

Wheel zoom:

```c
a = h / w;
d = dir[1] / 4.0f;
shift[0] = WHEEL_COEF * d;
shift[1] = -a * shift[0];
dvz_panzoom_zoom_shift(pz, shift, center_px);
dvz_panzoom_end(pz);
```

Pointer conventions in Datoviz:

- left drag pans;
- right drag zooms x/y;
- wheel zooms;
- double click resets.

Important design question:

Should GSP:

A. Keep S035 canonical `View2D` actions as the only strict public navigation model, but replace the current approximate adapter profile with a Datoviz-exact adapter profile that reimplements the Datoviz panzoom formulas and constants, producing canonical `View2D` updates?

B. Use Datoviz native `DvzPanzoom`/`dvz_view_panzoom()` as the implementation for Datoviz live interaction, then read back or resolve the resulting native panzoom visible extent and synchronize that into canonical `View2D` after each native interaction?

C. Support both, with one strict path and one native/demo path. If so, which is strict and how should capabilities/diagnostics name the other?

When answering, assume we are free to break existing Python-facing APIs in this area. Prefer one
coherent interaction stack over parallel legacy/new stacks. If the legacy axes/panzoom code conflicts
with canonical `View2D` or Datoviz-exact interaction, recommend deleting or rewriting it rather than
adapting around it.

Please decide the right architecture for GSP_API, considering:

- preserving backend-neutral public semantics;
- achieving exact Datoviz user feel;
- keeping axes/guides synchronized during pan/zoom and resize;
- avoiding duplicated stale formulas when Datoviz changes;
- feasibility with Python bindings currently available;
- conformance testing and capability reporting;
- avoiding leakage of Datoviz-native controller names into public GSP APIs.
- eliminating legacy compatibility layers and duplicated interaction semantics.

Expected output format:

1. Decision: choose A, B, C, or a clearly stated variant.
2. Rationale: 5-8 bullet points grounded in the facts above.
3. Axis synchronization model: specify exactly what state is authoritative and when axes/guides recompute.
4. Datoviz parity plan: specify how constants/formulas should be sourced or verified.
5. API/capability boundary: specify public names/concepts and private backend-only names.
6. Implementation steps: concise ordered list of tasks.
7. Tests/proofs: concise ordered list of tests/smokes needed before claiming support.
8. Risks/open questions: concise list.

Do not assume access to files outside this prompt.
