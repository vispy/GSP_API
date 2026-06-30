# S039 Next Stage Scoping

S039 opens after completed S038 MeshVisual unlit RGBA material boundary.

## Direction

Evaluate Lambert-with-normals as the next narrow material expansion. This stage is architecture/spec
first and must not implement public normal or lighting behavior before P024 is accepted.

## Mission Stack

| Mission | State | Summary |
|---|---|---|
| M170 | completed | Create S039 scoping and P024 consultation packet. |
| M171 | blocked | Convert P024 response into ADR/spec baseline before implementation. |

## Stop Conditions

- Do not include texture/UV/sampler work in S039.
- Do not expose backend-native material, shader, or draw-state names.
- Do not launch implementation workers until M171 completes.
