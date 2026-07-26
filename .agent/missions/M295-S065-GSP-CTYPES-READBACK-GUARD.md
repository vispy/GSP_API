# M295 - S065 GSP ctypes state-readback fail-closed guard

## Status

Approved for direct execution with `codex-ucl-gpt-5.6-sol-medium` after M294 integration.

## Baseline and defect

- GSP baseline is `6b5b8bc06e8dfceea87343c7db39ed38494a72d4`.
- Datoviz M294 repairs the current generated state layouts, but GSP must independently reject a future incomplete or stale ctypes record before making a native output-pointer call.
- Existing panel-frame paths already use incomplete-record diagnostics; retained View3D state readback does not.
- The guard must distinguish retained 3D rendering/attachment readiness from state-readback readiness so an absent readback layout does not silently corrupt memory or falsely describe an unrelated visual feature.

## Required implementation

1. Add a dedicated Datoviz View3D state-readback diagnostic/readiness boundary in both the adapter capability surface and protocol renderer where appropriate.
2. Before constructing or passing `DvzPanelView3DState`, require a real `ctypes.Structure` subclass with nonempty `_fields_`, positive size, and the required state field names. Use existing incomplete-record helpers or generalize them without duplicating unsafe logic.
3. Make malformed/incomplete bindings fail with a clear `DatovizV04Unavailable` diagnostic and prove the native `dvz_panel_view3d_state` function is never called.
4. Preserve retained DATA-space View3D rendering when only optional state readback is unavailable; gate live navigation or any operation that requires native readback honestly.
5. Do not add a hand-written ABI mirror, ignore a native failure, weaken gallery validation, or change public GSP protocol semantics.

## Required tests and validation

- Fake zero-size ctypes state record rejects before native invocation.
- Missing required fields reject before native invocation.
- Valid fake state layout preserves existing readback/navigation behavior.
- Real repaired Datoviz binding reports state readback ready.
- Focused GSP Datoviz tests, full GSP tests, strict mypy, Ruff, wheel builds, installed-wheel smoke, and `git diff --check`.
- One coherent GSP commit and unconditional independent review.

## Stop conditions

- Stop on need for a GSP-local ABI mirror, Datoviz public ABI change, or weakened capability semantics.
- Do not push, tag, release, publish, merge, create a PR, or change package versions.

