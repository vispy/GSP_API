# M294 - S065 Datoviz panel-state ctypes ABI correction

## Status

Approved for direct execution with `codex-ucl-gpt-5.6-sol-medium`.

## Baseline and reproduced defect

- Datoviz baseline is `bb1e709a74f8f4c05b22b244496cef7584cffb8c` on the clean isolated source registered as `datoviz-ctypes-fix`.
- The canonical Datoviz checkout contains unrelated untracked `paper/figure.png` and `paper/paper.pdf`; never touch, stage, commit, or copy them.
- Generated `datoviz/_ctypes.py` declares `DvzPanelView3DState` and `DvzPanelView2DState` as empty `ctypes.Structure` subclasses with no `_fields_`.
- Python therefore reports size zero for both records, while the current C ABI reports View3D state size 304/alignment 16 and View2D state size 192/alignment 16.
- `dvz_panel_view3d_state()` assigns the complete C record through the supplied pointer. GSP currently passes a pointer to the zero-byte Python object, overwriting Python-managed memory. Exact-wheel Gallery 2 then writes a valid PNG and JSON before crashing during garbage collection with signal 11.
- Exact Gallery 2 without the retained-state evidence call exits zero. Runtime-patching a complete, 16-byte-aligned View3D state layout also exits zero, including explicit garbage collection.

## Required implementation

1. Follow Datoviz `AGENTS.md`, binding policy, and build/test rules.
2. Add both `DvzPanelView2DState` and `DvzPanelView3DState` to the supported layout-record policy in `spec/bindings/ctypes.yml`.
3. Make the generator emit ABI-exact ctypes layouts for these records, including the required 16-byte matrix/record alignment. Implement a general, narrowly scoped alignment mechanism based on extracted record/type facts or explicit binding policy; do not hand-edit only the generated `_ctypes.py`, hard-code host paths, or add a one-off runtime monkeypatch.
4. Preserve Datoviz's Python `>=3.10` support. Python only added effective `ctypes.Structure._align_` support in 3.13, and local probes prove that 3.10-3.12 ignore it. A solution that exposes the aligned records or pointer-output functions unconditionally is forbidden.
5. The preferred bounded design is runtime-verified conditional layout support: on Python/ctypes runtimes where requested alignment is effective, emit the complete records and bind the output functions; otherwise leave the records opaque and omit or explicitly mark the affected raw functions unavailable. Generalize function emission so a native output-pointer function cannot be callable when its concrete pointee record is absent, zero-size, incomplete, or misaligned. An equally safe portable mechanism is acceptable only with multi-version ABI proof.
6. Make unsupported-runtime behavior explicit and diagnostic-bearing through the generated binding's existing missing/unsupported machinery. Do not raise during ordinary `import datoviz` merely because these optional aligned records are unavailable.
7. Regenerate the tracked ctypes binding with the normal Datoviz command.
8. Extend generator/policy/smoke tests so both state records must have the complete required fields, positive size, correct offsets, and ABI size/alignment on supported runtimes. At minimum verify the ABI prologue, state fields, camera/projection fields, orthographic bounds, and matrices.
9. Add tests for a pre-3.13/no-effective-alignment runtime proving both records remain opaque and both native output functions are unavailable rather than unsafe.
10. Add a bounded native readback smoke or equivalent existing focused test proving both output records are safe to pass to their public C functions and that returned `struct_size` equals the generated ctypes size when aligned layouts are supported.
11. Keep the public C structs and functions unchanged unless evidence proves the declared ABI itself is wrong. Do not modify GSP, VisPy2, the `data` submodule, paper files, runtime libraries, release metadata, or unrelated Datoviz work.

## Required validation

- Focused generator unit tests.
- Multi-version or simulated-runtime tests proving safe behavior both with and without effective `_align_`.
- `just ctypes`.
- `just ctypes-check`.
- `just ctypes-smoke`.
- The narrowest relevant scene/native test for both panel-state readbacks.
- A Python ABI probe showing View2D size 192/alignment 16 and View3D size 304/alignment 16, or the platform-neutral exact values produced by the C ABI validator if those constants are not portable.
- A bounded exact-wheel or source Gallery 2 evidence subprocess proving PNG plus JSON creation, exit code zero, and clean explicit garbage collection.
- `git diff --check`, staged-scope inspection, and one coherent Datoviz commit.

## Acceptance

- On supported ctypes runtimes, neither generated state record remains zero-size and Python/C ABI size, alignment, and field offsets agree.
- On older supported Python runtimes that cannot express 16-byte alignment, the affected records remain intentionally opaque and the unsafe output functions are not callable.
- Native state readback cannot overwrite the Python allocation.
- Gallery 2 evidence exits cleanly repeatedly without ignoring signals or bypassing cleanup.
- Independent review issues unconditional ACCEPT.

## Stop conditions

- Stop on need to change unrelated public ABI or runtime behavior.
- Stop rather than weakening ABI validation, skipping the state readback, accepting signal 11 as success, or committing generated binaries/user files.
- Do not push, tag, release, publish, merge, create a PR, or modify package versions.
