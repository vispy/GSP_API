# Strict Mypy Debt Inventory

Status: M047 discovery after import-surface hardening.

After resolving the original M045 blockers, `uv run mypy src/ --strict --show-error-codes` reaches
the wider source tree and reports 539 errors across 85 files.

## Resolved In M047 So Far

- Datoviz untyped imports are quarantined with a narrow `datoviz` / `datoviz.*` mypy override.
- `types-colorama` is a dev dependency, so `colorama` is no longer an uncontrolled missing-stub
  failure.
- `gsp_extra` now has explicit package markers, which removes the namespace-package duplicate-module
  failure around `gsp_extra.bufferx`.
- Public package re-export lists were added for `gsp.core`, `gsp.types`, and `gsp.visuals`.
- Import smoke tests cover `gsp_extra` modules as part of the package surface.

## Remaining Debt Groups

### Legacy Visual And `TransBuf` Typing

Many legacy visual modules use `TransBuf` in type positions in a way strict mypy treats as a variable
rather than a valid type. This affects `gsp.visuals`, `vispy2.scatter`, `vispy2.plot`,
`vispy2.axes`, `gsp_network`, and `gsp_extra.object3d`.

Next action: settle the canonical type import/export for `TransBuf`, then repair the dependent
modules in one pass.

### Annotation Debt

Strict mypy reports missing return annotations in legacy modules, including event/control callbacks,
renderer registration helpers, network tools, axes pan/zoom handlers, and object hierarchy helpers.

Next action: add return annotations where behavior is clear, prioritizing public helpers and callback
methods that are exercised by tests.

### Numpy Return And Container Shapes

Several math, tick, and axes helpers return values mypy sees as `Any` or as list shapes where tuple
shapes are declared. This includes `gsp.protocol.ticks`, `vispy2.axes.axis_tick_locator`,
`gsp.utils.math_utils*`, `gsp_extra.mpl3d.glm`, and axes display helpers.

Next action: use `np.asarray`/`typing.cast` at narrow boundaries and align declared container types
with runtime values.

### Vendored And Optional Helpers

The vendored `gsp_extra.mpl3d.trackball` module is largely untyped. `gsp_extra.misc.mesh_utils`
imports optional `meshio` and has shape/type mismatches around optional arrays.

Next action: either type the vendored helper boundary explicitly or quarantine it with a focused
module override, and make `meshio` optional typing explicit.

### Legacy Renderer And Network Surface

The Matplotlib, Datoviz legacy wrapper, and network packages still have callback, registration, and
remote-renderer typing issues. These are not Datoviz v0.4 protocol adapter semantics and should be
handled without changing runtime behavior.

Next action: annotate registration helpers, add explicit renderer package exports, and fix local
variable typing in network server code.

## Guardrail

Do not make the strict command pass by adding broad package-level `ignore_errors` overrides. Any
ignore must be tied to a specific optional dependency, vendored module, or explicitly documented
legacy boundary.
