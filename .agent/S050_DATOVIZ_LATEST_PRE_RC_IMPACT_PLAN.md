# S050 Datoviz latest pre-RC impact plan

Date: 2026-07-05

Mission: M232 - S050 Datoviz latest pre-RC compatibility impact replay

## Context

The sibling Datoviz checkout has moved beyond the M231 replay baseline.

| Field | Value |
|---|---|
| Datoviz path | `/home/cyrille/GIT/Viz/datoviz` |
| Branch | `api/pre-rc-cleanup` |
| M231 replay commit | `af168b5a9` |
| Current inspected commit | `1ef626a56` |
| Current worktree | clean |

The relevant post-M231 Datoviz commits are concentrated in:

- stable and low-level mutator return contracts moving to `DvzResult`;
- generated raw `ctypes` updates;
- low-level controller mutators for camera, arcball, panzoom, turntable, and fly;
- GUI/canvas teardown timing (`Wait for canvas device before teardown`, `Wait before app GUI teardown`);
- controller result-contract documentation;
- post-result-contract planning/classification notes, including future composition-layer rendering
  docs that do not change GSP's current adapter surface.

## Impact On GSP

| Area | Impact | GSP plan |
|---|---|---|
| Generic mutator return handling | Expected compatible. M231 already centralized success handling so integer `0` / ctypes integer `0` is success. | Re-run focused `_call_succeeded` and adapter smoke tests against current Datoviz. Patch only if a new return wrapper shape appears. |
| View3D camera updates | Potentially affected because `dvz_camera_set_view()` and camera projection mutators now return `DvzResult`. | Verify retained View3D setup/update and navigation smokes. Do not change public GSP View3D semantics unless replay proves a regression. |
| View2D/panel setup and visual binding | Stable panel and scene mutators now consistently return `DvzResult`. | Re-run the S028 replay pack and compare against M231 artifacts. |
| Offscreen review stability | Datoviz added teardown waits after M231. This may reduce remaining SIGSEGV rows. | Re-run guide/colorbar/text-heavy S028 rows through the isolated-child review harness before changing capability rows. |
| Texture2D promotion | Not unblocked. Current commits do not prove sampler, origin, unmanaged RGBA, or exact unlit multiplication semantics. | Keep M222 blocked. Any Texture2D row promotion still requires fresh M228-style evidence. |
| Removed transitional texture wrapper | Already reflected in GSP spec and adapter posture: sampled fields plus `dvz_visual_set_field()` are the pre-RC path. | Do not reintroduce `dvz_visual_set_texture_rgba8()` compatibility. |

## Next Step

Open M232 as the next ready Mission Control item ahead of blocked M222.

M232 should refresh evidence against Datoviz `1ef626a56` without editing the sibling repository:

1. inspect Datoviz `agents/now/HANDOFF_PUBLIC_API_PRE_RC_AUDIT.md` and current generated `datoviz/_ctypes.py`;
2. run the Datoviz v0.4 import/API smoke against `/home/cyrille/GIT/Viz/datoviz`;
3. run the focused GSP Datoviz adapter tests covering `_call_succeeded`, sampled fields, View2D, and retained View3D camera paths;
4. run `tools/run_datoviz_pre_rc_replay.sh`;
5. compare the new replay matrix to both the committed pre-RC baseline and the M231 `af168b5a9` evidence;
6. update capability/status docs only from fixture-backed evidence.

## Stop Conditions

- Stop before editing `/home/cyrille/GIT/Viz/datoviz`.
- Stop before advertising Datoviz Texture2D capabilities.
- Stop before promoting guide/colorbar/text/query rows from teardown-only improvements without semantic evidence.
- Stop and create a ChatGPT Pro consultation packet if a Datoviz API change creates a GSP protocol conflict rather than a binding or compatibility issue.
