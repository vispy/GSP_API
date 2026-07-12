# Queries and readback

## Panel-query model

A query asks what semantic or rendered contribution exists at a panel coordinate. The request declares panel, coordinate space, scope, hit policy, and desired payloads.

Scopes distinguish data visuals, guides, and all rendered contributions. A backend may support one scope without supporting another.

## Result states

| Status | Meaning |
|---|---|
| Hit | A supported contribution satisfies the request. |
| Miss | The request was valid and supported, but no contribution matched. |
| Outside panel | The coordinate is outside the target region. |
| Unsupported | Required scope, policy, or payload capability is unavailable. |
| Stale | The request references an obsolete scene, view, or layout snapshot. |
| Invalid | The request itself violates the contract. |

Unsupported, stale, and invalid states must not be encoded as misses.

## Payloads

Common payloads include visual identity, item or primitive index, visual/data/UV coordinates, displayed RGBA, scalar source and normalized values, depth/order, guide identity, and optional extension data. Only requested and supported fields may be returned.

Mesh-triangle picking is limited to advertised opaque DATA-space triangle scopes. Geometry payloads may add barycentric coordinates, data-space hit position, panel-NDC depth, and projected facing. Base identity-only payloads remain valid independently.

## Coherence

Queries that depend on view, projection, resource, or resolved-layout state carry the relevant snapshot identity. Implementations must reject stale queries rather than combining state from different frames.
