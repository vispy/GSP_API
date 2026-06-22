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
- Semantic x/y guide fixture with explicit x ticks, deterministic auto y ticks, labels, grid intent,
  and panel title.
- Guide query fixture coverage for tick hits, misses, and unsupported provider status.
- Local tiled-source fixture with static manifest linkage, clipped viewport mosaic materialization,
  Matplotlib reference rendering, and typed tiled-image query payload.
- In-process replay harness that returns semantic point/image, guide, and tiled-source results.
- Backend conformance matrix with Matplotlib pass and Datoviz clean-skip expectations.
- Minimal debug-json report over semantic replay results, with array transport omitted.
- Deterministic `tools/conformance_debug_report.py` diagnostic report output.

## Reference Backend

Matplotlib is the reference/conformance backend for this baseline. Tests inspect Matplotlib artists and deterministic CPU query results. Datoviz v0.4 remains the flagship GPU backend target, but Datoviz conformance is not required until its adapter slice exists.

## Not Covered Yet

- Datoviz rendering or query execution.
- Datoviz conformance pass requirements.
- VisPy2 producer API.
- Production transport encodings.
- JSON/base64 replay fixtures.
- Versioned JSON schema authority.
- General `data` / `guides` / `all-rendered` query-scope precedence.

## Diagnostic Report

`tools/conformance_debug_report.py` prints deterministic, sorted debug JSON for inspection and CI
diagnostics. It is explicitly non-authoritative: consumers must not treat it as the versioned
fixture schema or as an array transport contract.
