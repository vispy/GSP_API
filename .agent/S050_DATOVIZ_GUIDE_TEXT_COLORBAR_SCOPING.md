# S050 Datoviz Guide, Text, And Colorbar Strictness Scoping

Date: 2026-07-03

Mission: M202 - S050 Datoviz guide text and colorbar strictness scoping

## Decision

Continue with bounded Datoviz strictness proof missions, but keep the areas split:

1. Colorbar explicit ticks and labels are the cleanest next proof.
2. Guide query/all-rendered contribution evidence is promising, but full guide strictness remains
   blocked by missing native panel-title API evidence.
3. TextVisual strictness should be handled as a focused visual-QA proof, not a protocol change.

No public protocol semantics should change in this branch. Datoviz guide strictness must not be
promoted from grid clipping alone.

## Current Local Datoviz Evidence

Read-only sibling checkout inspected:

- path: `/home/cyrille/GIT/Viz/datoviz`
- branch: `v0.4-dev`
- commit: `dc8b168ed86e0f674be204d00c29e5869ee5e6c4`
- pre-existing dirty file: `NOTES`

The local Python facade exposes:

| Area | Symbols | Status |
|---|---|---|
| Panel frame snapshots | `dvz_panel_resolve_frame`, `DvzPanelFrameInfo`, `DvzGuideLayout`, `DvzRenderedContribution` | present |
| Guide query | `DvzGuideHit`, `dvz_panel_frame_guide_hit` | present |
| Contributions | `dvz_panel_frame_contribution_count`, `dvz_panel_frame_contribution` | present |
| Panel title | `dvz_panel_set_title`, `dvz_panel_title` | absent |
| Text | `dvz_text`, `dvz_text_set_string`, `dvz_text_style`, `dvz_text_set_style`, `dvz_text_placement`, `dvz_text_set_placement` | present |
| Colorbar | `dvz_colorbar_desc`, `dvz_colorbar`, `dvz_colorbar_set_title`, `dvz_colorbar_set_ticks`, `dvz_colorbar_set_format` | present |

The Datoviz source also contains:

- `src/scene/core/panel_frame_snapshot.c::dvz_panel_frame_guide_hit()`;
- `include/datoviz/scene.h::dvz_panel_frame_guide_hit()`;
- `src/scene/annotation/colorbar.c::dvz_colorbar_set_ticks()`;
- `src/scene/tests/fields.c::test_scene_colorbar_explicit_ticks_and_labels`;
- text placement and text-anchor logic in `src/scene/annotation/text.c`,
  `text_layout.c`, and `text_glyph_realize.c`.

No Datoviz files were edited.

## Guide Strictness

Current GSP code already has a partial Datoviz guide-query path:

- `DatovizV04ProtocolRenderer.query_panel()` routes `QueryScope.GUIDES` and
  `QueryScope.ALL_RENDERED` into `_query_panel_guides()`.
- `_query_datoviz_panel_frame_guides()` maps `DvzGuideHit` into `GuideQueryPayload`.
- `gsp_datoviz.capabilities` reports `guide_query` and `all_rendered_guides` when panel frame
  snapshot and guide-hit symbols are available.
- Focused fake-facade tests cover hit payloads and stale layout snapshot rejection.

Strict guide promotion still needs runtime/review evidence, and it must preserve the S043 rule that
guide rows promote only with native guide identity, layout boxes, guide query/readback,
all-rendered contributions, and snapshot id equality.

Blocker: the local facade does not expose `dvz_panel_set_title` or `dvz_panel_title`. Existing GSP
title rendering uses screen text as an adapted review path. Therefore full guide strictness remains
blocked unless the title requirement is explicitly excluded from a narrower row contract or Datoviz
adds/proves native title semantics.

## Text Strictness

Existing state:

- `text/rotation_alpha_ndc` is already strict for center-anchored NDC ASCII text, rotation, alpha,
  logical font size, and draw-above-image behavior.
- `text/basic_ndc` remains adapted because default `BASELINE` anchor semantics are not strictly
  verified.
- `text/anchor_grid_ndc` remains adapted because baseline/top/bottom text-box anchors are not
  fixture-proven.
- `text/data_vs_ndc` remains adapted because DATA and NDC placement were only compared under the
  identity `[-1, +1]` view.
- `text/multiline_unicode_smoke` remains adapted because Unicode fallback and multiline anchoring
  are not proven.

The current Datoviz facade exposes the retained text placement/style/string path needed for a
focused proof. The next TextVisual mission should use fixtures and visual QA; it should not change
the TextVisual public contract.

## Colorbar Strictness

Existing state:

- The GSP Datoviz adapter already lowers `ColorbarGuide.ticks` and `tick_labels` through
  `dvz_colorbar_set_ticks()` when available.
- Fake-facade tests cover native scale creation, colorbar construction, explicit ticks/labels,
  title, formatting, and framebuffer-scaled style values.
- Older S029 handoff notes recorded a Datoviz WIP segfault, but the current local facade exposes
  the required colorbar symbols and the source contains a native explicit tick/label test.

The next colorbar mission should refresh runtime evidence against the current local Datoviz checkout,
regenerate the relevant review artifact, and update stale handoff/release wording only if the proof
passes. Colorbar query remains out of scope unless Datoviz panel frame guide hit records prove
colorbar guide identity and payload semantics for ticks/title/ramp.

## Follow-Up Mission Order

| Mission | State | Purpose |
|---|---|---|
| M206 | ready | Validate Datoviz colorbar explicit tick/label runtime and review evidence. |
| M207 | draft | Audit Datoviz guide query/all-rendered contribution runtime evidence and decide whether any guide row can narrow-promote without native panel-title support. |
| M208 | draft | Prove Datoviz TextVisual anchor/DATA/multiline rows through focused fixtures and review artifacts. |

M201 stays blocked by the upstream mesh triangle query identity gap. M204 stays blocked pending
ChatGPT Pro consultation for materials/textures and broader VisPy2 API shape.

## M206 Target

M206 should:

- verify the current local Datoviz colorbar explicit tick symbols and native source tests;
- run a bounded GSP colorbar review artifact for `color/scalar_image_viridis_colorbar`;
- confirm explicit tick values and labels survive through the Datoviz adapter path;
- update stale colorbar handoff wording if the old segfault blocker no longer applies;
- avoid changing public `ColorbarGuide` semantics;
- keep colorbar query unsupported unless native guide-hit evidence clearly covers colorbar parts.

## Stop Conditions

- Stop before claiming full guide strictness from grid clipping alone.
- Stop before changing text or colorbar public contracts without a consultation packet.
- Stop before treating screen-text panel titles as native Datoviz title strictness.
- Stop before editing `/home/cyrille/GIT/Viz/datoviz` without explicit approval.
- Stop before promoting colorbar query without native guide-hit payload evidence for colorbar parts.
