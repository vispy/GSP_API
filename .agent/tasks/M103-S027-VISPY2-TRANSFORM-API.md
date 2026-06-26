# M103-S027 - VisPy2 transform/view producer API

## Mission

M103

## Goal

Add bounded VisPy2 producer API support for accepted S027 affine transform bindings and deterministic
View2D state.

## Status

Ready.

## Deliverables

- Add producer-level affine2d helper or equivalent.
- Accept visual `transform=` parameters for supported positional visual methods.
- Ensure `set_xlim`, `set_ylim`, and any new `set_view2d` convenience emit accepted `View2D`.
- Add focused tests and docs/examples where local patterns call for them.

## Acceptance

- VisPy2 emits GSP protocol transform records, not backend-native objects.
- Existing VisPy2 protocol tests remain green.
- Deferred 3D/camera/controller semantics remain absent.

## Stop Conditions

- Stop if a public transform stack/graph, camera object, or controller event model is needed.
