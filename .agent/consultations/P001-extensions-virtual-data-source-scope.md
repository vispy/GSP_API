# P001 - Extensions and virtual data-source v0.1 scope

Status: pending ChatGPT Pro response.

## Why This Is Needed

M011 is an architecture mission. It must not implement extension manifests, virtual data sources,
server-side fetch, or tiled-image proof code until the minimal scope is decided. The main risk is
accidentally designing a broad plugin/cloud/data platform when the project only needs a small
GSP v0.1-compatible proof.

## Exact Prompt For ChatGPT Pro

You are an architecture reviewer for the GSP / VisPy2 project.

GSP is a Graphics Server Protocol for semantic scientific visualization. The current repository has
an accepted v0.1 vertical slice with:

- stable protocol IDs;
- capability snapshots and explicit adaptation decisions;
- contiguous in-process buffer resources;
- local in-process transport without mandatory JSON/base64;
- `PointVisual` and `ImageVisual` protocol models;
- Matplotlib reference rendering for point/image visuals;
- deterministic CPU reference panel query for point-over-image;
- a bounded Datoviz v0.4 adapter slice for point and RGBA8 image visuals;
- a minimal VisPy2 producer MVP that emits GSP protocol point/image visuals.

Project principles:

1. GSP is a server/session protocol inspired by LSP, not merely a Python object graph.
2. Local desktop use must have a fast in-process path with no mandatory JSON/base64 serialization.
3. JSON/base64 is allowed for fixtures, debugging, replay, and simple transport only.
4. Capability discovery and explicit adaptation are mandatory.
5. Visual families are semantic contracts, not backend draw calls.
6. Query/readback is first-class and should use a unified panel-query model.
7. Extensions must be manifest-, version-, and capability-driven.
8. Huge datasets should be represented as virtual data sources, not ordinary buffers.
9. Datoviz v0.4 is the flagship GPU backend, but M011 must not require Datoviz changes.
10. Matplotlib is the reference/conformance/publication backend.
11. VisPy2 is the high-level Python producer of GSP scenes.

Current draft specs:

- Extensions may define visual families, transforms, data sources, formats/decoders,
  query/readout payloads, and transports. Every extension needs an id, semantic version, kind,
  schema, capability requirements, implementation declarations, fallback policy, diagnostics policy,
  and query contract where applicable.
- Virtual data sources are for huge datasets such as tiled image pyramids, cloud microscopy data,
  map tiles, point-cloud octrees, remote simulation timesteps, and custom chunk APIs.
- A data source should declare logical shape, coordinate system, chunk/tile scheme, levels of detail,
  fetch locality, cache policy, credentials policy, materialization policy, and query/readout
  behavior.
- Remote renderers should be able to fetch data server-side when permitted, avoiding client data
  transfer.

The current `ImageVisual` v0.1 model accepts eager local NumPy images with shape `(H, W)`,
`(H, W, 3)`, or `(H, W, 4)`, explicit extent, origin, and interpolation. The current query model
supports statuses `hit`, `miss`, `outside-panel`, `unsupported`, `stale`, `dropped`, and `failed`.
Capability snapshots include coarse `query_modes` and `extensions`.

Please define a minimal v0.1 architecture for GSP extensions and virtual data sources that supports
a local fake tiled-image proof without introducing a production plugin system or cloud fetch stack.

Answer these specific questions:

1. What is the smallest extension manifest model that is useful now?
2. Should virtual data sources be a core protocol object, an extension object, or both?
3. What exact fields should a minimal `TiledImageSource` or `VirtualImageSource` contain?
4. How should data locality be represented: local in-memory, local file, client-fetch, server-fetch,
   remote opaque handle, or other categories?
5. What is the safe v0.1 credential/security policy?
6. What should Matplotlib reference behavior do for a tiled source: materialize a requested tile,
   materialize a viewport mosaic, or reject with diagnostic?
7. How should query/readout work for virtual tiled images in v0.1?
8. Which capabilities should advertise support for extension manifests and virtual data sources?
9. What must be explicitly out of scope?
10. What is the smallest local proof that validates the architecture?

Constraints:

- Do not require JSON/base64 for the local in-process path.
- Do not require network access or real cloud credentials.
- Do not require Datoviz changes.
- Do not design a general package manager or broad plugin loader.
- Keep the proof compatible with the existing v0.1 point/image/query model.
- Prefer small dataclasses/protocol models and tests over runtime infrastructure.

## Expected Output Format

Please respond with these sections:

1. **Recommendation Summary**
   - 5-10 bullets describing the recommended architecture.

2. **ADR Draft**
   - Title.
   - Status: Proposed.
   - Context.
   - Decision.
   - In scope.
   - Out of scope.
   - Consequences.
   - Open questions.

3. **Minimal Protocol Models**
   - Proposed dataclass-like definitions or schemas for:
     - extension manifest;
     - data-source descriptor;
     - tiled image source;
     - tile request/result;
     - locality/fetch/security enums.

4. **Capability Surface**
   - Exact capability fields or extension names to add/reuse.
   - How unsupported behavior should adapt/reject.

5. **Reference Matplotlib Proof**
   - What local fake provider should do.
   - What renderer/query tests should prove.
   - What must remain mocked or deferred.

6. **Task List For Codex Agents**
   - Small tasks in recommended execution order.
   - Paths likely touched.
   - Stop conditions for each task.

7. **Non-Goals**
   - Explicit list of things not to implement in M011/M012.

8. **Risk Review**
   - Security/credential risks.
   - Scope risks.
   - Compatibility risks with Datoviz and VisPy2.

## Context Files To Provide Alongside This Prompt

If possible, paste or attach these repository files:

- `PROJECT_CHARTER.md`
- `ARCHITECTURE.md`
- `adr/ADR-0003-gsp-v0.1-vertical-slice.md`
- `spec/extensions.md`
- `spec/data_sources.md`
- `spec/resources.md`
- `spec/visuals/image.md`
- `spec/query.md`
- `spec/capabilities.md`
- `spec/vispy2/api.md`

## Blocked Decisions

Implementation must wait for the answer to these decisions:

- whether virtual data sources are core protocol objects, extension-defined objects, or both;
- exact minimal source/tile/locality/security fields;
- whether Matplotlib reference behavior should materialize full mosaics or only requested tiles;
- how v0.1 query/readout maps from virtual image tiles back to logical source coordinates;
- what capability names advertise the feature without overclaiming production remote fetch support.

## Dependent Work To Pause

Do not implement any of the following until the ChatGPT Pro answer is available and captured:

- ADR for extension/data-source architecture;
- `VirtualImageSource` / `TiledImageSource` source models;
- fake tile provider tests;
- Matplotlib tiled-image rendering/query proof;
- extension manifest loader or registry.
