# M097-S026 - Datoviz runtime scalar color slice

## Mission

M097

## Goal

Implement or explicitly capability-gate the narrow accepted S026 scalar color runtime slice in the
Datoviz v0.4 adapter.

## Status

Completed.

## Deliverables

- Completed: Datoviz scalar `ImageVisual` color-scale CPU pre-mapping for finite eager arrays.
- Completed: Datoviz `PointVisual` scalar color CPU pre-mapping for finite eager arrays.
- Completed: Shared S026 scalar mapping helper moved to `gsp.protocol.color_mapping`.
- Completed: Semantic scalar query payload decoration from retained point/image scalar source data.
- Completed: Structured unsupported diagnostics for ColorbarGuide rendering/query.
- Completed: Structured unsupported diagnostics for marker scalar fill and retained mesh scalar gate.
- Completed: Focused tests for implemented paths and capability-gated paths.

## Notes

- The Datoviz adapter now accepts a `color_scales` registry and uses canonical S026 mapping through
  shared protocol color-mapping utilities.
- CPU pre-mapping is recorded in Datoviz capability metadata as `cpu_premap_scalar_to_rgba`.
- Query decoration is deterministic when the Datoviz query result can be matched to exactly one
  retained scalar point/image visual and includes usable item or texel identity.
- Requested scalar query payloads that cannot be matched return `unsupported` with
  `scalar_query_source_unavailable`.

## Validation

- Full suite: `346 passed, 2 skipped`.
- Focused Datoviz renderer suite: `61 passed`.
- Focused S026 reference/query suite: `57 passed`.
- Touched source strict mypy: clean.
- Touched files ruff: clean.
- Backend import checks: Matplotlib and DatoViz imports passed with `PYTHONPATH=src`.
- Repo-wide strict mypy still fails on existing type debt and missing stubs outside this mission.

## Acceptance

- Follows `spec/color_mapping.md`, `spec/backends/datoviz.md`, and
  `spec/backend_capabilities_visuals.md`.
- Does not alter public protocol or VisPy2 API semantics.
- Emits structured diagnostics for unsupported or lossy behavior.
