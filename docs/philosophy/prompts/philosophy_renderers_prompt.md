## Prompt
i would like to generate a documentation on renderers. put the result in ./docs/philosophy/philosophy_renderers.md
- gsp_datoviz
- gsp_network
- gsp_matplotlib

- study how they are implemented
- extract common pattern
- describe how to write a new renders

## Plan

---

# Plan — `philosophy_renderers.md`

## Context

The user is writing a "Philosophy of GSP_API" series of design documents, sibling to the already-shipped [philosophy_packages.md](../../Users/jetienne/work/GSP_API/docs/philosophy/philosophy_packages.md) and [philosophy_examples.md](../../Users/jetienne/work/GSP_API/docs/philosophy/philosophy_examples.md). The next instalment is about **renderers** — the three concrete backends shipped today (`gsp_matplotlib`, `gsp_datoviz`, `gsp_network`). The prompt file [philosophy_renderers_prompt.md](../../Users/jetienne/work/GSP_API/docs/philosophy/philosophy_renderers_prompt.md) is empty apart from the user's instruction:

> study how they are implemented · extract common pattern · describe how to write a new renderer

Output target: `docs/philosophy/philosophy_renderers.md` (note: prompt says `philosophy_rendererd.md` — clearly a typo; we'll write to `philosophy_renderers.md` and confirm with the user via AskUserQuestion if there's any doubt).

The audience is the same as the other philosophy docs: a developer reading the codebase to learn it, or someone about to write a fourth backend (e.g. `gsp_webgpu`, `gsp_three`, `gsp_plotly`). The doc should encode the **conventions** that turn three independent packages into a coherent backend ecosystem — not re-document each renderer end-to-end.

## What the exploration uncovered (input to the design)

The three renderer packages are **structurally identical**. Same subdirectory layout, same registration shape, same `RendererBase` contract, same per-visual file fan-out, same isinstance dispatch, same animator/events triad. The differences are local — what each renderer does *inside* `_render_visual()` and how it implements `show()`.

Key shared facts (all verified against the code):

| Concern | Shared contract | File |
|---|---|---|
| Renderer interface | `RendererBase` (ABC: `__init__(canvas)`, `render(...)`, `show()`, `close()`, `clear()`, `get_canvas()`) | [src/gsp/types/renderer_base.py](../../Users/jetienne/work/GSP_API/src/gsp/types/renderer_base.py) |
| Animator interface | `AnimatorBase` (ABC: `add_callback`, `event_listener`, `start`, `stop`, `on_video_saved`) | [src/gsp/types/animator_base.py](../../Users/jetienne/work/GSP_API/src/gsp/types/animator_base.py) |
| Events interface | `ViewportEventsBase` (ABC: 7 named `Event[...]` slots) | [src/gsp/types/viewport_events_base.py](../../Users/jetienne/work/GSP_API/src/gsp/types/viewport_events_base.py) |
| Discovery | `RendererRegistry` (dict keyed by name → `(renderer, events, animator)` triad) | [src/gsp/utils/renderer_registery.py](../../Users/jetienne/work/GSP_API/src/gsp/utils/renderer_registery.py) |
| Per-package wiring | `register_renderer_<name>()` called from `__init__.py` at import time | each package's `renderer_registration.py` |

The **per-visual renderer fan-out** is the second strong convention: each package's `renderer/` subdirectory contains exactly one main renderer + one file per visual type (`*_image.py`, `*_markers.py`, `*_mesh.py`, `*_paths.py`, `*_pixels.py`, `*_points.py`, `*_segments.py`, `*_texts.py`). Verified — both `gsp_datoviz/renderer/` and `gsp_matplotlib/renderer/` ship exactly the same eight visual files. Each is a static class with a single `render(renderer, viewport, visual, model_matrix, camera)` method. Dispatch is a hand-written `isinstance` chain in `_render_visual()`, not a registry — pragmatic for a small fixed visual set.

The **divergences** worth naming as "this is renderer-specific, copy with care":

- **MatplotlibRenderer** — Figure/Axes lifecycle, lazy axes-per-viewport caching, `image_format` parameter on `render()` enables PNG/SVG/PDF/JPG via `figure.savefig(format=...)`.
- **DatovizRenderer** — `dvz.App` + `dvz_figure` + lazily-created `dvz_panel` per viewport; create-once-update-always GPU resources cached in `_dvz_visuals`; CPU-side MVP transform before sending vertices to datoviz; Y-axis flip (datoviz top-left vs GSP bottom-left); offscreen mode required for screenshot capture.
- **NetworkRenderer** — Zero local dispatch. Whole scene serialised via `PydanticSerializer`, POSTed as JSON to `/render`, response is PNG bytes decoded into a local matplotlib figure for display. The server (`src/gsp_network/tools/network_server.py`) instantiates a real `MatplotlibRenderer` or `DatovizRenderer(offscreen=True)` based on the `renderer_name` field in the payload. Client-side input events (mouse, keyboard) **do not** propagate to the server — interaction is local.

## Document outline (what gets written to `docs/philosophy/philosophy_renderers.md`)

The doc will mirror the section style of [philosophy_examples.md](../../Users/jetienne/work/GSP_API/docs/philosophy/philosophy_examples.md): numbered sections, one canonical snippet per pattern, file/line citations everywhere, and a closing "verification" section so the reader can ground every claim in the code.

### 1. Preamble
One paragraph: "Three renderer packages, one shape." Frame the doc as *what is shared* (the 95%) followed by *what each backend does differently*, capped with a "write your own" walkthrough. Audience: someone reading a renderer to learn it, or someone writing a fourth.

### 2. The Five Design Principles
Borrow the structure from `philosophy_examples.md` §2. Five principles:

1. **One interface, three backends.** The `RendererBase` ABC is the contract; everything else is registration. → cite `src/gsp/types/renderer_base.py:15-74`.
2. **The three-fold triad.** A renderer never ships alone — it always comes with a paired `ViewportEventsBase` and `AnimatorBase`. The registry stores them as a `RendererRegistryItem` triad (`src/gsp/utils/renderer_registery.py:14-21`). The reason: events and animators are renderer-specific (they hook into matplotlib's `mpl_connect`, datoviz's timer, or — for network — the local matplotlib loop), so they must be co-versioned with the renderer.
3. **Self-registration on import.** Each package's `__init__.py` calls `register_renderer_<name>()` at import time. The user installs `gsp_matplotlib` and the name `"matplotlib"` simply *exists* in the registry. No central manifest. → cite each `renderer_registration.py:10-17`.
4. **Static-class dispatch, not a plugin registry.** Per-visual rendering is a hand-written `isinstance` chain in `_render_visual()`, dispatching to a static class with a single `render(renderer, viewport, visual, model_matrix, camera)` method. Eight visual types today; eight `if/elif` arms. The cost of a registry isn't worth paying yet.
5. **Bytes out, not pixels out.** Every `render()` returns `bytes` — PNG by default, but `image_format` lets matplotlib emit SVG/PDF, and the network renderer literally ships those bytes over HTTP. The unified return type is what makes `NetworkRenderer` possible without changing any caller.

### 3. The Canonical Package Skeleton
A walkthrough of "what every renderer package looks like on disk." Use `gsp_matplotlib/` as the reference, with side-by-side `gsp_datoviz/` and `gsp_network/` parallels in a table. Files to enumerate:

```
gsp_<backend>/
├── __init__.py                          # imports submodules, calls register_*
├── renderer_registration.py             # one function: register_renderer_<name>()
├── renderer/
│   ├── <backend>_renderer.py            # the RendererBase implementation
│   └── <backend>_renderer_<visual>.py   # one file per visual type
├── animator/
│   └── animator_<backend>.py            # AnimatorBase implementation
├── viewport_events/
│   └── viewport_events_<backend>.py     # ViewportEventsBase implementation
└── utils/                               # backend-specific helpers
```

Then a 7-row table mapping each subdir to "what shared base class it implements", "where the matplotlib version lives", "where the datoviz version lives", "where the network version lives".

### 4. The `RendererBase` Contract — Method by Method
For each of the six abstract methods, state the contract from `RendererBase`, then a one-sentence summary of what each backend does:

- `__init__(canvas)` — store the canvas, allocate any per-renderer state (figure, dvz.App, http session).
- `render(viewports, visuals, model_matrices, cameras) -> bytes` — the workhorse. Iterate four parallel lists in lockstep (asserted equal length). Returns image bytes (default PNG).
- `show()` — blocking. Matplotlib opens a `pyplot.show()` window; datoviz runs `dvz_app.run()` until 'q'; network reuses matplotlib's `pyplot.show()` to display the bytes it received.
- `close()` — release resources. Each backend calls the corresponding teardown (`pyplot.close()`, `dvz_app.destroy()`, `pyplot.close()`).
- `clear()` — wipe the current frame. Matplotlib calls `figure.clf()`; others do the equivalent.
- `get_canvas()` — return the `Canvas` passed to `__init__`. Trivial.

For each of those, cite the matplotlib implementation as the reference (it's the most readable) and note where datoviz/network differ.

### 5. The Per-Visual Renderer Pattern
This is the load-bearing convention. Three sub-points:

**5.1 The dispatch table is `isinstance`, not a dict.** Show `_render_visual()` from `matplotlib_renderer.py:202-238` as the canonical shape. Note that all three backends use the same eight if/elif arms in the same order. To add a ninth visual type to the project, you add one arm to each `_render_visual()`.

**5.2 The per-visual class is static and stateless.** Each `<backend>_renderer_<visual>.py` exports one class with a single static `render(renderer, viewport, visual, model_matrix, camera)` method. State (matplotlib Artists, datoviz GPU handles) lives back on the main renderer in `_artists` / `_dvz_visuals` dicts keyed by `f"{viewport_uuid}_{visual_uuid}"`. The reason: the per-visual file is just a code-organisation unit; the lifecycle owner is always the main renderer.

**5.3 Lazy create, mutate-update.** First call to `render(viewport, points, ...)` creates a matplotlib `PathCollection` (or datoviz GPU object); subsequent calls mutate the existing artist's offsets/sizes/colors instead of rebuilding. This is what makes the animator efficient — return only the changed visuals from your callback (`AnimatorBase.event_listener`) and the renderer never recreates artists.

### 6. The Registry and Discovery
Walk through `RendererRegistry` (`src/gsp/utils/renderer_registery.py:24-99`). Three entry points:

- `register_renderer(name, renderer_type, events_type, animator_type)` — called once per package at import time.
- `create_renderer(name, canvas)` — used by `ExampleHelper.create_renderer` (cite [examples/common/example_helper.py:42](../../Users/jetienne/work/GSP_API/examples/common/example_helper.py#L42)).
- `create_viewport_events(renderer_base, viewport)` and `create_animator(renderer_base)` — these look up the triad by *instance type* (`isinstance(renderer_base, item.renderer_base_type)`), so once you have a renderer instance you can ask the registry for its matched events/animator without naming the backend again.

This explains why the triad is enforced: the registry's `_get_item_by_renderer_base` would fail to find the matching events/animator if any renderer shipped without them.

### 7. Backend-Specific Notes
Three short subsections, each ~150 words, covering only what's *unique* to that backend:

**7.1 gsp_matplotlib** — Multi-format output (`image_format=` to `render()` plumbed to `figure.savefig`), one `Axes` per viewport cached in `self._axes`, blocking `pyplot.show()`, animator wraps `FuncAnimation`. Reference: `matplotlib_renderer.py:107-200`.

**7.2 gsp_datoviz** — `dvz.App` + `dvz.figure` + lazy `dvz_panel` per viewport, GPU resources cached in `_dvz_visuals`, **CPU-side MVP transform** (the GPU sees pre-transformed vertices, not matrices), Y-axis flip, screenshots require offscreen mode (a temporary offscreen renderer is spawned for that case). Reference: `datoviz_renderer.py:114-179`.

**7.3 gsp_network** — Pure thin client. `render()` calls `PydanticSerializer.serialize(...)` then HTTP POST to `/render`; response PNG goes into a local matplotlib figure for display. Server side: `src/gsp_network/tools/network_server.py` instantiates a real local renderer (`renderer_name` field selects matplotlib vs `DatovizRenderer(offscreen=True)`). **Asymmetric events**: client input does not propagate to the server. Reference: `network_renderer.py:96-167`, `network_server.py:1-157`.

### 8. Writing a New Renderer: A Checklist
The "now you do it" section, parallel in shape to `philosophy_examples.md` §6. Concrete checklist items:

- [ ] **Pick a name and create the package.** `src/gsp_<name>/` with subdirs `renderer/`, `animator/`, `viewport_events/`, plus `renderer_registration.py` and `__init__.py`.
- [ ] **Subclass `RendererBase`.** Implement the six abstract methods. Look at `MatplotlibRenderer` (`matplotlib_renderer.py:38-262`) as the simplest reference.
- [ ] **Decide your dispatch.** If you can lean on a host library that has primitives for points/lines/meshes (matplotlib, datoviz, plotly), follow the per-visual-file pattern: one file per visual type, hand-written `isinstance` chain in `_render_visual()`, static `render(renderer, viewport, visual, model_matrix, camera)` method on each. If you're rendering from scratch (e.g. raw OpenGL), the per-visual files are *still* the right unit — they just contain shader setup instead of library calls.
- [ ] **Subclass `AnimatorBase` and `ViewportEventsBase`.** They must be co-versioned with the renderer; the registry will pair them by instance type. Network is the simplest reference for both because it just reuses matplotlib's loop.
- [ ] **Cache lazily, mutate not rebuild.** Store per-visual artist/GPU handles in `self._artists` (or `self._<backend>_visuals`) keyed by `f"{viewport_uuid}_{visual_uuid}"`. First render creates; subsequent renders update.
- [ ] **Self-register on import.** `renderer_registration.py:register_renderer_<name>()` calls `RendererRegistry.register_renderer(...)` with all three classes; `__init__.py` calls that function at module top level.
- [ ] **Add the name to `ExampleHelper`.** Update `get_renderer_name()`'s assertion in [examples/common/example_helper.py](../../Users/jetienne/work/GSP_API/examples/common/example_helper.py) to include your new name, and `create_renderer()` to instantiate it.
- [ ] **Verify by running an existing example.** `GSP_RENDERER=<your_name> python examples/points_example.py` should produce a PNG visually equivalent to the matplotlib output.

### 9. Verification
Mirror `philosophy_examples.md` §8: a short numbered list of `grep`/`ls` commands the reader can run to confirm the doc against the code. Examples:

- `ls src/gsp_matplotlib/renderer/ src/gsp_datoviz/renderer/ src/gsp_network/renderer/` — confirms the parallel file fan-out.
- `grep -n "register_renderer" src/gsp_*/renderer_registration.py` — confirms the three call sites.
- `grep -n "isinstance(visual," src/gsp_*/renderer/*_renderer.py` — confirms the dispatch pattern.
- `grep -n "class.*RendererBase" src/gsp_*/renderer/*_renderer.py` — confirms the contract is the only inheritance edge.

## Files this plan touches

- **Write** — `/Users/jetienne/work/GSP_API/docs/philosophy/philosophy_renderers.md` (new file, the deliverable).
- **Read-only references** (no edits):
  - `src/gsp/types/renderer_base.py`
  - `src/gsp/types/animator_base.py`
  - `src/gsp/types/viewport_events_base.py`
  - `src/gsp/utils/renderer_registery.py`
  - `src/gsp_matplotlib/{__init__.py, renderer_registration.py, renderer/matplotlib_renderer.py, renderer/matplotlib_renderer_*.py, animator/, viewport_events/}`
  - `src/gsp_datoviz/{__init__.py, renderer_registration.py, renderer/datoviz_renderer.py, …}`
  - `src/gsp_network/{__init__.py, renderer_registration.py, renderer/network_renderer.py, tools/network_server.py, …}`
  - `examples/common/example_helper.py` (cited in §6 and §8)
  - `docs/philosophy/philosophy_examples.md` (the style template)

## Verification of the deliverable

Once written, the doc verifies as follows:

1. **Style match** — the doc reads like `philosophy_examples.md`: numbered sections, principled framing in §2, canonical-skeleton walk in §3, pattern catalog in §4-7, checklist in §8, verification commands in §9.
2. **Every claim has a citation** — file path with line number for each non-trivial statement, in the form `[file.py:N](relative/path/file.py#LN)`.
3. **The "writing a new renderer" checklist is testable** — a reader could create `src/gsp_dummy/` with the listed structure and the registry would pick it up.
4. **The shell commands in §9 produce the expected output** — they really run against this codebase and confirm the structural claims.

## Open question for the user

The prompt file says output should go to `docs/philosophy/philosophy_rendererd.md`. That looks like a typo for `philosophy_renderers.md` (matches the prompt-file naming `philosophy_renderers_prompt.md` and the existing siblings `philosophy_examples.md`, `philosophy_packages.md`). I'll confirm with AskUserQuestion before writing.
