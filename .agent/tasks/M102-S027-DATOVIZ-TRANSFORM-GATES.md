# M102-S027 - Datoviz transform capability gates

## Mission

M102

## Goal

Add Datoviz capability gates and explicit adaptation diagnostics for the accepted S027 2D
transform/view subset.

## Status

Ready.

## Deliverables

- Advertise transform semantic capabilities and placement only when supported.
- Add structured unsupported diagnostics for deferred S027 behavior.
- Add bounded CPU adaptation for finite eager arrays only if it can preserve query/source semantics.
- Add focused tests for capability reports and unsupported/adapted paths.

## Acceptance

- Datoviz does not silently ignore transform bindings.
- Datoviz does not silently materialize virtual or huge sources for transforms.
- Render placement and query inverse support are separately visible.

## Stop Conditions

- Stop if current bindings cannot distinguish native/adapted/unsupported behavior.
- Stop on any need for public 3D camera/projection/controller semantics.
