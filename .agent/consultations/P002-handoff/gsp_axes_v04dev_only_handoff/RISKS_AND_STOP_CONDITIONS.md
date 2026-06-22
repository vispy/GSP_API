# Risks And Stop Conditions

## Risk: v0.3 documentation leakage

Do not implement from old `datoviz.org` v0.3-era pages or examples. They may mention `panel.axes(...)`, but v0.4-dev README says v0.4 is not a compatibility layer for v0.3 Python plotting.

Mitigation:

- Inspect `include/datoviz/` in the local `v0.4-dev` checkout.
- Use generated raw bindings only if they expose the verified C ABI.
- Treat docs/spec prose as secondary to headers and tests.

## Risk: backend-native behavior becomes protocol truth

Matplotlib and Datoviz native axes should realize GSP semantics, not define them.

Mitigation:

- GSP owns `View2D`, `AxisGuide`, and `TickSpec`.
- Providers declare strict versus adapted realization.
- Native auto ticks are adapted unless they are known to implement the selected GSP policy exactly.

## Risk: provider/capability bloat

Axis providers can become too broad too early.

Mitigation:

- Start with linear 2D X/Y only.
- Use a small capability schema.
- Keep log/date/category, legends, colorbars, grids beyond basic axis grid, and general layout out of scope.

## Risk: Datoviz v0.4-dev branch churn

The branch is active. Symbol names or struct fields may change.

Mitigation:

- Name provider `datoviz.v04.panel_axis.wip`.
- Gate capability on actual imported/exported symbols.
- Add local verification tests.
- Fail with diagnostics instead of guessing.

## Risk: query semantics confusion

If guide contributions are queryable, users may hit tick labels when they expected data. If they are not queryable, low-level rendered-scene query is incomplete.

Mitigation:

- Add query scopes.
- Default high-level data picking to `data`.
- Default low-level rendered-scene query to `all-rendered` when supported.
- Return `unsupported` when a provider cannot query guide contributions.

## Hard stop conditions

- Stop if a change appends generated axes into `Figure.visuals()`.
- Stop if Datoviz adapter code calls an API name not present in the local v0.4-dev checkout.
- Stop if strict conformance silently uses backend auto ticks.
- Stop if tests depend on obsolete v0.3 plotting wrappers.
