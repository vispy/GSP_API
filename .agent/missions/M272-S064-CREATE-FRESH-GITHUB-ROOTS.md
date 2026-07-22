# M272 - S064 create fresh GitHub roots

## Status

Draft; authorized after M271 succeeds.

## Acceptance

- Fresh public `vispy/gsp` and `vispy/vispy2` repositories are created without generated commits.
- Qualified local repositories remain clean and receive only explicit `origin` remotes.
- Local `main` histories push normally without force and become the remote default branches.
- Remote heads exactly match the qualified local heads.

## Stop conditions

Stop on a name collision, dirty worktree, unexpected generated commit, non-fast-forward requirement,
or any mismatch between local and remote heads.
