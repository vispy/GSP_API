# M259 - S061 curated migration inventory

## Stage

S061 - GSP And VisPy2 Migration Foundation

## Status

Draft; blocked on M258.

## Summary

Produce a machine-readable and human-reviewable manifest classifying current protocol, adapters,
producer, tests, specifications, documentation, examples, fixtures, legacy code, experiments, and
artifacts as migrate-now, archive-only, or defer/reassess.

## Acceptance

- Every migrate-now component has a destination owner and exact source commit/path/blob provenance.
- Current code has no unexplained dependency on an archive-only component.
- Generated evidence is reduced to the minimal reproducible fixtures and expectations.
- No implementation file is moved and no new repository is created.

## Stop conditions

Stop if protocol authority is disputed, a core component still requires the legacy object graph, or
the manifest would silently discard evidence that is not recoverable from the verified archive.

