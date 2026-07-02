# S044 Scoping - Datoviz Grid Clipping Proof And View3D Mesh Triangle Picking

## Stage Goal

Advance two remaining Datoviz capability gaps after S043:

- consolidate native Datoviz grid clipping as an independently verified capability without
  over-claiming full guide strictness; and
- define and then implement a bounded View3D mesh triangle picking/readback proof distinct from
  `query.view3d.ray_readback.v1`.

## Current State

| Area | State | Notes |
|---|---|---|
| Datoviz grid clipping | Native verified on current local source | Datoviz commit `9ba820489` supplies plot viewport plus plot clipping. GSP detects this separately from guide strictness. |
| Datoviz guide strictness | Completed in S043 where evidence-backed | Guide strictness still depends on guide identity, layout boxes, query/readback, all-rendered contributions, and snapshot equality. |
| Datoviz View3D ray readback | Supported for canonical ray-context payloads | `query.view3d.ray_readback.v1` returns public ray context, not a visual hit. |
| View3D mesh triangle picking | Accepted by P028, implementation pending | Public capability is `query.view3d.mesh_triangle_pick.v1`; GPU remains a private implementation route. |

## Authority And Boundary

Follow:

1. `PROJECT_CHARTER.md`
2. `ARCHITECTURE.md`
3. `SPEC_INDEX.md`
4. `spec/layout.md`
5. `spec/query.md`
6. `spec/view3d.md`
7. `spec/view3d_navigation.md`
8. `spec/backends/datoviz.md`
9. accepted ADRs and `.agent/decisions/**`
10. existing source code

GSP public semantics must remain backend-independent. Datoviz-native shader, draw-state, Vulkan,
controller, framebuffer, and object-id implementation names remain private backend details.

## Mission Stack

| Mission | State | Purpose |
|---|---|---|
| M189 | completed | Open S044 and create the P028 GPU 3D picking consultation packet. |
| M190 | ready | Consolidate Datoviz native grid clipping proof and ensure review/capability wording is precise. |
| M191 | completed | Integrate the P028 response into ADR/spec/mission boundaries for View3D mesh triangle picking. |
| M192 | ready | Implement the bounded View3D mesh triangle picking proof accepted by P028. |

## Implementation Order

1. Audit the current Datoviz grid clipping capability gate, review rows, diagnostics, docs, and
   capability matrix. Keep grid clipping native-verified but separate from full guide strictness.
2. Submit `.agent/consultations/P028-gpu-3d-visual-picking.md` to ChatGPT Pro and wait for the
   response.
3. Convert the P028 response into durable protocol authority: ADR/spec updates, capability names,
   query payload shape, strict/adapted boundaries, and implementation stop conditions.
4. Implement only the accepted bounded mesh triangle picking proof with tests, review artifacts, and
   capability gates.

## Stop Conditions

- Stop if grid clipping evidence depends on overlay masking or hidden layout state.
- Stop before promoting Datoviz guide rows solely because grid clipping is native-verified.
- Stop mesh triangle picking implementation if public visual/triangle mapping or pick-scene
  freshness cannot be proven.
- Stop if the public query surface would expose Datoviz-private object ids, shader names, pipeline
  details, or toolkit event concepts.
- Stop if visual picking cannot prove snapshot/revision freshness against the render state used for
  the pick.

## Acceptance

- `tools/agentctl next` lists M190 as the next ready mission and M191 as blocked pending P028.
- Grid clipping capability wording remains accurate for both verified and unverified Datoviz builds.
- Mesh triangle picking implementation follows the accepted P028 backend-neutral protocol boundary.
