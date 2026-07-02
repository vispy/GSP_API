# S050 Scoping - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

Generated: 2026-07-02

## Decision

Open S050 as the implementation branch after the post-S048 status review.

The user approved moving beyond planning with the instruction to stop only when manual action is
needed. The first technical target is Datoviz native `query.view3d.mesh_triangle_pick.v1` evidence,
because it is the most visible current "must not advertise" capability boundary.

## Current State

| Area | State | Notes |
|---|---|---|
| Protocol/spec authority | Current through S048 | S044 already accepted backend-neutral mesh triangle picking and Matplotlib CPU oracle behavior. |
| Datoviz mesh picking | Not advertised | Needs public GSP `visual_id`, canonical triangle `primitive_index`, and freshness evidence. |
| Datoviz guide/layout | Partial strictness | Native grid clipping is verified separately; guide query/all-rendered guide contributions remain unsupported. |
| Datoviz text/colorbar | Adapted/capability-gated | Strict text anchors/rotation/multiline/query and colorbar query/tick parity remain future work. |
| Strict 3D raster semantics | Deferred | Opaque GPU depth, culling, non-opaque alpha, and richer mesh query semantics need bounded proof. |
| Materials/textures/VisPy2 API | Architecture/API-shape work | Requires ChatGPT Pro consultation before implementation. |
| Release mechanics | Deferred | M131 still requires explicit target version, package version update, tag, and publication target. |

## Mission Batch

| Mission | State | Purpose |
|---|---|---|
| M199 | completed | Reconcile control-plane state, open S050, and draft the implementation batch. |
| M200 | approved | Inspect/prove Datoviz native mesh-pick evidence without promoting capability prematurely. |
| M201 | draft | Scope Datoviz query/readback parity after M200 reports its API evidence. |
| M202 | draft | Scope Datoviz guide, text, and colorbar strictness after the picking evidence branch. |
| M203 | draft | Scope strict 3D depth and mesh semantics. |
| M204 | blocked | Prepare ChatGPT Pro consultation for materials/textures and broader VisPy2 public API shape. |

## M200 Acceptance

M200 should answer these questions with source/runtime evidence:

- Does the local Datoviz v0.4 checkout expose a public pick result with enough information to map
  native state to GSP `visual_id` and canonical mesh triangle `primitive_index`?
- Can GSP prove pick-scene freshness against layout, View3D revision, projection snapshot, and
  pick-scene snapshot ids?
- Can the adapter implement this inside GSP only, or does Datoviz need an upstream API handoff?
- If implementation is possible, what is the smallest safe follow-up mission?

## Stop Conditions

- Stop before editing the sibling Datoviz repository unless the user explicitly approves that
  scope.
- Stop before advertising Datoviz `query.view3d.mesh_triangle_pick.v1`.
- Stop and create a ChatGPT Pro consultation packet if M200 discovers a protocol semantic conflict
  rather than a binding/evidence gap.
- Stop before release mechanics, version bumps, tags, publishing, PR creation, force pushes, or
  external repository changes.

## Provider Guidance

M200 is approved for `codex-ucl` as a bounded evidence mission. If provider launch is unsafe or
manual, execute it in the current local Mission Control session.
