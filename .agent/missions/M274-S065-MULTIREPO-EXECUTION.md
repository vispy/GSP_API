# M274 - S065 safe multi-repository worker execution

## Status

Completed. The accepted implementation is commit `feafeae`; closeout evidence is recorded in
`.agent/S065_M274_MULTIREPO_EXECUTION.md`.

## Goal

Extend `tools/agentctl` so later medium-agent missions can safely work in isolated worktrees from
the sibling `gsp` and `vispy2` repositories while Mission Control remains authoritative in
`GSP_API`.

## Required implementation

1. Add a repository registry to `.agent/project.json` with keys `mission-control`, `gsp`,
   `vispy2`, and read-only `datoviz`; include absolute path, expected GitHub remote, and writable
   policy.
2. Allow mission status records to declare `repositories` and repository-keyed `path_locks`.
3. At launch, validate every target repository:
   - exists and is a Git worktree;
   - expected remote identity matches;
   - writable targets are clean;
   - read-only targets never receive a worktree/branch;
   - requested locks do not overlap active run locks by exact or ancestor/descendant path.
4. For each writable target, create an isolated worktree and `agent/<run-id>` branch from the
   current target HEAD. Place multiple target worktrees under one run workspace so the provider
   sandbox can access all of them.
5. Build the prompt from Mission Control authority files, the mission file, the S065 baseline, and
   each target repository's `AGENTS.md`. Identify every worktree path and read-only evidence path.
6. Record target repository, baseline head, worktree, branch, locks, PID, and command in `run.json`.
7. Preserve current single-repository and manual-provider behavior.
8. Fail closed before launching on dirty state, remote mismatch, lock conflict, missing AGENTS, or
   unsafe read-only targeting.
9. Add standard-library automated tests using temporary Git repositories. Tests must cover
   successful one- and two-repository preparation, dirty target, remote mismatch, read-only target,
   overlapping locks, non-overlapping locks, and backward compatibility.
10. Document launch/review/integration behavior without automating merges or status completion.

## Files and locks

- Repository: `mission-control`
- Lock: `tools/agentctl`
- Lock: `.agent/project.json`
- Lock: `tools/tests/**` or the chosen agentctl test location
- Lock: Mission Control operating documentation

## Acceptance

- All new launcher tests pass.
- `tools/agentctl brief`, `review-now`, `next`, `mission show M274`, and `runs` still work.
- A dry/preparation test proves a two-repository workspace without launching a paid provider.
- No real sibling worktree or branch is left behind by tests.
- JSON validation, Ruff if applicable, and `git diff --check` pass.
- Commit one coherent Mission Control change and report its hash.

## Stop conditions

Stop if safe multi-repository sandbox access cannot be achieved with isolated child worktrees, if
the change would grant write access to Datoviz, or if integration would require automatic merging,
force operations, credential changes, or provider-account switching.
