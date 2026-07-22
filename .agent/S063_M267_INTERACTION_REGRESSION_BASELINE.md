# M267 interaction regression baseline

Date: 2026-07-22

## Outcome

Committed the S063 red regression baseline in the fresh-root `gsp` repository as commit
`0a950be42cb13ae26e7ba3283d7405a9e1daf605` before changing production code.

| Gate | Baseline |
|---|---|
| Pre-S063 GSP suite | 443 passed |
| S063 baseline suite | 446 passed, 3 intentionally failing |
| Matplotlib DATA native-limit behavior | Fails: artist remains axes-relative |
| Matplotlib NDC native-limit behavior | Passes: overlay remains stationary |
| Matplotlib canonical session synchronization | Fails: no session-owned live binding |
| Datoviz interactive session wiring | Fails: canonical controller is not enabled |
| Cross-provider semantic pan contract | Passes: ranges and revision transition agree |
| Ruff on new tests | Pass |

The migrated static tests that intentionally encode the old eager DATA-to-axes lowering are in
`packages/gsp-matplotlib/tests/test_matplotlib_protocol_slice.py`, including inline affine,
reversed-range, and family-specific DATA placement assertions. M268 must update those assertions
only where the native Matplotlib transform changes; semantic positions remain unchanged.

Datoviz native provenance is
`be7f2a80354c25e85bab88c85f5ea7340975b569`. No Datoviz checkout files were modified.

No authority conflict or public API requirement was found. M268 is approved next.
