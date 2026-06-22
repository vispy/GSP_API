# M044-PACKAGING-IMPORT-DOCS-AUDIT - Packaging/import/docs audit

## Mission

M044

## Goal

Kick off S019 by auditing packaging metadata, import-surface behavior, README/docs entry points, and
example documentation drift.

## Acceptance

- S019 is marked active in Mission Control.
- Obvious scratch artifacts from prior handoffs are removed when approved by the user.
- Packaging risks are recorded, including runtime/dev dependency separation, Datoviz version policy,
  Git URL dependency policy, and fixture package-data inclusion.
- Import-surface risks are recorded, including backend import side effects and package name wording.
- Docs/examples drift is recorded, including backend environment variable mismatch, stale example
  filenames, stale documentation links, and repo command guidance.
- Follow-up S019 missions are queued for packaging/import cleanup and docs/examples cleanup.

## Stop conditions

Stop before changing dependency policy, renaming packages, changing the public `vispy2` API, or
declaring Datoviz v0.4 packaging support without a local wheel/release strategy.

## Source

Mission Control recommendation after S018 completion.

## Result

Completed. `docs/packaging_import_surface_audit.md` records the S019 kickoff findings and follow-up
missions M045/M046 are queued.
