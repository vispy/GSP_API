# Feature matrix

This page is generated from the versioned implementation profiles in `profiles/`. Statuses
describe only the stated scope; runtime capability discovery remains authoritative for a
specific process, binding, and device.

| Implementation | Feature | Status | Exact scope | Limitations |
|---|---|---|---|---|
| `gsp_vispy2@0.2` | `visual.primitives2d` | **strict** | point, marker, segment, path, image and text record production | — |
| `gsp_vispy2@0.2` | `visual.mesh` | **strict** | accepted indexed mesh, color, flat Lambert and Texture2D record production | — |
| `gsp_vispy2@0.2` | `guide.semantic` | **strict** | axes, ticks, labels, title, grid and colorbar intent | — |
| `gsp_vispy2@0.2` | `view2d` | **strict** | ranges, reversed ranges and affine transform bindings | — |
| `gsp_vispy2@0.2` | `view3d` | **partial** | producer records used by bounded review examples | general public session execution is separate |
| `gsp_vispy2@0.2` | `execution.matplotlib` | **adapted** | transitional render_matplotlib/show/savefig conveniences | tuple return is transitional; bare Figure.show remains Matplotlib-specific |
| `gsp_vispy2@0.2` | `execution.datoviz` | **partial** | experimental explicit open_session, inspection, bounded blocking display, one-frame polling and owned cleanup | no implicit sessions, retained updates, close callbacks or embedding guarantee |
| `gsp.matplotlib@0.2` | `visual.point` | **strict** | finite 2D DATA/NDC points, RGBA, logical-pixel diameters | — |
| `gsp.matplotlib@0.2` | `visual.marker` | **strict** | accepted 2D marker shapes, fill, angle, stroke | — |
| `gsp.matplotlib@0.2` | `visual.segment` | **strict** | accepted 2D independent segments | — |
| `gsp.matplotlib@0.2` | `visual.path` | **strict** | accepted 2D subpaths, widths, caps, joins | — |
| `gsp.matplotlib@0.2` | `visual.image` | **strict** | RGBA/scalar 2D images with accepted origin and interpolation | — |
| `gsp.matplotlib@0.2` | `visual.text` | **strict** | accepted TextVisual layout roles and item query identity | — |
| `gsp.matplotlib@0.2` | `visual.mesh2d` | **strict** | accepted 2D triangle mesh uniform/per-face RGBA | — |
| `gsp.matplotlib@0.2` | `guide.axis-layout` | **partial** | native axes, deterministic GSP ticks, labels, grid and partial resolved layout | layout_strict remains unadvertised; colorbar query unsupported |
| `gsp.matplotlib@0.2` | `view2d.navigation` | **strict** | canonical client-side pan/zoom/set/reset reference behavior | — |
| `gsp.matplotlib@0.2` | `view3d.mesh` | **adapted** | canonical CPU projection and 2D raster reference | not strict GPU clipping or fragment depth |
| `gsp.matplotlib@0.2` | `mesh.flat-lambert` | **adapted** | strict canonical face-color resolution with adapted 3D raster | — |
| `gsp.matplotlib@0.2` | `mesh.texture2d-unlit` | **unsupported** | protocol accepted; renderer rejects explicitly | no textured mesh renderer |
| `gsp.matplotlib@0.2` | `query.panel-data` | **partial** | point, image, text, 2D mesh, transforms and bounded View3D reference payloads | payload and scope capabilities remain independent |
| `gsp.matplotlib@0.2` | `output.publication` | **strict** | PNG, SVG and PDF reference output | — |
| `gsp.datoviz-v0.4@0.2` | `visual.point` | **strict** | proven retained point scopes | — |
| `gsp.datoviz-v0.4@0.2` | `visual.marker` | **partial** | proven shapes/style combinations only | support depends on active public binding symbols |
| `gsp.datoviz-v0.4@0.2` | `visual.segment` | **strict** | proven segment width/cap scopes | — |
| `gsp.datoviz-v0.4@0.2` | `visual.path` | **strict** | proven retained subpath scopes | — |
| `gsp.datoviz-v0.4@0.2` | `visual.image` | **partial** | RGBA and bounded scalar-image paths | image texel/color/value query parity unadvertised |
| `gsp.datoviz-v0.4@0.2` | `visual.text` | **adapted** | isolated proven text rows | combined/offscreen and advanced layout behavior remains feature-specific |
| `gsp.datoviz-v0.4@0.2` | `visual.mesh2d` | **adapted** | bounded triangle mesh paths; per-face color may expand vertices | — |
| `gsp.datoviz-v0.4@0.2` | `guide.axis-layout` | **partial** | native axes and partial panel-frame layout when complete bindings are available | full guide/all-rendered query and strict layout not advertised |
| `gsp.datoviz-v0.4@0.2` | `view2d.navigation` | **strict** | retained programmatic View2D updates and proven live bounded lifecycle | — |
| `gsp.datoviz-v0.4@0.2` | `view3d.mesh` | **partial** | retained DATA-space opaque meshes for advertised projection/depth combinations | mesh triangle identity query not advertised |
| `gsp.datoviz-v0.4@0.2` | `mesh.flat-lambert` | **strict** | CPU-resolved exact per-face Lambert colors on the proven retained path | — |
| `gsp.datoviz-v0.4@0.2` | `mesh.texture2d-unlit` | **blocked** | public API feasibility only | sampler, origin, unmanaged RGBA, multiplication and stability evidence incomplete |
| `gsp.datoviz-v0.4@0.2` | `query.panel-data` | **partial** | panel query and live point identity | scientific readback, hit_policy=all, image texel/value and mesh triangle picking unadvertised |
| `gsp.datoviz-v0.4@0.2` | `output.png` | **partial** | isolated offscreen/live PNG capture when advertised by active binding | capture is not scientific readback |

## Status meanings

- **strict**: the stated scope implements the normative contract without a semantic adapter.
- **adapted**: the outcome is conforming within scope, but an explicit adaptation is involved.
- **partial**: only the written subset is implemented; inspect limitations and runtime capabilities.
- **unsupported**: the implementation rejects the feature explicitly.
- **blocked**: implementation or promotion awaits named evidence; it is not a capability claim.
- **not-assessed**: no conformance claim has been made.

See the [backend profile interpretation rules](../specification/backend-profiles.md) and
[capability contract](../specification/capabilities.md).
