# GSP Protocol Spec - Draft

GSP is a Graphics Server Protocol for semantic scientific visualization.

The protocol defines a session between a producer/client and a renderer/server. The server may be local/in-process or remote.

Minimum command categories:

- initialize/session;
- capability query;
- resource creation/update;
- visual creation/update;
- transform creation/update;
- panel/camera/controller state;
- frame submission;
- panel query/readback;
- diagnostics/events;
- shutdown.

The protocol semantics are independent from the transport encoding.

The first implementation should prove:

1. local in-process point/image scene;
2. Matplotlib reference rendering;
3. Datoviz v0.4 mapping assessment;
4. one panel-query proof.

## M002 protocol spine

The first concrete protocol models live in `src/gsp/protocol/`.

They define:

- stable protocol IDs and object references;
- `CapabilitySnapshot` and adaptation decisions;
- contiguous `BufferResource` and `AttributeSource` descriptors;
- ordered `CommandBatch` and minimum command categories;
- an `InProcessTransport` contract for the local fast path.

These models intentionally coexist beside the legacy object graph. Legacy renderers are not yet required to consume them directly.

## S027 transform/view baseline

`spec/transforms.md` is the authority for accepted S027 transform and view semantics. The public
protocol accepts only finite invertible 2D affine transform resources or inline visual transform
bindings, plus deterministic linear `View2D` state. Public 3D camera, projection, controller,
navigation-event, transform-stack, and nonlinear transform semantics are reserved/deferred.

Implementation work must add protocol-owned dataclasses/enums/validation for `AFFINE_2D`,
`View2D`, visual transform bindings, placement capabilities, and transform query inverse payloads
without exposing Matplotlib transform objects, Datoviz slots, backend shader handles, or native
camera objects.

## S029/S034 resolved layout baseline

`spec/layout.md` is the authority for resolved guide layout, logical pixels, render targets, layout
snapshots, and layout conformance tiers. GSP guide records remain semantic protocol objects.
`ResolvedLayoutSnapshot` is a derived artifact used when a backend advertises layout-strict render,
query, readback, or all-rendered guide behavior.

Render and query results must carry a matching `layout_snapshot_id` whenever layout strictness is
claimed. Backend-native layout may remain an implementation mechanism, but it is not the protocol
contract unless the resulting GSP layout snapshot is exposed.

## S035 View2D navigation baseline

`spec/navigation.md` is the authority for accepted S035 `View2D` navigation semantics. Public
navigation is expressed as deterministic semantic actions such as `pan_by`, `zoom_about`, `set_view`,
and `reset_view`; accepted actions produce explicit `View2D` updates and revision/snapshot
identifiers.

Raw mouse, wheel, keyboard, touch, toolkit, browser, Datoviz, Matplotlib, or VisPy event streams are
backend or producer adapters, not public protocol semantics. Retained GPU backends must lower strict
pan/zoom to panel view/projection or equivalent uniform/state updates for unchanged visuals rather
than re-uploading visual geometry buffers.

S035 includes a small backend-neutral pointer adapter for review/integration, but the public
protocol boundary remains the semantic action/result model. Current reviewed paths are Matplotlib
native drag/wheel review, Datoviz retained scripted smoke, and Datoviz v0.4 union input events
adapted into GSP semantic navigation actions. Backend-native controllers such as Datoviz
`dvz_view_panzoom()` are not strict GSP navigation unless their resulting state is synchronized back
to canonical `View2D`.
