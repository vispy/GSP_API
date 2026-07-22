# P037 review - VisPy2 and GSP repository architecture

Date: 2026-07-22

## Outcome

The P037 response is complete, internally coherent, and aligned with the project charter and target
architecture. Mission Control recommends accepting its central topology:

- create a clean `gsp` repository for protocol authority, backend SPI, conformance, and the initial
  Matplotlib and Datoviz adapter distributions;
- create a separate clean `vispy2` repository for the plotting producer;
- retain `GSP_API` as the complete, recoverable research archive;
- use fresh root commits with explicit source/blob provenance rather than filtered ancestry;
- separate `gsp-core`, `gsp-matplotlib`, `gsp-datoviz`, and `vispy2` distributions;
- route execution through lazy `gsp.backends` providers and backend-neutral GSP sessions.

## Authority review

The response preserves the existing non-negotiable boundaries:

- GSP remains independent of any one producer or transport.
- VisPy2 figures and axes retain semantic state only.
- Sessions own adapters, devices, windows, event loops, resources, and displays.
- The local path remains typed and in-process without mandatory JSON/base64.
- Capabilities and adaptations remain explicit and diagnostic-bearing.
- Matplotlib stays the 0.x one-shot publication default; Datoviz remains the flagship GPU adapter.

No conflict was found with `PROJECT_CHARTER.md`, `ARCHITECTURE.md`, or the GSP 0.2 semantic
specification.

## Decision requiring owner approval

P037 intentionally changes the temporary external identity recorded by accepted ADR-0033:

| Existing 0.2 prototype decision | P037 target |
|---|---|
| distribution `gsp-vispy2` | distribution `vispy2` |
| import `gsp_vispy2` | import `vispy2` |
| one combined repository/distribution | separate `gsp` and `vispy2` repositories and distributions |

This is a justified pre-publication break, but it requires explicit owner approval and a separate
confirmation that use of the `vispy2` repository and distribution identity is authorized and will
not misrepresent an upstream release. Until then ADR-0035 remains proposed and no package may be
published under that name.

## Operational qualifications

- The response's tag and bundle commands are a design, not authorization to create tags or durable
  archives.
- Durable bundle storage and the eventual hosting locations of the two repositories remain owner
  decisions.
- New repositories should first be local and unpublished; remote creation, pushes, archive-mode
  changes, and releases require separate explicit approval.
- The Datoviz adapter may be migrated and tested from source, but its publication remains gated on a
  normally installable RC3-compatible artifact and exact checkpoint replay.
- The proposed public session SPI is architectural direction; exact method signatures still require
  tests and bounded implementation review rather than being copied verbatim from the consultation.

## Recommended first stage

Approve proposed S061 only as a non-destructive migration foundation: accept the topology and naming
decision, reproduce and record the source baseline, create and verify a recoverable local archive,
and produce a reviewed migrate/archive/defer manifest. Creating the new product repositories is a
later stage with its own explicit approval.

