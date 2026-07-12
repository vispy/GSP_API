# VisPy2 RC1 acceptance matrix

Status: evidence baseline for S051; not a public execution API.

The S051 acceptance matrix is authored exclusively through the experimental public `vispy2`
producer calls. A private adapter retains the emitted GSP records and NumPy arrays in process and
passes equivalent scene records to the Matplotlib and Datoviz QA adapters. Debug JSON plus NPZ
sidecars are replay evidence only.

| Case | Public producer coverage | Intended boundary |
|---|---|---|
| `vispy2/primitives` | scatter, markers, segments, plot, View2D, guides | representative 2D families |
| `vispy2/scalar_image_colorbar` | imshow, scalar color scale, colorbar | known guide/colorbar boundary |
| `vispy2/text` | text | adaptation and native-lifecycle boundary |
| `vispy2/mesh` | untextured indexed mesh | retained mesh path |
| `vispy2/texture2d_boundary` | texture and per-vertex UV mesh | explicitly unsupported until independent evidence |

Acceptance outcomes use `strict`, `adapted`, `deactivated`, `unsupported`, or `backend_failure`.
Every non-strict result must have a diagnostic code; record IDs are preserved in the manifest.
This matrix does not add `open_session()`, public backend selection, `Display`, or a public Datoviz
execution method, and it does not promote renderer capabilities.
