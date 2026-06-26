# M102-S027 - Datoviz transform capability gates

## Mission

M102

## Goal

Add Datoviz capability gates and explicit adaptation diagnostics for the accepted S027 2D
transform/view subset.

## Status

Completed.

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

## Completion Notes

- Datoviz capability snapshots now expose S027 CPU-adapter placement and transform diagnostics.
- Inline affine transform adaptation is explicit and retained in renderer adaptation metadata.
- Transform query inverse requests return `GSP_QUERY_INVERSE_UNSUPPORTED`.
- Validation: full `uv run pytest tests/` passed with 359 passed and 8 skipped; backend import smoke
  passed; mypy still reports five pre-existing unrelated errors outside M102 scope.
