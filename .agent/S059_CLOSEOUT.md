# S059 closeout - Texture2D nearest-or-linear filtering

Date: 2026-07-22

S059 extends the bounded Texture2D-unlit mesh contract with visual-owned nearest-or-linear
filtering while preserving every existing nearest payload and capability guarantee.

## Outcome

- `TextureFilter` has `nearest` and `linear` values; `MeshVisual.texture_filter` is an appended
  nearest-default field and canonical nearest records omit it.
- Linear sampling uses the accepted base-level, clamp-to-edge, no-mipmap, unmanaged numeric,
  straight-alpha bilinear rule. Base RGBA multiplication follows sampling.
- VisPy2 exposes only the keyword-only `texture_filter` producer argument and advertises its
  producer capability independently from renderer support.
- Datoviz maps the selected value to both minification and magnification on the mesh `"texture"`
  field slot and advertises `meshvisual.texture_filter.linear.v1` separately from the original
  nearest material capability.
- Matplotlib continues to reject all textured meshes explicitly.

## Native evidence

The repeatable checkpoint used local Datoviz
`be7f2a80354c25e85bab88c85f5ea7340975b569` (`v0.4.0rc2-15-gbe7f2a803`). It rendered all five
nearest regression cases and all four new linear cases. Eight capture probes cover texel centers,
V orientation, clamp, bilinear interpolation, minification, magnification, straight-alpha/base-RGBA
multiplication, and one texture referenced by visuals with distinct filters. Every channel matched
the CPU reference exactly: 0/255 maximum error versus the accepted 2/255 tolerance.

Evidence is recorded under
`artifacts/visual_qa/s059/m252-checkpoint-be7f2a803/`; the checkpoint's focused suite passed 241
tests.

## Repository validation

- full pytest with coverage: 680 passed, 2 skipped, 66% aggregate coverage;
- strict mypy: clean across 221 source files;
- Ruff: clean;
- Matplotlib and exact local-source Datoviz imports: clean;
- specification traceability, profile consistency, public-doc consistency, and strict MkDocs: clean;
- the current-protocol nearest/linear Datoviz example passes capability inspection.

## Deferred scope

Sampler resources, resource-owned filter state, wrap modes other than clamp-to-edge, independent
min/mag controls, mipmaps, anisotropy, LOD controls, color management, and Matplotlib textured-mesh
rendering remain outside GSP 0.2. No release, tag, push, or publication operation was performed.
