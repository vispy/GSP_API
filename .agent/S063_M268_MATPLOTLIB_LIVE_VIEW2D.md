# M268 Matplotlib canonical live View2D synchronization

Date: 2026-07-22

Implemented and committed in fresh-root GSP commit `003e6f4`.

- DATA coordinates now remain native Matplotlib data coordinates on `Axes.transData`.
- NDC coordinates remain axes-relative on `Axes.transAxes`.
- A private session-owned binding synchronizes native X/Y limit callbacks into canonical
  `View2D` state, monotonic revision tokens, view snapshot IDs, and refreshed layout snapshots.
- Canonical-to-native application uses a recursion guard and advances exactly once.
- Session close disconnects both native limit callbacks deterministically.
- Reversed ranges and inline affine transforms retain their semantic values; migrated tests now
  assert the native transform boundary instead of the superseded eager axes-fraction lowering.

Validation: 298 core/Matplotlib/conformance tests passed; strict mypy passed for all 51 GSP source
files; Ruff and diff whitespace checks passed. The full suite has only the one intentional M269
Datoviz session-wiring failure remaining.

M269 is approved next.
