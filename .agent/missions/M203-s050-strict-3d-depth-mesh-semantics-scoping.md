# M203 - S050 strict 3D depth and mesh semantics scoping

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Draft pending M200.

## Summary

Scope strict 3D raster and mesh behavior after mesh-picking evidence is known. Candidate targets
include strict opaque GPU depth proof, culling policy, alpha limitations, face/vertex query
expansion, and clearer test fixtures for adapted versus strict 3D behavior.

## Stop Conditions

- Stop before advertising `meshvisual.positions3d.opaque_depth.v1` without independent strict
  less-depth evidence.
- Stop before accepting culling or non-opaque alpha semantics without explicit spec authority.
