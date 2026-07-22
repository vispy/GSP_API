# M262 - S062 gsp-core curation and isolation

## Stage

S062 - Clean GSP And VisPy2 Repository Bootstrap

## Status

Draft; blocked on M261.

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

