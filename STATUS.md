# Project Status

Canonical machine-readable status lives in `.agent/status.json`.

Use:

```bash
tools/agentctl brief
tools/agentctl review-now
tools/agentctl next
```

Current state:

- Completed through S022 remote source family selection and consultation.
- Current stage: S023 Visual Families v1 and Manual Visual QA Foundation.
- S023 progress: M064-M068 complete; M069-M072 remain draft.
- M064 Datoviz v0.4 API audit and probe is complete.
- M065 visual QA harness foundation is complete.
- M066 PointVisual v1 and Datoviz retained point path is complete.
- M067 MarkerVisual v1 is complete.
- M068 SegmentVisual v1 is complete.
- Datoviz v0.4 parity milestone reached: S023 point, marker, nearest-image, and point-over-image
  cases now render in both Matplotlib and Datoviz with good-enough visual/color parity in the
  regenerated `s023_all_cases.png` contact sheet.
- Next mission: M069 PathVisual v1.

Notes:

- M006 accepted ADR-0003 as the GSP v0.1 vertical-slice mini-contract.
- The v0.1 conformance baseline lives under `fixtures/conformance/`.
- The local in-process path remains direct Python objects/NumPy/memoryview and does not require JSON/base64.
- M007 added a bounded Datoviz v0.4 protocol renderer using the local C-shaped `dvz_*` facade.
- Datoviz query support remains deferred until Python can decode `DvzQueryResult`.
- M008 added an experimental VisPy2 producer MVP that emits GSP protocol point/image visuals and renders through the Matplotlib reference backend.
- M009 hardened query statuses, query capability checks, and Datoviz query handoff tasks.
- M010 refreshed safe aisw provider inventory: Codex profiles `adikia`/`ibl` and Claude profile `main` are available as enabled providers. No credentials or tokens are recorded.
- M011 accepted ADR-0004, added static extension/data-source models, and proved a local fake tiled-image Matplotlib mosaic/query path without network or credentials.
- ADR-0005 defines semantic axis intent with capability-resolved realization providers.
- M012 added deterministic `auto-linear-nice-v0` tick resolution, explicit tick pass-through, and resolver tests.
- M013 added Matplotlib native rendering for semantic `AxisGuide` ticks/labels/grid and `PanelTextGuide` titles.
- M014 added bounded reference guide query support with `GuideQueryPayload`, without hardening the broader query-scope model.
- M015 added guide/tick/title conformance fixtures and semantic Matplotlib/guide-query conformance checks.
- M016 added public VisPy2 guide APIs that emit semantic `AxisGuide`, `TickSpec`, and `PanelTextGuide` intent.
- S023 introduced manual visual QA artifacts under `artifacts/visual_qa/s023/`; generated runs are
  intentionally ignored.
- Datoviz `v0.4-dev` includes the merged legacy sRGB blend pipeline needed for Matplotlib-compatible
  visual QA comparisons: merge commit `f0d90d2bb` in the Datoviz repo.
- GSP defaults S023 Datoviz visual QA runs to `legacy_srgb_blend` so Matplotlib and Datoviz compare
  in display-space color semantics.
