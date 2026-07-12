# Backend profiles

Backend profiles report implementation support; they do not redefine protocol semantics.

## Matplotlib

Matplotlib is the reference and publication backend for accepted 2D semantics, scalar color behavior, guides, layout, and many query paths. Its 3D mesh path is an adapted reference raster implementation where exact GPU clipping, depth, or interaction equivalence is not established.

Texture2D mesh rendering is unsupported and must produce an explicit diagnostic rather than a flat-color substitute.

## Datoviz v0.4

Datoviz is the flagship retained GPU target. Support is advertised per capability and exact feature combination. Current evidence includes substantial point, marker, segment, path, image, transform, retained View2D, View3D mesh, opaque depth, and bounded flat-Lambert scopes.

Important limitations include feature-specific adapted text and guide behavior, independent query coverage, crash-isolated offscreen cases, and blocked Texture2D mesh renderer promotion. A successful image capture does not establish query or layout strictness.

## Legacy implementations

The older Datoviz v0.3 renderer, `RendererBase` object API, environment-variable backend selection, and Flask network renderer are compatibility material. They are not current backend or transport profiles.

## Runtime authority

This documentation summarizes known evidence. The active session's capability snapshot remains authoritative for an installed backend build.
