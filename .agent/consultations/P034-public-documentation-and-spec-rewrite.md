# P034 - Public Documentation And Specification Rewrite

## Prompt to paste into ChatGPT Pro

```text
We are redesigning the complete public documentation website and normative specification for
GSP_API, an experimental Python scientific-visualization project. Produce a decisive documentation
architecture and migration plan from the facts below. Do not ask for files or additional context;
this prompt is self-contained.

PROJECT PURPOSE AND AUTHORITY

The authority order in the repository is:
1. PROJECT_CHARTER.md
2. ARCHITECTURE.md
3. SPEC_INDEX.md
4. spec/**
5. accepted ADRs and decision records
6. legacy map
7. existing source code

The charter mission is:
"Create a backend-independent Graphics Server Protocol (GSP) for scientific visualization and a
new VisPy2 Python interface that targets GSP."

The charter's non-negotiable technical principles are:
- GSP is a server/session protocol inspired by LSP, not merely a Python object graph.
- Local desktop use has a fast in-process path with no mandatory JSON/base64 serialization.
- JSON/base64 is for fixtures, debugging, replay, and simple transport only.
- Capability discovery and explicit adaptation are mandatory.
- Visual families are semantic contracts, not backend draw calls.
- Query/readback is first-class and uses a unified panel-query model.
- Extensions are manifest-, version-, and capability-driven.
- Huge datasets use virtual data sources rather than ordinary buffers.
- Datoviz v0.4 is the flagship GPU backend.
- Matplotlib is the reference/conformance/publication backend.
- VisPy2 is the high-level Python producer of GSP scenes.

The target architecture is:

  VisPy2 / plotting APIs / domain libraries
    -> GSP producer API
      -> GSP session and protocol model
        -> backend adapters
          -> Matplotlib reference backend
          -> Datoviz v0.4 GPU backend
          -> future remote/web/specialized backends

A GSP server may be in-process, a subprocess, remote, a browser worker, or a cloud GPU service. It
advertises capabilities, accepts scene/resource/visual commands, executes frames, returns query and
readback results, and emits diagnostics. Protocol meaning is independent of encoding. Transport
classes include in-process Python/NumPy/memoryview, future binary IPC, network, and debug JSON.

CURRENT IMPLEMENTATION SURFACES

The repository currently contains two overlapping systems:

1. The intended protocol system under gsp.protocol, including command batches, panels, views,
   visuals, resources, transforms, layout, capabilities, navigation, queries, diagnostics,
   extensions, transports, data sources, and backend protocol renderers. Current protocol review
   examples construct records such as View2D, PointVisual, AxisGuide, PanelTextGuide, View3D, and
   MeshVisual. Matplotlib provides reference behavior. Datoviz v0.4 support is advertised per
   capability and is sometimes strict, adapted, unsupported, or blocked.

2. A legacy object-oriented rendering system under gsp.core, gsp.visuals, gsp.types, and related
   backend packages. It uses Canvas, Viewport, Camera, Buffer, Visual subclasses, RendererBase,
   RendererRegistry, and renderer.render(viewports, visuals, model_matrices, cameras). Many old
   examples select matplotlib, datoviz-v03, or network through GSP_RENDERER. This code remains in the
   repository as implementation and compatibility material, but it is not the final protocol
   authority.

The public site currently presents both systems as one architecture. The Home page briefly
describes protocol records and points to current review examples. However, About and approximately
2,100 lines of Philosophy material teach the legacy RendererBase model, four parallel render lists,
runtime registry selection, datoviz-v03, and legacy network rendering. A naive user cannot tell
which architecture is GSP.

DOCUMENTATION AUDIT FACTS

- MkDocs Material is used. The site builds successfully with strict mode.
- Current top-level navigation: Home, About, Status and releases, Protocol specification, Testing
  and conformance, Gallery, Philosophy, API Reference.
- The published protocol page is only 51 lines and is mostly a directory of GitHub links.
- CommandBatch and CapabilitySnapshot appear on zero published website pages.
- Generated API HTML is about 5.7 MB. The gsp API page alone is about 1.5 MB and exposes broad
  package/module dumps rather than task-oriented public surfaces.
- The spec corpus has 37 Markdown files and about 6,634 lines.
- It contains approximately 515 references to internal stages, missions, or Pro consultations using
  labels such as S023, M008, and P022.
- Many normative headings are chronology-based: "M002 protocol spine", "S027 baseline", "M011
  proof", etc.
- Some specs say Draft, implementation pending, or staged across missions even though the related
  implementation stages are recorded complete.
- SPEC_INDEX.md says it tells agents where to find authoritative information. It mixes normative
  specs with internal .agent decisions, evidence notes, closeouts, and stage history.
- The public Status page says stages S001-S050 are complete. This is internal delivery information,
  not useful product maturity information.
- A public navigation item is named "Historical S023 QA".
- Backend statements are often too broad. The website says the same scene can run against
  interchangeable backends, while actual Datoviz v0.4 support is capability-gated and the old
  datoviz-v03 and network renderers are separate legacy paths.
- GSP and VisPy2 are experimental version 0.1.0 prototypes and are not published on PyPI.
- Python 3.13 or newer is required.

CURRENT TECHNICAL SCOPE TO EXPLAIN

The accepted/current protocol includes:
- session/protocol command records and in-process transport;
- panels and resolved layout;
- immutable or validated resources including buffers and Texture2D protocol resources;
- PointVisual, MarkerVisual, SegmentVisual, PathVisual, ImageVisual, TextVisual, and MeshVisual;
- explicit coordinate spaces and 2D affine transforms;
- View2D ranges and semantic navigation actions;
- AxisGuide, PanelTextGuide, tick intent, grid intent, and ColorbarGuide;
- scalar color mapping with canonical named colormaps and linear normalization;
- static orthographic and perspective View3D plus navigation actions;
- bounded opaque 3D mesh depth, flat Lambert shading, face culling semantics, and mesh triangle query
  payload contracts;
- capability discovery, explicit adaptation, structured diagnostics, query/readback, extension
  manifests, and virtual/preconfigured/HTTP-array data-source work.

Support must be described on separate axes:
- protocol schema/validation support;
- VisPy2 producer support;
- Matplotlib reference-renderer support;
- Datoviz v0.4 renderer support;
- strict versus adapted behavior;
- query/readback support;
- legacy API availability.

Examples of important current limitations:
- Datoviz capabilities must never be inferred merely from the existence of an API symbol or a
  rendered image; strict claims require semantic runtime evidence.
- Datoviz Texture2D renderer promotion is blocked despite protocol validation and VisPy2 producer
  support.
- Some Datoviz guide/text/colorbar/query cases remain adapted, unsupported, or crash-isolated.
- Matplotlib is normative for many semantics but some 3D rendering paths are explicitly adapted
  references rather than strict GPU-equivalent rendering.
- Legacy datoviz-v03 and Flask network paths must not be presented as the current target protocol.

SCREENSHOT ASSETS

The repository has hundreds of committed visual-QA PNGs and these useful current matched
Matplotlib/Datoviz captures generated from the same scenes:
- points over image, 900x650 per backend;
- View3D cube, 1280x720 per backend;
- View3D terrain, 1280x720 per backend;
- flat Lambert mesh, 1280x720 per backend;
- lit mesh/arcball, 1280x720 per backend;
- Suzanne OBJ flat Lambert mesh, 1280x720 per backend.

There are also 1440x480 side-by-side composites, but they have excessive whitespace and QA-style
labels. The intended website policy is to regenerate or verify captures against the current code,
copy a small curated set into stable mkdocs_source/assets paths, use responsive side-by-side layouts,
and caption every comparison accurately. Images must not imply exact backend parity where a row is
adapted or otherwise not strict.

USER'S DESIRED OUTCOME

The user wants an extensive rewrite. The website should explain to a naive technical user:
- what GSP is;
- why it exists;
- how a GSP session works;
- the roles of VisPy2, the protocol, and renderer adapters;
- scenes, panels, views, visuals, resources, capabilities, queries, and diagnostics in simple terms;
- what is implemented today and what is experimental or unsupported;
- how to install and run a first current protocol example;
- how Matplotlib and Datoviz compare, using sensible up-to-date screenshots;
- how to navigate from plain-language concepts into normative details.

Internal agent stages, missions, consultations, closeouts, and evidence chronology must disappear
from public and normative reading paths. They may remain in a clearly separated development-history
archive. Legacy APIs may remain documented only if clearly labeled and isolated from the current
recommended path.

The user will review the rebuilt site locally through a running MkDocs development server before
the rewrite is finalized.

PROPOSED INITIAL INFORMATION ARCHITECTURE

Home
Getting Started
  What is GSP?
  Installation
  First visualization
  Choosing a backend
Concepts
  Architecture and session lifecycle
  Scenes, panels, views, and visuals
  Resources and data
  Capabilities and adaptation
  Queries and diagnostics
  Local and remote rendering
User Guide
  Visuals
  Images and color mapping
  Guides and layout
  Interaction
  3D scenes and meshes
Backend Support
  Feature matrix
  Matplotlib
  Datoviz
  Remote rendering
Specification
Python API
Examples
Contributing
Development History

DECISIONS REQUIRED

1. Define the single public mental model for GSP and the exact relationship among VisPy2, protocol
   records, sessions, transports, and renderers.
2. Decide how the legacy RendererBase/object-graph API should appear, if at all, in the public site.
3. Refine or replace the proposed information architecture for a naive technical audience.
4. Define a stable normative spec structure that removes delivery chronology without losing
   technical decisions or conformance detail.
5. Define a consistent document-status vocabulary and rules for protocol support versus backend
   implementation support.
6. Define a screenshot selection and caption policy that is visually useful and technically honest.
7. Give a phased rewrite order that minimizes contradictory intermediate states.
8. Identify claims in the provided facts that should not be made publicly without additional proof.

CONSTRAINTS

- Do not redesign protocol semantics. This is a documentation architecture decision grounded in
  existing accepted authority.
- Do not make the legacy source code authoritative when it conflicts with the charter or specs.
- Do not erase historical evidence; relocate it outside the public/normative reading path.
- Do not claim backend parity globally.
- Do not make PyPI installation claims.
- Prefer durable concept names over release, stage, mission, or consultation identifiers.
- The result must be actionable by an implementation agent without requiring further architectural
  interpretation.

Produce exactly the following output format.
```

## Expected output format

```markdown
# Consultation Result: GSP Public Documentation And Specification Architecture

## Executive Decision

A concise statement of the one public mental model and the documentation strategy.

## Audience And Learning Outcomes

| Audience | What they must understand | Recommended entry page |
|---|---|---|

## Canonical Terminology

| Term | Plain-language definition | Normative meaning | Avoid/confusing alternative |
|---|---|---|---|

## Legacy Boundary

State exactly what to keep, relabel, archive, or remove from public navigation.

## Final Information Architecture

Provide the complete navigation tree. For every page, add one sentence describing its purpose.

## Homepage Blueprint

Give the ordered homepage sections, their purpose, recommended screenshot, and primary action.

## Getting-Started Narrative

Give the exact conceptual order for the first tutorial and identify what code/API surface it should
use.

## Specification Architecture

Provide the target spec file tree and explain which current subject matter belongs in each file.
Separate normative rules, backend profiles, conformance material, ADR rationale, and history.

## Status And Support Model

Define the document-status vocabulary and the support matrix dimensions. Include a sample support
table with honest wording for Matplotlib, Datoviz v0.4, VisPy2 producer support, and legacy APIs.

## Screenshot Policy

Define selection, regeneration, dimensions, filenames, accessibility text, captions, strict/adapted
labels, provenance, and update policy. Recommend the first 4-6 scenes to publish.

## Migration Map

| Current page or corpus | Action: rewrite/move/archive/delete | Destination | Key correction |
|---|---|---|---|

Cover all current top-level pages, Philosophy documents, API pages, SPEC_INDEX.md, and the spec
corpus.

## Phased Implementation Plan

For each phase provide allowed scope, deliverables, validation, user-review checkpoint, and stop
conditions. Order phases to avoid a misleading partially migrated site.

## Claims Requiring Proof Or Qualification

List risky public claims, the required evidence, and safe interim wording.

## Acceptance Checklist

Provide a concrete checklist for determining that the rewrite is ready for local user review and
then ready to merge.

## Decision Record Draft

Provide a concise ADR-style decision documenting the public documentation model, legacy boundary,
specification organization, and consequences.
```

## Stop condition

Dependent website and specification rewriting must remain paused until the user pastes or commits
the ChatGPT Pro response.
