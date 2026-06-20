# M006 - Protocol hardening and conformance baseline

## Goal

Stabilize the current working GSP v0.1 vertical slice into a coherent mini-contract covering stable IDs, capabilities, resources, command batches, point/image visuals, Matplotlib reference rendering, and reference panel query.

The goal is not to add major new features. The goal is to make the current slice harder to accidentally break and easier for Datoviz and VisPy2 agents to consume.

## State

Ready for Mission Control discussion.

## Required reading

- PROJECT_CHARTER.md
- ARCHITECTURE.md
- SPEC_INDEX.md
- LEGACY_MAP.md
- STATUS.md
- spec/protocol.md
- spec/capabilities.md
- spec/resources.md
- spec/query.md
- spec/visuals/point.md
- spec/visuals/image.md
- spec/backends/matplotlib.md
- Existing tests around protocol, resources, visuals, Matplotlib renderer, and query.

## Expected tasks

- Create or complete ADR-0003 defining the GSP v0.1 mini-contract scope.
- Add or refine conformance fixtures for:
  - point visual;
  - image visual;
  - point-over-image query;
  - basic capability snapshot.
- Ensure fixtures exercise the local in-process path and do not require JSON/base64.
- Add a compact conformance README explaining how Matplotlib acts as reference backend.
- Tighten tests so future agents cannot silently change:
  - ID behavior;
  - visual schema expectations;
  - query status semantics;
  - Matplotlib point/image rendering assumptions.
- Update STATUS.md and .agent/status.json.

## Allowed paths

- adr/
- spec/
- fixtures/
- tests/
- src/gsp/
- src/gsp_matplotlib/
- .agent/status.json
- STATUS.md
- .agent/tasks/
- .agent/reviews/

## Forbidden paths

- src/gsp_datoviz/
- src/vispy2/
- ../datoviz/
- Any Datoviz external checkout.
- Any provider credential or aisw profile file.

## Acceptance criteria

- All existing tests pass.
- New conformance tests pass.
- A clear ADR exists for v0.1 vertical-slice scope.
- Matplotlib remains reference backend for point/image/query.
- No mandatory JSON/base64 is introduced into the local execution path.
- STATUS.md and .agent/status.json reflect M006 completion or blockage.

## Stop conditions

Stop and create a consultation packet if:

- the v0.1 protocol scope becomes ambiguous;
- the task requires changing Datoviz code;
- the task requires broad transform or extension design;
- fixture format would force JSON/base64 as the primary local path;
- tests reveal incompatible assumptions from M002-M005.

## Notes

This mission should be consolidation, not expansion. It should prepare M007 and M008.
