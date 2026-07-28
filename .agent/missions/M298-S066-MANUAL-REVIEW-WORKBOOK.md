# M298 - S066 self-contained manual API and backend review workbook

## Status

Owner-approved on 2026-07-28 for immediate execution by Mission Control.

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
