# GSP v0.1 Conformance Fixtures

These fixtures define the current GSP v0.1 vertical-slice baseline.

They are Python/in-process fixtures, not JSON fixtures. This is intentional: the local fast path must carry protocol objects, NumPy arrays, and memoryviews directly without mandatory JSON/base64 serialization.

## Covered

- Stable protocol object IDs.
- Reference `CapabilitySnapshot` for the v0.1 slice.
- Point visual with float32 positions, rgba8 colors, and scalar-per-item sizes.
- Image visual with rgba8 data, explicit extent, and explicit origin.
- Point-over-image panel query with frontmost z-order behavior.
- Matplotlib reference rendering for point and image visuals.

## Reference Backend

Matplotlib is the reference/conformance backend for this baseline. Tests inspect Matplotlib artists and deterministic CPU query results. Datoviz v0.4 remains the flagship GPU backend target, but Datoviz conformance is not required until its adapter slice exists.

## Not Covered Yet

- Datoviz rendering or query execution.
- VisPy2 producer API.
- Extension manifests.
- Virtual or tiled data sources.
- Production transport encodings.
- JSON/base64 replay fixtures.
