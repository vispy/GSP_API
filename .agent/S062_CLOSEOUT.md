# S062 closeout - clean GSP and VisPy2 repository bootstrap

Date: 2026-07-22

## Outcome

Created and qualified two independent, fresh-history local repositories:

| Repository | Head | Root | Remotes |
|---|---|---|---|
| `/Users/cyrille/GIT/Viz/gsp` | `884bb0a` | `3cb9fce` | none |
| `/Users/cyrille/GIT/Viz/vispy2` | `55a16b3` | `eb498d4` | none |

The GSP monorepo owns `gsp-core`, `gsp-matplotlib`, and `gsp-datoviz`. The separate VisPy2
repository owns only the high-level semantic producer. Both repositories retain exact migration
provenance and are independently valid according to `git fsck`; the source archive bundle remains
available with verified SHA-256 `4b6b8bdd0e403ea9f0ed7d169a7694ac0985e7a8906890d2f74cf1dc5c611f8b`.

## Installed-wheel qualification

| Combination | Result |
|---|---|
| Core only | 167 tests; no adapters imported; empty backend discovery |
| VisPy2 + core only | 10 producer tests and semantic example |
| `vispy2[matplotlib]` from local artifacts | dependency resolution and 126 adapter tests |
| `vispy2[datoviz]` from local artifacts | dependency resolution and 150 adapter tests |
| All four distributions | one unchanged VisPy2 scene rendered through both providers |

Strict mypy passes for 51 GSP and three VisPy2 source files. Ruff passes both repositories. All
package imports in the qualification environment resolve from installed wheels. Datoviz native
validation used the explicitly configured checkout at
`be7f2a80354c25e85bab88c85f5ea7340975b569`; no sibling Datoviz files were modified.

Final wheel SHA-256 values:

- `gsp-core`: `727ec6d12078b8abf2aa1f3eebc6373704eba6a2e17b5c98256c9e8f37e607cc`
- `gsp-matplotlib`: `5935b2bb5845449d3ba63391c68d29492a89dd458ae224ead85f99e336eade6b`
- `gsp-datoviz`: `675edf044d778b7d64bd66c38b39c54a63a1fe623405437ade70f69d2646d116`
- `vispy2`: `637b73fe6755b838744042024bf90e6255bc1491e342e325505fc2abd1ab9730`

## Boundary decisions now implemented

- Metadata-only backend discovery is lazy and side-effect-free.
- Backend selection and adaptation policy are explicit.
- VisPy2 imports only `gsp-core` and retains no backend/session/native state.
- One-shot Matplotlib publication uses an ephemeral provider session.
- Interactive and non-blocking execution uses an explicit caller-owned session.
- Datoviz source checkout bootstrapping remains development-only until a compatible ordinary RC3
  artifact exists.

## External state

No GitHub repository, remote, push, pull request, tag, release, or publication was created. Those
operations require a new explicit owner-approved stage. `GSP_API` remains the historical source and
Mission Control archive; no history was rewritten or removed.
