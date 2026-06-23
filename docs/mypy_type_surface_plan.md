# Strict Mypy Type-Surface Plan

Status: M047 complete. The original import-surface blockers and the broader legacy typing debt are
resolved or explicitly quarantined at narrow optional/vendored boundaries. See
`docs/mypy_strict_debt_inventory.md`.

`PYTHONPATH=. uv run mypy src/ --strict --show-error-codes` passes.

## Failure Groups

### Untyped Datoviz Imports

Legacy Datoviz wrapper modules import `datoviz`, `datoviz.visuals`, and private wrapper modules such
as `datoviz._figure`. The installed package does not provide stubs or a `py.typed` marker, so strict
mypy reports `import-untyped`.

Next steps:

- Add a narrow mypy config section for Datoviz wrapper imports, or add local minimal stubs under a
  dedicated stub path.
- Keep v0.4 protocol code typed against structural `Any`/facade helpers until Datoviz publishes a
  typed Python surface.
- Avoid changing runtime Datoviz behavior as part of type cleanup.

### `gsp_extra` Relative Imports

`gsp_extra.camera_controls` uses relative imports that mypy cannot resolve cleanly in the current
namespace-package layout, and mypy also reports `gsp_extra.bufferx` as loaded twice.

Next steps:

- Add missing `__init__.py` files or convert the affected imports to absolute package imports.
- Verify wheel contents still include `gsp_extra` after the package-layout change.
- Add/import-smoke tests for the affected `gsp_extra` modules.

### Missing Third-Party Stubs

`colorama` is used at runtime and lacks installed stubs in the current environment.

Next steps:

- Add `types-colorama` to the dev dependency group, or configure mypy to ignore that specific
  untyped import.
- Prefer stubs for stable third-party packages and targeted ignores for unstable optional backends.

## Result

M047 closed the type-surface hardening without broad package-level ignores. The remaining config
boundaries are limited to optional dependencies, vendored helpers, and stale backup artifacts that
are not part of the intended package surface.
