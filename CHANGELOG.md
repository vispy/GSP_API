# Changelog

All notable changes are recorded here. The project is pre-1.0 and follows semantic versioning for
development releases.

## [Unreleased]

### Breaking changes

- Renamed the distribution to `gsp-vispy2` 0.2.0 and the independent producer import to
  `gsp_vispy2`; removed the ambiguous `vispy2` compatibility package.
- Moved the public learning path from the legacy `Canvas`/`RendererBase` system to semantic GSP 0.2
  records, explicit capabilities, structured results, and explicit execution boundaries.
- Removed legacy mesh-shading aliases and tightened transport initialization, sequencing, lifecycle,
  snapshot identity, command status, and diagnostic contracts.

### Specification and conformance

- Consolidated the GSP 0.2 target specification into ten detailed normative chapters with 90 stable
  requirement identifiers and explicit dispositions for 101 source documents.
- Added machine-readable producer and renderer profiles that separate strict, adapted, partial,
  unsupported, and blocked scopes with concrete evidence.
- Added requirement-to-test traceability, a generated public feature matrix, and consistency tools
  enforced by CI.

### Public documentation

- Added an executable first tutorial sourced directly from `examples/docs/first_scene.py`.
- Added curated producer, lifecycle/transport, scene/resource/visual, query, and diagnostic API pages.
- Added 0.2 migration guidance, legacy URL redirects, screenshot provenance, repository links, and
  explicit source-only/pre-1.0 maturity boundaries.

### Backend support

- Matplotlib remains the required portable reference backend and publishes an exact 0.2 profile.
- Datoviz v0.4 remains optional and capability-gated; no symbol, screenshot, or unrelated test is
  treated as feature promotion.
- Added an experimental explicit `open_session("datoviz")` preview for capability inspection,
  bounded blocking display, one-frame polling, structured diagnostics, and deterministic cleanup.
- Texture2D mesh rendering remains unsupported by Matplotlib. The Datoviz adapter now advertises
  the bounded strict capability when the post-RC2 field-slot sampling API is present, using the GSP
  nearest/clamp/no-mipmap profile. GSP now also exposes visual-owned nearest-or-linear filtering;
  Datoviz maps the choice to both field-slot filters and advertises linear support separately after
  exact offscreen conformance, while VisPy2 emits it through `texture_filter="linear"`.
- No production current-protocol remote transport, general retained display-update API, close
  callbacks, or event-loop embedding contract is claimed.

### Validation

- Full pytest, targeted strict mypy, Ruff, package build, specification/profile/public-doc checks,
  executable tutorial, compatibility redirects, and strict MkDocs build.

## [0.1.0] - 2026-03-16

### Added

- Initial object-oriented plotting and visualization prototype.
- Matplotlib, legacy Datoviz, network, Pydantic, and high-level plotting experiments.
- Early examples, tests, and project documentation.

[Unreleased]: https://github.com/vispy/GSP_API/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/vispy/GSP_API/releases/tag/v0.1.0
