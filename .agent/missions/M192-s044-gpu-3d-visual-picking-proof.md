# M192 - S044 View3D mesh triangle picking proof

## Stage

S044 - Datoviz Grid Clipping Proof And View3D Mesh Triangle Picking

## Status

Completed by local-main-codex.

## Summary

Implement the bounded backend-neutral View3D mesh triangle picking proof accepted by P028.

## Candidate Deliverables

- Protocol query dataclasses and validation for the accepted visual-hit payload.
- Datoviz capability gates for the accepted picking route.
- Matplotlib/reference behavior or structured adapted diagnostics, depending on P028.
- Datoviz implementation using only private backend internals behind public GSP semantics.
- Focused tests for identity, depth/occlusion, stale snapshot rejection, and unsupported fallbacks.
- Review example proving a 3D visual hit differs from plain ray-context readback.

## Acceptance

- Capability is advertised only when all accepted P028 prerequisites are present.
- Query results include stable public visual identity and snapshot/revision freshness evidence.
- No public API exposes Datoviz-private implementation concepts.
- Older Datoviz builds report structured unsupported diagnostics.

## Stop Conditions

- Stop until M191 completes.
- Stop if picking cannot distinguish frontmost visible hit from ray construction alone when the
  accepted semantics require occlusion-aware visual identity.

## Result

Completed locally. Added the S044 typed request/response payloads, diagnostics, capability constant,
Matplotlib CPU reference oracle for strict-scope DATA-space mesh triangle picking, Datoviz
non-advertisement metadata plus structured unsupported renderer response, and focused tests.

Datoviz does not advertise `query.view3d.mesh_triangle_pick.v1` yet because public visual/triangle
mapping and synchronized native pick-state freshness are not proven.
