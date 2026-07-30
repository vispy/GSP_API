# S066 canonical GSP 0.2 specification authority

Date: 2026-07-30

## Decision

The fresh-root `gsp` repository is the sole canonical specification home for GSP 0.2.
`GSP_API` remains the complete historical archive and evidence source, but its `spec/` copy is not
current authority.

## Rationale

- The fresh repository owns the shipped protocol packages, conformance fixtures, adapters, and
  eleven-family registry.
- Its `AGENTS.md` already states that GSP_API material is not authoritative merely because it
  exists.
- Keeping current protocol authority beside the implementation and conformance surface avoids two
  independently evolving “current” copies.
- Historical GSP_API details remain useful migration inputs. Missing accepted semantics, including
  the later resolved-viewport material identified by M299, must be ported through reviewed
  specification changes rather than treated as an implicit override.

## Consequences

- Q190 is closed.
- Fresh `gsp/SPEC_INDEX.md` explicitly declares authority and uses the real `specs/current/` paths.
- `GSP_API/SPEC_INDEX.md` is marked historical.
- The pre-release audit must inventory semantic content present only in GSP_API and open explicit
  synchronization work where the canonical fresh specification is incomplete.
