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

### Changed
- Clarified Datoviz packaging policy: legacy Datoviz wrapper support is optional, while Datoviz v0.4
  adapter work remains capability-gated until compatible release artifacts exist.
- Updated README, MkDocs, and examples documentation to use `GSP_RENDERER` consistently and to
  distinguish Matplotlib, optional legacy Datoviz, network, and Datoviz v0.4 protocol surfaces.
- Updated `examples/README.md` to list shipped public example scripts and to show the current
  `renderer.render(...)` API pattern.

### Validation
- `PYTHONPATH=. uv run mypy src/ --strict --show-error-codes`
- `PYTHONPATH=. uv run pytest -q`
- `uv run mkdocs build --strict`
- `uv build`

## [0.1.0] - 2026-03-16

### Added

- Initial release with core plotting and visualization infrastructure
- AxesDisplay and AxesManaged for interactive axes with pan/zoom
- Support for scatter, line, and point visuals
- Matplotlib and DatoViz backend support
- Comprehensive documentation and examples

[Unreleased]: https://github.com/vispy/GSP_API/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/vispy/GSP_API/releases/tag/v0.1.0
