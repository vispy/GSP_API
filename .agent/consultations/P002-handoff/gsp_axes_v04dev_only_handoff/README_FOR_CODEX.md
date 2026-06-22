# GSP / VisPy2 Axes Handoff — Datoviz v0.4-dev Only

This package supersedes the earlier `gsp_axes_native_provider_handoff.zip` and `gsp_axes_native_provider_update_2026-06-22.zip`.

The correction is important: for this axes mission, treat `datoviz/datoviz` branch `v0.4-dev` as the only Datoviz source of truth. Do **not** rely on `datoviz.org` pages or v0.3-era Python plotting examples when implementing the GSP Datoviz adapter.

## One-sentence decision

GSP should own semantic `Panel` / `View2D` / `AxisGuide` intent and identity, while each backend selects a capability-declared **axis realization provider**: GSP reference, Matplotlib native, Datoviz v0.4-dev native panel-axis APIs, generated primitives, or a future custom provider.

## Why this zip exists

The first answer assumed Datoviz might need primitive line/text fallback for axes. After checking `datoviz/datoviz` `v0.4-dev`, that assumption must be narrowed:

- Datoviz v0.4-dev is a C-first retained scene / DRP2 / runtime branch, not a v0.3 Python plotting compatibility layer.
- The exported v0.4-dev scene header includes panel data domains, a panel 2D view descriptor, visible data-domain readback, data-to-visual normalization, panel-owned axes, axis visibility, grid visibility, labels, tick policy, style, plot margins, units, and datetime formatting hooks.
- Therefore, the Datoviz backend path should attempt a native axis provider first when its capabilities match the GSP axis intent.
- GSP still must not make Datoviz native ticks or Matplotlib native ticks the protocol specification.

## Read order for the local Codex agent

1. `CODEX_AGENT_REPLY.md` — direct answer/instructions to the local agent.
2. `DATOVIZ_V04DEV_GITHUB_FINDINGS.md` — source-of-truth findings and exact APIs to inspect locally.
3. `UPDATED_ARCHITECTURE_RECOMMENDATION.md` — revised P002 answer in the requested architecture format.
4. `ADR-002-axis-realization-providers-v04dev.md` — ADR draft.
5. `PROVIDER_INTERFACE_SKETCH.md` — provider/capability model.
6. `TASK_PLAN.md` — implementation sequence, likely paths, and stop conditions.
7. `CONFORMANCE_TESTS.md` — small tests to prove the design.
8. `RISKS_AND_STOP_CONDITIONS.md` — what not to overcommit.
9. `SOURCE_NOTES.json` — sources checked and intentionally excluded sources.

## Hard rules for the agent

- Do not append generated axes as ordinary user visuals in `Figure.visuals()`.
- Do not use v0.3-era `panel.axes(...)` examples as implementation authority.
- Do not make Datoviz native auto-tick output the GSP conformance spec.
- Do not make Matplotlib native auto-tick output the GSP conformance spec.
- Do not guess current Datoviz type fields. Inspect the local `v0.4-dev` checkout headers before writing adapter calls.
- Prefer source headers under `include/datoviz/` over docs/spec prose when there is a conflict.
