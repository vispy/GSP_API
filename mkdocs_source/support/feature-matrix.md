# Feature matrix

This is a reader-oriented summary, not a substitute for runtime capability discovery.

| Feature family | Protocol | VisPy2 producer | Matplotlib | Datoviz v0.4 |
|---|---|---|---|---|
| Points, markers, segments, paths | Accepted | Available | Reference | Capability-gated; substantial strict scopes |
| Images and scalar color | Accepted | Available | Reference | Partial; exact scope depends on image and color capabilities |
| Text | Accepted | Available | Reference | Partial/adapted; some combined offscreen cases are crash-isolated |
| Axes, grid, titles, colorbars | Accepted | Available | Reference | Feature-specific; do not assume guide query parity |
| View2D transforms/navigation | Accepted | Available | Reference | Capability-gated retained paths |
| View3D and opaque meshes | Accepted bounded scope | Available | Adapted reference rendering | Capability-gated retained GPU paths |
| Flat Lambert mesh shading | Accepted bounded scope | Available | Reference color resolution with adapted 3D raster | Strict only for proven Datoviz scope |
| Texture2D mesh material | Accepted | Available | Unsupported | Blocked from renderer promotion |
| Panel and visual queries | Accepted payload families | Producer coverage varies | Reference scopes | Independent, feature-specific capabilities |
| Production remote transport | Architectural target | Not applicable | Not available | Not available |

For interpretation rules and backend limitations, continue with the local
[backend profiles](../specification/backend-profiles.md) and
[capabilities specification](../specification/capabilities.md).
