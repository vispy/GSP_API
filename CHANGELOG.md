# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Changed `Text` alignement options from a vector to number with 9 options `TOP_LEFT`, `TOP_CENTER`, `TOP_RIGHT`, `CENTER_LEFT`, `CENTER_CENTER`, `CENTER_RIGHT`, `BOTTOM_LEFT`, `BOTTOM_CENTER`, and `BOTTOM_RIGHT` (default is now `CENTER_CENTER`).
- Changed `Text` angle from radiant to degree
- `AxesDisplay.set_title()`, `set_xlabel()`, `set_ylabel()` — render a plot title (14 pt, centered above the inner viewport), an x-axis label (13 pt, centered below tick labels), and a y-axis label (13 pt, rotated 90°, centered left of tick labels). Each label has its own position and visual style, is optional (pass `None` to clear), and follows the existing UUID-preservation pattern so redraws on pan/zoom are efficient.
- `AxesManaged.set_title()`, `set_xlabel()`, `set_ylabel()` — thin delegating methods for the same functionality on the higher-level managed axes API.
- Updated `examples/vispy_axes_display_example.py` to demonstrate all three labels.
- Added release checklist and tag policy documentation for S019 closeout.
- Added conformance fixture packaging, import-surface smoke coverage, and release-facing docs polish.
- Added strict mypy closure for `src/` with documented optional/vendored typing boundaries.
- Added resolved layout snapshots, layout-aware guide query support, device-scale layout metadata,
  and layout visual QA fixtures.
- Added retained semantic `View2D` navigation and live review wiring for supported backends.
- Added static orthographic `View3D`, `(N,3)` mesh rendering paths, canonical ray readback payloads,
  and View3D navigation action semantics.
- Added flat Lambert face-normal mesh shading, Datoviz CPU-resolved Lambert promotion, and 3D manual
  review examples.
- Added backend-neutral `query.view3d.mesh_triangle_pick.v1` protocol payloads with a Matplotlib CPU
  reference oracle for bounded opaque DATA-space mesh triangle picking.

### Changed
- Clarified Datoviz packaging policy: legacy Datoviz wrapper support is optional, while Datoviz v0.4
  adapter work remains capability-gated until compatible release artifacts exist.
- Enforced `legacy_srgb_blend` as the Datoviz v0.4 renderer and visual-QA default for
  Matplotlib-parity comparisons; `linear_srgb` is now an explicit diagnostic option.
- Updated README, MkDocs, and examples documentation to use `GSP_RENDERER` consistently and to
  distinguish Matplotlib, optional legacy Datoviz, network, and Datoviz v0.4 protocol surfaces.
- Updated `examples/README.md` to list shipped public example scripts and to show the current
  `renderer.render(...)` API pattern.
- Promoted Datoviz guide, grid-clipping, View3D rendering, View3D navigation, and Lambert support
  only where local v0.4 evidence and capability gates prove the accepted semantics.
- Kept Datoviz native grid clipping separate from full guide strictness; grid clipping is not a
  guide-query or all-rendered contribution claim.

### Fixed
- Fixed Matplotlib-only example execution so public examples no longer import optional legacy
  Datoviz modules unless the `datoviz-v03` renderer path is selected.
- Fixed `examples/protocol_live_window.py` so `GSP_TEST=True` closes the Matplotlib figure instead
  of opening a blocking live window during batch example validation.

### Validation
- `PYTHONPATH=. uv run mypy src/ --strict --show-error-codes`
- `PYTHONPATH=. uv run pytest -q`
- `uv run mkdocs build --strict`
- `uv build`
- `PYTHONPATH=. uv run python tools/run_all_examples.py`
- `PYTHONPATH=. uv run python tools/check_expected_output.py`
- Focused S034-S044 validation includes layout, guide, navigation, View3D, Lambert, Datoviz v0.4
  capability gates, and mesh-triangle-pick tests recorded in the corresponding `.agent/S0xx_*` and
  mission files.

### Backend support
- Matplotlib remains the required reference and release-readiness backend.
- Legacy Datoviz wrapper support is optional through `pip install -e ".[datoviz-legacy]"` and the
  `GSP_RENDERER=datoviz-v03` example path.
- Datoviz v0.4 protocol adapter work remains capability-gated and is not declared as a package
  dependency until compatible release artifacts exist.
- Datoviz v0.4 may support retained View2D navigation, retained DATA-space View3D rendering,
  View3D live navigation, grid clipping, and CPU-resolved flat Lambert only when the active local
  v0.4 facade exposes the required symbols and the adapter advertises the corresponding capability.
- The network renderer requires a separate server process and remote renderer configuration.

### Known limitations
- Datoviz v0.4 text and guide/View2D review rows include adapted, not strict, cases: several text
  anchor/placement/unicode semantics remain verification-gated, while guide panel-title and
  guide/all-rendered query semantics remain unsupported.
- Strict opaque GPU depth, perspective projection, textures/UVs, smooth/Phong lighting, and public
  material resources remain deferred.
- Datoviz v0.4 does not advertise `query.view3d.mesh_triangle_pick.v1`; native visual/triangle
  mapping and pick-scene freshness remain unproven.
- Optional Datoviz, network, and session replay checks are outside the required release validation
  path unless their exact environment is recorded separately.

## [0.1.0] - 2026-03-16

### Added

- Initial release with core plotting and visualization infrastructure
- AxesDisplay and AxesManaged for interactive axes with pan/zoom
- Support for scatter, line, and point visuals
- Matplotlib and DatoViz backend support
- Comprehensive documentation and examples

[Unreleased]: https://github.com/vispy/GSP_API/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/vispy/GSP_API/releases/tag/v0.1.0
