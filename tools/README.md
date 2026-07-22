# tools/agentctl

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
tools/agentctl pro-packet
```

The first version is intentionally simple and uses only Python standard library.
- `compare-review-examples`: runs `examples/review/[0-9]*.py` through Matplotlib and Datoviz review paths. It opens live windows by default; pass `--offscreen` to write artifacts under `artifacts/example_review/`.
- `install-viz-envrc`: installs `tools/viz-workspace.envrc.example` as the parent Viz workspace `.envrc` so local review commands prefer the sibling `../datoviz` checkout and Vulkan SDK/MoltenVK paths.
- `run_datoviz_pre_rc_replay.sh`: post-Datoviz-merge replay helper. It runs the Datoviz v0.4 smoke, guide-axis probe, S028 Datoviz offscreen review pack, then compares the candidate `capability_matrix.json` to the committed pre-RC baseline.
- `run_datoviz_v04dev_checkpoint.sh`: rolling local `v0.4-dev` checkpoint. It verifies exact sibling-checkout import provenance, runs the facade/query smoke, guide probe, isolated S028 review and comparison, public and internal lifecycle matrices, and focused adapter/session tests.
