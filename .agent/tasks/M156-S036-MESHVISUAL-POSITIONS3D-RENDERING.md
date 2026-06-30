# M156 - S036 MeshVisual `(N, 3)` DATA/NDC rendering path

Make `(N, 3)` `MeshVisual` renderable through static `View3D` where capabilities are advertised.

## Deliverables

- DATA and NDC interpretation rules.
- Structured unsupported diagnostics.
- Datoviz retained rendering path or exact unsupported evidence.
- Regression coverage for unchanged `(N, 2)` mesh behavior.

## Stop Condition

Stop if support would silently flatten z or expose Datoviz-native draw/camera state publicly.

