# S061 closeout - GSP and VisPy2 migration foundation

Date: 2026-07-22

## Outcome

S061 accepted the two-repository architecture and `vispy2` identity, established a reproducible clean
source baseline, created an independently recoverable full-history archive, and validated a curated
component migration manifest. No new repository, remote, public tag, push, release, publication,
deletion, or history rewrite was performed.

## Evidence

| Area | Result |
|---|---|
| Architecture | ADR-0035 accepted: separate fresh-root `gsp` and `vispy2` repositories |
| Source baseline | `463d34d1d6560f045e5c40af594372d0fea93ab5`; all repository/package/native gates pass |
| Archive | Complete 42 MiB bundle; SHA-256 `4b6b8bdd0e403ea9f0ed7d169a7694ac0985e7a8906890d2f74cf1dc5c611f8b`; recovery verified |
| Inventory | 31 components: 16 migrate-now, 11 archive-only, four defer/reassess |
| Dependency audit | No formal-protocol dependency on legacy object graph; four explicit rewrite gates |
| Target paths | `/Users/cyrille/GIT/Viz/gsp` and `/Users/cyrille/GIT/Viz/vispy2` are available |

Detailed evidence lives in `.agent/S061_M258_SOURCE_BASELINE_ARCHIVE.md`,
`.agent/S061_M259_CURATED_MIGRATION_INVENTORY.md`, and
`.agent/migration/S061_migration_manifest.json`.

## Decision for next stage

S062 is proposed as a local unpublished fresh-root bootstrap. It must implement package boundaries
and installed-wheel gates before any GitHub repository is created. S062 requires separate explicit
approval and does not inherit permission for remote creation or publication.

