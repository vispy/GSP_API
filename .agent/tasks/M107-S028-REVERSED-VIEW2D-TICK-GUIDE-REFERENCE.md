# M107-S028 - Reversed View2D tick and guide reference behavior

## Mission

M107

## Goal

Implement reference tick/grid rendering behavior for reversed `View2D` limits after M106 defines
the exact semantics.

## Status

Draft.

## Deliverables

- Tick resolver support for reversed finite domains.
- Matplotlib guide rendering tests for reversed x/y limits.
- Grid visibility/placement checks under reversed limits.

## Acceptance

- Focused tests pass.
- No Matplotlib native locator authority leaks into GSP semantics.
