# M305 review - P038 canonical protocol refactor

Date: 2026-07-30

## Decision

Accepted and complete.

## Architecture delivered

- `Panel` is identity-only; every scene carries a versioned explicit normalized panel layout.
- Core resolves normalized panel allocation to deterministic logical-pixel rectangles and produces
  per-panel layout snapshots.
- Attachments own `PLOT`, `PANEL`, or `RENDER_TARGET` clipping; `View2D` no longer owns clipping.
- GSP session capabilities are provider-neutral. VisPy2 producer emission features are local,
  non-wire values and old producer-prefixed requests fail closed.
- Matplotlib and Datoviz consume core-resolved geometry and reject unsupported topology or clipping
  before creating backend resources.
- Checked-in schemas, specifications, migration fixtures, and direct conformance tests define the
  new boundary without compatibility aliases.

## Qualification

| Gate | Result |
|---|---|
| GSP source | 802 passed |
| GSP typing/lint | strict mypy clean for 51 files; Ruff clean |
| VisPy2 source | 126 passed |
| VisPy2 typing/lint/docs | strict mypy clean for 4 files; Ruff and strict MkDocs passed |
| Installed four-wheel set | 928 passed |
| Schemas and diff integrity | passed |

Traceability commits: GSP `ed08d18`; VisPy2 `1d1842c`.

## Remaining publication boundary

P038 is closed. Publication still requires explicit owner authorization and an ordinary compatible
Datoviz dependency or a publication set that formally excludes the development-only Datoviz
adapter. This review performs neither release operation.
