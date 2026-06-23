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

Completed. The full strict command now passes:

```bash
PYTHONPATH=. uv run mypy src/ --strict --show-error-codes
```

Closure included typed fixes across TransBuf consumers, public re-export surfaces, callback and
registration annotations, numpy helper return boundaries, Matplotlib renderer stubs, VisPy2 axes
helpers, network/server typing, and legacy Datoviz wrapper callbacks. Remaining ignores are narrow:
Datoviz and optional `meshio` imports, `http_constants` stubs, stale math backup files excluded from
the source walk, and the vendored `gsp_extra.mpl3d.*` helper boundary.
