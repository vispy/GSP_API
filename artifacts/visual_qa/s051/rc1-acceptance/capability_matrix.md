# Backend Capability Matrix

Run id: `s051-vispy2-rc1-acceptance`

| Case | Backend | Status | Reason code | Rendering | Query |
|---|---|---|---|---|---|
| `vispy2/primitives` | matplotlib | strict / pass.semantic_strict | `matplotlib_reference_rendered` | True | False |
| `vispy2/primitives` | datoviz | crashed / fail.semantic | `datoviz_runtime_error` | False | False |
| `vispy2/scalar_image_colorbar` | matplotlib | strict / pass.semantic_strict | `matplotlib_reference_rendered` | True | False |
| `vispy2/scalar_image_colorbar` | datoviz | unsupported / unsupported.capability | `datoviz_adapter_unsupported` | False | False |
| `vispy2/text` | matplotlib | strict / pass.semantic_strict | `matplotlib_reference_rendered` | True | False |
| `vispy2/text` | datoviz | crashed / fail.semantic | `datoviz_runtime_error` | False | False |
| `vispy2/mesh` | matplotlib | strict / pass.semantic_strict | `matplotlib_reference_rendered` | True | False |
| `vispy2/mesh` | datoviz | crashed / fail.semantic | `datoviz_runtime_error` | False | False |
| `vispy2/texture2d_boundary` | matplotlib | not_run / unsupported.capability | `matplotlib_reference_not_run` | False | False |
| `vispy2/texture2d_boundary` | datoviz | unsupported / unsupported.capability | `datoviz_adapter_unsupported` | False | False |
