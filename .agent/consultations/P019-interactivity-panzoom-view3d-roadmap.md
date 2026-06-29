# P019 - Interactivity, Pan/Zoom, and View3D Roadmap

## Prompt for ChatGPT Pro

You are advising on the next architecture stage for GSP_API, a Python Graphics Server Protocol-style
scene-description API for backend-agnostic scientific visualization.

The project has just completed a release-candidate API review pack. The user reviewed six examples
against both Matplotlib and Datoviz backends and approved the current public API shape. The remaining
gap is capability breadth: there is no live interactivity, no public pan/zoom controller semantics,
and no accepted public 3D camera/View3D semantics.

Important project facts:

- Authority order is: PROJECT_CHARTER.md, ARCHITECTURE.md, SPEC_INDEX.md, spec/**, accepted ADRs,
  .agent/decisions/**, LEGACY_MAP.md, existing source.
- Query/readback is first-class and must remain coherent with rendering semantics.
- Backends currently include Matplotlib reference behavior, Datoviz v0.4 mapping/adaptation, and a
  VisPy2-style producer API layer.
- Current stage is S033, "Datoviz Guide Strictness and Release Decision". Implementation is complete
  enough for a release candidate, pending explicit release approval.
- Existing examples/review include scatter, image, points-over-image, guides/ticks, color mapping
  with colorbar, and text labels. These were reviewed successfully by the user.
- Existing S027 transform/view baseline deliberately accepted only finite invertible 2D affine
  transforms and deterministic `View2D`. It explicitly deferred public controller, gesture,
  interaction, inertia, linked-navigation, event semantics, public 3D camera, View3D, projection,
  depth, clipping-plane, orbit-controller, 3D mesh query, material, lighting, and perspective
  semantics.
- Existing S027 decision says pan and zoom are represented as explicit `View2D` updates, but it does
  not define mouse, keyboard, gesture, wheel, inertia, linked-view, or controller event protocols.
- Existing MeshVisual v1 accepts `(N,2)` strict 2D triangular meshes and permits `(N,3)` positions
  only as capability-gated protocol data requiring an accepted 3D panel/view projection capability.
  MeshVisual does not define a camera or mesh-local transform.
- Existing layout work separates semantic guide records from derived layout snapshots. Render/query
  results must carry matching layout snapshot ids when layout strictness is claimed.
- Existing Datoviz support should use v0.4 retained-scene APIs where possible, but no backend-native
  object model should leak into public protocol semantics.
- The project prefers narrow, testable stages, explicit capability matrices, structured unsupported
  diagnostics, and conformance fixtures over broad unproven abstractions.

Decision problem:

Choose the next one to three implementation stages after the release-candidate review. The user is
asking what to build next because the current system lacks interactivity, pan/zoom, and true 3D.
We need a pragmatic roadmap that avoids overfreezing a graphics-engine object model while moving
toward useful live scientific visualization.

Candidate directions:

1. Release the current 2D/static API as v0.1 first, then start interactivity.
2. Add a narrow `View2D` pan/zoom controller stage before release.
3. Add a protocol-owned interaction/event model for pointer, wheel, keyboard, and controller state.
4. Add `View3D`/camera/projection semantics first so MeshVisual 3D can become useful.
5. Add Datoviz-native live interactivity as an adapted backend feature without public protocol
   guarantees.
6. Add VisPy2-style interactive producer conveniences while keeping the protocol static.

Please answer with a concrete staged recommendation.

Constraints for your answer:

- Do not recommend importing Matplotlib, Datoviz, VisPy, or browser event models wholesale into the
  public protocol.
- Preserve render/query/readback coherence.
- Preserve backend capability-gating and structured unsupported diagnostics.
- Prefer a small releaseable stage over broad architecture.
- Identify what requires strict conformance fixtures and what can remain adapted/experimental.
- Explicitly say whether release should happen before or after the first interactivity stage.
- If public interaction semantics are recommended, specify the minimal event/controller concepts and
  which concepts remain deferred.
- If public 3D is recommended soon, specify the minimal `View3D`/camera semantics and which 3D
  concepts remain deferred.

Expected output format:

1. Recommendation summary: 3-6 bullets.
2. Stage plan table with columns: Stage, Goal, Public semantics added, Backends, Fixtures, Stop
   condition.
3. Minimal accepted semantics for the first new stage.
4. Explicit deferrals.
5. Risks and mitigations.
6. A short Mission Control recommendation suitable for turning into mission records.

## Local Mission Control Note

Dependent implementation should pause until the response is pasted or committed as
`.agent/consultations/P019-response.md`.
