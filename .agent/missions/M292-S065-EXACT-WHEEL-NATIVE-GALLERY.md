# M292 - S065 exact-wheel native gallery qualification

## Status

Completed with unconditional independent acceptance on 2026-07-27. GSP `fd20c94` and VisPy2
`7d2eb41` produced fourteen fresh 800x600 captures from exactly four wheels; VisPy2 `63d3301`
publishes the portable evidence.

## Baseline

- GSP `6b5b8bc` includes accepted logical layout production and backend consumption.
- VisPy2 `81557b8` includes the accepted fail-closed schema-2 gallery validator.
- Datoviz `04f9fdd` is read-only. Preserve all user working-tree state.
- M290 source corrections and M291 HiDPI normalization are independently accepted.

## Required execution

1. Verify GSP and VisPy2 candidate heads are clean and committed.
2. Build exactly four fresh wheels from those heads into a new temporary directory:
   `gsp-core`, `gsp-matplotlib`, `gsp-datoviz`, and `vispy2`.
3. Run the M290 validator with four explicit named wheel inputs and the prequalified GSP Python
   environment for third-party dependencies.
4. Require all fourteen Matplotlib/Datoviz PNGs at exactly `800x600`, canonical filenames only,
   exact shared layout/projection evidence, camera raster geometry ratios within 2%, capability and
   query checks, and a portable schema-2 manifest with the four exact wheel hashes.
5. Reject absolute host paths in the new manifest, current review notes, and touched gallery
   Markdown. Preserve repository-relative image links.
6. Run Gallery 5 from the VisPy2 repository with experimental Datoviz View3D navigation enabled,
   observe successful window startup, send one bounded interrupt, require exit code zero, and leave
   no process running.
7. Visually inspect all gallery pairs, including figure dimensions, perspective/orthographic
   ordering, camera fit/orbit/pan/zoom scale, titles/axes policy, lighting differences, and the
   previously reported top red-square depth relation.
8. Obtain an independent artifact/evidence review.
9. Commit only regenerated VisPy2 gallery artifacts and necessary repository-relative review notes.

## Required validation

- Exact wheel hashes match the manifest.
- Every manifest artifact hash and dimension matches the published file.
- All project imports come from the validator's isolated project site and Pillow is importable.
- Producer-only `gsp-core` plus `vispy2` wheel isolation passes with no adapters importable.
- Full committed-head GSP and VisPy2 pytest, strict mypy, Ruff, docs/links, provider probes, and
  `git diff --check` remain green.
- No Datoviz file is edited, staged, committed, or pushed.

## Acceptance

- Native validator exits zero without stale-output reuse.
- Gallery 5 bounded lifecycle exits zero and leaves no process.
- Independent artifact review issues unconditional ACCEPT.
- M288, M289, M290, and M292 can close; M284/S065 remains open only for human visual acceptance.

## Stop conditions

- Stop rather than weakening a dimension, provenance, capability, geometry, or freshness check.
- Stop on a Datoviz source change, native crash, repeat timeout, schema failure, absolute-path leak,
  or a material visual mismatch.
- Do not merge, tag, release, publish packages, create a PR, or modify versions.
- Push only GSP_API, GSP, and VisPy2 after all final commits and checks; never push Datoviz.

## 2026-07-27 closeout

- Schema-2 manifest, exact wheel/source/script/artifact hashes, portable imports, shared layout,
  capability/query probes, and all fourteen fresh captures passed.
- Camera fit/orbit/pan/zoom raster ratios are 0.988–0.995 against a 2% tolerance.
- Gallery 5 started from the isolated four-wheel site, accepted one bounded interrupt, exited zero,
  and left no process.
- Full committed-head gates passed: 801 GSP tests, 84 VisPy2 tests, strict mypy, Ruff,
  documentation/link checks, and producer-only isolation.
- Independent artifact review returned unconditional ACCEPT.
- M288, M289, M290, and M292 close. M284 and S065 remain at 95% pending owner visual and
  interactive acceptance.
