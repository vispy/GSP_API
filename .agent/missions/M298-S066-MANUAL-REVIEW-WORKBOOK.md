# M298 - S066 self-contained manual API and backend review workbook

## Status

Completed on 2026-07-28 in VisPy2 `32d63b7`.

Evidence: all ten workbook Python blocks compiled and ran successfully; repository documentation
validation compiled 22 Python blocks and checked 43 local links; isolated Matplotlib and Datoviz
outputs were 800×600; 105 tests, strict mypy, Ruff, and `git diff --check` passed; and four clean
wheels produced fourteen fresh captures plus a schema-2 manifest.

Owner amendment on 2026-07-28: VisPy2 `7e08163` converts the human path to blocking live windows.
Matplotlib uses `Figure.show()` or an explicit caller-owned session; every Datoviz case uses a
fresh ordinary process, `display(block=False)`, and `session.run()` until native close. PNGs remain
only inside the optional automated qualification and are not human-review evidence. The live
conversion also records the current public gap that VisPy2 DATA-space `imshow()` cannot use the
qualified Datoviz NDC-only image lowering.

Single-terminal amendment: VisPy2 `ecd7da1` adds `examples/manual_live_compare.py`. One parent
command launches matching Matplotlib and Datoviz windows concurrently in isolated children,
applies the same resolved plot viewport to each 3D pair, waits for both windows to close, and
supports the full priority/camera sequence through `all` or one named case. The runner and all nine
scene builders are covered by tests and documented as the primary human visual path.

Close-lifecycle correction: the owner's first live `priority-2d` run exposed a Datoviz SIGSEGV in
`dvz_input_unsubscribe()`. Datoviz's unbounded app loop reaped the closed view and destroyed its
input router before returning to GSP, although callers still needed to unsubscribe callbacks.
Datoviz `3b5a18894` now preserves those resources until explicit reap or app destruction, and
VisPy2 `e4eeaf8` additionally drives the paired-review Datoviz child with bounded one-frame pumping
for compatibility and crash isolation. Datoviz built successfully with 37/37 app tests passing;
VisPy2 passed 116 tests plus strict typing, lint, and documentation validation. Actual native
click-close behavior remains an owner-run acceptance check.

Live-size correction: the owner's next `priority-2d` review showed that an `800×600 pixel_exact`
request produced a roughly `400×300` Matplotlib host window but an `800×600` Datoviz host window
on a Retina display. VisPy2 `5b38b95` now detects Matplotlib's active device-pixel ratio once,
requests `800×600` host-logical pixels with the same scale in both children, hides the Matplotlib
toolbar, and compensates for GUI-manager chrome until its reported canvas is exactly `800×600`.
Both renderers now resolve to `800×600` logical and `1600×1200` framebuffer pixels at scale 2.
The correction passed 121 tests, strict typing, Ruff, 29-block/59-link documentation validation,
and all nine headless paired cases. Native side-by-side appearance remains an owner check.

HiDPI visual-size correction: once the windows matched, the owner's screenshot exposed roughly
2× Datoviz point, marker, stroke, and text sizes. The GSP Datoviz adapter had converted canvas
pixels with `framebuffer_per_canvas_px`, but Datoviz's `_px` attributes are already logical pixels
and its runtime applies device scale during frame emission. GSP `ef345d3` now converts with
`canvas_to_host_scale`, preventing the Retina scale from being applied twice; colorbar dimensions
now use the resolved host-logical canvas too. The complete GSP validation passed 801 tests, strict
mypy, and Ruff. Owner live comparison remains the final visual confirmation.

Matplotlib raster-DPI correction: the follow-up live comparison confirmed that semantic visual
sizes were corrected, but Matplotlib's native title, ticks, spines, and grid still rendered at
96 DPI inside a 2×, 1600×1200 framebuffer. GSP `767d09e` now defaults the Matplotlib raster DPI to
`reference_dpi * requested_device_scale` when no output DPI is explicitly requested, while keeping
the figure's host-logical extent at 800×600. Explicit guide pixel styles now convert through the
resolved canvas as well. Actual backend captures resolve to the same 800×600 logical and 1600×1200
physical geometry, and GSP passed 803 tests, strict mypy, and Ruff. Owner live comparison remains
the final visual confirmation.

## Goal

Create one linear, self-contained Markdown workbook that lets the owner manually review the
current VisPy2 public API and its Matplotlib and Datoviz realizations before any release process.
The owner should be able to read from beginning to end, copy complete code blocks into a dedicated
IPython terminal or ordinary Python scripts, optionally reuse existing example files, record
observations, and reach an explicit human acceptance decision.

## Deliverable

Create `docs/manual-pre-release-review.md` in the fresh-root VisPy2 repository. The workbook is the
authoritative review path. Links to existing documentation and examples are optional shortcuts;
all code needed for the review must be embedded in the workbook.

## Required structure

1. Scope, non-goals, exact reviewed commits, known intentional adaptations, and finding severity.
2. Prerequisites and copyable commands for:
   - a dedicated IPython process for semantic construction and Matplotlib review;
   - ordinary one-case-per-process Python execution for native Datoviz review;
   - a review output directory outside all repositories.
3. Public API orientation and runtime signature/help inspection.
4. Complete 2D examples covering points/scatter, markers, paths/segments, pixels, vectors/quiver,
   primitives, text, images, color mapping, guides, and relevant view controls.
5. Complete 3D examples covering mesh, spheres, vectors, primitives, pixels, billboard text,
   perspective, orthographic, fit, orbit, pan, zoom, reset, and flat-Lambert lighting.
6. Explicit sessions, discovery, ordinary and versioned capabilities, file output, lifecycle,
   structured unsupported behavior, and one supported point query.
7. Current-head Matplotlib/Datoviz gallery regeneration and a side-by-side visual checklist.
8. Live Datoviz navigation with orbit, pan, zoom, reset, lighting, close, and Ctrl-C fallback.
9. Focused implementation-reading traces from VisPy2 through GSP into each adapter.
10. Embedded observation tables, issue templates, section sign-offs, and final go/no-go checklist.

Every exercise must include its goal, complete code, exact execution method, expected result,
backend-specific expectations, and questions/check boxes. Code blocks must be independently
recoverable after an IPython restart and must not depend on hidden notebook state.

## Execution constraints

- Prefer public VisPy2 APIs. Import GSP protocol types only where sessions, capabilities, or queries
  genuinely require them.
- Use current fresh-root paths and package names; do not reuse stale `gsp_vispy2` or archive commands.
- Keep Datoviz native cases in bounded ordinary child processes rather than a long-lived IPython
  process.
- Use no absolute paths inside reusable repository documentation. Derive sibling repositories from
  the VisPy2 checkout and use a caller-selected external output directory.
- Distinguish strict semantics, documented adaptations, experimental behavior, and unsupported
  behavior. Do not ask for cross-backend pixel identity.
- Include the current flat-Lambert Gallery 5 behavior and remove the stale unlit-mesh wording from
  the review path.
- Do not change public APIs, backend implementations, versions, tags, packages, or release files.

## Validation

- Compile every embedded Python block that is intended for direct execution.
- Execute semantic construction and Matplotlib examples.
- Execute bounded Datoviz static cases in isolated child processes where the qualified runtime
  supports them.
- Run the existing current-head gallery validator or an equivalent exact-wheel qualification
  without treating old artifacts as fresh evidence.
- Validate local Markdown links and shell commands.
- Run VisPy2 pytest, strict mypy, Ruff, documentation validation, and `git diff --check`.
- Perform an independent editorial/technical review of the workbook before integration.

## Acceptance

- One Markdown file can be followed linearly without consulting other documents.
- All required code is embedded and copyable.
- Existing scripts are clearly optional shortcuts.
- Expected differences and unsupported behavior are explicit.
- The owner can record findings and make a human release-readiness decision.
- No release operation occurs.

## Stop conditions

Stop and report rather than changing source behavior if the workbook exposes an implementation
bug, a source/spec contradiction, a capability lie, a native crash, or a missing public API that
would require design work. Record such findings for a later approved correction mission.
