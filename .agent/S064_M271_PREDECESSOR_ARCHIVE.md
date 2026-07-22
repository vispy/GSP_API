# M271 predecessor archive evidence

Date: 2026-07-22

## Verified backups

| Repository | Bundle | SHA-256 |
|---|---|---|
| `vispy/GSP` | `/Users/cyrille/GIT/Viz/archive/vispy-GSP-pre-S064-20260722.bundle` | `62c22797ef9f010ac55f13e219388bbe6f1b6c4d42151fb7912a8d4a855fa779` |
| `vispy/vispy2` | `/Users/cyrille/GIT/Viz/archive/vispy-vispy2-pre-S064-20260722.bundle` | `4c2de794326fb5b548d5197b5c113260f6c544ca076dd2d7bcc6e513100d9829` |

Both bundles pass `git bundle verify`. The GSP bundle contains both branches plus all fetched pull
request head/merge refs; the VisPy2 bundle contains its complete main history.

## GitHub outcome

| Original | Archive | Repository ID | Archived | Preserved head |
|---|---|---:|---|---|
| `vispy/GSP` | `vispy/GSP-old` | 835608053 | yes | `c39b719f76b12342eb74568edc239ed09184e152` |
| `vispy/vispy2` | `vispy/vispy2-old` | 828833508 | yes | `a02138452a6350d9fc6d25be9ab41e50b2d9e202` |

GitHub rejected direct Pages deletion with HTTP 422 before rename. The approved safe fallback renamed
the repository first: the old `/GSP/` Pages path then returned 404 and the preserved archive site
moved to `/GSP-old/`. Both repositories were archived only after identity and path verification.

No repository was deleted and no history was rewritten. M272 is approved next.
