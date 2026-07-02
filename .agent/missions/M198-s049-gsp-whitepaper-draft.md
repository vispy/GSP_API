# M198 - S049 GSP white paper draft for Nicolas review

## Stage

S049 - GSP White Paper Draft

## Status

Completed by local-main-codex.

## Summary

Prepare a community-facing GSP white paper draft suitable for review by Nicolas Rougier and Cyrille
Rossant. The draft should present the current protocol, capability, conformance, backend, and
VisPy2 direction while preserving the central rationale: GSP is not another plotting library, but a
shared protocol layer for scientific visualization.

## Deliverables

- A tracked `whitepaper/` source tree with LaTeX source, reusable figures, and build output.
- A narrative draft aimed at scientific visualization library developers.
- A short review note identifying authorship, technical claims, and specific feedback requested
  from Nicolas.
- A rendered PDF validated for basic layout and legibility.

## Acceptance

- The paper explains the rationale and intent without becoming API reference.
- Current GSP concepts are represented accurately at a high level: session protocol, semantic visual
  families, capability discovery, explicit adaptation, query/readback, conformance fixtures,
  Matplotlib reference rendering, Datoviz GPU rendering, and VisPy2 as producer API.
- The draft is honest about current status and open questions.
- The PDF builds locally.

## Stop Conditions

- Stop before changing public protocol semantics.
- Stop before claiming unproven backend capability support.
- Stop before launching external workers.
- Stop before public release or PR creation.

## Result

Completed. See `.agent/S049_CLOSEOUT.md`.

The draft source, rendered PDF, figures, and review notes live under `whitepaper/`.
