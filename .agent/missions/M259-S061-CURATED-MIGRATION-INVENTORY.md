# M259 - S061 curated migration inventory

## Stage

S061 - GSP And VisPy2 Migration Foundation

## Status

Completed.

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

## Result

Created a validated 31-component migration manifest with 16 migrate-now, 11 archive-only, and four
defer/reassess components. Every source component resolves to the declared Git blob/tree object at
baseline `463d34d`; every migrate-now component has a destination owner. The dependency audit found
no formal-protocol dependency on the legacy object graph and made four expected rewrite gates
explicit: core colormap/Matplotlib coupling, legacy Matplotlib initialization, Datoviz sibling-source
bootstrap, and direct VisPy2 adapter imports. See `.agent/S061_M259_CURATED_MIGRATION_INVENTORY.md`
and `.agent/migration/S061_migration_manifest.json`.
