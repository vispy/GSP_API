This roadmap treats the uploaded self-contained post-S011 prompt as the project source of truth. 

## 1. Recommendation Summary

* **Make `S012` the strict Matplotlib guide/tick reference stage.** This should be the next sequential anchor because it defines the conformance target for semantic axes, ticks, titles, grids, guide queries, and VisPy2 guide APIs.
* **Run Datoviz v0.4 binding evidence work in parallel with `S012`.** GSP_API should collect proof, fake-facade tests, and handoff packets, but must not edit Datoviz or infer behavior from v0.3 APIs.
* **Do not let backend-native auto ticks become the GSP spec.** GSP should own deterministic `auto-linear-nice-v0`; native backends can be strict only when they render exactly requested ticks/labels, otherwise adapted.
* **Delay broad query-scope implementation until one focused consultation.** The future `data`, `guides`, and `all-rendered` scopes need a short ChatGPT Pro consultation before hardening result payload and precedence semantics.
* **Grow VisPy2 only after the semantic guide spine is stable.** Public APIs like `set_xlabel`, `set_ylabel`, `set_title`, explicit ticks, and grid toggles should emit semantic guide objects, not generated visuals.
* **Keep virtual data-source follow-up local and bounded.** Harden tiled-source viewport semantics, manifest validation, fixtures, and queries, but do not add real remote fetch, credentials, prefetch, or plugin loading yet.
* **Build conformance around semantic fixtures first, pixel fixtures second.** Text and tick rendering can be platform-sensitive, so fixture design should prioritize protocol/query semantics and bounded rendered checks.
* **Use Datoviz as a capability-driven flagship backend, not a blocking dependency.** Missing v0.4 Python bindings should produce clean skips and handoff artifacts, not guessed adapter code.
* **Packaging/docs come after the reference/conformance baseline.** Documentation should reflect stable provider/status/query semantics rather than freeze premature API choices.
* **The immediate next mission should be `M012`: deterministic strict tick resolver and guide-provider foundation.**

---

## 2. Stage Roadmap

| Stage ID | Title                                                 | Goal                                                                                                                                              | Depends on                       | Parallelizable?        | Why now                                                                                                                   |
| -------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `S012`   | Matplotlib strict guide/tick provider baseline        | Establish deterministic `AxisGuide`, `TickSpec`, `PanelTextGuide`, and strict Matplotlib guide behavior as the reference/conformance target.      | `S011`, axis-provider proof      | Mostly sequential      | The project needs one strict, testable guide provider before VisPy2 APIs, query scopes, and Datoviz parity can stabilize. |
| `S013`   | VisPy2 semantic guide API growth                      | Add stable high-level APIs for labels, titles, ticks, grid intent, and guide inspection while preserving `Figure.visuals()` as user visuals only. | `S012` core tick/guide semantics | Partly                 | API wrappers can begin after model review, but rendering examples should wait for `S012`/`S013` integration.              |
| `S014`   | Datoviz v0.4 binding evidence and handoff             | Produce a maintained evidence matrix and upstream handoff packet for Python facade/raw gaps.                                                      | Axis-provider proof              | Yes                    | This can run beside Matplotlib work and prevents GSP_API from guessing unavailable Datoviz behavior.                      |
| `S015`   | Unified query scopes and capability semantics         | Define and implement `data`, `guides`, and `all-rendered` query scopes with provider-aware `unsupported` vs `miss` behavior.                      | `S012`; consultation gate        | Partly                 | Guide rendering without guide query semantics will quickly produce ambiguous behavior.                                    |
| `S016`   | Datoviz capability/query parity next pack             | Add skip-clean Datoviz parity tests for DATA coordinates, axes, image contracts, and query binding proof when symbols exist.                      | `S014`, `S015`                   | Partly                 | Datoviz should advance by capability evidence, fake-facade proofs, and clean skips while bindings mature.                 |
| `S017`   | Extension and virtual data-source hardening           | Tighten static extension manifests, tiled-source viewport semantics, and deterministic local materialization/query fixtures.                      | `S011`                           | Yes                    | This work is independent if it avoids real remote fetch, credentials, async cache, and dynamic plugins.                   |
| `S018`   | Conformance fixture and replay harness                | Create durable protocol fixtures, in-process replay, backend conformance matrix, and skip-clean CI expectations.                                  | `S012`, `S015`, `S017`           | Partly                 | Once guides, queries, and tiled-source semantics exist, the project needs stable regression fixtures.                     |
| `S019`   | Packaging, docs, and examples                         | Clarify public import surface, optional backend dependencies, examples, and status docs.                                                          | `S012`, `S013`, `S018`           | Yes, late              | Documentation should describe settled semantics, not provisional implementation details.                                  |
| `S020`   | Remote data and dynamic extension security pre-design | Prepare a security ADR/consultation before any real HTTP/S3/GCS/Zarr/OME-Zarr/COG/map-tile or plugin loading work.                                | `S017`                           | No, consultation-gated | The current extension proof explicitly excludes production remote fetch and plugin loading.                               |

---

## 3. Mission Batch

| Mission ID |  Stage | Title                                                 | Goal                                                                                                                          | Agent type                 | Priority | Dependencies                | Stop conditions                                                                                                             |
| ---------- | -----: | ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | -------------------------- | -------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `M012`     | `S012` | Strict tick resolver and guide-provider foundation    | Add deterministic `auto-linear-nice-v0` resolution and protocol/reference tests for strict guide intent.                      | `local-main-codex`         | P0       | `S011`, axis-provider proof | Stop if `TickSpec`/guide schema requires an ADR-level change or if generated guides would need to enter `Figure.visuals()`. |
| `M013`     | `S012` | Matplotlib `AxisGuide` and `PanelTextGuide` rendering | Render x/y guides, labels, grids, explicit ticks, auto ticks, and title from semantic guide objects.                          | `codex-worker`             | P0       | `M012`                      | Stop if implementation depends on Matplotlib native locator output as conformance truth.                                    |
| `M014`     | `S012` | Reference guide query support                         | Add guide-scoped query behavior for providers that support guide queries; return `unsupported`, not `miss`, when unavailable. | `local-main-codex`         | P0       | `M012`, `M013`              | Stop if query payload/result shape needs broader query-scope architecture.                                                  |
| `M015`     | `S012` | Guide conformance fixtures                            | Add deterministic fixtures for explicit ticks, auto ticks, guide labels, grids, titles, and unsupported guide queries.        | `claude-worker`            | P0       | `M012`-`M014`               | Stop if rendered output is platform-flaky and cannot be checked semantically.                                               |
| `M016`     | `S013` | VisPy2 label/title/tick/grid APIs                     | Implement public guide APIs that emit semantic `AxisGuide`, `TickSpec`, and `PanelTextGuide` intent.                          | `codex-worker`             | P1       | `M012`                      | Stop if an API would expose backend-provider details or mutate user visual lists.                                           |
| `M017`     | `S013` | VisPy2 examples and guide API tests                   | Add examples/tests for scatter, image, limits, labels, title, ticks, grid, and semantic structure inspection.                 | `claude-worker`            | P1       | `M016`, `M013`              | Stop if public API names are still under architecture review.                                                               |
| `M018`     | `S014` | Datoviz v0.4 header/binding evidence refresh          | Create/update evidence scripts and reports for verified v0.4-dev headers vs installed Python binding exposure.                | `codex-worker`             | P0       | Axis-provider proof         | Stop if local checkout is unavailable; record that as evidence instead of guessing.                                         |
| `M019`     | `S014` | Datoviz Python facade handoff packet                  | Produce a focused Datoviz-side handoff request with symbol matrix, behavior asks, and minimal examples.                       | `human-review`             | P0       | `M018`                      | Stop before editing the external Datoviz repository.                                                                        |
| `M020`     | `S014` | Datoviz fake-facade contract next pack                | Expand fake-facade tests for panel domain/view2d, axes, image field contract, and capability gates.                           | `codex-worker`             | P1       | `M018`                      | Stop if tests assert symbols not verified in v0.4-dev headers or injected fake facade.                                      |
| `M021`     | `S015` | Query scope semantics consultation                    | Ask ChatGPT Pro to decide `data`, `guides`, `all-rendered` precedence, payload shape, and capability declarations.            | `chatgpt-pro-consultation` | P0       | `M014` findings             | Stop until the prompt is self-contained and accepted.                                                                       |
| `M022`     | `S015` | Query scope protocol hardening                        | Add scope enum/model/capability updates while preserving existing query statuses and modes.                                   | `local-main-codex`         | P0       | `M021`                      | Stop if backward compatibility with existing query fixtures breaks unexpectedly.                                            |
| `M023`     | `S015` | Reference query implementation and fixtures           | Implement Matplotlib/reference behavior for data, guides, and all-rendered scopes where supported.                            | `codex-worker`             | P1       | `M022`, `M014`              | Stop if guide query behavior cannot distinguish `unsupported` from `miss`.                                                  |
| `M024`     | `S016` | Datoviz DATA coordinate-space parity proof            | Add a Datoviz DATA-coordinate proof using only verified v0.4 panel/domain/transform symbols.                                  | `codex-worker`             | P1       | `M018`, `M020`              | Stop if Python binding lacks required symbols; produce skip-clean evidence.                                                 |
| `M025`     | `S016` | Datoviz query binding decoder proof                   | Decode `DvzQueryResult` only if accessible through v0.4 Python facade/raw bindings or injected fake facade.                   | `codex-worker`             | P1       | `M018`, `M022`              | Stop if installed package lacks raw/facade query symbols.                                                                   |
| `M026`     | `S016` | Datoviz capability parity declaration audit           | Ensure Datoviz capabilities report strict/adapted/experimental/unsupported based only on actual symbol exposure.              | `claude-worker`            | P1       | `M020`, `M024`, `M025`      | Stop if any capability would be inferred from docs or desired behavior rather than binding evidence.                        |
| `M027`     | `S017` | Tiled-source viewport semantics hardening             | Tighten deterministic local tiled-source viewport selection, edge handling, and query payload behavior.                       | `local-main-codex`         | P1       | `S011`                      | Stop if real network, credentials, cache eviction, prefetch, or retry semantics become necessary.                           |
| `M028`     | `S017` | Static extension manifest validation                  | Validate manifest IDs, versions, capabilities, and extension-source linkage without dynamic plugin loading.                   | `codex-worker`             | P1       | `S011`, optional `M027`     | Stop if implementation implies plugin discovery/loading.                                                                    |
| `M029`     | `S018` | Golden protocol fixture and replay harness            | Add durable JSON fixtures and in-process replay for points, images, guides, queries, and tiled-source scenes.                 | `local-main-codex`         | P0       | `M015`, `M022`, `M027`      | Stop if fixture format starts becoming protocol authority without spec text.                                                |
| `M030`     | `S018` | Backend conformance matrix and skip-clean tests       | Add conformance matrix for Matplotlib strict, Datoviz experimental/adapted/unsupported, and extension features.               | `claude-worker`            | P1       | `M029`, `M020`              | Stop if CI would fail solely because v0.4 Datoviz Python bindings are unavailable.                                          |
| `M031`     | `S019` | Packaging and import-surface audit                    | Verify package metadata, optional dependencies, public exports, test commands, and backend import failure behavior.           | `claude-worker`            | P1       | `M016`, `M029`              | Stop if versioning/release policy is unresolved.                                                                            |
| `M032`     | `S019` | Example gallery refresh                               | Add small examples for Matplotlib rendering, guide APIs, queries, and local tiled-source proof.                               | `codex-worker`             | P2       | `M017`, `M027`, `M029`      | Stop if examples require Datoviz local checkout or unavailable v0.4 bindings.                                               |
| `M033`     | `S020` | Remote data and dynamic extension security ADR prompt | Prepare a ChatGPT Pro prompt for security model before remote sources or plugin loading.                                      | `chatgpt-pro-consultation` | P2       | `M027`, `M028`              | Stop before implementation of any real remote fetch, credentials, or dynamic loading.                                       |

---

## 4. Immediate Next Mission Packet

### Mission

`M012 — Strict tick resolver and guide-provider foundation`

### Goal

Implement the deterministic reference foundation for semantic guide/tick realization:

* `auto-linear-nice-v0` tick resolution;
* explicit tick pass-through semantics;
* protocol/reference tests for strict guide intent;
* Matplotlib strict-provider readiness without relying on Matplotlib native locator output;
* preservation of the invariant that generated guides/axes are not appended to `Figure.visuals()`.

This mission should prepare `M013` to perform actual Matplotlib guide/title/grid rendering.

### Required reading

* Uploaded post-S011 roadmap prompt.
* `adr/ADR-0005-axis-realization-providers-v04dev.md`
* `src/gsp/protocol/panels.py`
* `src/gsp/protocol/guides.py`
* `src/gsp/protocol/capabilities.py`
* `src/gsp_matplotlib/capabilities.py`
* `src/gsp_datoviz/capabilities.py`
* `src/gsp_datoviz/protocol_renderer.py`
* `src/vispy2/protocol.py`
* `tests/test_axis_provider_capabilities.py`
* `tests/test_vispy2_protocol_mvp.py`
* `tests/test_datoviz_v04_protocol_renderer.py`

### Expected tasks

1. Inspect current `Panel`, `View2D`, `AxisGuide`, `TickSpec`, and provider capability models.
2. Add a small pure-Python deterministic tick resolver for `auto-linear-nice-v0`.

   * Prefer a protocol/reference location such as `src/gsp/protocol/ticks.py` if that matches the existing package structure.
   * Keep it backend-independent.
3. Define resolver behavior for:

   * normal increasing linear limits;
   * reversed limits, if current `View2D` allows them;
   * degenerate limits;
   * explicit ticks and labels;
   * invalid/non-finite limits.
4. Add tests proving that auto ticks are deterministic and not delegated to Matplotlib locators.
5. Add tests proving explicit tick values and labels are preserved exactly at the protocol/reference layer.
6. Add tests that guide/tick preparation does not mutate `Figure.visuals()`.
7. Confirm Matplotlib capability declaration remains strict only for semantics it can support.
8. Confirm Datoviz capability behavior is unchanged unless exposed symbols justify changes.
9. Add or update minimal spec notes if the resolver behavior needs durable explanation.

### Allowed paths

* `src/gsp/protocol/**`
* `src/gsp_matplotlib/**`
* `src/vispy2/**`, only for tests or minimal integration required to preserve current invariants
* `tests/**`
* `spec/**`, only for brief resolver/fixture notes
* `adr/**`, only if a minor addendum is clearly needed
* `.agent/tasks/**` and `.agent/missions/**`, if Mission Control wants task tracking committed with the implementation

### Forbidden paths

* No edits to external Datoviz repositories.
* No reliance on Datoviz v0.3 plotting APIs or old `panel.axes(...)` examples.
* No use of Matplotlib native auto tick output as the GSP conformance definition.
* No appending generated axes, guides, ticks, labels, or titles to `Figure.visuals()`.
* No real HTTP/S3/GCS/Zarr/OME-Zarr/COG/map-tile clients.
* No credential, cache, retry, prefetch, progressive loading, or plugin-loading work.
* No force-push, merge-to-main, or external repository modification.

### Acceptance criteria

* A deterministic `auto-linear-nice-v0` resolver exists and is covered by unit tests.
* Explicit ticks and labels are preserved exactly through the protocol/reference layer.
* Auto tick fixtures are stable across test runs and do not depend on Matplotlib locators.
* Existing point/image/query/VisPy2 MVP tests still pass.
* `Figure.visuals()` continues to return user data visuals only.
* Matplotlib remains declared strict only for the current semantic slice.
* Datoviz behavior remains provider-gated and skip-clean when v0.4 bindings are unavailable.
* No unverified Datoviz API names or v0.3 plotting APIs are introduced.

### Tests to run

At minimum:

```bash
PYTHONPATH=. uv run pytest tests/test_axis_provider_capabilities.py
PYTHONPATH=. uv run pytest tests/test_vispy2_protocol_mvp.py
PYTHONPATH=. uv run pytest tests/test_datoviz_v04_protocol_renderer.py
PYTHONPATH=. uv run pytest
```

Add focused tests for the new resolver, for example:

```bash
PYTHONPATH=. uv run pytest tests/test_tick_resolver.py
```

Use the project’s actual test filename if a different convention already exists.

### Stop conditions

Stop and create a review note instead of forcing implementation if:

* `TickSpec` lacks enough information to distinguish explicit ticks from auto resolver requests.
* `AxisGuide` lacks required orientation/side/domain linkage and fixing it would be an ADR-level model change.
* Correct behavior would require making Matplotlib native locator output normative.
* The implementation would append generated guide/tick/title objects into `Figure.visuals()`.
* Datoviz capability changes would require guessing behavior from unavailable Python bindings.
* Tests become platform-dependent pixel comparisons rather than semantic checks.

### Review checklist

* Does the implementation preserve GSP as the semantic protocol authority?
* Are auto ticks generated by GSP/reference code, not by Matplotlib locators?
* Are explicit ticks and labels exact?
* Are guide/tick/title objects separate from user data visuals?
* Are capability declarations still honest?
* Are Datoviz tests skip-clean when v0.4 Python symbols are absent?
* Are no v0.3 Datoviz APIs or external docs used?
* Are tests small, deterministic, and appropriate for local Codex execution?

---

## 5. Task Files To Create

| Task file                                              | Mission | Summary                                                                   | Dependencies            | Acceptance criteria                                               |
| ------------------------------------------------------ | ------: | ------------------------------------------------------------------------- | ----------------------- | ----------------------------------------------------------------- |
| `.agent/tasks/M012-MPL-STRICT-TICKS.md`                |  `M012` | Implement deterministic `auto-linear-nice-v0` resolver.                   | `S011`                  | Resolver is backend-independent, tested, and stable.              |
| `.agent/tasks/M012-EXPLICIT-TICK-PASSTHROUGH.md`       |  `M012` | Preserve explicit tick values/labels exactly at protocol/reference layer. | `M012-MPL-STRICT-TICKS` | Tests prove exact values and labels survive unchanged.            |
| `.agent/tasks/M012-GUIDE-VISUALS-INVARIANT.md`         |  `M012` | Add tests that generated guides do not enter `Figure.visuals()`.          | Existing VisPy2 MVP     | User visuals remain points/images only.                           |
| `.agent/tasks/M013-MPL-AXISGUIDE-RENDER.md`            |  `M013` | Render semantic x/y axis guides in Matplotlib.                            | `M012`                  | Labels, ticks, and guide visibility come from semantic models.    |
| `.agent/tasks/M013-MPL-PANELTEXTGUIDE-TITLE.md`        |  `M013` | Render semantic panel title/text guide.                                   | `M012`                  | Title rendering is semantic and tested.                           |
| `.agent/tasks/M013-MPL-GRID-SEMANTICS.md`              |  `M013` | Render grid intent from `AxisGuide`.                                      | `M012`                  | Grid state is controlled by semantic guide config.                |
| `.agent/tasks/M014-GUIDE-QUERY-SUPPORT.md`             |  `M014` | Add guide-scoped query behavior for supported providers.                  | `M013`                  | Unsupported guide queries return `unsupported`, not `miss`.       |
| `.agent/tasks/M015-GUIDE-CONFORMANCE-FIXTURES.md`      |  `M015` | Add guide/tick/title conformance fixtures.                                | `M012`-`M014`           | Fixtures are deterministic and backend-classified.                |
| `.agent/tasks/M016-VISPY2-LABEL-TITLE-API.md`          |  `M016` | Add `set_xlabel`, `set_ylabel`, and `set_title` style APIs.               | `M012`                  | APIs create semantic guide/text objects.                          |
| `.agent/tasks/M016-VISPY2-TICKS-GRID-API.md`           |  `M016` | Add explicit tick and grid APIs.                                          | `M012`                  | APIs emit `TickSpec`/guide intent without backend leakage.        |
| `.agent/tasks/M017-VISPY2-GUIDE-EXAMPLES.md`           |  `M017` | Add examples for labels, titles, ticks, grid, and limits.                 | `M016`, `M013`          | Examples run with Matplotlib reference backend.                   |
| `.agent/tasks/M018-DATOVIZ-V04-BINDING-EVIDENCE.md`    |  `M018` | Script/report verified v0.4 headers vs Python binding exposure.           | Axis-provider proof     | Evidence matrix records present/missing symbols.                  |
| `.agent/tasks/M019-DATOVIZ-HANDOFF-PACKET.md`          |  `M019` | Prepare Datoviz-side Python facade/raw binding request.                   | `M018`                  | Handoff is specific, minimal, and externally reviewable.          |
| `.agent/tasks/M020-DATOVIZ-FAKE-FACADE-CONTRACT.md`    |  `M020` | Expand fake-facade tests for v0.4 axes/view2d/image/query symbols.        | `M018`                  | Tests only use verified or fake-injected symbols.                 |
| `.agent/tasks/M021-QUERY-SCOPE-CONSULTATION-PROMPT.md` |  `M021` | Write self-contained ChatGPT Pro prompt for query scopes.                 | `M014`                  | Prompt asks exact questions on scope, precedence, payloads, caps. |
| `.agent/tasks/M022-QUERY-SCOPE-PROTOCOL.md`            |  `M022` | Implement accepted query scope model changes.                             | `M021`                  | Existing query statuses remain compatible.                        |
| `.agent/tasks/M023-REFERENCE-QUERY-FIXTURES.md`        |  `M023` | Add Matplotlib/reference query fixtures for data/guides/all-rendered.     | `M022`                  | Fixtures distinguish hit/miss/outside/unsupported.                |
| `.agent/tasks/M027-TILED-SOURCE-VIEWPORT-SEMANTICS.md` |  `M027` | Harden deterministic local tiled-source viewport selection.               | `S011`                  | Edge cases and query payloads are tested.                         |
| `.agent/tasks/M028-EXTENSION-MANIFEST-VALIDATION.md`   |  `M028` | Validate static manifests, versions, capabilities, and source linkage.    | `S011`                  | No dynamic plugin loading is introduced.                          |
| `.agent/tasks/M029-GOLDEN-REPLAY-HARNESS.md`           |  `M029` | Add protocol fixture and in-process replay harness.                       | `M015`, `M022`, `M027`  | Replay works without JSON/base64 requirement for local path.      |
| `.agent/tasks/M030-CONFORMANCE-MATRIX.md`              |  `M030` | Maintain backend conformance/skip matrix.                                 | `M029`, `M020`          | Matplotlib strict and Datoviz skip/adapted states are explicit.   |
| `.agent/tasks/M031-PACKAGING-IMPORT-AUDIT.md`          |  `M031` | Audit package metadata, exports, optional backend imports.                | `M029`                  | Imports fail gracefully when optional backends are absent.        |
| `.agent/tasks/M033-REMOTE-SECURITY-ADR-PROMPT.md`      |  `M033` | Prepare security consultation before remote sources/plugins.              | `M027`, `M028`          | No implementation begins before ADR acceptance.                   |

---

## 6. Datoviz Handoff Plan

### Keep in GSP_API

* Capability declarations and provider selection logic.
* Fake-facade tests for verified v0.4-dev symbol names.
* Skip-clean tests when installed Python `datoviz` lacks v0.4 facade/raw symbols.
* Protocol-side adaptation decisions.
* Matplotlib/reference conformance fixtures.
* Datoviz adapter guards that only enable features when symbols are actually exposed.
* Evidence documents under `.agent/`, `spec/`, or handoff notes.
* Tests proving explicit strict GSP ticks are rejected or marked adapted/unsupported when Datoviz cannot accept explicit tick values through the available binding.

### Handoff to Datoviz

Ask Datoviz to expose or confirm Python bindings for the verified v0.4-dev surface, especially:

* panel domain/view APIs:

  * `panel_set_domain`
  * `panel_view2d`
  * `panel_set_view2d`
  * `panel_view2d_extent`
  * `panel_visible_domain`
  * `panel_data_to_visual_positions`
* panel axis APIs:

  * `panel_axis`
  * `axis_tick_policy`
  * `axis_style`
  * `axis_set_visible`
  * `axis_set_grid`
  * `axis_set_label`
  * `axis_set_tick_policy`
  * `axis_set_style`
  * `axis_set_plot_margins`
  * `axis_set_units`
  * `axis_set_datetime`
* constants and structs:

  * `DVZ_DIM_X`
  * `DVZ_DIM_Y`
  * `DvzPanelView2D`
  * `DvzAxisTickPolicy`
  * `DvzAxisStyle`
  * `DvzQueryResult`
* query lifecycle:

  * how query requests are submitted;
  * whether results are synchronous/asynchronous;
  * how stale/dropped/failed states should be detected;
  * coordinate spaces for returned hits;
  * object/visual identifiers returned by query results.

### Evidence to collect

* Datoviz checkout branch and commit hash.
* Header paths inspected.
* Exact grep output for each required symbol.
* Python introspection output for the installed `datoviz` package.
* Whether `datoviz.raw` imports.
* Whether facade symbols are exposed directly.
* Minimal fake-facade call traces proving GSP_API uses only verified names.
* A table mapping each GSP feature to:

  * required Datoviz symbol;
  * header evidence;
  * Python binding exposure;
  * GSP capability status;
  * test file covering it.

### Do not implement in GSP_API

* Do not edit the Datoviz repository.
* Do not vendor Datoviz headers or bindings.
* Do not build a private ctypes/cffi shim around unreviewed internal libraries.
* Do not rely on Datoviz v0.3 plotting APIs.
* Do not use `datoviz.org` v0.3-era examples as implementation authority.
* Do not claim strict tick support unless explicit tick values and labels can be rendered exactly.
* Do not make backend auto ticks a conformance target.
* Do not make Datoviz availability mandatory for CI.
* Do not block Matplotlib/reference progress on Datoviz binding availability.

---

## 7. Conformance Plan

### Protocol model tests

Add tests for:

* stable IDs for panels, views, guides, visual attachments, and text guides;
* `Panel` / `View2D` / `VisualAttachment` consistency;
* `AxisGuide` orientation, visibility, label, grid, and tick intent;
* `PanelTextGuide` title/text semantics;
* explicit tick value/label validation;
* `auto-linear-nice-v0` deterministic output;
* provider status semantics: `strict`, `adapted`, `experimental`, `unsupported`;
* capability snapshots for guide rendering and guide query support;
* invariant that generated guides are not user visuals.

### Matplotlib reference tests

Add tests for:

* strict explicit tick rendering;
* strict explicit tick label rendering;
* deterministic auto tick rendering from GSP resolver;
* `View2D` x/y limit honoring with guides enabled;
* x/y label rendering;
* panel title rendering;
* grid visibility;
* point and image rendering still working with guides present;
* optional guide query support if implemented;
* non-conformance/adapted mode, if Matplotlib native locators are left active intentionally.

### Datoviz skip-clean tests

Add tests for:

* no v0.4 symbols: provider remains unsupported or unavailable;
* fake v0.4 facade symbols present: provider advertises only the supported experimental/adapted slice;
* explicit strict ticks rejected or adapted when explicit tick support is unavailable;
* `panel_set_domain`, `panel_set_view2d`, `panel_axis`, and axis label calls use verified symbol names only;
* query decoder tests skip cleanly when raw/facade query symbols are absent;
* no v0.3 plotting APIs are referenced.

### Query tests

Add tests for:

* existing statuses: `hit`, `miss`, `outside-panel`, `unsupported`, `stale`, `dropped`, `failed`;
* existing modes: `panel-query`, `point-item`, `image-texel`;
* new scopes after consultation: `data`, `guides`, `all-rendered`;
* guide query unsupported behavior;
* guide query hit behavior where provider supports it;
* all-rendered precedence rules once accepted;
* stale/dropped/failed propagation;
* tiled-image query payload compatibility with normal `QueryResult`.

### Guide/tick tests

Add fixtures for:

* explicit linear ticks with labels;
* explicit ticks without labels;
* auto-linear-nice ticks over small, large, negative, positive, and crossing-zero domains;
* degenerate or near-degenerate domains;
* reversed domains, if supported;
* x-only guide;
* y-only guide;
* both guides;
* grid on/off;
* empty label vs missing label;
* title present/absent.

### Tiled-source tests

Add tests for:

* deterministic viewport-to-tile selection;
* edge tiles and partial coverage;
* stable synthetic/in-memory materialization;
* query payloads for tiled-image results;
* extension manifest linkage to `gsp.tiled-image@0.1`;
* no remote fetch;
* no credentials;
* no dynamic plugin loading.

---

## 8. Risks And Stop Conditions

| Risk                                                  | Stop condition                                                                                                                            |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Protocol authority drifts into backend implementation | Stop when Matplotlib, Datoviz, or existing code behavior starts defining protocol semantics without spec/ADR support.                     |
| Matplotlib native ticks become normative              | Stop if tests compare against Matplotlib locator output rather than GSP `auto-linear-nice-v0` or explicit ticks.                          |
| Generated guides become user visuals                  | Stop if implementation appends axes, ticks, grid lines, labels, or titles to `Figure.visuals()`.                                          |
| Datoviz v0.4 binding gaps cause guessed code          | Stop if a worker needs a symbol that is not present in installed Python bindings or fake-facade tests. Create a handoff artifact instead. |
| v0.3 Datoviz API contamination                        | Stop if implementation references old v0.3 plotting examples, including old `panel.axes(...)` style usage.                                |
| Query semantics become ambiguous                      | Stop before implementing `data`, `guides`, or `all-rendered` if precedence or payload shape is unclear. Use `M021`.                       |
| Remote data scope creep                               | Stop if a tiled-source task needs real network fetch, credentials, retry, cache eviction, prefetch, or progressive loading.               |
| Extension security boundary is crossed                | Stop if static manifest validation turns into dynamic plugin loading. Use `M033`.                                                         |
| Pixel conformance becomes flaky                       | Stop if fixture checks fail due to font/platform/antialiasing differences and convert the fixture to semantic/query checks.               |
| Public VisPy2 API leaks provider details              | Stop if user-facing API requires selecting Matplotlib or Datoviz provider IDs directly for ordinary usage.                                |
| Capability declarations become aspirational           | Stop if a backend advertises strict support without exact behavior and tests.                                                             |
| Worker mission grows unbounded                        | Stop if a mission touches more than one stage’s architectural scope without explicit Mission Control approval.                            |

---

## 9. ChatGPT Pro Follow-Up Triggers

Use ChatGPT Pro again before implementing any of these:

1. **Unified query scopes.**
   Exact question: “Define GSP query scope semantics for `data`, `guides`, and `all-rendered`, including precedence, payload shape, provider capabilities, and status behavior.”

2. **Remote virtual data sources.**
   Exact question: “Design the security and capability model for real HTTP/S3/GCS/Zarr/OME-Zarr/COG/map-tile sources, including credentials, provenance, caching, and failure semantics.”

3. **Dynamic extension loading.**
   Exact question: “Define a safe extension loading model for GSP, including manifest trust, version negotiation, sandboxing, and capability discovery.”

4. **Datoviz query lifecycle after bindings appear.**
   Exact question: “Map Datoviz v0.4 query results and lifecycle to GSP `QueryResult` statuses, scopes, IDs, stale/dropped behavior, and coordinate spaces.”

5. **Nonlinear or nonnumeric axes.**
   Exact question: “Extend `AxisGuide`, `TickSpec`, and `View2D` semantics for log, datetime, categorical, or transformed axes without making backend-native locators normative.”

6. **Text and guide conformance policy.**
   Exact question: “Define a conformance strategy for rendered text, ticks, labels, and grids that balances semantic exactness with font/platform variability.”

7. **VisPy2 public API expansion beyond Matplotlib-like basics.**
   Exact question: “Design VisPy2’s stable guide/layout/query API surface while keeping GSP backend-independent and provider-capability-driven.”

8. **Extension version negotiation beyond static manifests.**
   Exact question: “Define extension compatibility, version ranges, feature flags, and deprecation behavior for manifest-driven GSP extensions.”

Safe for local Codex or worker agents without further consultation:

* `M012` deterministic tick resolver;
* `M013` Matplotlib semantic guide rendering;
* `M015` guide fixtures after `M012`/`M013`;
* `M016` basic VisPy2 label/title/tick/grid APIs after semantic model is stable;
* `M018` Datoviz evidence refresh;
* `M019` handoff packet drafting;
* `M020` fake-facade tests;
* `M027` local-only tiled-source hardening;
* `M028` static manifest validation;
* `M029` replay harness after fixture model is clear;
* `M031` packaging/import audit;
* `M032` examples that avoid unavailable Datoviz bindings.

---

## 10. Mission Control Update Suggestions

### `.agent/status.json`

Update to include:

* current completed state through `S011`;
* recent follow-up commits noted as completed context;
* next active mission: `M012`;
* queued missions: `M013` through `M033`;
* stage list: `S012` through `S020`;
* backend status summary:

  * Matplotlib: strict reference backend, guide work pending;
  * Datoviz: v0.4-dev flagship backend, Python binding gaps, provider-gated;
  * VisPy2: MVP complete, guide API pending;
  * Extensions: static manifest/tiled-source proof complete, hardening pending.

### `.agent/missions/*.md`

Create mission files:

* `.agent/missions/M012-strict-tick-resolver-guide-foundation.md`
* `.agent/missions/M013-matplotlib-axisguide-paneltextguide-rendering.md`
* `.agent/missions/M014-reference-guide-query-support.md`
* `.agent/missions/M015-guide-conformance-fixtures.md`
* `.agent/missions/M016-vispy2-guide-api-growth.md`
* `.agent/missions/M017-vispy2-guide-examples-tests.md`
* `.agent/missions/M018-datoviz-v04-binding-evidence-refresh.md`
* `.agent/missions/M019-datoviz-python-facade-handoff.md`
* `.agent/missions/M020-datoviz-fake-facade-contract-next-pack.md`
* `.agent/missions/M021-query-scope-semantics-consultation.md`
* `.agent/missions/M022-query-scope-protocol-hardening.md`
* `.agent/missions/M023-reference-query-fixtures.md`
* `.agent/missions/M024-datoviz-data-coordinate-parity-proof.md`
* `.agent/missions/M025-datoviz-query-binding-decoder-proof.md`
* `.agent/missions/M026-datoviz-capability-parity-audit.md`
* `.agent/missions/M027-tiled-source-viewport-semantics-hardening.md`
* `.agent/missions/M028-extension-manifest-validation.md`
* `.agent/missions/M029-golden-protocol-replay-harness.md`
* `.agent/missions/M030-backend-conformance-matrix.md`
* `.agent/missions/M031-packaging-import-surface-audit.md`
* `.agent/missions/M032-example-gallery-refresh.md`
* `.agent/missions/M033-remote-extension-security-adr-consultation.md`

### `.agent/tasks/*.md`

Create the task files listed in section 5, with dependencies and acceptance criteria copied into each task file.

### `STATUS.md`

Update after acceptance with:

* “Post-S011 roadmap accepted.”
* “Next mission: `M012 — Strict tick resolver and guide-provider foundation`.”
* “Primary current priority: Matplotlib strict guide/tick reference provider.”
* “Parallel current priority: Datoviz v0.4 Python binding evidence and handoff.”
* “Consultation gates: query scopes, remote data security, dynamic extension loading.”

### Specs and ADRs

Likely additions or updates:

* `spec/axis-guides.md` or equivalent: deterministic tick resolver and guide-provider behavior.
* `spec/query-scopes.md`: after `M021`.
* `spec/conformance-fixtures.md`: fixture/replay rules.
* `spec/extensions.md`: static manifest validation updates.
* `adr/ADR-0006-query-scope-semantics.md`: after `M021`, if accepted.
* `adr/ADR-0007-remote-data-extension-security.md`: before any remote fetch or plugin loading work.
