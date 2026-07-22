# M258 source baseline and recoverable archive

Date: 2026-07-22

## Outcome

The approved S061 source baseline is reproducible and a complete external Git bundle is independently
recoverable. No public tag, remote mutation, deletion, history rewrite, release, or publication was
performed.

## Source provenance

| Item | Value |
|---|---|
| Repository | `/Users/cyrille/GIT/Viz/GSP_API` |
| Branch | `main` |
| Baseline commit | `463d34d1d6560f045e5c40af594372d0fea93ab5` |
| Describe | `463d34d` |
| Worktree at validation/archive | clean |
| Remote | `git@github.com:vispy/GSP_API` |
| Datoviz checkout | `/Users/cyrille/GIT/Viz/datoviz` |
| Datoviz commit | `be7f2a80354c25e85bab88c85f5ea7340975b569` |
| Datoviz describe | `v0.4.0rc2-15-gbe7f2a803` |
| Datoviz imported module | `/Users/cyrille/GIT/Viz/datoviz/datoviz/__init__.py` |

The Datoviz checkout retained its two pre-existing untracked paper outputs,
`paper/figure.png` and `paper/paper.pdf`; M258 did not modify them.

The first validation pass found that the generated specification source inventory did not yet list
the newly accepted ADR-0035 and S060 decision. Commit `463d34d` refreshed only that inventory. All
baseline validation and archive evidence below targets the resulting clean commit.

## Validation

| Gate | Result |
|---|---|
| Full pytest with source coverage | 680 passed, 2 skipped; 66% legacy-inclusive total coverage |
| Strict mypy | clean across 221 source files |
| Ruff | clean |
| Strict MkDocs | passed |
| Specification traceability | passed |
| Backend profile consistency | passed |
| Public documentation consistency | passed |
| Wheel and sdist build | passed |
| Isolated wheel install/import | passed with Python 3.13.4 |
| Datoviz rolling v0.4-dev checkpoint | passed; 171 focused tests |
| Datoviz Texture2D checkpoint | nearest and linear supported; 241 focused tests |

Package artifacts were generated outside the repository in
`/tmp/gsp-m258-package.G1O2WN/dist`:

| Artifact | Size | SHA-256 |
|---|---:|---|
| `gsp_vispy2-0.2.0-py3-none-any.whl` | 452 KiB | `53ea1376ef14e48837cbccc21d2f189cb00b1c0d480689e33366a6c4d898106b` |
| `gsp_vispy2-0.2.0.tar.gz` | 340 KiB | `c09473c06a89481790037588db0b09dcc0a6254d2f6a1dba14bcf2c6ee5ada46` |

These hashes reproduce the S060 release-readiness build exactly.

Native checkpoint output was generated under the standard repository artifact paths, then moved
unmodified to `/tmp/gsp-m258-checkpoints.1sgWfw` so the source worktree remained clean. The
authoritative reproducibility inputs are the committed tools, tests, fixtures, and exact Datoviz
revision rather than these temporary generated runs.

## Archive

| Item | Value |
|---|---|
| Bundle | `/Users/cyrille/GIT/Viz/archives/GSP_API/GSP_API-source-463d34d1-2026-07-22.bundle` |
| Checksum file | `/Users/cyrille/GIT/Viz/archives/GSP_API/GSP_API-source-463d34d1-2026-07-22.bundle.sha256` |
| Size | 42 MiB |
| SHA-256 | `4b6b8bdd0e403ea9f0ed7d169a7694ac0985e7a8906890d2f74cf1dc5c611f8b` |
| Included refs | 26, including local heads, remote-tracking refs, stash, worktree refs, and `HEAD` |
| Bundle head | `463d34d1d6560f045e5c40af594372d0fea93ab5` |

Recovery validation passed:

1. `git bundle verify` reported a complete history.
2. SHA-256 checksum verification passed.
3. A clean clone from only the bundle succeeded.
4. The clone resolved the exact baseline commit.
5. `git fsck --full` completed successfully in both source and recovery clones.

Unreachable blobs/trees in the source and two dangling commits reported in the recovery clone are
ordinary recoverable objects referenced by prior local/stash history; they did not cause an fsck or
bundle verification failure.

## Recovery procedure

Verify the checksum file, clone the bundle into an empty destination, run `git fsck --full`, and
confirm commit `463d34d1d6560f045e5c40af594372d0fea93ab5`. The bundle and checksum are deliberately
outside the repository and must not be added to a product repository. Selecting durable off-machine
archive storage remains a later owner decision.

