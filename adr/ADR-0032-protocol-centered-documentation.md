# ADR-0032: Protocol-Centered Public Documentation

Status: accepted

## Context

The repository contains the current GSP protocol model and an older object-oriented renderer API.
The public website presented both as one architecture, while normative specifications were partly
organized around internal delivery stages. This obscured the authority defined by the project
charter and made backend support appear broader than the available evidence.

## Decision

Public documentation will describe one model: producers create semantic GSP records for a
capability-negotiated session, and backend adapters execute the accepted operations. VisPy2 is the
intended high-level producer, Matplotlib is the reference backend, and Datoviz v0.4 is a
capability-gated GPU backend.

The legacy `Canvas`/`Viewport`/`RendererBase` API, `datoviz-v03`, and the legacy Flask renderer are
compatibility material. They will not appear in recommended learning paths. Protocol semantics,
backend profiles, conformance evidence, decision rationale, and development history will be kept
as separate documentation layers.

Support claims use explicit states and scopes. A screenshot or available backend symbol does not
establish strict support. Public documentation must also distinguish accepted protocol contracts
from executable session infrastructure that has not yet been implemented.

Internal stage, mission, and consultation identifiers are not part of public or normative
terminology. Historical records remain preserved outside the recommended reading path.

## Consequences

- New users receive a concept-first protocol explanation.
- Legacy documentation remains available but is visibly isolated.
- Backend comparisons require evidence-aware captions and provenance.
- The specification can be normalized by durable semantic domain without changing protocol
  behavior.
- Documentation must not invent a session or convenience API to make a tutorial appear complete.

## Basis

Accepted from the P034 ChatGPT Pro consultation response in
`.agent/consultations/P034-response.md`.
