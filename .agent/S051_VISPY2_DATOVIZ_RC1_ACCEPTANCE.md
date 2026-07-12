# S051 VisPy2 to Datoviz RC1 acceptance evidence

Date: 2026-07-12

Mission: M233

## Result

Five representative scenes were authored through public `vispy2` calls and lowered to the accepted
in-memory visual-QA scene model without JSON or base64 in the execution path. Matplotlib and Datoviz
received the same semantic scene records. Datoviz execution used one child process per case.

| Outcome | Count |
|---|---:|
| strict | 4 |
| unsupported | 2 Datoviz rows plus the Matplotlib Texture2D boundary |
| backend failure | 3 Datoviz rows |

The scalar-image/colorbar Datoviz row rejected as unsupported before execution. The primitive,
text, and untextured-mesh Datoviz children failed in native execution and preserved crash reports.
Texture2D remained unsupported on both backends and was not promoted. All non-strict outcomes have
structured reason codes and semantic record IDs in `acceptance_manifest.json`.

## Evidence

- `artifacts/visual_qa/s051/rc1-acceptance/acceptance_manifest.json`
- paired backend artifacts and logs under the same directory;
- versioned debug-JSON scene fixtures with NPZ array sidecars under `scenes/`;
- Datoviz checkout `v0.4-dev` at `ff62b3256f1de7dd2df2ee890c99968715789a27`.

Focused validation: 86 tests passed. Strict mypy is clean for the new S051 adapter; a combined check
also reports three pre-existing missing-ndarray-type-argument findings in `cases.py`.

## Promotion decision

The post-RC public session preview promotion conditions are **not met**. Known crashes are not yet
rejected before native execution, and repeated deterministic create/show/close lifecycle evidence
does not exist. ADR-0033 remains unchanged. No public session or renderer capability is promoted.
