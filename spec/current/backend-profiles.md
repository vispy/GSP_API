# Backend profiles

Backend profiles report implementation support; they do not redefine protocol semantics.

## Matplotlib

Matplotlib is the reference and publication backend for accepted 2D semantics, scalar color behavior, guides, layout, and many query paths. Its 3D mesh path is an adapted reference raster implementation where exact GPU clipping, depth, or interaction equivalence is not established.

Texture2D mesh rendering is unsupported and must produce an explicit diagnostic rather than a flat-color substitute.

## Datoviz v0.4

Datoviz is the flagship retained GPU target. Support is advertised per capability and exact feature combination. Current evidence includes substantial point, marker, segment, path, image, transform, retained View2D, View3D mesh, opaque depth, bounded flat-Lambert, and bounded Texture2D-unlit scopes.

The Texture2D path requires the post-RC2 field-slot sampling API and advertises support only when the generated binding exposes it. The existing material capability guarantees nearest/clamp/no-mipmap sampling. S059 adds visual-owned linear filtering through a separate capability, promoted after the Datoviz `be7f2a803` checkpoint rendered 9/9 cases and matched all eight numeric probes exactly.

Important limitations include feature-specific adapted text and guide behavior, independent query coverage, and crash-isolated offscreen cases. A successful image capture does not establish query or layout strictness.

## Legacy implementations

The older Datoviz v0.3 renderer, `RendererBase` object API, environment-variable backend selection, and Flask network renderer are compatibility material. They are not current backend or transport profiles.

## Runtime authority

This documentation summarizes known evidence. The active session's capability snapshot remains authoritative for an installed backend build.
