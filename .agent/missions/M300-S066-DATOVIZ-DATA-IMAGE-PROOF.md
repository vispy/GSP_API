# M300 - S066 Datoviz DATA-space image proof and Q200 closure

## Status

Approved by the owner on 2026-07-30. Implementation checkpoint completed under
`local-main-codex`; final paired-live acceptance is pending a reboot after the owner reported a
broken GPU driver.

Checkpoint evidence: `.agent/reviews/M300-DATOVIZ-DATA-IMAGE-CHECKPOINT.md`.

## Goal

Determine whether the qualified Datoviz v0.4 retained scene API can render a public VisPy2
DATA-space scalar image correctly under View2D. If the native proof passes, remove the GSP
Datoviz adapter's NDC-only restriction, qualify the public live scalar-image/colorbar path, and
resolve Q200 truthfully.

## Repositories and locks

- `datoviz`: read-only evidence source and native runtime.
- `gsp`: writable under `packages/gsp-datoviz/src` and `packages/gsp-datoviz/tests`.
- `vispy2`: writable under `tests`, `examples`, and `docs`.
- `mission-control`: writable under `.agent`.

Existing unrelated Datoviz documentation-generator changes are outside mission scope and must
remain untouched.

## Execution sequence

1. Prove a native Datoviz image quad attached with `DVZ_VISUAL_COORD_DATA`.
2. Verify extent, origin, plot clipping, resize, View2D pan/zoom, reversed axes, and overlay
   registration using deterministic state or capture evidence where available.
3. Verify scalar sampled-field, colormap, and native colorbar composition.
4. If the native proof passes, update the GSP Datoviz adapter to accept DATA-space images and
   attach them through the retained View2D path.
5. Add focused adapter tests, isolated native lifecycle evidence, and a public VisPy2 live
   comparison or workbook path.
6. Run focused tests followed by repository pytest, strict mypy, Ruff, installed-wheel, and
   relevant backend/lifecycle gates.
7. Update capability documentation and close or reclassify
   `Q200-VISPY2-DATOVIZ-DATA-IMAGE-LIVE-COVERAGE`.

## Acceptance

- Public `VisPy2.imshow()` DATA extents render in Datoviz without semantic conversion to a fixed
  screen-space image.
- Image placement remains registered with overlays through View2D state changes and resize.
- Origin, nearest/linear sampling, clipping, scalar mapping, and linked colorbar behavior are
  covered.
- Unsupported query/readback behavior remains independently capability-gated.
- Native close and teardown complete without crash or hang.
- No versions, tags, publication metadata, pushes, PRs, or release operations are performed.

## Stop conditions

- Stop before changing Datoviz source or public APIs.
- Stop and report if existing Datoviz APIs cannot express correct retained DATA-image semantics.
- Stop on a native crash, source/spec conflict, unrelated dirty-state overlap, credential need, or
  required work outside the declared locks.
- If a public Datoviz API or protocol redesign is required, prepare a self-contained ChatGPT Pro
  consultation packet before dependent implementation.
