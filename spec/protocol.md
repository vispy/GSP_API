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
