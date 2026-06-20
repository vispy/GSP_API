# M011 - Extensions and virtual data-source architecture proof

## Goal

Create a spec-first proof for GSP extensions and virtual data sources, focused on huge tiled/image-like datasets and server-side fetch semantics.

This mission should not implement a large distributed renderer. It should produce a small, testable architecture slice and one local reference proof if the ADR permits it.

## State

Draft. Requires ChatGPT Pro consultation before implementation beyond documentation.

## Required reading

- PROJECT_CHARTER.md
- ARCHITECTURE.md
- spec/extensions.md
- spec/data_sources.md
- spec/resources.md
- spec/visuals/image.md
- spec/query.md
- M006 ADR and conformance baseline
- M008 VisPy2 producer MVP if complete

## Expected tasks

- Create a ChatGPT Pro consultation packet for extension/data-source v0.1 scope.
- After consultation, create an ADR for:
  - extension manifests;
  - virtual data sources;
  - data locality;
  - local vs server-side fetch;
  - minimal tiled image proof.
- Define a minimal `VirtualImageSource` or `TiledImageSource` model.
- Add a local fake tile provider proof only if the ADR scope is clear.
- Keep Matplotlib as reference implementation.
- Do not add real cloud credentials or remote fetch infrastructure.

## Allowed paths

- spec/extensions.md
- spec/data_sources.md
- spec/resources.md
- spec/visuals/image.md
- adr/
- tests/
- fixtures/
- src/gsp/ if approved by ADR
- src/gsp_matplotlib/ if approved by ADR
- .agent/consultations/
- .agent/tasks/
- .agent/status.json
- STATUS.md

## Forbidden paths

- src/gsp_datoviz/
- ../datoviz/
- real cloud credentials
- production remote renderer implementation
- broad plugin loader implementation before ADR

## Acceptance criteria

- ChatGPT Pro consultation packet exists before coding.
- ADR exists before implementation.
- Minimal scope is explicit.
- No production cloud/remote system is introduced.
- If implemented, local tiled-source proof has tests and uses no network credentials.

## Stop conditions

Stop if:

- extension model becomes too broad;
- security/credential model is unclear;
- server-side fetch policy is unclear;
- implementation would require Datoviz changes;
- this starts competing with VisPy2 or Datoviz adapter priorities.

## Notes

This is important but should not precede M006. Prefer after M008 unless strategic priority changes.
