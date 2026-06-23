# Strict Mypy Debt Inventory

Status: M047 closed.

`PYTHONPATH=. uv run mypy src/ --strict --show-error-codes` now passes with no errors across 186
source files.

## Resolved In M047

- Datoviz untyped imports are quarantined with a narrow `datoviz` / `datoviz.*` mypy override.
- `types-colorama` is a dev dependency, so `colorama` is no longer an uncontrolled missing-stub
  failure.
- `gsp_extra` now has explicit package markers, which removes the namespace-package duplicate-module
  failure around `gsp_extra.bufferx`.
- Public package re-export lists were added for `gsp.core`, `gsp.types`, and `gsp.visuals`.
- Import smoke tests cover `gsp_extra` modules as part of the package surface.
- `TransBuf` is now an explicit `TypeAlias`, which removes the broad `valid-type` failure family
  from the focused visual/VisPy2/network slice.
- The focused strict target
  `src/gsp/visuals src/vispy2/scatter src/vispy2/plot src/gsp_network src/gsp_extra/object3d.py`
  passes.
- `types-requests` is a dev dependency, `http_constants` is quarantined with a narrow missing-import
  override, and network renderer/server annotation issues in the focused slice are fixed.
- Full strict mypy passes after typed fixes for legacy annotations, numpy helper boundaries,
  Matplotlib renderer stubs, VisPy2 axes helpers, pydantic serialization, optional Datoviz callbacks,
  OBJ parser accumulators, and renderer registration helpers.

## Documented Boundaries

- `datoviz` / `datoviz.*`: optional legacy backend with no typed Python surface in the local
  environment.
- `meshio` / `meshio.*`: optional helper import without installed stubs.
- `http_constants` / `http_constants.*`: runtime dependency without installed stubs.
- `gsp_extra.mpl3d.*`: vendored helper boundary quarantined with a focused override.
- `src/gsp/utils/math_utils copy*.py`, `math_utils_new.py`, and `math_utils_original.py`: stale
  backup artifacts excluded from the strict source walk.

## Guardrail

Do not make the strict command pass by adding broad package-level `ignore_errors` overrides. Any
ignore must be tied to a specific optional dependency, vendored module, or explicitly documented
legacy boundary.
