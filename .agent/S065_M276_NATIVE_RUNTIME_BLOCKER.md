# M276 native runtime blocker

Date: 2026-07-23

M276 stopped without modifying either worktree because its first isolated native Datoviz lifecycle
probe exited with `SIGABRT`. This is an explicit mission stop condition, so live View3D navigation
was not promoted and no partial implementation was integrated.

| Evidence | Result |
|---|---|
| Worker run | `R20260723-112827-M276` with `codex-ucl` |
| Baseline worktrees | GSP `c39b046`; VisPy2 `60077e8`; both remain clean |
| Focused synthetic Datoviz suite | 152 passed |
| Binding discovery | retained View3D camera and live-input symbols are present |
| First native lifecycle iteration | `SIGABRT`, exit 134 |
| Crash report | `/Users/cyrille/Library/Logs/DiagnosticReports/Python-2026-07-23-113154.ips` |
| Capability posture | live View3D navigation remains experimental and unadvertised |

The crash stack is:

```text
dvz_app
  -> dvz_app_with_config
  -> dvz_app_with_resources
  -> _app_gpu_config_add_glfw_extensions
  -> dvz_window_glfw_init
  -> glfwInit
  -> _glfwInitCocoa
  -> GetCurrentProcess / _RegisterApplication
  -> abort
```

This occurs during native application initialization, before scene creation, camera updates,
subscriptions, or cleanup. It therefore does not prove a camera or callback defect, and the
required 25 lifecycle iterations cannot run in the current agent subprocess environment.

Static review nevertheless identified bounded work still required by M276:

- `DatovizSession.display()` and `run()` wire interactive View2D but not View3D;
- renderer shutdown closes `live_navigation` but omits `live_view3d_navigation`;
- Matplotlib lacks focused revised-View3D rerender coverage;
- the caller-owned VisPy2 live-camera example is absent.

Session wiring must remain conditional on an advertised live View3D capability. Offscreen rendering
must remain noninteractive, callback subscription/unsubscription must match exactly, and fake
router tests cannot justify promotion. The accepted P029 boundary requires genuine native
panel/application lifecycle evidence.

## Safe resume choices

1. Resume the full mission in a GUI-capable native execution environment and run 25 isolated,
   timeout-bounded create/display/update/close iterations.
2. With explicit owner approval, split out only the non-native cleanup, Matplotlib rerender, and
   example work while keeping live Datoviz session wiring and capability promotion blocked.

M277 remains dependent on M276 and is not launched automatically while this stop condition is
active.

## Owner decision

The owner approved safe resume choice 2 on 2026-07-23. M276 is amended to implement only cleanup,
capability-gated plumbing, Matplotlib rerender evidence, and the caller-owned VisPy2 example. Live
Datoviz capability remains unadvertised, native qualification moves to M284, and M277 may proceed
after the amended slice passes supervisor review.
