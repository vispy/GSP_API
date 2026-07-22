# S064 closeout - GitHub predecessor archival and fresh-root publication

Date: 2026-07-22

## Outcome

S064 is complete. The two predecessor repositories are preserved under archival names, and the
fresh GSP and VisPy2 histories are public at their intended canonical names with green CI.

| Role | Repository | Repository identity | State / exact head |
|---|---|---|---|
| Archived predecessor | `vispy/GSP-old` | `835608053` / `R_kgDOMc5d9Q` | archived; `master` preserved at `c39b719f` |
| Archived predecessor | `vispy/vispy2-old` | `828833508` / `R_kgDOMWb-5A` | archived; `main` preserved at `a0213845` |
| Fresh root | `vispy/gsp` | `1309232723` / `R_kgDOTglOUw` | public `main` at `e2e7ac5b27fe34cfd60679c1a544f4d6f2bee717` |
| Fresh root | `vispy/vispy2` | `1309232757` / `R_kgDOTglOdQ` | public `main` at `7cffafb3aa9d57468cecc7108735623ce124c196` |

The fresh repositories were created empty and received normal, non-force pushes. Their initial
heads were `cb10e1b57cb43ccbed19bafff56f8da09e44dac9` (GSP) and
`55a16b30344a259b81d4842ce55330d014416d39` (VisPy2). Local and remote final heads match exactly,
and both local worktrees are clean.

## Recovery and Pages

| Bundle | SHA-256 |
|---|---|
| `/Users/cyrille/GIT/Viz/archive/vispy-GSP-pre-S064-20260722.bundle` | `62c22797ef9f010ac55f13e219388bbe6f1b6c4d42151fb7912a8d4a855fa779` |
| `/Users/cyrille/GIT/Viz/archive/vispy-vispy2-pre-S064-20260722.bundle` | `4c2de794326fb5b548d5197b5c113260f6c544ca076dd2d7bcc6e513100d9829` |

Both mirror bundles pass Git bundle verification and preserve all predecessor refs. GitHub rejected
direct Pages deletion with HTTP 422, so the safe rename fallback moved the archived site to
`https://vispy.org/GSP-old/` (HTTP 200); the stale canonical `https://vispy.org/GSP/` path now
returns HTTP 404.

## CI qualification

Both workflows grant only `contents: read`, use Python 3.13, and run pytest, strict mypy, Ruff,
wheel builds, and isolated installed-wheel tests. They use the current Node 24 action majors
(`actions/checkout@v7` and `actions/setup-python@v7`).

| Repository | Local qualification | Final GitHub Actions result |
|---|---|---|
| GSP | 451 source tests; 51 strict-typed files; Ruff; three wheels; 451 installed-wheel tests | success: `29956292325` at `e2e7ac5` |
| VisPy2 | 10 source tests; 3 strict-typed files; Ruff; core + producer wheels; 10 installed-wheel tests and semantic example | success: `29956293133` at `7cffafb` |

The first clean Linux GSP run exposed an optional-Datoviz mypy portability mismatch. A module-only
`ignore_missing_imports` override fixed the absent-vs-untyped optional dependency distinction while
preserving strict checks for all GSP source files; the replacement and final runs passed.

## Repository settings and exclusions

Both fresh repositories are public, unarchived, default to `main`, enable issues, disable wiki and
discussions, and contain only the `main` branch. Both archival repositories remain public and
archived. No predecessor repository was deleted, and no history was rewritten.

No pull request, force push, tag, GitHub release, package publication, credential change, or sibling
Datoviz repository modification occurred. Release/version decisions remain a separately authorized
stage.
