# M100-S027 - Transform protocol dataclasses and validation

## Mission

M100

## Goal

Add the accepted S027 protocol model and validation layer for finite invertible 2D affine transforms,
linear `View2D`, visual transform bindings, placement vocabulary, and query inverse payload shells.

## Status

Ready.

## Deliverables

- Add protocol enums/dataclasses under `src/gsp/protocol/` using existing local style.
- Validate matrix shape, finiteness, affine final row, invertibility, transform references, view
  limits, and unsupported deferred kinds.
- Add focused tests for identity, translate, scale, rotate/shear, reversed view limits, and negative
  diagnostics.
- Keep renderer/backend behavior out of this mission except where imports need updating.

## Acceptance

- Focused tests pass.
- Protocol docs and code agree with `spec/transforms.md`.
- No backend-native transform object appears in public protocol models.

## Stop Conditions

- Stop on conflict with accepted ADR/spec authority.
- Stop if implementation requires deciding 3D camera/projection/controller behavior.
