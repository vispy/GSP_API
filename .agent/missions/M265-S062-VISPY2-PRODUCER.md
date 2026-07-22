# M265 - S062 VisPy2 producer migration

## Stage

S062 - Clean GSP And VisPy2 Repository Bootstrap

## Status

Approved; M264 completed.

## Summary

Migrate the semantic producer into the `vispy2` distribution, add immutable `Figure.to_scene()`, and
route publication and interactive execution through GSP sessions without concrete adapter imports.

## Acceptance

- Producer-only tests pass with only the built `gsp-core` wheel installed.
- `vispy2` contains no imports of `gsp_matplotlib` or `gsp_datoviz`.
- `savefig()` and blocking `show()` use an ephemeral Matplotlib session with actionable missing-extra
  errors; interactive/non-blocking execution uses an explicit caller-owned GSP session.
- Figure, axes, visuals, and scene snapshots retain no backend/session/native state.

## Stop conditions

Stop if the public API requires backend state on producer objects, direct adapter imports, silent
fallback/adaptation, or a compatibility alias for the unpublished prototype identity.
