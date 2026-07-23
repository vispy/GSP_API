# M274 safe multi-repository execution closeout

Date: 2026-07-23

M274 added the execution boundary required for supervised medium-agent work across the fresh
`gsp` and `vispy2` repositories while retaining `GSP_API` as Mission Control.

| Evidence | Result |
|---|---|
| Worker run | `R20260723-103316-M274` with `codex-ucl` |
| Worker branch commit | `4cd65a0` |
| Integrated Mission Control commit | `feafeae` |
| Focused launcher suite | 12 passed |
| Formatting and lint | Ruff passed |
| JSON and whitespace validation | Passed |
| Real registry validation | Clean writable GSP/VisPy2 accepted; dirty read-only Datoviz accepted without a worktree |

The accepted launcher validates registered repository identity, clean writable sources, required
repository instructions, stop conditions, serialized mission approval, and exact or
ancestor/descendant path-lock conflicts before a provider starts. Writable repositories receive
isolated child worktrees under one sandbox workspace. Datoviz remains a read-only evidence path and
never receives a branch or worktree.

An independent review rejected the first draft until worker prompts explicitly enforced lock
roots, approval was rechecked under the launch mutex, partial worktree failures were recoverable,
and prompt/template failures entered the cleanup path. Additional tests cover those cases and
legacy single-repository behavior.

The launcher deliberately does not integrate commits, mark missions complete, push, open pull
requests, or remove successful worktrees. Mission Control performs review, commits sandbox-limited
worker changes when necessary, and integrates accepted commits through explicit reversible Git
operations.
