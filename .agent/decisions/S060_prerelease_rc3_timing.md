# S060 decision - GSP prerelease timing versus Datoviz RC3

Date: 2026-07-22

## Decision

Classify the current GSP 0.2 source and package artifacts as release-ready, but do not initiate a
GSP prerelease operation yet. Wait for the next Datoviz RC3 development commit or release artifact,
rerun the exact-provenance compatibility and Texture2D checkpoints, and then request explicit user
approval for a version/tag/publication mission.

## Rationale

- The GSP wheel and sdist build, install, and import cleanly; repository validation is green.
- The current Datoviz adapter and nearest-or-linear Texture2D path have exact native evidence.
- That evidence is tied to local Datoviz commit
  `be7f2a80354c25e85bab88c85f5ea7340975b569`, described as
  `v0.4.0rc2-15-gbe7f2a803`, rather than a compatible released v0.4 artifact.
- `pyproject.toml` intentionally does not declare Datoviz v0.4 as a dependency; the only Datoviz
  extra remains the legacy v0.3 integration.
- Publishing, tagging, or selecting a new version requires explicit authority and was outside S060.

This is an operational timing decision, not a claim that GSP protocol correctness depends on
Datoviz or that Matplotlib/reference users cannot use the current source.

## Revalidation trigger

When the local Datoviz revision changes materially or an RC3 wheel/tag appears:

1. record the exact checkout, tag/describe string, imported module path, and worktree state;
2. run `tools/run_datoviz_v04dev_checkpoint.sh`;
3. run `tools/run_datoviz_texture2d_checkpoint.sh` and require 9/9 renders plus numeric conformance;
4. if a wheel exists, test the packaged GSP adapter against that installed artifact rather than only
   the sibling source checkout;
5. rerun package builds and the release checklist;
6. ask the user to approve the exact version, tag, and publication target before any release action.

No implementation mission is justified while the Datoviz revision remains unchanged and all
current checkpoints are green.
