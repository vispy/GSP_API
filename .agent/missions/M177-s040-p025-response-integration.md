# M177 - S040 P025 response integration

## Stage

S040 - Datoviz Strict Flat Lambert Promotion

## Status

Completed by local-main-codex.

## Summary

Convert the P025 response into a durable S040 decision and, if approved, open the implementation
mission for Datoviz strict S039 flat Lambert support.

## Deliverables

- Archive the pasted P025 response as `.agent/consultations/P025-response.md`.
- Add a durable S040 decision record and any required ADR/spec/backend-spec updates.
- Decide whether Datoviz should use CPU-resolved exact face colors, a native lighting path, or stay
  explicitly unsupported.
- Open the next implementation or closeout mission.

## Acceptance

- The chosen route preserves accepted S039 public protocol semantics.
- Capability promotion criteria are explicit before any Datoviz advertisement changes.
- Required fixtures and diagnostics are listed before implementation.

## Stop Condition

Stop if P025 does not provide enough evidence to choose between CPU-resolved colors, native Datoviz
lighting, or continued unsupported behavior.

## Result

Completed. Archived `.agent/consultations/P025-response.md`, accepted CPU-resolved exact per-face
colors as the S040 Datoviz strict route, added ADR-0027 and S040 decision/backend-spec updates, and
opened M178 for implementation.
