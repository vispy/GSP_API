# Python API

The current recommended Python surface is `gsp.protocol`. It contains validated records and helpers
for capabilities, commands, transports, panels, views, visuals, resources, guides, navigation,
layout, queries, extensions, and diagnostics.

## Start with these types

| Task | Types |
|---|---|
| Session contract | `InProcessGSPServer`, `InProcessTransport`, `InitializeResult`, `CommandResult` |
| Commands | `ProtocolCommand`, `CommandKind`, `CommandBatch` |
| Capability discovery | `CapabilitySnapshot`, `AdaptationDecision`, `AdaptationOutcome` |
| 2D scenes | `Panel`, `View2D`, `PointVisual`, `ImageVisual`, `AxisGuide` |
| 3D scenes | `View3D`, `Camera3D`, `MeshVisual`, projection records |
| Queries | `QueryRequest`, `QueryResult`, typed query payloads |

The generated module dumps from the older website mixed protocol and legacy implementation APIs and
are no longer part of the recommended navigation. The `gsp.core`, `gsp.visuals`, `RendererBase`, and
registry-based renderer surfaces remain compatibility material.

The package exports these records from `gsp.protocol`; applications should not import protocol
implementation modules by filesystem location.
