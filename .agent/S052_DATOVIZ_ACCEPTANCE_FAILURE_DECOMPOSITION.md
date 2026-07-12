# S052 Datoviz acceptance failure decomposition

Date: 2026-07-12

Mission: M234

## Finding

The three S051 native failures shared one trigger: Datoviz panel-frame snapshot readback accepted
generated ctypes record names as sufficient evidence even though the installed record layouts were
empty forward declarations.

At Datoviz `v0.4-dev` commit `ff62b3256f1de7dd2df2ee890c99968715789a27`:

| Record | `ctypes.sizeof()` | `_fields_` |
|---|---:|---|
| `DvzPanelFrameInfo` | 0 | absent |
| `DvzGuideLayout` | 0 | absent |
| `DvzGuideHit` | 0 | absent |

With default VisPy2 axis guides, the adapter called `dvz_panel_frame_info()` with a pointer to a
zero-byte `DvzPanelFrameInfo`. An isolated reproduction failed in
`_datoviz_frame_guide_boxes`/partial layout resolution before `report.json` was written. Removing
axis guides from the otherwise identical primitives scene rendered and captured successfully,
showing that point/marker/segment/path execution was not the failure trigger. Text and mesh scenes
also inherit default VisPy2 guides, so their S051 failures did not establish text- or mesh-specific
native faults.

## Hardening

Panel-frame snapshot and guide-query readiness now reject zero-size generated ctypes structures
before any native copy call. Ordinary Python test doubles remain supported. The renderer then treats
partial layout snapshot readback as unavailable while preserving the completed render and its
structured diagnostic; it does not relabel native signals as unsupported.

The refreshed pack at `artifacts/visual_qa/s052/rc1-preflight-hardened/` records:

| Outcome | Count |
|---|---:|
| Matplotlib strict | 4 |
| Datoviz adapted | 3 |
| Datoviz unsupported | 2 |
| Native crashes | 0 |

Primitives, text, and untextured mesh render through Datoviz as adapted pending promotion audit.
Scalar image plus colorbar and Texture2D remain explicitly unsupported. No capability was promoted.

## Lifecycle evidence

`artifacts/visual_qa/s052/lifecycle/lifecycle_probe.json` records five isolated
create/capture/report/close iterations for each surviving Datoviz case:

- 15 attempted;
- 15 clean exits;
- 15 complete reports;
- 15 complete artifacts;
- zero timeouts or native/teardown failures.

This establishes a bounded offscreen lifecycle baseline. It does not establish live-window event
loop ownership, non-blocking display, retained updates, or a public session contract.

## Public API decision

ADR-0033 remains unchanged. The evidence removes the S051 native-crash blocker but is insufficient
by itself to publish `open_session()`: live blocking/non-blocking ownership and deterministic window
cleanup still need a separate preview-lifecycle proof.
