# M047-TYPE-SURFACE-HARDENING - Strict mypy type-surface hardening

## Mission

M047

## Goal

Resolve or explicitly quarantine the existing strict mypy failures left outside M045.

## Acceptance

- Datoviz legacy wrapper imports no longer produce uncontrolled strict-mypy failures.
- `gsp_extra` relative import and duplicate-module issues are fixed with package-layout or import
  cleanup.
- Missing third-party stubs are added or narrowly ignored.
- `uv run mypy src/ --strict --show-error-codes` passes, or only reports documented optional-backend
  boundaries with local config explaining why.
- Existing pytest suite remains green.

## Stop conditions

Stop before changing Datoviz runtime adapter semantics, deleting legacy examples, or broadening mypy
ignores across unrelated packages.

## Source

M045 validation note and M046 follow-up planning.

## Progress

In progress. The original uncontrolled import-surface failures are resolved: Datoviz untyped imports
are quarantined with a narrow mypy override, `types-colorama` is a dev dependency, and `gsp_extra`
has explicit package markers and import smoke coverage. The first TransBuf/export/network batch is
also clean: the focused strict target covering `gsp.visuals`, `vispy2.scatter`, `vispy2.plot`,
`gsp_network`, and `gsp_extra.object3d` passes. Full strict mypy now reports 191 legacy typing errors
across 48 files; these are inventoried in `docs/mypy_strict_debt_inventory.md`. Do not mark this
mission complete until the strict command passes or remaining failures are narrowed to documented
optional/vendored boundaries without broad package-level ignores.
