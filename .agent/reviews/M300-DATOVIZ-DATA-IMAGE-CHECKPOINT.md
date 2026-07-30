# M300 Datoviz DATA-space image checkpoint

Date: 2026-07-30

## Decision

The existing public Datoviz v0.4 retained scene API is sufficient for GSP DATA-space images. No Datoviz source or public API change was required, and no ChatGPT Pro consultation was triggered.

GSP now lowers `ImageVisual` through the visual's declared DATA or NDC attachment coordinate instead of rejecting DATA images and forcing all accepted images into view space. VisPy2 adds a maintained `scalar-image` paired-review case with a public DATA-space `imshow()`, linked color scale and colorbar, and three overlay registration points.

Final paired live human acceptance remains pending a machine reboot because the owner reported that the GPU driver became unavailable after the native evidence below had completed. Do not run further Vulkan/Datoviz native gates until after that reboot.

## Source checkpoint

- GSP baseline: `767d09e2869bb7b72932c5e9cceb7f481d6f81bf`
- GSP implementation: `378ec88`
- VisPy2 baseline: `4f0f0be0f4efadb5275223282a6e771693d7fb73`
- VisPy2 implementation and review path: `2d02c1b`
- Datoviz used for the initial native proof: `4c4f73f6c`
- Datoviz remained read-only; unrelated documentation-generator changes were not touched.

## Native evidence completed before the GPU-driver pause

| Evidence | Result | SHA-256 |
|---|---|---|
| Native Datoviz scalar sampled-field image using the default DATA attachment and pan/zoom path | 1280×720 non-blank capture | `f45483eb87238214870dc9e2c95637f29c6b339505d2993de124c97e4d5047a0` |
| Public VisPy2 DATA `imshow()` through GSP Datoviz with viridis mapping and native colorbar | 800×600 non-blank capture | `53718bef993ae76fead51b9a27f0bc5a96b064ea0c18f3832f01e2d81b500ef5` |
| Initial discrete image plus corner/origin registration points | visually registered | `8b3bd9ba6b97cea0c8b7d643caa3fd9740e43b8b8ebaed3028544652be0fbf41` |
| Retained View2D zoom | image and origin point remained registered | `5db180a207f81452dc28ac81c99c99a1b983320e3d79551ef72d95d3823b9f5b` |
| Retained reversed-x View2D | image and numeric axis reversed coherently | `8002991915f345a6c36e69f4e30b07fe103f03f60e3d6a25327065bfe8098398` |
| Isolated Datoviz paired-runner child | one bounded frame and clean close | passed |
| Matplotlib paired-runner child | headless reference path completed | passed |

The captures were temporary current-runtime evidence outside all repositories; they are not release artifacts.

## CPU-safe validation after the GPU-driver pause

| Gate | Result |
|---|---|
| GSP focused Datoviz renderer tests | 255 passed |
| GSP complete source tests | 804 passed |
| GSP strict mypy | 51 source files clean |
| VisPy2 maintained comparison tests | 18 passed |
| VisPy2 source tests excluding one unrelated Matplotlib raster-area baseline | 123 passed, 1 deselected |
| VisPy2 strict mypy | 3 source files clean |
| Changed VisPy2 Ruff gate | passed after import normalization; two pre-existing `TRY004` findings excluded |
| Documentation validation | 30 Python blocks and 64 local links passed |
| Strict MkDocs build | passed; existing checkout-relative informational links remained non-site-local |
| Wheel build | `gsp-core`, `gsp-matplotlib`, `gsp-datoviz`, and `vispy2` built |
| Isolated wheel install and public semantic construction | passed from `site-packages` |
| Diff whitespace validation | passed |

Repository-wide Ruff is not a usable clean baseline at these heads: it reports unrelated pre-existing findings outside M300. The full VisPy2 source suite also has one unrelated Matplotlib 3.11 raster-area threshold failure (`10,000` required versus `8,874` observed for one face tone); M300 does not change that gallery or the Matplotlib renderer.

## Required post-reboot closeout

1. Confirm the Datoviz source commit and rebuild/reselect the qualified binding if it changed.
2. Run `examples/manual_live_compare.py scalar-image` from the exact candidate wheels.
3. Inspect lower-origin orientation, DATA extent, nearest cells, the three red registration points, colorbar ticks, resize, and interactive pan/zoom.
4. Close both windows and confirm the Datoviz child exits without a crash or hang.
5. If accepted, promote the capability-matrix row from candidate strict to strict, resolve Q200, and complete M300.
