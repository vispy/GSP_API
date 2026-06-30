# M155 - S036 projection and snapshot conformance

Implement deterministic orthographic projection math and snapshot identity for `View3D`.

## Deliverables

- Camera basis/projection helpers.
- View/projection snapshot ids.
- Canonical basis, cube projection, reversed bounds, and off-axis projection fixtures.

## Stop Condition

Stop if projection conventions are ambiguous or backend-specific clip/depth semantics leak into the
public contract.

