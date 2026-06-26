# M103-S027 - VisPy2 transform/view producer API

## Mission

M103

## Goal

Add bounded VisPy2 producer API support for accepted S027 affine transform bindings and deterministic
View2D state.

## Status

Completed.

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

## Completion Notes

- Implemented bounded VisPy2 affine transform producer APIs.
- No backend-native transform, camera, shader, or controller object was exposed.
- Validation: full `uv run pytest tests/` passed with 363 passed and 8 skipped before the local
  tuple typing fix; focused VisPy2 tests passed after the fix; mypy reports only five pre-existing
  unrelated errors outside M103 scope.
