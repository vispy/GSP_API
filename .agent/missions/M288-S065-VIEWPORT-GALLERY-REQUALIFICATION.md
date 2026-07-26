# M288 - S065 viewport gallery requalification and owner handoff

## Status

Approved for execution. M287 was integrated and independently accepted on 2026-07-26. Execute with
the pinned `codex-ucl-gpt-5.6-sol-medium` provider.

## Goal

Exercise the shared resolved viewport through VisPy2, regenerate the portable gallery, and return a
review pack where cross-backend geometry scale is automatically checked instead of judged only by
eye.

## Required scope

In `vispy2`:

- Expose only the minimum high-level path needed to request/reuse a resolved layout for a figure.
  Keep backend objects out of VisPy2 public camera and visual APIs.
- Update galleries 2-4 to render both backends from the same resolved layout snapshot.
- Preserve the exact 800×600 canvas request and repository-relative documentation paths.
- Keep the existing truthful title limitation: Matplotlib renders the semantic title; Datoviz may
  omit it with the recorded unsupported diagnostic, but both use the same plot viewport.
- Extend the installed-wheel validator to record and compare:
  - canvas size;
  - panel rectangle;
  - plot rectangle;
  - effective perspective aspect;
  - selected projected NDC anchor pixels;
  - non-background geometry bounds for the uniform camera mesh.
- Use semantic/projected anchor checks as the strict evidence. Treat raster geometry bounds as a
  tolerant review check so antialiasing and backend rasterization do not create false failures.
- Regenerate all fourteen static PNGs, the manifest, capability matrix, gallery docs, and owner
  review pack from exact committed wheels outside source trees.
- Re-run the exact Gallery 5 command from `GSP_API`, exercise orbit/pan/zoom/reset manually or by
  qualified replay where possible, and verify one `Ctrl-C` exits cleanly with no process behind.

In `gsp`, add only focused corrections exposed by installed-wheel validation; stop on semantic
expansion and return to Mission Control if M287 did not fully establish the required path.

## Acceptance

- Every PNG is exactly 800×600.
- Galleries 2-4 report the same panel and plot rectangles for Matplotlib and Datoviz.
- Perspective effective aspect is identical and equals the shared plot-rectangle ratio when the
  authored aspect is absent.
- Camera-sequence geometry width and height ratios are within 2 percent across backends after
  accounting for documented raster tolerance.
- Orthographic and perspective anchor projections agree within one logical pixel.
- Titles neither resize nor shift one backend's viewport independently.
- Full GSP and VisPy2 tests, strict mypy, Ruff, docs/link validation, wheel isolation, hashes,
  dimensions, and diff checks pass.
- An independent supervisor reviews all image pairs and accepts the pack.
- The owner receives the portable corrected review document; M284 and S065 remain open until the
  owner explicitly accepts it.
- Changes are committed separately in each writable repository.

## Stop conditions

- Stop rather than weakening scale, viewport, query, or capability assertions to make the gallery
  pass.
- Stop on any reproducible native crash, hang, cleanup failure, or mismatched render/query snapshot.
- Stop if completion requires a Datoviz repository edit; report the missing API for a separately
  approved mission.
- No absolute paths in committed Markdown or manifests.
- Do not push, merge, tag, release, publish, or change package versions.
