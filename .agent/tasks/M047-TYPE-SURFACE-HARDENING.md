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
