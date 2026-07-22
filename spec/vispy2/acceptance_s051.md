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
| `vispy2/texture2d_boundary` | texture and per-vertex UV mesh | capability-gated Datoviz nearest/clamp/no-mipmap rendering; Matplotlib remains explicitly unsupported |

Acceptance outcomes use `strict`, `adapted`, `deactivated`, `unsupported`, or `backend_failure`.
Every non-strict result must have a diagnostic code; record IDs are preserved in the manifest.
This matrix does not add `open_session()`, public backend selection, `Display`, or a public Datoviz
execution method, and it does not promote renderer capabilities.

## S052 preflight correction

S052 established that the three original Datoviz backend failures shared an incomplete generated
panel-frame ctypes binding, triggered by default VisPy2 axis guides during partial layout snapshot
readback. Readiness now rejects zero-size generated records before native execution. The refreshed
matrix renders primitives, text, and untextured mesh as adapted, with zero native crashes, while
colorbar and Texture2D boundaries remained unsupported at that checkpoint. Fifteen isolated
create/capture/report/close cycles completed cleanly. This evidence remains internal and does not
publish the session API.

## Post-RC2 Texture2D follow-up

Datoviz `v0.4-dev` commit `be7f2a80354c25e85bab88c85f5ea7340975b569` adds public field-slot
sampling controls. The GSP adapter now advertises `meshvisual.material.texture2d_unlit.v1` only
when those generated bindings are present and lowers the accepted producer record to RGBA8
linear-color upload, per-vertex UVs, nearest min/mag filtering, clamp/no-mipmap defaults, and the
unlit material model. The S050 review pack renders all five Texture2D cases without a Datoviz crash
or unsupported result.

This promotion does not change the S051 producer schema and does not add linear filtering to GSP.
Datoviz supports linear field-slot sampling, but the public GSP S050 contract remains fixed to
nearest while P036 is under consultation. Matplotlib continues to reject Texture2D meshes with the
structured unsupported diagnostic.
