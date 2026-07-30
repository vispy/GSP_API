# M302 final pre-release audit

Date: 2026-07-30

## Verdict

**NO-GO for tagging or publication at the audited heads.**

The implementation is a strong experimental alpha candidate: native Datoviz evidence passes,
GSP's complete source and installed-wheel suites pass, public artifacts build, strict typing and
lint are clean, and documentation validation succeeds. Publication is nevertheless blocked by one
red supported-dependency CI test, contradictory release-facing documentation, incomplete package
metadata/licensing, a canonical specification/implementation mismatch, and an unresolved
pre-migration producer capability namespace.

## Audited state

| Component | Commit | State |
|---|---|---|
| GSP_API / Mission Control | `b5d947121dcc802264ce1b1b5474b53ee92d3c72` | clean before M302 records; local branch ahead of origin |
| GSP | `d45544a55756099da42ac0c15202a6e8fd8251f6` | clean; local branch ahead of origin |
| VisPy2 | `6f9cdd6181c09d6032d27840ea0d993432985366` | clean; local branch ahead of origin |
| Datoviz | `adacad87f7dce877e940a42178cc1a8d301bd1b1` | clean, read-only |
| Runtime | CPython 3.13.3, NVIDIA RTX 5090, Vulkan driver 595.84 | available |

Temporary audit artifacts are under `/tmp/m302-prerelease.HhBruZ`; they are not release artifacts.

## Validation results

| Gate | Result |
|---|---|
| M300 post-reboot Datoviz scalar image | pass: native render, capture, lifecycle, pan, zoom, reversed-x, 640×480, 800×600, and 1024×768 |
| GSP source pytest | **804 passed** |
| GSP installed-wheel pytest | **804 passed** from an isolated Python 3.13 environment |
| GSP strict mypy | 51 source files clean |
| GSP Ruff | pass |
| VisPy2 source/installed pytest | **123 passed, 1 failed** |
| VisPy2 strict mypy | 3 source files clean |
| VisPy2 Ruff | pass |
| Documentation blocks and links | 33 Python blocks compiled; 65 local links resolved |
| VisPy2 strict MkDocs | pass, with known informational checkout-link notices |
| Public example compilation | pass |
| Installed-wheel semantic example | pass from `site-packages` |
| Wheels | four built successfully; `check-wheel-contents` reports all OK |
| Source distributions | four built successfully |
| Twine checks | pass with missing-long-description warnings on all eight artifacts |

## Publication blockers

### B1 — Supported Matplotlib range makes CI red

`vispy2/tests/test_gallery_05_navigation.py::test_live_gallery_matplotlib_raster_has_two_large_face_tones`
requires at least 10,000 exact pixels of each face color. Matplotlib 3.11.1, allowed by
`matplotlib>=3.10,<4`, produces 8,874 pixels for `(65, 120, 203)`. The failure reproduces from the
fresh installed wheels. The other 123 VisPy2 tests pass.

This looks like a brittle raster-area threshold rather than an M300 semantic regression, but a
published candidate cannot knowingly ship with a red declared-dependency CI gate. Replace the
absolute threshold with an evidence-backed geometry/relative-area assertion, or narrow the
dependency range only if a real Matplotlib incompatibility is proven.

### B2 — Release-facing changelog contradicts M300

`vispy2/CHANGELOG.md` says Datoviz DATA-space images are unsupported. M300 now proves and strictly
documents public DATA-space scalar images plus colorbars. The changelog must be corrected before
release notes or publication.

### B3 — Canonical specification and implementation disagree on `Panel`

Q190 is resolved: fresh-root GSP is canonical. Its `specs/current/scene.md` defines a target Panel
with `parent_id`, `clip`, `background_rgba`, and `metadata`, while the shipped `gsp.protocol.Panel`
requires `figure_id` and exposes `viewport_rect`. The canonical `views-layout.md` mentions resolved
plot rectangles but does not repair the scene-record mismatch. GSP_API contains the later accepted
viewport semantics.

Before claiming GSP 0.2 specification conformance, synchronize the accepted viewport contract into
the canonical chapters and explicitly distinguish implemented 0.2-alpha fields from reserved
target fields.

### B4 — Producer capability identifiers retain the superseded package name

Canonical registries, requirement JSON, protocol constants, and ADR-0034 still expose
`gsp_vispy2.producer.*` identifiers although ADR-0035 accepts the `vispy2` identity. Stable protocol
identifiers need an explicit decision: preserve and document them as legacy wire identifiers, or
perform a pre-1.0 rename with migration/alias policy. Do not silently change them.

### B5 — Publication metadata and licensing are incomplete

All four artifacts pass Twine only with warnings because no long description is included. The
three GSP wheel/sdist artifacts also contain no LICENSE file or license metadata. Package metadata
lacks project URLs and standard classifiers; GSP has no changelog. Add package-specific readmes,
license declarations/files, project URLs, classifiers, and release notes before publication.

### B6 — The Datoviz distribution is not ordinarily installable as a working backend

`gsp-datoviz` intentionally declares no Datoviz dependency because no ordinary compatible artifact
is available. Consequently `vispy2[datoviz]` installs the adapter but not a functioning runtime.
This is honestly documented and is not an implementation defect, but it blocks publishing the
Datoviz extra as an ordinary supported installation. Either defer those artifacts or publish them
under an explicitly experimental development-source policy.

## Required documentation/evidence refresh

- Refresh `QUALIFICATION.md` heads and artifact hashes after corrections.
- Replace stale M285 carry-forward wording in the GSP backend guide with current M292/M300
  evidence.
- Add a GSP changelog and coherent cross-repository release note.
- Update the white paper only after canonical specification synchronization; M299's P0 findings
  remain applicable.
- Record the exact supported Matplotlib range and the Datoviz dependency boundary in release notes.

## Honest deferrals, not blockers for an experimental alpha

- full image-texel/scientific readback;
- comprehensive 3D, sphere, vector, primitive, and glyph picking;
- panel-title parity in Datoviz;
- default/live Datoviz View3D navigation beyond the opt-in experimental path;
- pixel-identical backend raster output;
- a complete material/lighting/volume/glyph system;
- binary IPC and production remote transports.

These remain acceptable only while capability negotiation and documentation continue to fail
closed.

## Recommended correction sequence

1. Fix B1 and restore the complete VisPy2 source and installed-wheel CI suite.
2. Correct the changelog and current evidence wording.
3. Synchronize canonical Panel/viewport semantics.
4. Resolve the producer capability namespace through an explicit protocol decision.
5. Complete package metadata, licensing, changelogs, and long descriptions.
6. Decide whether to defer `gsp-datoviz` and `vispy2[datoviz]` from the first publication.
7. Rebuild all artifacts, repeat installed-wheel/native gates, and write new qualification hashes.
8. Only then request explicit version/tag/publication approval.
