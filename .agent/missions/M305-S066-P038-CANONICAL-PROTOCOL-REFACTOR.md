# M305 - S066 P038 canonical protocol refactor

## Status

Completed under `local-main-codex` on 2026-07-30 after owner approval.

## Goal

Implement P038 as the long-term pre-publication architecture across canonical GSP protocol,
specification, adapters, conformance, and the VisPy2 producer boundary.

## Scope

- identity-only `Panel` and required versioned scene-level explicit panel layout;
- centralized normalized-to-logical-pixel resolution and per-panel resolved snapshots;
- attachment-owned `ClipScope` with no `View2D.clip`;
- Matplotlib and Datoviz consumption of core-resolved panel and plot rectangles;
- VisPy2-local non-wire `EmissionFeature` API and removal of producer identifiers from GSP;
- checked-in migration evidence, direct multi-panel fixtures, documentation, and release gates.

## Non-goals

Do not add speculative grid, nested, overlapping, or constraint layout variants. Do not preserve
runtime aliases for unpublished fields or capability identifiers. Do not tag, publish, push, merge,
or modify Datoviz itself.

## Stop conditions

Stop before backend resource creation when a requested layout, clip scope, material, or filtering
case is unsupported. Stop and report if implementation conflicts with higher authority than the
accepted P038 decision.

## Acceptance

- P038 release gate checklist is satisfied or every remaining item is explicitly evidenced as a
  publication blocker.
- Source, strict typing, lint, documentation, conformance, built-wheel, and installed-wheel gates
  pass for the affected publication set.
- Changes are recorded as traceable commits in mission control, GSP, and VisPy2 without publication.

## Completion evidence

- GSP source: 802 tests passed; strict mypy passed for 51 source files; Ruff and schema syntax passed.
- VisPy2 source: 126 tests passed; strict mypy passed for four source files; Ruff and strict MkDocs
  passed.
- Four fresh wheels built and installed together; the installed qualification set passed 928 tests.
- Migration fixtures cover the before/after scene shape and deterministic conversion report.
- Matplotlib and Datoviz reject unsupported multi-panel or clip-scope requests before backend
  resource creation.
- GSP recorded the refactor in `ed08d18`; VisPy2 recorded its producer migration in `1d1842c`.
- No Datoviz source, version, tag, push, publication, or merge operation was performed.
