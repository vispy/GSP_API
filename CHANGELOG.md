# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `AxesDisplay.set_title()`, `set_xlabel()`, `set_ylabel()` — render a plot title (14 pt, centered above the inner viewport), an x-axis label (13 pt, centered below tick labels), and a y-axis label (13 pt, rotated 90°, centered left of tick labels). Each label has its own position and visual style, is optional (pass `None` to clear), and follows the existing UUID-preservation pattern so redraws on pan/zoom are efficient.
- `AxesManaged.set_title()`, `set_xlabel()`, `set_ylabel()` — thin delegating methods for the same functionality on the higher-level managed axes API.
- Updated `examples/vispy_axes_display_example.py` to demonstrate all three labels.

[Unreleased]: https://github.com/your-org/GSP_API/compare/v0.1.0...HEAD
