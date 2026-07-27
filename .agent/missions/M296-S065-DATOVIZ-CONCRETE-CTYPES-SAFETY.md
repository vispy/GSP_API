# M296 - S065 Datoviz concrete ctypes record safety

## Status

Completed and independently accepted. Datoviz commit `b45d692e4` generates ABI-exact layouts for the supported records, records explicit provenance for safe pointer-opaque records, omits exactly 43 unsafe functions, and validates cleanly on Python 3.12 and 3.14 without a crash.

## Baseline and defect

- Datoviz baseline is `d8bf64544` in the clean isolated source registered as
  `datoviz-ctypes-fix`.
- M294 fixed the aligned panel View2D/View3D state records, but the generated binding still contains
  22 unconditionally empty, non-opaque concrete records.
- Native functions using caller-allocated pointers to those records remain exposed. A caller can
  therefore allocate a zero-byte ctypes instance and let native code read or write beyond it.
- Intentional opaque handles are not defective and must not be broadly suppressed.

## Required architecture

Replace the M294 conditional-output special case with a policy-validated disposition for every
public concrete record referenced by a generated function or callback:

1. ABI layout, optionally conditional on effective ctypes alignment;
2. explicit safe pointer-opaque provenance for native-owned or callback-borrowed pointers; or
3. explicit unsupported disposition that omits unsafe dependent functions.

Omit a function if a by-value argument/result or caller-supplied input/output/inout pointer targets
an unavailable concrete layout. Native-returned pointers and callback-borrowed pointers may remain
only through explicit policy exceptions. Preserve private/API-opaque handles. Populate
`_UNSUPPORTED_FUNCTIONS` with exact record-specific diagnostics, and keep module import successful.

Do not hand-write ABI mirrors. Use extracted record data, generated ABI evidence, and policy.

## Generate now

Generate and ABI-validate these high-level records:

| Record | Native size/alignment | Runtime policy |
|---|---:|---|
| `DvzBounds` | 56 / 8 | portable |
| `DvzFieldGeometry` | 104 / 8 | portable |
| `DvzGuideHit` | 208 / 8 | portable |
| `DvzGuideLayout` | 208 / 8 | portable |
| `DvzMVP` | 208 / 16 | conditional |
| `DvzPanelFrameInfo` | 4544 / 16 | conditional |
| `DvzPanzoomEval` | 24 / 4 | portable |
| `DvzPanzoomResolved` | 224 / 16 | conditional through `DvzMVP` |
| `DvzVisualTransformDesc` | 112 / 16 | conditional |

Enable the following functions only when every required layout is ready:

- bounds: `dvz_visual_bounds`, `dvz_panel_visual_bounds`, `dvz_panel_bounds`;
- field geometry: `dvz_ffi_field_geometry`, `dvz_sampled_field_set_geometry`,
  `dvz_field_geometry`;
- guides: `dvz_panel_frame_guide_hit`, `dvz_panel_frame_guide_layout`;
- MVP: `dvz_arcball_mvp`, `dvz_camera_mvp`, `dvz_panzoom_mvp`;
- frame: `dvz_panel_frame_info`;
- panzoom: `dvz_panzoom_resolve`;
- visual transform: `dvz_ffi_visual_transform_desc`, `dvz_visual_set_transform_desc`,
  `dvz_visual_transform_desc`.

On runtimes without effective 16-byte ctypes alignment, omit every function dependent on
`DvzMVP`, `DvzPanelFrameInfo`, `DvzPanzoomResolved`, or `DvzVisualTransformDesc`.
`DvzPanzoomEval` remains available as a harmless portable layout.

## Explicit safe pointer-opaque exceptions

Keep these zero-sized Python declarations and their native-owned/borrowed pointer APIs:

- `DvzGeometry`: native-owned pointer returned and consumed by geometry APIs;
- `DvzTessellatedPath`: owned pointer returned by tessellators and passed to destroy;
- `DvzTextAtlasGlyph`: borrowed const return only;
- `DvzVolumeState`: borrowed const return only;
- `DvzWindowSurface`: borrowed pointer returns only;
- `DvzCanvasLiveImageFrame`: borrowed callback payload only.

Preserve sentinel APIs for geometry create/destroy, tessellate/destroy,
`dvz_text_atlas_glyph`, `dvz_volume_state`, `dvz_window_surface`,
`dvz_window_backend_surface`, `DvzCanvasLiveImageCallback`, `DvzCanvasDraw`, and
`dvz_canvas_set_draw_callback`. The policy must not classify these records as safe for
caller allocation.

## Explicit unsupported records and functions

Suppress these exact APIs until their low-level Vulkan/platform layouts are supported:

- `DvzBarriers`: `dvz_barriers`, `dvz_barriers_buffer`, `dvz_barriers_buffer_count`,
  `dvz_barriers_capacity`, `dvz_barriers_dependency_flags`, `dvz_barriers_flags`,
  `dvz_barriers_image`, `dvz_barriers_image_count`, `dvz_barriers_memory`,
  `dvz_barriers_memory_count`, `dvz_cmd_barriers`.
- `DvzDeviceConfig`: `dvz_device_config`, `dvz_device_config_enable_canvas_extensions`,
  `dvz_device_config_request_extension`, `dvz_device_config_request_queue`,
  `dvz_device_config_set_features10`, `dvz_device_config_set_features11`,
  `dvz_device_config_set_features12`, `dvz_device_config_set_features13`,
  `dvz_device_config_set_gpu_index`, `dvz_device_create`.
- `DvzGpuCtxConfig`: `dvz_gpu_ctx_config`, `dvz_canvas_configure_gpu_ctx`, `dvz_gpu_ctx`,
  `dvz_gpu_ctx_config_add_instance_extension`, `dvz_gpu_ctx_config_alloc`,
  `dvz_gpu_ctx_config_enable_canvas_extensions`, `dvz_gpu_ctx_config_features10`,
  `dvz_gpu_ctx_config_features12`, `dvz_gpu_ctx_config_features13`,
  `dvz_gpu_ctx_config_gpu`, `dvz_gpu_ctx_config_validation`.
- `DvzDrp2ColorAttachment` and `DvzDrp2RenderPassDesc`:
  `dvz_drp2_render_pass_desc`, `dvz_drp2_stream_begin_render_pass_desc`.
- `DvzStreamFrame`: `dvz_stream_start`, `dvz_stream_update`,
  `dvz_drp2_runtime_attach_frame_target`, `dvz_drp2_runtime_copy_texture_to_frame`.
- `DvzWindowExternalSurfaceInfo`: `dvz_window_external_surface_info`,
  `dvz_view_external_surface`, `dvz_view_update_external_surface`,
  `dvz_window_wrap_attach_surface`, `dvz_window_wrap_update_surface`.

Preserve the scalar FFI external-surface helpers, including
`dvz_ffi_view_external_surface` and its update counterpart; they do not expose the unsupported
record to the caller.

## Required tests

1. Policy validation fails when any public concrete record used by value, pointer, or callback lacks
   one of the three dispositions. Cover all 22 audited records plus M294's two conditional panel
   state records.
2. Synthetic generator tests prove suppression for missing-layout const input, mutable
   output/inout, by-value argument, by-value result, and nested unavailable dependencies.
3. Synthetic tests prove explicit native-returned pointer and callback-borrowed exceptions remain,
   without weakening private opaque-handle behavior.
4. ABI tests compare size, alignment, and every field offset with
   `build/bindings/ctypes_abi.json`. Include at least:
   - Bounds `min@8`, `max@32`;
   - Field geometry `origin@24`, `unit@72`;
   - Guide `box@36`, `data@64`, labels at `79` for hit and `80` for layout;
   - MVP matrices at `0/64/128`, `time@192`;
   - Panel frame `data_to_view@304`, flags at `368+`, diagnostics at `376`;
   - Panzoom resolved `visible_extent@208`;
   - Visual transform `label@32`, `matrix@48`.
5. Simulate ineffective `_align_`: portable 8/4-byte layouts and functions remain; the four aligned
   families are empty/unsupported and every dependent function is absent with diagnostics.
6. Assert exact omission of every function in the unsupported lists and exact preservation of the
   safe pointer-opaque sentinel APIs.
7. Assert no emitted function accepts/returns by value or accepts a caller-supplied pointer to an
   undisposed zero-size concrete record.
8. Native smoke:
   - actual default/output calls for `DvzFieldGeometry` and `DvzVisualTransformDesc`, including
     `struct_size == ctypes.sizeof(...)`;
   - controller MVP and panzoom resolve;
   - bounded scene/frame/guide/bounds readbacks or an equivalent existing native setup;
   - explicit garbage collection and subprocess exit `0`.

## Required validation

- `just ctypes`
- `just ctypes-check`
- `just ctypes-smoke`
- focused generator and policy tests
- relevant narrow native scene/controller tests
- Python 3.10-3.12 unsupported/alignment fallback path
- Python 3.13+ supported path
- C ABI validator and Python offsets agree
- `git diff --check`
- one coherent commit
- unconditional independent review

## Stop conditions

- Stop on any required public C ABI change.
- Stop rather than adding a hand-written Vulkan/platform struct mirror.
- Do not weaken M294 alignment/runtime gating.
- Do not omit or regress intentional opaque handle APIs.
- Do not touch paper files or unrelated generated/docs artifacts.
- Do not push, tag, release, publish, merge, create a PR, or change package versions.
