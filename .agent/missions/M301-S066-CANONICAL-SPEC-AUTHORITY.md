# M301 - S066 canonical GSP 0.2 specification authority

## Status

Approved by the owner and completed on 2026-07-30.

## Goal

Resolve Q190 without manual intervention by designating one current specification home and making
the historical boundary explicit.

## Acceptance

- Fresh-root `gsp` is explicitly canonical for GSP 0.2.
- GSP_API is explicitly historical rather than a competing current specification.
- Broken canonical index paths are corrected.
- Later archive-only semantics are queued for deliberate synchronization rather than silently
  overriding the canonical registry.

## Non-goals

This mission does not synchronize every specification chapter, revise the white paper, change
public APIs, tag, publish, push, or merge.
