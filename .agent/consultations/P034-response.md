# Consultation Result: GSP Public Documentation And Specification Architecture

## Executive Decision

GSP must be presented through one protocol-centered mental model:

> **A producer describes a scientific visualization using semantic GSP records and submits command batches to a capability-negotiated session. The session validates and executes those commands through a backend adapter, then returns query results, readbacks, and diagnostics.**

VisPy2 is the intended high-level Python producer. Direct GSP records are the lower-level integration and conformance interface. A transport connects the producer to the session but does not define protocol meaning. In-process Python/NumPy transport is a first-class path, not a serialized emulation. Matplotlib is the reference and publication backend. Datoviz v0.4 is the flagship GPU backend, but every feature claim is capability-gated and may be strict, adapted, unsupported, or blocked. 

The documentation must therefore be divided into four clearly separated layers:

1. **Public explanatory documentation:** concept-first, task-oriented, and suitable for a new technical user.
2. **Normative specification:** organized by durable protocol concepts rather than implementation chronology.
3. **Backend profiles and conformance evidence:** implementation-specific support claims that never redefine protocol semantics.
4. **Development history and legacy documentation:** preserved but excluded from recommended and normative reading paths.

The public site must never describe `Canvas`, `Viewport`, `RendererBase`, runtime renderer registries, `datoviz-v03`, or the legacy Flask renderer as the architecture of GSP.

## Audience And Learning Outcomes

| Audience                          | What they must understand                                                                                      | Recommended entry page                                 |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| Scientific Python user            | What GSP does, how to install the prototype, and how to produce a first visualization                          | Getting Started → First visualization                  |
| Visualization-library user        | When to use VisPy2, direct GSP records, Matplotlib, or Datoviz                                                 | Getting Started → What is GSP?                         |
| Library or domain-tool integrator | How to emit semantic protocol records and manage sessions, capabilities, resources, and diagnostics            | Concepts → Architecture and roles                      |
| Backend implementer               | Which semantics an adapter must implement, how capabilities are declared, and how conformance is demonstrated  | Backend Support → Reading support tables               |
| Protocol or conformance reviewer  | Which documents are normative, which requirements apply, and where evidence is recorded                        | Specification → Specification overview                 |
| Contributor                       | How to change public documentation, protocol rules, adapters, or conformance assets without mixing authorities | Contributing → Documentation and specification changes |
| Maintainer of legacy applications | Which compatibility APIs remain available and how they differ from the GSP protocol architecture               | Development History → Legacy renderer API              |
| Project evaluator                 | What is implemented today, what remains experimental, and which backend combinations are known to work         | Project Status → Current maturity                      |

## Canonical Terminology

| Term                 | Plain-language definition                                                              | Normative meaning                                                                                                                                   | Avoid/confusing alternative                                                |
| -------------------- | -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| GSP                  | A protocol for describing and executing scientific visualizations                      | The transport-independent semantic contracts, commands, resources, queries, diagnostics, and capability rules defined by the accepted specification | “A Python renderer,” “a scene-graph library,” or “the current source tree” |
| Producer             | Software that creates GSP commands and resources                                       | The protocol peer that submits commands to a session; it may be VisPy2, another plotting API, or a domain library                                   | Client object graph                                                        |
| VisPy2               | The intended high-level Python interface to GSP                                        | A producer that translates user-facing visualization operations into valid GSP protocol operations                                                  | GSP itself                                                                 |
| Protocol record      | A validated description of a command, resource, view, visual, guide, or related entity | A typed value whose fields and invariants are defined by the specification                                                                          | Backend draw call                                                          |
| Command batch        | A submitted group of protocol operations                                               | A `CommandBatch` with specified ordering, validation, failure, and execution semantics                                                              | Render list                                                                |
| Session              | A capability-negotiated execution context between producer and server                  | The scope for protocol state, identifiers, resources, command execution, queries, diagnostics, and lifecycle                                        | Renderer instance                                                          |
| GSP server           | The protocol executor associated with a session                                        | The peer that advertises capabilities, accepts commands, invokes backend adapters, and returns results or diagnostics                               | Only a remote network service                                              |
| Transport            | The mechanism carrying protocol operations between producer and server                 | An implementation of transport-independent protocol exchange; current examples include in-process and debug JSON paths                              | Protocol encoding                                                          |
| In-process transport | A local producer/server connection using native Python-compatible values               | A transport that may carry NumPy arrays, buffers, and memory views without mandatory JSON/base64 conversion                                         | Mock network transport                                                     |
| Scene                | The current semantic visualization state known to a session                            | The aggregate state established by accepted commands, resources, panels, views, visuals, and guides                                                 | A required Python object graph                                             |
| Panel                | A rectangular presentation and query region                                            | A protocol entity participating in resolved layout and containing or associating views and guides                                                   | Legacy viewport                                                            |
| Resolved layout      | The concrete panel geometry used for rendering and queries                             | The layout result after constraints and dimensions have been resolved according to protocol rules                                                   | Backend window layout                                                      |
| View                 | A mapping from data or world coordinates into a panel                                  | A `View2D` or `View3D` contract defining ranges, projection, navigation state, and associated transforms                                            | Camera alone                                                               |
| Visual               | A semantic graphical family such as points, paths, images, text, or meshes             | A protocol contract whose meaning is independent of backend-specific drawing primitives                                                             | Shader, pipeline, or draw call                                             |
| Guide                | A semantic annotation associated with a panel or view                                  | Axis, tick, grid, text, or colorbar intent that a backend interprets according to the specification                                                 | Pre-rendered decoration                                                    |
| Resource             | Validated data referenced by visuals or commands                                       | An immutable or otherwise specification-controlled protocol resource such as a buffer or `Texture2D`                                                | Arbitrary backend allocation                                               |
| Virtual data source  | A logical source for data too large or dynamic to treat as an ordinary buffer          | A capability- and protocol-governed interface for deferred or partial data access                                                                   | A very large `Buffer`                                                      |
| Backend adapter      | The translation layer between GSP semantics and a renderer implementation              | An implementation that advertises capabilities and either implements, explicitly adapts, or rejects protocol features                               | Global renderer registry entry                                             |
| Backend              | The rendering technology used by an adapter                                            | An implementation profile such as Matplotlib or Datoviz v0.4; it does not alter protocol meaning                                                    | Interchangeable implementation with universal parity                       |
| Capability snapshot  | The session’s declared support envelope                                                | A `CapabilitySnapshot` describing supported features, limits, adaptations, and extensions for that session                                          | Detection from imported symbols                                            |
| Strict support       | Implementation without a declared semantic deviation                                   | Runtime behavior supported by semantic conformance evidence for the stated feature combination                                                      | “It rendered an image”                                                     |
| Adapted support      | Deliberate implementation through a documented approximation or changed behavior       | Support whose deviation is explicitly declared through capabilities, profile documentation, and diagnostics where required                          | Silent fallback                                                            |
| Partial support      | Support for only an explicitly enumerated subset                                       | A profile status that must list included and excluded cases                                                                                         | Supported                                                                  |
| Unsupported          | A feature the implementation does not advertise or execute                             | Deterministic rejection or absence from the advertised capability set                                                                               | Broken                                                                     |
| Blocked              | A potential implementation whose public promotion is intentionally disabled            | A status used when safety, crash isolation, semantic evidence, or unresolved correctness prevents a support claim                                   | Supported but experimental                                                 |
| Frame                | A requested execution or presentation point                                            | The protocol operation that causes pending state to be rendered or otherwise executed according to session semantics                                | Calling `renderer.render(...)`                                             |
| Query                | A structured request about panel, visual, or rendered state                            | A first-class protocol operation using the unified panel-query model and capability-specific payload contracts                                      | Backend-specific picking hook                                              |
| Readback             | Returned data derived from resources or rendered state                                 | A query/result class with explicit format, scope, and capability requirements                                                                       | Screenshot only                                                            |
| Diagnostic           | A structured report from validation, adaptation, execution, or queries                 | A machine-readable code, severity, location, and explanatory payload governed by the protocol                                                       | Console warning                                                            |
| Extension manifest   | A declaration of non-core protocol behavior                                            | A versioned, capability-driven description of extension identity, requirements, and compatibility                                                   | Arbitrary plugin import                                                    |
| Legacy renderer API  | The older object-oriented rendering system still present for compatibility             | The `Canvas`/`Viewport`/`Camera`/`Visual`/`RendererBase` path, which is outside the current GSP protocol authority                                  | GSP producer API                                                           |

## Legacy Boundary

The legacy object-oriented renderer must remain available only as explicitly isolated compatibility material.

**Keep in the repository:**

* Existing legacy source code required by compatibility users or tests.
* Legacy examples that still serve maintenance or migration purposes.
* Historical design documents, evidence, stage records, and closeouts.
* API documentation needed to maintain applications that still use the legacy packages.

**Relabel:**

* Every page or API entry involving `Canvas`, `Viewport`, `Camera`, `Buffer`, legacy `Visual` subclasses, `RendererBase`, or `RendererRegistry` must carry the label **Legacy renderer API — not the GSP protocol API**.
* `datoviz-v03` must be called **Legacy Datoviz v0.3 renderer**.
* The Flask/network path must be called **Legacy network renderer**, not “remote GSP.”
* Environment-variable selection through `GSP_RENDERER` must be documented solely as legacy behavior.

**Move:**

* Legacy conceptual documentation to `Development History → Legacy renderer architecture`.
* Legacy API reference pages to `Development History → Legacy Python API`.
* Old examples to a visibly separate `examples/legacy/` collection and corresponding historical gallery page.
* Chronological implementation evidence to `development-history/`, never to normative specification pages.
* Existing Philosophy material to an archived section after extracting any still-valid protocol concepts into newly written concept pages.

**Remove from recommended public navigation:**

* All old RendererBase architecture explanations.
* Four-parallel-render-list explanations.
* Runtime registry selection as the normal backend model.
* `datoviz-v03` and legacy Flask renderer pages as current backend choices.
* The navigation label “Historical S023 QA.”
* Broad generated package dumps that expose legacy and protocol APIs without distinction.

**Navigation and search rules:**

* No current tutorial, homepage, concept page, backend page, or normative specification page may link to the legacy API as a recommended next step.
* A single migration note may link from the current API overview to the legacy archive.
* Legacy pages must display a persistent warning banner and must not use canonical metadata for current GSP concepts.
* Existing public URLs should redirect to either the corresponding new page or the accurately labeled archive; they must not silently reinterpret old content as current architecture.

## Final Information Architecture

* **Home** — Defines GSP in one sentence, shows the producer/session/adapter architecture, exposes current maturity, and routes users to the first tutorial or support matrix.

* **Getting Started**

  * **What is GSP?** — Explains the problem GSP addresses, the protocol-centered mental model, and the distinct roles of VisPy2, GSP, transports, and backends.
  * **Installation** — Gives verified source-installation instructions for Python 3.13 or newer without implying PyPI availability.
  * **First visualization** — Builds and executes one minimal current protocol scene through an in-process Matplotlib session.
  * **Choosing a backend** — Explains reference versus GPU backends, capability discovery, and why backend choice is explicit rather than globally interchangeable.
  * **Where to go next** — Routes users to VisPy2, direct protocol integration, backend implementation, examples, or the normative specification according to their task.

* **Concepts**

  * **Architecture and roles** — Defines producers, sessions, servers, transports, adapters, and backends using the canonical architecture diagram.
  * **Session lifecycle** — Explains capability discovery, command submission, validation, execution, frame production, queries, diagnostics, and shutdown in order.
  * **Scenes, panels, views, and visuals** — Introduces the semantic scene model without presenting it as a mandatory Python object graph.
  * **Resources and data sources** — Explains buffers, textures, immutable or validated resources, and virtual data sources.
  * **Coordinates, transforms, and layout** — Explains coordinate spaces, 2D affine transforms, panel geometry, and resolved layout.
  * **Capabilities and adaptation** — Explains strict, adapted, partial, unsupported, and blocked behavior, including runtime negotiation.
  * **Queries, readback, and diagnostics** — Presents the unified panel-query model and structured failure or adaptation reporting.
  * **Local and remote execution** — Separates protocol meaning from in-process, subprocess, future binary IPC, network, browser-worker, and cloud deployment choices.

* **User Guide**

  * **Building and updating a scene** — Shows the normal command and resource lifecycle for creating, changing, and executing scene state.
  * **Visual families** — Introduces visuals as semantic contracts and links to family-specific guidance.

    * **Points and markers** — Covers `PointVisual` and `MarkerVisual`, data requirements, coordinates, and supported styling.
    * **Segments and paths** — Covers `SegmentVisual` and `PathVisual`, connectivity, line semantics, and limitations.
    * **Images and scalar color mapping** — Covers `ImageVisual`, `Texture2D`, linear normalization, and canonical named colormaps.
    * **Text and guides** — Covers `TextVisual`, `AxisGuide`, `PanelTextGuide`, ticks, grids, and colorbars.
    * **Meshes and 3D visuals** — Covers `MeshVisual`, projections, depth, flat Lambert shading, face culling, and bounded 3D scope.
  * **Panels, guides, and layout** — Shows how views and annotations are placed and how resolved geometry affects rendering and queries.
  * **Interaction and navigation** — Explains semantic 2D and 3D navigation actions rather than backend event APIs.
  * **Resources and large data** — Gives practical resource-lifetime guidance and distinguishes ordinary buffers from virtual data sources.
  * **Queries and readback** — Shows supported query patterns, capability checks, result payloads, and failure diagnostics.
  * **Extensions** — Explains extension manifests, version constraints, capabilities, and compatibility requirements.

* **Backend Support**

  * **Reading support tables** — Defines every support label and explains why protocol acceptance, producer support, renderer support, and query support are separate axes.
  * **Feature matrix** — Provides the versioned, evidence-backed cross-backend support table.
  * **Matplotlib profile** — Documents reference semantics, publication use, strict behavior, and declared 3D adaptations.
  * **Datoviz v0.4 profile** — Documents GPU support feature by feature, including strict, adapted, unsupported, blocked, and crash-isolated cases.
  * **Transport and deployment profiles** — Documents the current in-process and debug transports and clearly labels unimplemented remote or binary paths.
  * **Known limitations** — Provides a concise, user-facing list of limitations linked to exact profile entries and diagnostics.

* **Project Status**

  * **Current maturity** — States that GSP and VisPy2 are experimental 0.1.0 prototypes and describes what that means for users.
  * **Implemented protocol scope** — Summarizes accepted schema and behavior by durable feature family rather than internal stages.
  * **Implementation gaps** — Lists major producer, backend, query, data-source, and transport gaps without using delivery chronology.
  * **Release notes** — Records public version changes, compatibility implications, and user-visible behavior rather than internal mission completion.

* **Specification**

  * **Specification overview** — Explains authority, conformance language, document statuses, and how to navigate the normative corpus.
  * **Protocol model** — Defines protocol independence from encoding, session roles, state, and execution semantics.
  * **Sessions, commands, and frames** — Defines session lifecycle, command batches, ordering, validation, failure, and frame execution.
  * **Capabilities, adaptation, and diagnostics** — Defines negotiation, support declarations, adaptation requirements, and structured diagnostics.
  * **Scene model**

    * **Scene state** — Defines identifiers, ownership, state transitions, and relationships among protocol entities.
    * **Panels and resolved layout** — Defines panel geometry, constraints, and resolved layout.
    * **Coordinate spaces and transforms** — Defines coordinate spaces and 2D affine transformations.
    * **View2D and navigation** — Defines ranges, mapping, and semantic 2D navigation actions.
    * **View3D and navigation** — Defines orthographic and perspective views and semantic 3D navigation actions.
  * **Resources and data**

    * **Resource model** — Defines resource validation, mutability, identity, lifetime, and references.
    * **Buffers** — Defines ordinary protocol buffers and their validation rules.
    * **Texture2D** — Defines texture shape, format, sampling, and image-resource semantics.
    * **Data sources** — Defines virtual, preconfigured, and HTTP-array data-source contracts within accepted scope.
  * **Visual semantics**

    * **Common visual contract** — Defines shared visibility, transforms, resources, ordering, and validation behavior.
    * **Points and markers** — Defines point and marker semantics.
    * **Segments and paths** — Defines segment and path semantics.
    * **Images** — Defines image geometry and sampling semantics.
    * **Text** — Defines text content, placement, and styling semantics.
    * **Meshes** — Defines bounded opaque meshes, depth, shading, face culling, and related payloads.
  * **Guides and color**

    * **Axes, ticks, and grids** — Defines guide intent without prescribing backend drawing calls.
    * **Panel text** — Defines panel-level title, label, and annotation intent.
    * **Scalar color mapping** — Defines normalization and scalar-to-color semantics.
    * **Named colormaps** — Defines the canonical colormap registry.
    * **Colorbars** — Defines colorbar intent and its relationship to scalar mapping.
  * **Queries and readback**

    * **Panel-query model** — Defines common query targeting, coordinates, and result envelopes.
    * **Readback** — Defines pixel or resource readback semantics and formats.
    * **Query payloads** — Defines feature-specific results, including mesh-triangle payloads.
  * **Transports**

    * **Transport-independent semantics** — Defines the behavior all transports must preserve.
    * **In-process transport** — Defines native Python/NumPy/memoryview exchange requirements.
    * **Debug JSON encoding** — Defines the non-primary encoding used for fixtures, replay, debugging, and simple transport.
  * **Registries** — Publishes stable capability keys, diagnostic codes, extension identifiers, and other normative registries.
  * **Backend profiles** — Links to non-normative Matplotlib and Datoviz implementation declarations without placing them above the protocol specification.
  * **Conformance** — Links normative requirements to executable tests, runtime evidence, and visual evidence.
  * **Decision rationale** — Indexes accepted ADRs that explain choices without duplicating normative requirements.

* **Python API**

  * **API overview and stability** — Defines the supported public Python surfaces and their prototype stability.
  * **Producer and session API** — Documents the public producer, session, transport, and execution entry points by task.
  * **Protocol records** — Documents current command, panel, view, transform, capability, and extension records.
  * **Visual and resource records** — Documents visuals, guides, buffers, textures, and data-source records.
  * **Queries and diagnostics** — Documents query construction, result handling, capability inspection, and diagnostic processing.
  * **Backend adapter interface** — Documents the public adapter surface for backend implementers, not internal renderer implementation details.

* **Examples**

  * **Gallery** — Shows only curated scenes generated through the current protocol path, with exact support labels.
  * **Minimal 2D examples** — Provides small executable examples using views, points, markers, segments, and paths.
  * **Images, guides, and color** — Demonstrates texture resources, scalar mapping, axes, grids, text, and colorbars.
  * **Interaction and queries** — Demonstrates navigation actions, panel queries, readback, and diagnostics.
  * **3D scenes and meshes** — Demonstrates projections, meshes, depth, shading, culling, and 3D navigation.
  * **Backend comparisons** — Presents matched Matplotlib and Datoviz captures with per-scene strict or adapted qualifications.
  * **Example index** — Lists requirements, expected capabilities, backend status, and execution commands for every maintained example.

* **Contributing**

  * **Contributor workflow** — Gives repository, testing, review, and change-management procedures.
  * **Documentation and specification changes** — Defines authority checks, status transitions, terminology rules, and required migration work.
  * **Protocol change process** — Defines when an ADR is required and how normative text, registries, tests, and profiles change together.
  * **Backend adapters** — Explains capability declarations, deterministic rejection, adaptation, diagnostics, and profile maintenance.
  * **Conformance and visual QA** — Defines semantic tests, runtime evidence, capture provenance, and review expectations.
  * **Governance and ADRs** — Explains decision authority and how accepted rationale is retained.

* **Development History**

  * **History overview** — Explains that this section preserves implementation chronology and is not protocol authority.
  * **Legacy renderer architecture** — Documents the old object-oriented rendering model for maintenance and historical understanding.
  * **Legacy Python API** — Provides isolated API material for `Canvas`, `Viewport`, `RendererBase`, and related compatibility surfaces.
  * **Legacy backend paths** — Documents `datoviz-v03`, the old network renderer, and `GSP_RENDERER` behavior.
  * **Archived philosophy documents** — Preserves superseded design essays after valid current concepts have been extracted.
  * **Delivery archive** — Preserves stages, missions, consultations, closeouts, and evidence chronology outside public and normative reading paths.

## Homepage Blueprint

| Order | Section                               | Purpose                                                                                                                                                    | Recommended screenshot or visual                                                                      | Primary action                 |
| ----: | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------ |
|     1 | Definition and value proposition      | State that GSP is a backend-independent semantic protocol and session model for scientific visualization, not another renderer abstraction                 | No screenshot; use a compact architecture diagram                                                     | Build your first visualization |
|     2 | One mental model                      | Show producer → session/protocol → adapter → backend, with results and diagnostics returning to the producer                                               | Purpose-built SVG diagram with in-process and remote transport variants                               | Understand the architecture    |
|     3 | Current prototype status              | State experimental version, Python requirement, source-installation status, and the distinction between accepted protocol scope and uneven backend support | No screenshot; use four restrained status cards                                                       | View current status            |
|     4 | First successful result               | Demonstrate the smallest current protocol scene through Matplotlib                                                                                         | One deterministic Matplotlib points screenshot from the first tutorial                                | Run the example                |
|     5 | Why capabilities matter               | Explain that support is negotiated per session and that “backend-independent” does not mean every backend implements every feature                         | Small capability-flow diagram, not a backend image                                                    | Read the support matrix        |
|     6 | VisPy2, direct protocol, and adapters | Give three concise pathways: application user, protocol integrator, and backend implementer                                                                | No screenshot; use three text cards                                                                   | Choose a pathway               |
|     7 | Backend comparison                    | Show the same verified scene through Matplotlib and Datoviz with visible strict/adapted labels                                                             | Responsive two-column points-over-image comparison, only after current regeneration and qualification | Compare backends               |
|     8 | 3D scope                              | Demonstrate the accepted bounded mesh and view model without implying complete GPU parity                                                                  | Responsive View3D cube or flat-Lambert mesh comparison                                                | Explore 3D scenes              |
|     9 | Queries and diagnostics               | Show that rendering is bidirectional and failures or adaptations are structured                                                                            | Compact request/result/diagnostic diagram                                                             | Learn about queries            |
|    10 | Specification entry                   | Lead users from plain language to exact normative definitions                                                                                              | No screenshot; show a small map from concept pages to specification sections                          | Open the specification         |

The homepage must not contain a generic package API dump, internal stage counters, a backend-parity claim, or a legacy renderer selector.

## Getting-Started Narrative

The first tutorial must use the **current protocol path**, an **in-process session**, and the **Matplotlib protocol adapter**. It must not use `Canvas`, `Viewport`, `RendererBase`, `RendererRegistry`, `GSP_RENDERER`, `datoviz-v03`, or the legacy network renderer.

The tutorial order must be:

1. **State the result.** Show the final small 2D point visualization and say that the producer will submit semantic records to a local GSP session.
2. **State prerequisites.** Require Python 3.13 or newer and identify the supported development platforms only when verified.
3. **Install from the repository.** Provide a clean-checkout installation command and explicitly state that no PyPI release is currently available.
4. **Create an explicit local session.** Use the verified Matplotlib protocol-session constructor or factory already exercised by current protocol tests or review examples.
5. **Inspect capabilities.** Retrieve the session’s `CapabilitySnapshot` and check the exact capabilities required by the example.
6. **Create protocol state.** Construct one panel, one `View2D`, one validated numeric resource, and one `PointVisual`.
7. **Submit a `CommandBatch`.** Submit the resource and scene commands through the in-process transport; do not call a backend renderer directly.
8. **Execute a frame.** Request frame execution and display or save the Matplotlib result through the supported session result path.
9. **Inspect diagnostics.** Show how warnings, adaptations, validation errors, or unsupported features would be retrieved.
10. **Add one query.** Use a small panel query only if it is supported by the verified Matplotlib profile; otherwise make it the next tutorial.
11. **Explain the mapping.** Show, in prose or a small diagram, that a VisPy2 producer would emit equivalent protocol operations rather than bypassing the session.
12. **Introduce Datoviz separately.** Repeat the scene with Datoviz only on the Choosing a backend page, after checking the required capability set and documenting the observed support class.

The first example should use points rather than textures, text, guides, or 3D so that its success does not depend on known Datoviz promotion gaps. A second example may add an image or guide specifically to demonstrate capability negotiation and adaptation.

The code surface must be limited to:

* Public records and helpers under the verified `gsp.protocol` producer-facing surface.
* `CommandBatch` and `CapabilitySnapshot`.
* Current panel, `View2D`, resource, and `PointVisual` records.
* The public in-process session/transport entry point.
* The current Matplotlib protocol adapter.
* Structured result and diagnostic APIs.

The documentation implementation agent must copy imports and constructors from an executable current protocol test or review example. It must not invent convenience APIs while writing the tutorial. The exact tutorial file must be checked into the repository and executed in documentation CI so that displayed code and tested code are identical.

## Specification Architecture

The normative specification and implementation evidence must be reorganized as follows:

```text
SPEC_INDEX.md

spec/
  README.md
  conformance-language.md
  protocol-model.md

  core/
    sessions.md
    commands-and-batches.md
    execution-and-frames.md
    identifiers-lifetimes-and-validation.md
    capabilities-and-adaptation.md
    diagnostics.md
    extensions.md

  scene/
    scene-state.md
    panels-and-layout.md
    coordinate-spaces-and-transforms.md
    view2d-and-navigation.md
    view3d-and-navigation.md

  resources/
    resource-model.md
    buffers.md
    texture2d.md
    data-sources.md

  visuals/
    common-visual-contract.md
    points-and-markers.md
    segments-and-paths.md
    images.md
    text.md
    meshes.md

  guides/
    axes-ticks-and-grid.md
    panel-text.md
    colorbars.md

  color/
    scalar-mapping.md
    named-colormaps.md

  queries/
    panel-query-model.md
    readback.md
    query-payloads.md

  transports/
    transport-independent-semantics.md
    in-process.md
    debug-json.md

  registries/
    capability-keys.md
    diagnostic-codes.md
    extension-identifiers.md
    colormap-names.md

profiles/
  README.md
  backends/
    matplotlib.md
    datoviz-v04.md
  transports/
    in-process.md
    debug-json.md

conformance/
  README.md
  requirements-map.md
  test-manifest.md
  visual-qa.md
  evidence/
    matplotlib.md
    datoviz-v04.md
    producers/
      vispy2.md

adr/
  README.md
  accepted/
  proposed/
  superseded/

development-history/
  README.md
  stages/
  missions/
  consultations/
  closeouts/
  evidence-notes/
  legacy/
```

Only `spec/**` defines protocol semantics. `profiles/**` declares implementation behavior. `conformance/**` records verification. `adr/**` records rationale. `development-history/**` preserves chronology and has no normative authority.

`SPEC_INDEX.md` becomes a short normative manifest containing only:

* Durable semantic document identifier.
* Title.
* Status.
* Normative scope.
* Dependencies.
* Supersedes/superseded-by relationship.
* Link to the specification document.

It must not index `.agent` decisions, implementation closeouts, evidence notes, mission summaries, or consultations.

| Current subject matter                                         | Target destination                                                   |
| -------------------------------------------------------------- | -------------------------------------------------------------------- |
| Overall producer/session/server/adapter architecture           | `spec/protocol-model.md`                                             |
| Session lifecycle and protocol state                           | `spec/core/sessions.md`                                              |
| `CommandBatch`, command ordering, validation, and failure      | `spec/core/commands-and-batches.md`                                  |
| Frame execution and result timing                              | `spec/core/execution-and-frames.md`                                  |
| Entity identity, ownership, lifetimes, and resource references | `spec/core/identifiers-lifetimes-and-validation.md`                  |
| Capability discovery and explicit adaptation                   | `spec/core/capabilities-and-adaptation.md`                           |
| Structured errors, warnings, and adaptation reports            | `spec/core/diagnostics.md`                                           |
| Extension manifests, versions, and capability requirements     | `spec/core/extensions.md`                                            |
| Panels and resolved layout                                     | `spec/scene/panels-and-layout.md`                                    |
| Coordinate spaces and 2D affine transforms                     | `spec/scene/coordinate-spaces-and-transforms.md`                     |
| `View2D`, ranges, and 2D navigation                            | `spec/scene/view2d-and-navigation.md`                                |
| Orthographic/perspective `View3D` and navigation               | `spec/scene/view3d-and-navigation.md`                                |
| Shared resource rules                                          | `spec/resources/resource-model.md`                                   |
| Buffer schema and validation                                   | `spec/resources/buffers.md`                                          |
| `Texture2D` protocol resource                                  | `spec/resources/texture2d.md`                                        |
| Virtual, preconfigured, and HTTP-array source contracts        | `spec/resources/data-sources.md`                                     |
| Shared visual fields and behavior                              | `spec/visuals/common-visual-contract.md`                             |
| `PointVisual` and `MarkerVisual`                               | `spec/visuals/points-and-markers.md`                                 |
| `SegmentVisual` and `PathVisual`                               | `spec/visuals/segments-and-paths.md`                                 |
| `ImageVisual`                                                  | `spec/visuals/images.md`                                             |
| `TextVisual`                                                   | `spec/visuals/text.md`                                               |
| `MeshVisual`, depth, shading, culling, and mesh semantics      | `spec/visuals/meshes.md`                                             |
| `AxisGuide`, ticks, and grids                                  | `spec/guides/axes-ticks-and-grid.md`                                 |
| `PanelTextGuide`                                               | `spec/guides/panel-text.md`                                          |
| `ColorbarGuide`                                                | `spec/guides/colorbars.md`                                           |
| Linear normalization and scalar mapping                        | `spec/color/scalar-mapping.md`                                       |
| Canonical named colormaps                                      | `spec/color/named-colormaps.md`                                      |
| Unified panel-query targeting                                  | `spec/queries/panel-query-model.md`                                  |
| Readback formats and behavior                                  | `spec/queries/readback.md`                                           |
| Mesh-triangle and other feature-specific query payloads        | `spec/queries/query-payloads.md`                                     |
| Encoding-independent transport requirements                    | `spec/transports/transport-independent-semantics.md`                 |
| Python/NumPy/memoryview transport rules                        | `spec/transports/in-process.md`                                      |
| JSON/base64 fixture, debug, and replay encoding                | `spec/transports/debug-json.md`                                      |
| Matplotlib implementation claims and deviations                | `profiles/backends/matplotlib.md`                                    |
| Datoviz v0.4 implementation claims and deviations              | `profiles/backends/datoviz-v04.md`                                   |
| Executable semantic tests and evidence mapping                 | `conformance/requirements-map.md` and `conformance/test-manifest.md` |
| Visual captures and comparison procedures                      | `conformance/visual-qa.md`                                           |
| Why a protocol decision was made                               | An accepted ADR linked from the relevant specification section       |
| Stage, mission, consultation, proof chronology, or closeout    | `development-history/`                                               |

Every normative file must begin with a standard header:

```text
Title:
Semantic identifier:
Status:
Normative scope:
Protocol version:
Dependencies:
Supersedes:
```

Normative headings must describe subject matter, for example “Command validation and atomicity,” not “M002 protocol spine” or “S027 baseline.”

Migration of each current specification document must follow this rule:

1. Extract every normative requirement and assign it to exactly one semantic specification file.
2. Move implementation support statements to a backend, producer, or transport profile.
3. Move test results and runtime observations to conformance evidence.
4. Move rationale to an ADR when it remains useful.
5. Move chronology and delivery narrative to development history.
6. Resolve contradictions using the established repository authority order.
7. Preserve traceability through archival references, but do not expose chronology in normative headings.
8. Do not mark a specification “implemented” merely because a delivery stage was closed.

## Status And Support Model

Document status and implementation support are separate systems.

**Normative document statuses**

| Status     | Meaning                                                         | Public consequence                                                   |
| ---------- | --------------------------------------------------------------- | -------------------------------------------------------------------- |
| Draft      | Incomplete proposal with no normative authority                 | May be discussed but must not be presented as accepted protocol      |
| Candidate  | Semantically complete and under formal review                   | May have implementations, but compatibility is not yet guaranteed    |
| Accepted   | Current normative protocol authority                            | Implementations are measured against it                              |
| Deprecated | Still defined for compatibility but not recommended for new use | Replacement and removal conditions must be named                     |
| Superseded | Replaced by another accepted document                           | Removed from the active normative path and retained for traceability |

“Implemented,” “complete,” “blocked,” and “pending” are not specification-document statuses.

**Implementation support labels**

| Label          | Meaning                                                                                            |
| -------------- | -------------------------------------------------------------------------------------------------- |
| Not assessed   | No sufficient evidence has been recorded; this does not mean unsupported                           |
| Unsupported    | The implementation does not advertise the feature and must reject its use deterministically        |
| Partial        | Only the enumerated subset is supported                                                            |
| Adapted        | The feature executes through a documented semantic approximation or deviation                      |
| Strict         | The declared feature combination satisfies the protocol semantics and has current runtime evidence |
| Blocked        | Public support promotion is disabled despite some implementation work                              |
| Not applicable | The axis does not apply to the feature                                                             |

Every public feature row must expose these independent dimensions:

1. Protocol schema and validation status.
2. VisPy2 producer support.
3. Matplotlib reference-renderer support.
4. Datoviz v0.4 renderer support.
5. Strict versus adapted behavior.
6. Query/readback support.
7. Legacy API availability.
8. Required capability key or capability combination.
9. Evidence identifier, backend version, and last verified commit.

The runtime `CapabilitySnapshot` is authoritative for a specific session. The website matrix describes a tested implementation envelope and must not override runtime negotiation.

A rendered image, an importable symbol, an adapter code path, or a closed delivery stage is insufficient evidence for strict support. Strict support requires semantic runtime tests for the exact feature combination and relevant limits.

**Sample support table**

| Feature                                | Protocol schema / validation           | VisPy2 producer                                                          | Matplotlib reference renderer                                                 | Datoviz v0.4 renderer                                                                                   | Query/readback                                                            | Legacy API                                                                   |
| -------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `View2D` + `PointVisual`               | Accepted current scope                 | Mark Supported only after a VisPy2 emission test; otherwise Not assessed | Reference support, with strictness recorded per profile                       | Capability-gated; do not claim strict support without current semantic evidence                         | Separate query capability; rendering support does not imply query support | Similar legacy visuals may remain available, but are not protocol-equivalent |
| `Texture2D` + `ImageVisual`            | Validation support is present          | Supported according to current producer evidence                         | Reference support subject to the Matplotlib profile                           | **Blocked for renderer promotion**; a rendered capture must not be called supported or strict by itself | Readback and image queries require separate profile entries               | Legacy texture paths, if present, are compatibility-only                     |
| Axis, text, grid, and colorbar guides  | Accepted by feature-specific contracts | Must be listed separately rather than summarized globally                | Normative/reference behavior for documented cases                             | Mixed: adapted, unsupported, or crash-isolated depending on the exact guide case                        | Per-guide and per-query capability                                        | Legacy annotation behavior is not evidence of protocol conformance           |
| `View3D` + opaque `MeshVisual`         | Accepted bounded 3D scope              | Not assessed globally until VisPy2 producer tests are linked             | Some paths are adapted references rather than strict GPU-equivalent rendering | Capability-gated per projection, depth, shading, culling, and navigation combination                    | Mesh queries require separate capability and payload evidence             | Legacy 3D renderer paths remain distinct                                     |
| Mesh-triangle query payload            | Accepted payload contract              | Producer construction support must be tested independently               | Runtime query support recorded separately from mesh rendering                 | Runtime query support recorded separately from mesh rendering                                           | Contract support does not imply backend execution support                 | No equivalence should be inferred                                            |
| `Canvas` / `Viewport` / `RendererBase` | Not part of the current GSP protocol   | Not applicable                                                           | Not applicable to the protocol profile                                        | Not applicable to Datoviz v0.4 protocol support                                                         | Not applicable                                                            | Available only where compatibility code remains; deprecated and isolated     |

Support tables must favor precise phrases such as “Strict for `PointVisual` with 2D affine transforms under capability set X” over broad phrases such as “Points supported.”

## Screenshot Policy

**Selection**

* Publish only scenes executed through the current protocol/session path.
* Use the same scene records, resource data, dimensions, ranges, and camera state for both backends.
* Compare one coherent semantic feature set per row.
* Do not include legacy `datoviz-v03` or Flask-renderer captures in current backend comparisons.
* Do not select an image solely because the two outputs look similar.
* Do not imply pixel equality or complete backend interchangeability.
* A mixed-support scene must be labeled according to its weakest relevant feature or explicitly marked “Mixed; see details.”

**Regeneration**

Each published capture must be reproducible from a checked-in example or capture script. Regeneration must record:

* Repository commit.
* Python version.
* GSP and VisPy2 versions or commit identifiers.
* Backend and adapter versions.
* Operating system.
* For Datoviz: GPU, driver, and relevant graphics-runtime version.
* Fixed random seed.
* Input data checksum.
* View, camera, and output dimensions.
* Capture command.
* Capability snapshot or normalized capability subset.
* Conformance evidence identifiers.
* Capture timestamp.
* Image checksum.

Matplotlib and Datoviz captures must be generated independently and laid out with responsive HTML/CSS. The existing whitespace-heavy 1440×480 composites must not be used as primary website assets.

**Dimensions**

* Use **900×650** source images for 2D examples where that is the established verified capture size.
* Use **1280×720** source images for 3D scenes.
* Display through responsive containers with equal visual widths, preserved aspect ratios, and no upscaling beyond source dimensions.
* Provide smaller derived assets only through an automated, lossless or high-quality build step.
* Retain PNG for exact visual-QA assets; optional WebP derivatives may be generated for page delivery if PNG remains the provenance source.

**Stable paths and filenames**

```text
mkdocs_source/assets/comparisons/
  points-over-image/
    matplotlib.png
    datoviz-v04.png
    provenance.yaml
  view3d-cube/
    matplotlib.png
    datoviz-v04.png
    provenance.yaml
  view3d-terrain/
    matplotlib.png
    datoviz-v04.png
    provenance.yaml
  flat-lambert-mesh/
    matplotlib.png
    datoviz-v04.png
    provenance.yaml
  suzanne-flat-lambert/
    matplotlib.png
    datoviz-v04.png
    provenance.yaml
  lit-mesh-arcball/
    matplotlib.png
    datoviz-v04.png
    provenance.yaml
```

Support labels must not be encoded into filenames because evidence may change while the scene identity remains stable. Labels belong in profile metadata and captions.

**Accessibility text**

Alternative text must describe the scientific content and view, not merely name the backend.

Good:

> “Perspective view of a shaded Suzanne mesh with visible front-facing triangles and a dark background, rendered by Datoviz v0.4.”

Bad:

> “Datoviz screenshot.”

Where a visual difference is relevant, the surrounding prose must explain it without relying on color alone.

**Captions**

Every comparison row must identify:

* The common scene.
* The backend and version.
* The support classification.
* The exact strict or adapted scope.
* Any visible or semantic limitation.
* A link to the backend profile and provenance record.

Caption pattern:

> **Matplotlib — reference, adapted for 3D shading.** Same GSP mesh scene and camera as the adjacent Datoviz capture. Geometry, projection, and face-culling intent are represented; lighting is a declared reference adaptation.

> **Datoviz v0.4 — strict for the listed mesh capability set.** Same GSP mesh scene and camera as the adjacent Matplotlib capture. Status verified against evidence DVZ-MESH-… at the recorded commit.

No caption may say “identical,” “equivalent,” or “fully interchangeable” unless a narrowly defined conformance requirement and evidence justify that exact statement.

**Strict and adapted labels**

* Use visible text labels, not color-only badges.
* `Strict` requires current semantic runtime evidence.
* `Adapted` must name the deviation.
* `Partial` must list the included subset.
* `Blocked` may be shown only to explain a known limitation, never as a normal supported example.
* A crash-isolated case must not be shown as a normal successful backend comparison.

**Update policy**

Regenerate or re-verify an asset when any of these changes:

* Protocol semantics used by the scene.
* Producer output.
* Adapter implementation.
* Backend version.
* Capability declaration.
* Camera, layout, color, or shading rules.
* Capture environment in a way likely to affect output.

Visual similarity can support review but cannot promote a capability to strict support. Promotion requires the corresponding semantic tests and profile update.

**First scenes to publish**

1. **Minimal 2D points** — Matplotlib-only tutorial result; establishes the basic current protocol path.
2. **Points over image** — Useful for layering, resources, and 2D transforms; publish the Datoviz side only with an explicit Texture2D blocked/adapted qualification supported by current evidence.
3. **View3D cube** — Smallest understandable projection, depth, and camera comparison.
4. **Flat Lambert mesh** — Demonstrates bounded mesh shading and face semantics.
5. **View3D terrain** — Demonstrates a denser mesh and depth behavior without claiming huge-data support.
6. **Suzanne OBJ flat Lambert mesh** — A recognizable nontrivial geometry comparison; publish only after deterministic regeneration.

The lit mesh/arcball scene should follow later because it combines lighting and interaction and is therefore harder to classify honestly in a single comparison.

## Migration Map

| Current page or corpus                                          | Action: rewrite/move/archive/delete | Destination                                                                                   | Key correction                                                                                                                 |
| --------------------------------------------------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Home                                                            | Rewrite                             | `Home`                                                                                        | Lead with the protocol-session mental model, current maturity, and explicit capability-gated backend support                   |
| About                                                           | Rewrite and split                   | `Getting Started → What is GSP?` and `Concepts → Architecture and roles`                      | Remove the RendererBase model and explain producer, session, transport, adapter, and backend roles                             |
| Status and releases                                             | Rewrite                             | `Project Status`                                                                              | Replace S001–S050 completion reporting with product maturity, accepted scope, verified support, gaps, and public release notes |
| Protocol specification page                                     | Replace                             | `Specification → Specification overview`                                                      | Replace the 51-line GitHub directory with a navigable semantic specification, authority explanation, and status model          |
| Testing and conformance                                         | Rewrite and split                   | `Specification → Conformance` and `Contributing → Conformance and visual QA`                  | Separate normative requirements, test mappings, backend evidence, and contributor procedures                                   |
| Historical S023 QA                                              | Archive and relabel                 | `Development History → Delivery archive`                                                      | Remove the stage identifier from public navigation and state that the material is historical evidence                          |
| Gallery                                                         | Rewrite                             | `Examples → Gallery` and `Examples → Backend comparisons`                                     | Include only current protocol scenes with capability and provenance labels                                                     |
| Philosophy top-level section                                    | Remove from current navigation      | None                                                                                          | Do not teach the legacy renderer model as project philosophy                                                                   |
| Still-valid Philosophy concepts                                 | Rewrite, not copy                   | Relevant `Concepts` pages                                                                     | Express ideas in current protocol terminology and verify them against accepted authority                                       |
| Superseded Philosophy content                                   | Archive                             | `Development History → Archived philosophy documents`                                         | Preserve history while removing it from the recommended learning path                                                          |
| API Reference top-level page                                    | Replace                             | `Python API`                                                                                  | Publish task-oriented public surfaces rather than broad module dumps                                                           |
| Generated `gsp` package dump                                    | Delete from public build or exclude | None, except curated API pages                                                                | Prevent protocol, implementation internals, and legacy objects from appearing as one API                                       |
| Current protocol API records                                    | Curate                              | `Python API → Protocol records`, `Visual and resource records`, and `Queries and diagnostics` | Make `CommandBatch`, `CapabilitySnapshot`, and current records discoverable                                                    |
| Legacy API records                                              | Move and isolate                    | `Development History → Legacy Python API`                                                     | Label every entry as compatibility-only and outside the current GSP protocol                                                   |
| Current protocol review examples                                | Promote after verification          | `Examples` and the first tutorial                                                             | Use as executable sources for documentation rather than copying untested snippets                                              |
| Legacy examples selected by `GSP_RENDERER`                      | Move and relabel                    | `examples/legacy/` and `Development History → Legacy backend paths`                           | Do not present environment-variable renderer selection as the current model                                                    |
| `datoviz-v03` documentation                                     | Archive                             | `Development History → Legacy backend paths`                                                  | Distinguish it from the Datoviz v0.4 protocol adapter                                                                          |
| Legacy Flask/network renderer documentation                     | Archive                             | `Development History → Legacy backend paths`                                                  | Do not present it as the current remote GSP transport                                                                          |
| Screenshot and visual-QA assets                                 | Curate and regenerate               | `mkdocs_source/assets/comparisons/`                                                           | Use stable paths, reproducible scenes, exact captions, and per-backend provenance                                              |
| `SPEC_INDEX.md`                                                 | Rewrite                             | Repository root `SPEC_INDEX.md`                                                               | Make it a normative semantic manifest, not an agent-navigation or evidence index                                               |
| 37-file specification corpus                                    | Restructure by semantic domain      | `spec/**`                                                                                     | Remove stage/mission headings, separate semantics from profiles, evidence, rationale, and history                              |
| Normative text mentioning S/M/P identifiers                     | Rewrite                             | Relevant semantic specification file                                                          | Replace chronology-based labels with durable requirement and concept names                                                     |
| Implementation support statements inside specs                  | Move                                | `profiles/**`                                                                                 | Keep protocol acceptance independent from implementation progress                                                              |
| Test results and proof notes inside specs                       | Move                                | `conformance/**`                                                                              | Prevent evidence from becoming normative semantics                                                                             |
| Accepted decision rationale                                     | Retain and normalize                | `adr/accepted/`                                                                               | Link rationale from specs without duplicating requirements                                                                     |
| `.agent` decisions, consultations, closeouts, and mission notes | Archive                             | `development-history/**`                                                                      | Preserve traceability but remove them from public and normative reading paths                                                  |
| MkDocs navigation                                               | Replace atomically                  | New navigation tree                                                                           | Avoid a transition state in which old and new architectures appear side by side                                                |
| Existing public URLs                                            | Redirect                            | Corresponding new or archived page                                                            | Preserve inbound links without preserving misleading claims                                                                    |

## Phased Implementation Plan

| Phase                                              | Allowed scope                                                                                                | Deliverables                                                                                                                                                                             | Validation                                                                                                                                                  | User-review checkpoint                                                                          | Stop conditions                                                                                                                     |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 0. Decision lock                                   | Planning and inventory only; no dependent website or specification rewrite                                   | Accepted consultation result, canonical mental model, legacy boundary, target trees, and proposed ADR                                                                                    | Confirm all decisions conform to the charter and stated authority order                                                                                     | User reviews and accepts or amends this consultation result                                     | Stop all dependent rewriting until the consultation response is pasted or committed and the decision is accepted                    |
| 1. Authority and content inventory                 | Classification and tooling; no public navigation cutover                                                     | Inventory of every public page, spec file, generated API page, example, screenshot, requirement, support claim, and historical identifier; destination map for every normative statement | No accepted normative statement lacks a target; every support claim has an evidence state; conflicting statements are flagged against authority order       | User reviews the inventory summary and unresolved authority conflicts                           | Stop if an unresolved conflict would require redesigning protocol semantics or treating source code as higher authority             |
| 2. Parallel specification normalization            | Create new semantic spec, profile, conformance, ADR, and history trees without deleting old source documents | Rewritten `SPEC_INDEX.md` draft; semantic specification files; backend and producer profiles; conformance requirement map; archived chronology                                           | Cross-reference check; requirement traceability; banned chronology terms absent from active normative text; no implementation state used as document status | User reviews the new specification index and representative core, visual, and query files       | Stop if any accepted rule is lost, duplicated inconsistently, or placed only in an implementation profile                           |
| 3. Parallel public-documentation build             | Create new pages outside the published navigation or under a separate MkDocs configuration                   | Home, Getting Started, Concepts, User Guide skeleton, Backend Support, Project Status, and Specification overview                                                                        | MkDocs strict build; terminology audit; all factual support statements trace to profiles; no legacy architecture in recommended paths                       | User reviews the conceptual flow and first tutorial source before screenshots and API expansion | Stop if the first tutorial does not run from a clean Python 3.13 environment or uses a legacy API surface                           |
| 4. Support, examples, screenshots, and curated API | Add evidence-backed content to the parallel site                                                             | Feature matrix; Matplotlib and Datoviz profiles; executable example index; regenerated captures and provenance; task-oriented API pages; legacy archive                                  | Semantic tests; capture scripts; capability/profile consistency; API import tests; accessibility checks; generated-output size budget                       | User reviews backend wording, selected screenshots, captions, and the API boundary              | Stop if a screenshot or API symbol implies unsupported parity, or if strict support lacks semantic evidence                         |
| 5. Integrated local review                         | Switch a local-only MkDocs configuration to the complete proposed navigation; no merge or public deployment  | Full local site, redirects draft, archived legacy/history pages, search index, and review checklist                                                                                      | `mkdocs serve` and strict build; link checker; search-term audit; responsive review; clean-install tutorial run                                             | Mandatory user review through the running local MkDocs development server                       | Stop until the user explicitly approves the architecture, navigation, wording, screenshots, and legacy boundary                     |
| 6. Atomic cutover                                  | Replace navigation and authoritative indexes in one coordinated change                                       | New public navigation; new `SPEC_INDEX.md`; active semantic spec tree; redirects; legacy/history archive; obsolete generated pages removed from build                                    | Full tests, strict docs build, link validation, requirement traceability, redirect checks, support-evidence checks, and clean repository diff               | User reviews the final cutover diff if it differs materially from the locally approved site     | Stop if old and new architectural narratives coexist in current navigation or if any required redirect points to misleading content |
| 7. Merge and maintenance baseline                  | Merge only approved cutover; no unreviewed semantic additions                                                | Accepted ADR, maintenance owners, documentation CI, capture regeneration rules, status-update procedure                                                                                  | CI passes from a clean checkout; public pages correspond to approved local build; archive retained                                                          | No additional checkpoint unless merge corrections change user-visible meaning                   | Stop if merge-time fixes alter protocol meaning, support classification, or public architecture without renewed review              |

The navigation cutover and `SPEC_INDEX.md` authority cutover should occur in the same phase. Publishing either the new public site against the old chronology-based spec index, or the new spec index beneath the old RendererBase-oriented site, would create a misleading intermediate state.

## Claims Requiring Proof Or Qualification

| Risky public claim                                                             | Required evidence                                                                                             | Safe interim wording                                                                                                                                           |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| “The same scene runs on interchangeable backends.”                             | Feature-by-feature capability intersection and semantic runtime evidence for the exact scene                  | “Protocol semantics are backend-independent; a scene can run on a backend only when the session advertises the required capabilities.”                         |
| “GSP supports Matplotlib and Datoviz.”                                         | Versioned backend profiles listing each feature and support class                                             | “Matplotlib provides the reference implementation for documented semantics; Datoviz v0.4 provides capability-gated GPU support.”                               |
| “Datoviz strictly supports a feature because an API symbol exists.”            | Runtime conformance tests exercising semantic behavior and limits                                             | “The symbol exists, but strict support is not claimed until runtime semantic evidence is recorded.”                                                            |
| “Datoviz strictly supports a feature because a screenshot was produced.”       | Non-visual semantic tests plus current capability declaration                                                 | “The scene produced a capture under the recorded environment; this does not by itself establish strict support.”                                               |
| “Datoviz supports `Texture2D`.”                                                | Successful promotion criteria, semantic tests, stability evidence, and an updated capability profile          | “`Texture2D` validates at protocol level and has VisPy2 producer support, but Datoviz renderer promotion is currently blocked.”                                |
| “Guides, text, or colorbars work on Datoviz.”                                  | Separate tests and profiles for every stated guide/text/colorbar combination                                  | “Datoviz behavior is feature-specific and currently includes adapted, unsupported, or crash-isolated cases.”                                                   |
| “Queries work wherever rendering works.”                                       | Per-query capability declarations, payload tests, and backend evidence                                        | “Query and rendering support are independent capabilities.”                                                                                                    |
| “Mesh rendering implies mesh-triangle queries.”                                | Mesh query execution tests and payload validation for each backend                                            | “The mesh-triangle payload contract is accepted; backend execution support is reported separately.”                                                            |
| “Matplotlib is a strict equivalent of GPU 3D rendering.”                       | Requirement-level evidence showing no declared semantic differences                                           | “Matplotlib is the reference backend; some 3D paths are documented adaptations rather than strict GPU-equivalent rendering.”                                   |
| “Datoviz is the flagship backend, therefore it supports the full protocol.”    | Complete feature-profile evidence                                                                             | “Datoviz v0.4 is the flagship GPU target, with support negotiated and documented per capability.”                                                              |
| “Remote rendering is supported.”                                               | Current non-legacy server/transport implementation, tests, security and failure semantics, and profile        | “The protocol model permits remote deployment; no current remote profile should be claimed without verified implementation evidence.”                          |
| “The Flask network renderer is remote GSP.”                                    | Proof that it implements the current session, capability, command, query, diagnostic, and extension contracts | “The Flask renderer is a legacy network path and is not the current target protocol.”                                                                          |
| “Binary IPC is available.”                                                     | Implemented transport profile and conformance tests                                                           | “Binary IPC is a planned transport class, not a current supported transport unless a profile is published.”                                                    |
| “JSON is the GSP wire format.”                                                 | Not applicable; this conflicts with the stated architecture                                                   | “Protocol meaning is encoding-independent; JSON/base64 is intended for fixtures, debugging, replay, and simple transport.”                                     |
| “The in-process path is zero-copy.”                                            | End-to-end ownership, lifetime, aliasing, and copy measurements for stated resource types                     | “The in-process transport does not require JSON/base64 and may carry native NumPy or memoryview-compatible data.”                                              |
| “The in-process path is fast.”                                                 | Reproducible benchmark against defined alternatives and workloads                                             | “The in-process path is designed to avoid mandatory serialization overhead.”                                                                                   |
| “Huge datasets are supported.”                                                 | Verified virtual-data-source implementation, limits, scheduling behavior, and backend integration             | “The protocol includes or is developing virtual data-source contracts; support must be stated per source type, producer, and backend.”                         |
| “HTTP-array data sources are implemented.”                                     | Executable examples, error behavior, range or chunk semantics, and profile evidence                           | “HTTP-array data-source work exists within the current scope; its implementation status is reported separately.”                                               |
| “VisPy2 supports all accepted protocol features.”                              | Producer conformance tests mapping VisPy2 operations to valid records for each feature                        | “VisPy2 is the intended high-level producer; current producer coverage is listed feature by feature.”                                                          |
| “GSP is production-ready.”                                                     | Stability policy, compatibility guarantees, deployment evidence, security review, and release process         | “GSP and VisPy2 are experimental 0.1.0 prototypes.”                                                                                                            |
| “Install GSP with `pip install gsp`.”                                          | A verified published PyPI distribution with an unambiguous package name                                       | “Clone the repository and install from source using the documented development procedure.”                                                                     |
| “Python 3.13+ is supported everywhere.”                                        | Packaging metadata and CI on each stated operating system and architecture                                    | “The current project requires Python 3.13 or newer; supported platforms are listed only where CI or manual evidence exists.”                                   |
| “Stages S001–S050 being complete means the product is feature-complete.”       | Not applicable; delivery completion is not product maturity evidence                                          | “Internal delivery stages are complete records of work; current product maturity is described by accepted protocol scope and verified implementation support.” |
| “The specification is complete because an implementation stage closed.”        | Accepted document status and normative review                                                                 | “Specification status and implementation status are tracked independently.”                                                                                    |
| “The legacy API and protocol API are two interfaces to the same architecture.” | This would require semantic equivalence that is not established                                               | “The legacy object-oriented renderer remains compatibility material and is not the current GSP protocol architecture.”                                         |
| “Backend images prove exact parity.”                                           | Defined equivalence metric plus semantic and visual evidence                                                  | “The images show two executions of the same scene; captions identify any strict, adapted, partial, or unsupported behavior.”                                   |

## Acceptance Checklist

**Ready for local user review**

* [ ] The homepage defines GSP as a semantic session protocol, not a renderer object graph.
* [ ] The architecture diagram shows producer, session/protocol, transport, adapter, backend, results, and diagnostics.
* [ ] VisPy2, direct protocol records, transports, and backend adapters have distinct roles.
* [ ] Matplotlib is described as the reference/publication backend.
* [ ] Datoviz v0.4 is described as a capability-gated GPU backend rather than a globally interchangeable renderer.
* [ ] The source-installation page does not claim PyPI availability.
* [ ] The Python 3.13 requirement matches repository metadata and tested environments.
* [ ] The first tutorial runs from a clean environment using only the current protocol path.
* [ ] The first tutorial uses an explicit in-process Matplotlib session and a `CommandBatch`.
* [ ] `CapabilitySnapshot` appears in both explanatory documentation and curated API documentation.
* [ ] No recommended page uses `Canvas`, `Viewport`, `RendererBase`, `RendererRegistry`, or `GSP_RENDERER`.
* [ ] No current backend page treats `datoviz-v03` as Datoviz v0.4 support.
* [ ] No current remote-rendering page relies on the legacy Flask path.
* [ ] The feature matrix separates protocol, VisPy2, Matplotlib, Datoviz, query/readback, and legacy axes.
* [ ] Every strict claim links to current semantic runtime evidence.
* [ ] Every adapted claim identifies the adaptation.
* [ ] Every partial claim enumerates its supported subset.
* [ ] Every blocked claim explains the promotion condition without presenting the feature as supported.
* [ ] Missing evidence is labeled Not assessed rather than guessed as Strict or Unsupported.
* [ ] The runtime capability model is explained as authoritative for each session.
* [ ] The active specification contains no chronology-based headings.
* [ ] `SPEC_INDEX.md` indexes only normative semantic documents.
* [ ] Every accepted normative statement in the old corpus has exactly one destination in the new specification.
* [ ] Implementation claims have been removed from normative specification status fields.
* [ ] Tests and evidence have been moved to `conformance/**`.
* [ ] Rationale has been moved to or linked from accepted ADRs.
* [ ] Stages, missions, consultations, closeouts, and evidence chronology remain preserved under development history.
* [ ] A repository-wide audit confirms that `S[0-9]{3}`, `M[0-9]{3}`, `P[0-9]{3}`, “consultation,” and “closeout” do not occur in current public or normative reading paths except in explicit historical references.
* [ ] The old Philosophy section is absent from current navigation.
* [ ] Legacy pages display a persistent compatibility-only warning.
* [ ] The generated API no longer exposes a broad undifferentiated `gsp` package dump.
* [ ] Public API pages contain only verified public producer, protocol, session, query, diagnostic, resource, and adapter surfaces.
* [ ] All displayed code is imported from or synchronized with executable example files.
* [ ] Curated captures have stable asset paths and provenance records.
* [ ] Every comparison caption names backend version, support class, exact scope, and deviations.
* [ ] Alternative text describes scene content and does not depend on backend names alone.
* [ ] Responsive layouts work at narrow, tablet, and desktop widths.
* [ ] The MkDocs build succeeds in strict mode.
* [ ] Internal and external links pass validation.
* [ ] Search results for “renderer,” “Datoviz,” “network,” and “architecture” return current pages before historical ones.
* [ ] The complete proposed site is running locally through the MkDocs development server.
* [ ] The user has reviewed the homepage, first tutorial, feature matrix, backend comparison, specification index, and legacy archive locally.

**Ready to merge**

* [ ] The user has explicitly approved the locally served rewrite.
* [ ] The accepted ADR matches the approved public mental model and legacy boundary.
* [ ] The navigation cutover and `SPEC_INDEX.md` cutover occur atomically.
* [ ] Old public URLs have tested redirects to accurate current or archived destinations.
* [ ] No old and new architecture pages coexist in the current navigation.
* [ ] No superseded generated API dump remains in the published build.
* [ ] Documentation, protocol, profile, conformance, and example tests pass from a clean checkout.
* [ ] Screenshot checksums and provenance correspond to the merged commit or an explicitly recorded parent commit.
* [ ] Backend profile versions match the tested backend versions.
* [ ] Requirement-to-test traceability contains no accepted requirement without a disposition.
* [ ] The archive retains historical evidence and original provenance.
* [ ] Release notes describe the documentation/specification reorganization without claiming new protocol behavior.
* [ ] The final merge diff contains no unreviewed protocol-semantic change.
* [ ] CI enforces strict documentation builds, executable examples, terminology checks, and support-evidence consistency.

## Decision Record Draft

**Title:** Protocol-centered public documentation and semantic specification organization
**Status:** Proposed
**Decision type:** Documentation architecture and specification organization

**Context**

The repository contains an intended session/protocol architecture and an older object-oriented rendering architecture. Current public documentation presents both as one system, making it difficult for users to determine which concepts are authoritative. The normative corpus is organized partly around internal delivery chronology and mixes protocol requirements, implementation status, evidence, rationale, and history. Backend documentation also risks implying parity that is not supported by capability-specific evidence.

The repository authority order places the charter and architecture above specifications, accepted ADRs, legacy mappings, and source code. The charter defines GSP as a backend-independent server/session protocol with native in-process transport, explicit capabilities and adaptations, semantic visual families, first-class queries, manifest-driven extensions, virtual data sources, a Matplotlib reference backend, a Datoviz v0.4 GPU backend, and VisPy2 as the high-level producer.

**Decision**

1. The single public mental model will be a producer submitting semantic commands and resources to a capability-negotiated GSP session, which executes them through a backend adapter and returns results and diagnostics.
2. VisPy2 will be presented as the intended high-level producer. Direct protocol records will be presented as the lower-level integration and conformance surface.
3. Transport and encoding will be treated separately from protocol meaning. The in-process path will be first-class; JSON/base64 will not be presented as the defining wire representation.
4. Matplotlib will be documented as the reference and publication backend. Datoviz v0.4 will be documented through capability- and evidence-specific support claims.
5. The legacy `Canvas`/`Viewport`/`RendererBase` architecture will be retained only as isolated compatibility and development-history material.
6. Public documentation will follow a concept-first progression from Home and Getting Started through Concepts, User Guide, Backend Support, Specification, curated Python API, and Examples.
7. Normative specifications will be organized by durable semantic domains rather than stages, missions, consultations, or delivery proofs.
8. Protocol semantics, backend and producer profiles, conformance evidence, ADR rationale, and development history will reside in separate document trees.
9. Document status will be independent of implementation support. Backend support will use the controlled labels Not assessed, Unsupported, Partial, Adapted, Strict, Blocked, and Not applicable.
10. Strict support claims will require current semantic runtime evidence. API presence, source-code paths, screenshots, and completed delivery stages will not be sufficient.
11. Backend comparison images will use verified current protocol scenes, separate responsive captures, explicit support labels, and reproducible provenance.
12. The new navigation and normative index will be activated atomically after local user review.

**Consequences**

* New users receive one coherent explanation of GSP.
* Protocol authority no longer depends on implementation chronology or legacy code.
* Backend limitations become visible and technically precise.
* Public matrices require ongoing evidence maintenance.
* Some implementation features will initially be labeled Not assessed because existing evidence is insufficient for stronger claims.
* Broad generated API documentation will be replaced by smaller curated surfaces.
* Historical material remains available but loses prominence and normative ambiguity.
* Existing inbound documentation links require redirects.
* Specification migration requires explicit requirement traceability to ensure no accepted rule is lost.
* Documentation updates that change support classifications must update profiles, evidence, examples, and captions together.

**Rejected alternatives**

* Keeping legacy and protocol APIs in one architecture section was rejected because it preserves the current ambiguity.
* Treating existing source code as the definitive architecture was rejected because it conflicts with the repository authority order.
* Publishing a single backend-support boolean was rejected because support differs by schema, producer, renderer, adaptation, query, and feature combination.
* Retaining mission- or stage-based normative headings was rejected because those identifiers are unstable implementation chronology rather than durable protocol concepts.
* Using screenshot similarity as conformance evidence was rejected because visual output alone cannot establish semantic equivalence.
* Deleting historical records was rejected because traceability must be preserved.

**Implementation constraint**

No dependent website or specification rewrite proceeds until this decision is accepted by the user.

