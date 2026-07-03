# M203 - S050 strict 3D depth and mesh semantics scoping

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed by local-main-codex.

## Summary

Scope strict 3D raster and mesh behavior after mesh-picking evidence is known. Candidate targets
include strict opaque GPU depth proof, culling policy, alpha limitations, face/vertex query
expansion, and clearer test fixtures for adapted versus strict 3D behavior.

## Stop Conditions

- Stop before advertising `meshvisual.positions3d.opaque_depth.v1` without independent strict
  less-depth evidence.
- Stop before accepting culling or non-opaque alpha semantics without explicit spec authority.

## Result

Completed locally. See `.agent/S050_STRICT_3D_DEPTH_MESH_SCOPING.md`.

Outcome: strict opaque 3D depth remains unadvertised for Datoviz pending an independent retained
View3D runtime proof. Matplotlib remains an adapted CPU-sorted 3D raster path. Follow-up work was
split into M209 fixture planning, M210 Datoviz runtime proof, and M211/M212 ChatGPT Pro consultation
packets for culling/alpha and expanded 3D query semantics.
