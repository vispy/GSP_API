# S050 Datoviz Texture2D public API feasibility

Date: 2026-07-04

Mission: M220 - S050 Datoviz Texture2D public API feasibility

## Decision

Datoviz v0.4-dev has a plausible public API path for textured meshes, but GSP must not advertise
`meshvisual.material.texture2d_unlit.v1` from the current evidence alone.

Strict S050 support is blocked by missing public proof for mesh sampler semantics, texture-origin
semantics, and unmanaged numeric RGBA behavior. If runtime fixtures prove the current mesh shader
already uses nearest/clamp/no-mipmap sampling, S050-compatible origin handling, and no implicit color
conversion, the existing public symbols are likely enough for a gated implementation. If not,
upstream Datoviz API work is required to expose mesh texture sampler and color-role controls.

No GSP semantic question blocks this audit; the accepted S050 contract is specific enough.

## Evidence Source

GSP checkout:

- path: `/Users/cyrille/GIT/Viz/GSP_API`
- branch: `agentic-gsp-vispy2`

Datoviz checkout inspected read-only:

- path: `/Users/cyrille/GIT/Viz/datoviz`
- branch: `v0.4-dev`
- commit: `5d865b45d`

The sibling Datoviz worktree had unrelated local state (`m data`, `?? paper/paper.pdf`). No sibling
files were edited.

Runtime binding import used:

```text
/Users/cyrille/GIT/Viz/datoviz/datoviz/__init__.py
```

## Public Symbols Present

The active v0.4-dev generated Python binding exposes the required candidate symbols:

| Requirement | Public symbol | Evidence |
|---|---|---|
| Mesh visual constructor | `dvz_mesh` | present in runtime binding and `include/datoviz/scene.h` |
| Mesh positions/colors | `dvz_visual_set_data(..., "position" / "color", ...)` | present; header documents mesh attributes |
| Mesh indices | `dvz_visual_set_index_data` | present in runtime binding |
| Per-vertex UV upload | `dvz_visual_set_data(..., "texcoords", ...)` | header documents optional mesh `"texcoords"` as `vec2f` |
| RGBA8 texture convenience upload | `dvz_visual_set_texture_rgba8` | present; header accepts image/glyph/mesh visuals |
| Explicit sampled-field binding | `dvz_visual_set_field(..., "texture", field)` | present; docstring says mesh visuals accept `"texture"` |
| Sampled-field descriptor | `dvz_sampled_field_desc`, `DvzSampledFieldDesc` | present |
| Sampled-field upload | `dvz_sampled_field`, `dvz_field_data_view`, `dvz_sampled_field_set_data` | present |
| RGBA8 format constant | `DVZ_FIELD_FORMAT_RGBA8_UNORM` | present |
| 2D field constant | `DVZ_FIELD_DIM_2D` | present |
| Color semantic constant | `DVZ_FIELD_SEMANTIC_COLOR` | present |
| Color role constants | `DVZ_COLOR_ROLE_SRGB_COLOR`, `DVZ_COLOR_ROLE_DATA` | present |

Header evidence from `/Users/cyrille/GIT/Viz/datoviz/include/datoviz/scene.h`:

- the `dvz_visual_set_data()` attribute table lists mesh `"position"`, optional `"color"`,
  optional `"normal"`, optional `"texcoords"`, and optional `"instance_transform"`;
- the `dvz_mesh()` documentation says binding an RGBA8 2D sampled field to the `"texture"` slot
  enables the first retained textured-mesh shader path;
- the `dvz_visual_set_field()` generated docstring says mesh visuals accept the `"texture"` slot
  for a first-slice RGBA8 2D texture;
- `dvz_visual_set_texture_rgba8()` documents image, glyph, or mesh visuals and binds mesh textures
  to `"texture"`.

## Runtime Snapshot

The default sampled-field descriptor returned by `dvz_sampled_field_desc()` was:

```text
dim=0
format=22
semantic=4
color_role=1
width=0
height=0
depth=1
```

In the generated binding these correspond to:

- `DVZ_FIELD_DIM_2D = 0`;
- `DVZ_FIELD_FORMAT_RGBA8_UNORM = 22`;
- `DVZ_FIELD_SEMANTIC_COLOR = 4`;
- `DVZ_COLOR_ROLE_SRGB_COLOR = 1`.

`DvzSampledFieldDesc` exposes only `flags`, `dim`, `format`, `semantic`, `color_role`, `width`,
`height`, and `depth`; it has no public sampler fields.

## S050 Requirement Matrix

| S050 requirement | Current Datoviz public API status | Strict status |
|---|---|---|
| Immutable RGBA8 texture resource upload | `dvz_visual_set_texture_rgba8()` or sampled field with `RGBA8_UNORM` can upload tightly packed row-major RGBA8 bytes. | Feasible. |
| Per-vertex UVs indexed by mesh faces | Mesh `"texcoords"` attribute is public; indexed mesh upload is already part of the GSP Datoviz mesh path. | Feasible. |
| Bind texture to mesh material | Mesh `"texture"` sampled-field slot is public. | Feasible. |
| Nearest min/mag sampling | `dvz_image_set_sampling()` documents nearest sampling for image visuals only; no mesh-equivalent public setter or descriptor field was found. | Blocked pending runtime proof or upstream API/docs. |
| Clamp-to-edge in `u` and `v` | Sampler address-mode APIs exist at lower levels, but no public retained mesh texture sampler control was found. | Blocked pending runtime proof or upstream API/docs. |
| No mipmaps / base LOD only | No public retained mesh texture LOD/mipmap control or guarantee was found. | Blocked pending runtime proof or upstream API/docs. |
| `image[0]` is top row and high `v` samples top texels | Upload docs say row-major; mesh texture origin behavior is not specified. | Blocked pending runtime proof. |
| Unmanaged numeric RGBA | Convenience wrapper and default descriptor use `DVZ_COLOR_ROLE_SRGB_COLOR`; S050 forbids implicit sRGB/color-profile conversion. | Blocked pending runtime proof or a public numeric color role path. |
| Multiplicative unlit output | Mesh shader path is public, but docs do not specify exact `base * tex` output or absence of native lighting/material tint. | Blocked pending runtime proof. |

## Candidate Implementation Shape

A candidate GSP Datoviz implementation would use only public retained-scene APIs:

1. validate `Texture2D` resources through the protocol path;
2. create `dvz_mesh(scene, 0)`;
3. upload positions, colors, indices, and `MeshVisual.uvs` as `"texcoords"`;
4. create an RGBA8 2D sampled field with `DVZ_FIELD_FORMAT_RGBA8_UNORM`;
5. upload row-major `uint8 (H,W,4)` bytes through `dvz_sampled_field_set_data()`;
6. bind the field to the mesh with `dvz_visual_set_field(mesh, "texture", field)`;
7. render only under structured capability gates until fixture evidence proves the remaining S050
   requirements.

The shortcut `dvz_visual_set_texture_rgba8()` is also public, but it hardcodes
`DVZ_COLOR_ROLE_SRGB_COLOR`, so the explicit sampled-field path is preferable for any future proof.

## Blockers Before Promotion

Do not promote `texture2d.rgba8.v1`, `meshvisual.uv.vertex2d.v1`, or
`meshvisual.material.texture2d_unlit.v1` for Datoviz until all of these are true:

- runtime S050 fixture evidence proves nearest sampling on mesh textures;
- runtime fixture evidence proves clamp-to-edge behavior for out-of-range UVs;
- runtime or public API evidence proves no mipmaps or LOD-dependent sampling;
- runtime UV-orientation fixture proves the S050 top-row/high-v contract or the GSP adapter applies
  a documented UV/image adaptation before upload;
- runtime color-multiplication fixture proves exact unmanaged byte-normalized RGB and alpha
  multiplication without sRGB conversion, gamma conversion, or hidden lighting/material tint;
- opaque View3D textured fixture passes only on the retained DATA-space View3D path and only with
  strict alpha.

## Required Upstream Work If Fixtures Fail

If the current mesh shader defaults fail any strict fixture, Datoviz needs public retained-scene API
support for at least:

- mesh texture sampler selection or documented fixed nearest/clamp/no-mipmap semantics;
- a numeric RGBA color-role path suitable for unmanaged byte-normalized sampling;
- public documentation of mesh texture origin and shader color equation.

Private Vulkan samplers, shader slots, mesh ids, and native texture handles remain outside the GSP
implementation boundary.

## Validation

Commands run:

```bash
uv run python - <<'PY'
import sys
sys.path.insert(0, '/Users/cyrille/GIT/Viz/datoviz')
import datoviz as dvz
...
PY
```

Result: public candidate symbols were present and `dvz_sampled_field_desc()` returned the default
RGBA8/color descriptor described above.

No renderer code was changed and no Datoviz texture capability was advertised in this mission.
