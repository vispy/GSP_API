# M045-PACKAGING-IMPORT-SURFACE-CLEANUP - Packaging/import-surface cleanup

## Mission

M045

## Goal

Resolve the highest-priority packaging metadata and import-surface issues identified by M044.

## Acceptance

- Project metadata has a non-empty description suitable for local package metadata.
- Runtime dependencies are reviewed and obvious dev-only tools are moved to the dev dependency group
  when no runtime imports require them.
- Datoviz dependency policy is explicit and does not falsely advertise unavailable v0.4 wheel
  support.
- The minimal JSON conformance fixture package-data strategy is verified or documented.
- Lightweight import-surface smoke tests cover core package imports and optional backend import
  behavior.

## Stop conditions

Stop before publishing packaging artifacts, replacing the Datoviz adapter strategy, or changing
legacy renderer registration semantics without tests and docs.

## Source

M044 packaging/import/docs audit.

## Result

Completed. `pyproject.toml` now has release-facing package metadata, explicit top-level package
inclusion, fixture package-data inclusion, dev-only validation tools in the dev dependency group, and
an optional `datoviz-legacy` extra. `docs/packaging_import_surface_policy.md` records the Datoviz
and package-data policy. `tests/test_import_surface.py` covers core imports, optional Datoviz import
behavior, and package-resource access to the minimal JSON fixture.
