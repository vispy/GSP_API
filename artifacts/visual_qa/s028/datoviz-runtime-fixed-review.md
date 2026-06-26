# S028 Datoviz Runtime-Fixed Visual QA Review

Status: local evidence generated after explicitly configuring the sibling Datoviz v0.4-dev runtime.

## Runtime Environment

The Datoviz runtime did not render through the GSP visual QA harness until the v0.4-dev checkout and
bundled MoltenVK ICD were made explicit:

```sh
DATOVIZ_REPO=/Users/cyrille/GIT/Viz/datoviz \
tools/run_datoviz_visual_qa.sh \
  --suite s028 \
  --backends matplotlib,datoviz \
  --out artifacts/visual_qa/s028/datoviz-runtime-fixed-full \
  --run-id s028-dataviz-runtime-fixed-full \
  --contact-sheet \
  --resolution 800x600
```

The wrapper sets:

```sh
GSP_DATOVIZ_QA_ENABLE_OFFSCREEN=1
PYTHONPATH=/Users/cyrille/GIT/Viz/datoviz
DYLD_LIBRARY_PATH=/Users/cyrille/GIT/Viz/datoviz/libs/vulkan/macos_arm64
VK_ICD_FILENAMES=/Users/cyrille/GIT/Viz/datoviz/libs/vulkan/macos_arm64/MoltenVK_icd.json
```

The QA default is now `--datoviz-color-pipeline linear_srgb`. The local v0.4-dev facade does not
expose `dvz_figure_set_color_pipeline`, so `legacy_srgb_blend` is not available unless Datoviz adds
that symbol.

Datoviz emits `validation layer is not supported` warnings in this environment, but the render path
continues when the ICD path is configured.

## Generated Runs

| Run | Purpose | Summary |
|---|---|---|
| `datoviz-runtime-fixed-full` | Full S028 suite with fixed Datoviz runtime env | Datoviz rendered point, marker, segment, and path; remaining cases returned structured unsupported diagnostics. |

## Current Visual-Family Evidence

| Family / feature | Matplotlib | Datoviz runtime | Current GSP Datoviz status |
|---|---|---|---|
| Point | rendered | rendered | Reviewable now. |
| Marker | rendered | rendered | Reviewable now for core RGBA marker cases. |
| Segment | rendered | rendered | Reviewable now. |
| Path | rendered | rendered | Reviewable now. |
| Image | rendered | unsupported | Blocked by missing `dvz_image_set_sampling`; all current image QA cases request nearest sampling. |
| Overlay point over image | rendered | unsupported | Blocked by image sampling. |
| Text | rendered | unsupported | Adapter gate: text placement, anchors, font-size, rotation, and font-role semantics unverified. |
| Mesh 2D | rendered | unsupported | Adapter gate: flat RGBA, per-face color, 2D z=0 mapping, topology, and face query semantics unverified. |
| Colorbar | rendered | unsupported | Adapter does not pass QA color scales/guides into Datoviz renderer yet; native colorbar contract remains unverified. |
| Guides/View2D | rendered | unsupported | Adapter QA path does not render Datoviz guides; DATA point case also hits NDC-only point gate. |
| True 3D | not strict | not attempted | Public 3D camera/projection/controller semantics remain deferred pending P013. |

## Artifact Entry Points

- Full S028 review sheet:
  `artifacts/visual_qa/s028/datoviz-runtime-fixed-full/contact_sheets/s028_all_cases.png`
- Run summary:
  `artifacts/visual_qa/s028/datoviz-runtime-fixed-full/summary.md`
- Machine-readable report:
  `artifacts/visual_qa/s028/datoviz-runtime-fixed-full/report.json`

## Immediate Follow-ups

1. Keep the runtime env vars above in any Datoviz visual QA command on macOS.
2. Add or expose `dvz_image_set_sampling` in the Datoviz facade, or add a GSP adapter policy for
   knowingly adapted linear image sampling.
3. After P013 returns, decide whether text, mesh, colorbar, and guide rendering should be promoted
   through focused GSP adapter missions or remain documented as unsupported until Datoviz-side
   contracts land.
