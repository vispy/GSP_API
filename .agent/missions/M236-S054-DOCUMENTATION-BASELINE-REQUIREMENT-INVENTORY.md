# M236 - S054 documentation baseline and normative requirement inventory

## Stage

S054 - GSP 0.2 Protocol API And Documentation Consolidation

## Status

Completed.

## Summary

Preserve the protocol-centered public-documentation draft, classify the existing normative corpus,
and create an auditable old-to-new requirement inventory before the detailed GSP 0.2 rewrite.

## Acceptance

- Commit the accepted P034 decision and current public-site draft as an explicitly incomplete
  baseline.
- Inventory every authoritative specification source by durable domain and disposition.
- Establish stable requirement identifiers and a machine-checkable traceability format.
- Strict MkDocs builds and no accepted rule is silently discarded.

## Stop Conditions

Stop on a charter/architecture conflict requiring a new decision. Do not treat implementation as
semantic authority. Do not publish, tag, push, merge, or edit external repositories.

## Approval

The project owner approved the full breaking consolidation and requested commits along the way.

## Result

The protocol-centered public site and P034/ADR-0032 decision are preserved as a strict-building
baseline. `spec/current/` is explicitly a consolidation draft rather than a falsely complete
implementation specification. The traceability inventory classifies 101 sources: 39 detailed
normative sources, 10 consolidation chapters, 34 accepted ADRs, and 18 accepted decision records.

Stable requirement IDs, a JSON registry schema, a deterministic inventory generator/checker, and
focused tests are in place. Every detailed specification source has a target semantic chapter.
