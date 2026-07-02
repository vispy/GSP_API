# M202 - S050 Datoviz guide text and colorbar strictness scoping

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Draft pending M200/M201.

## Summary

Scope which adapted Datoviz guide, text, and colorbar rows can move toward strict support without
changing public protocol semantics. Candidate work includes guide query/all-rendered guide
contributions, panel title/layout parity, text anchors/rotation/multiline/query payloads, explicit
colorbar tick labels, and colorbar query.

## Stop Conditions

- Stop before claiming full guide strictness from grid clipping alone.
- Stop before changing text or colorbar public contracts without a consultation packet.
