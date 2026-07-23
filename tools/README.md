# Mission Control launcher

`tools/agentctl` is a minimal repo-local Mission Control CLI intended to be called by Codex.

Useful commands:

```bash
tools/agentctl brief
tools/agentctl review-now
tools/agentctl next
tools/agentctl usage
tools/agentctl mission list
tools/agentctl mission show M001
tools/agentctl task list
tools/agentctl runs
tools/agentctl launch-approved
tools/agentctl launch M275 --provider codex-ucl --prepare-only
tools/agentctl pro-packet
```

The launcher uses only the Python standard library. Mission Control remains authoritative in this
repository even when a mission changes the sibling GSP and VisPy2 repositories.

## Repository declarations

`.agent/project.json` registers every repository by a stable key, absolute source path, expected
GitHub remote, and writable policy. Mission entries in `.agent/status.json` may select those keys
and declare repository-keyed locks:

```json
{
  "repositories": ["gsp", "vispy2", "datoviz"],
  "path_locks": {
    "gsp": ["packages/gsp-core"],
    "vispy2": ["src/vispy2", "tests"]
  }
}
```

Every explicitly selected writable repository requires at least one lock. Read-only repositories
must not have locks. Missions without these fields retain the legacy single-repository
`mission-control` behavior.

## Launch and preparation

Before creating anything, `agentctl launch` verifies that the mission is approved, the provider is
configured, stop conditions exist, every selected path is a Git worktree with the expected
`origin`, every writable source is clean, every target has `AGENTS.md`, and no requested lock is
equal to, above, or below a lock held by an active run. Launch validation is serialized so two
concurrent launch commands cannot claim overlapping locks.

For an external provider, each writable target is branched from its current exact `HEAD` as
`agent/<run-id>` and checked out below one coordination workspace:

```text
GSP_API-agent-workspaces/<run-id>/
  .git/                 # uncommitted coordination wrapper for sandbox scope
  gsp/                  # isolated linked worktree, when writable
  vispy2/               # isolated linked worktree, when writable
```

The provider starts at the coordination workspace, which makes every child worktree available
inside one sandbox root. A selected read-only repository such as Datoviz stays at its registered
source path and is included in the prompt only as an evidence path; it never receives an agent
branch or worktree.

`--prepare-only` performs the complete validation, prompt construction, worktree creation, and
metadata recording but does not start the provider. The prepared run holds its locks until Mission
Control marks it terminal and removes its worktrees. Manual or disabled providers retain the
current prompt-only `manual_required` flow and do not create isolated worktrees.

If preparation fails after a worktree was created, the launcher removes only the worktrees and
branches created for that failed run. It records no mission progress and starts no provider.

## Review and integration

Each `run.json` records the source repository, baseline commit, worktree, branch, locks, provider
command, and PID. Review each repository branch independently against its recorded baseline and run
the mission's required tests in the corresponding worktree. Mission Control then integrates
accepted commits through an explicit, normal, reversible Git operation.

`agentctl` deliberately does not merge branches, update a mission to completed, delete successful
run worktrees, push, or create pull requests. Those steps happen only after review, and run/mission
status is updated separately so integration remains traceable.

## Other visualization tools

- `compare-review-examples`: runs `examples/review/[0-9]*.py` through Matplotlib and Datoviz review paths. It opens live windows by default; pass `--offscreen` to write artifacts under `artifacts/example_review/`.
- `install-viz-envrc`: installs `tools/viz-workspace.envrc.example` as the parent Viz workspace `.envrc` so local review commands prefer the sibling `../datoviz` checkout and Vulkan SDK/MoltenVK paths.
- `run_datoviz_pre_rc_replay.sh`: post-Datoviz-merge replay helper. It runs the Datoviz v0.4 smoke, guide-axis probe, S028 Datoviz offscreen review pack, then compares the candidate `capability_matrix.json` to the committed pre-RC baseline.
- `run_datoviz_v04dev_checkpoint.sh`: rolling local `v0.4-dev` checkpoint. It verifies exact sibling-checkout import provenance, runs the facade/query smoke, guide probe, isolated S028 review and comparison, public and internal lifecycle matrices, and focused adapter/session tests.
- `run_datoviz_texture2d_checkpoint.sh`: focused S059 nearest-or-linear Texture2D checkpoint. It verifies exact sibling-checkout provenance and field-slot sampling symbols, renders five nearest regression cases plus four linear cases, checks eight numeric probes within `2/255`, runs the current-protocol VisPy2 example, and executes focused adapter/producer tests. Odd output dimensions are required so center probes map to exact pixel centers.
