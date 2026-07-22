# M273 - S064 GitHub CI qualification and closeout

## Status

Draft; authorized after M272 succeeds.

## Acceptance

- Minimal least-privilege CI workflows cover pytest, strict mypy, Ruff, and wheel builds.
- GSP and VisPy2 checks pass locally before CI commits are pushed.
- CI commits push normally to `main`; no pull request is created for this approved bootstrap.
- Repository settings, archive state, remotes, heads, and Actions results are recorded.
- No tag, release, or package publication occurs.
