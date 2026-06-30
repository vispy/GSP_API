# M157 - S036 opaque depth fixture

Establish the strict opaque 3D depth contract.

## Deliverables

- Opaque nearer-fragment-wins fixture.
- No-face-culling reversed winding fixture.
- Alpha-not-strict negative/adapted fixture.
- Clipping boundary documented as adapted/unsupported unless strict clipping lands.

## Stop Condition

Stop if strict depth requires exposing backend depth-buffer state as public protocol.

