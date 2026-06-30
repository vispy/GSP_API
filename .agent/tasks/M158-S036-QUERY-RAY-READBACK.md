# M158 - S036 query ray readback

Add strict projection-inverse ray context for `View3D` while keeping 3D mesh picking deferred.

## Deliverables

- Query payload with panel xy/NDC, near/far DATA points, ray direction, and snapshot ids.
- Center/corner ray fixtures.
- Stale snapshot mismatch diagnostics.
- Structured unsupported result for 3D visual hit requests.

## Stop Condition

Stop if ray-triangle picking or depth-buffer readback becomes required.

