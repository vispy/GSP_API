# M262 - S062 gsp-core curation and isolation

## Stage

S062 - Clean GSP And VisPy2 Repository Bootstrap

## Status

Completed.

## Summary

Curate formal protocol records, specifications, accepted rationale, fixtures, and tests into
`gsp-core`; remove the core Matplotlib dependency and prove the isolated wheel.

## Acceptance

- `gsp-core` imports with only declared semantic/numeric dependencies.
- No legacy object graph or adapter package is imported or installed.
- Core protocol/conformance tests pass from the built installed wheel.
- Every imported file has exact or derived provenance.

## Stop conditions

Stop if named colormap semantics cannot be preserved without a backend dependency, an archive-only
module is required, or wheel tests depend on source-tree paths.

## Result

Curated and isolated `gsp-core==0.2.0a1` in GSP commit `a0d76b7`; 164 tests pass from its installed
wheel, strict mypy/Ruff pass, metadata requires only NumPy, and importing GSP loads no backend. See
`.agent/S062_M262_GSP_CORE_CURATION.md`.
